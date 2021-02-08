import logging
from trigger.scoring import TriggerScoringCalculator
from trigger.operation import read_operations

from interference.clusters.covariance import CovarianceCluster
from trigger.test.trigger_test_runner import TriggerTestRunner
from data.operations_instances_ss_confirmed import fetch_operations_files

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('covariance_tests')
logger.setLevel(logging.INFO)

def test_cov():

    param_grid = {
        "initial_std": [10],
        "dimensions": [1024],
    }

    for operations_file in fetch_operations_files():

        logger.info("Doing operations @ %s", operations_file)

        if operations_file.layer.find("concat") != -1:
            param_grid["dimensions"] = [2048]
        else:
            param_grid["dimensions"] = [1024]

        TriggerTestRunner(
            processor_class = CovarianceCluster,
            param_grid=param_grid,
            operations=read_operations(operations_file.full_path),
            scoring_calculator=TriggerScoringCalculator(),
            output_base_folder=f"results/openings_users/operations/{operations_file.test_subpath}",
        ).run_tests()