import json

from bi.algorithms import DecisionTreeRegression
from bi.common import utils as CommonUtils
from bi.narratives.decisiontreeregression.decision_tree import DecisionTreeRegNarrative


class DecisionTreeRegressionScript:
    def __init__(self, data_frame, df_helper,df_context, result_setter, spark,story_narrative,meta_parser,scriptWeight=None, analysisName=None):
        self._story_narrative = story_narrative
        self._result_setter = result_setter
        self._data_frame = data_frame
        self._dataframe_helper = df_helper
        self._dataframe_context = df_context
        self._spark = spark
        self._metaParser = meta_parser
        self._scriptWeightDict = scriptWeight
        self._analysisName = analysisName

    def Run(self):
        df_decision_tree_obj = DecisionTreeRegression(self._data_frame, self._dataframe_context, self._dataframe_helper, self._spark, self._metaParser,scriptWeight=self._scriptWeightDict,analysisName=self._analysisName).test_all(measure_columns=(self._dataframe_context.get_result_column(),))
        narratives_obj = DecisionTreeRegNarrative(self._dataframe_context.get_result_column(), df_decision_tree_obj, self._dataframe_helper, self._dataframe_context, self._result_setter,self._story_narrative,scriptWeight=self._scriptWeightDict,analysisName=self._analysisName)
