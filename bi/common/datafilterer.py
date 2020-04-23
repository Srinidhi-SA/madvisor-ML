from pyspark.ml.feature import Bucketizer
from pyspark.sql.dataframe import DataFrame
from pyspark.sql.functions import col
from pyspark.sql.types import DoubleType

from utils import accepts


#import bi.common.dataframe

class DataFrameFilterer:
    @accepts(object,DataFrame)
    def __init__(self, dataframe):
        self._data_frame = dataframe

    def bucketize(self, splits, target_col):
        self._bucket_name = 'bucket_'+target_col
        bucketizer = Bucketizer(inputCol=target_col,
                                outputCol=self._bucket_name)
        splits.sort()
        bucketizer.setSplits(splits)
        column_data_types = {field.name: field.dataType for field in self._data_frame.schema.fields}
        if column_data_types[target_col] != DoubleType:
            self._data_frame = self._data_frame.select(*[col(target_col).cast('double').alias(target_col) if column==target_col else column for column in self._data_frame.columns])
        self._data_frame = bucketizer.transform(self._data_frame)
        return self._bucket_name

    def values_between(self,colname,start_value, end_value, greater_than_equal = 0, less_than_equal=1):
        if (greater_than_equal == 0) and (less_than_equal==1):
            self._data_frame = self._data_frame.filter(col(colname) > start_value).filter(col(colname) <= end_value)
        elif (greater_than_equal == 0) and (less_than_equal==0):
            self._data_frame = self._data_frame.filter(col(colname) > start_value).filter(col(colname) < end_value)
        elif (greater_than_equal == 1) and (less_than_equal==1):
            self._data_frame = self._data_frame.filter(col(colname) >= start_value).filter(col(colname) <= end_value)
        elif (greater_than_equal == 1) and (less_than_equal==0):
            self._data_frame = self._data_frame.filter(col(colname) >= start_value).filter(col(colname) < end_value)

    def dates_between(self,colname,start_value, end_value, greater_than_equal = 1, less_than_equal=1):
        if (greater_than_equal == 0) and (less_than_equal==1):
            self._data_frame = self._data_frame.filter(col(colname) > start_value and col(colname) <= end_value)
        elif (greater_than_equal == 0) and (less_than_equal==0):
            self._data_frame = self._data_frame.filter(col(colname) > start_value and col(colname) < end_value)
        elif (greater_than_equal == 1) and (less_than_equal==1):
            self._data_frame = self._data_frame.filter(col(colname) >= start_value and col(colname) <= end_value)
        elif (greater_than_equal == 1) and (less_than_equal==0):
            self._data_frame = self._data_frame.filter(col(colname) >= start_value and col(colname) < end_value)

    def values_above(self,colname, start_value, greater_than_equal=0):
        if greater_than_equal == 0:
            self._data_frame = self._data_frame.filter(col(colname) > start_value)
        elif greater_than_equal == 1:
            self._data_frame = self._data_frame.filter(col(colname) >= start_value)

    def values_below(self, colname, end_value, less_than_equal=1):
        if less_than_equal==0:
            self._data_frame = self._data_frame.filter(col(colname) < end_value)
        elif less_than_equal==1:
            self._data_frame = self._data_frame.filter(col(colname) <= end_value)

    def values_in(self, colname, values):
        if type(values) == str:
            values = values[1:-1]
            values = values.split(',')
        self._data_frame = self._data_frame.where(col(colname).isin(values))

    def values_not_in(self, colname, values):
        if type(values) == str:
            values = values[1:-1]
            values = values.split(',')
        self._data_frame = self._data_frame.where(col(colname).isin(values)==False)

    def get_aggregated_result(self, colname, target):
        return self._data_frame.select(colname).groupBy(colname).agg({'*': 'count'}).collect()

    def get_filtered_data_frame(self):
        return self._data_frame
