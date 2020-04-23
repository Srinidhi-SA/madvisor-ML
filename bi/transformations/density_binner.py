from pyspark.ml.feature import Bucketizer
from pyspark.ml.feature import QuantileDiscretizer
from pyspark.sql import functions as FN
from pyspark.sql.types import DoubleType

from bi.common import BIException
from bi.common.decorators import accepts
from bi.common.results import DataFrameHistogram
from bi.common.results import Histogram

"""
Constants for Binner classes
"""


class DensityBinner:
    """
    Utility class for binning numeric columns of a data frame
    """
    def __init__(self, data_frame, dataframe_helper):
        self._data_frame = data_frame
        self._numeric_columns = dataframe_helper.get_numeric_columns()
        self._column_data_types = dataframe_helper.get_column_data_types()
        self._num_rows = dataframe_helper.get_num_rows()

    @accepts(object, num_bins=int)
    def get_bins_for_all_measure_columns(self, num_bins=10):
        """
        TODO: 1) df is procssed twice for every column, better process df only once for all columns

        :param num_bins:
        :return:
        """
        dataframe_histogram = DataFrameHistogram()
        for column_name in self._numeric_columns:
            binned_column_resut = self.get_bins(column_name, num_bins=num_bins)
            dataframe_histogram.add_histogram(binned_column_resut)

        return dataframe_histogram

    @accepts(object, basestring, num_bins=int, split_points=(list, tuple))
    def get_bins(self, column_name, num_bins=10, split_points=None):
        """
        Finds number of items in each bin. Only one of the params num_bins ot split_points need to be supplied.

        :param column_name: column to be binned
        :param num_bins:    number of bins to create
        :param split_points:    list of tupels [(a,b), (b, c), ...] such that
                                all values in the range [a, b) assigned to bucket1
        :return:
        """
        if not column_name in self._numeric_columns:
            raise BIException.column_does_not_exist(column_name)

        splits = None
        if split_points == None:
            min_max = self._data_frame.agg(FN.min(column_name).alias('min'), FN.max(column_name).alias('max')).collect()
            min_value = min_max[0]['min']
            max_value = min_max[0]['max']
            quantile_discretizer = QuantileDiscretizer(numBuckets=10, inputCol=column_name,
                                                       outputCol='buckets',
                                                       relativeError=0.01)
            bucketizer = quantile_discretizer.fit(self._data_frame)
            # splits have these values [-Inf, Q1, Median, Q3, Inf]
            splits = bucketizer.getSplits()
        else:
            splits = split_points
        # cast column_name to double type if needed, otherwise Bucketizer does not work
        splits[0] = min_value-0.1
        splits[-1] = max_value+0.1
        column_df = None
        if self._column_data_types.get(column_name) != DoubleType:
            column_df = self._data_frame.select(
                FN.col(column_name).cast('double').alias('values'))
        else:
            column_df = self._data_frame.select(FN.col(column_name).alias('values'))

        bucketizer = Bucketizer(inputCol='values',
                                outputCol='bins')
        bucketizer.setSplits(splits)
        if min_value==max_value:
            histogram = Histogram(column_name, self._num_rows)
            bin_number = 0
            start_value = min_value-0.5
            end_value = max_value+0.5
            histogram.add_bin(bin_number, start_value, end_value, self._num_rows)
        else:
            buckets_and_counts = bucketizer.transform(column_df).groupBy('bins').agg(
                {'*': 'count'}).collect()
            histogram = Histogram(column_name, self._num_rows)
            for row in buckets_and_counts:
                bin_number = int(row[0])
                start_value = splits[bin_number]
                end_value = splits[bin_number + 1]
                histogram.add_bin(bin_number, start_value, end_value, float(row[1])*100.0/(end_value-start_value))

        return histogram
