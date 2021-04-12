from typing import Iterable, List, Tuple

from interference.transformers.transformer_pipeline import TransformerPipeline, Instance

import numpy
from sentence_transformers import SentenceTransformer

from ccdr.models.equipment import Equipment
from dataclasses import asdict

class EquipmentTransformer(TransformerPipeline[Equipment]):

    def __init__(self, modelname: str = 'neuralmind/bert-large-portuguese-cased'):
        self.model = SentenceTransformer(modelname)

    def calculate_embedding(self, equipment: Equipment) -> numpy.ndarray:
        return self.model.encode(stringify(equipment))

    def transform(self, equipment: Equipment) -> Instance[Equipment]:
        embedding = self.calculate_embedding(equipment)
        return Instance(equipment, embedding)

# TODO: Keep this?
def stringify(equipment: Equipment) -> str:
    return str(asdict(equipment))