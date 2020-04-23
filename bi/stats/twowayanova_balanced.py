import pandas as pd
from pyspark.sql import DataFrame
from pyspark.sql.functions import mean, sum, col, count

from bi.common import DataFrameHelper
from bi.common.decorators import accepts
from bi.common.results import DFTwoWayAnovaResult
from bi.common.results import MeasureAnovaResult

#from bi.stats.descr import DescriptiveStats

"""
Two way ANOVA test
"""


class TwoWayAnova:
    """
        var1 = n*mean2
        var2 = sum(x2)
        var5 = n*mean2 for each group(a,b)
        var3 = n*mean2 for each group a

    """

    @accepts(object, DataFrame)
    def __init__(self, data_frame,df_helper):
        self._data_frame = data_frame
        self._dataframe_helper = df_helper
        self._measure_columns = self._dataframe_helper.get_numeric_columns()
        self._dimension_columns = self._dataframe_helper.get_string_columns()
        self._df = self._dataframe_helper.get_num_rows()
        self._mean = {}

    @accepts(object, measure_columns=(list, tuple), dimension_columns=(list, tuple), max_num_levels=int)
    def test_all(self, measure_columns=None, dimension_columns=None, max_num_levels=40):
        measures = measure_columns
        if measure_columns is None:
            measures = self._measure_columns
        dimensions = dimension_columns
        if dimension_columns is None:
            dimensions = self._dimension_columns
        max_num_levels = min(max_num_levels, round(self._dataframe_helper.get_num_rows()**0.35))
        DF_Anova_Result = DFTwoWayAnovaResult()
        dimensions_to_test = [dim for dim in dimensions if self._dataframe_helper.get_num_unique_values(dim) <= max_num_levels]

        for m in measures:
            #var = self._data_frame.select(col(m).alias('x'),(col(m)**2).alias('x2')).agg({'x':'count','x':'mean','x2':'sum'}).collect()
            var = self._data_frame.select(col(m).alias('x'),(col(m)**2).alias('x2')).agg(*[count(col('x')),mean(col('x')),sum(col('x2'))]).collect()
            self._anova_result = MeasureAnovaResult(var[0])
            self.test_against(m, dimensions_to_test)
            DF_Anova_Result.add_measure_result(m,self._anova_result)
        return DF_Anova_Result

    def test_anova(self,measure,dimension):
        var = self._data_frame.groupby(dimension).agg(*[count(col(measure)),mean(col(measure))]).collect()
        var = pd.DataFrame(var,columns=['levels', 'counts', 'means'])
        var['total'] = var.means*var.counts
        var['var3'] = var.counts*var.means*var.means
        self._anova_result.set_OneWayAnovaResult(dimension,var)

    def test_against(self,measure, dimensions):
        for dimension in dimensions:
            self.test_anova(measure,dimension)
        for i in range(0,len(dimensions)-1):
            for j in range(i+1,len(dimensions)):
                self.test_anova_interaction(measure,dimensions[i],dimensions[j])

    def test_anova_interaction(self,measure,dimension1,dimension2):
        var = self._data_frame.groupby(dimension1,dimension2).agg(*[count(col(measure)),mean(col(measure))]).collect()
        var = pd.DataFrame(var,columns=['level1','level2', 'counts', 'means'])
        var['total'] = var.means*var.counts
        var['var5'] = var.counts*var.means*var.means
        self._anova_result.set_TwoWayAnovaResult(dimension1,dimension2,var)
