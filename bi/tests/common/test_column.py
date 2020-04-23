
import unittest

from pyspark.sql.types import ArrayType
from pyspark.sql.types import BinaryType
from pyspark.sql.types import DateType
from pyspark.sql.types import DecimalType
from pyspark.sql.types import DoubleType
from pyspark.sql.types import FloatType
from pyspark.sql.types import IntegerType
from pyspark.sql.types import LongType
from pyspark.sql.types import ShortType
from pyspark.sql.types import StringType
from pyspark.sql.types import TimestampType

from bi.common.column import ColumnType


class TestColumnType(unittest.TestCase):
    """Test cases for testing functionality of bi.commom.column.ColumnType

    """

    def setup(self):
        pass

    def tearDown(self):
        pass

    def test_measure_types(self):
        ## Binary type test
        self.assertEqual(ColumnType(BinaryType).get_abstract_data_type(), ColumnType.MEASURE)
        ## Integer type test
        self.assertEqual(ColumnType(IntegerType).get_abstract_data_type(), ColumnType.MEASURE)
        ## Long Type
        self.assertEqual(ColumnType(LongType).get_abstract_data_type(), ColumnType.MEASURE)
        ## short type
        self.assertEqual(ColumnType(ShortType).get_abstract_data_type(), ColumnType.MEASURE)
        ## Decimal type
        self.assertEqual(ColumnType(DecimalType).get_abstract_data_type(), ColumnType.MEASURE)
        ## Double type
        self.assertEqual(ColumnType(DoubleType).get_abstract_data_type(), ColumnType.MEASURE)
        ## Float Type
        self.assertEqual(ColumnType(FloatType).get_abstract_data_type(), ColumnType.MEASURE)

    def test_dimension_types(self):
        ## string type
        self.assertEqual(ColumnType(StringType).get_abstract_data_type(), ColumnType.DIMENSION)

    def test_time_dimension_type(self):
        ## date type
        self.assertEqual(ColumnType(DateType).get_abstract_data_type(), ColumnType.TIME_DIMENSION)
        ## timestamp type
        self.assertEqual(ColumnType(TimestampType).get_abstract_data_type(), ColumnType.TIME_DIMENSION)

    def test_unknown_type(self):
        self.assertEqual(ColumnType(ArrayType).get_abstract_data_type(), ColumnType.UNKNOWN)


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestColumnType)
    unittest.TextTestRunner(verbosity=2).run(suite)
