# -*- coding: utf-8 -*-
"""This module contains result object for descriptive stats"""

from bi.common.decorators import accepts
from bi.common.results.histogram import Histogram
from bi.common import utils



class FivePointSummary:
    """Five Point summary stats for a measure column"""

    LEFT_HINGE = 'left_hinge'
    RIGHT_HINGE = 'right_hinge'
    Q1 = 'q1'
    Q2 = 'q2'
    Q3 = 'q3'
    Q4 = 'q4'
    MEDIAN = 'median'
    LEFT_OUTLIERS = 'left'
    RIGHT_OUTLIERS = 'right'

    @accepts(object, left_hinge_value=(int, long, float), q1_value=(int, long, float),
             median=(int, long, float), q3_value=(int, long, float), right_hinge_value=(int, long, float),
             num_left_outliers=(int, long, float), num_right_outliers=(int, long, float),
             q1_freq=(int, long, float), q2_freq=(int, long, float),
             q3_freq=(int, long, float), q4_freq=(int, long, float))
    def __init__(self, left_hinge_value=0.0, q1_value=0.0, median=0.0, q3_value=0.0, right_hinge_value=0.0,
                 num_left_outliers=0, num_right_outliers=0,
                 q1_freq=0, q2_freq=0, q3_freq=0, q4_freq=0):
        self.splits = {
            FivePointSummary.LEFT_HINGE: utils.round_sig(left_hinge_value,3),
            FivePointSummary.Q1: utils.round_sig(q1_value,3),
            FivePointSummary.Q2: utils.round_sig(median,3),
            FivePointSummary.MEDIAN: utils.round_sig(median,3),
            FivePointSummary.Q3: utils.round_sig(q3_value,3),
            FivePointSummary.RIGHT_HINGE: utils.round_sig(right_hinge_value,3)
        }
        self.outliers = {
            FivePointSummary.LEFT_OUTLIERS: num_left_outliers,
            FivePointSummary.RIGHT_OUTLIERS: num_right_outliers
        }
        self.freq = {
            FivePointSummary.Q1: q1_freq,
            FivePointSummary.Q2: q2_freq,
            FivePointSummary.Q3: q3_freq,
            FivePointSummary.Q4: q4_freq
        }

    def set_sums(self,quartile_sums):
        self.sums = quartile_sums

    def set_means(self, quartile_means):
        self.means = quartile_means

    def get_means(self):
        return self.means

    def get_sums(self):
        return self.sums

    def get_frequencies(self):
        return self.freq

    def get_num_outliers(self):
        return self.outliers.get(FivePointSummary.LEFT_OUTLIERS) + self.outliers.get(FivePointSummary.RIGHT_OUTLIERS)

    def get_left_outliers(self):
        return self.outliers.get(FivePointSummary.LEFT_OUTLIERS)

    def get_right_outliers(self):
        return self.outliers.get(FivePointSummary.RIGHT_OUTLIERS)

    def get_q1_split(self):
        return self.splits.get(FivePointSummary.Q1)

    def get_q2_split(self):
        return self.splits.get(FivePointSummary.Q2)

    def get_q3_split(self):
        return self.splits.get(FivePointSummary.Q3)

class MeasureDescriptiveStats:
    """Descriptive stats for a measure column"""

    @accepts(object)
    def __init__(self):
        self.n = 0
        self.min = 0.0
        self.max = 0.0
        self.total = 0.0
        self.mean = 0.0
        self.var = 0.0
        self.std_dev = 0.0
        self.skew = 0.0
        self.kurtosis = 0.0
        self.five_point_summary = None
        self.histogram = None
        # TODO: remove raw_data object post demo
        #self.raw_data = None

    @accepts(object, num_values=(int, long), min_value=(int, long, float), max_value=(int, long, float),
             total=(int, long, float), mean=(int, long, float), variance=(int, long, float),
             std_dev=(int, long, float), skew=(int, long, float), kurtosis=(int, long, float))
    def set_summary_stats(self, num_values=0, min_value=0.0, max_value=0.0, total=0.0,
                          mean=0.0, variance=0.0, std_dev=0.0, skew=0.0,
                          kurtosis=0.0):
        self.n = num_values
        self.min = utils.round_sig(min_value,3)
        self.max = utils.round_sig(max_value,3)
        self.total = utils.round_sig(total,3)
        self.mean =utils.round_sig(mean,3)
        self.var = utils.round_sig(variance,3)
        self.std_dev = utils.round_sig(std_dev,3)
        self.skew = utils.round_sig(skew,3)
        self.kurtosis = utils.round_sig(kurtosis,3)

    @accepts(object, FivePointSummary)
    def set_five_point_summary_stats(self, five_point_summary):
        self.five_point_summary = five_point_summary

    @accepts(object, Histogram)
    def set_histogram(self, histogram):
        self.histogram = histogram

    def get_histogram(self):
        return self.histogram.get_bins()

    def get_five_point_summary_stats(self):
        return self.five_point_summary

    #@accepts(object, (list, tuple))
    #def set_raw_data(self, data):
    #    self.raw_data = data

    def get_num_values(self):
        return self.n

    def get_min(self):
        return self.min

    def get_max(self):
        return self.max

    def get_total(self):
        return self.total

    def get_mean(self):
        return self.mean

    def get_variance(self):
        return self.var

    def get_std_dev(self):
        return self.std_dev

    def get_skew(self):
        return self.skew

    def get_kurtosis(self):
        return self.kurtosis

    def get_n(self):
        return self.n

class DimensionDescriptiveStats:
    """Descriptive stats for a dimension column"""

    @accepts(object, num_null_values=(int, long), num_non_null_values=(int, long), cardinality=(int, long))
    def __init__(self, num_null_values=0, num_non_null_values=0, cardinality=1):
        self.n = num_non_null_values + num_null_values
        self.num_null_values = num_null_values
        self.num_non_null_values = num_non_null_values
        self.cardinality = cardinality
        self.freq = {}  # level-value -> freq

    @accepts(object, dict)
    def set_value_frequencies(self, value_freq_dict):
        self.freq.update(value_freq_dict)

    def get_n(self):
        return self.n

    def get_num_null_values(self):
        return self.num_null_values

    def get_num_non_null_values(self):
        return self.num_non_null_values

    def get_cardinality(self):
        return self.cardinality

    def get_value_frequencies(self):
        return self.freq


class TimeDimensionDescriptiveStats:
    """Descriptive stats for a time dimension column"""

    @accepts(object, basestring, basestring)
    def __init__(self, column_name, column_type):
        self._column_name = column_name
        self._column_type = column_type


class DataFrameDescriptiveStats:
    """Descriptive stats for all column in a dataframe"""

    @accepts(object, num_columns=(int, long), num_rows=(int, long))
    def __init__(self, num_columns=0, num_rows=0):
        self.num_columns = num_columns
        self.num_rows = num_rows
        self.measures = {}
        self.dimensions = {}
        self.time_dimensions = {}

    @accepts(object, basestring, MeasureDescriptiveStats)
    def add_measure_stats(self, measure_column_name, measure_column_descr_stats):
        self.measures[measure_column_name] = measure_column_descr_stats

    def get_measure_columns(self):
        return self.measures.keys()

    def get_measure_column_stats(self, column_name):
        return self.measures.get(column_name)

    @accepts(object, basestring, DimensionDescriptiveStats)
    def add_dimension_stats(self, dimension_column_name, dimension_column_descr_stats):
        self.dimensions[dimension_column_name] = dimension_column_descr_stats

    @accepts(object, basestring, TimeDimensionDescriptiveStats)
    def add_time_dimension_stats(self, time_dimension_column_name, time_dimension_column_descr_stats):
        self.time_dimensions[time_dimension_column_name] = time_dimension_column_descr_stats

    def get_num_columns(self):
        return self.num_columns
