
import math

from bi.common import ALPHA_LEVELS
from bi.common.decorators import accepts
from bi.common.exception import BIException
from bi.common.results import ColumnCorrelations
from bi.common.results import CorrelationStats
from bi.common.results import Correlations as AllCorrelations
from bi.stats.util import Stats

"""
Utility class for finding correlation among numerical columns in a data frame
"""

class Correlation:
    def __init__(self, data_frame, df_helper, df_context):
        self._data_frame = data_frame
        self._dataframe_helper = df_helper
        self._dataframe_context = df_context


    def all_correlations(self):
        """
        Finds correlation among all pairs of numeric column in this data frame
        :return: list of CorrelationResult objects
        """
        all_pairs_corr = AllCorrelations()
        for column in self._numeric_columns:
            all_pairs_corr.add_correlation(self.correlations_for_one_column(column))
        return all_pairs_corr

    def correlations_for_one_column(self, column):
        """Finds correlations for a column(measure) with all other measure columns
        """
        column_correlations = ColumnCorrelations(column)
        for other_column in self._dataframe_helper.get_numeric_columns():
            if column == other_column:
                ### std_error is 0 for correlation among same columns,
                ### as a result t_value calculation fails. So,
                ### avoiding calculating corr between same columns
                continue
            corr = self.correlation(column, other_column)
            column_correlations.add_correlation(other_column, corr)
        return column_correlations

    @accepts(object, (basestring, str), (basestring, str))
    def correlation(self, column_one, column_two):
        """
        Find correlation between two numeric columns
        :param column_one:
        :param column_two:
        :return:
        """
        if column_one not in self._dataframe_helper.get_numeric_columns():
            raise BIException.non_numeric_column(column_one)

        if column_two not in self._dataframe_helper.get_numeric_columns():
            raise BIException.non_numeric_column(column_two)

        return self._corr(column_one, column_two)

    @accepts(object, (str, basestring), (str, basestring))
    def _corr(self, column_one, column_two):
        """
        Finds correlation between two columns, also calculates
            a) statistical significance info
            b) effect size info - coefficient of determination, and
            c) confidence intervals.

        :param column_one:
        :param column_two:
        :return:
        """
        corr = self._data_frame.corr(column_one, column_two)
        num_of_samples = self._data_frame.select(column_one).count()
        df = num_of_samples - 2
        std_error = math.sqrt((1 - math.pow(corr, 2)) / df)
        t_value = corr / std_error
        p_value = Stats.t_distribution_critical_value(t_value, df=df)
        coeff_determination = math.pow(corr, 2)

        corr_stats = CorrelationStats(correlation=corr, std_error=std_error, t_value=t_value, p_value=p_value,
                                      degrees_of_freedom=df, coeff_determination=coeff_determination)
        for alpha in ALPHA_LEVELS:
            (lower_bound, upper_bound) = self._confidence_interval(corr, num_of_samples, alpha)
            corr_stats.set_confidence_interval(alpha, lower_bound, upper_bound)

        return corr_stats

    def _confidence_interval(self, correlation, num_samples, alpha):
        """
        Finds confidence interval for correlation at given alpha level

        Ref: http://www2.sas.com/proceedings/sugi31/170-31.pdf

        :param correlation:
        :param num_samples:
        :param alpha:
        :return: tuple (lower_bound, upper_bound)
        """
        normalized_correlation = 0.5 * math.log(float(1 + correlation) / (1 - correlation))
        std_dev = math.sqrt(1.0 / (num_samples - 3))
        normalized_lowerbound = normalized_correlation - Stats.normal_distribution_percentile_point_function(
            alpha) * std_dev
        normalized_upperbound = normalized_correlation + Stats.normal_distribution_percentile_point_function(
            alpha) * std_dev
        return (math.tanh(normalized_lowerbound), math.tanh(normalized_upperbound))
