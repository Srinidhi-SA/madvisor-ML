from bi.narratives.anova import AnovaNarratives
from bi.stats import TwoWayAnova


class TwoWayAnovaScript:
    def __init__(self, data_frame, df_helper, df_context, result_setter, spark, story_narrative, meta_parser,scriptWeight=None, analysisName=None):
        self._story_narrative = story_narrative
        self._result_setter = result_setter
        self._data_frame = data_frame
        self._dataframe_helper = df_helper
        self._dataframe_context = df_context
        self._spark = spark
        self._metaParser = meta_parser
        self._scriptWeightDict = scriptWeight
        self._analysisName = analysisName
        if analysisName == None:
            self._analysisName = self._dataframe_context.get_analysis_name()
        else:
            self._analysisName = analysisName
        if scriptWeight == None:
            self._scriptWeightDict = self._dataframe_context.get_measure_analysis_weight()
        else:
            self._scriptWeightDict = scriptWeight

    def Run(self):

        df_anova_obj = TwoWayAnova(self._data_frame, self._dataframe_helper, self._dataframe_context,
                                   self._metaParser,scriptWeight=self._scriptWeightDict,analysisName=self._analysisName).test_all(measure_columns=(self._dataframe_context.get_result_column(),))
        # df_anova_result = CommonUtils.as_dict(df_anova_obj)
        # print 'RESULT: %s' % (json.dumps(df_anova_result, indent=2))
        anova_narratives_obj = AnovaNarratives(df_anova_obj, self._dataframe_helper, self._dataframe_context,
                                               self._result_setter, self._story_narrative,scriptWeight=self._scriptWeightDict,analysisName=self._analysisName)
        # print anova_narratives
        # DataWriter.write_dict_as_json(self._spark, {'RESULT':json.dumps(df_anova_result['result'])}, self._dataframe_context.get_result_file()+'OneWayAnova/')
        # DataWriter.write_dict_as_json(self._spark, {'narratives':json.dumps(anova_narratives['narratives'])}, self._dataframe_context.get_narratives_file()+'OneWayAnova/')
        # print "Narratives: %s" % (json.dumps(anova_narratives, indent=2))
