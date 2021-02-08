from trigger.test.covariance_test import test_cov
from trigger.test.ecm_tests import test_ecm
from trigger.test.gng_test import test_gng


if __name__ == "__main__":
    test_ecm()
    test_gng()
    test_cov()