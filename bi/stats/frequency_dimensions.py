import json

from bi.common import utils as CommonUtils
from bi.common.decorators import accepts
from bi.common.results import FreqDimensionResult

"""
Count Frequency in a Dimension
"""


class FreqDimensions:

    def __init__(self, data_frame, df_helper, df_context, scriptWeight=None, analysisName=None):
        self._data_frame = data_frame
        self._dataframe_helper = df_helper
        self._dataframe_context = df_context

        self._completionStatus = self._dataframe_context.get_completion_status()
        if analysisName == None:
            self._analysisName = self._dataframe_context.get_analysis_name()
        else:
            self._analysisName = analysisName
        self._messageURL = self._dataframe_context.get_message_url()
        if scriptWeight == None:
            self._scriptWeightDict = self._dataframe_context.get_dimension_analysis_weight()
        else:
            self._scriptWeightDict = scriptWeight

        self._scriptStages = {
            "freqinitialization":{
                "summary":"Initialized the Frequency Scripts",
                "weight":4
                },
            "groupby":{
                "summary":"running groupby operations",
                "weight":6
                },
            "completion":{
                "summary":"Frequency Stats Calculated",
                "weight":0
                },
            }
        CommonUtils.create_update_and_save_progress_message(self._dataframe_context,self._scriptWeightDict,self._scriptStages,self._analysisName,"freqinitialization","info",weightKey="script")


    @accepts(object, measure_columns=(list, tuple), dimension_columns=(list, tuple))
    def test_all(self, measure_columns=None, dimension_columns=None):
        freq_dimension_result = FreqDimensionResult()
        dimension = dimension_columns[0]
        frequency_dict = {}
        grouped_dataframe = self._data_frame.groupby(dimension).count().toPandas()
        CommonUtils.create_update_and_save_progress_message(self._dataframe_context,self._scriptWeightDict,self._scriptStages,self._analysisName,"groupby","info",weightKey="script")

        frequency_dict[dimension] = grouped_dataframe.to_dict()
        grouped_dataframe = grouped_dataframe.dropna()
        frequency_dict = json.dumps(frequency_dict)
        freq_dimension_result.set_params(frequency_dict)
        CommonUtils.create_update_and_save_progress_message(self._dataframe_context,self._scriptWeightDict,self._scriptStages,self._analysisName,"completion","info",weightKey="script")
        return freq_dimension_result
