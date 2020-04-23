# -*- coding: utf-8 -*-
"""This module contains result object for Anova test"""

from bi.common.decorators import accepts
from bi.common.results.descr import DimensionDescriptiveStats
from bi.common.results.descr import MeasureDescriptiveStats
from bi.common.results.descr import TimeDimensionDescriptiveStats


class ColumnValueGroup(object):
    """Encapsulates unique combination of values for one or more dimension columns"""

    @accepts(object, dict)
    def __init__(self, columns_names_values_dict):
        self.column_names = sorted(columns_names_values_dict.keys())
        self.column_values = [columns_names_values_dict.get(k) for k in self.column_names]

    def get_column_names(self):
        return self.column_names

    def has_column(self, column_name):
        return column_name in self.column_names

    def get_column_values(self):
        return self.column_values

    def get_column_value(self, column_name):
        column_index = 0
        for col_name in self.get_column_names():
            if col_name == column_name:
                return self.get_column_values()[column_index]
            else:
                column_index += 1

        return None

    def __eq__(self, other):
        if len(self.get_column_names()) != len(other.get_column_names()):
            return False

        def column_values_match(column_name):
            """
            Checks if column_name exists in both objects and their values match
            :param column_name:
            :return:
            """
            if not other.has_column(column_name):
                return False

            if not self.get_column_value(column_name) != other.get_column_value(column_name):
                return False

            return True

        return all(column_values_match(column_name)
                   for column_name in self.get_column_names())

    def __ne__(self, other):
        if len(self.get_column_names()) != len(other.get_column_names()):
            return True

        def column_missing_or_values_differ(column_name):
            """
            Checks if column_name is missing from one object.
            If column_name exists in both objects, checks if their values differ.
            :param column_name:
            :return: boolean
            """
            if not other.has_column(column_name):
                return True

            if self.get_column_value(column_name) == other.get_column_value(column_name):
                return True

            return False

        return any(column_missing_or_values_differ(column_name)
                   for column_name in self.get_column_names())


class AnovaColumnValueGroupStats:
    """Descriptive stats of a measure column for a particular ColumnValueGroup in an Anova test"""

    @accepts(object, ColumnValueGroup,
             (MeasureDescriptiveStats, DimensionDescriptiveStats, TimeDimensionDescriptiveStats))
    def __init__(self, column_value_group, descr_stats):
        self._column_value_group = column_value_group
        self.column_names = column_value_group.get_column_names()
        self.column_values = column_value_group.get_column_values()
        self.descr_stats = descr_stats

    def get_column_names(self):
        return self.column_names

    def get_column_values(self):
        return self.column_values

    def get_column_value(self, column_name):
        return self._column_value_group.get_column_value(column_name)

    def get_descr_stats(self):
        return self.descr_stats


class AnovaResult:
    """Encapsulates results of an Anova test"""

    def __init__(self):
        self.groups = []
        self.df1 = 0
        self.df2 = 0
        self.ssb = 0.0  # sum of squares between
        self.mssb = 0.0  # mean sum of squares between
        self.sse = 0.0  # sum of squares error
        self.msse = 0.0  # mean sum of squares error
        self.f_value = 0.0
        self.p_value = 0.0
        self.n = 0
        # TODO: calculate proper effect size
        self.effect_size = 0


    @accepts(object, AnovaColumnValueGroupStats)
    def add_group_stats(self, anova_column_value_group_stats):
        if anova_column_value_group_stats not in self.groups:
            self.groups.append(anova_column_value_group_stats)
            self.n += anova_column_value_group_stats.get_descr_stats().get_num_values()

    @accepts(object, df1=(int, long, float), df2=(int, long, float), sum_of_squares_between=(int, long, float),
             mean_sum_of_squares_between=(int, long, float), sum_of_squares_error=(int, long, float),
             mean_sum_of_squares_error=(int, long, float), f_value=(int, long, float), p_value=(int, float),
             total_number_of_records=(int, long))
    def set_params(self, df1, df2, sum_of_squares_between=0.0, mean_sum_of_squares_between=0.0,
                   sum_of_squares_error=0.0, mean_sum_of_squares_error=0.0, f_value=0.0, p_value=0.0,
                   total_number_of_records=140):
        self.df1 = df1
        self.df2 = df2
        self.ssb = sum_of_squares_between
        self.mssb = mean_sum_of_squares_between
        self.sse = sum_of_squares_error
        self.msse = mean_sum_of_squares_error
        self.f_value = f_value
        self.p_value = p_value
        self.n = total_number_of_records

        if(self.p_value <= 0.05):
            self.effect_size = sum_of_squares_between/sum_of_squares_error


    @accepts(object, float)
    def is_statistically_significant(self, alpha):
        return self.p_value < alpha

    def get_df1(self):
        return self.df1

    def get_df2(self):
        return self.df2

    def get_sum_of_squares_between(self):
        return self.ssb

    def get_mean_sum_of_squares_between(self):
        return self.mssb

    def get_sum_of_squares_error(self):
        return self.sse

    def get_mean_sum_of_squares_error(self):
        return self.msse

    def get_f_value(self):
        return self.f_value

    def get_p_value(self):
        return self.p_value

    def get_total_number_of_records(self):
        return self.n

    def get_number_of_groups(self):
        return len(self.groups)

    def get_effect_size(self):
        return self.effect_size

    @accepts(object, bool)
    def get_anova_column_value_groups_by_mean(self, descending_order=True):
        return sorted(self.groups,
                      key=lambda
                          anova_column_value_group_stats: anova_column_value_group_stats.get_descr_stats().get_mean(),
                      reverse=descending_order)

    @accepts(object, bool)
    def get_anova_column_value_groups_by_total(self, descending_order=True):
        return sorted(self.groups,
                      key=lambda
                          anova_column_value_group_stats: anova_column_value_group_stats.get_descr_stats().get_total(),
                      reverse=descending_order)


class DFAnovaResult:
    """
    Result object for all Anova tests in a dataframe
    """

    def __init__(self):
        self.measures = []
        self.results = {}

    @accepts(object, (str, basestring), (str, basestring), AnovaResult)
    def add_anova_result(self, measure_column, dimension_column, anova_result):
        if measure_column not in self.measures:
            self.measures.append(measure_column)
        if not self.results.has_key(measure_column):
            self.results[measure_column] = {}
        self.results.get(measure_column)[dimension_column] = anova_result

    def get_measure_columns(self):
        return self.measures

    def get_dimensions_analyzed(self, measure_column):
        if not self.results.has_key(measure_column):
            return []
        return self.results.get(measure_column).keys()

    def get_anova_result(self, measure_column, dimension_column):
        if not self.results.has_key(measure_column) or not self.results.get(measure_column).has_key(dimension_column):
            return None
        return self.results.get(measure_column).get(dimension_column)
