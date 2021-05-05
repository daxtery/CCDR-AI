from typing import Iterable, List, Tuple

from interference.transformers.transformer_pipeline import TransformerPipeline, Instance

import numpy
from sentence_transformers import SentenceTransformer

from ccdr.models.equipment import Equipment, stringify


class EquipmentTypeTransformer(TransformerPipeline[Equipment]):

    def __init__(self, modelname: str = 'neuralmind/bert-large-portuguese-cased'):
        self.model = SentenceTransformer(modelname)

    def calculate_embedding(self, equipment: Equipment):
        return self.model.encode(equipment.type_)


class StringuifyEquipmentTransformer(TransformerPipeline[Equipment]):

    def __init__(self, modelname: str = 'neuralmind/bert-large-portuguese-cased'):
        self.model = SentenceTransformer(modelname)

    def calculate_embedding(self, equipment: Equipment):
        stringuified = stringify(equipment)
        return self.model.encode(stringuified)
