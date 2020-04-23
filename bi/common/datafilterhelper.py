from pyspark.sql.functions import udf

from bi.common.datafilterer import DataFrameFilterer


class DataFilterHelper:
    def __init__(self, data_frame, df_context):
        self._data_frame = data_frame
        self._df_context = df_context

    def clean_data_frame(self):
        """
        used to convert dimension columns to measures takes input from config (measure suggestions).
        """
        try:
            func = udf(lambda x: utils.tryconvert(x), FloatType())
            self._data_frame = self._data_frame.select(*[func(c).alias(c) if c in self.measure_suggestions else c for c in self.columns])
            self._data_frame.schema.fields
        except:
            pass

    def set_params(self):
        self.subset_columns = self._df_context.get_column_subset()
        if not self.subset_columns==None:
            self._data_frame = self.subset_data_frame(self.subset_columns)

        self.measure_suggestions = self._df_context.get_measure_suggestions()

        if self.measure_suggestions != None:
            self.measure_suggestions = [m for m in self.measure_suggestions if m in self.subset_columns]
            if len(self.measure_suggestions)>0:
                    self.clean_data_frame()

        self.df_filterer = DataFrameFilterer(self._data_frame)
        self.dimension_filter = self._df_context.get_dimension_filters()
        if not self.dimension_filter==None:
            for colmn in self.dimension_filter.keys():
                self.df_filterer.values_in(colmn, self.dimension_filter[colmn])
        self.measure_filter = self._df_context.get_measure_filters()
        if not self.measure_filter==None:
            for colmn in self.measure_filter.keys():
                self.df_filterer.values_between(colmn, self.measure_filter[colmn][0],self.measure_filter[colmn][1],1,1)

        self._data_frame = self.df_filterer.get_filtered_data_frame()

    def get_data_frame(self):
        return self._data_frame

    def subset_data_frame(self, columns):
        return self._data_frame.select(*columns)
