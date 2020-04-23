import pandas as pd
import time
from datetime import datetime

import pandas as pd
from dateutil.relativedelta import relativedelta
from pyspark.sql.functions import col, udf
from pyspark.sql.functions import lit

from bi.common import NarrativesTree, NormalCard, HtmlData, C3ChartData
from bi.common import ScatterChartData, NormalChartData, ChartJson
from bi.common import utils as CommonUtils
from bi.narratives import utils as NarrativesUtils
from bi.settings import setting as GLOBALSETTINGS
from trend_narratives import TrendNarrative


class TimeSeriesNarrative:
    def __init__(self, df_helper, df_context, result_setter, spark, story_narrative, meta_parser):
        self._story_narrative = story_narrative
        self._result_setter = result_setter
        self._spark = spark
        self._dataframe_helper = df_helper
        self._dataframe_context = df_context
        self._data_frame = df_helper.get_data_frame()
        self._num_significant_digits = NarrativesUtils.get_significant_digit_settings("trend")
        self._metaParser = meta_parser


        self._result_column = self._dataframe_context.get_result_column()
        self._string_columns = self._dataframe_helper.get_string_columns()
        self._timestamp_columns = self._dataframe_helper.get_timestamp_columns()

        # self._selected_date_columns = None
        self._selected_date_columns = self._dataframe_context.get_selected_date_columns()
        self._all_date_columns = self._dataframe_context.get_date_columns()
        self._string_columns = list(set(self._string_columns)-set(self._all_date_columns))

        self._dateFormatDetected = False
        self._existingDateFormat = None
        self._dateFormatConversionDict = NarrativesUtils.date_formats_mapping_dict()
        self._dateColumnFormatDict =  df_context.get_date_format_dict()
        if self._dataframe_context.get_requested_date_format() != None:
            self._requestedDateFormat = df_context.get_requested_date_format()
        else:
            self._requestedDateFormat = None

        self._analysistype = self._dataframe_context.get_analysis_type()
        self._trendSettings = self._dataframe_context.get_trend_settings()
        self._trendSpecificMeasure = False
        if self._trendSettings != None:
            if self._analysistype == "dimension" and self._trendSettings["name"] != "Count":
                self._trendSpecificMeasure = True
                self._analysistype = "measure"
                self._result_column = self._trendSettings["selectedMeasure"]
            elif self._analysistype == "measure" and self._trendSettings["name"] != "Count":
                self._result_column = self._trendSettings["selectedMeasure"]

        self._trend_subsection = self._result_setter.get_trend_section_name()
        self._regression_trend_card = None
        self._blockSplitter = GLOBALSETTINGS.BLOCKSPLITTER
        self._highlightFlag = "|~HIGHLIGHT~|"
        self._trend_on_td_column = False
        self._number_of_dimensions_to_consider = 10

        self._completionStatus = self._dataframe_context.get_completion_status()
        self._analysisName = self._dataframe_context.get_analysis_name()
        self._messageURL = self._dataframe_context.get_message_url()
        if self._analysistype == "dimension":
            self._scriptWeightDict = self._dataframe_context.get_dimension_analysis_weight()
            self._scriptStages = {
                "initialization":{
                    "summary":"Initialized the Frequency Narratives",
                    "weight":0
                    },
                "summarygeneration":{
                    "summary":"summary generation finished",
                    "weight":10
                    },
                "completion":{
                    "summary":"Frequency Stats Narratives done",
                    "weight":0
                    },
                }
        elif self._analysistype == "measure":
            if self._trendSpecificMeasure:
                self._scriptWeightDict = self._dataframe_context.get_dimension_analysis_weight()
            else:
                self._scriptWeightDict = self._dataframe_context.get_measure_analysis_weight()
            self._scriptStages = {
                "trendNarrativeStart":{
                    "summary":"Started the Descriptive Stats Narratives",
                    "weight":1
                    },
                "trendNarrativeEnd":{
                    "summary":"Narratives for descriptive Stats Finished",
                    "weight":0
                    },
                }

        self._base_dir = "/trend/"
        dateColCheck = NarrativesUtils.check_date_column_formats(self._selected_date_columns,\
                                                    self._timestamp_columns,\
                                                    self._dateColumnFormatDict,\
                                                    self._dateFormatConversionDict,
                                                    self._requestedDateFormat)
        print dateColCheck

        self._dateFormatDetected = dateColCheck["dateFormatDetected"]
        self._trend_on_td_column = dateColCheck["trendOnTdCol"]
        if self._dateFormatDetected:
            self._requestedDateFormat = dateColCheck["requestedDateFormat"]
            self._existingDateFormat = dateColCheck["existingDateFormat"]
            # self._date_column_suggested is the column used for trend
            self._date_column_suggested = dateColCheck["suggestedDateColumn"]
        if self._existingDateFormat:
            self._data_frame,dataRangeStats = NarrativesUtils.calculate_data_range_stats(self._data_frame,self._existingDateFormat,self._date_column_suggested,self._trend_on_td_column)
            print dataRangeStats
            self._durationString = dataRangeStats["durationString"]
            self._duration = dataRangeStats["duration"]
            self._dataLevel = dataRangeStats["dataLevel"]
            first_date = dataRangeStats["firstDate"]
            last_date = dataRangeStats["lastDate"]

            if self._timestamp_columns != None:
                if self._selected_date_columns == None:
                    self._selected_date_columns = self._timestamp_columns
                else:
                    self._selected_date_columns += self._timestamp_columns
        if self._trend_subsection=="regression":
            if self._selected_date_columns != None:
                if self._dateFormatDetected:
                    trend_subsection_data = self._result_setter.get_trend_section_data()
                    measure_column = trend_subsection_data["measure_column"]
                    result_column = trend_subsection_data["result_column"]
                    base_dir = trend_subsection_data["base_dir"]

                    card3heading = 'How '+ result_column +' and '+ measure_column + ' changed over time'
                    if self._dataLevel == "day":
                        grouped_data = self._data_frame.groupBy("suggestedDate").agg({measure_column : 'sum', result_column : 'sum'})
                        grouped_data = grouped_data.withColumnRenamed(grouped_data.columns[-1],result_column)
                        grouped_data = grouped_data.withColumnRenamed(grouped_data.columns[-2],measure_column)
                        grouped_data = grouped_data.withColumn("year_month",udf(lambda x:x.strftime("%b-%y"))("suggestedDate"))
                        grouped_data = grouped_data.orderBy("suggestedDate",ascending=True)
                        grouped_data = grouped_data.withColumnRenamed(grouped_data.columns[0],"key")
                        grouped_data = grouped_data.toPandas()
                    elif self._dataLevel == "month":
                        grouped_data = self._data_frame.groupBy("year_month").agg({measure_column : 'sum', result_column : 'sum'})
                        grouped_data = grouped_data.withColumnRenamed(grouped_data.columns[-1],result_column)
                        grouped_data = grouped_data.withColumnRenamed(grouped_data.columns[-2],measure_column)
                        grouped_data = grouped_data.withColumn("suggestedDate",udf(lambda x:datetime.strptime(x,"%b-%y"))("year_month"))
                        grouped_data = grouped_data.orderBy("suggestedDate",ascending=True)
                        grouped_data = grouped_data.withColumnRenamed("suggestedDate","key")
                        grouped_data = grouped_data.select(["key",measure_column,result_column,"year_month"]).toPandas()
                        grouped_data["key"] = grouped_data["year_month"].apply(lambda x: datetime.strptime(x,"%b-%y").date())

                    trend_narrative_obj = TrendNarrative(self._result_column,self._date_column_suggested,grouped_data,self._existingDateFormat,self._requestedDateFormat,self._base_dir, self._metaParser)

                    card3data = trend_narrative_obj.generate_regression_trend_data(grouped_data,measure_column,result_column,self._dataLevel,self._durationString)

                    card3narrative = NarrativesUtils.get_template_output(base_dir,\
                                                                    'regression_card3.html',card3data)


                    card3chart =trend_narrative_obj.generate_regression_trend_chart(grouped_data,self._dataLevel)
                    card3paragraphs = NarrativesUtils.paragraph_splitter(card3narrative)
                    card2 = {'charts': card3chart, 'paragraphs': card3paragraphs, 'heading': card3heading}
                    self.set_regression_trend_card_data(card2)
                else:
                    print "NO DATE FORMAT DETECTED"
            else:
                print "NO DATE COLUMNS PRESENT"


        if self._analysistype=="measure":
            self._completionStatus += self._scriptWeightDict[self._analysisName]["total"]*self._scriptStages["trendNarrativeStart"]["weight"]/10
            progressMessage = CommonUtils.create_progress_message_object(self._analysisName,\
                                        "trendNarrativeStart",\
                                        "info",\
                                        self._scriptStages["trendNarrativeStart"]["summary"],\
                                        self._completionStatus,\
                                        self._completionStatus)
            CommonUtils.save_progress_message(self._messageURL,progressMessage)
            self._dataframe_context.update_completion_status(self._completionStatus)
            # self._startMeasureTrend = self._result_setter.get_trend_section_completion_status()
            self._startMeasureTrend = True

            if self._startMeasureTrend == True:
                self.narratives = {"SectionHeading":"",
                                   "card1":{},
                                   "card2":{},
                                   "card3":{}
                                }
                if self._selected_date_columns != None:
                    if self._dateFormatDetected:
                        grouped_data = NarrativesUtils.get_grouped_data_for_trend(self._data_frame,self._dataLevel,self._result_column,self._analysistype)
                        self._data_frame = self._data_frame.drop(self._date_column_suggested)
                        # self._data_frame = self._data_frame.withColumnRenamed("year_month", self._date_column_suggested)

                        significant_dimensions = []
                        significant_dimension_dict = df_helper.get_significant_dimension()
                        if significant_dimension_dict != {} and significant_dimension_dict != None:
                            significant_dimension_tuple = tuple(significant_dimension_dict.items())
                            significant_dimension_tuple = sorted(significant_dimension_tuple,key=lambda x: x[1],reverse=True)
                            significant_dimensions = [x[0] for x in significant_dimension_tuple[:self._number_of_dimensions_to_consider]]
                        else:
                            significant_dimensions = self._string_columns[:self._number_of_dimensions_to_consider]
                        print "significant_dimensions",significant_dimensions
                        trend_narrative_obj = TrendNarrative(self._result_column,self._date_column_suggested,grouped_data,self._existingDateFormat,self._requestedDateFormat,self._base_dir, self._metaParser)
                        # grouped_data.to_csv("/home/gulshan/marlabs/datasets/trend_grouped_pandas.csv",index=False)
                        dataDict = trend_narrative_obj.generateDataDict(grouped_data,self._dataLevel,self._durationString)
                        # # update reference time with max value
                        reference_time = dataDict["reference_time"]
                        dataDict["duration"] = self._duration
                        dataDict["dataLevel"] = self._dataLevel
                        dataDict["durationString"] = self._durationString
                        dataDict["significant_dimensions"] = significant_dimensions
                        if len(significant_dimensions) > 0:
                            if self._dataLevel=="day":
                                datetimeformat = self._existingDateFormat
                            elif self._dataLevel=="month":
                                datetimeformat = "%b-%y"
                            # xtraData = trend_narrative_obj.get_xtra_calculations(self._data_frame,grouped_data,significant_dimensions,self._date_column_suggested,self._result_column,self._existingDateFormat,reference_time,self._dataLevel)
                            xtraData = trend_narrative_obj.get_xtra_calculations(self._data_frame,grouped_data,significant_dimensions,self._date_column_suggested,self._result_column,datetimeformat,reference_time,self._dataLevel)
                            if xtraData != None:
                                dataDict.update(xtraData)
                        # print 'Trend dataDict:  %s' %(json.dumps(dataDict, indent=2))
                        self._result_setter.update_executive_summary_data(dataDict)
                        dataDict.update({"blockSplitter":self._blockSplitter,"highlightFlag":self._highlightFlag})

                        summary1 = NarrativesUtils.get_template_output(self._base_dir,\
                                                                        'measure_trend_card1.html',dataDict)
                        summary2 = NarrativesUtils.get_template_output(self._base_dir,\
                                                                        'measure_trend_card2.html',dataDict)
                        measureTrendCard = NormalCard()
                        measureTrendcard1Data = NarrativesUtils.block_splitter(summary1,self._blockSplitter,highlightFlag=self._highlightFlag)
                        measureTrendcard2Data = NarrativesUtils.block_splitter(summary2,self._blockSplitter)
                        # print measureTrendcard1Data

                        bubbledata = dataDict["bubbleData"]
                        # print bubbledata
                        card1BubbleData = "<div class='col-md-6 col-xs-12 xs-p-20'><h2 class='text-center'><span>{}</span><br/><small>{}</small></h2></div><div class='col-md-6 col-xs-12 xs-p-20'><h2 class='text-center'><span>{}</span><br/><small>{}</small></h2></div>".format(bubbledata[0]["value"],bubbledata[0]["text"],bubbledata[1]["value"],bubbledata[1]["text"])
                        # print card1BubbleData

                        trend_chart_data = grouped_data[["key","value"]].T.to_dict().values()
                        trend_chart_data = sorted(trend_chart_data,key=lambda x:x["key"])
                        card1chartdata = {"actual":[],"predicted":[]}

                        if self._dataLevel == "day":
                            card1chartdata["actual"] = [{"key":str(val["key"]),"value":val["value"]} for val in trend_chart_data]
                        elif self._dataLevel == "month":
                            card1chartdata["actual"] = [{"key":val["key"].strftime("%b-%y"),"value":val["value"]} for val in trend_chart_data]

                        if self._duration<365:
                            prediction_window = 3
                        else:
                            prediction_window = 6
                        predicted_values = trend_narrative_obj.get_forecast_values(grouped_data["value"],prediction_window)[len(grouped_data["value"]):]
                        predicted_values = [round(x,self._num_significant_digits) for x in predicted_values]

                        forecasted_data = []
                        forecasted_data.append(card1chartdata["actual"][-1])
                        forecasted_dates = []
                        # forecast_start_time = datetime.strptime(card1chartdata["actual"][-1]["key"],"%b-%y")
                        if self._dataLevel == "month":
                            forecast_start_time = datetime.strptime(card1chartdata["actual"][-1]["key"],"%b-%y")
                        elif self._dataLevel == "day":
                            forecast_start_time = datetime.strptime(card1chartdata["actual"][-1]["key"],"%Y-%m-%d")
                        for val in range(prediction_window):
                            if self._dataLevel == "month":
                                key = forecast_start_time+relativedelta(months=1+val)
                                forecasted_dates.append(key)
                            elif self._dataLevel == "day":
                                key = forecast_start_time+relativedelta(days=1+val)
                                forecasted_dates.append(key)
                        forecasted_list = zip(forecasted_dates,predicted_values)
                        if self._dataLevel == "month":
                            forecasted_list = [{"key":val[0].strftime("%b-%y"),"value":val[1]} for val in forecasted_list]
                        elif self._dataLevel == "day":
                            forecasted_list = [{"key":val[0].strftime("%Y-%m-%d"),"value":val[1]} for val in forecasted_list]
                        forecasted_data += forecasted_list
                        card1chartdata["predicted"] = forecasted_data
                        # print json.dumps(card1chartdata,indent=2)
                        card1chartdata = ScatterChartData(data=card1chartdata)
                        chartJson = ChartJson()
                        chartJson.set_data(card1chartdata.get_data())
                        chartJson.set_label_text({'x':' ','y': 'No. of Observations'})
                        chartJson.set_legend({"actual":"Observed","predicted":"Forecast"})
                        chartJson.set_chart_type("scatter_line")
                        chartJson.set_axes({"x":"key","y":"value"})
                        chartJson.set_yaxis_number_format(".2f")
                        st_info = ["Trend Analysis", "Forecast Method : Holt Winters Method"]
                        measureTrendcard1Data.insert(1,C3ChartData(data=chartJson,info=st_info))
                        measureTrendcard1Data.append(HtmlData(data=card1BubbleData))
                        cardData = measureTrendcard1Data+measureTrendcard2Data
                        measureTrendCard.set_card_data(cardData)
                        measureTrendCard.set_card_name("Trend Analysis")
                        trendStoryNode = NarrativesTree("Trend",None,[],[measureTrendCard])
                        self._story_narrative.add_a_node(trendStoryNode)
                        self._result_setter.set_trend_node(trendStoryNode)

                        # prediction_data = [{"key":x["key"],"value":x["value"]} for x in trend_chart_data]
                        # last_val = prediction_data[-1]
                        # last_val.update({"predicted_value":last_val["value"]})
                        # prediction_data[-1] = last_val
                        #
                        # for val in range(prediction_window):
                        #     dataLevel = dataDict["dataLevel"]
                        #     if self._dataLevel == "month":
                        #         last_key = prediction_data[-1]["key"]
                        #         key = last_key+relativedelta(months=1)
                        #         prediction_data.append({"key":key,"predicted_value":predicted_values[val]})
                        #         forecasted_data.append({"key":key,"value":predicted_values[val]})
                        #     elif self._dataLevel == "day":
                        #         last_key = prediction_data[-1]["key"]
                        #         key = last_key+relativedelta(days=1)
                        #         prediction_data.append({"key":key,"predicted_value":predicted_values[val]})
                        # prediction_data_copy = prediction_data
                        # prediction_data = []
                        # for val in prediction_data_copy:
                        #     val["key"] = val["key"].strftime("%b-%y")
                        #     prediction_data.append(val)

                        # forecastDataDict = {"startForecast":predicted_values[0],
                        #                     "endForecast":predicted_values[prediction_window-1],
                        #                     "measure":dataDict["measure"],
                        #                     "forecast":True,
                        #                     "forecast_percentage": round((predicted_values[prediction_window-1]-predicted_values[0])/predicted_values[0],self._num_significant_digits),
                        #                     "prediction_window_text": str(prediction_window) + " months"
                        #                     }
                        #
                        # self._result_setter.update_executive_summary_data(forecastDataDict)
                        # summary3 = NarrativesUtils.get_template_output(self._base_dir,\
                                                                        # 'trend_narrative_card3.html',forecastDataDict)
                        self._completionStatus += self._scriptWeightDict[self._analysisName]["total"]*self._scriptStages["trendNarrativeEnd"]["weight"]/10
                        progressMessage = CommonUtils.create_progress_message_object(self._analysisName,\
                                                    "trendNarrativeEnd",\
                                                    "info",\
                                                    self._scriptStages["trendNarrativeEnd"]["summary"],\
                                                    self._completionStatus,\
                                                    self._completionStatus)
                        CommonUtils.save_progress_message(self._messageURL,progressMessage)
                        self._dataframe_context.update_completion_status(self._completionStatus)
                    else:
                        # self._result_setter.update_executive_summary_data({"trend_present":False})
                        print "Trend Analysis for Measure Failed"
                        print "#"*20+"Trend Analysis Error"+"#"*20
                        print "No date format for the date column %s was detected." %(self._date_column_suggested)
                        print "#"*60
                        self._completionStatus += self._scriptWeightDict[self._analysisName]["total"]
                        self._dataframe_context.update_completion_status(completionStatus)
                        progressMessage = CommonUtils.create_progress_message_object("Trend","failedState","error",\
                                        "Trend failed as "+"No date format for the date column %s was detected." %(self._date_column_suggested),\
                                        completionStatus,completionStatus)
                        CommonUtils.save_progress_message(messageURL,progressMessage)
                        self._dataframe_context.update_completion_status(self._completionStatus)
                else:
                    # self._result_setter.update_executive_summary_data({"trend_present":False})
                    print "Trend Analysis for Measure Failed"
                    print "#"*20+"Trend Analysis Error"+"#"*20
                    print "No date column present for Trend Analysis."
                    print "#"*60
                    self._completionStatus += self._scriptWeightDict[self._analysisName]["total"]
                    self._dataframe_context.update_completion_status(completionStatus)
                    progressMessage = CommonUtils.create_progress_message_object("Trend","failedState","error",\
                                    "No Date Column Present",\
                                    completionStatus,completionStatus)
                    CommonUtils.save_progress_message(messageURL,progressMessage)
                    self._dataframe_context.update_completion_status(self._completionStatus)
            else:
                print "overall Trend not Started YET"

        elif self._analysistype == "dimension":
            print "Dimension Trend Started"
            self._completionStatus += self._scriptWeightDict[self._analysisName]["total"]*self._scriptStages["initialization"]["weight"]/10
            progressMessage = CommonUtils.create_progress_message_object(self._analysisName,\
                                        "initialization",\
                                        "info",\
                                        self._scriptStages["initialization"]["summary"],\
                                        self._completionStatus,\
                                        self._completionStatus)
            CommonUtils.save_progress_message(self._messageURL,progressMessage)
            self._dataframe_context.update_completion_status(self._completionStatus)



            self.narratives = {
                               "card0":{}
                               }
            if self._selected_date_columns != None:
                if self._dateFormatDetected:
                    # result_column_levels = [x[0] for x in self._data_frame.select(self._result_column).distinct().collect()]
                    try:
                        result_column_levels = self._metaParser.get_unique_level_names(self._result_column)
                    except:
                        result_column_levels = [x[0] for x in self._data_frame.select(self._result_column).distinct().collect()]

                    print "-"*100
                    # TODO Implement meta parser getter here
                    print result_column_levels
                    level_count_df = self._data_frame.groupBy(self._result_column).count().orderBy("count",ascending=False)
                    level_count_df_rows =  level_count_df.collect()
                    top2levels = [level_count_df_rows[0][0],level_count_df_rows[1][0]]
                    cardData = []
                    chart_data = {}
                    cardData1 = []
                    c3_chart = {"dataType":"c3Chart","data":{}}
                    print "#"*40
                    overall_count = NarrativesUtils.get_grouped_count_data_for_dimension_trend(self._data_frame,self._dataLevel,self._result_column)
                    print "#"*40
                    for idx,level in  enumerate(top2levels):
                        print "calculations in progress for the level :- ",level
                        leveldf = self._data_frame.filter(col(self._result_column) == level)
                        grouped_data = NarrativesUtils.get_grouped_data_for_trend(leveldf,self._dataLevel,self._result_column,self._analysistype )
                        grouped_data.rename(columns={"value":"value_count"},inplace=True)
                        grouped_data = pd.merge(grouped_data, overall_count, on='key', how='left')
                        # grouped_data["value"] = grouped_data["value_count"].apply(lambda x:round(x*100/float(self._data_frame.count()),self._num_significant_digits))
                        grouped_data["value"] = grouped_data["value_count"]/grouped_data["totalCount"]
                        grouped_data["value"] = grouped_data["value"].apply(lambda x:round(x*100,self._num_significant_digits))
                        leveldf = leveldf.drop(self._date_column_suggested)
                        leveldf = leveldf.withColumnRenamed("year_month", self._date_column_suggested)
                        if "year_month" not in leveldf.columns:
                            leveldf = leveldf.withColumn("year_month", col(self._date_column_suggested))
                        leveldf = leveldf.withColumn('value_col', lit(1))

                        trend_narrative_obj = TrendNarrative(self._result_column,self._date_column_suggested,grouped_data,self._existingDateFormat,self._requestedDateFormat,self._base_dir, self._metaParser)
                        dataDict = trend_narrative_obj.generateDataDict(grouped_data,self._dataLevel,self._durationString)
                        dataDict["target_column"] = dataDict["measure"]
                        dataDict["measure"] = level
                        dataDict["duration"] = self._duration
                        dataDict["dataLevel"] = self._dataLevel
                        dataDict["durationString"] = self._durationString
                        # grouped_data.to_csv("/home/gulshan/marlabs/datasets/grouped_data"+str(idx))
                        # print json.dumps(dataDict,indent=2)
                        significant_dimensions = []
                        significant_dimension_dict = df_helper.get_chisquare_significant_dimension()
                        if significant_dimension_dict != {} and significant_dimension_dict != None:
                            significant_dimension_tuple = tuple(significant_dimension_dict.items())
                            significant_dimension_tuple = sorted(significant_dimension_tuple,key=lambda x: x[1],reverse=True)
                            significant_dimensions = [x[0] for x in significant_dimension_tuple[:self._number_of_dimensions_to_consider]]
                        else:
                            significant_dimensions = self._string_columns[:self._number_of_dimensions_to_consider]
                        print "significant_dimensions",significant_dimensions
                        reference_time = dataDict["reference_time"]
                        dataDict["significant_dimensions"] = significant_dimensions
                        if len(significant_dimensions) > 0:
                            st = time.time()
                            xtraData = trend_narrative_obj.get_xtra_calculations(leveldf,grouped_data,significant_dimensions,self._date_column_suggested,"value_col",self._existingDateFormat,reference_time,self._dataLevel)
                            print "time for get_xtra_calculations" ,time.time()-st
                            if xtraData != None:
                                dataDict.update(xtraData)
                        dimensionCount = trend_narrative_obj.generate_dimension_extra_narrative(grouped_data,dataDict,self._dataLevel)
                        if dimensionCount != None:
                            dataDict.update(dimensionCount)

                        dataDict.update({"level_index":idx,"blockSplitter":self._blockSplitter,"highlightFlag":self._highlightFlag})


                        self._result_setter.update_executive_summary_data(dataDict)
                        trendStory = NarrativesUtils.get_template_output(self._base_dir,\
                                                                        'dimension_trend.html',dataDict)
                        blocks = NarrativesUtils.block_splitter(trendStory,self._blockSplitter)

                        if idx != 0:
                            cardData1 += blocks[2:]
                        else:
                            cardData1 += blocks

                        trend_chart_data = grouped_data[["key","value"]].T.to_dict().values()
                        trend_chart_data = sorted(trend_chart_data,key=lambda x:x["key"])
                        card1chartdata = trend_chart_data
                        if self._dataLevel == "day":
                                card1chartdata = [{"key":str(val["key"]),"value":val["value"]} for val in card1chartdata]
                        elif self._dataLevel == "month":
                            card1chartdata = [{"key":val["key"].strftime("%b-%y"),"value":val["value"]} for val in card1chartdata]
                        chart_data[level] = card1chartdata

                    labels = {"x":"key","y":chart_data.keys()[0],"y2":chart_data.keys()[1]}
                    c3Chart = {
                               "data":chart_data,
                               "format":"%b-%y",
                               "label":labels,
                               "label_text":{
                                             "x":"Time",
                                             "y":"Percentage of "+labels["y"],
                                             "y2":"Percentage of "+labels["y2"]
                                             }
                               }


                    c3_chart["data"] = c3Chart
                    multiLineData = []
                    for idx in range(len(chart_data[top2levels[0]])):
                        key = chart_data[top2levels[0]][idx]["key"]
                        value = chart_data[top2levels[0]][idx]["value"]
                        try:
                            value1 = chart_data[top2levels[1]][idx]["value"]
                        except:
                            value1 = 0
                        multiLineData.append({"key":key,top2levels[0]:value,top2levels[1]:value1})
                    chartData = NormalChartData(multiLineData)
                    chartJson = ChartJson()
                    chartJson.set_data(chartData.get_data())
                    chartJson.set_label_text(c3Chart["label_text"])
                    chartJson.set_legend(c3Chart["label"])
                    chartJson.set_chart_type("line")
                    chartJson.set_yaxis_number_format(".2f")
                    chartJson.set_axes(labels)
                    st_info = ["Trend Analysis", "Forecast Method : Holt Winters Method"]
                    cardData1.insert(1,C3ChartData(data=chartJson,info=st_info))
                    trendCard = NormalCard(name="Trend Analysis",slug=None,cardData = cardData1)
                    trendStoryNode = NarrativesTree("Trend",None,[],[trendCard])
                    self._story_narrative.add_a_node(trendStoryNode)
                    self._result_setter.set_trend_node(trendStoryNode)
                    self._completionStatus += self._scriptWeightDict[self._analysisName]["total"]*self._scriptStages["summarygeneration"]["weight"]/10
                    progressMessage = CommonUtils.create_progress_message_object(self._analysisName,\
                                                "summarygeneration",\
                                                "info",\
                                                self._scriptStages["summarygeneration"]["summary"],\
                                                self._completionStatus,\
                                                self._completionStatus)
                    CommonUtils.save_progress_message(self._messageURL,progressMessage)
                    self._dataframe_context.update_completion_status(self._completionStatus)

                    self._completionStatus += self._scriptWeightDict[self._analysisName]["total"]*self._scriptStages["completion"]["weight"]/10
                    progressMessage = CommonUtils.create_progress_message_object(self._analysisName,\
                                                "completion",\
                                                "info",\
                                                self._scriptStages["completion"]["summary"],\
                                                self._completionStatus,\
                                                self._completionStatus)
                    CommonUtils.save_progress_message(self._messageURL,progressMessage)
                    self._dataframe_context.update_completion_status(self._completionStatus)
                else:
                    self._result_setter.update_executive_summary_data({"trend_present":False})
                    print "Trend Analysis for Dimension Failed"
                    print "#"*20+"Trend Analysis Error"+"#"*20
                    if self._date_column_suggested:
                        print "No date format for the date column %s was detected." %(self._date_column_suggested)
                    print "#"*60
                    self._completionStatus += self._scriptWeightDict[self._analysisName]["total"]
                    self._dataframe_context.update_completion_status(self._completionStatus)
                    progressMessage = CommonUtils.create_progress_message_object("Trend","failedState","error",\
                                    "Trend failed as "+"No date format for the date column %s was detected." %(self._date_column_suggested),\
                                    self._completionStatus,self._completionStatus)
                    CommonUtils.save_progress_message(messageURL,progressMessage)
                    self._dataframe_context.update_completion_status(self._completionStatus)

            else:
                self._result_setter.update_executive_summary_data({"trend_present":False})
                print "Trend Analysis for Dimension Failed"
                print "#"*20+"Trend Analysis Error"+"#"*20
                print "No date column present for Trend Analysis."
                print "#"*60
                self._completionStatus += self._scriptWeightDict[self._analysisName]["total"]
                self._dataframe_context.update_completion_status(self._completionStatus)
                progressMessage = CommonUtils.create_progress_message_object("Trend","failedState","error",\
                                "No date column present",\
                                self._completionStatus,self._completionStatus)
                CommonUtils.save_progress_message(messageURL,progressMessage)
                self._dataframe_context.update_completion_status(self._completionStatus)

    def set_regression_trend_card_data(self,data):
        self._regression_trend_card = data

    def get_regression_trend_card_data(self):
        return self._regression_trend_card

    def get_story_narrative(self):
        return self._story_narrative

__all__ = [
    'TrendNarrative',
    'TimeSeriesCalculations'
]
