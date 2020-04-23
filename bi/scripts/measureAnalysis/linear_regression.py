import time

from bi.algorithms import LinearRegression
from bi.common import utils as CommonUtils
from bi.narratives.regression import RegressionNarrative


# from bi.stats import Correlation

class LinearRegressionScript:
    def __init__(self, data_frame, df_helper, df_context, result_setter, spark, correlations,story_narrative,meta_parser):
        self._result_setter = result_setter
        self._metaParser = meta_parser
        self._story_narrative = story_narrative
        self._data_frame = data_frame
        self._dataframe_helper = df_helper
        self._dataframe_context = df_context
        self._spark = spark
        self._correlations = correlations

    def Run(self):
        fs = time.time()
        regression_result_obj = LinearRegression(self._data_frame, self._dataframe_helper, self._dataframe_context,self._metaParser,self._spark).fit(self._dataframe_context.get_result_column())
        regression_result = CommonUtils.as_dict(regression_result_obj)
        print "time taken for regression ",time.time()-fs,"seconds"

        # print 'Regression result: %s' % (json.dumps(regression_result, indent=2))
        # DataWriter.write_dict_as_json(self._spark, regression_result, self._dataframe_context.get_result_file()+'Regression/')

        # regression_narratives_obj = LinearRegressionNarrative(len(self._dataframe_helper.get_numeric_columns()),regression_result_obj, self._correlations,self._dataframe_helper)
        # regression_narratives = CommonUtils.as_dict(regression_narratives_obj)

        regression_narratives_obj = RegressionNarrative(self._dataframe_helper,self._dataframe_context,self._result_setter,self._spark,regression_result_obj,self._correlations,self._story_narrative,self._metaParser)
        regression_narratives = CommonUtils.as_dict(regression_narratives_obj.narratives)
        #print 'Regression narratives:  %s' %(json.dumps(regression_narratives, indent=2))
        # DataWriter.write_dict_as_json(self._spark, {"REGRESSION":json.dumps(regression_narratives)}, self._dataframe_context.get_narratives_file()+'Regression/')
