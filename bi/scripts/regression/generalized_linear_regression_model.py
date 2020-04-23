import json
import time

try:
    import cPickle as pickle
except:
    import pickle
from itertools import chain


from pyspark.sql import SQLContext
from pyspark.sql.types import DoubleType
from bi.common import utils as CommonUtils
from bi.algorithms import utils as MLUtils
from bi.common import DataFrameHelper
from bi.common import MLModelSummary,NormalCard,KpiData,C3ChartData,HtmlData,SklearnGridSearchResult

from bi.stats.frequency_dimensions import FreqDimensions
from bi.narratives.dimension.dimension_column import DimensionColumnNarrative
from bi.stats.chisquare import ChiSquare
from bi.narratives.chisquare import ChiSquareNarratives

from pyspark.sql.functions import udf
from pyspark.sql import functions as FN
from pyspark.sql.types import *
from pyspark.ml.regression import GeneralizedLinearRegression
from pyspark.ml.feature import IndexToString
from pyspark.ml.tuning import ParamGridBuilder, TrainValidationSplit,CrossValidator
from pyspark.ml.evaluation import RegressionEvaluator

from bi.settings import setting as GLOBALSETTINGS







class GeneralizedLinearRegressionModelScript:
    def __init__(self, data_frame, df_helper,df_context, spark, prediction_narrative, result_setter,meta_parser):
        self._metaParser = meta_parser
        self._prediction_narrative = prediction_narrative
        self._result_setter = result_setter
        self._data_frame = data_frame
        self._dataframe_helper = df_helper
        self._dataframe_context = df_context
        self._spark = spark
        self._model_summary = MLModelSummary()
        self._score_summary = {}
        self._slug = GLOBALSETTINGS.MODEL_SLUG_MAPPING["generalizedlinearregression"]

    def Train(self):
        st_global = time.time()
        algosToRun = self._dataframe_context.get_algorithms_to_run()
        algoSetting = filter(lambda x:x["algorithmSlug"]==GLOBALSETTINGS.MODEL_SLUG_MAPPING["generalizedlinearregression"],algosToRun)[0]
        categorical_columns = self._dataframe_helper.get_string_columns()
        uid_col = self._dataframe_context.get_uid_column()
        if self._metaParser.check_column_isin_ignored_suggestion(uid_col):
            categorical_columns = list(set(categorical_columns) - {uid_col})
        allDateCols = self._dataframe_context.get_date_columns()
        categorical_columns = list(set(categorical_columns)-set(allDateCols))
        print categorical_columns
        result_column = self._dataframe_context.get_result_column()
        numerical_columns = self._dataframe_helper.get_numeric_columns()
        numerical_columns = [x for x in numerical_columns if x != result_column]

        model_path = self._dataframe_context.get_model_path()
        if model_path.startswith("file"):
            model_path = model_path[7:]
        validationDict = self._dataframe_context.get_validation_dict()
        print "model_path",model_path
        pipeline_filepath = "file://"+str(model_path)+"/"+str(self._slug)+"/pipeline/"
        model_filepath = "file://"+str(model_path)+"/"+str(self._slug)+"/model"
        pmml_filepath = "file://"+str(model_path)+"/"+str(self._slug)+"/modelPmml"

        df = self._data_frame
        pipeline = MLUtils.create_pyspark_ml_pipeline(numerical_columns,categorical_columns,result_column,algoType="regression")

        pipelineModel = pipeline.fit(df)
        indexed = pipelineModel.transform(df)
        featureMapping = sorted((attr["idx"], attr["name"]) for attr in (chain(*indexed.schema["features"].metadata["ml_attr"]["attrs"].values())))

        # print indexed.select([result_column,"features"]).show(5)
        MLUtils.save_pipeline_or_model(pipelineModel,pipeline_filepath)
        glinr = GeneralizedLinearRegression(labelCol=result_column, featuresCol='features',predictionCol="prediction")
        if validationDict["name"] == "kFold":
            defaultSplit = GLOBALSETTINGS.DEFAULT_VALIDATION_OBJECT["value"]
            numFold = int(validationDict["value"])
            if numFold == 0:
                numFold = 3
            trainingData,validationData = indexed.randomSplit([defaultSplit,1-defaultSplit], seed=12345)
            paramGrid = ParamGridBuilder()\
                .addGrid(glinr.regParam, [0.1, 0.01]) \
                .addGrid(glinr.fitIntercept, [False, True])\
                .build()
            crossval = CrossValidator(estimator=glinr,
                          estimatorParamMaps=paramGrid,
                          evaluator=RegressionEvaluator(predictionCol="prediction", labelCol=result_column),
                          numFolds=numFold)
            st = time.time()
            cvModel = crossval.fit(indexed)
            trainingTime = time.time()-st
            print "cvModel training takes",trainingTime
            bestModel = cvModel.bestModel
        elif validationDict["name"] == "trainAndtest":
            trainingData,validationData = indexed.randomSplit([float(validationDict["value"]),1-float(validationDict["value"])], seed=12345)
            st = time.time()
            fit = glinr.fit(trainingData)
            trainingTime = time.time()-st
            print "time to train",trainingTime
            bestModel = fit
        print bestModel.explainParams()
        print bestModel.extractParamMap()
        print bestModel.params
        print 'Best Param (regParam): ', bestModel._java_obj.getRegParam()
        print 'Best Param (MaxIter): ', bestModel._java_obj.getMaxIter()

        # modelPmmlPipeline = PMMLPipeline([
        #   ("pretrained-estimator", objs["trained_model"])
        # ])
        # try:
        #     modelPmmlPipeline.target_field = result_column
        #     modelPmmlPipeline.active_fields = np.array([col for col in x_train.columns if col != result_column])
        #     sklearn2pmml(modelPmmlPipeline, pmml_filepath, with_repr = True)
        #     pmmlfile = open(pmml_filepath,"r")
        #     pmmlText = pmmlfile.read()
        #     pmmlfile.close()
        #     self._result_setter.update_pmml_object({self._slug:pmmlText})
        # except:
        #     pass

        coefficientsArray = [(name, bestModel.coefficients[idx]) for idx, name in featureMapping]
        MLUtils.save_pipeline_or_model(bestModel,model_filepath)
        transformed = bestModel.transform(validationData)
        transformed = transformed.withColumn(result_column,transformed[result_column].cast(DoubleType()))
        transformed = transformed.select([result_column,"prediction",transformed[result_column]-transformed["prediction"]])
        transformed = transformed.withColumnRenamed(transformed.columns[-1],"difference")
        transformed = transformed.select([result_column,"prediction","difference",FN.abs(transformed["difference"])*100/transformed[result_column]])
        transformed = transformed.withColumnRenamed(transformed.columns[-1],"mape")
        sampleData = None
        nrows = transformed.count()
        if nrows > 100:
            sampleData = transformed.sample(False, float(100)/nrows, seed=420)
        else:
            sampleData = transformed
        print sampleData.show()
        evaluator = RegressionEvaluator(predictionCol="prediction",labelCol=result_column)
        metrics = {}
        metrics["r2"] = evaluator.evaluate(transformed,{evaluator.metricName: "r2"})
        metrics["rmse"] = evaluator.evaluate(transformed,{evaluator.metricName: "rmse"})
        metrics["mse"] = evaluator.evaluate(transformed,{evaluator.metricName: "mse"})
        metrics["mae"] = evaluator.evaluate(transformed,{evaluator.metricName: "mae"})
        runtime = round((time.time() - st_global),2)
        # print transformed.count()
        mapeDf = transformed.select("mape")
        # print mapeDf.show()
        mapeStats = MLUtils.get_mape_stats(mapeDf,"mape")
        mapeStatsArr = mapeStats.items()
        mapeStatsArr = sorted(mapeStatsArr,key=lambda x:int(x[0]))
        # print mapeStatsArr
        quantileDf = transformed.select("prediction")
        # print quantileDf.show()
        quantileSummaryDict = MLUtils.get_quantile_summary(quantileDf,"prediction")
        quantileSummaryArr = quantileSummaryDict.items()
        quantileSummaryArr = sorted(quantileSummaryArr,key=lambda x:int(x[0]))
        # print quantileSummaryArr
        self._model_summary.set_model_type("regression")
        self._model_summary.set_algorithm_name("Generalized Linear Regression")
        self._model_summary.set_algorithm_display_name("Generalized Linear Regression")
        self._model_summary.set_slug(self._slug)
        self._model_summary.set_training_time(runtime)
        self._model_summary.set_training_time(trainingTime)
        self._model_summary.set_target_variable(result_column)
        self._model_summary.set_validation_method(validationDict["displayName"])
        self._model_summary.set_model_evaluation_metrics(metrics)
        self._model_summary.set_model_params(bestEstimator.get_params())
        self._model_summary.set_quantile_summary(quantileSummaryArr)
        self._model_summary.set_mape_stats(mapeStatsArr)
        self._model_summary.set_sample_data(sampleData.toPandas().to_dict())
        self._model_summary.set_coefficinets_array(coefficientsArray)
        self._model_summary.set_feature_list(list(x_train.columns))

        # print CommonUtils.convert_python_object_to_json(self._model_summary)
        modelSummaryJson = {
            "dropdown":{
                        "name":self._model_summary.get_algorithm_name(),
                        "accuracy":CommonUtils.round_sig(self._model_summary.get_model_evaluation_metrics()["r2"]),
                        "slug":self._model_summary.get_slug()
                        },
            "levelcount":self._model_summary.get_level_counts(),
            "modelFeatureList":self._model_summary.get_feature_list(),
            "levelMapping":self._model_summary.get_level_map_dict()
        }

        glinrCards = [json.loads(CommonUtils.convert_python_object_to_json(cardObj)) for cardObj in MLUtils.create_model_summary_cards(self._model_summary)]

        for card in glinrCards:
            self._prediction_narrative.add_a_card(card)
        self._result_setter.set_model_summary({"generalizedlinearregression":json.loads(CommonUtils.convert_python_object_to_json(self._model_summary))})
        self._result_setter.set_generalized_linear_regression_model_summary(modelSummaryJson)
        self._result_setter.set_glinr_cards(glinrCards)

    def Predict(self):
        self._scriptWeightDict = self._dataframe_context.get_ml_model_prediction_weight()
        self._scriptStages = {
            "initialization":{
                "summary":"Initialized the Generalized Linear Regression Scripts",
                "weight":2
                },
            "predictionStart":{
                "summary":"Generalized Linear Regression Model Prediction Started",
                "weight":2
                },
            "predictionFinished":{
                "summary":"Generalized Linear Regression Model Prediction Finished",
                "weight":6
                }
            }
        CommonUtils.create_update_and_save_progress_message(self._dataframe_context,self._scriptWeightDict,self._scriptStages,self._slug,"initialization","info",display=True,emptyBin=False,customMsg=None,weightKey="total")

        SQLctx = SQLContext(sparkContext=self._spark.sparkContext, sparkSession=self._spark)
        dataSanity = True
        categorical_columns = self._dataframe_helper.get_string_columns()
        uid_col = self._dataframe_context.get_uid_column()
        if self._metaParser.check_column_isin_ignored_suggestion(uid_col):
            categorical_columns = list(set(categorical_columns) - {uid_col})
        allDateCols = self._dataframe_context.get_date_columns()
        categorical_columns = list(set(categorical_columns)-set(allDateCols))
        numerical_columns = self._dataframe_helper.get_numeric_columns()
        result_column = self._dataframe_context.get_result_column()
        test_data_path = self._dataframe_context.get_input_file()
        CommonUtils.create_update_and_save_progress_message(self._dataframe_context,self._scriptWeightDict,self._scriptStages,self._slug,"predictionStart","info",display=True,emptyBin=False,customMsg=None,weightKey="total")

        test_data_path = self._dataframe_context.get_input_file()
        score_data_path = self._dataframe_context.get_score_path()+"/data.csv"
        trained_model_path = "file://" + self._dataframe_context.get_model_path()
        trained_model_path += "/model"
        pipeline_path = "/".join(trained_model_path.split("/")[:-1])+"/pipeline"
        print "trained_model_path",trained_model_path
        print "pipeline_path",pipeline_path
        print "score_data_path",score_data_path
        pipelineModel = MLUtils.load_pipeline(pipeline_path)
        trained_model = MLUtils.load_generalized_linear_regresssion_pyspark_model(trained_model_path)
        df = self._data_frame
        indexed = pipelineModel.transform(df)
        transformed = trained_model.transform(indexed)
        if result_column in transformed.columns:
            transformed = transformed.withColumnRenamed(result_column,"originalLabel")
        transformed = transformed.withColumnRenamed("prediction",result_column)
        pandas_scored_df = transformed.select(list(set(self._data_frame.columns+[result_column]))).toPandas()
        if score_data_path.startswith("file"):
            score_data_path = score_data_path[7:]
        pandas_scored_df.to_csv(score_data_path,header=True,index=False)
        CommonUtils.create_update_and_save_progress_message(self._dataframe_context,self._scriptWeightDict,self._scriptStages,self._slug,"predictionFinished","info",display=True,emptyBin=False,customMsg=None,weightKey="total")


        print "STARTING Measure ANALYSIS ..."
        columns_to_keep = []
        columns_to_drop = []
        columns_to_keep = self._dataframe_context.get_score_consider_columns()
        if len(columns_to_keep) > 0:
            columns_to_drop = list(set(df.columns)-set(columns_to_keep))
        else:
            columns_to_drop += ["predicted_probability"]
        columns_to_drop = [x for x in columns_to_drop if x in df.columns and x != result_column]
        print "columns_to_drop",columns_to_drop
        spark_scored_df = transformed.select(list(set(columns_to_keep+[result_column])))

        df_helper = DataFrameHelper(spark_scored_df, self._dataframe_context,self._metaParser)
        df_helper.set_params()
        df = df_helper.get_data_frame()
        # self._dataframe_context.set_dont_send_message(True)
        try:
            fs = time.time()
            descr_stats_obj = DescriptiveStatsScript(df, df_helper, self._dataframe_context, self._result_setter, self._spark,self._prediction_narrative,scriptWeight=self._scriptWeightDict,analysisName="Descriptive analysis")
            descr_stats_obj.Run()
            print "DescriptiveStats Analysis Done in ", time.time() - fs, " seconds."
        except:
            print "Frequency Analysis Failed "

        try:
            fs = time.time()
            df_helper.fill_na_dimension_nulls()
            df = df_helper.get_data_frame()
            dt_reg = DecisionTreeRegressionScript(df, df_helper, self._dataframe_context, self._result_setter, self._spark,self._prediction_narrative,self._metaParser,scriptWeight=self._scriptWeightDict,analysisName="Predictive modeling")
            dt_reg.Run()
            print "DecisionTrees Analysis Done in ", time.time() - fs, " seconds."
        except:
            print "DTREE FAILED"

        try:
            fs = time.time()
            two_way_obj = TwoWayAnovaScript(df, df_helper, self._dataframe_context, self._result_setter, self._spark,self._prediction_narrative,self._metaParser,scriptWeight=self._scriptWeightDict,analysisName="Measure vs. Dimension")
            two_way_obj.Run()
            print "OneWayAnova Analysis Done in ", time.time() - fs, " seconds."
        except:
            print "Anova Analysis Failed"
