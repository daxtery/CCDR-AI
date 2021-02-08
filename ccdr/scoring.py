from dataclasses import dataclass, field
from typing import Any, Dict

from trigger.metrics.match import quality_metric, real_metric
from trigger.models.user import User
from trigger.models.opening import Opening

from interference.scoring import ScoringOptions, Scoring, ScoringCalculator
from interference.transformers.transformer_pipeline import Instance


@dataclass()
class CCDRScoringOptions(ScoringOptions):
    similarity_weight: float = .5
    quality_weight: float = .5
    quality_metric_hardskill_weight: float = .6
    quality_metric_softskill_weight: float = .4


@dataclass()
class CCDRScoring(Scoring):
    quality_score: float
    is_quality_match: bool = field(repr=False)

    real_score: float
    is_real_match: bool = field(repr=False)

    @property
    def is_match(self) -> bool:
        return self.is_real_match

    @property
    def score(self) -> float:
        return self.real_score


class CCDRScoringCalculator(ScoringCalculator):

    def __init__(self, scoring_options: CCDRScoringOptions = CCDRScoringOptions()):
        self.scoring_options = scoring_options

    def __call__(
        self,
        user_instance: Instance[User],
        opening_instance: Instance[Opening]
    ) -> CCDRScoring:

        base_scoring: Scoring = ScoringCalculator.__call__(
            self, user_instance, opening_instance)

        quality_score = quality_metric(
            user_instance.value,
            opening_instance.value,
            self.scoring_options.quality_metric_hardskill_weight,
            self.scoring_options.quality_metric_softskill_weight
        )

        real_score = real_metric(
            base_scoring.similarity_score,
            quality_score,
            self.scoring_options.similarity_weight,
            self.scoring_options.quality_weight
        )

        return CCDRScoring(
            base_scoring.similarity_score,
            base_scoring.is_match,
            quality_score,
            quality_score >= self.scoring_options.score_to_be_match,
            real_score,
            real_score >= self.scoring_options.score_to_be_match
        )

    def describe(self) -> Dict[str, Any]:
        return {
            "scoring_options": self.scoring_options,
            "scoring": [
                "similarity_score = similarity_metric(instance1.embedding, instance2.embedding)",
                f"quality_score = quality_metric(instance1.user, instance2.opening, {self.scoring_options.quality_metric_hardskill_weight}, {self.scoring_options.quality_metric_softskill_weight})",
                f"real_metric(similarity_score, quality_score, {self.scoring_options.similarity_weight}, {self.scoring_options.quality_weight})",
            ]
        }
