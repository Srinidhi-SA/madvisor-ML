from bi.common import utils as CommonUtils
from bi.narratives.chisquare import ChiSquareNarratives
from bi.stats.chisquare import ChiSquare

class ChiSquareScript:
    def __init__(self, data_frame, df_helper, df_context, spark, story_narrative,result_setter,meta_parser):
        self._data_frame = data_frame
        self._dataframe_helper = df_helper
        self._dataframe_context = df_context
        self._spark = spark
        self._story_narrative = story_narrative
        self._result_setter = result_setter
        self._metaParser = meta_parser

    def Run(self):
        df_chisquare_obj = ChiSquare(self._data_frame, self._dataframe_helper, self._dataframe_context,self._metaParser).test_all(dimension_columns=(self._dataframe_context.get_result_column(),))
        # df_chisquare_result = CommonUtils.as_dict(df_chisquare_obj)
        # print 'RESULT: %s' % (json.dumps(df_chisquare_result, indent=2))
        # DataWriter.write_dict_as_json(self._spark, df_chisquare_result, self._dataframe_context.get_result_file()+'ChiSquare/')
        # Narratives
        # print self._data_frame.select('Sales').show()
        if df_chisquare_obj.get_result() != {}:
            chisquare_narratives = CommonUtils.as_dict(ChiSquareNarratives(self._dataframe_helper, df_chisquare_obj,self._spark, self._dataframe_context,self._data_frame,self._story_narrative,self._result_setter))
        # print '*'*1500
        # print 'Narrarives: %s' %(json.dumps(chisquare_narratives, indent=2))
        # DataWriter.write_dict_as_json(self._spark, {"narratives":json.dumps(chisquare_narratives["narratives"])}, self._dataframe_context.get_narratives_file()+'ChiSquare/')
