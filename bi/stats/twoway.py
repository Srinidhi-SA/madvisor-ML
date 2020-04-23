import __builtin__
import time

import pandas as pd
from pyspark.sql.functions import mean, sum, count, col
from scipy.stats import f

from bi.common import utils as CommonUtils
from bi.common.decorators import accepts
from bi.common.results import DFTwoWayAnovaResult, OneWayAnovaResult
from bi.common.results import MeasureAnovaResult, TrendData
from bi.common.results import TopLevelDfAnovaStats
from bi.narratives import utils as NarrativesUtils
from bi.settings import setting as GLOBALSETTINGS

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

    def __init__(self, data_frame, df_helper, df_context, meta_parser,scriptWeight=None, analysisName=None):
        self._data_frame = data_frame
        self._dataframe_helper = df_helper
        self._dataframe_context = df_context
        self._metaParser = meta_parser
        self._measure_columns = self._dataframe_helper.get_numeric_columns()
        self._dimension_columns = self._dataframe_helper.get_string_columns()
        self._timestamp_columns = self._dataframe_helper.get_timestamp_columns()
        if analysisName == None:
            self._analysisName = self._dataframe_context.get_analysis_name()
        else:
            self._analysisName = analysisName
        if scriptWeight == None:
            self._scriptWeightDict = self._dataframe_context.get_measure_analysis_weight()
        else:
            self._scriptWeightDict = scriptWeight


        print "=================dimension columns======================"
        print self._dimension_columns
        print "=================dimension columns======================"

        print "==================measure_columns ========================"
        print self._measure_columns
        print "==================measure_columns ========================"

        self._storyOnScoredData = self._dataframe_context.get_story_on_scored_data()
        self._date_columns = self._dataframe_context.get_date_columns()
        self._uid_col = self._dataframe_context.get_uid_column()
        if self._metaParser.check_column_isin_ignored_suggestion(self._uid_col):
            self._dimension_columns = list(set(self._dimension_columns) - {self._uid_col})
        if len(self._date_columns) >0 :
            self._dimension_columns = list(set(self._dimension_columns)-set(self._date_columns))
        self.top_dimension_result = {}
        # if selected date col empty then on td_node
        self._dataRangeStats = None
        self._dateFormatDetected = False
        self._trend_on_td_column = False
        self._existingDateFormat = None
        self._dateFormatConversionDict = NarrativesUtils.date_formats_mapping_dict()
        self._dateColumnFormatDict =  df_context.get_date_format_dict()
        if self._dataframe_context.get_requested_date_format() != None:
            self._requestedDateFormat = df_context.get_requested_date_format()
        else:
            self._requestedDateFormat = None
        dateColCheck = None
        scriptsToRun = self._dataframe_context.get_analysis_name_list()

        print self._dateColumnFormatDict
        self._selected_date_columns = self._dataframe_context.get_selected_date_columns()
        if self._selected_date_columns != None:
            dateColCheck = NarrativesUtils.check_date_column_formats(self._selected_date_columns,\
                                                    self._timestamp_columns,\
                                                    self._dateColumnFormatDict,\
                                                    self._dateFormatConversionDict,
                                                    self._requestedDateFormat)
        # print dateColCheck
        if not self._dataframe_context.get_anova_on_scored_data():
            if dateColCheck:
                self._dataframe_context.set_date_format_details(dateColCheck)
                self._dateFormatDetected = dateColCheck["dateFormatDetected"]
                self._trend_on_td_column = dateColCheck["trendOnTdCol"]
                if self._dateFormatDetected:
                    self._requestedDateFormat = dateColCheck["requestedDateFormat"]
                    self._existingDateFormat = dateColCheck["existingDateFormat"]
                    self._date_columns_suggested = dateColCheck["suggestedDateColumn"]
            if self._dateFormatDetected:
                print "self._existingDateFormat",self._existingDateFormat
                print "self._existingDateFormat",self._existingDateFormat
                self._data_frame,self._dataRangeStats = NarrativesUtils.calculate_data_range_stats(self._data_frame,self._existingDateFormat,self._date_columns_suggested,self._trend_on_td_column)

        self._completionStatus = self._dataframe_context.get_completion_status()
        self._analysisName = self._dataframe_context.get_analysis_name()
        self._analysisDict = self._dataframe_context.get_analysis_dict()
        self._messageURL = self._dataframe_context.get_message_url()
        self._scriptWeightDict = self._dataframe_context.get_measure_analysis_weight()
        if analysisName == None:
            self._analysisName = self._dataframe_context.get_analysis_name()
        else:
            self._analysisName = analysisName
        if scriptWeight == None:
            self._scriptWeightDict = self._dataframe_context.get_measure_analysis_weight()
        else:
            self._scriptWeightDict = scriptWeight
        self._scriptStages = {
            "anovaStart":{
                "summary":"Initialized the Anova Scripts",
                "weight":0
                },
            "anovaEnd":{
                "summary":"Anova Calculated",
                "weight":10
                },
            }
        # progressMessage = CommonUtils.create_progress_message_object(self._analysisName,\
        #                             "anovaStart",\
        #                             "info",\
        #                             self._scriptStages["anovaStart"]["summary"],\
        #                             self._completionStatus,\
        #                             self._completionStatus)
        # CommonUtils.save_progress_message(self._messageURL,progressMessage)
        # self._dataframe_context.update_completion_status(self._completionStatus)
        CommonUtils.create_update_and_save_progress_message(self._dataframe_context,self._scriptWeightDict,self._scriptStages,self._analysisName,"anovaStart","info",display=False,emptyBin=False,customMsg=None,weightKey="script")




    @accepts(object, measure_columns=(list, tuple), dimension_columns=(list, tuple))
    def test_all(self, measure_columns=None, dimension_columns=None):
        measures = measure_columns
        if measure_columns is None:
            measures = self._measure_columns
        dimensions = dimension_columns
        print "===================dimensions================"
        if dimension_columns is None:
            dimensions = self._dimension_columns
        try:
            nColsToUse = self._analysisDict[self._analysisName]["noOfColumnsToUse"]
        except:
            nColsToUse = None
        if nColsToUse != None:
            dimensions = dimensions[:nColsToUse]
        sqrt_nrows = round(self._dataframe_helper.get_num_rows()**0.5)
        acceptable_level_count = GLOBALSETTINGS.ANOVAMAXLEVEL
        print {"acceptable_level_count":acceptable_level_count,"sqrt_nrows":sqrt_nrows}
        max_levels = __builtin__.min([acceptable_level_count,int(sqrt_nrows)])
        df_anova_result = DFTwoWayAnovaResult()
        dimensions_to_test = [dim for dim in dimensions if self._dataframe_helper.get_num_unique_values(dim) <= max_levels]
        print "======================= dimensions_to_test ==============================="
        print dimensions_to_test
        self._dimensions_to_test = [x for x in dimensions_to_test if x in self._data_frame.columns]
        print "dimensions to test ",self._dimensions_to_test
        for measure in measures:
            measureColStat = self._data_frame.select([sum(measure).alias("total"),mean(measure).alias("average"),count(measure).alias("count")]).collect()
            measureColMean = measureColStat[0][1]
            measureColCount = measureColStat[0][2]
            measureColSst = self._data_frame.select(sum(pow(col(measure)-measureColMean,2))).collect()[0][0]
            self._anova_result = MeasureAnovaResult(measureColMean=measureColMean,measureColCount=measureColCount, measureColSst=measureColSst)
            print self._dataRangeStats
            if self._dateFormatDetected:
                grouped_data = NarrativesUtils.get_grouped_data_for_trend(self._data_frame,self._dataRangeStats["dataLevel"],measure,"measure")
                trendData = TrendData()
                trendData.set_params(grouped_data,None,\
                                    self._dataRangeStats["lastDate"],\
                                    self._dataRangeStats["firstDate"],\
                                    self._dataRangeStats["duration"],\
                                    self._dataRangeStats["durationString"],\
                                    self._dataRangeStats["dataLevel"]
                                    )
                self._anova_result.set_trend_data(trendData)

            for dimension in self._dimensions_to_test:
                print "dimension--",dimension
                anovaResult = self.one_way_anova_test(self._data_frame,measure,dimension,measureColMean=measureColMean,measureColCount=measureColCount, measureColSst=measureColSst)
                dimensionAnovaResult = OneWayAnovaResult()
                dimensionAnovaResult.set_params(df_within=anovaResult["df_within"],
                                                df_between=anovaResult["df_between"],
                                                sum_of_squares_between=anovaResult["ss_between"],
                                                sum_of_squares_within=anovaResult["ss_within"],
                                                mean_sum_of_squares_between=anovaResult["ms_between"],
                                                mean_sum_of_squares_within=anovaResult["ms_within"],
                                                f_value=anovaResult["f_stat"],
                                                p_value=anovaResult["p_value"],
                                                eta_squared=anovaResult["eta_squared"],
                                                f_critical=anovaResult["f_critical"],
                                                total_number_of_records=anovaResult["n_total"],
                                                n_groups=anovaResult["n_groups"],
                                                levelDf=anovaResult["levelDf"]
                                                )
                self._anova_result.set_oneWayAnovaResultDict(dimension,dimensionAnovaResult)
                # for top level
                if anovaResult["p_value"] < 0.05:
                    effect_size = anovaResult["eta_squared"]
                    self._dataframe_helper.add_significant_dimension(dimension,effect_size)
                    topLevelAnova = TopLevelDfAnovaStats()
                    levelDf = anovaResult["levelDf"]
                    toplevelStats = levelDf.ix[levelDf["total"].argmax()]
                    print "toplevelStats",toplevelStats
                    topLevelAnova.set_top_level_stat(toplevelStats)
                    topLevelDf = self._data_frame.where(col(dimension).isin([toplevelStats.levels]))
                    if self._dateFormatDetected:
                        levelPivot = NarrativesUtils.get_level_pivot(self._data_frame,self._dataRangeStats["dataLevel"],measure,dimension,index_col=None)
                        topLevelGroupedData = NarrativesUtils.get_grouped_data_for_trend(topLevelDf,self._dataRangeStats["dataLevel"],measure,"measure")
                        trendData = TrendData()
                        trendData.set_grouped_data(topLevelGroupedData)
                        trendData.set_level_pivot(levelPivot)
                        topLevelAnova.set_trend_data(trendData)

                    topLevelDfMeasureColStat = topLevelDf.select([sum(measure).alias("total"),mean(measure).alias("average"),count(measure).alias("count")]).collect()
                    topLevelDfMeasureColMean = measureColStat[0][1]
                    topLevelDfMeasureColCount = measureColStat[0][2]
                    topLevelDfMeasureColSst = self._data_frame.select(sum(pow(col(measure)-measureColMean,2))).collect()[0][0]
                    dimensions_to_test_for_top_level = list(set(self._dimensions_to_test) - {dimension})
                    topLevelAnovaDimensions = {}
                    for dimensionlTopLevel in dimensions_to_test_for_top_level:
                        print "top level dimensions",dimensionlTopLevel
                        topLevelDfAnovaResult = self.one_way_anova_test(topLevelDf,measure,dimensionlTopLevel,measureColMean=topLevelDfMeasureColMean,measureColCount=topLevelDfMeasureColCount,measureColSst=topLevelDfMeasureColSst)
                        dimensiontopLevelAnovaResult = OneWayAnovaResult()
                        dimensiontopLevelAnovaResult.set_params(df_within=topLevelDfAnovaResult["df_within"],
                                                        df_between=topLevelDfAnovaResult["df_between"],
                                                        sum_of_squares_between=topLevelDfAnovaResult["ss_between"],
                                                        sum_of_squares_within=topLevelDfAnovaResult["ss_within"],
                                                        mean_sum_of_squares_between=topLevelDfAnovaResult["ms_between"],
                                                        mean_sum_of_squares_within=topLevelDfAnovaResult["ms_within"],
                                                        f_value=topLevelDfAnovaResult["f_stat"],
                                                        p_value=topLevelDfAnovaResult["p_value"],
                                                        eta_squared=topLevelDfAnovaResult["eta_squared"],
                                                        f_critical=topLevelDfAnovaResult["f_critical"],
                                                        total_number_of_records=topLevelDfAnovaResult["n_total"],
                                                        n_groups=topLevelDfAnovaResult["n_groups"],
                                                        levelDf=topLevelDfAnovaResult["levelDf"]
                                                        )
                        topLevelAnova.set_top_level_anova(dimensionlTopLevel,dimensiontopLevelAnovaResult)
                        # contributionDict = self.compute_contributions(topLevelDfAnovaResult["levelDf"])
                        # print contributionDict
                        # topLevelAnova.set_dimension_contributions(dimension,contributionDict)
                    self._anova_result.set_topLevelDfAnovaResult(dimension,topLevelAnova)

            df_anova_result.add_measure_result(measure,self._anova_result)
            print self._anova_result.get_dimensions_analyzed()
            print "checking effect size access",self._anova_result.get_OneWayAnovaEffectSize(self._dimensions_to_test[0])


        # self._completionStatus += self._scriptWeightDict[self._analysisName]["script"]
        # progressMessage = CommonUtils.create_progress_message_object(self._analysisName,\
        #                             "anovaEnd",\
        #                             "info",\
        #                             self._scriptStages["anovaEnd"]["summary"],\
        #                             self._completionStatus,\
        #                             self._completionStatus)
        # CommonUtils.save_progress_message(self._messageURL,progressMessage)
        # self._dataframe_context.update_completion_status(self._completionStatus)
        CommonUtils.create_update_and_save_progress_message(self._dataframe_context,self._scriptWeightDict,self._scriptStages,self._analysisName,"anovaEnd","info",display=False,emptyBin=False,customMsg=None,weightKey="script")
        return df_anova_result



    def one_way_anova_test(self,df,measure,dimension,measureColMean=None,measureColCount=None,measureColSst=None):
        st=time.time()
        print "running anova for :-","measure-",measure,"|***|","dimension-",dimension
        if measureColMean == None:
            measureColStat = df.select([sum(measure).alias("total"),mean(measure).alias("average")]).collect()
            overallMean = measureColStat[0][1]
        else:
            overallMean = measureColMean
        level_aggregate_df = df.na.drop(subset=dimension).groupby(dimension).agg(*[count(col(measure)).alias("count"),mean(col(measure)).alias("average")])
        level_aggregate_df = level_aggregate_df.withColumn("total",col("count")*col("average"))
        level_aggregate_pandasdf = level_aggregate_df.toPandas()
        if measureColCount != None:
            n_total = df.count()
        else:
            n_total = measureColCount
        n_groups = level_aggregate_df.count()
        df_total = n_total-1
        df_within = n_total-n_groups
        df_between = n_groups-1
        if measureColSst == None:
            ss_total = df.select(sum(pow(col(measure)-overallMean,2))).collect()[0][0]
        else:
            ss_total = measureColSst
        ss_between = level_aggregate_df.select(sum(pow(col("average")-overallMean,2))).collect()[0][0]
        ss_within = 0
        for index, row in level_aggregate_pandasdf.iterrows():
            filtered_df = df.filter(col(dimension)==row[dimension])
            group_sse = filtered_df.select(sum(pow(col(measure)-row["average"],2))).collect()[0][0]
            ss_within = ss_within+group_sse
        try:
            ms_between = ss_between/df_between
        except:
            ms_between = 0
        try:
            ms_within = ss_within/df_within
        except:
            ms_within = 0
        try:
            f_stat = ms_between/ms_within
        except:
            f_stat = 0
        f_critical = f.ppf(q=1-0.05, dfn=df_between, dfd=df_within)
        p_value = f.cdf(f_stat, df_between, df_within)
        eta_squared = ss_between/ss_total
        level_aggregate_pandasdf.columns = ["levels"]+list(level_aggregate_pandasdf.columns[1:])
        anovaOutput = {
                       "df_total":df_total,
                       "df_within":df_within,
                       "df_between":df_between,
                       "n_total":n_total,
                       "n_groups":n_groups,
                       "ss_between":ss_between,
                       "ss_within":ss_within,
                       "ss_total":ss_total,
                       "ms_between":ms_between,
                       "ms_within":ms_within,
                       "f_stat":f_stat,
                       "f_critical":f_critical,
                       "p_value":p_value,
                       "eta_squared":eta_squared,
                       "levelDf":level_aggregate_pandasdf
                      }
        # print anovaOutput
        print "finished in :-",time.time()-st
        return anovaOutput


    def test_anova_interaction(self,measure,dimension1,dimension2):
        var = self._data_frame.groupby(dimension1,dimension2).agg(*[count(col(measure)),mean(col(measure))]).collect()
        var = pd.DataFrame(var,columns=['level1','level2', 'counts', 'means'])
        var['total'] = var.means*var.counts
        #var['var5'] = var.counts*var.means*var.means
        sse = 0
        for i in range(len(var)):
            group_sse = self._data_frame.filter((col(dimension1)==var.level1[i]) & (col(dimension2)==var.level2[i])).\
                        select((col(measure)-var.means[i])*(col(measure)-var.means[i])).\
                        agg({'*':'sum'}).collect()
            sse = sse+group_sse[0][0]
        self._anova_result.set_TwoWayAnovaResult(dimension1,dimension2,var,sse)
