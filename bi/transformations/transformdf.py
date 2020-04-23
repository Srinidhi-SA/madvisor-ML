import time

from pyspark.sql.functions import col, udf
from pyspark.sql.types import StringType
from bi.settings import setting as GLOBALSETTINGS
from pyspark.sql.functions import col, create_map, lit
from itertools import chain
from bi.common.decorators import accepts




#import bi.common.dataframe

class DataFrameTransformer:
    # @accepts(object,DataFrame,DataFrameHelper,ContextSetter)
    def __init__(self, dataframe, df_helper, df_context, meta_parser):
        self._data_frame = dataframe
        self._metaParser = meta_parser
        self._dataframe_helper = df_helper
        self._dataframe_context = df_context
        self._completionStatus = 0
        self._start_time = time.time()
        self._analysisName = "transformation"
        self._messageURL = self._dataframe_context.get_message_url()
        self._replaceTypeList = ["equals","contains","startsWith","endsWith"]
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

    def applyTransformations(self):
        """
        here all the filter settings will come from the df_context
        """
        existingColTransforms = self._dataframe_context.get_existing_column_transform_settings()
        newColTransforms = self._dataframe_context.get_new_column_transform_settings()
        if len(existingColTransforms) > 0:
            for transformObj in existingColTransforms:
                transformActionList = [obj["actionName"]  for obj in transformObj["columnSetting"]]
                colName = self._metaParser.get_name_from_slug(transformObj["slug"])
                if "delete" in transformActionList:
                    self.delete_column(colName)
                else:
                    for obj in transformObj["columnSetting"]:
                        if obj["actionName"] == "replace":
                            self.update_column_data(colName,obj["replacementValues"])
                        if obj["actionName"] == "rename":
                            self.update_column_name(colName,obj["newName"])
                        if obj["actionName"] == "data_type":
                            castDataType = [x["name"] for x in obj["listOfActions"] if x["status"] == True][0]
                            print castDataType
                            if castDataType == "numeric":
                                newDataType = 'int'
                            elif castDataType == "text":
                                newDataType = "string"
                            elif castDataType == "datetime":
                                newDataType = "timestamp"
                            self.update_column_datatype(colName,newDataType)
                            print self._data_frame.printSchema()
                    print self._data_frame.printSchema()




    def add_new_columns(self,df,new_col_name,old_col_list,operator):
        print "adding new column"
        col_dtype_list=[] #will take dtype of all the merger column to see unique value
        ncol_dtype=False
        col_dtype_map={}
        col_dtype_setlist=df.dtypes
        for col_dtype_set in col_dtype_setlist:
            col_dtype_map[col_dtype_set[0]]=col_dtype_set[1]
        #will check data type of each column,if all of them are same then only we will merge different col dataset to create new col
        print col_dtype_map
        dtype_col_map={}
        for old_col in old_col_list:
            dtype=col_dtype_map[old_col]
            col_dtype_list.append(dtype)
            if dtype in dtype_col_map:
                dtype_col_map[dtype]=dtype_col_map[dtype].append(old_col)
            else:
                dtype_col_map[dtype]=[old_col]
        print col_dtype_list
        uniq_dtype_list=list(set(col_dtype_list))
        newdf=df
        if uniq_dtype_list and len(uniq_dtype_list)==1:
            #newdf = df.withColumn('total', sum(df[col] for col in df.columns))
            print new_col_name
            newdf=df.withColumn(new_col_name,lit(10))
            #TODO here actual operation is not happening,need to change according to the passed operator
            #newdf=     df.withColumn(new_col_name,sum(df[col] for col in old_col_list))
            #all the data type of merger columns are same so we can create new column adding different fields data
            print "all data type is same"
        else:
            print "data type of merger column are different so cant concatnate different data types"
            for dtype in dtype_col_map.keys():
                print dtype_col_map[dtype]
        return newdf

    def delete_column(self,column):
        self._data_frame = self._data_frame.drop(column)

    def update_column_data(self,column_name,replace_obj_list):
        for replace_obj in replace_obj_list:
            if replace_obj["valueToReplace"] == "" and replace_obj["replacedValue"] == "":
                pass
            else:
                key = replace_obj["valueToReplace"]
                value = replace_obj["replacedValue"]
                replace_type = replace_obj["replaceType"]
                if replace_type in self._replaceTypeList:
                    if replace_type == "contains":
                        replace_values = udf(lambda x: x.replace(key,value),StringType())
                        self._data_frame = self._data_frame.withColumn(column_name,replace_values(col(column_name)))
                    if replace_type == "startsWith":
                        print replace_obj
                        replace_values = udf(lambda x: replace_obj["replacedValue"]+x[len(replace_obj["valueToReplace"]):] if x.startswith(replace_obj["valueToReplace"]) else x,StringType())
                        self._data_frame = self._data_frame.withColumn(column_name,replace_values(col(column_name)))
                    if replace_type == "endsWith":
                        print replace_obj
                        replace_values = udf(lambda x: x[:-len(replace_obj["valueToReplace"])]+replace_obj["replacedValue"] if x.endswith(replace_obj["valueToReplace"]) else x,StringType())
                        self._data_frame = self._data_frame.withColumn(column_name,replace_values(col(column_name)))
                    if replace_type == "equals":
                        replace_values = udf(lambda x: x.replace(key,value) if x==replace_obj["valueToReplace"] else x,StringType())
                        self._data_frame = self._data_frame.withColumn(column_name,replace_values(col(column_name)))

    def update_column_datatype(self,column_name,data_type):
        print "Updating column data type"
        self._data_frame = self._data_frame.withColumn(column_name, self._data_frame[column_name].cast(data_type))
        print self._data_frame.printSchema()
        # TODO update data type as measure or dimension

    def update_column_name(self,old_column_name,new_column_name):
        print "old_column_name",old_column_name
        print "new_column_name",new_column_name
        if new_column_name:
            self._data_frame = self._data_frame.withColumnRenamed(old_column_name,new_column_name)
            # print self._data_frame.columns

    @accepts(object,targetCol = (tuple,list),topnLevel=int,defaltName=basestring,newLevelNameDict=dict)
    def change_dimension_level_name(self,targetCol,defaltName = "Others",topnLevel = None, newLevelNameDict = None):
        """
        used to change level names of a particular dimension columns
        Parameters
        ----------
        self : Object
            An Object of class DataFrameTransformer
        targetCol : list/tuple of strings
            column on which to apply this transformation.
        topnLevel : int or None
            Top levels to keep(by level count). all other levels will be clubbed as "Others"
        defaltName : basestring
            default Name given to all the Other levels
        newLevelNameDict : dict
            mapping for changing Level Name {"existingName1":"newName1","existingName2":"newName2"}

        Notes
        ----------
        If both topnLevel and newLevelNameDict are provided then topnLevel will take precedence

        """
        if topnLevel != None:
            topnLevel = topnLevel
        else:
            topnLevel = GLOBALSETTINGS.DTREE_TARGET_DIMENSION_MAX_LEVEL - 1
        print targetCol

        for colName in targetCol:
            levelCountDict = self._metaParser.get_unique_level_dict(colName)
            levelCountArray = sorted(levelCountDict.items(),key=lambda x:x[1],reverse=True)
            countArr = [x[1] for x in levelCountArray]
            totalCount = sum(countArr)
            existinCount = sum(countArr[:topnLevel])
            newLevelCount = levelCountArray[:topnLevel]
            newLevelCount.append((defaltName,totalCount-existinCount))
            mappingDict = dict([(tup[0],tup[0]) if idx <= topnLevel-1 else (tup[0],defaltName) for idx,tup in enumerate(levelCountArray)])
            mapping_expr = create_map([lit(x) for x in chain(*mappingDict.items())])
            existingCols = self._data_frame.columns
            self._data_frame = self._data_frame.withColumnRenamed(colName,str(colName)+"JJJLLLLKJJ")
            self._data_frame = self._data_frame.withColumn(colName,mapping_expr.getItem(col(str(colName)+"JJJLLLLKJJ")))
            self._data_frame = self._data_frame.select(existingCols)
            self._dataframe_helper.set_dataframe(self._data_frame)
            self._metaParser.update_level_counts(colName,dict(newLevelCount))


    def get_transformed_data_frame(self):
        return self._data_frame
