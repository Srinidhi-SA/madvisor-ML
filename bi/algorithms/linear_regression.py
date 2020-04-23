from pyspark.ml.regression import LinearRegression as LR

from bi.common.exception import BIException
from bi.common.results.regression import DFRegressionResult
from bi.common.results.regression import RegressionResult
from bi.common import utils as CommonUtils
from bi.common import DataLoader
from bi.common import DataFrameHelper
from bi.algorithms import utils as MLUtils


import time

class LinearRegression:
    LABEL_COLUMN_NAME = 'label'
    FEATURES_COLUMN_NAME = 'features'

    MAX_ITERATIONS = 5
    REGULARIZATION_PARAM = 0.1

    def __init__(self, data_frame, df_helper, df_context, meta_parser,spark):
        self._data_frame = data_frame
        self._dataframe_helper = df_helper
        self._dataframe_context = df_context
        self._metaParser = meta_parser
        self._spark = spark

        self._ignoreRegressionElasticityMessages = self._dataframe_context.get_ignore_msg_regression_elasticity()
        self._completionStatus = self._dataframe_context.get_completion_status()
        self._analysisName = self._dataframe_context.get_analysis_name()
        self._analysisDict = self._dataframe_context.get_analysis_dict()
        self._messageURL = self._dataframe_context.get_message_url()
        self._scriptWeightDict = self._dataframe_context.get_measure_analysis_weight()
        self._scriptStages = {
            "regressionTrainingStart":{
                "summary":"Started the Regression Script",
                "weight":0
                },
            "regressionTrainingEnd":{
                "summary":"Regression coefficients calculated",
                "weight":10
                },
            }
        progressMessage = CommonUtils.create_progress_message_object(self._analysisName,\
                                    "regressionTrainingStart",\
                                    "info",\
                                    self._scriptStages["regressionTrainingStart"]["summary"],\
                                    self._completionStatus,\
                                    self._completionStatus)
        if self._ignoreRegressionElasticityMessages != True:
            CommonUtils.save_progress_message(self._messageURL,progressMessage,ignore = self._ignoreRegressionElasticityMessages)
            self._dataframe_context.update_completion_status(self._completionStatus)

        self._data_frame = self._dataframe_helper.fill_missing_values(self._data_frame)

    def fit_all(self):
        """
        Performs one vs all-other measures regression fit
        :return:
        """
        if len(self._measure_columns) <= 1:
            return None

        df_regression_result = DFRegressionResult()
        measure_columns = set(self._measure_columns)
        for output_column in measure_columns:
            input_columns = list(measure_columns - {output_column})
            regression_result = self.fit(output_column, input_columns)
            if regression_result != None:
                df_regression_result.add_regression_result(regression_result)

        return df_regression_result

    def fit(self, output_column, input_columns=None):
        print "linear regression fit started"
        if output_column not in self._dataframe_helper.get_numeric_columns():
            raise BIException('Output column: %s is not a measure column' % (output_column,))

        if input_columns == None:
            input_columns = list(set(self._dataframe_helper.get_numeric_columns()) - {output_column})

        nColsToUse = self._analysisDict[self._analysisName]["noOfColumnsToUse"]
        if nColsToUse != None:
            input_columns = input_columns[:nColsToUse]
        if len(set(input_columns) - set(self._dataframe_helper.get_numeric_columns())) != 0:
            raise BIException('At least one of the input columns %r is not a measure column' % (input_columns,))

        all_measures = input_columns+[output_column]
        print all_measures
        measureDf = self._data_frame.select(all_measures)
        lr = LR(maxIter=LinearRegression.MAX_ITERATIONS, regParam=LinearRegression.REGULARIZATION_PARAM,
                elasticNetParam=1.0, labelCol=LinearRegression.LABEL_COLUMN_NAME,
                featuresCol=LinearRegression.FEATURES_COLUMN_NAME)

        st = time.time()
        pipeline = MLUtils.create_pyspark_ml_pipeline(input_columns,[],output_column)
        pipelineModel = pipeline.fit(measureDf)
        training_df = pipelineModel.transform(measureDf)
        training_df = training_df.withColumn("label",training_df[output_column])
        print "time taken to create training_df",time.time()-st
        # st = time.time()
        # training_df.cache()
        # print "caching in ",time.time()-st
        st = time.time()
        lr_model = lr.fit(training_df)
        lr_summary = lr_model.evaluate(training_df)
        print "lr model summary", time.time()-st
        sample_data_dict = {}
        for input_col in input_columns:
            sample_data_dict[input_col] = None

        coefficients = [float(val) if val != None else None for val in lr_model.coefficients.values]
        try:
            p_values = [float(val) if val != None else None for val in lr_model.summary.pValues]
        except:
            p_values = [None]*len(coefficients)
        # print p_values
        # print coefficients
        regression_result = RegressionResult(output_column, list(set(input_columns)))
        regression_result.set_params(intercept=float(lr_model.intercept),\
                                     coefficients=coefficients,\
                                     p_values = p_values,\
                                     rmse=float(lr_summary.rootMeanSquaredError), \
                                     r2=float(lr_summary.r2),\
                                     sample_data_dict=sample_data_dict)

        self._completionStatus = self._dataframe_context.get_completion_status()
        self._completionStatus += self._scriptWeightDict[self._analysisName]["script"]
        progressMessage = CommonUtils.create_progress_message_object(self._analysisName,\
                                    "regressionTrainingEnd",\
                                    "info",\
                                    self._scriptStages["regressionTrainingEnd"]["summary"],\
                                    self._completionStatus,\
                                    self._completionStatus)
        if self._ignoreRegressionElasticityMessages != True:
            CommonUtils.save_progress_message(self._messageURL,progressMessage,ignore = self._ignoreRegressionElasticityMessages)
            self._dataframe_context.update_completion_status(self._completionStatus)

        return regression_result
