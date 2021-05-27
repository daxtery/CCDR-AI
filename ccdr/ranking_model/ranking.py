from collections import defaultdict
from typing import Any, Callable, Counter, Dict, Iterator, List, Sequence, Tuple, Iterable
import tensorflow as tf
from transformers import AutoTokenizer, TFBertModel


def argsort(seq: Sequence):
    # http://stackoverflow.com/questions/3071415/efficient-method-to-calculate-the-rank-vector-of-a-list-in-python
    return sorted(range(len(seq)), key=seq.__getitem__)


class RankingExtension:
    def __init__(self, tokenizer_name: str, model_name: str, ranker_factory: Callable[[], "RankingModel"]):
        self.stringuified_equipment_tf_output: Dict[str, Any] = {}

        self.tokenizer = AutoTokenizer.from_pretrained(
            tokenizer_name)

        self.model = TFBertModel.from_pretrained(
            model_name, from_pt=True)

        self.ranker_factory = ranker_factory
        self.ranker = ranker_factory()

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
                query_output, self.stringuified_equipment_tf_output[tag]
            )
            scores.append(score)

        indexes = argsort(scores)

        return {
            equipment_tags[index]: scores[index]
            for index in indexes
        }

    def learn(self, clicks: Dict[str, List[Tuple[str, bool]]]):
        # NOTE: This method can run at the same time as a call to rank()
        # Which means, we have to keep a self.ranker in "sync"
        # The solution found was having a ranker factory and create one
        # here; only when ready do we set it to self.ranker
        new_ranker = self.ranker_factory()

        # ...

        new_ranker.train(clicks)

        self.ranker = new_ranker
        pass


class RankingModel(tf.keras.Model):

    def __init__(self):

        super().__init__()

        self.ranking_net = tf.keras.Sequential([

            tf.keras.layers.Dense(256, activation=tf.keras.activations.relu,
                                  kernel_initializer=tf.keras.initializers.glorot_uniform),
            tf.keras.layers.Dense(128, activation=tf.keras.activations.relu,
                                  kernel_initializer=tf.keras.initializers.glorot_uniform),
            tf.keras.layers.Dense(1)
        ])

    def __call__(self, query_output, equipment_output) -> float:
        x = tf.concat([query_output, equipment_output], axis=-1)
        score = self.ranking_net(x)
        return score.numpy()[0][0]  # type: ignore

    def train(self, clicks: Dict[str, List[Tuple[str, bool]]]):
        pass
