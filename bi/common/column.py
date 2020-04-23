from pyspark.sql.types import BinaryType
from pyspark.sql.types import BooleanType
from pyspark.sql.types import DateType
from pyspark.sql.types import DecimalType
from pyspark.sql.types import DoubleType
from pyspark.sql.types import FloatType
from pyspark.sql.types import IntegerType
from pyspark.sql.types import LongType
from pyspark.sql.types import ShortType
from pyspark.sql.types import StringType
from pyspark.sql.types import TimestampType


class ColumnType:
    """
    Kind of data a column, in a data frame, holds
    """
    UNKNOWN = 'UNKNOWN'
    # variable types
    MEASURE = 'Measure'
    DIMENSION = 'Dimension'
    TIME_DIMENSION = 'TimeDimension'
    BOOLEAN = 'Boolean'
    # actual data types generalized
    INTEGER = 'INTEGER'
    REAL = 'REAL NUMBER'
    STRING = 'STRING'
    DATE = 'DATE'
    TIME_STAMP = 'TIME STAMP'
    BOOL = 'BOOLEAN'

    def __init__(self, data_type):
        self._data_type = data_type
        self._actual_data_type = None
        self._abstract_data_type = None
        self._set_actual_and_abstract_types()

    def _set_actual_and_abstract_types(self):
        if self._data_type in (BinaryType, IntegerType, LongType, ShortType):
            self._actual_data_type = ColumnType.INTEGER
            self._abstract_data_type = ColumnType.MEASURE

        elif self._data_type in (DecimalType, DoubleType, FloatType):
            self._actual_data_type = ColumnType.REAL
            self._abstract_data_type = ColumnType.MEASURE

        elif self._data_type in (StringType, ):
            self._actual_data_type = ColumnType.STRING
            self._abstract_data_type = ColumnType.DIMENSION

        elif self._data_type in (DateType,):
            self._actual_data_type = ColumnType.DATE
            self._abstract_data_type = ColumnType.TIME_DIMENSION

        elif self._data_type in (TimestampType,):
            self._actual_data_type = ColumnType.TIME_STAMP
            self._abstract_data_type = ColumnType.TIME_DIMENSION

        elif self._data_type in (BooleanType, ):
            self._actual_data_type = ColumnType.BOOL
            self._abstract_data_type = ColumnType.BOOLEAN

        else:
            self._actual_data_type = ColumnType.UNKNOWN
            self._abstract_data_type = ColumnType.UNKNOWN

    def get_actual_data_type(self):
        return self._actual_data_type

    def get_abstract_data_type(self):
        return self._abstract_data_type
