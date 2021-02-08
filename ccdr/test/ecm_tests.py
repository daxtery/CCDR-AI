import logging

from trigger.scoring import TriggerScoringCalculator
from trigger.operation import read_operations

from interference.clusters.ecm import ECM
from trigger.test.trigger_test_runner import TriggerTestRunner
from data.operations_instances_ss_confirmed import fetch_operations_files

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('ecm_tests')
logger.setLevel(logging.INFO)

def test_ecm():

    param_grid = {
        "distance_threshold": [0.001, 0.01, 0.1, 0.3, 0.5,
                               0.7, 0.9, 1, 1.2, 1.4, 1.5]
    }

    for operations_file in fetch_operations_files():

        logger.info("Doing operations @ %s", operations_file)

        TriggerTestRunner(
            processor_class=ECM,
            param_grid=param_grid,
            operations=read_operations(operations_file.full_path),
            scoring_calculator=TriggerScoringCalculator(),
            output_base_folder=f"results/openings_users/operations/{operations_file.test_subpath}",
        ).run_tests()