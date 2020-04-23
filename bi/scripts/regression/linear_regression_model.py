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

from bi.common import MLModelSummary,NormalCard,KpiData,C3ChartData,HtmlData,SklearnGridSearchResult,SkleanrKFoldResult
from bi.common import NormalChartData, ChartJson


from bi.stats.frequency_dimensions import FreqDimensions
from bi.narratives.dimension.dimension_column import DimensionColumnNarrative
from bi.stats.chisquare import ChiSquare
from bi.narratives.chisquare import ChiSquareNarratives

from pyspark.sql.functions import udf
from pyspark.sql import functions as FN
from pyspark.sql.types import *
from pyspark.ml.regression import LinearRegression
from pyspark.ml.feature import IndexToString
from pyspark.ml.tuning import ParamGridBuilder, TrainValidationSplit,CrossValidator
from pyspark.ml.evaluation import RegressionEvaluator

from bi.settings import setting as GLOBALSETTINGS
from bi.algorithms import DecisionTrees
from bi.narratives.decisiontree.decision_tree import DecisionTreeNarrative
from bi.scripts.measureAnalysis.descr_stats import DescriptiveStatsScript
from bi.scripts.measureAnalysis.two_way_anova import TwoWayAnovaScript
from bi.scripts.measureAnalysis.decision_tree_regression import DecisionTreeRegressionScript

from sklearn.metrics import mean_absolute_error
from sklearn.metrics import mean_squared_error
from sklearn.metrics import r2_score
from math import sqrt
import pandas as pd
import numpy as np
from sklearn.externals import joblib
from sklearn2pmml import sklearn2pmml
from sklearn2pmml import PMMLPipeline

from sklearn.linear_model import LinearRegression
from sklearn.model_selection import KFold
from sklearn.model_selection import GridSearchCV
from sklearn.model_selection import RandomizedSearchCV




class LinearRegressionModelScript:
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
        self._slug = GLOBALSETTINGS.MODEL_SLUG_MAPPING["linearregression"]
        self._analysisName = "linearRegression"
        self._dataframe_context.set_analysis_name(self._analysisName)
        self._mlEnv = self._dataframe_context.get_ml_environment()

        self._completionStatus = self._dataframe_context.get_completion_status()
        print self._completionStatus,"initial completion status"
        self._messageURL = self._dataframe_context.get_message_url()
        self._scriptWeightDict = self._dataframe_context.get_ml_model_training_weight()
        self._ignoreMsg = self._dataframe_context.get_message_ignore()
        print self._scriptWeightDict
        print "="*400

        self._scriptStages = {
            "initialization":{
                "summary":"Initialized the Linear Regression Scripts",
                "weight":4
                },
            "training":{
                "summary":"Linear Regression Model Training Started",
                "weight":2
                },
            "completion":{
                "summary":"Linear Regression Model Training Finished",
                "weight":4
                },
            }


    def Train(self):
        st_global = time.time()
        CommonUtils.create_update_and_save_progress_message(self._dataframe_context,self._scriptWeightDict,self._scriptStages,self._slug,"initialization","info",display=True,emptyBin=False,customMsg=None,weightKey="total")

        appType = self._dataframe_context.get_app_type()
        algosToRun = self._dataframe_context.get_algorithms_to_run()
        algoSetting = filter(lambda x:x.get_algorithm_slug()==self._slug,algosToRun)[0]
        categorical_columns = self._dataframe_helper.get_string_columns()
        uid_col = self._dataframe_context.get_uid_column()
        if self._metaParser.check_column_isin_ignored_suggestion(uid_col):
            categorical_columns = list(set(categorical_columns) - {uid_col})
        allDateCols = self._dataframe_context.get_date_columns()
        categorical_columns = list(set(categorical_columns)-set(allDateCols))
        result_column = self._dataframe_context.get_result_column()
        numerical_columns = self._dataframe_helper.get_numeric_columns()
        numerical_columns = [x for x in numerical_columns if x != result_column]
        print "categorical_columns",categorical_columns

        model_path = self._dataframe_context.get_model_path()
        if model_path.startswith("file"):
            model_path = model_path[7:]
        validationDict = self._dataframe_context.get_validation_dict()
        print "model_path",model_path
        pipeline_filepath = "file://"+str(model_path)+"/"+str(self._slug)+"/pipeline/"
        model_filepath = "file://"+str(model_path)+"/"+str(self._slug)+"/model"
        pmml_filepath = "file://"+str(model_path)+"/"+str(self._slug)+"/modelPmml"

        df = self._data_frame
        if self._mlEnv == "spark":
            pipeline = MLUtils.create_pyspark_ml_pipeline(numerical_columns,categorical_columns,result_column,algoType="regression")

            pipelineModel = pipeline.fit(df)
            indexed = pipelineModel.transform(df)
            featureMapping = sorted((attr["idx"], attr["name"]) for attr in (chain(*indexed.schema["features"].metadata["ml_attr"]["attrs"].values())))

            # print indexed.select([result_column,"features"]).show(5)
            MLUtils.save_pipeline_or_model(pipelineModel,pipeline_filepath)
            linr = LinearRegression(labelCol=result_column, featuresCol='features',predictionCol="prediction",maxIter=10, regParam=0.3, elasticNetParam=0.8)
            if validationDict["name"] == "kFold":
                defaultSplit = GLOBALSETTINGS.DEFAULT_VALIDATION_OBJECT["value"]
                numFold = int(validationDict["value"])
                if numFold == 0:
                    numFold = 3
                trainingData,validationData = indexed.randomSplit([defaultSplit,1-defaultSplit], seed=12345)
                paramGrid = ParamGridBuilder()\
                    .addGrid(linr.regParam, [0.1, 0.01]) \
                    .addGrid(linr.fitIntercept, [False, True])\
                    .addGrid(linr.elasticNetParam, [0.0, 0.5, 1.0])\
                    .build()
                crossval = CrossValidator(estimator=linr,
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
                fit = linr.fit(trainingData)
                trainingTime = time.time()-st
                print "time to train",trainingTime
                bestModel = fit
            print bestModel.explainParams()
            print bestModel.extractParamMap()
            print bestModel.params
            print 'Best Param (regParam): ', bestModel._java_obj.getRegParam()
            print 'Best Param (MaxIter): ', bestModel._java_obj.getMaxIter()
            print 'Best Param (elasticNetParam): ', bestModel._java_obj.getElasticNetParam()

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
            self._model_summary.set_model_type("regression")
            self._model_summary.set_algorithm_name("Linear Regression")
            self._model_summary.set_algorithm_display_name("Linear Regression")
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
            # print CommonUtils.convert_python_object_to_json(self._model_summary)
        elif self._mlEnv == "sklearn":
            model_filepath = model_path+"/"+self._slug+"/model.pkl"
            x_train,x_test,y_train,y_test = self._dataframe_helper.get_train_test_data()
            x_train = MLUtils.create_dummy_columns(x_train,[x for x in categorical_columns if x != result_column])
            x_test = MLUtils.create_dummy_columns(x_test,[x for x in categorical_columns if x != result_column])
            x_test = MLUtils.fill_missing_columns(x_test,x_train.columns,result_column)
            # x_train.to_csv("/home/gulshan/marlabs/datasets/lrTest/x_train.csv",index=False)
            # x_test.to_csv("/home/gulshan/marlabs/datasets/lrTest/x_test.csv",index=False)
            # y_train.to_csv("/home/gulshan/marlabs/datasets/lrTest/y_train.csv",index=False)
            # y_test.to_csv("/home/gulshan/marlabs/datasets/lrTest/y_test.csv",index=False)

            # print "features before VIF-"*100
            # print x_train.columns.tolist()
            # print len(x_train.columns)

            ############# Uncomment following part if you want to use VIF feature selection #############
            ######################## VIF feature slection block of code ########################

            # x_train_new = MLUtils.feature_selection_vif(x_train)
            # x_test_new =x_test[x_train_new.columns.tolist()]

            # print "features after VIF-"*100
            # print x_test_new.columns.tolist()
            # print len(x_test_new.columns)

            # x_train = x_train_new
            # x_test = x_test_new

            ######################## VIF feature slection block of code ########################

            st = time.time()
            est = LinearRegression()

            CommonUtils.create_update_and_save_progress_message(self._dataframe_context,self._scriptWeightDict,self._scriptStages,self._slug,"training","info",display=True,emptyBin=False,customMsg=None,weightKey="total")

            self._dataframe_context.update_completion_status(self._completionStatus)
            if algoSetting.is_hyperparameter_tuning_enabled():
                hyperParamInitParam = algoSetting.get_hyperparameter_params()
                evaluationMetricDict = {"name":hyperParamInitParam["evaluationMetric"]}
                evaluationMetricDict["displayName"] = GLOBALSETTINGS.SKLEARN_EVAL_METRIC_NAME_DISPLAY_MAP[evaluationMetricDict["name"]]
                hyperParamAlgoName = algoSetting.get_hyperparameter_algo_name()
                params_grid = algoSetting.get_params_dict_hyperparameter()
                params_grid = {k:v for k,v in params_grid.items() if k in est.get_params()}
                print params_grid
                if hyperParamAlgoName == "gridsearchcv":
                    estGrid = GridSearchCV(est,params_grid)
                    gridParams = estGrid.get_params()
                    hyperParamInitParam = {k:v for k,v in hyperParamInitParam.items() if k in gridParams}
                    estGrid.set_params(**hyperParamInitParam)
                    estGrid.fit(x_train,y_train)
                    bestEstimator = estGrid.best_estimator_
                    modelFilepath = "/".join(model_filepath.split("/")[:-1])
                    sklearnHyperParameterResultObj = SklearnGridSearchResult(estGrid.cv_results_,est,x_train,x_test,y_train,y_test,appType,modelFilepath,evaluationMetricDict=evaluationMetricDict)
                    resultArray = sklearnHyperParameterResultObj.train_and_save_models()
                    self._result_setter.set_hyper_parameter_results(self._slug,resultArray)
                    self._result_setter.set_metadata_parallel_coordinates(self._slug,{"ignoreList":sklearnHyperParameterResultObj.get_ignore_list(),"hideColumns":sklearnHyperParameterResultObj.get_hide_columns(),"metricColName":sklearnHyperParameterResultObj.get_comparison_metric_colname(),"columnOrder":sklearnHyperParameterResultObj.get_keep_columns()})
                elif hyperParamAlgoName == "randomsearchcv":
                    estRand = RandomizedSearchCV(est,params_grid)
                    estRand.set_params(**hyperParamInitParam)
                    bestEstimator = None
            else:
                evaluationMetricDict = {"name":GLOBALSETTINGS.REGRESSION_MODEL_EVALUATION_METRIC}
                evaluationMetricDict["displayName"] = GLOBALSETTINGS.SKLEARN_EVAL_METRIC_NAME_DISPLAY_MAP[evaluationMetricDict["name"]]
                algoParams = algoSetting.get_params_dict()
                algoParams = {k:v for k,v in algoParams.items() if k in est.get_params().keys()}
                est.set_params(**algoParams)
                self._result_setter.set_hyper_parameter_results(self._slug,None)
                if validationDict["name"] == "kFold":
                    defaultSplit = GLOBALSETTINGS.DEFAULT_VALIDATION_OBJECT["value"]
                    numFold = int(validationDict["value"])
                    if numFold == 0:
                        numFold = 3
                    kFoldClass = SkleanrKFoldResult(numFold,est,x_train,x_test,y_train,y_test,appType,evaluationMetricDict=evaluationMetricDict)
                    kFoldClass.train_and_save_result()
                    kFoldOutput = kFoldClass.get_kfold_result()
                    bestEstimator = kFoldClass.get_best_estimator()
                elif validationDict["name"] == "trainAndtest":
                    est.fit(x_train, y_train)
                    bestEstimator = est
            # print x_train.columns
            trainingTime = time.time()-st
            y_score = bestEstimator.predict(x_test)
            try:
                y_prob = bestEstimator.predict_proba(x_test)
            except:
                y_prob = [0]*len(y_score)
            featureImportance={}

            objs = {"trained_model":bestEstimator,"actual":y_test,"predicted":y_score,"probability":y_prob,"feature_importance":featureImportance,"featureList":list(x_train.columns),"labelMapping":{}}
            coefficients = objs["trained_model"].coef_
            coefficientsArray = [(col_name, coefficients[idx]) for idx, col_name in enumerate(x_train.columns)]
            interceptValue = None
            interceptValue = objs["trained_model"].intercept_

            if not algoSetting.is_hyperparameter_tuning_enabled():
                modelName = "M"+"0"*(GLOBALSETTINGS.MODEL_NAME_MAX_LENGTH-1)+"1"
                modelFilepathArr = model_filepath.split("/")[:-1]
                modelFilepathArr.append(modelName+".pkl")
                joblib.dump(objs["trained_model"],"/".join(modelFilepathArr))
            metrics = {}
            metrics["r2"] = r2_score(y_test, y_score)
            metrics["mse"] = mean_squared_error(y_test, y_score)
            metrics["mae"] = mean_absolute_error(y_test, y_score)
            metrics["rmse"] = sqrt(metrics["mse"])
            transformed = pd.DataFrame({"prediction":y_score,result_column:y_test})
            transformed["difference"] = transformed[result_column] - transformed["prediction"]
            transformed["mape"] = np.abs(transformed["difference"])*100/transformed[result_column]

            sampleData = None
            nrows = transformed.shape[0]
            if nrows > 100:
                sampleData = transformed.sample(n=100,random_state=420)
            else:
                sampleData = transformed
            print sampleData.head()

            mapeCountArr = pd.cut(transformed["mape"],GLOBALSETTINGS.MAPEBINS).value_counts().to_dict().items()
            mapeStatsArr = [(str(idx),dictObj) for idx,dictObj in enumerate(sorted([{"count":x[1],"splitRange":(x[0].left,x[0].right)} for x in mapeCountArr],key = lambda x:x["splitRange"][0]))]

            predictionColSummary = transformed["prediction"].describe().to_dict()
            quantileBins = [predictionColSummary["min"],predictionColSummary["25%"],predictionColSummary["50%"],predictionColSummary["75%"],predictionColSummary["max"]]
            quantileBins = sorted(list(set(quantileBins)))
            transformed["quantileBinId"] = pd.cut(transformed["prediction"],quantileBins)
            quantileDf = transformed.groupby("quantileBinId").agg({"prediction":[np.sum,np.mean,np.size]}).reset_index()
            quantileDf.columns = ["prediction","sum","mean","count"]
            quantileArr = quantileDf.T.to_dict().items()
            quantileSummaryArr = [(obj[0],{"splitRange":(obj[1]["prediction"].left,obj[1]["prediction"].right),"count":obj[1]["count"],"mean":obj[1]["mean"],"sum":obj[1]["sum"]}) for obj in quantileArr]
            runtime = round((time.time() - st_global),2)

            self._model_summary.set_model_type("regression")
            self._model_summary.set_algorithm_name("Linear Regression")
            self._model_summary.set_algorithm_display_name("Linear Regression")
            self._model_summary.set_slug(self._slug)
            self._model_summary.set_training_time(runtime)
            self._model_summary.set_training_time(trainingTime)
            self._model_summary.set_target_variable(result_column)
            self._model_summary.set_validation_method(validationDict["displayName"])
            self._model_summary.set_model_evaluation_metrics(metrics)
            self._model_summary.set_model_params(bestEstimator.get_params())
            self._model_summary.set_quantile_summary(quantileSummaryArr)
            self._model_summary.set_mape_stats(mapeStatsArr)
            self._model_summary.set_sample_data(sampleData.to_dict())
            self._model_summary.set_feature_importance(featureImportance)
            self._model_summary.set_feature_list(list(x_train.columns))
            self._model_summary.set_coefficinets_array(coefficientsArray)
            self._model_summary.set_intercept(interceptValue)

            try:
                pmml_filepath = str(model_path)+"/"+str(self._slug)+"/traindeModel.pmml"
                modelPmmlPipeline = PMMLPipeline([
                  ("pretrained-estimator", objs["trained_model"])
                ])
                modelPmmlPipeline.target_field = result_column
                modelPmmlPipeline.active_fields = np.array([col for col in x_train.columns if col != result_column])
                sklearn2pmml(modelPmmlPipeline, pmml_filepath, with_repr = True)
                pmmlfile = open(pmml_filepath,"r")
                pmmlText = pmmlfile.read()
                pmmlfile.close()
                self._result_setter.update_pmml_object({self._slug:pmmlText})
            except:
                pass
        if not algoSetting.is_hyperparameter_tuning_enabled():
            modelDropDownObj = {
                        "name":self._model_summary.get_algorithm_name(),
                        "evaluationMetricValue":self._model_summary.get_model_accuracy(),
                        "evaluationMetricName":"r2",
                        "slug":self._model_summary.get_slug(),
                        "Model Id":modelName
                        }

            modelSummaryJson = {
                "dropdown":modelDropDownObj,
                "levelcount":self._model_summary.get_level_counts(),
                "modelFeatureList":self._model_summary.get_feature_list(),
                "levelMapping":self._model_summary.get_level_map_dict(),
                "slug":self._model_summary.get_slug(),
                "name":self._model_summary.get_algorithm_name()
            }
        else:
            modelDropDownObj = {
                        "name":self._model_summary.get_algorithm_name(),
                        "evaluationMetricValue":resultArray[0]["R-Squared"],
                        "evaluationMetricName":"r2",
                        "slug":self._model_summary.get_slug(),
                        "Model Id":resultArray[0]["Model Id"]
                        }
            modelSummaryJson = {
                "dropdown":modelDropDownObj,
                "levelcount":self._model_summary.get_level_counts(),
                "modelFeatureList":self._model_summary.get_feature_list(),
                "levelMapping":self._model_summary.get_level_map_dict(),
                "slug":self._model_summary.get_slug(),
                "name":self._model_summary.get_algorithm_name()
            }

        linrCards = [json.loads(CommonUtils.convert_python_object_to_json(cardObj)) for cardObj in MLUtils.create_model_summary_cards(self._model_summary)]

        for card in linrCards:
            self._prediction_narrative.add_a_card(card)
        self._result_setter.set_model_summary({"linearregression":json.loads(CommonUtils.convert_python_object_to_json(self._model_summary))})
        self._result_setter.set_linear_regression_model_summary(modelSummaryJson)
        self._result_setter.set_linr_cards(linrCards)

        CommonUtils.create_update_and_save_progress_message(self._dataframe_context,self._scriptWeightDict,self._scriptStages,self._slug,"completion","info",display=True,emptyBin=False,customMsg=None,weightKey="total")


    def Predict(self):
        self._scriptWeightDict = self._dataframe_context.get_ml_model_prediction_weight()
        self._scriptStages = {
            "initialization":{
                "summary":"Initialized the Linear Regression Scripts",
                "weight":2
                },
            "predictionStart":{
                "summary":"Linear Regression Model Prediction Started",
                "weight":2
                },
            "predictionFinished":{
                "summary":"Linear Regression Model Prediction Finished",
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
        targetVariable = result_column

        if self._mlEnv == "spark":
            score_data_path = self._dataframe_context.get_score_path()+"/data.csv"
            trained_model_path = "file://" + self._dataframe_context.get_model_path()
            trained_model_path += "/model"
            pipeline_path = "/".join(trained_model_path.split("/")[:-1])+"/pipeline"
            print "trained_model_path",trained_model_path
            print "pipeline_path",pipeline_path
            print "score_data_path",score_data_path
            pipelineModel = MLUtils.load_pipeline(pipeline_path)
            trained_model = MLUtils.load_linear_regresssion_pyspark_model(trained_model_path)
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
        elif self._mlEnv == "sklearn":
            CommonUtils.create_update_and_save_progress_message(self._dataframe_context,self._scriptWeightDict,self._scriptStages,self._slug,"predictionStart","info",display=True,emptyBin=False,customMsg=None,weightKey="total")

            score_data_path = self._dataframe_context.get_score_path()+"/data.csv"
            trained_model_path = "file://" + self._dataframe_context.get_model_path()
            trained_model_path += "/"+self._dataframe_context.get_model_for_scoring()+".pkl"
            print "trained_model_path",trained_model_path
            print "score_data_path",score_data_path
            if trained_model_path.startswith("file"):
                trained_model_path = trained_model_path[7:]
            trained_model = joblib.load(trained_model_path)
            model_columns = self._dataframe_context.get_model_features()
            # print "model_columns",model_columns

            df = self._data_frame.toPandas()
            # pandas_df = MLUtils.factorize_columns(df,[x for x in categorical_columns if x != result_column])
            pandas_df = MLUtils.create_dummy_columns(df,[x for x in categorical_columns if x != result_column])
            pandas_df = MLUtils.fill_missing_columns(pandas_df,model_columns,result_column)
            if uid_col:
                pandas_df = pandas_df[[x for x in pandas_df.columns if x != uid_col]]
            print len(model_columns),len(pandas_df.columns)
            y_score = trained_model.predict(pandas_df)
            coefficients = trained_model.coef_
            coefficientsArray = [(col_name, coefficients[idx]) for idx, col_name in enumerate(pandas_df.columns)]

            coefficientsCard = NormalCard()
            coefficientsArray = sorted(coefficientsArray,key=lambda x:abs(x[1]),reverse=True)
            coefficientsArray = [{"key":tup[0],"value":tup[1]} for tup in coefficientsArray]
            coefficientsArray = MLUtils.normalize_coefficients(coefficientsArray)
            chartDataValues = [x["value"] for x in coefficientsArray]
            coefficientsChartJson = ChartJson()
            coefficientsChartJson.set_data(coefficientsArray)
            coefficientsChartJson.set_chart_type("bar")
            coefficientsChartJson.set_label_text({'x':' ','y':'Coefficients'})
            coefficientsChartJson.set_axes({"x":"key","y":"value"})
            # coefficientsChartJson.set_title("Influence of Key Features on {}".format(targetVariable))
            # coefficientsChartJson.set_yaxis_number_format(".4f")
            coefficientsChartJson.set_yaxis_number_format(CommonUtils.select_y_axis_format(chartDataValues))
            coefficientsChart = C3ChartData(data=coefficientsChartJson)
            coefficientsCardData = [HtmlData(data="<h4>Influence of Key Features on {}</h4>".format(targetVariable)),coefficientsChart]
            coefficientsCard.set_card_data(coefficientsCardData)
            coefficientsCard = json.loads(CommonUtils.convert_python_object_to_json(coefficientsCard))
            self._result_setter.set_coeff_card_regression_score(coefficientsCard)

            scoreKpiArray = MLUtils.get_scored_data_summary(y_score)
            kpiCard = NormalCard()
            kpiCardData = [KpiData(data=x) for x in scoreKpiArray]
            kpiCard.set_card_data(kpiCardData)
            kpiCard.set_cente_alignment(True)
            print CommonUtils.convert_python_object_to_json(kpiCard)
            self._result_setter.set_kpi_card_regression_score(kpiCard)

            pandas_df[result_column] = y_score
            df[result_column] = y_score
            df.to_csv(score_data_path,header=True,index=False)
            CommonUtils.create_update_and_save_progress_message(self._dataframe_context,self._scriptWeightDict,self._scriptStages,self._slug,"predictionFinished","info",display=True,emptyBin=False,customMsg=None,weightKey="total")


            print df.columns
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
            pandas_scored_df = df[list(set(columns_to_keep+[result_column]))]
            spark_scored_df = SQLctx.createDataFrame(pandas_scored_df)
            # spark_scored_df.write.csv(score_data_path+"/data",mode="overwrite",header=True)
            # TODO update metadata for the newly created dataframe
            self._dataframe_context.update_consider_columns(columns_to_keep)
            print spark_scored_df.printSchema()

        df_helper = DataFrameHelper(spark_scored_df, self._dataframe_context,self._metaParser)
        df_helper.set_params()
        df = df_helper.get_data_frame()
        try:
            fs = time.time()
            descr_stats_obj = DescriptiveStatsScript(df, df_helper, self._dataframe_context, self._result_setter, self._spark,self._prediction_narrative,scriptWeight=self._scriptWeightDict,analysisName="Descriptive analysis")
            descr_stats_obj.Run()
            print "DescriptiveStats Analysis Done in ", time.time() - fs, " seconds."
        except:
            print "DescriptiveStats Analysis Failed "

        # try:
        #     fs = time.time()
        #     df_helper.fill_na_dimension_nulls()
        #     df = df_helper.get_data_frame()
        #     dt_reg = DecisionTreeRegressionScript(df, df_helper, self._dataframe_context, self._result_setter, self._spark,self._prediction_narrative,self._metaParser,scriptWeight=self._scriptWeightDict,analysisName="Predictive modeling")
        #     dt_reg.Run()
        #     print "DecisionTrees Analysis Done in ", time.time() - fs, " seconds."
        # except:
        #     print "DTREE FAILED"
        #
        # try:
        fs = time.time()
        two_way_obj = TwoWayAnovaScript(df, df_helper, self._dataframe_context, self._result_setter, self._spark,self._prediction_narrative,self._metaParser,scriptWeight=self._scriptWeightDict,analysisName="Measure vs. Dimension")
        two_way_obj.Run()
        print "OneWayAnova Analysis Done in ", time.time() - fs, " seconds."
        # except:
        #     print "Anova Analysis Failed"



        progressMessage = CommonUtils.create_progress_message_object("Measure analysis","custom","info","Score Summary Finished",100,100,display=True)
        CommonUtils.save_progress_message(self._messageURL,progressMessage,ignore=False)
