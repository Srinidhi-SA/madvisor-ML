from bi.common.decorators import accepts
from bi.common.results import DfMetaData, MetaData, ColumnData, ColumnHeader

class MetaParser:
    def __init__(self):
        self.columnData = []
        self.headers = []
        self.sampleData = []
        self.metaData = []

    def set_params(self,metaDataDict):
        columnDataArray = metaDataDict["columnData"]
        headerArray = metaDataDict["headers"]
        if "sampleData" in metaDataDict:
            self.sampleData = metaDataDict["sampleData"]
        metaDataArray = metaDataDict["metaData"]
        for headerObj in headerArray:
            colHeaderClass = ColumnHeader()
            colHeaderClass.set_params(headerObj)
            self.headers.append(colHeaderClass)
        for metadataObj in metaDataArray:
            metaDataClass = MetaData()
            metaDataClass.set_params(metadataObj)
            self.metaData.append(metaDataClass)
        for colDataObj in columnDataArray:
            colDataClass = ColumnData()
            colDataClass.set_params(colDataObj)
            self.columnData.append(colDataClass)

        self.noOfRows = [obj.get_value() for obj in self.metaData if obj.get_name() == "noOfRows"][0]
        self.noOfColumns = [obj.get_value() for obj in self.metaData if obj.get_name() == "noOfColumns"][0]
        self.percentage_columns = [obj.get_value() for obj in self.metaData if obj.get_name() == "percentageColumns"][0]
        self.dollar_columns = [obj.get_value() for obj in self.metaData if obj.get_name() == "dollarColumns"][0]
        self.ignoreColumnSuggestions = [obj.get_value() for obj in self.metaData if obj.get_name() == "ignoreColumnSuggestions"][0]
        self.ignoreReason = [obj.get_value() for obj in self.metaData if obj.get_name() == "ignoreColumnReason"][0]
        self.ignoreColDict = dict(zip(self.ignoreColumnSuggestions,self.ignoreReason))
        self.utf8ColumnSuggestion = [obj.get_value() for obj in self.metaData if obj.get_name()=="utf8ColumnSuggestion"][0]
        self.dateTimeSuggestions = [obj.get_value() for obj in self.metaData if obj.get_name()=="dateTimeSuggestions"][0]
        self.uidCols = [k for k,v in self.ignoreColDict.items() if v.startswith("Index Column")]
        self.column_dict = dict([(obj.get_name(),obj) for obj in self.columnData])

    def update_column_dict(self,colname,columnStats):
        colDataObj = ColumnData()
        colDataObj.set_name(colname)
        colDataObj.set_abstract_datatype("dimension")
        colDataObj.update_level_count(columnStats["LevelCount"])
        colDataObj.update_unique_values(columnStats["numberOfUniqueValues"])
        self.column_dict.update({colname:colDataObj})

    def update_level_counts(self,columnList,levelCountDict):
        if isinstance(columnList,list) or isinstance(columnList,tuple):
            for val in columnList:
                colDataObj = self.column_dict[val]
                colDataObj.update_level_count(levelCountDict[val])
                colDataObj.update_unique_values(len(levelCountDict[val]))
                self.column_dict[val] = colDataObj
        elif isinstance(columnList,str):
            colDataObj = self.column_dict[columnList]
            colDataObj.update_level_count(levelCountDict)
            colDataObj.update_unique_values(len(levelCountDict))
            self.column_dict[columnList] = colDataObj

    def get_num_unique_values(self, column_name):
        return self.column_dict[column_name].get_unique_value_count(column_name)

    @accepts(object,column_name=(list,tuple,str))
    def get_unique_level_dict(self,column_name):
        if isinstance(column_name,str):
            return self.column_dict[column_name].get_level_count_dict(column_name)
        elif isinstance(column_name,list) or isinstance(column_name,tuple):
            out = {}
            for col in column_name:
                out[col] = self.column_dict[col].get_level_count_dict(col)
            return out

    def get_suggested_uid_columns(self):
        return self.uidCols

    def get_unique_level_names(self,column_name):
        if self.column_dict[column_name].get_column_type()=="dimension":
            return self.column_dict[column_name].get_level_count_dict(column_name).keys()
        else:
            return None

    # def get_minimum_value(self,column_name):
    #     if self.column_dict[column_name].get_column_type()=="measure":
    #         return self.column_dict[column_name].get_colstat_values(column_name,"min")
    #     else:
    #         return None
    # def get_maximum_value(self,column_name):
    #     if self.column_dict[column_name].get_column_type()=="measure":
    #         return self.column_dict[column_name].get_colstat_values(column_name,"max")
    #     else:
    #         return None

    def get_percentage_columns(self):
        return self.percentage_columns

    def get_dollar_columns(self):
        return self.dollar_columns

    def get_ignore_columns(self):
        return self.ignoreColumnSuggestions

    def check_column_isin_ignored_suggestion(self,colname):
        if colname in self.ignoreColumnSuggestions:
            return True
        else:
            return False

    def get_measure_suggestions(self):
        return []

    def get_date_format(self):
        return self.dateTimeSuggestions

    def get_utf8_columns(self):
        return self.utf8ColumnSuggestion

    def get_num_rows(self):
        return self.noOfRows

    def get_num_columns(self):
        return self.noOfColumns

    def get_name_from_slug(self,slug):
        headerOfInterest = filter(lambda x:x.get_slug()==slug,self.headers)
        if len(headerOfInterest) == 1:
            return headerOfInterest[0].get_name()
        else:
            return None
