from dataclasses import dataclass, field
from typing import Any, Dict

from ccdr.models.equipment import Equipment
from ccdr.models.user_query import UserQuery

from interference.scoring import ScoringOptions, Scoring, ScoringCalculator
from interference.transformers.transformer_pipeline import Instance


@dataclass()
class ToyScoringOptions(ScoringOptions):
    pass


@dataclass()
class ToyScoring(Scoring):
    pass


class ToyScoringCalculator(ScoringCalculator):

    def __init__(self, scoring_options: ToyScoringOptions = ToyScoringOptions()):
        self.scoring_options = scoring_options

    def __call__(
        self,
        user_query_instance: Instance[UserQuery],
        equipment_instance: Instance[Equipment]
    ) -> ToyScoring:

        base_scoring: Scoring = ScoringCalculator.__call__(
            self, user_query_instance, equipment_instance)

        return ToyScoring(
            base_scoring.similarity_score,
            base_scoring.is_match,
        )

    def describe(self) -> Dict[str, Any]:
        return {
            "scoring_options": self.scoring_options,
            "scoring": [
                "similarity_metric(instance1.embedding, instance2.embedding)",
            ]
        }
