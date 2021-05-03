from typing import Iterable, List, Tuple

from interference.transformers.transformer_pipeline import TransformerPipeline, Instance

import numpy
from sentence_transformers import SentenceTransformer

from ccdr.models.equipment import Equipment, stringify


class EquipmentTypeTransformer(TransformerPipeline[Equipment]):

    def __init__(self, modelname: str = 'neuralmind/bert-large-portuguese-cased'):
        self.model = SentenceTransformer(modelname)

    def calculate_embedding(self, equipment: Equipment):
        _type = self.extract_type(equipment)
        return self.model.encode(_type)

    def extract_type(self, equipment: Equipment):
        return "TODO:"


class StringuifyEquipmentTransformer(TransformerPipeline[Equipment]):

    def __init__(self, modelname: str = 'neuralmind/bert-large-portuguese-cased'):
        self.model = SentenceTransformer(modelname)

    def calculate_embedding(self, equipment: Equipment):
        stringuified = stringify(equipment)
        return self.model.encode(stringuified)
