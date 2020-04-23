class DfMetaData:
    """
    Functionalities:
    """
    def __init__(self, metaData=None, columnData=None, headers=None, sampleData=None):
        if metaData is None:
            metaData = []
        if columnData is None:
            columnData = []
        if headers is None:
            headers = []
        if sampleData is None:
            sampleData = []
        self.metaData = metaData
        self.columnData = columnData
        self.headers = headers
        self.sampleData = sampleData

    def set_meta_data(self,data):
        self.metaData = data

    def set_column_data(self,data):
        self.columnData = data

    def set_header(self,data):
        self.headers = data

    def set_sample_data(self,data):
        self.sampleData = data

    def add_meta_data(self,data):
        self.metaData.append(data)

    def add_column_data(self,data):
        self.columnData.append(data)

    def add_headers(self,data):
        self.headers.append(data)


class MetaData:
    def __init__(self,name=None,value=None,display=True,displayName=None):
        self.name = name
        self.value = value
        self.display = display
        self.displayName = displayName

    # @accepts(object,dict)
    def set_params(self,data):
        if "name" in data:
            self.name = data["name"]
        if "value" in data:
            self.value = data["value"]
        if "display" in data:
            self.display = data["display"]
        if "displayName" in data:
            self.displayName = data["displayName"]

    def set_name(self,data):
        self.name = data

    def set_display_name(self,data):
        self.displayName = data

    def set_value(self,data):
        self.value = data

    def set_display(self,boolData):
        self.display = boolData

    def get_value(self):
        return self.value

    def get_name(self):
        return self.name

class ColumnData:
    def __init__(self, name=None, slug=None, columnStats=None, chartData=None, columnType = None):
        if columnStats is None:
            columnStats = []
        if chartData is None:
            chartData = {}
        self.name = name
        self.slug = None
        self.ignoreSuggestionFlag = False
        self.dateSuggestionFlag = False
        self.ignoreSuggestionMsg = None
        self.columnStats = columnStats
        self.chartData = chartData
        self.columnType = columnType
        self.actualColumnType = None

    # @accepts(object,dict)
    def set_params(self,data):
        if "name" in data:
            self.name = data["name"]
        if "slug" in data:
            self.slug = data["slug"]
        if "ignoreSuggestionFlag" in data:
            self.ignoreSuggestionFlag = data["ignoreSuggestionFlag"]
        if "dateSuggestionFlag" in data:
            self.dateSuggestionFlag = data["dateSuggestionFlag"]
        if "ignoreSuggestionMsg" in data:
            self.ignoreSuggestionMsg = data["ignoreSuggestionMsg"]
        if "columnStats" in data:
            self.columnStats = data["columnStats"]
        if "chartData" in data:
            self.chartData = data["chartData"]
        if "columnType" in data:
            self.columnType = data["columnType"]
        if "actualColumnType" in data:
            self.actualColumnType = data["actualColumnType"]


    def set_name(self,data):
        self.name = data

    def set_slug(self,data):
        self.slug = data

    def set_column_stats(self,data):
        self.columnStats = data

    def set_column_chart(self,data):
        self.chartData = data

    def set_abstract_datatype(self,data):
        self.columnType = data

    def set_actual_datatype(self,data):
        self.actualColumnType = data

    def set_level_count_to_null(self):
        self.columnStats = [obj if obj["name"] != "LevelCount" else {"name":obj["name"],"value":None,"display":False} for obj in self.columnStats]

    def set_chart_data_to_null(self):
        self.chartData = {}

    def set_ignore_suggestion_flag(self,data):
        self.ignoreSuggestionFlag = data

    def set_ignore_suggestion_message(self,data):
        self.ignoreSuggestionMsg = data

    def set_date_suggestion_flag(self,data):
        self.dateSuggestionFlag = data

    def is_utf8_column(self):
        return self.utf

    def is_ignore_suggestion_true(self):
        return self.ignoreSuggestionFlag

    def is_date_suggestion_true(self):
        return self.dateSuggestionFlag

    def get_ignore_reason(self):
        return self.ignoreSuggestionMsg

    def get_name(self):
        return self.name

    def get_slug(self):
        return self.slug

    def get_column_type(self):
        return self.columnType

    def get_actual_column_type(self):
        return self.actualColumnType

    def get_level_count_dict(self,colName):
        if self.columnType == "dimension":
            return [x["value"] for x in self.columnStats if x["name"] == "LevelCount"][0]
        else:
            return [x["value"] for x in self.columnStats if x["name"] == "LevelCount"][0]

    def get_colstat_values(self,colName,key=None):
        if self.columnType == "measure":
            if key != None:
                return [x["value"] for x in self.columnStats if x["name"] == key][0]
        else:
            return None

    def get_unique_value_count(self,colName):
        return [x["value"] for x in self.columnStats if x["name"] == "numberOfUniqueValues"][0]

    def update_level_count(self,levelCountDict):
        names = [x["name"]  for x in self.columnStats]
        if "LevelCount" in names:
            idx = names.index("LevelCount")
            newObj = self.columnStats[idx]
            newObj.update({"value":levelCountDict})
            self.columnStats[idx] = newObj
        else:
            newObj = {'display': True, 'displayName': 'LevelCount', 'name': 'LevelCount', 'value': levelCountDict}
            self.columnStats.append(newObj)

    def update_unique_values(self,uniqueVal):
        names = [x["name"]  for x in self.columnStats]
        if "numberOfUniqueValues" in names:
            idx = names.index("numberOfUniqueValues")
            newObj = self.columnStats[idx]
            newObj.update({"value":uniqueVal})
            self.columnStats[idx] = newObj
        else:
            newObj = {'display': False, 'displayName': 'Unique Values', 'name': 'numberOfUniqueValues', 'value': uniqueVal}
            self.columnStats.append(newObj)


class ColumnHeader:
    def __init__(self,name = None,slug = None):
        self.name = name
        self.slug = slug

    # @accepts(object,dict)
    def set_params(self,data):
        if "name" in data:
            self.name = data["name"]
        if "slug" in data:
            self.slug = data["slug"]

    def set_name(self,data):
        self.name = data

    def set_slug(self,data):
        self.slug = data

    def get_slug(self):
        return self.slug

    def get_name(self):
        return self.name
