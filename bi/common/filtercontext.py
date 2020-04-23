class FilterContextSetter:
    def __init__(self, config_obj):
        self._config_obj = config_obj
        self.CSV_FILE = ""
        self.RESULT_FILE = ""
        self.considercolumns = []

    def set_params(self):
        self.CSV_FILE = self._config_obj.get_file_settings()['inputfile'][0]
        self.RESULT_FILE = self._config_obj.get_file_settings()['result_file'][0]
        self.considercolumns = self._config_obj.get_column_settings().get('consider_columns')
        self.dimension_filter = self._config_obj.get_dimension_filters()
        self.measure_filter = self._config_obj.get_measure_filters()
        self.measure_suggestions = self._config_obj.get_file_settings().get('measure_suggestions')

    def set_params_cl(self, ip, result, cc, df, mf, ms=None):
        if ms is None:
            ms = []
        self.CSV_FILE = ip
        self.RESULT_FILE = result
        self.considercolumns = cc
        self.dimension_filter = df
        self.measure_filter = mf
        self.measure_suggestions = ms

    def get_input_file(self):
        return self.CSV_FILE

    def get_result_file(self):
        return self.RESULT_FILE

    def get_dimension_filters(self):
        return self.dimension_filter

    def get_measure_filters(self):
        return self.measure_filter

    def get_column_subset(self):
        return self.considercolumns

    def get_measure_suggestions(self):
        return self.measure_suggestions
