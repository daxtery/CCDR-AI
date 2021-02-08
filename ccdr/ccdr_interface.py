from trigger.models.user import User
from trigger.models.opening import Opening
from trigger.scoring import TriggerScoring, TriggerScoringCalculator
from trigger.evaluation.matches import eval_matches
from typing import Any, Dict, List, Optional, Sequence, Type, TypeVar, cast
from interference.interface import Interface
from interference.operations import CalculateMatchesInfo
from interference.scoring import Scoring
from interference.transformers.transformer_pipeline import TransformerPipeline, Instance
from interference.clusters.processor import Processor
import numpy

T = TypeVar('T')
U = TypeVar('U')


class CCDRInterface(Interface):

    def __init__(
        self,
        processor: Processor,
        transformers: Dict[str, TransformerPipeline],
        scoring_calculator: TriggerScoringCalculator
    ) -> None:
        super().__init__(processor, transformers, scoring_calculator=scoring_calculator)
        self.scoring_calculator = scoring_calculator

    def _evaluate_matches_inner(self, values: List[CalculateMatchesInfo]):
        instances, scorings = self._calculate_operation_matches_inner(values)
        # Don't worry, they are trigger scorings :)
        scorings = cast(Sequence[Sequence[TriggerScoring]], scorings)
        return eval_matches(instances, scorings)
