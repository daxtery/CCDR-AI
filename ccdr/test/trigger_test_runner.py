from trigger.transformers.opening_transformer import OpeningTransformer
from trigger.transformers.user_transformer import UserTransformer
from trigger.scoring import TriggerScoringCalculator
from typing import Any, Dict, List, Type
from trigger.trigger_interface import TriggerInterface
from interference.test.test_operations_runner import TestRunner
from interference.clusters.processor import Processor
from interference.transformers.transformer_pipeline import TransformerPipeline, NumpyToInstancePipeline, IdentityPipeline
from interference.operations import Operation


class TriggerTestRunner(TestRunner):

    def __init__(
        self,
        processor_class: Type[Processor],
        param_grid: Dict[str, Any],
        operations: List[Operation],
        transformers: Dict[str, TransformerPipeline] = {
            "numpy": NumpyToInstancePipeline(),
            "identity": IdentityPipeline(),
            "user": UserTransformer(),
            "opening": OpeningTransformer(),
        },
        scoring_calculator: TriggerScoringCalculator = TriggerScoringCalculator(),
        only_output_evaluates: bool = True,
        output_base_folder: str = "",
        use_last_folder_name_as_processor_class: bool = True,
        output_type: str = 'json',
        skip_done: bool = False,
    ):

        super().__init__(
            processor_class,
            param_grid,
            operations,
            transformers=transformers,
            scoring_calculator=scoring_calculator,
            only_output_evaluates=only_output_evaluates,
            output_base_folder=output_base_folder,
            use_last_folder_name_as_processor_class=use_last_folder_name_as_processor_class,
            output_type=output_type,
            skip_done=skip_done
        )

        self.scoring_calculator = scoring_calculator

    def init_inferface(self, params) -> TriggerInterface:
        processor = self.processor_class(**params) # type: ignore
        return TriggerInterface(processor, self.transformers, self.scoring_calculator)
