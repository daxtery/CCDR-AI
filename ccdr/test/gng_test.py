from trigger.scoring import TriggerScoringCalculator
from trigger.test.trigger_test_runner import TriggerTestRunner
from data.operations_instances_ss_confirmed import fetch_operations_files
import logging

from interference.clusters.gturbo import GTurbo
from trigger.operation import read_operations


logger = logging.getLogger('gng_tests')
logger.setLevel(logging.WARNING)

def test_gng():

    param_grid = {
                    "epsilon_b": [0.001, 0.01],
                    "epsilon_n": [0],
                    "lam": [200, 500],
                    "beta": [0.9995],
                    "alpha": [0.95],
                    "max_age": [200, 500],
                    "r0": [0.5, 1, 2.5, 5, 8]
                }

    for operations_file in fetch_operations_files():

        logger.info("Doing operations @ %s", operations_file)

        if operations_file.layer.find("concat") != -1:
            param_grid["dimensions"] = [2048]
        else:
            param_grid["dimensions"] = [1024]

        TriggerTestRunner(
            processor_class=GTurbo,
            param_grid=param_grid,
            operations=read_operations(operations_file.full_path),
            scoring_calculator=TriggerScoringCalculator(),
            output_base_folder=f"results/openings_users/operations/{operations_file.test_subpath}",
            skip_done=True,
        ).run_tests()