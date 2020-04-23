import json

from bi.common import DataWriter
from bi.common import utils as CommonUtils
from bi.narratives.anova import AnovaNarratives
from bi.stats import OneWayAnova


class OneWayAnovaScript:
    def __init__(self, data_frame, df_helper, df_context, spark):
        self._data_frame = data_frame
        self._dataframe_helper = df_helper
        self._dataframe_context = df_context
        self._spark = spark

    def Run(self):
        df_anova_obj = OneWayAnova(self._data_frame, self._dataframe_helper, self._dataframe_context).test_all(measure_columns=(self._dataframe_context.get_result_column(),))
        df_anova_result = CommonUtils.as_dict(df_anova_obj)
        #print 'RESULT: %s' % (json.dumps(df_anova_result, indent=2))
        DataWriter.write_dict_as_json(self._spark, {'RESULT': json.dumps(df_anova_result)}, self._dataframe_context.get_result_file()+'OneWayAnova/')
        #print 'Written Anova Result'
        anova_narratives = CommonUtils.as_dict(AnovaNarratives(len(self._dataframe_helper.get_string_columns()), df_anova_obj, self._dataframe_helper))
        #print "Narratives: %s" % (json.dumps(anova_narratives, indent=2))
        DataWriter.write_dict_as_json(self._spark, anova_narratives, self._dataframe_context.get_narratives_file()+'OneWayAnova/')
