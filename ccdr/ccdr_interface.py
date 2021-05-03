from typing import Any, Dict, List, Optional, Sequence, Type, TypeVar, cast, overload

from ccdr.models.equipment import Equipment
from ccdr.models.user_query import UserQuery

from interference.interface import Interface
from interference.transformers.transformer_pipeline import TransformerPipeline, Instance
from interference.clusters.processor import Processor
from interference.scoring import ScoringCalculator

from typing_extensions import TypedDict


class TransformersDict(TypedDict):
    equipment: TransformerPipeline[Equipment]
    query: TransformerPipeline[UserQuery]
