from datetime import datetime

from pyspark.sql import functions as FN
from pyspark.sql.dataframe import DataFrame
from pyspark.sql.types import DateType
from pyspark.sql.types import TimestampType

from dataframe import DataFrameHelper
from utils import accepts


class DataType:
    STRING = 'string'
    DATE = 'date'
    TIMESTAMP = 'timestamp'


class ColumnTypeConversion:
    """
    Encapsulates information required for type casting a column
    """

    @accepts(object, (str, basestring), (str, basestring), (str, basestring), (str, basestring))
    def __init__(self, orig_column_name, orig_column_type, orig_column_data_format, required_column_type):
        self._orig_column_name = orig_column_name
        self._orig_column_type = orig_column_type
        self._orig_column_data_format = orig_column_data_format
        self._required_column_type = required_column_type

    def get_original_column_name(self):
        return self._orig_column_name

    def get_original_column_type(self):
        return self._orig_column_type

    def get_original_column_data_format(self):
        return self._orig_column_data_format

    def get_required_column_type(self):
        return self._required_column_type


class DataCleanser:
    """
    Cleanses a data frame as pre user requirement.
    At present, supports three kinds of cleansing operations:
        1) column type transformation:
            1.1) string to date type conversion
            1.2) string to timestamp conversion
        2) column omission: unnecessary columns like, id and descriptive text columns
            can be removed altogether from a data frame.
        3) Null row omission: All rows containing null values in ANY one or ALL columns
            will be removed from a dataframe.
    """

    ANY_COLUMN_IS_NULL = 'any'
    ALL_COLUMNS_ARE_NULL = 'all'

    @accepts(object, DataFrame, DataFrameHelper)
    def __init__(self, data_frame, df_helper):
        self._data_frame = data_frame
        self._dataframe_helper = df_helper
        self._transformations = {}  # column_name -> ColumnTypeConversion(...)
        self._columns_to_remove = []
        self._remove_null_rows = False
        self._remove_null_row_type = DataCleanser.ANY_COLUMN_IS_NULL

    @accepts(object, (str, basestring), (str, basestring), (DateType, TimestampType))
    def type_cast_string_column(self, column_name, orig_column_data_format, required_column_type):
        # column_name does not exist => ignore
        if not self._dataframe_helper.has_column(column_name):
            return

        if type(required_column_type) == DateType:
            self._transformations[column_name] = ColumnTypeConversion(column_name, DataType.STRING,
                                                                      orig_column_data_format, DataType.DATE)
        elif type(required_column_type) == TimestampType:
            self._transformations[column_name] = ColumnTypeConversion(column_name, DataType.STRING,
                                                                      orig_column_data_format, DataType.TIMESTAMP)

    @accepts(object, (str, basestring))
    def remove_column(self, column_name):
        # column_name does not exist => ignore
        if not self._dataframe_helper.has_column(column_name):
            return
        if self._transformations.has_key(column_name):
            del self._transformations[column_name]
        if column_name not in self._columns_to_remove:
            self._columns_to_remove.append(column_name)

    @accepts(object, all_columns_null=bool)
    def remove_null_rows(self, all_columns_null=True):
        self._remove_null_rows = True
        if all_columns_null:
            self._remove_null_row_type = DataCleanser.ALL_COLUMNS_ARE_NULL
        else:
            self._remove_null_row_type = DataCleanser.ANY_COLUMN_IS_NULL

    def transform(self):
        """
        :return:
        """
        for column_name in self._columns_to_remove:
            if self._transformations.has_key(column_name):
                del self._transformations[column_name]

        columns_to_retain = [column for column in self._dataframe_helper.get_columns() if
                             column not in self._columns_to_remove]

        columns_to_transform = self._transformations.keys()
        column_expressions = []
        for column_name in columns_to_retain:
            if self._transformations.has_key(column_name):
                column_expressions.append(self._column_type_casting_expression(self._transformations.get(column_name)))
            else:
                column_expressions.append(FN.col(column_name))

        # rows containing null value in any column being type cast be omitted first
        transformed_df = self._data_frame.dropna(how=DataCleanser.ANY_COLUMN_IS_NULL,
                                                 subset=columns_to_transform).select(*column_expressions).cache()
        if not self._remove_null_rows:
            return transformed_df

        return transformed_df.dropna(how=self._remove_null_row_type)

    @accepts(object, ColumnTypeConversion)
    def _column_type_casting_expression(self, column_type_conversion):
        orig_column_name = column_type_conversion.get_original_column_name()
        orig_column_type = column_type_conversion.get_original_column_type()
        orig_column_format = column_type_conversion.get_original_column_data_format()
        required_column_type = column_type_conversion.get_required_column_type()

        if orig_column_type == DataType.STRING:
            if required_column_type == DataType.DATE:
                user_def_fn = self._string_to_date_fn(orig_column_format)
                return user_def_fn(FN.col(orig_column_name)).alias(orig_column_name)

            if required_column_type == DataType.TIMESTAMP:
                user_def_fn = self._string_to_timestamp_fn(orig_column_format)
                return user_def_fn(FN.col(orig_column_name)).alias(orig_column_name)


        # print 'Some thing wrong...', orig_column_name, orig_column_type, orig_column_format, required_column_type
        return None

    def _string_to_date_fn(self, format):
        return FN.udf(lambda x: datetime.strptime(x, format), DateType())

    def _string_to_timestamp_fn(self, format):
        return FN.udf(lambda x: datetime.strptime(x, format), TimestampType())
