import time
from datetime import datetime

from bi.algorithms import TimeSeriesAnalysis
# from nltk import tokenize
from bi.narratives import utils as NarrativesUtils


class TrendNarrative:

    def __init__(self, measure_column, time_dimension_column, grouped_data, existingDateFormat,requestedDateFormat,base_dir, meta_parser):
        self._measure_column = measure_column
        self._td_column = time_dimension_column
        self._grouped_data = grouped_data
        self._requestedDateFormat = requestedDateFormat

        self._heading = 'Trend Analysis'
        self._sub_heading = 'Analysis by Measure'
        self.output_column_sample = None
        self.summary = None
        self.key_takeaway = None
        self.narratives = {}
        self._num_significant_digits = NarrativesUtils.get_significant_digit_settings("trend")

        self._base_dir = base_dir+"/templates/trend/"

        self.month_dict = {1:"Jan",2:"Feb",3:"Mar",4:"Apr",5:"May",6:"Jun",7:"Jul",8:"Aug",9:"Sep",10:"Oct",11:"Nov",12:"Dec"}
        self._metaParser = meta_parser


    def formatDateColumn(self,df,requestedDateFormat):
        df_copy = df
        date_series = df_copy["key"]
        date_series = date_series.apply(lambda x: datetime.strptime(x ,requestedDateFormat).date())
        df_copy["key"] = date_series
        return df_copy

    def generateDataDict(self,df,dataLevel,durationString):
        ## if timestam comes into play then
        if type(df["key"][0]) == "str":
            df["key"] = df["key"].apply(lambda x:datetime.strptime(x,"%Y-%M-%d" ).date())
        df = df.sort_values(by = "key",ascending=True)
        df.reset_index(drop=True,inplace=True)
        dataDict = {"trend_present":True}
        dataDict["dataLevel"] = dataLevel
        dataDict["durationString"] = durationString
        # df["perChange"] = [round((y-x)*100/float(x),self._num_significant_digits) for x,y in zip(df["value"],df["value"].iloc[1:])]+[round((df["value"].iloc[-1]-df["value"].iloc[-2])*100/float(df["value"].iloc[-2]),self._num_significant_digits)]
        df["perChange"] = [0]+[round((x-y)*100/float(y),self._num_significant_digits) for x,y in zip(df["value"].iloc[1:],df["value"])]
        dataDict["measure"] = self._measure_column
        df["trendDirection"] = df["perChange"].apply(lambda x: "P" if x>=0 else "N")
        # print df
        trendString = "".join(df["trendDirection"])
        maxRuns = NarrativesUtils.longestRun(trendString)
        # list(set(zip([x.strftime('%m') for x in df["key"]],[x.strftime('%Y') for x in df["key"]])))
        dataDict["bubbleData"] = [{"value":"","text":""},{"value":"","text":""}]
        dataDict["overall_growth"] = round((df["value"].iloc[-1]-df["value"].iloc[0])*100/float(df["value"].iloc[0]),self._num_significant_digits)
        dataDict["bubbleData"][0]["value"] = str(abs(dataDict["overall_growth"]))+"%"
        if dataDict["overall_growth"] >= 0:
            dataDict["bubbleData"][0]["text"] = "Overall growth in %s over the last %s"%(self._measure_column ,dataDict["durationString"])
        else:
            dataDict["bubbleData"][0]["text"] = "Overall decline in %s over the last %s"%(self._measure_column ,dataDict["durationString"])

        max_growth_index = df["perChange"].argmax()
        dataDict["bubbleData"][1]["value"] = str(abs(round(list(df["perChange"])[max_growth_index],self._num_significant_digits)))+"%"
        if list(df["perChange"])[max_growth_index] >= 0:
            if dataDict["dataLevel"] == "day":
                dataDict["bubbleData"][1]["text"] = "Largest growth in %s happened in %s"%(self._measure_column ,list(df["key"])[max_growth_index])
            elif dataDict["dataLevel"] == "month":
                dataDict["bubbleData"][1]["text"] = "Largest growth in %s happened in %s"%(self._measure_column ,list(df["year_month"])[max_growth_index])
        else:
            if dataDict["dataLevel"] == "day":
                dataDict["bubbleData"][1]["text"] = "Largest decline in %s happened in %s"%(self._measure_column ,list(df["key"])[max_growth_index])
            elif dataDict["dataLevel"] == "month":
                dataDict["bubbleData"][1]["text"] = "Largest decline in %s happened in %s"%(self._measure_column ,list(df["year_month"])[max_growth_index])

        # print dataDict["bubbleData"]
        dataDict["start_value"] = round(df["value"].iloc[0],self._num_significant_digits)
        dataDict["end_value"] = round(df["value"].iloc[-1],self._num_significant_digits)
        dataDict["average_value"] = round(df["value"].mean(),self._num_significant_digits)
        dataDict["total"] = round(df["value"].sum(),self._num_significant_digits)

        peak_index = df["value"].argmax()
        low_index = df["value"].argmin()
        dataDict["peakIndex"] = peak_index
        dataDict["lowIndex"] = low_index
        dataDict["peakValue"] = df["value"][peak_index]
        dataDict["lowestValue"] = df["value"][low_index]
        if dataDict["dataLevel"] == "day":
            dataDict["start_time"] = str(df["key"].iloc[0])
            dataDict["end_time"] = str(df["key"].iloc[-1])
            dataDict["peakTime"] = df["key"][peak_index]
            dataDict["lowestTime"] = df["key"][low_index]
            dataDict["reference_time"] = dataDict["peakTime"]
        else:
            dataDict["start_time"] = df["year_month"].iloc[0]
            dataDict["end_time"] = df["year_month"].iloc[-1]
            dataDict["peakTime"] = df["year_month"][peak_index]
            dataDict["lowestTime"] = df["year_month"][low_index]
            dataDict["reference_time"] = dataDict["peakTime"]
        print "Overall Growth ",dataDict["overall_growth"]
        if dataDict["overall_growth"] < 0:
            dataDict["overall_growth_text"] = "negative growth"
        else:
            dataDict["overall_growth_text"] = "positive growth"

        k = peak_index
        while k != -1 and df["perChange"][k] >= 0:
            k = k-1
        l = low_index
        while l != -1 and df["perChange"][l] < 0:
            l = l-1
        if peak_index - k > 0:
            dataDict["peakStreakDuration"] = peak_index - k
        else:
            dataDict["peakStreakDuration"] = 0
        if low_index - l > 0:
            dataDict["lowStreakDuration"] = low_index - l
        else:
            dataDict["lowStreakDuration"] = 0
        if dataDict["lowStreakDuration"] >=2 :
            if dataDict["dataLevel"] == "day":
                dataDict["lowStreakBeginMonth"] = df["key"][l]
            elif dataDict["dataLevel"] == "month":
                dataDict["lowStreakBeginMonth"] = df["year_month"][l]
            dataDict["lowStreakBeginValue"] = df["value"][l]

        # table_data = {"increase":[],"decrease":[]}
        # percent_stats = NarrativesUtils.get_max_min_stats(df,dataDict["dataLevel"],trend = "positive", stat_type = "percentage")
        # ###############################
        # #####      TEMP FIX      ######
        # # dataDict["bubbleData"][1]["value"] = str(percent_stats['increased_by'])
        # # dataDict["bubbleData"][1]["text"] = "Largest growth in %s happened in %s"%(self._measure_column ,percent_stats['period'])
        # ###############################
        # abs_stats = NarrativesUtils.get_max_min_stats(df,dataDict["dataLevel"],trend = "positive", stat_type = "absolute")
        # streak = NarrativesUtils.get_streak_data(df,trendString,maxRuns,"positive",dataDict["dataLevel"])
        # table_data["increase"].append(percent_stats)
        # table_data["increase"].append(abs_stats)
        # table_data["increase"].append(streak)
        #
        # percent_stats = NarrativesUtils.get_max_min_stats(df,dataDict["dataLevel"],trend = "negative", stat_type = "percentage")
        # abs_stats = NarrativesUtils.get_max_min_stats(df,dataDict["dataLevel"],trend = "negative", stat_type = "absolute")
        # streak = NarrativesUtils.get_streak_data(df,trendString,maxRuns,"negative",dataDict["dataLevel"])
        # table_data["decrease"].append(percent_stats)
        # table_data["decrease"].append(abs_stats)
        # table_data["decrease"].append(streak)
        #
        # dataDict["table_data"] = table_data
        return dataDict

    def get_xtra_calculations(self,sparkdf,grouped_data,significant_columns,index_col,value_col,dateColDateFormat,reference_time,dataLevel):
        print "dateColDateFormat",dateColDateFormat
        if type(grouped_data["key"][0]) == "str":
            grouped_data["key"] = grouped_data["key"].apply(lambda x:datetime.strptime(x,"%Y-%M-%d" ).date())
        grouped_data = grouped_data.sort_values(by = "key",ascending=True)
        grouped_data.reset_index(drop=True,inplace=True)
        print "level contribution started"
        st = time.time()
        print "significant_columns",significant_columns
        if dataLevel == "day":
            index_col = "suggestedDate"
        else:
            index_col = "year_month"
            dateColDateFormat = "%b-%y"
        level_cont = NarrativesUtils.calculate_level_contribution(sparkdf,significant_columns,index_col,dateColDateFormat,value_col,reference_time, self._metaParser)
        print "level_cont finished in ",time.time()-st
        level_cont_dict = NarrativesUtils.get_level_cont_dict(level_cont)
        bucket_dict = NarrativesUtils.calculate_bucket_data(grouped_data,dataLevel)
        bucket_data = NarrativesUtils.get_bucket_data_dict(bucket_dict)
        dim_data = NarrativesUtils.calculate_dimension_contribution(level_cont)
        if level_cont_dict != None:
            if bucket_data != None:
                level_cont_dict.update(bucket_data)
            if dim_data != None:
                level_cont_dict.update(dim_data)

        return level_cont_dict

    def get_forecast_values(self,series,prediction_window):
        if len(series) > 12:
            slen = 12
        else:
            slen = 1
        alpha, beta, gamma = 0.716, 0.029, 0.993
        time_series_object = TimeSeriesAnalysis()
        prediction = time_series_object.triple_exponential_smoothing(series, slen, alpha, beta, gamma, prediction_window)
        return prediction

    def generate_sub_heading(self,measure_column):
        sub_heading = "This section provides insights on how %s is performing over time and captures the most significant moments that defined the overall pattern or trend over the observation period." %(measure_column)
        return sub_heading

    def generate_summary(self,dataDict):
        output = NarrativesUtils.get_template_output(self._base_dir,\
                                                        'trend_summary.html',data_dict)
        return output

    def generate_dimension_extra_narrative(self,df,dataDict,dataLevel):
        if type(df["key"][0]) == "str":
            df["key"] = df["key"].apply(lambda x:datetime.strptime(x,"%Y-%M-%d" ).date())
        df = df.sort_values(by = "key",ascending=True)
        outDict = {}
        outDict["total_count"] = int(df["value_count"].sum())
        bucket_end = dataDict["bucket_end"]
        bucket_start = dataDict["bucket_start"]
        if dataLevel == "month":
            bucket_start_index = list(df["year_month"]).index(dataDict["bucket_start"])
            bucket_end_index = list(df["year_month"]).index(dataDict["bucket_end"])
            max_index = list(df["year_month"]).index(dataDict["peakTime"])
        elif dataLevel == "day":
            bucket_start_index = list(df["key"]).index(dataDict["bucket_start"])
            bucket_end_index = list(df["key"]).index(dataDict["bucket_end"])
            max_index = list(df["key"]).index(dataDict["peakTime"])
        outDict["bucket_count"] = int(df["value_count"].iloc[bucket_start_index:bucket_end_index].sum())
        outDict["max_count"] = int(df["value_count"][max_index])
        ratio = round(outDict["bucket_count"]*100/float(outDict["total_count"]),self._num_significant_digits)
        if ratio < 20:
            outDict["bucket_ratio_string"] = ""
        elif ratio > 20 and ratio <=30:
            outDict["bucket_ratio_string"] = "one fourth"
        elif ratio > 30 and ratio <=40:
            outDict["bucket_ratio_string"] = "one third"
        elif ratio > 40 and ratio <=55:
            outDict["bucket_ratio_string"] = "half"
        elif ratio > 55 and ratio <=70:
            outDict["bucket_ratio_string"] = "two third"
        elif ratio >70 and ratio <=80:
            outDict["bucket_ratio_string"] = "three fourth"
        else:
            outDict["bucket_ratio_string"] = str(ratio)
        return outDict

    def generate_regression_trend_data(self,agg_data,measure_column,result_column,dataLevel,durationString):
        if type(agg_data["key"][0]) == "str":
            agg_data["key"] = agg_data["key"].apply(lambda x:datetime.strptime(x,"%Y-%M-%d" ).date())
        agg_data = agg_data.sort_values(by = "key",ascending=True)
        date_column = agg_data.columns[0]
        data_dict = {}
        data_dict["dataLevel"] = dataLevel
        data_dict["durationString"] = durationString
        data_dict['target'] = result_column
        data_dict['measure'] = measure_column
        data_dict['total_measure'] = int(agg_data[measure_column].sum())
        data_dict['total_target'] = int(agg_data[result_column].sum())
        data_dict['fold'] = round(data_dict['total_measure']*100/data_dict['total_target'] - 100.0, self._num_significant_digits)
        data_dict['num_dates'] = len(agg_data.index)

        peak_index = agg_data[measure_column].argmax()
        lowest_index = agg_data[measure_column].argmin()
        if data_dict["dataLevel"] == "day":
            data_dict['start_date'] = agg_data["key"].iloc[0]
            data_dict['end_date'] = agg_data["key"].iloc[-1]
            data_dict['lowest_date'] = agg_data["key"].ix[lowest_index]
            data_dict['peak_date'] = agg_data["key"].ix[peak_index]

        elif data_dict["dataLevel"] == "month":
            data_dict['start_date'] = agg_data["year_month"].iloc[0]
            data_dict['end_date'] = agg_data["year_month"].iloc[-1]
            data_dict['lowest_date'] = agg_data["year_month"].ix[lowest_index]
            data_dict['peak_date'] = agg_data["year_month"].ix[peak_index]

        data_dict['start_value'] = round(agg_data[measure_column].iloc[0],self._num_significant_digits)
        data_dict['end_value'] = round(agg_data[measure_column].iloc[-1],self._num_significant_digits)
        # data_dict['target_start_value'] = agg_data[result_column].iloc[0]
        # data_dict['target_end_value'] = agg_data[result_column].iloc[-1]
        data_dict['change_percent'] = NarrativesUtils.round_number(agg_data[measure_column].iloc[-1]*100/agg_data[measure_column].iloc[0] - 100,2)
        data_dict['correlation'] = NarrativesUtils.round_number(agg_data[measure_column].corr(agg_data[result_column]),2)

        data_dict['peak_value'] = NarrativesUtils.round_number(agg_data[measure_column].ix[peak_index],2)
        data_dict['lowest_value'] = NarrativesUtils.round_number(agg_data[measure_column].ix[lowest_index],2)
        return data_dict

    def generate_regression_trend_chart(self, agg_data,dataLevel):
        if type(agg_data["key"][0]) == "str":
            agg_data["key"] = agg_data["key"].apply(lambda x:datetime.strptime(x,"%Y-%M-%d" ).date())
        agg_data = agg_data.sort_values(by = "key",ascending=True)
        relevant_columns = list(set(agg_data.columns) - {"key", "year_month"})
        chart_data = dict(zip(relevant_columns,[[]]*len(relevant_columns)))
        label = {"y":"","y2":""}
        label["y"] = relevant_columns[0]
        label["y2"] = relevant_columns[1]
        label_text = {"y":relevant_columns[0],"y2":relevant_columns[1],"x":"Time Duration"}
        for col in relevant_columns:
            trend_chart_data = agg_data[["key",col]].T.to_dict().values()
            trend_chart_data = sorted(trend_chart_data,key=lambda x:x["key"])
            if dataLevel == "day":
                trend_chart_data = [{"key":str(val["key"]),"value":round(val[col],2)} for val in trend_chart_data]
            elif dataLevel == "month":
                trend_chart_data = [{"key":val["key"].strftime("%b-%y"),"value":round(val[col],2)} for val in trend_chart_data]

            chart_data[col] = trend_chart_data
        output = {"chart":None}
        output["chart"] = {"label":label,"data":chart_data,"label_text":label_text,"format":"%b-%y"}
        return output
