import time

from pyspark.sql.functions import col

from bi.common import utils as CommonUtils


#import bi.common.dataframe

class DataFrameFilterer:
    # @accepts(object,DataFrame,DataFrameHelper,ContextSetter)
    def __init__(self, dataframe, df_helper, df_context):
        self._data_frame = dataframe
        self._dataframe_helper = df_helper
        self._dataframe_context = df_context

        self._completionStatus = 0
        self._start_time = time.time()
        self._analysisName = "subsetting"
        self._messageURL = self._dataframe_context.get_message_url()
        self._scriptStages = {
            "initialization":{
                "summary":"initialized the filter parameters",
                "weight":3
                },
            "dimensionfilters":{
                "summary":"dimensionfilters is Run",
                "weight":3
                },
            "measurefilters":{
                "summary":"measurefilters is run",
                "weight":6
                },
            "datetimefilters":{
                "summary":"Datetimefilter is run",
                "weight":3
                }
            }

    def applyFilter(self):
        """
        here all the filter settings will come from the df_context
        """
        dimension_filters = self._dataframe_context.get_dimension_filters()
        measure_filters = self._dataframe_context.get_measure_filters()
        time_dimension_filters = self._dataframe_context.get_time_dimension_filters()

        self._completionStatus += self._scriptStages["initialization"]["weight"]
        progressMessage = CommonUtils.create_progress_message_object(self._analysisName,\
                                    "initialization",\
                                    "info",\
                                    self._scriptStages["initialization"]["summary"],\
                                    self._completionStatus,\
                                    self._completionStatus)
        CommonUtils.save_progress_message(self._messageURL,progressMessage)


        if len(dimension_filters) > 0:
            for filter_dict in dimension_filters:
                if filter_dict["filterType"] == "valueIn":
                    self.values_in(filter_dict["colname"],filter_dict["values"])

        time_taken_dimensionfilters = time.time()-self._start_time
        self._completionStatus += self._scriptStages["dimensionfilters"]["weight"]
        print "dimensionfilters takes",time_taken_dimensionfilters
        progressMessage = CommonUtils.create_progress_message_object(self._analysisName,\
                                    "dimensionfilters",\
                                    "info",\
                                    self._scriptStages["dimensionfilters"]["summary"],\
                                    self._completionStatus,\
                                    self._completionStatus)
        CommonUtils.save_progress_message(self._messageURL,progressMessage)

        if len(measure_filters) > 0:
            for filter_dict in measure_filters:
                if filter_dict["filterType"] == "valueRange":
                    self.values_between(filter_dict["colname"],\
                                                           filter_dict["lowerBound"],\
                                                           filter_dict["upperBound"],\
                                                           greater_than_equal=1,\
                                                           less_than_equal =1)
        time_taken_measurefilters = time.time()-self._start_time
        self._completionStatus += self._scriptStages["measurefilters"]["weight"]
        print "measurefilters takes",time_taken_measurefilters
        progressMessage = CommonUtils.create_progress_message_object(self._analysisName,\
                                    "measurefilters",\
                                    "info",\
                                    self._scriptStages["measurefilters"]["summary"],\
                                    self._completionStatus,\
                                    self._completionStatus)
        CommonUtils.save_progress_message(self._messageURL,progressMessage)

        if len(time_dimension_filters) > 0:
            for filter_dict in time_dimension_filters:
                if filter_dict["filterType"] == "valueRange":
                    self.values_between(filter_dict["colname"],\
                                                           filter_dict["lowerBound"],\
                                                           filter_dict["upperBound"],\
                                                           greater_than_equal=1,\
                                                           less_than_equal =1)
        time_taken_datetimefilters = time.time()-self._start_time
        self._completionStatus += self._scriptStages["datetimefilters"]["weight"]
        print "datetimefilters takes",time_taken_datetimefilters
        progressMessage = CommonUtils.create_progress_message_object(self._analysisName,\
                                    "datetimefilters",\
                                    "info",\
                                    self._scriptStages["datetimefilters"]["summary"],\
                                    self._completionStatus,\
                                    self._completionStatus)
        CommonUtils.save_progress_message(self._messageURL,progressMessage)
        return self._data_frame

    def values_between(self,colname,start_value, end_value, greater_than_equal = 0, less_than_equal=1):
        if (greater_than_equal == 0) and (less_than_equal==1):
            self._data_frame = self._data_frame.filter(col(colname) > start_value).filter(col(colname) <= end_value)
        elif (greater_than_equal == 0) and (less_than_equal==0):
            self._data_frame = self._data_frame.filter(col(colname) > start_value).filter(col(colname) < end_value)
        elif (greater_than_equal == 1) and (less_than_equal==1):
            self._data_frame = self._data_frame.filter(col(colname) >= start_value).filter(col(colname) <= end_value)
        elif (greater_than_equal == 1) and (less_than_equal==0):
            self._data_frame = self._data_frame.filter(col(colname) >= start_value).filter(col(colname) < end_value)

    def dates_between(self,colname,start_value, end_value, greater_than_equal = 1, less_than_equal=1):
        if (greater_than_equal == 0) and (less_than_equal==1):
            self._data_frame = self._data_frame.filter(col(colname) > start_value and col(colname) <= end_value)
        elif (greater_than_equal == 0) and (less_than_equal==0):
            self._data_frame = self._data_frame.filter(col(colname) > start_value and col(colname) < end_value)
        elif (greater_than_equal == 1) and (less_than_equal==1):
            self._data_frame = self._data_frame.filter(col(colname) >= start_value and col(colname) <= end_value)
        elif (greater_than_equal == 1) and (less_than_equal==0):
            self._data_frame = self._data_frame.filter(col(colname) >= start_value and col(colname) < end_value)

    def values_above(self,colname, start_value, greater_than_equal=0):
        if greater_than_equal == 0:
            self._data_frame = self._data_frame.filter(col(colname) > start_value)
        elif greater_than_equal == 1:
            self._data_frame = self._data_frame.filter(col(colname) >= start_value)

    def values_below(self, colname, end_value, less_than_equal=1):
        if less_than_equal==0:
            self._data_frame = self._data_frame.filter(col(colname) < end_value)
        elif less_than_equal==1:
            self._data_frame = self._data_frame.filter(col(colname) <= end_value)

    def values_in(self, colname, values):
        self._data_frame = self._data_frame.where(col(colname).isin(values))

    def values_not_in(self, colname, values):
        self._data_frame = self._data_frame.where(col(colname).isin(values)==False)

    def get_aggregated_result(self, colname, target):
        return self._data_frame.select(colname).groupBy(colname).agg({'*': 'count'}).collect()

    def get_filtered_data_frame(self):
        return self._data_frame
