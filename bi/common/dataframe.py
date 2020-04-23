import datetime as dt
# import dateparser
import datetime as dt
from datetime import datetime
from itertools import chain

# import dateparser
import pandas as pd
from pyspark.ml.feature import Bucketizer
from pyspark.sql import DataFrame
from pyspark.sql import functions as FN
from pyspark.sql.functions import col, create_map, lit
from pyspark.sql.functions import udf
from pyspark.sql.types import *
from pyspark.sql.types import StringType
from pyspark.sql.types import IntegerType
from sklearn.model_selection import train_test_split

from bi.common import ContextSetter
from bi.common import utils as CommonUtils
from bi.common import MetaParser
from column import ColumnType
from decorators import accepts
from exception import BIException
from bi.settings import setting as GLOBALSETTINGS



class DataFrameHelper:
    """
    Provides helper method to query properties of a dataframe
    """

    MEASURE_COLUMNS = "measure_columns"
    DIMENSION_COLUMNS = "dimension_columns"
    TIME_DIMENSION_COLUMNS = "time_dimension_columns"
    BOOLEAN_COLUMNS = "boolean_columns"
    NULL_VALUES = 'num_nulls'
    NON_NULL_VALUES = 'num_non_nulls'

    @accepts(object,data_frame=DataFrame,df_context=ContextSetter,meta_parser=MetaParser)
    def __init__(self, data_frame, df_context, meta_parser):
        # stripping spaces from column names
        self._data_frame = data_frame.select(*[col(c.name).alias(c.name.strip()) for c in data_frame.schema.fields])
        self.columns = self._data_frame.columns
        self._dataframe_context = df_context
        self._metaParser = meta_parser

        self.column_data_types = {}
        self.numeric_columns = []
        self.string_columns = []
        self.timestamp_columns = []
        self.boolean_columns = []

        self.num_rows = 0
        self.num_columns = 0
        self.measure_suggestions = []
        self.train_test_data = {"x_train":None,"x_test":None,"y_train":None,"y_test":None}
        self._date_formats = {}
        self.significant_dimensions = {}
        self.chisquare_significant_dimensions = {}

        self.ignorecolumns = self._dataframe_context.get_ignore_column_suggestions()
        self.utf8columns = self._dataframe_context.get_utf8_columns()
        self.resultcolumn = self._dataframe_context.get_result_column()
        self.consider_columns = self._dataframe_context.get_consider_columns()
        self.percentage_columns = self._dataframe_context.get_percentage_columns()
        self.dollar_columns = self._dataframe_context.get_dollar_columns()
        self.colsToBin = []

    def set_dataframe(self,sparkDf):
        self._data_frame = sparkDf

    def set_params(self):
        print "Setting the dataframe"
        self._data_frame = CommonUtils.convert_percentage_columns(self._data_frame, self.percentage_columns)
        self._data_frame = CommonUtils.convert_dollar_columns(self._data_frame, self.dollar_columns)
        colsToBin = [x["colName"] for x in self._dataframe_context.get_custom_analysis_details()]
        print "ignorecolumns:-",self.ignorecolumns
        # removing any columns which comes in customDetails from ignore columns
        self.ignorecolumns = list(set(self.ignorecolumns)-set(colsToBin))
        self.consider_columns = list(set(self.consider_columns)-set(self.utf8columns))
        print "self.resultcolumn",self.resultcolumn
        if self.resultcolumn != "":
            colsToKeep = list(set(self.consider_columns).union(set([self.resultcolumn])))
        else:
            colsToKeep = list(set(self.consider_columns))
        colsToBin = list(set(colsToBin)&set(colsToKeep))
        print "colsToKeep:-",colsToKeep
        print "colsToBin:-",colsToBin
        self.colsToBin = colsToBin
        appid = str(self._dataframe_context.get_app_id())
        if appid != "None":
            app_type = GLOBALSETTINGS.APPS_ID_MAP[appid]["type"]
        else:
            app_type = None
        if app_type != "REGRESSION":
            if self._dataframe_context.get_job_type() != "subSetting":
                if self._dataframe_context.get_job_type() != "prediction":
                    self._data_frame = self._data_frame.select(colsToKeep)
                else:
                    if app_type == "CLASSIFICATION":
                        if self._dataframe_context.get_story_on_scored_data() == False:
                            result_column = self._dataframe_context.get_result_column()
                            updatedColsToKeep = list(set(colsToKeep) - {result_column})
                            self._data_frame = self._data_frame.select(updatedColsToKeep)
                        elif self._dataframe_context.get_story_on_scored_data() == True:
                            self._data_frame = self._data_frame.select(colsToKeep)
                    elif app_type == "REGRESSION":
                        self._data_frame = self._data_frame.select(colsToKeep)
        self.columns = self._data_frame.columns
        self.bin_columns(colsToBin)
        self.update_column_data()
        print "boolean_columns",self.boolean_columns
        self.boolean_to_string(list(set(colsToKeep) & set(self.boolean_columns)))
        dataTypeChange = self._dataframe_context.get_change_datatype_details()
        print dataTypeChange
        self.change_data_type(dataTypeChange)
        self.update_column_data()

    def update_column_data(self):
        dfSchemaFields = self._data_frame.schema.fields
        self.columns = [field.name for field in dfSchemaFields]
        self.num_columns = len(self._data_frame.columns)
        self.num_rows = self._metaParser.get_num_rows()
        self.column_data_types = {field.name: field.dataType for field in dfSchemaFields}
        self.numeric_columns = []
        self.string_columns = []
        self.boolean_columns = []
        self.timestamp_columns = []
        for field in dfSchemaFields:
            if ColumnType(type(field.dataType)).get_abstract_data_type() == ColumnType.MEASURE:
                self.numeric_columns.append(field.name)
            if ColumnType(type(field.dataType)).get_abstract_data_type() == ColumnType.DIMENSION:
                self.string_columns.append(field.name)
            if ColumnType(type(field.dataType)).get_abstract_data_type() == ColumnType.BOOLEAN:
                self.boolean_columns.append(field.name)
            if ColumnType(type(field.dataType)).get_abstract_data_type() == ColumnType.TIME_DIMENSION:
                self.timestamp_columns.append(field.name)
        # print self.string_columns


    def boolean_to_string(self,colsToConvert):
        if len(colsToConvert) > 0:
            for column in colsToConvert:
                self._data_frame = self._data_frame.withColumn(column, self._data_frame[column].cast(StringType()))

    def change_data_type(self,dataTypeChange):
        print "Updating column data type"
        for obj in dataTypeChange:
            try:
                if obj["columnType"] == "dimension":
                    self._data_frame = self._data_frame.withColumn(obj["colName"], self._data_frame[obj["colName"]].cast(StringType()))
                elif obj["columnType"] == "measure":
                    self._data_frame = self._data_frame.withColumn(obj["colName"], self._data_frame[obj["colName"]].cast(IntegerType()))
                print self._data_frame.printSchema()
            except:
                pass

    def set_train_test_data(self,df):
        result_column = self._dataframe_context.get_result_column()
        train_test_ratio = float(self._dataframe_context.get_train_test_split())
        date_columns = self._dataframe_context.get_date_columns()
        uidCol = self._dataframe_context.get_uid_column()
        print "All DATE Columns",date_columns
        considerColumns = self._dataframe_context.get_consider_columns()
        columns_to_ignore = [result_column]+date_columns
        if uidCol:
            columns_to_ignore += [uidCol]
        print "These Columns are Ignored:- ",  columns_to_ignore
        columns_to_keep = list(set(considerColumns)-set(columns_to_ignore))
        if train_test_ratio == None:
            train_test_ratio = 0.7
        appid = self._dataframe_context.get_app_id()
        print "appid",appid
        print "="*30
        app_type = GLOBALSETTINGS.APPS_ID_MAP[appid]["type"]
        print "app_type",app_type
        print "="*30
        if app_type == "CLASSIFICATION":
            x_train,x_test,y_train,y_test = train_test_split(df[columns_to_keep], df[result_column], train_size=train_test_ratio, random_state=42, stratify=df[result_column])
        elif app_type == "REGRESSION":
            x_train,x_test,y_train,y_test = train_test_split(df[columns_to_keep], df[result_column], train_size=train_test_ratio, random_state=42)
        # x_train,x_test,y_train,y_test = MLUtils.generate_train_test_split(df,train_test_ratio,result_column,drop_column_list)
        self.train_test_data = {"x_train":x_train,"x_test":x_test,"y_train":y_train,"y_test":y_test}

    def fill_missing_values(self,df):
        """
        Filling missing values
        missing values in categorical columns are replaced by 'NA'
        missing values in numerical columns are replaced by 0
        if there is missing value in target column those rows are deleted
        """
        categorical_columns = self.get_string_columns()
        numerical_columns = self.get_numeric_columns()
        replacement_dict = {}
        for col in numerical_columns:
            replacement_dict[col] = 0
        for col in categorical_columns:
            replacement_dict[col] = "NA"
        df = df.fillna(replacement_dict)
        return df

    def remove_null_rows(self, column_name):
        """
        remove rows where the given column has null values
        """
        self._data_frame = self._data_frame.na.drop(subset=[column_name])
        self.num_rows = self._data_frame.count()


    def bin_columns(self,colsToBin):
        for bincol in colsToBin:
            minval,maxval = self._data_frame.select([FN.max(bincol).alias("max"),FN.min(bincol).alias("min")]).collect()[0]
            n_split=10
            splitsData = CommonUtils.get_splits(minval,maxval,n_split)
            splits = splitsData["splits"]
            self._data_frame = self._data_frame.withColumn(bincol, self._data_frame[bincol].cast(DoubleType()))
            bucketizer = Bucketizer(inputCol=bincol,outputCol="BINNED_INDEX")
            bucketizer.setSplits(splits)
            self._data_frame = bucketizer.transform(self._data_frame)
            mapping_expr = create_map([lit(x) for x in chain(*splitsData["bin_mapping"].items())])
            self._data_frame = self._data_frame.withColumnRenamed("bincol",bincol+"JJJLLLLKJJ")
            self._data_frame = self._data_frame.withColumn(bincol,mapping_expr.getItem(col("BINNED_INDEX")))
            self._data_frame = self._data_frame.select(self.columns)

    def get_cols_to_bin(self):
        return self.colsToBin

    def get_column_data_types(self):
        return self.column_data_types

    def get_columns(self):
        return self.columns

    @accepts(object, basestring)
    def has_column(self, column_name):
        return column_name in self.get_columns()

    def get_numeric_columns(self):
        return self.numeric_columns

    @accepts(object, basestring)
    def is_numeric_column(self, column_name):
        return column_name in self.get_numeric_columns()

    def get_string_columns(self):
        return self.string_columns

    def get_all_levels(self,column_name):
        return [levels[0] for levels in self._data_frame.select(column_name).distinct().collect()]

    def get_num_unique_values(self,column_name):
        return self._data_frame.select(column_name).distinct().count()

    @accepts(object, basestring)
    def is_string_column(self, column_name):
        return column_name in self.get_string_columns()

    def get_timestamp_columns(self):
        return self.timestamp_columns

    @accepts(object, basestring)
    def is_timestamp_column(self, column_name):
        return column_name in self.get_timestamp_columns()

    def get_num_rows(self):
        return self.num_rows

    def get_num_columns(self):
        return self.num_columns

    def get_boolean_columns(self):
        return self.boolean_columns

    def get_data_frame(self):
        return self._data_frame

    def add_significant_dimension(self, dimension, effect_size):
        self.significant_dimensions[dimension] = effect_size

    def get_significant_dimension(self):
        return self.significant_dimensions

    def add_chisquare_significant_dimension(self, dimension, effect_size):
        self.chisquare_significant_dimensions[dimension] = effect_size

    def get_chisquare_significant_dimension(self):
        return self.chisquare_significant_dimensions

    def get_num_null_values(self, column_name):
        if not self.has_column(column_name):
            raise BIException('No such column exists: %s' %(column_name,))

        column = FN.col(column_name)
        rows = self._data_frame.select(column).groupBy(FN.isnull(column)).agg({'*': 'count'}).collect()
        for row in rows:
            if row[0] == True:
                return row[1]
        return 0

    def filter_dataframe(self, colname, values):
        if type(values) == str:
            values = values[1:-1]
            values = values.split(',')
        df = self._data_frame.where(col(colname).isin(values))
        return df

    def get_aggregate_data(self, aggregate_column, measure_column, existingDateFormat = None, requestedDateFormat = None):
        self._data_frame = self._data_frame.na.drop(subset=aggregate_column)
        if existingDateFormat != None and requestedDateFormat != None:
            print existingDateFormat,requestedDateFormat
            # def date(s):
            #   return str(s.date())
            # date_udf = udf(date, StringType())
            # Below line is just for testing a special scenario
            # func = udf(lambda x: datetime.strptime(x.strip("*"),existingDateFormat).strftime(requestedDateFormat), StringType())
            func = udf(lambda x: datetime.strptime(x,existingDateFormat).strftime(requestedDateFormat), StringType())

            self._data_frame = self._data_frame.select(*[func(column).alias(aggregate_column) if column==aggregate_column else column for column in self._data_frame.columns])
            # subset_data = self._data_frame.select(aggregate_column,measure_column, date_udf(aggregate_column).alias("dateString"))
            subset_data = self._data_frame.select(aggregate_column,measure_column, aggregate_column)
            agg_data = subset_data.groupBy(aggregate_column).agg(FN.sum(measure_column)).toPandas()
            agg_data.columns = ["key","value"]
        else:
            agg_data = self._data_frame.groupBy(aggregate_column).agg(FN.sum(measure_column)).toPandas()
            agg_data.columns = ["key","value"]
        return agg_data

    def get_agg_data_frame(self,aggregate_column, measure_column, result_column,existingDateFormat=None,requestedDateFormat=None):
        data_frame = self._data_frame
        if existingDateFormat != None and requestedDateFormat != None:
            agg_data = data_frame.groupBy(aggregate_column).agg({measure_column : 'sum', result_column : 'sum'}).toPandas()
            try:
                agg_data['date_col'] = pd.to_datetime(agg_data[aggregate_column], format = existingDateFormat)
            except Exception as e:
                print e
                print '----  ABOVE EXCEPTION  ----' * 10
                existingDateFormat = existingDateFormat[3:6]+existingDateFormat[0:3]+existingDateFormat[6:]
                agg_data['date_col'] = pd.to_datetime(agg_data[aggregate_column], format = existingDateFormat)
            agg_data = agg_data.sort_values('date_col')
            agg_data[aggregate_column] = agg_data['date_col'].dt.strftime(requestedDateFormat)
            agg_data.columns = [aggregate_column,measure_column,result_column,"date_col"]
            agg_data = agg_data[[aggregate_column,measure_column, result_column]]
        elif existingDateFormat != None:
            agg_data = data_frame.groupBy(aggregate_column).agg({measure_column : 'sum', result_column : 'sum'}).toPandas()
            try:
                agg_data['date_col'] = pd.to_datetime(agg_data[aggregate_column], format = existingDateFormat)
            except Exception as e:
                print e
                print '----  ABOVE EXCEPTION  ----' * 10
                existingDateFormat = existingDateFormat[3:6]+existingDateFormat[0:3]+existingDateFormat[6:]
                agg_data['date_col'] = pd.to_datetime(agg_data[aggregate_column], format = existingDateFormat)
            agg_data = agg_data.sort_values('date_col')
            agg_data.columns = [aggregate_column,measure_column,result_column,"date_col"]
            agg_data = agg_data[['Date','measure']]
        else:
            agg_data = data_frame.groupBy(aggregate_column).agg({measure_column : 'sum', result_column : 'sum'}).toPandas()
            agg_data.columns = [aggregate_column,measure_column,result_column]
        return agg_data

    def fill_na_measure_mean(self):
        stats = self._data_frame.agg(*(avg(c).alias(c) for c in self.numeric_columns))
        self._data_frame = self._data_frame.na.fill(stats.first().asDict())
        #return self._data_frame.na.fill(stats.first().asDict())

    def fill_na_dimension_nulls(self):
        self._data_frame = self._data_frame.na.fill(value='nulls',subset=self.string_columns)

    def fill_na_zero(self):
        self._data_frame = self._data_frame.na.fill(0)

    def get_train_test_data(self):
        train_test_data = self.train_test_data
        x_train = train_test_data["x_train"]
        x_test = train_test_data["x_test"]
        y_train = train_test_data["y_train"]
        y_test = train_test_data["y_test"]
        return (x_train,x_test,y_train,y_test)

    @accepts(object,(tuple,list))
    def get_level_counts(self,colList):
        levelCont = {}
        for column in colList:
            levelCont[column] = self._data_frame.groupBy(column).count().toPandas().set_index(column).to_dict().values()[0]
        return levelCont

class DataFrameColumnMetadata:
    @accepts(object, basestring, type(ColumnType.MEASURE), type(ColumnType.INTEGER))
    def __init__(self, column_name, abstract_data_type, actual_data_type):
        self._column_name = column_name
        self._abstract_data_type = abstract_data_type
        self._actual_data_type = actual_data_type

    def get_column_name(self):
        return self._column_name

    def get_abstract_data_type(self):
        return self._abstract_data_type

    def get_actual_data_type(self):
        return self._actual_data_type

    def as_dict(self):
        """ Utility function return object as a dict for persisting as a JSON object
        :return:
        """
        return {
            self._column_name: self._column_type,
            'actual_data_type': self._actual_data_type,
            'abstract_data_type': self._abstract_data_type
        }
