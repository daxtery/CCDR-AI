from trigger.scoring import TriggerScoringCalculator
from trigger.test.trigger_test_runner import TriggerTestRunner
from data.operations_instances_ss_confirmed import fetch_operations_files
import logging

from interference.clusters.fake import Fake
from trigger.operation import read_operations


logger = logging.getLogger('fake_tests')
logger.setLevel(logging.WARNING)

def test_fake():

    param_grid = {}

    for operations_file in fetch_operations_files():

        logger.info("Doing operations @ %s", operations_file)

        TriggerTestRunner(
            processor_class=Fake,
            param_grid=param_grid,
            operations=read_operations(operations_file.full_path),
            scoring_calculator=TriggerScoringCalculator(),
            output_base_folder=f"results/openings_users/operations/{operations_file.test_subpath}",
            skip_done=True,
        ).run_tests()