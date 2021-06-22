from collections import defaultdict

from tensorflow.python.ops import script_ops
from tensorflow.python.platform.tf_logging import vlog
from server.database import MongoDatabaseAccessor
from typing import Any, Callable, Dict, List, Sequence, Tuple, Text
import tensorflow as tf
import tensorflow_recommenders as tfrs
from transformers import AutoTokenizer, TFBertModel


def argsort(seq: Sequence):
    # http://stackoverflow.com/questions/3071415/efficient-method-to-calculate-the-rank-vector-of-a-list-in-python
    return sorted(range(len(seq)), key=seq.__getitem__)


Feedback = Dict[str, List[Tuple[str, float]]]


class RankingExtension:
    def __init__(
        self,
        database_accessor: MongoDatabaseAccessor,
        tokenizer_name: str,
        model_name: str,
        ranker_factory: Callable[[List[str], int, float], "EquipmentRankingModel"],
        training_epochs: int = 150,
        learning_rate: float = 1e-3,
    ):
        self.stringuified_equipment_tf_output: Dict[str, Any] = {}

        self.database_accessor = database_accessor
        self.training_epochs = training_epochs
        self.learning_rate = learning_rate

        self.tokenizer = AutoTokenizer.from_pretrained(
            tokenizer_name)

        self.model = TFBertModel.from_pretrained(
            model_name, from_pt=True)

        initial_ids = database_accessor.get_unique_ids()

        self.ranker_factory = ranker_factory
        self.ranker = ranker_factory(
            initial_ids, training_epochs, learning_rate)

    def _get_output(self, value: str):
        input_ = self.tokenizer.encode(value, return_tensors="tf")
        output_ = self.model(input_).pooler_output

        return output_

    def equipment_was_added(self, tag: str, stringified: str):
        self.stringuified_equipment_tf_output[tag] = self._get_output(
            stringified)

    def rank(self, query: str, equipment_tags: Sequence[str]) -> Dict[str, float]:
        scores: List[float] = []
        query_output = self._get_output(query)
        for tag in equipment_tags:
            assert tag in self.stringuified_equipment_tf_output
            score = self.ranker(
                query_output, tag
            )
            scores.append(score)

        indexes = argsort(scores)

        return {
            equipment_tags[index]: scores[index]
            for index in indexes[::-1]
        }

    def learn(self, clicks: Feedback):
        # NOTE: This method can run at the same time as a call to rank()
        # Which means, we have to keep a self.ranker in "sync"
        # The solution found was having a ranker factory and create one
        # here; only when ready do we set it to self.ranker

        ids = self.database_accessor.get_unique_ids()

        new_ranker = self.ranker_factory(
            ids, self.training_epochs, self.learning_rate)
        # ...

        new_ranker.train(clicks, self.tokenizer, self.model)

        self.ranker = new_ranker


class EquipmentRankingModel(tfrs.models.Model):

    def __init__(self, unique_equipment_ids, training_epochs, learning_rate):
        super().__init__()

        self.training_epochs = training_epochs
        self.learning_rate = learning_rate

        self.ranking_model: tf.keras.Model = RankingModel(unique_equipment_ids)
        self.tasks: tf.keras.layers.Layer = tfrs.tasks.Ranking(
            loss=tf.keras.losses.MeanSquaredError(),
            metrics=[tf.keras.metrics.RootMeanSquaredError()]
        )

    def compute_loss(self, inputs: Dict[Text, tf.Tensor], training: bool) -> tf.Tensor:

        queries = inputs['queries']
        equipment_ids = inputs['equipments_ids']

        ranking_predictions = self.ranking_model(queries, equipment_ids)

        return self.tasks(labels=inputs['scores'], predictions=ranking_predictions)

    def __call__(self, query_output, equipment_id) -> float:

        score = self.ranking_model(
            query_output, tf.convert_to_tensor(equipment_id))

        return score.numpy()[0][0][0]

    def _convert_to_tensor(self, query, tokenizer, model):

        input_ = tokenizer.encode(query, return_tensors="tf")
        output_ = model(input_).pooler_output

        return output_

    def _build_dataset(self, clicks: Feedback, tokenizer, model):

        queries = []
        equipments_ids = []
        scores = []

        for key, values in clicks.items():

            for value in values:

                queries.append(key)
                equipments_ids.append(value[0])
                scores.append(value[1])

        queries = [self._convert_to_tensor(
            query, tokenizer, model) for query in queries]

        tf_dataset = tf.data.Dataset.from_tensor_slices(
            {'queries': queries, 'equipments_ids': equipments_ids, 'scores': scores})

        shuffled = tf_dataset.shuffle(
            100_000, seed=42, reshuffle_each_iteration=False)
        dataset_size = len(shuffled)

        train_size = int(0.8 * dataset_size)
        test_size = int(0.2 * dataset_size)

        train = shuffled.take(train_size)
        test = shuffled.skip(train_size).take(test_size)

        return (train, test)

    def train(self, clicks: Feedback, tokenizer, model):

        train, test = self._build_dataset(clicks, tokenizer, model)

        cached_train = train.shuffle(100_000).batch(8192).cache()
        cached_test = test.batch(4096).cache()

        self.compile(optimizer=tf.keras.optimizers.Adagrad(
            learning_rate=self.learning_rate))

        self.fit(cached_train, epochs=self.training_epochs)

        self.evaluate(cached_test, return_dict=True)


class RankingModel(tf.keras.Model):

    def __init__(self, unique_equipments_ids):

        super().__init__()

        embedding_dim = 768

        self.equipment_embeddings = tf.keras.Sequential([
            tf.keras.layers.experimental.preprocessing.StringLookup(
                vocabulary=unique_equipments_ids, mask_token=None),
            tf.keras.layers.Embedding(
                len(unique_equipments_ids) + 1, embedding_dim)
        ])

        self.rankings = tf.keras.Sequential([

            tf.keras.layers.Dense(256, activation=tf.keras.activations.relu,
                                  kernel_initializer=tf.keras.initializers.glorot_uniform),
            tf.keras.layers.Dense(128, activation=tf.keras.activations.relu,
                                  kernel_initializer=tf.keras.initializers.glorot_uniform),
            tf.keras.layers.Dense(1)
        ])

    def call(self, query_output, equipment_id):

        query_rank = len(tf.shape(query_output))

        equipment_embedding = self.equipment_embeddings(equipment_id)

        if query_rank == 3:

            equipment_embedding = tf.expand_dims(equipment_embedding, axis=1)

        else:

            equipment_embedding = tf.expand_dims(equipment_embedding, axis=0)
            equipment_embedding = tf.expand_dims(equipment_embedding, axis=0)
            query_output = tf.expand_dims(query_output, axis=0)

        x = tf.concat([query_output, equipment_embedding], axis=-1)

        return self.rankings(x)
