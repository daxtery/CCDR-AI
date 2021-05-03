from typing import Iterable, List, Tuple

from interference.transformers.transformer_pipeline import TransformerPipeline, Instance

import numpy
from sentence_transformers import SentenceTransformer

from ccdr.models.user_query import UserQuery


class UserQueryTypeTransformer(TransformerPipeline[UserQuery]):

    def __init__(self, modelname: str = 'neuralmind/bert-large-portuguese-cased'):
        self.model = SentenceTransformer(modelname)

    def calculate_embedding(self, user_query: UserQuery):
        return self.model.encode(user_query.query)


class UserQueryTransformer(TransformerPipeline[UserQuery]):

    def __init__(self, modelname: str = 'neuralmind/bert-large-portuguese-cased'):
        self.model = SentenceTransformer(modelname)

    def calculate_embedding(self,  user_query: UserQuery):
        return self.model.encode(user_query.query)
