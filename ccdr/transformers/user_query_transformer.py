from interference.transformers.transformer_pipeline import TransformerPipeline, Instance

from sentence_transformers import SentenceTransformer


class TypeTransformer(TransformerPipeline[str]):

    def __init__(
        self,
        modelname: str = 'neuralmind/bert-large-portuguese-cased'
    ):
        self.model = SentenceTransformer(modelname)

    def calculate_embedding(self, _type: str):
        return self.model.encode(_type)
