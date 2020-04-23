import json
import math
import numpy as np
import pandas as pd

from datetime import datetime

from bi.narratives import utils as NarrativesUtils

from pyspark.sql.types import *
from pyspark.ml.feature import Bucketizer
import pyspark.sql.functions as FN




class TimeSeriesCalculations:
    def __init__(self, df_helper, df_context, result_setter, spark):
        self._result_setter = result_setter
        self._dataframe_helper = df_helper
        self._data_frame = df_helper.get_data_frame()
        self._spark = spark
        self._dataframe_context = df_context

        self._num_significant_digits = NarrativesUtils.get_significant_digit_settings("trend")
        self._dateFormatDetected = False
        self._date_columns = df_context.get_date_columns()
        self._dateFormatConversionDict = NarrativesUtils.date_formats_mapping_dict()
        self._td_columns = df_helper.get_timestamp_columns()
        self._result_column = df_context.get_result_column()

        if self._date_columns != None:
            time_dimension_column = self._date_columns[0]
            existingDateFormat = None
            dateColumnFormatDict =  df_helper.get_datetime_format(time_dimension_column)
            if time_dimension_column in dateColumnFormatDict:
                existingDateFormat = dateColumnFormatDict[time_dimension_column]
                self._dateFormatDetected = True
            if df_context.get_requested_date_format() != None:
                requestedDateFormat = df_context.get_requested_date_format()[0]
            else:
                requestedDateFormat = None
            if requestedDateFormat != None:
                requestedDateFormat = self._dateFormatConversionDict[requestedDateFormat]
            else:
                requestedDateFormat = existingDateFormat

        self._requestedDateFormat = requestedDateFormat
        self._existingDateFormat = existingDateFormat
        self._date_column_suggested = time_dimension_column
        self._base_dir = "/chisquare/"



    def chisquare_trend(self,column_name,base_dir):
        if self._date_columns != None:
            if self._dateFormatDetected:
                output = []
                date_column = self._date_column_suggested
                chisquare_column = column_name
                result_column = self._result_column
                if chisquare_column in self._dataframe_helper.get_numeric_columns():
                    min_max = self._data_frame.select([FN.min(chisquare_column), FN.max(chisquare_column)]).collect()
                    maxval = min_max[0][1]
                    minval = min_max[0][0]
                    step = (maxval - minval) / 5.0
                    splits = [math.floor(minval), minval + step, minval + (step * 2), minval + (step * 3), minval + (step * 4), math.ceil(maxval)]
                    bucketizer = Bucketizer(splits=splits,inputCol=chisquare_column,outputCol="BINNED_COL")
                    self._data_frame = self._data_frame.withColumn(chisquare_column, self._data_frame[chisquare_column].cast(DoubleType()))
                    bucketedData = bucketizer.transform(self._data_frame)
                    df = bucketedData.select([col for col in bucketedData.columns if col != chisquare_column])
                    df = df.withColumnRenamed("BINNED_COL",chisquare_column)
                    ranges = []
                    for idx in range(len(splits)-1):
                        text = str(splits[idx])+" to "+str(splits[idx+1])
                        ranges.append(text)
                    bin_dict = dict(zip(range(len(ranges)),ranges))
                else:
                    df = self._data_frame

                df = df.select([date_column,chisquare_column,result_column]).toPandas()
                df["suggestedDate"] = df[date_column].apply(lambda x: datetime.strptime(x,self._existingDateFormat))
                df["year_month"] = df["suggestedDate"].apply(lambda x:x.strftime("%b-%y"))
                # result_column_count_df = df.groupBy(self._result_column).count().orderBy("count",ascending=False)
                # grouped_data.sort_values(by='key', ascending=True)
                result_column_count = df[result_column].value_counts()
                top2levels = result_column_count[:2].index
                for level in top2levels:
                    filtered_df = df.loc[df[result_column] == level]
                    grouped_result = pd.DataFrame(filtered_df[date_column].value_counts()).reset_index()
                    grouped_result.columns=[date_column,"value"]
                    # grouped_result["suggestedDate"] = grouped_result[date_column].apply(lambda x: datetime.strptime(x,self._existingDateFormat))
                    grouped_result["year_month"] = grouped_result[date_column].apply(lambda x: datetime.strptime(x,self._existingDateFormat).strftime("%b-%y"))
                    crosstab_df = pd.DataFrame(pd.crosstab(filtered_df["suggestedDate"],filtered_df[chisquare_column])).reset_index()
                    if chisquare_column in self._dataframe_helper.get_numeric_columns():
                        crosstab_columns = crosstab_df.columns
                        chisquare_levels = crosstab_columns[1:]
                        chisquare_levels = map(lambda x:bin_dict[x],chisquare_levels)
                        crosstab_df.columns = [crosstab_columns[0]]+chisquare_levels
                    else:
                        chisquare_levels = crosstab_df.columns[1:]


                    crosstab_df["year_month"] = crosstab_df["suggestedDate"].apply(lambda x:x.strftime("%b-%y"))
                    final_df = pd.merge(grouped_result,crosstab_df, how='outer', on=['year_month'])
                    final_df.sort_values(by="suggestedDate",ascending=True,inplace=True)
                    final_df.reset_index(drop=True,inplace=True)
                    final_df["overallPerChange"] = [0]+[round((x-y)*100/float(y),self._num_significant_digits) for x,y in zip(final_df["value"].iloc[1:],final_df["value"])]

                    growth_dict = {}
                    for val in chisquare_levels:
                        growth_dict[val]  = {}
                        growth_dict[val]["growth"] = round(((final_df[val].iloc[-1]-final_df[val].iloc[0])*100/float(final_df[val].iloc[0])),self._num_significant_digits)
                        if growth_dict[val]["growth"] > 3 or final_df[val].iloc[0] == 0:
                            growth_dict[val]["growthType"] = "positive"
                            print growth_dict[val]["growth"]
                        elif growth_dict[val]["growth"] < -3:
                            growth_dict[val]["growthType"] = "negative"
                        else:
                            growth_dict[val]["growthType"] = "stable"
                        growth_dict[val]["total"] = sum(final_df[val])
                    growth_dict["overall"] = {}
                    growth_dict["overall"]["growth"] = round((final_df["value"].iloc[-1]-final_df["value"].iloc[0]/float(final_df["value"].iloc[0])),self._num_significant_digits)
                    data_dict = {}
                    total_tuple = []
                    for k,v in growth_dict.items():
                        if k != "overall":
                            total_tuple.append((k,v["total"]))
                    sorted_total_tuple = sorted(total_tuple,key=lambda x:x[1],reverse=True)
                    top_dimension = sorted_total_tuple[0][0]
                    final_df["topDimensionPerChange"] = [0]+[round((x-y)*100/float(y),self._num_significant_digits) for x,y in zip(final_df[top_dimension].iloc[1:],final_df[top_dimension])]
                    data_dict["dimension"] = chisquare_column
                    data_dict["correlation"] = final_df["value"].corr(final_df[top_dimension])
                    data_dict["subset_increase_percent"] = growth_dict[top_dimension]["growth"]
                    data_dict["overall_increase_percent"] = growth_dict["overall"]["growth"]
                    data_dict["target"] = level
                    data_dict["top_dimension"] = top_dimension
                    overall_peak_index = np.argmax(final_df["value"])
                    overall_low_index = np.argmin(final_df["value"])
                    top_dimension_peak_index = np.argmax(final_df[top_dimension])
                    top_dimension_low_index = np.argmin(final_df[top_dimension])
                    data_dict["overallPeakValue"] = final_df["value"][overall_peak_index]
                    data_dict["overallLowestValue"] = final_df["value"][overall_low_index]
                    data_dict["overallPeakTime"] = final_df["year_month"][overall_peak_index]
                    data_dict["overallLowestTime"] = final_df["year_month"][overall_low_index]
                    data_dict["overallPeakIncrease"] = final_df["overallPerChange"][overall_peak_index]
                    data_dict["topDimensionPeakValue"] = final_df[top_dimension][top_dimension_peak_index]
                    data_dict["topDimensionLowestValue"] = final_df[top_dimension][top_dimension_low_index]
                    data_dict["topDimensionPeakTime"] = final_df["year_month"][top_dimension_peak_index]
                    data_dict["topDimensionLowestTime"] = final_df["year_month"][top_dimension_low_index]
                    data_dict["topDimensionPeakIncrease"] = final_df["topDimensionPerChange"][top_dimension_peak_index]
                    data_dict["overall_streak"] = NarrativesUtils.streak_data(final_df,overall_peak_index,overall_low_index,\
                                                    "overallPerChange","value")
                    data_dict["top_dimension_streak"] = NarrativesUtils.streak_data(final_df,top_dimension_peak_index,top_dimension_low_index,\
                                                    "topDimensionPerChange",top_dimension)
                    # print growth_dict
                    data_dict["num_positive_growth_dimensions"] = 0
                    data_dict["positive_growth_dimensions"] = []
                    data_dict["positive_growth_values"] = []
                    data_dict["num_negative_growth_dimensions"] = 0
                    data_dict["negative_growth_dimensions"] = []
                    data_dict["negative_growth_values"] = []
                    data_dict["num_stable_growth_dimensions"] = 0
                    data_dict["stable_growth_dimensions"] = []
                    data_dict["stable_growth_values"] = []
                    data_dict["overall_growth_rate"] = growth_dict["overall"]["growth"]
                    data_dict["total_levels"] = len(chisquare_levels)
                    for val in chisquare_levels:
                        if growth_dict[val]["growthType"] == "positive":
                            data_dict["num_positive_growth_dimensions"] += 1
                            data_dict["positive_growth_dimensions"].append(val)
                            data_dict["positive_growth_values"].append(growth_dict[val]["growth"])
                        elif growth_dict[val]["growthType"] == "negative":
                            data_dict["num_negative_growth_dimensions"] += 1
                            data_dict["negative_growth_dimensions"].append(val)
                            data_dict["negative_growth_values"].append(growth_dict[val]["growth"])
                        else:
                            data_dict["num_stable_growth_dimensions"] += 1
                            data_dict["stable_growth_dimensions"].append(val)
                            data_dict["stable_growth_values"].append(growth_dict[val]["growth"])
                    summary1 = NarrativesUtils.get_template_output(self._base_dir,\
                                                                    'chisquare_trend.html',data_dict)
                    chart_data = {"data":[],"header":[]}
                    chart_data["header"] = ["time",result_column,top_dimension]
                    chart_data["data"]=[["time"],[result_column],[top_dimension]]
                    for idx in range(final_df.shape[0]):
                        chart_data["data"][0].append(final_df["year_month"].iloc[idx])
                        chart_data["data"][1].append(final_df["value"].iloc[idx])
                        chart_data["data"][2].append(final_df[top_dimension].iloc[idx])

                    paragraphs = NarrativesUtils.paragraph_splitter(summary1)
                    card_data = {"paragraphs":paragraphs,"chart":chart_data}
                    output.append([card_data])
                print json.dumps(output,indent=2)
