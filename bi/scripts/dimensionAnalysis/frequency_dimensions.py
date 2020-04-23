from bi.common import utils as CommonUtils
from bi.narratives.dimension.dimension_column import DimensionColumnNarrative
from bi.stats.frequency_dimensions import FreqDimensions


class FreqDimensionsScript:
    def __init__(self, data_frame, df_helper, df_context, spark, result_setter, story_narrative):
        self._story_narrative = story_narrative
        self._result_setter = result_setter
        self._data_frame = data_frame
        self._dataframe_helper = df_helper
        self._dataframe_context = df_context
        self._spark = spark

    def Run(self):
        df_freq_dimension_obj = FreqDimensions(self._data_frame, self._dataframe_helper, self._dataframe_context).test_all(dimension_columns=(self._dataframe_context.get_result_column(),))
        # df_freq_dimension_result = CommonUtils.as_dict(df_freq_dimension_obj)
        # print 'RESULT: %s' % (json.dumps(df_freq_dimension_result, indent=2))
        # DataWriter.write_dict_as_json(self._spark, df_freq_dimension_result, self._dataframe_context.get_result_file()+'FreqDimension/')

        # Narratives
        narratives_obj = DimensionColumnNarrative(self._dataframe_context.get_result_column(), self._dataframe_helper, self._dataframe_context, df_freq_dimension_obj,self._story_narrative,self._result_setter)
        narratives = CommonUtils.as_dict(narratives_obj)
        # print "Narratives: %s" % (json.dumps(narratives, indent=2))
        # DataWriter.write_dict_as_json(self._spark, narratives, self._dataframe_context.get_narratives_file()+'FreqDimension/')
