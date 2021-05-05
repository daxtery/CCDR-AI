from typing import Iterable, List, Tuple, Optional
from typing_extensions import Literal, Final

from interference.transformers.transformer_pipeline import TransformerPipeline, Instance

from sentence_transformers import SentenceTransformer

from ccdr.models.user_query import UserQuery


class TypeTransformer(TransformerPipeline[str]):

    def __init__(
        self,
        modelname: str = 'neuralmind/bert-large-portuguese-cased'
    ):
        self.model = SentenceTransformer(modelname)

    def calculate_embedding(self, _type: str):
        return self.model.encode(_type)


class UserQueryTransformer(TransformerPipeline[UserQuery]):

    def __init__(self, modelname: str = 'neuralmind/bert-large-portuguese-cased'):
        self.model = SentenceTransformer(modelname)

    def calculate_embedding(self,  user_query: UserQuery):
        return self.model.encode(user_query.query)
