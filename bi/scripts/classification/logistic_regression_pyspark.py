import json
import time

try:
    import cPickle as pickle
except:
    import pickle

from pyspark.sql import SQLContext
from bi.common import utils as CommonUtils
from bi.algorithms import utils as MLUtils
from bi.common import DataFrameHelper
from bi.stats.frequency_dimensions import FreqDimensions
from bi.narratives.dimension.dimension_column import DimensionColumnNarrative
from bi.stats.chisquare import ChiSquare
from bi.narratives.chisquare import ChiSquareNarratives
from pyspark.ml.evaluation import BinaryClassificationEvaluator
from pyspark.ml.feature import IndexToString
from pyspark.sql.functions import udf
from pyspark.sql.types import *

from pyspark.ml.classification import LogisticRegression, OneVsRest
from pyspark.ml.evaluation import MulticlassClassificationEvaluator







class LogisticRegressionPysparkScript:
    def __init__(self, data_frame, df_helper,df_context, spark):
        self._data_frame = data_frame
        self._dataframe_helper = df_helper
        self._dataframe_context = df_context
        self._spark = spark
        self._model_summary = {"confusion_matrix":{},"precision_recall_stats":{},"FrequencySummary":{},"ChiSquare":{}}
        self._score_summary = {}
        self._classifier = "lr" #lr or OneVsRest

    def Train(self):
        st = time.time()
        categorical_columns = self._dataframe_helper.get_string_columns()
        numerical_columns = self._dataframe_helper.get_numeric_columns()
        result_column = self._dataframe_context.get_result_column()
        categorical_columns = [x for x in categorical_columns if x != result_column]

        model_path = self._dataframe_context.get_model_path()
        pipeline_filepath = model_path+"/LogisticRegression/TrainedModels/pipeline"
        model_filepath = model_path+"/LogisticRegression/TrainedModels/model"
        summary_filepath = model_path+"/LogisticRegression/ModelSummary/summary.json"

        df=self._data_frame
        pipeline = MLUtils.create_pyspark_ml_pipeline(numerical_columns,categorical_columns,result_column)
        pipelineModel = pipeline.fit(df)
        indexed = pipelineModel.transform(df)
        MLUtils.save_pipeline_or_model(pipelineModel,pipeline_filepath)
        trainingData,validationData = MLUtils.get_training_and_validation_data(indexed,result_column,0.8)
        OriginalTargetconverter = IndexToString(inputCol="label", outputCol="originalTargetColumn")
        levels = trainingData.select("label").distinct().collect()

        if self._classifier == "lr":
            if len(levels) == 2:
                lr = LogisticRegression(maxIter=10, regParam=0.3, elasticNetParam=0.8)
            elif len(levels) > 2:
                lr = LogisticRegression(maxIter=10, regParam=0.3, elasticNetParam=0.8,family="multinomial")
            fit = lr.fit(trainingData)
        elif self._classifier == "OneVsRest":
            lr = LogisticRegression()
            ovr = OneVsRest(classifier=lr)
            fit = ovr.fit(trainingData)
        transformed = fit.transform(validationData)
        MLUtils.save_pipeline_or_model(fit,model_filepath)

        print fit.coefficientMatrix
        print fit.interceptVector

        # feature_importance = MLUtils.calculate_sparkml_feature_importance(indexed,fit,categorical_columns,numerical_columns)
        label_classes = transformed.select("label").distinct().collect()
        results = transformed.select(["prediction","label"])
        if len(label_classes) > 2:
            evaluator = MulticlassClassificationEvaluator(predictionCol="prediction")
            evaluator.evaluate(results)
            self._model_summary["model_accuracy"] = evaluator.evaluate(results,{evaluator.metricName: "accuracy"}) # accuracy of the model
        else:
            evaluator = BinaryClassificationEvaluator(rawPredictionCol="prediction")
            evaluator.evaluate(results)
            # print evaluator.evaluate(results,{evaluator.metricName: "areaUnderROC"})
            # print evaluator.evaluate(results,{evaluator.metricName: "areaUnderPR"})
            self._model_summary["model_accuracy"] = evaluator.evaluate(results,{evaluator.metricName: "areaUnderPR"}) # accuracy of the model


        # self._model_summary["feature_importance"] = MLUtils.transform_feature_importance(feature_importance)
        self._model_summary["runtime_in_seconds"] = round((time.time() - st),2)

        transformed = OriginalTargetconverter.transform(transformed)
        label_indexer_dict = [dict(enumerate(field.metadata["ml_attr"]["vals"])) for field in transformed.schema.fields if field.name == "label"][0]
        prediction_to_levels = udf(lambda x:label_indexer_dict[x],StringType())
        transformed = transformed.withColumn("predictedClass",prediction_to_levels(transformed.prediction))
        prediction_df = transformed.select(["originalTargetColumn","predictedClass"]).toPandas()
        objs = {"actual":prediction_df["originalTargetColumn"],"predicted":prediction_df["predictedClass"]}

        self._model_summary["confusion_matrix"] = MLUtils.calculate_confusion_matrix(objs["actual"],objs["predicted"])
        overall_precision_recall = MLUtils.calculate_overall_precision_recall(objs["actual"],objs["predicted"])
        self._model_summary["precision_recall_stats"] = overall_precision_recall["classwise_stats"]
        self._model_summary["model_precision"] = overall_precision_recall["precision"]
        self._model_summary["model_recall"] = overall_precision_recall["recall"]
        self._model_summary["target_variable"] = result_column
        self._model_summary["test_sample_prediction"] = overall_precision_recall["prediction_split"]
        self._model_summary["algorithm_name"] = "Random Forest"
        self._model_summary["validation_method"] = "Train and Test"
        self._model_summary["independent_variables"] = len(categorical_columns)+len(numerical_columns)
        self._model_summary["level_counts"] = CommonUtils.get_level_count_dict(trainingData,categorical_columns,self._dataframe_context.get_column_separator(),dataType="spark")
        # print json.dumps(self._model_summary,indent=2)
        self._model_summary["total_trees"] = 100
        self._model_summary["total_rules"] = 300
        CommonUtils.write_to_file(summary_filepath,json.dumps({"modelSummary":self._model_summary}))


    def Predict(self):
        SQLctx = SQLContext(sparkContext=self._spark.sparkContext, sparkSession=self._spark)
        dataSanity = True
        level_counts_train = self._dataframe_context.get_level_count_dict()
        categorical_columns = self._dataframe_helper.get_string_columns()
        numerical_columns = self._dataframe_helper.get_numeric_columns()
        time_dimension_columns = self._dataframe_helper.get_timestamp_columns()
        result_column = self._dataframe_context.get_result_column()
        categorical_columns = [x for x in categorical_columns if x != result_column]

        level_counts_score = CommonUtils.get_level_count_dict(self._data_frame,categorical_columns,self._dataframe_context.get_column_separator(),output_type="dict",dataType="spark")
        for key in level_counts_train:
            if key in level_counts_score:
                if level_counts_train[key] != level_counts_score[key]:
                    dataSanity = False
            else:
                dataSanity = False

        test_data_path = self._dataframe_context.get_input_file()
        score_data_path = self._dataframe_context.get_score_path()+"/ScoredData/data.csv"
        trained_model_path = self._dataframe_context.get_model_path()
        if trained_model_path.endswith(".pkl"):
            trained_model_path = "/".join(trained_model_path.split("/")[:-1])+"/model"
        pipeline_path = "/".join(trained_model_path.split("/")[:-1])+"/pipeline"
        score_summary_path = self._dataframe_context.get_score_path()+"/Summary/summary.json"

        pipelineModel = MLUtils.load_pipeline(pipeline_path)
        if self._classifier == "OneVsRest":
            trained_model = MLUtils.load_one_vs_rest_model(trained_model_path)
        elif self._classifier == "lr":
            trained_model = MLUtils.load_logistic_model(trained_model_path)

        df = self._data_frame
        indexed = pipelineModel.transform(df)
        transformed = trained_model.transform(indexed)
        label_indexer_dict = MLUtils.read_string_indexer_mapping(pipeline_path,SQLctx)
        prediction_to_levels = udf(lambda x:label_indexer_dict[x],StringType())
        transformed = transformed.withColumn(result_column,prediction_to_levels(transformed.prediction))

        # udf_to_calculate_probability = udf(lambda x:max(x[0]))
        # transformed = transformed.withColumn("predicted_probability",udf_to_calculate_probability(transformed.probability))
        # print transformed.select("predicted_probability").show(5)

        if "probability" in transformed.columns:
            probability_dataframe = transformed.select([result_column,"probability"]).toPandas()
            probability_dataframe = probability_dataframe.rename(index=str, columns={result_column: "predicted_class"})
            probability_dataframe["predicted_probability"] = probability_dataframe["probability"].apply(lambda x:max(x))
            self._score_summary["prediction_split"] = MLUtils.calculate_scored_probability_stats(probability_dataframe)
            self._score_summary["result_column"] = result_column
            scored_dataframe = transformed.select(categorical_columns+time_dimension_columns+numerical_columns+[result_column,"probability"]).toPandas()
            # scored_dataframe = scored_dataframe.rename(index=str, columns={"predicted_probability": "probability"})
        else:
            self._score_summary["prediction_split"] = []
            self._score_summary["result_column"] = result_column
            scored_dataframe = transformed.select(categorical_columns+time_dimension_columns+numerical_columns+[result_column]).toPandas()


        if score_data_path.startswith("file"):
            score_data_path = score_data_path[7:]
        scored_dataframe.to_csv(score_data_path,header=True,index=False)
        # print json.dumps({"scoreSummary":self._score_summary},indent=2)
        CommonUtils.write_to_file(score_summary_path,json.dumps({"scoreSummary":self._score_summary}))


        print "STARTING DIMENSION ANALYSIS ..."
        columns_to_keep = []
        columns_to_drop = []
        considercolumnstype = self._dataframe_context.get_score_consider_columns_type()
        considercolumns = self._dataframe_context.get_score_consider_columns()
        if considercolumnstype != None:
            if considercolumns != None:
                if considercolumnstype == ["excluding"]:
                    columns_to_drop = considercolumns
                elif considercolumnstype == ["including"]:
                    columns_to_keep = considercolumns
        if len(columns_to_keep) > 0:
            columns_to_drop = list(set(df.columns)-set(columns_to_keep))
        # spark_scored_df = transformed.select(categorical_columns+time_dimension_columns+numerical_columns+[result_column])
        scored_df = transformed.select(categorical_columns+time_dimension_columns+numerical_columns+[result_column])

        SQLctx = SQLContext(sparkContext=self._spark.sparkContext, sparkSession=self._spark)
        spark_scored_df = SQLctx.createDataFrame(scored_df.toPandas())
        columns_to_drop = [x for x in columns_to_drop if x in spark_scored_df.columns]
        modified_df = spark_scored_df.select([x for x in spark_scored_df.columns if x not in columns_to_drop])
        df_helper = DataFrameHelper(modified_df, self._dataframe_context)
        df_helper.set_params()
        df = df_helper.get_data_frame()
        try:
            fs = time.time()
            narratives_file = self._dataframe_context.get_score_path()+"/narratives/FreqDimension/data.json"
            result_file = self._dataframe_context.get_score_path()+"/results/FreqDimension/data.json"
            df_freq_dimension_obj = FreqDimensions(spark_scored_df, df_helper, self._dataframe_context).test_all(dimension_columns=[result_column])
            df_freq_dimension_result = CommonUtils.as_dict(df_freq_dimension_obj)
            CommonUtils.write_to_file(result_file,json.dumps(df_freq_dimension_result))
            narratives_obj = DimensionColumnNarrative(result_column, df_helper, self._dataframe_context, df_freq_dimension_obj)
            narratives = CommonUtils.as_dict(narratives_obj)
            CommonUtils.write_to_file(narratives_file,json.dumps(narratives))
            print "Frequency Analysis Done in ", time.time() - fs,  " seconds."
        except:
            print "Frequency Analysis Failed "

        try:
            fs = time.time()
            narratives_file = self._dataframe_context.get_score_path()+"/narratives/ChiSquare/data.json"
            result_file = self._dataframe_context.get_score_path()+"/results/ChiSquare/data.json"
            df_chisquare_obj = ChiSquare(df, df_helper, self._dataframe_context).test_all(dimension_columns= [result_column])
            df_chisquare_result = CommonUtils.as_dict(df_chisquare_obj)
            # print 'RESULT: %s' % (json.dumps(df_chisquare_result, indent=2))
            CommonUtils.write_to_file(result_file,json.dumps(df_chisquare_result))
            chisquare_narratives = CommonUtils.as_dict(ChiSquareNarratives(df_helper, df_chisquare_obj, self._dataframe_context,df))
            # print 'Narrarives: %s' %(json.dumps(chisquare_narratives, indent=2))
            CommonUtils.write_to_file(narratives_file,json.dumps(chisquare_narratives))
            print "ChiSquare Analysis Done in ", time.time() - fs, " seconds."
        except:
           print "ChiSquare Analysis Failed "
