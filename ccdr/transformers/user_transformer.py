from typing import Iterable, List, Tuple
from trigger.transformers.opening_transformer import LAYER
from trigger.transformers.input_transformer import SentenceEmbedder
from trigger.instances.user_instance import UserInstance
from interference.transformers.transformer_pipeline import TransformerPipeline, Instance

from typing_extensions import Final

import tensorflow as tf
import numpy

from ..models.user import User


class UserTransformer(TransformerPipeline[User]):

    def __init__(self, sentenceEmbedder: SentenceEmbedder = SentenceEmbedder(), layer: LAYER = 'avg', normed: bool = False):
        self.sentenceEmbedder = sentenceEmbedder
        self.layer: Final[LAYER] = layer
        self.normed = normed

    def calculate_embedding(self, user: User) -> numpy.ndarray:
        
        hardSkillsEmbedding = self.sentenceEmbedder.generateEmbeddingsFromList(user.hardSkills)

        softSkillsEmbedding = self.sentenceEmbedder.generateEmbeddingsFromList(user.softSkills)

        if self.layer == 'avg':
            jointEmbedding = tf.keras.layers.Average()([hardSkillsEmbedding, softSkillsEmbedding])

        elif self.layer == 'concat':
            jointEmbedding = tf.keras.layers.concatenate([hardSkillsEmbedding, softSkillsEmbedding])

        elif self.layer == 'no_ss':
            jointEmbedding = hardSkillsEmbedding

        if self.layer == 'no_ss':
            resultingEmbedding = jointEmbedding
            
        else:
            resultingEmbedding = jointEmbedding.numpy()

        if self.normed and not numpy.isnan(resultingEmbedding).any():

            resultingEmbedding = resultingEmbedding / numpy.linalg.norm(resultingEmbedding)

        return resultingEmbedding

    def transform(self, user: User) -> UserInstance:
        embedding = self.calculate_embedding(user)
        return UserInstance(user, embedding)

def transform_users_using_layers(
    openings: List[User],
    layers: List[LAYER] = ['avg', 'concat', 'no_ss'],
    normed_options: List[bool] = [True, False]
) -> Iterable[Tuple[LAYER, bool, List[UserInstance]]]:
    for layer in layers:
        for normed_option in normed_options:
            transformer = UserTransformer(layer=layer, normed=normed_option)

            yield layer, normed_option, [
                transformer.transform(opening)
                for opening in openings
            ]