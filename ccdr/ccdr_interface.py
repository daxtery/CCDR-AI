from ccdr.models.equipment import Equipment
from ccdr.models.user_query import UserQuery
from ccdr.scoring import ToyScoring, ToyScoringCalculator

from typing import Any, Dict, List, Optional, Sequence, Type, TypeVar, cast

from interference.interface import Interface
from interference.operations import CalculateMatchesInfo
from interference.transformers.transformer_pipeline import TransformerPipeline, Instance
from interference.clusters.processor import Processor

import numpy

T = TypeVar('T')
U = TypeVar('U')


class ToyInterface(Interface):

    def __init__(
        self,
        processor: Processor,
        transformers: Dict[str, TransformerPipeline],
        scoring_calculator: ToyScoringCalculator
    ) -> None:
        super().__init__(processor, transformers, scoring_calculator=scoring_calculator)
        self.scoring_calculator = scoring_calculator

    def get_scorings_for(self, instance: Instance[UserQuery]) -> Sequence[ToyScoring]:
        scorings = super().get_scorings_for(instance)
        scorings = cast(Sequence[ToyScoring], scorings)
        # FIXME: Save these for later?
        return scorings