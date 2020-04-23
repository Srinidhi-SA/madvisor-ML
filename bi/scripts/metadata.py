import time
import uuid

from bi.common import ColumnType
from bi.common import MetaDataHelper
from bi.common import utils as CommonUtils
from bi.common.results import DfMetaData, MetaData, ColumnData, ColumnHeader


class MetaDataScript:
    def __init__(self, data_frame, spark, dataframe_context):
        self._dataframe_context = dataframe_context
        self._completionStatus = self._dataframe_context.get_completion_status()
        self._start_time = time.time()
        self._analysisName = "metadata"
        self._messageURL = self._dataframe_context.get_message_url()
        self._ignoreMsgFlag = self._dataframe_context.get_metadata_ignore_msg_flag()
        self._scriptStages = {
            "schema":{
                "summary":"Loaded the data and Schema is Run",
                "weight":12
                },
            "sampling":{
                "summary":"Sampling the dataframe",
                "weight":5
                },
            "measurestats":{
                "summary":"calculating stats for measure columns",
                "weight":25
                },
            "dimensionstats":{
                "summary":"calculating stats for dimension columns",
                "weight":25
                },
            "timedimensionstats":{
                "summary":"calculating stats for time dimension columns",
                "weight":5
                },
            "suggestions":{
                "summary":"Ignore and Date Suggestions",
                "weight":25
                },
            }

        self._binned_stat_flag = True
        self._level_count_flag = True
        self._stripTimestamp = True
        self._data_frame = data_frame
        self._spark = spark
        self._total_columns = len([field.name for field in self._data_frame.schema.fields])
        self._total_rows = self._data_frame.count()
        self._max_levels = min(200, round(self._total_rows**0.5))

        self._percentage_columns = []
        self._numeric_columns = [field.name for field in self._data_frame.schema.fields if
                ColumnType(type(field.dataType)).get_abstract_data_type() == ColumnType.MEASURE]
        self._string_columns = [field.name for field in self._data_frame.schema.fields if
                ColumnType(type(field.dataType)).get_abstract_data_type() == ColumnType.DIMENSION]
        self._timestamp_columns = [field.name for field in self._data_frame.schema.fields if
                ColumnType(type(field.dataType)).get_abstract_data_type() == ColumnType.TIME_DIMENSION]
        self._boolean_columns = [field.name for field in self._data_frame.schema.fields if
                ColumnType(type(field.dataType)).get_abstract_data_type() == ColumnType.BOOLEAN]
        self._real_columns = [field.name for field in self._data_frame.schema.fields if
                ColumnType(type(field.dataType)).get_actual_data_type() == ColumnType.REAL]
        self._column_type_dict = {}
        self._dataSize = {"nRows":self._total_rows,"nCols":self._total_columns,"nBooleans":None,"nMeasures":None,"nDimensions":None,"nTimeDimensions":None,"dimensionLevelCountDict":{},"totalLevels":None}
        self.update_column_type_dict()

        time_taken_schema = time.time()-self._start_time
        print "schema rendering takes",time_taken_schema

        self._completionStatus += self._scriptStages["schema"]["weight"]
        progressMessage = CommonUtils.create_progress_message_object(self._analysisName,\
                                    "schema",\
                                    "info",\
                                    self._scriptStages["schema"]["summary"],\
                                    self._completionStatus,\
                                    self._completionStatus)
        CommonUtils.save_progress_message(self._messageURL,progressMessage,ignore=self._ignoreMsgFlag)
        self._dataframe_context.update_completion_status(self._completionStatus)

    def update_column_type_dict(self):
        self._column_type_dict = dict(\
                                        zip(self._numeric_columns,[{"actual":"measure","abstract":"measure"}]*len(self._numeric_columns))+\
                                        zip(self._string_columns,[{"actual":"dimension","abstract":"dimension"}]*len(self._string_columns))+\
                                        zip(self._timestamp_columns,[{"actual":"datetime","abstract":"datetime"}]*len(self._timestamp_columns))+\
                                        zip(self._boolean_columns,[{"actual":"boolean","abstract":"dimension"}]*len(self._boolean_columns))\
                                     )
        self._dataSize["nMeasures"] = len(self._numeric_columns)
        self._dataSize["nDimensions"] = len(self._string_columns)
        self._dataSize["nTimeDimensions"] = len(self._timestamp_columns)
        self._dataSize["nBooleans"] = len(self._boolean_columns)


    def run(self):
        self._start_time = time.time()
        metaHelperInstance = MetaDataHelper(self._data_frame, self._total_rows)
        sampleData = metaHelperInstance.get_sample_data()
        sampleData = sampleData.toPandas()
        sampleData = metaHelperInstance.format_sampledata_timestamp_columns(sampleData,self._timestamp_columns,self._stripTimestamp)
        time_taken_sampling = time.time()-self._start_time
        self._completionStatus += self._scriptStages["sampling"]["weight"]
        print "sampling takes",time_taken_sampling
        progressMessage = CommonUtils.create_progress_message_object(self._analysisName,\
                                    "sampling",\
                                    "info",\
                                    self._scriptStages["sampling"]["summary"],\
                                    self._completionStatus,\
                                    self._completionStatus)
        CommonUtils.save_progress_message(self._messageURL,progressMessage,ignore=self._ignoreMsgFlag)

        metaData = []
        metaData.append(MetaData(name="noOfRows",value=self._total_rows,display=True,displayName="Rows"))
        metaData.append(MetaData(name="noOfColumns",value=self._total_columns,display=True,displayName="Columns"))
        self._percentage_columns = metaHelperInstance.get_percentage_columns(self._string_columns)
        if len(self._percentage_columns)>0:
            self._data_frame = CommonUtils.convert_percentage_columns(self._data_frame,self._percentage_columns)
            self._numeric_columns = self._numeric_columns + self._percentage_columns
            self._string_columns = list(set(self._string_columns)-set(self._percentage_columns))
            self.update_column_type_dict()

        self._dollar_columns = metaHelperInstance.get_dollar_columns(self._string_columns)
        if len(self._dollar_columns)>0:
            self._data_frame = CommonUtils.convert_dollar_columns(self._data_frame,self._dollar_columns)
            self._numeric_columns = self._numeric_columns + self._dollar_columns
            self._string_columns = list(set(self._string_columns)-set(self._dollar_columns))
            self.update_column_type_dict()

        if len(self._numeric_columns) > 1:
            # print "self._numeric_columns : ", self._numeric_columns
            metaData.append(MetaData(name="measures",value=len(self._numeric_columns),display=True,displayName="Measures"))
        else:
            metaData.append(MetaData(name="measures",value=len(self._numeric_columns),display=True,displayName="Measure"))
        if len(self._string_columns) > 1:
            metaData.append(MetaData(name="dimensions",value=len(self._string_columns+self._boolean_columns),display=True,displayName="Dimensions"))
        else:
            metaData.append(MetaData(name="dimensions",value=len(self._string_columns+self._boolean_columns),display=True,displayName="Dimension"))
        if len(self._timestamp_columns) > 1:
            metaData.append(MetaData(name="timeDimension",value=len(self._timestamp_columns),display=True,displayName="Time Dimensions"))
        else:
            metaData.append(MetaData(name="timeDimension",value=len(self._timestamp_columns),display=True,displayName="Time Dimension"))

        metaData.append(MetaData(name="measureColumns",value = self._numeric_columns,display=False))
        metaData.append(MetaData(name="dimensionColumns",value = self._string_columns+self._boolean_columns,display=False))
        metaData.append(MetaData(name="timeDimensionColumns",value = self._timestamp_columns,display=False))
        metaData.append(MetaData(name="percentageColumns",value = self._percentage_columns,display=False))
        metaData.append(MetaData(name="dollarColumns",value = self._dollar_columns,display=False))
        columnData = []
        headers = []

        self._start_time = time.time()
        print "Count of Numeric columns",len(self._numeric_columns)
        measureColumnStat,measureCharts = metaHelperInstance.calculate_measure_column_stats(self._data_frame,self._numeric_columns,binColumn=self._binned_stat_flag)
        time_taken_measurestats = time.time()-self._start_time
        self._completionStatus += self._scriptStages["measurestats"]["weight"]
        print "measure stats takes",time_taken_measurestats
        progressMessage = CommonUtils.create_progress_message_object(self._analysisName,\
                                    "measurestats",\
                                    "info",\
                                    self._scriptStages["measurestats"]["summary"],\
                                    self._completionStatus,\
                                    self._completionStatus)
        CommonUtils.save_progress_message(self._messageURL,progressMessage,ignore=self._ignoreMsgFlag)

        self._start_time = time.time()
        dimensionColumnStat,dimensionCharts = metaHelperInstance.calculate_dimension_column_stats(self._data_frame,self._string_columns+self._boolean_columns,levelCount=self._level_count_flag)
        # print dimensionColumnStat
        self._dataSize["dimensionLevelCountDict"] = {k:filter(lambda x:x["name"]=="numberOfUniqueValues",v)[0]["value"] for k,v in dimensionColumnStat.items()}
        self._dataSize["totalLevels"] = sum(self._dataSize["dimensionLevelCountDict"].values())

        time_taken_dimensionstats = time.time()-self._start_time
        self._completionStatus += self._scriptStages["dimensionstats"]["weight"]
        # print "dimension stats takes",time_taken_dimensionstats
        progressMessage = CommonUtils.create_progress_message_object(self._analysisName,\
                                    "dimensionstats",\
                                    "info",\
                                    self._scriptStages["dimensionstats"]["summary"],\
                                    self._completionStatus,\
                                    self._completionStatus)
        CommonUtils.save_progress_message(self._messageURL,progressMessage,ignore=self._ignoreMsgFlag)

        self._start_time = time.time()
        timeDimensionColumnStat,timeDimensionCharts = metaHelperInstance.calculate_time_dimension_column_stats(self._data_frame,self._timestamp_columns,level_count_flag=self._level_count_flag)
        time_taken_tdstats = time.time()-self._start_time
        self._completionStatus += self._scriptStages["timedimensionstats"]["weight"]
        # print "time dimension stats takes",time_taken_tdstats
        progressMessage = CommonUtils.create_progress_message_object(self._analysisName,\
                                    "timedimensionstats",\
                                    "info",\
                                    self._scriptStages["timedimensionstats"]["summary"],\
                                    self._completionStatus,\
                                    self._completionStatus)
        CommonUtils.save_progress_message(self._messageURL,progressMessage,ignore=self._ignoreMsgFlag)

        self._start_time = time.time()
        ignoreColumnSuggestions = []
        ignoreColumnReason = []
        utf8ColumnSuggestion = []
        dateTimeSuggestions = {}
        for column in self._data_frame.columns:
            random_slug = uuid.uuid4().hex
            headers.append(ColumnHeader(name=column,slug=random_slug))
            data = ColumnData()
            data.set_slug(random_slug)
            data.set_name(column)
            data.set_abstract_datatype(self._column_type_dict[column]["abstract"])

            columnStat = []
            columnChartData = None
            if self._column_type_dict[column]["abstract"] == "measure":
                data.set_column_stats(measureColumnStat[column])
                data.set_column_chart(measureCharts[column])
                data.set_actual_datatype(self._column_type_dict[column]["actual"])
            elif self._column_type_dict[column]["abstract"] == "dimension":
                data.set_column_stats(dimensionColumnStat[column])
                data.set_column_chart(dimensionCharts[column])
                data.set_actual_datatype(self._column_type_dict[column]["actual"])
            elif self._column_type_dict[column]["abstract"] == "datetime":
                data.set_column_stats(timeDimensionColumnStat[column])
                data.set_column_chart(timeDimensionCharts[column])
                data.set_actual_datatype(self._column_type_dict[column]["actual"])


            if self._column_type_dict[column]["abstract"] == "measure":
                if column not in self._real_columns:
                    ignoreSuggestion,ignoreReason = metaHelperInstance.get_ignore_column_suggestions(self._data_frame,column,"measure",measureColumnStat[column],max_levels=self._max_levels)
                    if ignoreSuggestion:
                        ignoreColumnSuggestions.append(column)
                        ignoreColumnReason.append(ignoreReason)
                        data.set_level_count_to_null()
                        data.set_chart_data_to_null()
                        data.set_ignore_suggestion_flag(True)
                        data.set_ignore_suggestion_message(ignoreReason)

            elif self._column_type_dict[column]["abstract"] == "dimension":
                if self._level_count_flag:
                    utf8Suggestion = metaHelperInstance.get_utf8_suggestions(dimensionColumnStat[column])
                else:
                    utf8Suggestion = False
                if self._column_type_dict[column]["actual"] != "boolean":
                    uniqueVals = self._data_frame.select(column).distinct().na.drop().collect()
                else:
                    uniqueVals = []
                if len(uniqueVals) > 0:
                    dateColumnFormat = metaHelperInstance.get_datetime_format(uniqueVals)
                else:
                    dateColumnFormat = None
                if dateColumnFormat:
                    dateTimeSuggestions.update({column:dateColumnFormat})
                    data.set_level_count_to_null()
                    data.set_chart_data_to_null()
                    data.set_date_suggestion_flag(True)

                if utf8Suggestion:
                    utf8ColumnSuggestion.append(column)
                ignoreSuggestion,ignoreReason = metaHelperInstance.get_ignore_column_suggestions(self._data_frame,column,"dimension",dimensionColumnStat[column],max_levels=self._max_levels)
                if ignoreSuggestion:
                    ignoreColumnSuggestions.append(column)
                    ignoreColumnReason.append(ignoreReason)
                    data.set_level_count_to_null()
                    data.set_chart_data_to_null()
                    data.set_ignore_suggestion_flag(True)
                    data.set_ignore_suggestion_message(ignoreReason)

            columnData.append(data)
        for dateColumn in dateTimeSuggestions.keys():
            if dateColumn in ignoreColumnSuggestions:
                ignoreColIdx = ignoreColumnSuggestions.index(dateColumn)
                ignoreColumnSuggestions.remove(dateColumn)
                del(ignoreColumnReason[ignoreColIdx])
        for utfCol in utf8ColumnSuggestion:
            ignoreColumnSuggestions.append(utfCol)
            ignoreColumnReason.append("utf8 values present")
        progressMessage = CommonUtils.create_progress_message_object(self._analysisName,"custom","info","Validating Metadata Information",self._completionStatus,self._completionStatus,display=True)
        CommonUtils.save_progress_message(self._messageURL,progressMessage,ignore=self._ignoreMsgFlag)
        metaData.append(MetaData(name="ignoreColumnSuggestions",value = ignoreColumnSuggestions,display=False))
        metaData.append(MetaData(name="ignoreColumnReason",value = ignoreColumnReason,display=False))
        metaData.append(MetaData(name="utf8ColumnSuggestion",value = utf8ColumnSuggestion,display=False))
        metaData.append(MetaData(name="dateTimeSuggestions",value = dateTimeSuggestions,display=False))
        metaData.append(MetaData(name="dataSizeSummary",value = self._dataSize,display=False))
        dfMetaData = DfMetaData()
        dfMetaData.set_column_data(columnData)
        dfMetaData.set_header(headers)
        dfMetaData.set_meta_data(metaData)
        dfMetaData.set_sample_data(sampleData)

        time_taken_suggestions = time.time()-self._start_time
        self._completionStatus += self._scriptStages["suggestions"]["weight"]
        # print "suggestions take",time_taken_suggestions
        progressMessage = CommonUtils.create_progress_message_object(self._analysisName,\
                                    "suggestions",\
                                    "info",\
                                    self._scriptStages["suggestions"]["summary"],\
                                    self._completionStatus,\
                                    self._completionStatus)
        CommonUtils.save_progress_message(self._messageURL,progressMessage,ignore=self._ignoreMsgFlag)
        self._dataframe_context.update_completion_status(self._completionStatus)
        return dfMetaData
