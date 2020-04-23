import math

from pyspark.sql import functions as FN

from bi.common import BIException
from bi.common.decorators import accepts
from bi.common.results import AnovaColumnValueGroupStats
from bi.common.results import AnovaResult
from bi.common.results import ColumnValueGroup
from bi.common.results import DFAnovaResult

#from bi.stats.descr import DescriptiveStats

"""
One way ANOVA test
"""


class OneWayAnova:
    GRAND_MEAN_COLUMN_NAME = '__grand_mean'
    MEAN_COLUMN_NAME = '__mean'
    COUNT_COLUMN_NAME = '__count'
    SUM_OF_SQUARES = '__sum_of_squares'

    def __init__(self, data_frame, df_helper, df_context):
        self._data_frame = data_frame
        self._dataframe_helper = df_helper
        self._dataframe_context = df_context
        self._num_levels = 200

    @accepts(object, measure_columns=(list, tuple), dimension_columns=(list, tuple), max_num_levels=int)
    def test_all(self, measure_columns=None, dimension_columns=None, max_num_levels=200):
        measures = measure_columns
        if measure_columns is None:
            measures = self._dataframe_helper.get_numeric_columns()
        dimensions = dimension_columns
        if dimension_columns is None:
            dimensions = self._dataframe_helper.get_string_columns()
            date_columns = self._dataframe_context.get_date_columns()
            if date_columns != None:
                dimensions = list(set(dimensions)-set(date_columns))

        df_anova_result = DFAnovaResult()
        for m in measures:
            for d in dimensions:
                anova_result = self.test(m, d, max_num_levels=max_num_levels)
                if anova_result!=None:
                    df_anova_result.add_anova_result(m, d, anova_result)
        return df_anova_result

    @accepts(object, basestring, basestring, max_num_levels=int)
    def test(self, measure_column_name, dimension_column_name, max_num_levels=200):
        if not measure_column_name in self._dataframe_helper.get_numeric_columns():
            raise BIException.non_numeric_column(measure_column_name)
        if not dimension_column_name in self._dataframe_helper.get_string_columns():
            raise BIException.non_string_column(dimension_column_name)
        num_levels = self._data_frame.na.drop(subset=dimension_column_name).select(dimension_column_name).distinct().count()
        num_rows = self._data_frame.count()
        if num_levels > max_num_levels:
            print 'Dimension column(%s) has more than %d levels' % (dimension_column_name, max_num_levels)
            return None
        grand_mean_expr = (FN.mean(measure_column_name).alias(OneWayAnova.GRAND_MEAN_COLUMN_NAME),)
        grand_mean = self._data_frame.select(*grand_mean_expr).collect()[0][OneWayAnova.GRAND_MEAN_COLUMN_NAME]
        agg_expr = (FN.count(measure_column_name).alias(OneWayAnova.COUNT_COLUMN_NAME),
                    FN.mean(measure_column_name).alias(OneWayAnova.MEAN_COLUMN_NAME))

        groups_data = {}
        aggregated_data = self._data_frame.na.drop(subset=dimension_column_name).groupBy(dimension_column_name).agg(*agg_expr).collect()
        for row in aggregated_data:
            row_data = row.asDict()
            groups_data[row_data.get(dimension_column_name)] = row_data
        dimension_column = FN.col(dimension_column_name)
        measure_column = FN.col(measure_column_name)
        anova_result = AnovaResult()
        sum_of_squares_error = 0
        for group_name in groups_data.keys():
            group_mean = groups_data.get(group_name).get(OneWayAnova.MEAN_COLUMN_NAME)
            group_sum_of_squares = self._data_frame.filter(dimension_column == group_name) \
                .select(((measure_column - group_mean) * (measure_column - group_mean))) \
                .agg({'*': 'sum'}).collect()[0][0]
            sum_of_squares_error += group_sum_of_squares
            num_values_in_group = groups_data.get(group_name).get(OneWayAnova.COUNT_COLUMN_NAME)
            column_value_group = ColumnValueGroup({dimension_column_name: group_name})
            descr_stats = DescriptiveStats(
                self._data_frame.filter(dimension_column == group_name).select(measure_column), self._dataframe_helper, self._dataframe_context)
            try:
                group_descr_stats = descr_stats.stats_for_measure_column(measure_column_name)
            except Exception, e:
                print e
                group_descr_stats = {}
            anova_column_value_group_stats = AnovaColumnValueGroupStats(column_value_group, group_descr_stats)
            anova_result.add_group_stats(anova_column_value_group_stats)

        sum_of_squares_between = sum(
            [data[OneWayAnova.COUNT_COLUMN_NAME] * math.pow(grand_mean - data[OneWayAnova.MEAN_COLUMN_NAME], 2)
             for data in groups_data.values()])
        mean_sum_of_squares_between = float(sum_of_squares_between) / (num_levels - 1)

        mean_sum_of_squares_error = float(sum_of_squares_error) / (num_rows - num_levels)
        f_value = mean_sum_of_squares_between / mean_sum_of_squares_error
        p_value = Stats.f_distribution_critical_value(f_value, num_levels - 1, num_rows - num_levels)
        anova_result.set_params(df1=num_levels - 1,
                                df2=(num_rows - num_levels),
                                sum_of_squares_between=sum_of_squares_between,
                                mean_sum_of_squares_between=mean_sum_of_squares_between,
                                sum_of_squares_error=sum_of_squares_error,
                                mean_sum_of_squares_error=mean_sum_of_squares_error,
                                f_value=f_value,
                                p_value=p_value,
                                total_number_of_records=num_rows)

        return anova_result
