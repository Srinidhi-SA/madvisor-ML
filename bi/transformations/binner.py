from pyspark.ml.feature import Bucketizer
from pyspark.sql import functions as FN
from pyspark.sql.types import DoubleType

from bi.common import BIException
from bi.common import utils as CommonUtils
from bi.common.decorators import accepts
from bi.common.results import DataFrameHistogram
from bi.common.results import Histogram

"""
Constants for Binner classes
"""


class BinnerConstants:
    # temporary column names to use in intermediate data frames
    ORIGINAL_COLUMN_NAME = 'values'
    BINNED_COLUMN_NAME = 'bin'
    # field name constants
    BINS_FIELD = 'bins'
    NARRATIVES_FIELD = 'narratives'
    BIN_NUMBER_FIELD = 'bin_number'
    BIN_START_VALUE_FIELD = 'start_value'
    BIN_END_VALUE_FIELD = 'end_value'
    BIN_NUMBER_OF_RECORDS_FIELD = 'num_records'


class Binner:
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
            # splits = CommonUtils.frange(min_value, max_value, num_bins)
            splits = CommonUtils.return_optimum_bins(self._data_frame.select(column_name).toPandas()[column_name])
            if splits[0]>min_value:
                splits = [min_value-1]+list(splits)
                print "Min Point Added"
            if splits[-1]<max_value:
                splits = list(splits)+[max_value+1]
                print "Max Point Added"
        else:
            splits = split_points
        # cast column_name to double type if needed, otherwise Bucketizer does not work
        column_df = None
        if self._column_data_types.get(column_name) != DoubleType:
            column_df = self._data_frame.select(
                FN.col(column_name).cast('double').alias(BinnerConstants.ORIGINAL_COLUMN_NAME))
        else:
            column_df = self._data_frame.select(FN.col(column_name).alias(BinnerConstants.ORIGINAL_COLUMN_NAME))
        bucketizer = Bucketizer(inputCol=BinnerConstants.ORIGINAL_COLUMN_NAME,
                                outputCol=BinnerConstants.BINNED_COLUMN_NAME)
        bucketizer.setSplits(splits)
        if min_value==max_value:
            histogram = Histogram(column_name, self._num_rows)
            bin_number = 0
            start_value = min_value-0.5
            end_value = max_value+0.5
            histogram.add_bin(bin_number, start_value, end_value, self._num_rows)
        else:
            buckets_and_counts = bucketizer.transform(column_df).groupBy(BinnerConstants.BINNED_COLUMN_NAME).agg({'*': 'count'}).collect()
            histogram = Histogram(column_name, self._num_rows)
            for row in buckets_and_counts:
                bin_number = int(row[0])
                start_value = splits[bin_number]
                end_value = splits[bin_number + 1]
                histogram.add_bin(bin_number, start_value, end_value, row[1])

        return histogram


class BinnedColumnNarrative:
    @accepts(object, (list, tuple))
    def __init__(self, bins):
        self._bins = bins

    @accepts(object, min_freq_percentage=(int, long, float), top_n=int)
    def get_narratives(self, min_freq_percentage=50, top_n=3):
        total_freq = sum([bin.get(BinnerConstants.BIN_NUMBER_OF_RECORDS_FIELD) for bin in self._bins])
        narratives = []
        for start_index in range(0, len(self._bins)):
            for end_index in range(start_index + 1, len(self._bins)):
                freq = sum([self._bins[index].get(BinnerConstants.BIN_NUMBER_OF_RECORDS_FIELD) for index in
                            range(start_index, end_index)]) * 100.0 / total_freq

                if freq >= min_freq_percentage:
                    narratives.append({
                        'bins': [self._bins[index].get(BinnerConstants.BIN_NUMBER_FIELD) for index in
                                 range(start_index, end_index)],
                        'freq': freq
                    })

        ## consider ranges only with no more than 1/2 of total number of bins
        filtered_narratives = filter(lambda x: len(x.get('bins')) <= len(self._bins)/2, narratives)
        sorted_narratives = sorted(filtered_narratives, key=lambda x: (len(x.get('bins')), 100 - x.get('freq')))
        if len(sorted_narratives) == 0:
            return ['']
        text_narratives = []
        for narrative_obj in sorted_narratives[:top_n]:
            start_bin = \
                filter(lambda x: x.get(BinnerConstants.BIN_NUMBER_FIELD) == narrative_obj.get('bins')[0], self._bins)[0]
            end_bin = \
                filter(lambda x: x.get(BinnerConstants.BIN_NUMBER_FIELD) == narrative_obj.get('bins')[-1], self._bins)[
                    0]
            narrative_str = '%0.2f%% values are in the range %0.2f and %0.2f' % (
                narrative_obj.get('freq'), start_bin.get(BinnerConstants.BIN_START_VALUE_FIELD),
                end_bin.get(BinnerConstants.BIN_END_VALUE_FIELD))
            text_narratives.append(narrative_str)

        return text_narratives
