class ParserConfig():
    """docstring for ParserConfig."""
    def __init__(self, config):
        self.config = config
        self.FileSettings = {}
        self.ColumnSettings = {}
        self.DateSettings = {}
        self.DimensionFilter = {}
        self.MeasureFilter = {}
        self.DateFilter = {}
        self.FilterSettings = {}
        self.AdvanceSettings = {}
        self.TransformationSettings = {}
        self.StockSettings = {}
        self.DatabaseSettings = {}
        self.AlgorithmSettings = {}

    def get_algorithm_settings(self):
        return self.AlgorithmSettings

    def get_database_settings(self):
        return self.DatabaseSettings

    def get_dimension_filters(self):
        return self.DimensionFilter

    def get_measure_filters(self):
        return self.MeasureFilter

    def get_date_filters(self):
        return self.DateFilter

    def get_date_settings(self):
        return self.DateSettings

    def get_file_settings(self):
        return self.FileSettings

    def get_column_settings(self):
        return self.ColumnSettings

    def get_filter_settings(self):
        return self.FilterSettings

    def get_advance_settings(self):
        return self.AdvanceSettings

    def get_transformation_settings(self):
        return self.TransformationSettings

    def get_stock_settings(self):
        return self.StockSettings

    def ConfigSectionMap(self, section):
        dict1 = {}
        try:
            options = self.config.options(section)
        except:
            return dict1
        for option in options:
            try:
                if self.config.get(section, option).strip() is "":
                    dict1[option] = None
                else:
                    dict1[option] = map(str.strip,self.config.get(section, option).strip().split(','))
                if dict1[option] == -1:
                    DebugPrint("skip: %s" % option)
            except:
                print("exception on %s!" % option)
                dict1[option] = None
        return dict1

    def set_params(self):
        self.FileSettings = self.ConfigSectionMap('FILE_SETTINGS')
        self.ColumnSettings = self.ConfigSectionMap('COLUMN_SETTINGS')
        self.DateSettings = self.ConfigSectionMap('DATE_SETTINGS')
        # self.DimensionFilter = self.ConfigSectionMap('DIMENSION_FILTER')
        # self.MeasureFilter = self.ConfigSectionMap('MEASURE_FILTER')
        # self.DateFilter = self.ConfigSectionMap('DATE_FILTER')
        self.FilterSettings = self.ConfigSectionMap('FILTER_SETTINGS')

    def set_json_params(self):
        if 'FILE_SETTINGS' in self.config:
            self.FileSettings = self.config.get('FILE_SETTINGS')
        if 'COLUMN_SETTINGS' in self.config:
            self.ColumnSettings = self.config.get('COLUMN_SETTINGS')
        if 'FILTER_SETTINGS' in self.config:
            self.FilterSettings = self.config.get('FILTER_SETTINGS')
        if 'ADVANCED_SETTINGS' in self.config:
            self.AdvanceSettings = self.config.get('ADVANCED_SETTINGS')
        if 'TRANSFORMATION_SETTINGS' in self.config:
            self.TransformationSettings = self.config.get('TRANSFORMATION_SETTINGS')
        if 'STOCK_SETTINGS' in self.config:
            self.StockSettings = self.config.get('STOCK_SETTINGS')
        if 'DATA_SOURCE' in self.config:
            self.DatabaseSettings = self.config.get('DATA_SOURCE')
        if 'ALGORITHM_SETTING' in self.config:
            self.AlgorithmSettings = self.config.get('ALGORITHM_SETTING')
