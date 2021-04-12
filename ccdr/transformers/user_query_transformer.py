from typing import Iterable, List, Tuple

from interference.transformers.transformer_pipeline import TransformerPipeline, Instance

import numpy
from sentence_transformers import SentenceTransformer

from ccdr.models.user_query import UserQuery


class UserQueryTransformer(TransformerPipeline[UserQuery]):

    def __init__(self, modelname: str = 'neuralmind/bert-large-portuguese-cased'):
        self.model = SentenceTransformer(modelname)

    def calculate_embedding(self, user_query: UserQuery) -> numpy.ndarray:
        return self.model.encode(user_query.query)

    def transform(self, user_query: UserQuery) -> Instance[UserQuery]:
        embedding = self.calculate_embedding(user_query)
        return Instance(user_query, embedding)
