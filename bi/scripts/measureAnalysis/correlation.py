from bi.common import utils as CommonUtils
from bi.stats import Correlation


class CorrelationScript:
    def __init__(self, data_frame, df_helper, df_context, spark):
        self._data_frame = data_frame
        self._dataframe_helper = df_helper
        self._dataframe_context = df_context
        self._spark = spark

    def Run(self):
        correlations_obj = Correlation(self._data_frame, self._dataframe_helper, self._dataframe_context).correlations_for_one_column(self._dataframe_context.get_result_column())
        correlations_result = CommonUtils.as_dict(correlations_obj)

        # print 'RESULT: %s' % (json.dumps(correlations_result, indent=2))
        # DataWriter.write_dict_as_json(self._spark, correlations_result, self._dataframe_context.get_result_file()+'Correlation/')
        return correlations_obj
