
from unittest import TestLoader
from unittest import TestSuite

import test_column

def suite():
    return TestSuite((TestLoader().loadTestsFromTestCase(test_column.TestColumnType),))

