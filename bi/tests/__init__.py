
from unittest import TestSuite
from bi.tests.common import suite as CommonSuite

def suite():
    test_suites = []
    test_suites.extend(CommonSuite())

    return TestSuite(test_suites)
