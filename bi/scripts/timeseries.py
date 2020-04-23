from bi.common import utils as CommonUtils
from bi.narratives.trend import TimeSeriesNarrative


class TrendScript:

    def __init__(self, df_helper, df_context, result_setter, spark, story_narrative, meta_parser):
        self._story_narrative = story_narrative
        self._result_setter = result_setter
        self._dataframe_helper = df_helper
        self._spark = spark
        self._dataframe_context = df_context
        self._metaParser = meta_parser


    def Run(self):
        trend_narratives_obj = TimeSeriesNarrative(self._dataframe_helper, self._dataframe_context, self._result_setter, self._spark, self._story_narrative, self._metaParser)
        trend_narratives = CommonUtils.as_dict(trend_narratives_obj)
        # print json.dumps(trend_narratives, indent=2)
        # DataWriter.write_dict_as_json(self._spark, {"TREND":json.dumps(trend_narratives)}, self._dataframe_context.get_narratives_file()+'Trend/')
