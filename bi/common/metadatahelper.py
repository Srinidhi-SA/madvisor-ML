import time
from datetime import datetime

import pandas as pd
from pyspark.ml.feature import Bucketizer
from pyspark.sql.functions import col
from pyspark.sql.functions import monotonically_increasing_id
from pyspark.sql.functions import regexp_extract
from pyspark.sql.types import DoubleType

from bi.common import utils as CommonUtils
from bi.common.cardStructure import C3ChartData
from bi.common.charts import ChartJson, NormalChartData
from bi.common.decorators import accepts
from bi.settings import setting as GLOBALSETTINGS


class MetaDataHelper():

    def __init__(self, df, rows):
        self.df = df
        self.rows = rows
        self._sample_data = self.set_sample_data()


    def get_binned_stat(self,df,colname,col_stat,n_split = 10):

        splits  = CommonUtils.frange(col_stat["min"],col_stat["max"],num_steps=n_split)
        splits = sorted(splits)
        splits_range = [(splits[idx],splits[idx+1]) for idx in range(len(splits)-1)]

        splits_data = {"splits":splits,"splits_range":splits_range}
        splits = splits_data["splits"]
        double_df = df.withColumn(colname, df[colname].cast(DoubleType()))
        bucketizer = Bucketizer(inputCol=colname,outputCol="BINNED_INDEX")
        bucketizer.setSplits(splits)
        binned_df = bucketizer.transform(double_df)
        histogram_df = binned_df.groupBy("BINNED_INDEX").count().toPandas()
        str_splits_range = [" to ".join([str(x[0]),str(x[1])]) for x in splits_range]
        bin_name_dict = dict(zip(range(len(splits_range)),str_splits_range))
        bin_name_dict[n_split] = "null"
        histogram_df["orderIndex"] = histogram_df["BINNED_INDEX"].apply(lambda x: n_split if pd.isnull(x) else x)
        histogram_df["bins"] = histogram_df["orderIndex"].apply(lambda x:bin_name_dict[int(x)])
        relevant_df = histogram_df[["bins","count","orderIndex"]]
        histogram_dict = relevant_df.T.to_dict().values()
        histogram_dict = sorted(histogram_dict,key=lambda x:x["orderIndex"])
        output = []
        for val in histogram_dict:
            output.append({"name":val["bins"],"value":val["count"]})
        return output

    def calculate_measure_column_stats(self,df,measure_columns,**kwargs):
        binned_stat_flag = True
        xtraArgs = {}
        for key in kwargs:
            xtraArgs[key] =  kwargs[key]
        if "binColumn" in xtraArgs:
            binned_stat_flag = xtraArgs["binColumn"]
        df = df.select(measure_columns)
        total_count = df.count()
        output = {}
        chart_data = {}
        summary_df = df.describe().toPandas()
        displayNameDict = {"count":"Count",
                            "mean":"Mean",
                            "stddev":"Standard Deviation",
                            "min":"Min",
                            "max":"Max",
                            "numberOfNulls":"Null Values",
                            "numberOfUniqueValues":"Unique Values",
                            "numberOfNotNulls":"Not Nulls",
                            "LevelCount":"Unique Values"
                            }
        displayOrderDict = {"min":0,"max":1,"mean":2,"stddev":3,"numberOfUniqueValues":4,"numberOfNulls":5,"numberOfNotNulls":6,"count":7,"LevelCount":8}

        for column in measure_columns:
            col_stat = dict(zip(summary_df["summary"],summary_df[column]))
            for k,v in col_stat.items():
                if "." in v:
                    col_stat[k] = round(float(v),2)
                elif v != "NaN":
                    col_stat[k] = int(v)
                else:
                    col_stat[k] = v
            col_stat["numberOfNulls"] = total_count - int(col_stat["count"])
            col_stat["numberOfNotNulls"] = col_stat["count"]
            col_stat["numberOfUniqueValues"] = df.select(column).distinct().count()
            if col_stat["numberOfUniqueValues"] <= GLOBALSETTINGS.UNIQUE_VALUES_COUNT_CUTOFF_CLASSIFICATION:
                fs1 = time.time()
                levelCount = df.groupBy(column).count().toPandas().set_index(column).to_dict().values()[0]
                levelCount = {str(k):v for k,v in levelCount.items()}
                print "time for measure levelCount "+column,time.time()-fs1,"Seconds"
                col_stat["LevelCount"] = levelCount
            if binned_stat_flag:
                st = time.time()
                measure_chart_data = self.get_binned_stat(df,column,col_stat)
                print "Binned Stat",time.time()-st
                measure_chart_data = sorted(measure_chart_data,key=lambda x:x["value"],reverse=True)
                measure_chart_obj = ChartJson(NormalChartData(measure_chart_data).get_data(),chart_type="bar")
                measure_chart_obj.set_axes({"x":"name","y":"value"})
                measure_chart_obj.set_subchart(False)
                measure_chart_obj.set_hide_xtick(True)
                measure_chart_obj.set_show_legend(False)
                chart_data[column] = C3ChartData(data=measure_chart_obj)
            else:
                chart_data[column] = {}
            modified_col_stat = []
            for k,v in col_stat.items():
                if k not in ["numberOfNotNulls","LevelCount"]:
                    modified_col_stat.append({"name":k,"value":v,"display":True,"displayName":displayNameDict[k]})
                else:
                    modified_col_stat.append({"name":k,"value":v,"display":False,"displayName":displayNameDict[k]})
            modified_col_stat = sorted(modified_col_stat,key=lambda x:displayOrderDict[x["name"]])
            output[column] = modified_col_stat
        return output,chart_data

    def calculate_dimension_column_stats(self,df,dimension_columns,**kwargs):
        level_count_flag = True
        xtraArgs = {}
        for key in kwargs:
            xtraArgs[key] =  kwargs[key]
        if "levelCount" in xtraArgs:
            level_count_flag = xtraArgs["levelCount"]
        df = df.select(dimension_columns)
        total_count = df.count()
        output = {}
        chart_data = {}
        summary_df = df.describe().toPandas()
        # print summary_df
        displayNameDict = {"count":"Count",
                            "mean":"Mean",
                            "stddev":"Standard Deviation",
                            "min":"Min",
                            "max":"Max",
                            "numberOfNulls":"Null Values",
                            "numberOfUniqueValues":"Unique Values",
                            "numberOfNotNulls":"Not Nulls",
                            "MaxLevel":"Max Level",
                            "MinLevel":"Min Level",
                            "LevelCount":"LevelCount"
                            }

        displayOrderDict = {"MinLevel": 0, "MaxLevel": 1, "numberOfUniqueValues": 2, "numberOfNulls": 3,
                            "numberOfUniqueValues": 4, "numberOfNotNulls": 5, "count": 6, "min": 7, "max": 8,
                            "stddev": 9, "mean": 10, "LevelCount": 11}
        for column in dimension_columns:
            st = time.time()
            col_stat = {}
            if level_count_flag:
                fs1 = time.time()
                levelCount = df.groupBy(column).count().toPandas().set_index(column).to_dict().values()[0]
                levelCount = {str(k):v for k,v in levelCount.items()}
                print "time for levelCount "+column,time.time()-fs1,"Seconds"
                col_stat["LevelCount"] = levelCount
                if None in levelCount.keys():
                    col_stat["numberOfNulls"] = levelCount[None]
                    col_stat["numberOfNotNulls"] = total_count - col_stat["numberOfNulls"]
                else:
                    col_stat["numberOfNulls"] = 0
                    col_stat["numberOfNotNulls"] = total_count - col_stat["numberOfNulls"]

                col_stat["numberOfUniqueValues"] = len(levelCount.keys())
                levelCountWithoutNull = levelCount
                dimension_chart_data = [{"name":k,"value":v} if k != None else {"name":"null","value":v} for k,v in levelCount.items()]
                dimension_chart_data = sorted(dimension_chart_data,key=lambda x:x["value"],reverse=True)
                dimension_chart_obj = ChartJson(NormalChartData(dimension_chart_data).get_data(),chart_type="bar")
                dimension_chart_obj.set_axes({"x":"name","y":"value"})
                dimension_chart_obj.set_subchart(False)
                dimension_chart_obj.set_hide_xtick(True)
                dimension_chart_obj.set_show_legend(False)
                chart_data[column] = C3ChartData(data=dimension_chart_obj)
                if None in levelCount:
                    levelCountWithoutNull.pop(None)
                if levelCountWithoutNull != {}:
                    col_stat["MaxLevel"] = max(levelCountWithoutNull,key=levelCount.get)
                    col_stat["MinLevel"] = min(levelCountWithoutNull,key=levelCount.get)
                else:
                    col_stat["MaxLevel"] = None
                    col_stat["MinLevel"] = None
            else:
                col_stat = dict(zip(summary_df["summary"],summary_df[column]))
                # print col_stat
                col_stat["numberOfNulls"] = total_count - int(col_stat["count"])
                col_stat["numberOfNotNulls"] = total_count - int(col_stat["count"])
                col_stat["numberOfUniqueValues"] = None
                col_stat["MaxLevel"] = col_stat["max"]
                col_stat["MinLevel"] = col_stat["min"]
                chart_data[column] = {}

            modified_col_stat = []
            for k,v in col_stat.items():
                if k not in ["LevelCount","min","max","mean","stddev","numberOfNotNulls"]:
                    modified_col_stat.append({"name":k,"value":v,"display":True,"displayName":displayNameDict[k]})
                else:
                    modified_col_stat.append({"name":k,"value":v,"display":False,"displayName":displayNameDict[k]})
            modified_col_stat = sorted(modified_col_stat,key=lambda x:displayOrderDict[x["name"]])
            output[column] = modified_col_stat
            print "dimension stats for column "+column,time.time()-st
        return output,chart_data


    def calculate_time_dimension_column_stats(self,df,td_columns,**kwargs):
        level_count_flag = True
        xtraArgs = {}
        for key in kwargs:
            xtraArgs[key] =  kwargs[key]
        if "level_count_flag" in xtraArgs:
            level_count_flag = xtraArgs[key]
        # print level_count_flag
        df = df.select(td_columns)
        total_count = df.count()
        output = {}
        chart_data = {}
        # summary_df = df.describe().toPandas()
        # print summary_df
        displayNameDict = {"count":"Count",
                            "mean":"Mean",
                            "stddev":"Standard Deviation",
                            "min":"Min",
                            "max":"Max",
                            "numberOfNulls":"Null Values",
                            "numberOfUniqueValues":"Unique Values",
                            "numberOfNotNulls":"Not Nulls",
                            "MaxLevel":"Max Level",
                            "MinLevel":"Min Level",
                            "LevelCount":"LevelCount",
                            "firstDate":"Start Date",
                            "lastDate":"Last Date",
                            }
        # TODO: FIX copy paste error numberOfUniqueValues
        displayOrderDict = {"firstDate": 0, "lastDate": 1, "MinLevel": 12, "MaxLevel": 13, "numberOfUniqueValues": 2,
                            "numberOfNulls": 3, "numberOfUniqueValues": 4, "numberOfNotNulls": 5, "count": 6, "min": 7,
                            "max": 8, "stddev": 9, "mean": 10, "LevelCount": 11}
        for column in td_columns:
            col_stat = {}
            notNullDf = df.select(column).distinct().na.drop()
            notNullDf = notNullDf.orderBy([column],ascending=[True])
            notNullDf = notNullDf.withColumn("_id_", monotonically_increasing_id())
            first_date = notNullDf.select(column).first()[0]
            first_date = str(pd.to_datetime(first_date).date())
            try:
                print "TRY BLOCK STARTED"
                last_date = notNullDf.where(col("_id_") == id_max).select(column).first()[0]
            except:
                print "ENTERING EXCEPT BLOCK"
                pandas_df = notNullDf.select(["_id_",column]).toPandas()
                pandas_df.sort_values(by=column,ascending=True,inplace=True)
                last_date = str(pandas_df[column].iloc[-1].date())
            col_stat["firstDate"] = first_date
            col_stat["lastDate"] = last_date
            # col_stat["count"] = df.select(column).distinct().na.drop().count()
            col_stat["count"] = notNullDf.count()
            if level_count_flag:
                # print "start level count"
                fs1 = time.time()
                tdLevelCount = df.groupBy(column).count().toPandas().set_index(column).to_dict().values()[0]
                levelCount = {}
                for k,v in tdLevelCount.items():
                    if k != None:
                        levelCount[str(pd.to_datetime(k).date())] = v
                    else:
                        levelCount[k] = v
                # print "time for levelCount ",time.time()-fs1,"Seconds"
                col_stat["LevelCount"] = levelCount
                if None in levelCount.keys():
                    col_stat["numberOfNulls"] = levelCount[None]
                    col_stat["numberOfNotNulls"] = total_count - col_stat["numberOfNulls"]
                else:
                    col_stat["numberOfNulls"] = 0
                    col_stat["numberOfNotNulls"] = total_count - col_stat["numberOfNulls"]

                col_stat["numberOfUniqueValues"] = len(levelCount.keys())
                levelCountWithoutNull = levelCount
                dimension_chart_data = [{"name":k,"value":v} if k != None else {"name":"null","value":v} for k,v in levelCount.items()]
                dimension_chart_data = sorted(dimension_chart_data,key=lambda x:x["value"],reverse=True)
                dimension_chart_obj = ChartJson(NormalChartData(dimension_chart_data).get_data(),chart_type="bar")
                dimension_chart_obj.set_axes({"x":"name","y":"value"})
                dimension_chart_obj.set_subchart(False)
                dimension_chart_obj.set_hide_xtick(True)
                dimension_chart_obj.set_show_legend(False)
                chart_data[column] = C3ChartData(data=dimension_chart_obj)
                if None in levelCount:
                    levelCountWithoutNull.pop(None)
                if levelCountWithoutNull != {}:
                    col_stat["MaxLevel"] = max(levelCountWithoutNull,key=levelCount.get)
                    col_stat["MinLevel"] = min(levelCountWithoutNull,key=levelCount.get)
                else:
                    col_stat["MaxLevel"] = None
                    col_stat["MinLevel"] = None
            else:
                col_stat["firstDate"] = first_date
                col_stat["lastDate"] = last_date
                # col_stat["numberOfNulls"] = total_count - int(col_stat["count"])
                # col_stat["numberOfNotNulls"] = int(col_stat["count"])
                # col_stat["numberOfUniqueValues"] = None
                chart_data[column] = {}

            modified_col_stat = []
            for k,v in col_stat.items():
                if k not in ["LevelCount","min","max","mean","stddev","numberOfNotNulls","MaxLevel","MinLevel"]:
                    modified_col_stat.append({"name":k,"value":v,"display":True,"displayName":displayNameDict[k]})
                else:
                    modified_col_stat.append({"name":k,"value":v,"display":False,"displayName":displayNameDict[k]})
            modified_col_stat = sorted(modified_col_stat,key=lambda x:displayOrderDict[x["name"]])
            output[column] = modified_col_stat
        return output,chart_data


    # def get_datetime_suggestions(self,df,col_name):
    #     output = {}
    #     date_time_suggestions = {}
    #     formats = GLOBALSETTINGS.SUPPORTED_DATETIME_FORMATS["formats"]
    #     dual_checks = GLOBALSETTINGS.SUPPORTED_DATETIME_FORMATS["dual_checks"]
    #     row_vals = df.select(col_name).distinct().na.drop().collect()
    #     # row_vals = df.select(dims).na.drop().take(int(self.total_rows**0.5 + 1))
    #     if len(row_vals) > 0:
    #         x = row_vals[0][col_name]
    #         for format1 in formats:
    #             try:
    #                 t = datetime.strptime(x,format1)
    #                 # if (format1 in dual_checks):
    #                 #     for x1 in row_vals:
    #                 #         x = x1[dims]
    #                 #         try:
    #                 #             t = dt.datetime.strptime(x,format1)
    #                 #         except ValueError as err:
    #                 #             format1 = '%d'+format1[2]+'%m'+format1[5:]
    #                 #             break
    #                 output[col_name] = format1
    #                 break
    #             except ValueError as err:
    #                 pass
    #     return output

    def get_datetime_format(self,columnVector):
        """
        suggest candidate for datetime column.
        checks against a list of datetime formats

        Arguments:
        columnVector -- an array of strings of any size.

        Return:
        detectedFormat -- datetime format
        """
        detectedFormat = None
        # availableDateTimeFormat = GLOBALSETTINGS.SUPPORTED_DATETIME_FORMATS["formats"]
        # sample1 = str(columnVector[0])
        # for dt_format in availableDateTimeFormat:
        #     try:
        #         t = datetime.strptime(sample1,dt_format)
        #         detectedFormat = dt_format
        #         break
        #     except ValueError as err:
        #         pass
        formats = GLOBALSETTINGS.SUPPORTED_DATETIME_FORMATS["formats"]
        dual_checks = GLOBALSETTINGS.SUPPORTED_DATETIME_FORMATS["dual_checks"]
        x = columnVector[0][0]
        for format1 in formats:
            try:
                t = datetime.strptime(x,format1)
                if (format1 in dual_checks):
                    for x1 in columnVector:
                        x = x1[0]
                        try:
                            t = datetime.strptime(x,format1)
                        except ValueError as err:
                            format1 = '%d'+format1[2]+'%m'+format1[5:]
                            break
                detectedFormat = format1
                break
            except ValueError as err:
                pass
        return detectedFormat


    def get_ignore_column_suggestions(self,df,column_name,dataType,colStat,max_levels=100):
        ignore = False
        reason = None
        total_rows = df.count()
        modifiedColStat = {}
        for obj in colStat:
            modifiedColStat[obj["name"]] = obj["value"]
        colStat = modifiedColStat
        if dataType == "measure":
            if (colStat["numberOfUniqueValues"]==1):
                ignore = True
                reason = "Only one Unique Value"
            if (colStat["numberOfNulls"] > 0):
                if (colStat["numberOfUniqueValues"]==2):
                    ignore = True
                    reason = "Only one Unique Value"
            if (colStat["numberOfNulls"] == 0):
                if (colStat["numberOfUniqueValues"] == total_rows):
                    ignore = True
                    reason = "Index column (all values are distinct)"
            else:
                if (colStat["numberOfNulls"] > colStat["numberOfNotNulls"]):
                    ignore = True
                    reason = "Count of Nulls More than Count of Not Nulls"
                # handling cases where some ids will be missing
                elif (colStat["numberOfNotNulls"] <= 0.01*colStat["numberOfUniqueValues"]):
                    ignore = True
                    reason = "Index Column(Most of Not Null Values are unique)"

        elif dataType == "dimension":
            if (colStat["numberOfUniqueValues"]==1):
                ignore = True
                reason = "Only one Unique Value"
            if (colStat["numberOfNulls"] == 0):
                if (colStat["numberOfUniqueValues"] == total_rows):
                    ignore = True
                    reason = "Index Column (all values are distinct)"
            else:
                if (colStat["numberOfNulls"] > colStat["numberOfNotNulls"]):
                    ignore = True
                    reason = "Count of Nulls More than Count of Not Nulls"
                elif (colStat["numberOfNotNulls"]==1):
                    ignore = True
                    reason = "Only one Not Null value"
                elif colStat["numberOfUniqueValues"] > max_levels:
                    ignore = True
                    reason = "Number of Levels are more than the defined thershold"
        return ignore,reason


    def get_utf8_suggestions(self,colStat):
        utf8 = False
        modifiedColStat = {}
        for obj in colStat:
            modifiedColStat[obj["name"]] = obj["value"]
        colStat = modifiedColStat
        levels = colStat["LevelCount"].keys()
        for val in levels:
            if val:
                if any([ord(char)>127 for char in val]):
                    utf8 = True
                    break
        return utf8

    @accepts(object,pd.DataFrame,(tuple,list),bool)
    def format_sampledata_timestamp_columns(self,pandasDf,timestampCols,stripTimestampFlag):
        if len(timestampCols) > 0:
            for colname in timestampCols:
                pandasDf[colname] = pandasDf[colname].apply(str)
                if stripTimestampFlag == True:
                    pandasDf[colname] = pandasDf[colname].apply(lambda x:x[:10])
                else:
                    unique_timestamps = pandasDf[colname].unique()
                    if len(unique_timestamps) == 1 and unique_timestamps[0] == "00:00:00":
                        pandasDf[colname] = pandasDf[colname].apply(lambda x:x[:10])
        return pandasDf.values.tolist()

    def set_sample_data(self):
        if self.rows > 100:
            sample_data = self.df.sample(False, float(100)/self.rows, seed=420)
            return sample_data
        else:
            return self.df

    def get_sample_data(self):
        return self._sample_data

    def get_percentage_columns(self, dimension_columns):
        sdf = self._sample_data
        orig_count = sdf.count()
        percentage_columns = []
        for col in dimension_columns:
            df = sdf.withColumn('new_column', sdf[col].substr(-1, 1))
            df = df.select('new_column').distinct()
            if df.count()==1 and df.first()['new_column']=='%':
                # print "percentage"
                result = sdf.withColumn('percent', regexp_extract(sdf[col], '^(((\s)*?[+-]?([0-9]+(\.[0-9][0-9]?)?)(\s)*)[^%]*)',1))
                result = result.select(result.percent.cast('float'))
                not_nulls = result.select('percent').na.drop().count()
                if orig_count == not_nulls:
                    percentage_columns.append(col)
        return percentage_columns

    def get_dollar_columns(self, dimension_columns):
        sdf = self._sample_data
        orig_count = sdf.count()
        dollar_columns = []
        for col in dimension_columns:
            df = sdf.withColumn('new_column', sdf[col].substr(1, 1))
            df = df.select('new_column').distinct()
            if df.count()==1 and df.first()['new_column']=='$':
                # print "dollar_columns"
                result = sdf.withColumn('dollar', regexp_extract(sdf[col], '^([$]((\s)*?[+-]?([0-9]+(\.[0-9][0-9]?)?)(\s)*)*)',2))
                result = result.select(result.dollar.cast('float'))
                not_nulls = result.select('dollar').na.drop().count()
                if orig_count == not_nulls:
                    dollar_columns.append(col)
        return dollar_columns
