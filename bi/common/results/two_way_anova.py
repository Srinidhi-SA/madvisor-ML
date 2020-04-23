from datetime import datetime

import pandas as pd
from scipy import stats

from bi.common.decorators import accepts


class DFTwoWayAnovaResult:
    def __init__(self):
        self.result = {}
    def get_anova_result(self,measure,dimension):
        return self.result[measure].get_anova_result(dimension)
    def add_measure_result(self,measure,Measure_Anova_Result):
        self.result[measure] = Measure_Anova_Result
    def add_trend_result(self, measure, trend_result):
        self.result[measure].set_TrendResult(trend_result)
    def get_measure_result(self, measure):
        return self.result[measure]
    def get_measure_columns(self):
        return self.result.keys()
    def get_dimensions_analyzed(self,measure):
        return self.result[measure].get_dimensions_analyzed()
    def get_significant_dimensions(self,measure):
        return self.result[measure].get_OneWayAnovaSignificantDimensions()

class TrendData:
    def __init__(self,grouped_data=None,level_pivot=None,startDate=None,endDate=None,duration=None,durationString=None,dataLevel=None):
        self.grouped_data = grouped_data
        self.level_pivot = level_pivot
        self.endDate = endDate
        self.startDate = startDate
        self.duration = duration
        self.durationString = durationString
        self.dataLevel = dataLevel

    @accepts(object,grouped_data=pd.DataFrame,level_pivot=pd.DataFrame,endDate=datetime,startDate=datetime,
            duration=(int,float),durationString=basestring,dataLevel=basestring)
    def set_params(self,grouped_data,level_pivot,endDate,startDate,duration,durationString,dataLevel):
        self.grouped_data = grouped_data
        self.level_pivot = level_pivot
        self.endDate = endDate
        self.startDate = startDate
        self.duration = duration
        self.durationString = durationString
        self.dataLevel = dataLevel

    @accepts(object,data=pd.DataFrame)
    def set_grouped_data(self,data):
        self.grouped_data = data
    def get_grouped_data(self):
        return self.grouped_data.copy()
    @accepts(object,data=pd.DataFrame)
    def set_level_pivot(self,data):
        self.level_pivot = data
    def get_level_pivot(self):
        return self.level_pivot.copy()
    def get_end_date(self):
        return self.endDate
    def get_start_date(self):
        return self.startDate
    def get_data_level(self):
        return self.dataLevel
    def get_duration(self):
        return self.duration
    def get_duration_string(self):
        return self.durationString

class OneWayAnovaResult:
    """
    Encapsulates results of an Anova test
    """
    def __init__(self):
        self.df_within = 0
        self.df_between = 0
        self.ss_between = 0.0
        self.ss_within = 0.0
        self.mss_between = 0.0
        self.mss_within = 0.0
        self.f_value = 0.0
        self.p_value = 0.0
        self.eta_squared = 0.0
        self.f_critical = 0.0
        self.n_total = 0
        self.n_groups = 0
        self.levelDf = None


    @accepts(object, df_within=(int, long, float), df_between=(int, long, float),
             sum_of_squares_between=(int, long, float),sum_of_squares_within=(int, long, float),
             mean_sum_of_squares_between=(int, long, float),mean_sum_of_squares_within=(int, long, float),
             f_value=(int, long, float), p_value=(int, float),eta_squared=(int, long, float),
             f_critical=(int, long, float),total_number_of_records=(int, long),n_groups=(int, long),levelDf=pd.DataFrame)
    def set_params(self, df_within, df_between, sum_of_squares_between=0.0, sum_of_squares_within=0.0,
                   mean_sum_of_squares_between=0.0, mean_sum_of_squares_within=0.0, f_value=0.0, p_value=0.0,
                   eta_squared=0.0,f_critical=0.0,total_number_of_records=0,n_groups=0,levelDf=None):
        self.df_within = df_within
        self.df_between = df_between
        self.ss_between = sum_of_squares_between
        self.ss_within = sum_of_squares_within
        self.mss_between = mean_sum_of_squares_between
        self.mss_within = mean_sum_of_squares_within
        self.f_value = f_value
        self.p_value = p_value
        self.eta_squared = eta_squared
        self.f_critical = f_critical
        self.n_total = total_number_of_records
        self.n_groups = n_groups
        self.levelDf = levelDf

    @accepts(object, float)
    def is_statistically_significant(self, alpha):
        return self.p_value < alpha

    def get_df_within(self):
        return self.df_within

    def get_df_between(self):
        return self.df_between

    def get_sum_of_squares_between(self):
        return self.ss_between

    def get_sum_of_squares_within(self):
        return self.ss_within

    def get_mean_sum_of_squares_between(self):
        return self.mss_between

    def get_mean_sum_of_squares_within(self):
        return self.mss_within

    def get_f_value(self):
        return self.f_value

    def get_p_value(self):
        return self.p_value

    def get_total_number_of_records(self):
        return self.n_total

    def get_number_of_groups(self):
        return self.n_groups

    def get_effect_size(self):
        return self.eta_squared

    def get_level_dataframe(self):
        return self.levelDf



class TopLevelDfAnovaStats:
    def __init__(self):
        self.top_level_stat = None
        self.top_level_anova = {}
        self.contributions = {}
        self.trendData = None


    @accepts(object,data=pd.DataFrame)
    def set_top_level_stat(self,data):
        self.top_level_stat = data

    def get_top_level_stat(self):
        return self.top_level_stat

    def get_top_level_name(self):
        print self.top_level_stat
        return self.top_level_stat["levels"]

    @accepts(object,dimension=str,anovaResult=OneWayAnovaResult)
    def set_top_level_anova(self,dimension,anovaResult):
        self.top_level_anova.update({dimension:anovaResult})

    @accepts(object,dimension=str,contributionDict=dict)
    def set_dimension_contributions(self,dimension,contributionDict):
        print "contributionDict",contributionDict
        print "#$"*23
        self.contributions[dimension] = contributionDict

    def get_top_significant_dimensions(self,n=5):
        output = []
        for dim,anovaResult in self.top_level_anova.items():
            print "getting top n"
            print dim,anovaResult.get_p_value(),type(anovaResult.get_p_value())
            if anovaResult.get_p_value() < 0.05:
                output.append((dim,anovaResult,anovaResult.get_effect_size()))
        sortedOutput = sorted(output,key=lambda x:x[2],reverse=True)
        return sortedOutput[:n]

    @accepts(object,data=TrendData)
    def set_trend_data(self,data):
        self.trendData = data

    def get_trend_data(self):
        return self.trendData

class MeasureAnovaResult:
    def __init__(self, measureColMean=None,measureColCount=None, measureColSst=None):
        self.global_mean = measureColMean
        self.df = measureColCount - 1
        self.sst = measureColSst
        self.oneWayAnovaResultDict = {}
        self.topLevelDfAnovaResult = {}
        self.trendData = None
        #self.TwoWayAnovaResult = {}

    def get_one_way_anova_result(self,dimension):
        return self.oneWayAnovaResultDict[dimension]

    def get_dimensions_analyzed(self):
        return self.oneWayAnovaResultDict.keys()

    @accepts(object, dimension=(str), oneWayAnovaResult=OneWayAnovaResult)
    def set_oneWayAnovaResultDict(self, dimension,oneWayAnovaResult):
        self.oneWayAnovaResultDict.update({dimension:oneWayAnovaResult})

    @accepts(object, dimension=(str),topLevelAnovaResult=TopLevelDfAnovaStats)
    def set_topLevelDfAnovaResult(self,dimension,topLevelAnovaResult):
        self.topLevelDfAnovaResult[dimension]=topLevelAnovaResult

    def get_topLevelDfAnovaResult(self,dimension):
        return self.topLevelDfAnovaResult[dimension]

    def get_OneWayAnovaEffectSize(self, dimension):
        return self.oneWayAnovaResultDict[dimension].get_effect_size()


    def get_OneWayAnovaSignificantDimensions(self):
        significant_dimensions = {}
        insignificant_dimensions = []
        for dimension in self.oneWayAnovaResultDict:
            p_value = self.oneWayAnovaResultDict[dimension].get_p_value()
            effect_size = self.oneWayAnovaResultDict[dimension].get_effect_size()
            if p_value<=0.05:
                significant_dimensions[dimension] = effect_size
            else:
                insignificant_dimensions.append(dimension)
        return significant_dimensions,insignificant_dimensions

    @accepts(object,data=TrendData)
    def set_trend_data(self, data):
        self.trendData = data

    def get_trend_data(self):
        return self.trendData

    def set_TwoWayAnovaResult(self, dimension1,dimension2, var, sse):
        if not self.TwoWayAnovaResult.has_key(dimension1):
            self.TwoWayAnovaResult[dimension1]={}
        self.TwoWayAnovaResult[dimension1][dimension2] = TwoWayAnovaResult(var, self.global_mean, sse, self.sst)
        self.TwoWayAnovaResult[dimension1][dimension2].set_results(self.OneWayAnovaResult[dimension1], self.OneWayAnovaResult[dimension2])

    def get_TwoWayAnovaResult(self, dimension1,dimension2):
        if self.TwoWayAnovaResult.has_key(dimension1):
            if self.TwoWayAnovaResult[dimension1].has_key(dimension2):
                return self.TwoWayAnovaResult[dimension1][dimension2]
        if self.TwoWayAnovaResult.has_key(dimension2):
            if self.TwoWayAnovaResult[dimension2].has_key(dimension1):
                return self.TwoWayAnovaResult[dimension2][dimension1]



class TwoWayAnovaResult:
    def __init__(self, var, global_mean, sse, sst):
        self._global_mean = global_mean
        self.set_dim_table(var)
        self.set_ss_interaction(var)
        self.ss_error = float(sse)
        self.ss_total = float(sst)

    def set_ss_interaction(self,var):
        var['dev'] = var.counts * (var.means - self._global_mean)**2
        self.ss_interaction = float(var.dev.sum())

    def set_dim_table(self, var):
        self._dim_table = {}
        self._dim_table['level1']=var.level1.tolist()
        self._dim_table['level2']=var.level2.tolist()
        self._dim_table['counts']=var.counts.tolist()
        self._dim_table['means']=var.means.tolist()
        self._dim_table['total']=var.total.tolist()

    def set_results(self, anova_row, anova_column):
        self.ss_row = anova_row.get_ss_between()
        self.df_row = anova_row.get_df_between()
        self.ms_row = self.ss_row/self.df_row

        #self.ss_total = anova_row.get_ss_total()
        self.df_total = anova_row.get_df_total()
        self.ms_total = self.ss_total/self.df_total

        self.ss_column = anova_column.get_ss_between()
        self.df_column = anova_column.get_df_between()
        self.ms_column = self.ss_column/self.df_column

        #self.ss_interaction = self._n_mean2 - self.ss_row - self.ss_column - var1
        self.df_interaction = self.df_row * self.df_column
        self.ms_interaction = self.ss_interaction/self.df_interaction

        #self.ss_error = var2 - self._n_mean2
        self.df_error = self.df_total - (self.df_row+1)*(self.df_column+1) + 1
        self.ms_error = self.ss_error/self.df_error

        self.f_row = self.ms_row/self.ms_error
        self.f_column = self.ms_column/self.ms_error
        self.f_interaction = self.ms_interaction/self.ms_error

        '''
        self.p_row = Stats.f_distribution_critical_value(self.f_row, self.df_row, self.df_error)
        self.p_column = Stats.f_distribution_critical_value(self.f_column, self.df_column, self.df_error)
        self.p_interaction = Stats.f_distribution_critical_value(self.f_interaction, self.df_interaction, self.df_error)
        '''
        #'''
        self.p_row = 1 - stats.f.cdf(self.f_row, self.df_row,self.df_error)
        self.p_column = 1 - stats.f.cdf(self.f_column, self.df_column,self.df_error)
        self.p_interaction = 1 - stats.f.cdf(self.f_interaction, self.df_interaction,self.df_error)
        #'''
        self.effect_size_interaction = self.ss_interaction/self.ss_total
        self.effect_size_row = self.ss_row/self.ss_total
        self.effect_size_column = self.ss_column/self.ss_total

class TopDimensionStats:
    def __init__(self,top_dimension, total,df,mean, sst):
        self.top_dimension = top_dimension
        self.sum_measure = total
        self._df_total = df - 1
        self.avg_measure = mean
        self._sst = sst
        self.p_value = {}
        self.effect_size = {}
        self.contributions = {}

    def set_p_value(self,var,sse, dimension):
        df_between = len(var.index)-1
        if df_between == 0:
            self.p_value[dimension] = 1
            self.effect_size[dimension] = 0
            return
        df_total = var.counts.sum() - 1
        var['dev'] = var.counts * (var.means - self.avg_measure)**2
        ss_between = float(var.dev.sum())
        ss_within = sse
        df_within = self._df_total - df_between
        if ss_within > 0:
            self.effect_size[dimension] = ss_between/self._sst
        else:
            self.effect_size[dimension] = 0
        ms_between = ss_between/df_between
        ms_within = ss_within/df_within
        f_stat = ms_between/ms_within
        self.p_value[dimension] = 1 - stats.f.cdf(f_stat, df_between, df_within)
        if self.p_value[dimension]<=0.05:
            self.compute_contributions(dimension,var)

    def get_p_value(self, dimension):
        return self.p_value[dimension]

    def compute_contributions(self, dimension, var):
        var = var.sort_values('total', ascending = False)
        max_diff_index = var.total.diff(1).argmax()
        var = var.ix[:max_diff_index]
        var['percent'] = var['total']/self.sum_measure
        self.contributions[dimension] = dict(zip(var['levels'], var['percent']))

    def get_contributions(self, dimension):
        return self.contributions[dimension]

    def get_top_3_significant_dimensions(self):
        significant_dimensions = [k for k,v in self.p_value.items() if v<=0.05]
        if len(significant_dimensions)<2:
            return significant_dimensions
        else:
            significant_dimensions = sorted(significant_dimensions, key = lambda x: -self.effect_size[x])[:3]
            return significant_dimensions

    def get_significant_dimensions(self):
        significant_dimensions = [k for k,v in self.p_value.items() if v<=0.05]
        if len(significant_dimensions)<2:
            return significant_dimensions
        else:
            significant_dimensions = sorted(significant_dimensions, key = lambda x: -self.effect_size[x])
            return significant_dimensions




class TrendResult:
    def __init__(self, agg_data_frame, date_field, measure):
        self._data_frame = agg_data_frame
        self.subset_df = {}
        self.dimension_results = {}
        self.top_dimensions = {}
        self.date_field = date_field
        self.measure = measure
        self._growth_rate = (self._data_frame['measure'].iloc[-1]*100/self._data_frame['measure'].iloc[0]) - 100

    def get_data_frame(self):
        return self._data_frame

    def get_overall_growth_percent(self):
        return self._growth_rate

    def add_subset_df(self, data_frame, dimension, top_dimension):
        self.subset_df[dimension] = data_frame
        self.top_dimensions[dimension] = top_dimension.levels

    def add_trend_result(self,dimension, agg_data_frame):
        self.dimension_results[dimension] = TrendDimensionResult(agg_data_frame)

    def get_trend_result(self, dimension):
        return self.dimension_results[dimension]

    def get_grouped_data(self, dimension):
        return self.dimension_results[dimension].get_grouped_data()

    def get_subset_data(self,dimension):
        return self.subset_df[dimension]

    def get_top_dimension(self, dimension):
        return self.top_dimensions[dimension]

class TrendDimensionResult:
    def __init__(self, agg_data_frame_dimension):
        self.grouped_data_frame = agg_data_frame_dimension

    def get_grouped_data(self):
        return self.grouped_data_frame
