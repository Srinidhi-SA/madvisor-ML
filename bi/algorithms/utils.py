import __builtin__
import json
import os
import time
import math
import random
import shutil
import copy

import numpy as np
import pandas as pd
from sklearn import linear_model
from sklearn.metrics import mean_squared_error, r2_score
from pyspark.ml import Pipeline
from pyspark.ml.classification import RandomForestClassificationModel, OneVsRestModel, LogisticRegressionModel
from pyspark.ml.regression import LinearRegressionModel,GeneralizedLinearRegressionModel,GBTRegressionModel,DecisionTreeRegressionModel,RandomForestRegressionModel
from pyspark.ml.clustering import KMeans
from pyspark.ml.feature import Bucketizer
from pyspark.ml.feature import OneHotEncoder
from pyspark.ml.feature import StringIndexer, VectorAssembler
from pyspark.ml.pipeline import PipelineModel
from pyspark.sql import functions as FN
from pyspark.sql.functions import mean, stddev, col, sum, count
from pyspark.sql.functions import monotonically_increasing_id
from pyspark.sql.types import StringType

from pyspark.ml.regression import LinearRegression
from pyspark.ml.evaluation import RegressionEvaluator

from bi.common import NormalCard, NarrativesTree, HtmlData, C3ChartData, TableData, ModelSummary,PopupData,NormalCard,ParallelCoordinateData,DataBox,WordCloud
from bi.common import NormalChartData, ChartJson
from bi.common import utils as CommonUtils
from bi.settings import setting as GLOBALSETTINGS

def normalize_coefficients(coefficientsArray):
    valArray = [abs(obj["value"]) for obj in coefficientsArray]
    maxVal = max(valArray)
    outArray = []
    for obj in coefficientsArray:
        v = obj["value"]
        v = round(float(v)/maxVal,2)
        outArray.append({"key":obj["key"],"value":v})
    return outArray

def bucket_all_measures(df, measure_columns, dimension_columns, target_measure=None):
    if target_measure is None:
        target_measure = []
    df = df.select([col(c).cast('double').alias(c) if c in measure_columns else col(c) for c in list(set(measure_columns+dimension_columns+target_measure))])
    for measure_column in measure_columns:
        # quantile_discretizer = QuantileDiscretizer(numBuckets=4, inputCol=measure_column,
        #                                                outputCol='quantile',
        #                                                relativeError=0.01)
        # splits = quantile_discretizer.fit(df).getSplits()
        min_,max_ = df.agg(FN.min(measure_column), FN.max(measure_column)).collect()[0]
        # if len(splits)<5:
        #     diff = (max_ - min_)*1.0
        #     splits = [None,min_+diff*0.25,min_+diff*0.5,min_+diff*0.75,None]
        # print measure_column, min_, max_,splits
        # splits_new = [min_,splits[1],splits[3],max_]
        diff = (max_ - min_)*1.0
        splits_new = [min_-1,min_+diff*0.2,min_+diff*0.4,min_+diff*0.6,min_+diff*0.8,max_+1]
        bucketizer = Bucketizer(inputCol=measure_column,outputCol='bucket')
        bucketizer.setSplits(splits_new)
        df = bucketizer.transform(df)
        df = df.select([c for c in df.columns if c!=measure_column])
        df = df.select([col(c).alias(measure_column) if c=='bucket' else col(c) for c in df.columns])
    return df

def generate_random_number_array(df):
    out = [random.random() for idx in range(df.shape[0])]
    return out

def return_filtered_index(random_array,cutoff):
    id_train = []
    id_test = []
    for idx,val in enumerate(random_array):
        if val >= cutoff:
            id_test.append(idx)
        else:
            id_train.append(idx)

    return (id_train,id_test)

def drop_columns(df,drop_column_list):
    new_df = df.loc[:,[col for col in df.columns if col not in drop_column_list]]
    return new_df

def scale_columns(df,column_list):
    for val in column_list:
        norm_df = df[val]
        df[val] = (norm_df - norm_df.mean()) / (norm_df.max() - norm_df.min())

def missing_value_analysis(df,replacement_dict):
    bool_df = df.isnull()
    missing_dict = {}
    for val in bool_df.columns:
        missing_dict[val] = dict(bool_df[val].value_counts())
    missing_cols = [val for val in missing_dict.keys() if True in missing_dict[val].keys()]
    print('columns with missing value : ',missing_cols,'\n')

    if replacement_dict != {}:
        for col in missing_cols:
            if col in replacement_dict.keys():
                df[col] = df[col].apply(lambda x: replacement_dict[col] if pd.isnull(x) == True else x)
    else:
        new_dict = {}
        for col in missing_cols:
            missing_dict[col]['ratio'] = missing_dict[col][True]/sum(missing_dict[col].values())
            new_dict[col] = missing_dict[col]
        print('\n')
        return new_dict


def factorize_columns(df,cat_columns):
    df_copy = df.copy(deep=True)
    df_col = list(df.columns)
    for col in cat_columns:
        if col in df_col:
            uniq_vals = df_copy[col].unique()
            key = [idx for idx,x in enumerate(uniq_vals)]
            rep_dict = dict(zip(uniq_vals,key))
            if col != 'responded':
                df_copy[col]=df_copy[col].apply(lambda x: rep_dict[x])
            else:
                df_copy[col]=df_copy[col].apply(lambda x: 1 if x == 'yes' else 0)
            df_copy[col]=pd.factorize(df_copy[col])[0]
    return df_copy

def generate_train_test_split(df,cutoff,dependent_colname,drop_list):
    levels = df[dependent_colname].unique()
    if len(levels) > 2:
        out = generate_random_number_array(df)
        ids = return_filtered_index(out,0.7)
        df_x = df[[col for col in df.columns if col not in drop_list+[dependent_colname]]]
        x_train = df_x.iloc[ids[0],:]
        x_test = df_x.iloc[ids[1],:]
        r_response = np.array(df[dependent_colname])
        y_train = r_response[ids[0]]
        y_test = r_response[ids[1]]
    else:
        df1 = df[df[dependent_colname]==levels[0]]
        df2 = df[df[dependent_colname]==levels[1]]
        out1 = generate_random_number_array(df1)
        ids1 = return_filtered_index(out1,0.6)
        out2 = generate_random_number_array(df2)
        ids2 = return_filtered_index(out2,0.6)
        df_x1 = df1[[col for col in df.columns if col not in drop_list+[dependent_colname]]]
        x_train1 = df_x1.iloc[ids1[0],:]
        x_test1 = df_x1.iloc[ids1[1],:]
        df_x2 = df2[[col for col in df.columns if col not in drop_list+[dependent_colname]]]
        x_train2 = df_x2.iloc[ids2[0],:]
        x_test2 = df_x2.iloc[ids2[1],:]
        r_response = np.array(df[dependent_colname])
        x_train = pd.concat([x_train1,x_train2])
        x_test = pd.concat([x_test1,x_test2])
        y_train = np.concatenate((r_response[ids1[0]],r_response[ids2[0]]))
        y_test = np.concatenate((r_response[ids1[1]],r_response[ids2[1]]))
    return (x_train,x_test,y_train,y_test)

def calculate_predicted_probability(probability_array):
    out = []
    if len(probability_array[0]) > 1:
        for val in probability_array:
            out.append(__builtin__.max(val))
        return out
    else:
        return probability_array

def calculate_confusion_matrix(actual,predicted):
    """
    confusion matrix structure is defined below
    {"pred1":{"actual1":2,"actal2":3,"actual3":5},"pred2":{"actual1":5,"actal2":7,"actual3":5},"pred3":{"actual1":1,"actal2":3,"actual3":5}}
    """
    out = pd.crosstab(pd.Series(list(actual)),pd.Series(list(predicted)), rownames=['Known Class'], colnames=['Predicted Class'])
    dict_out = out.to_dict()
    actual_classes = list(set(actual))
    predicted_classes = list(set(predicted))
    total_classes = list(set(actual_classes+predicted_classes))
    dummy_dict = dict(zip(total_classes,[0]*len(total_classes)))
    for k in total_classes:
        if k not in predicted_classes:
            dict_out[k] = dummy_dict
    if len(actual_classes) < len(predicted_classes):
        for k in total_classes:
            if k not in predicted_classes:
                dict_out[k] = dummy_dict
            else:
                temp = dict_out[k]
                missing_keys = list(set(total_classes)-set(actual_classes))
                additional_data = dict(zip(missing_keys,[0]*len(missing_keys)))
                temp.update(additional_data)
                dict_out[k] = temp
    print dict_out
    return dict_out

def reformat_confusion_matrix(confusion_matrix):
    levels = confusion_matrix.keys()
    confusion_matrix_data = [[""]+levels]
    for outer in levels:
        inner_list = [outer]
        for inner in levels:
            inner_list.append(confusion_matrix[inner][outer])
        confusion_matrix_data.append(inner_list)
    return [list(x) for x in np.array(confusion_matrix_data).T]

def calculate_overall_precision_recall(actual,predicted,targetLevel = None):
    # get positive or negative class from the user
    df = pd.DataFrame({"actual":actual,"predicted":predicted})
    classes = df["actual"].unique()
    val_counts_predicted = df["predicted"].value_counts().to_dict()
    for val in classes:
        if val not in val_counts_predicted.keys():
            val_counts_predicted[val] = 0

    prediction_split = {}
    for val in val_counts_predicted.keys():
        prediction_split[val] = round(val_counts_predicted[val]*100/float(len(predicted)),2)
    val_counts = df["actual"].value_counts().to_dict()
    val_counts_tuple = tuple(val_counts.items())
    # positive_class = max(val_counts_tuple,key=lambda x:x[1])[0]
    # positive_class = __builtin__.max(val_counts,key=val_counts.get)
    if targetLevel == None:
        positive_class = __builtin__.min(val_counts,key=val_counts.get)
    else:
        positive_class = targetLevel
    print "val_counts_predicted",val_counts_predicted
    print "val_counts actual",val_counts
    print "positive_class",positive_class

    output = {"precision":0,"recall":0,"classwise_stats":None,"prediction_split":prediction_split,"positive_class":positive_class}
    if len(classes) > 2:
        class_precision_recall = calculate_precision_recall(actual,predicted)
        output["classwise_stats"] = class_precision_recall
        p = []
        r = []
        for val in class_precision_recall.keys():
            p.append(class_precision_recall[val]["precision"])
            r.append(class_precision_recall[val]["recall"])
        output["precision"] = np.mean(p)
        output["recall"] = np.mean(r)
    else:
        count_dict = {"tp":0,"fp":0,"tn":0,"fn":0}
        count_dict["tp"] = df[(df["actual"]==positive_class) & (df["predicted"]==positive_class)].shape[0]
        count_dict["fp"] = df[(df["actual"]!=positive_class) & (df["predicted"]==positive_class)].shape[0]
        count_dict["tn"] = df[(df["actual"]!=positive_class) & (df["predicted"]!=positive_class)].shape[0]
        count_dict["fn"] = df[(df["actual"]==positive_class) & (df["predicted"]!=positive_class)].shape[0]
        print {"tp":count_dict["tp"],"fp":count_dict["fp"],"tn":count_dict["tn"],"fn":count_dict["fn"]}
        if count_dict["tp"]+count_dict["fp"] > 0:
            output["precision"] = round(float(count_dict["tp"])/(count_dict["tp"]+count_dict["fp"]),2)
        else:
            output["precision"] = 0.0
        if count_dict["tp"]+count_dict["fn"] > 0:
            output["recall"] = round(float(count_dict["tp"])/(count_dict["tp"]+count_dict["fn"]),2)
        else:
            output["recall"] = 0.0
    print output
    return output

def calculate_precision_recall(actual,predicted,df=None):
    if df == None:
        df = pd.DataFrame({"actual":actual,"predicted":predicted})
    else:
        df=df
    classes = df["actual"].unique()
    output = {}
    for val in classes:
        class_summary = {}
        count_dict = {"tp":0,"fp":0,"tn":0,"fn":0}
        count_dict["tp"] = df[(df["actual"]==val) & (df["predicted"]==val)].shape[0]
        count_dict["fp"] = df[(df["actual"]!=val) & (df["predicted"]==val)].shape[0]
        count_dict["tn"] = df[(df["actual"]!=val) & (df["predicted"]!=val)].shape[0]
        count_dict["fn"] = df[(df["actual"]==val) & (df["predicted"]!=val)].shape[0]
        class_summary["counts"] = count_dict
        if count_dict["tp"]+count_dict["fp"] > 0:
            class_summary["precision"] = round(float(count_dict["tp"])/(count_dict["tp"]+count_dict["fp"]),2)
        else:
            class_summary["precision"] = 0.0
        if count_dict["tp"]+count_dict["fn"] > 0:
            class_summary["recall"] = round(float(count_dict["tp"])/(count_dict["tp"]+count_dict["fn"]),2)
        else:
            class_summary["recall"] = 0.0
        output[str(val)] = class_summary
    return output

def calculate_scored_probability_stats(scored_dataframe):
    new_df = scored_dataframe[["predicted_class","predicted_probability"]]
    bands = [0.25,0.50,0.75,0.90]
    output = {}

    for val in bands:
        temp_df = new_df[new_df["predicted_probability"] >= val]
        output[">"+str(100*val)+"%"] = temp_df["predicted_class"].value_counts().to_dict()
    temp_df = new_df[new_df["predicted_probability"] < 0.25]
    output["<25%"] = temp_df["predicted_class"].value_counts().to_dict()
    for key in output.keys():
        if output[key] == {}:
            output.pop(key, None)
    formattedSplit = reformat_prediction_split(output)
    print "formattedSplit"
    print formattedSplit
    print "="*200
    return formattedSplit

def create_dummy_columns(df,colnames):
    df1 = df[[col for col in df.columns if col not in colnames]]
    for col in colnames:
        if col in df.columns:
            dummies = pd.get_dummies(df[col],prefix = col)
            df1 = pd.concat([df1,dummies], axis = 1)
    return df1

def fill_missing_columns(df,model_columns,result_column):
    existing_columns = df.columns
    new_columns = list(set(existing_columns)-set(model_columns))
    missing_columns = list(set(model_columns)-set(existing_columns)-set(result_column))
    df_shape = df.shape
    for col in missing_columns:
        df[col] = [0]*df_shape[0]
    df = df[[x for x in model_columns if x != result_column]]
    df = df[model_columns]
    return df

def transform_feature_importance(feature_importance_dict):
    feature_importance_new = [["Name"],["Value"]]
    for k,v in feature_importance_dict.items():
        feature_importance_new[0].append(k)
        feature_importance_new[1].append(v)
    zipped_feature_importance = zip(feature_importance_new[0],feature_importance_new[1])
    zipped_feature_importance_subset = zipped_feature_importance[1:]
    zipped_feature_importance_subset = sorted(zipped_feature_importance_subset,key=lambda x:x[1],reverse=True)
    zipped_feature_importance = [zipped_feature_importance[0]]+zipped_feature_importance_subset
    feature_importance_new = [[],[]]
    for val in zipped_feature_importance:
        feature_importance_new[0].append(val[0])
        feature_importance_new[1].append(val[1])
    output = [feature_importance_new[0][:6],feature_importance_new[1][:6]]
    return output

def bin_column(df, measure_column,get_aggregation = False):
    allCols = df.columns
    df = df.select([col(c).cast('double').alias(c) if c == measure_column else col(c) for c in allCols])
    min_,max_,mean_,stddev_,total = df.agg(FN.min(measure_column), FN.max(measure_column), FN.mean(measure_column), FN.stddev(measure_column), FN.sum(measure_column)).collect()[0]
    df_without_outlier = df.filter(col(measure_column)>=mean_-3*stddev_).filter(col(measure_column)<=mean_+3*stddev_)
    diff = (max_ - min_)*1.0
    splits_new = [min_-1,min_+diff*0.4,min_+diff*0.7,max_+1]
    bucketizer = Bucketizer(inputCol=measure_column,outputCol='bucket')
    bucketizer.setSplits(splits_new)
    df = bucketizer.transform(df)
    if (get_aggregation):
        agg_df = df.groupby("bucket").agg(FN.sum(measure_column).alias('sum'), FN.count(measure_column).alias('count'))
        aggr = {}
        for row in agg_df.collect():
            aggr[row[0]] = {'sum': row[1], 'count': row[2], 'sum_percent': row[1]*100.0/total, 'count_percent': row[2]*100.0/df.count()}

    df = df.select([c for c in df.columns if c!=measure_column])
    df = df.withColumnRenamed("bucket",measure_column)
    if splits_new[0] > 1:
        splitRanges = ["("+str(round(splits_new[0]))+" to "+str(round(splits_new[1]))+")",
                    "("+str(round(splits_new[1]))+" to "+str(round(splits_new[2]))+")",
                    "("+str(round(splits_new[2]))+" to "+str(round(splits_new[3]))+")"
                    ]
    else:
        splitRanges = ["("+str(round(splits_new[0],2))+" to "+str(round(splits_new[1],2))+")",
                    "("+str(round(splits_new[1],2))+" to "+str(round(splits_new[2],2))+")",
                    "("+str(round(splits_new[2],2))+" to "+str(round(splits_new[3],2))+")"
                    ]

    if (get_aggregation):
        return df, aggr
    return df, splits_new[1:],splitRanges

def cluster_by_column(df, col_to_cluster, get_aggregation = False):
    my_df = df.select(df.columns)
    assembler = VectorAssembler(inputCols = [col_to_cluster], outputCol = "feature_vector")
    assembled = assembler.transform(my_df)

    avg,std,total = assembled.agg(mean(col_to_cluster).alias('avg'), stddev(col_to_cluster).alias('std'), sum(col_to_cluster).alias('total')).collect()[0]
    assembled_without_outlier = assembled.filter(col(col_to_cluster)>=avg-3*std).filter(col(col_to_cluster)<=avg+3*std)
    assembled_without_outlier = assembled_without_outlier.select([c for c in assembled_without_outlier.columns if c!=col_to_cluster])
    assembled = assembled.select([col(c) if c!=col_to_cluster else col(c).alias('target_col') for c in assembled.columns])
    # mmScaler = StandardScaler(inputCol="feature_vector", outputCol="standard_features",withStd=True, withMean=False)
    # scale_model = mmScaler.fit(assembled)
    # vectorized_data = scale_model.transform(assembled)
    kmeans = KMeans(predictionCol=col_to_cluster, featuresCol='feature_vector').setK(3).setSeed(1)
    model = kmeans.fit(assembled_without_outlier)
    final_df = model.transform(assembled)
    # print final_df.show(3)
    if (get_aggregation):
        agg_df = final_df.groupby(col_to_cluster).agg(sum('target_col').alias('sum'), count('target_col').alias('count'))
        aggr = {}
        for row in agg_df.collect():
            aggr[row[0]] = {'sum': row[1], 'count': row[2], 'sum_percent': row[1]*100.0/total, 'count_percent': row[2]*100.0/final_df.count()}
    final_df = final_df.select([c for c in final_df.columns if c!='feature_vector'])
    final_df = final_df.select([col(c) if c!=col_to_cluster else col(c).alias(col_to_cluster) for c in final_df.columns])
    # print final_df.show(3)
    if (get_aggregation):
        return final_df, aggr
    return final_df, model.clusterCenters()

def add_string_index(df,string_columns):
    string_columns = list(set(string_columns))
    my_df = df.select(df.columns)
    column_name_maps = {}
    mapping_dict = {}
    for c in string_columns:
        my_df = StringIndexer(inputCol=c, outputCol=c+'_index').fit(my_df).transform(my_df)
        column_name_maps[c+'_index'] = c
        mapping_dict[c] = dict(enumerate(my_df[[c+'_index']].schema[0].metadata['ml_attr']['vals']))
    my_df = my_df.select([c for c in my_df.columns if c not in string_columns])
    my_df = my_df.select([col(c).alias(column_name_maps[c]) if c in column_name_maps.keys() \
                            else col(c) for c in my_df.columns])
    return my_df, mapping_dict

##################################Spark ML Pipelines ###########################

def create_pyspark_ml_pipeline(numerical_columns,categorical_columns,target_column,algoName=None,algoType="classification"):
    indexers = [StringIndexer(inputCol=x, outputCol=x+'_indexed') for x in categorical_columns ] #String Indexer
    encoders = [OneHotEncoder(dropLast=False, inputCol=x+"_indexed", outputCol=x+"_encoded") for x in categorical_columns] # one hot encoder
    assembler_features = VectorAssembler(inputCols=[x+"_encoded" for x in sorted(categorical_columns)]+sorted(numerical_columns), outputCol='features')
    if algoName != "lr" and algoType == "classification":
        labelIndexer = StringIndexer(inputCol=target_column, outputCol="label")
    ml_stages = [[i,j] for i,j in zip(indexers, encoders)]
    pipeline_stages = []
    for ml_stage in ml_stages:
        pipeline_stages += ml_stage
    if algoName != "lr" and algoType == "classification":
        pipeline_stages += [assembler_features, labelIndexer]
    else:
        pipeline_stages += [assembler_features]
    pipeline = Pipeline(stages=pipeline_stages)
    return pipeline

def save_pipeline_or_model(pipeline,dir_path):
    """
    Need to check if any folder exist with the given name
    if yes then 1st delete that then proceed
    """
    # dir_path = dir_path.replace("ubuntu","hadoop")
    print "dir_path",dir_path
    if dir_path.startswith("file"):
        new_path = dir_path[7:]
    else:
        new_path = dir_path
    print "new_path",new_path
    try:
        pipeline.save(dir_path)
        print "saved in",dir_path
    except:
        print "saving in dir_path failed:- Trying new_path"
        pipeline.save(new_path)
        print "saved in",new_path

def load_pipeline(filepath):
    model = PipelineModel.load(filepath)
    return model

##########################SKLEARN Model Pipelines ##############################

def load_rf_model(filepath):
    model = RandomForestClassificationModel.load(filepath)
    return model
def load_linear_regresssion_pyspark_model(filepath):
    model = LinearRegressionModel.load(filepath)
    return model
def load_generalized_linear_regresssion_pyspark_model(filepath):
    model = GeneralizedLinearRegressionModel.load(filepath)
    return model
def load_gbt_regresssion_pyspark_model(filepath):
    model = GBTRegressionModel.load(filepath)
    return model
def load_dtree_regresssion_pyspark_model(filepath):
    model = DecisionTreeRegressionModel.load(filepath)
    return model
def load_rf_regresssion_pyspark_model(filepath):
    model = RandomForestRegressionModel.load(filepath)
    return model
def load_one_vs_rest_model(filepath):
    model = OneVsRestModel.load(filepath)
    return model
def load_logistic_model(filepath):
    model = LogisticRegressionModel.load(filepath)
    return model

def stratified_sampling(df,target_column,split):
    levels = [x[0] for x in df.select(target_column).distinct().collect()]
    frac = [split]*len(levels)
    sampling_dict = dict(zip(levels,frac))
    sampled_df = df.sampleBy(target_column, fractions = sampling_dict, seed=0)
    return sampled_df

def get_training_and_validation_data(df,target_column,split,appType="classification"):
    seed = 4232321145
    df = df.withColumn("monotonically_increasing_id", monotonically_increasing_id())
    if appType == "classification":
        trainingData = stratified_sampling(df,target_column,split)
    else:
        trainingData = df.sample(False, split, seed)
    validationIds = df.select("monotonically_increasing_id").subtract(trainingData.select("monotonically_increasing_id"))
    indexed = df.alias("indexed")
    validation = validationIds.alias("validation")
    validationData = indexed.join(validation, col("indexed.monotonically_increasing_id") == col("validation.monotonically_increasing_id"), 'inner').select("indexed.*")
    return trainingData,validationData

def calculate_sparkml_feature_importance(df,modelFit,categorical_columns,numerical_columns):
    featureImportanceSparseVector = modelFit.featureImportances
    feature_importance = {}
    start_idx = 0
    end_idx = 0
    for level in sorted(categorical_columns):
        # Not calling from meta here now, as this function is called only in logistic_regression_pyspark and random_forest_pyspark
        count = len(df.select(level).distinct().collect())
        end_idx += count
        col_percentage = 0
        for key in range(start_idx,end_idx):
            try:
                col_percentage += featureImportanceSparseVector[key]
            except:
                continue
        feature_importance[level] = col_percentage
        start_idx = end_idx
    for val in sorted(numerical_columns):
        feature_importance[val] = featureImportanceSparseVector[start_idx]
        start_idx += 1
    return feature_importance

def read_string_indexer_mapping(pipeline_path,sqlContext):
    metadata = sqlContext.read.text(pipeline_path+"/metadata")
    stageuids = json.loads(metadata.take(1)[0][0])["paramMap"]["stageUids"]
    if len(stageuids) < 11:
        try:
            parquet_key = "0"+str(len(stageuids)-1)+"_"+stageuids[-1]
            parquet_filepath = pipeline_path+"/stages/"+parquet_key+"/data"
            level_df = sqlContext.read.parquet(parquet_filepath)
        except:
            parquet_key = str(len(stageuids)-1)+"_"+stageuids[-1]
            parquet_filepath = pipeline_path+"/stages/"+parquet_key+"/data"
            level_df = sqlContext.read.parquet(parquet_filepath)
    else:
        parquet_key = str(len(stageuids)-1)+"_"+stageuids[-1]
        parquet_filepath = pipeline_path+"/stages/"+parquet_key+"/data"
        level_df = sqlContext.read.parquet(parquet_filepath)
    levels = [str(v) for v in  [x[0] for x in level_df.select("labels").collect()][0]]
    mapping_dict = dict(enumerate(levels))
    return mapping_dict

def reformat_prediction_split(prediction_split):
    inner_keys = []
    for key,val in prediction_split.items():
        inner_keys += val.keys()
    inner_keys = list(set(inner_keys))
    pred_split_new = [["Range"]]
    for val in inner_keys:
        pred_split_new.append([val])
    for k,v in prediction_split.items():
        pred_split_new[0].append(k)
        for idx,val in enumerate(pred_split_new[1:]):
            if val[0] in v:
                pred_split_new[idx+1].append(v[val[0]])
            else:
                pred_split_new[idx+1].append(0)
    return pred_split_new

def fill_missing_values(df,replacement_dict):
    """
    replacement_dict => {"col1":23,"col2":"GG","col3":45}
    """
    df = df.fillna(replacement_dict)
    return df


def get_model_comparison(collated_summary):
    summary = []
    algos = collated_summary.keys()
    algos_dict = {"randomforest":"Random Forest","xgboost":"XGBoost","logistic":"Logistic Regression","svm":"Support Vector Machine"}
    out = []
    for val in algos:
        out.append(algos_dict[val])
    out = [[""]+out]
    first_column = ["Accuracy","Precision","Recall"]
    data_keys = ["modelAccuracy","modelPrecision","modelRecall"]
    summary_map = {"Precision":"Best Precision","Recall":"Best Recall","Best Accuracy":"Accuracy"}
    map_dict = dict(zip(first_column,data_keys))
    for key in first_column:
        row = []
        for val in algos:
            # row.append(round(100*(collated_summary[val][map_dict[key]]),2))
            roundedVal = int(round(100*(collated_summary[val][map_dict[key]])))
            row.append(roundedVal)
        out.append([key]+row)
        max_index = __builtin__.max(xrange(len(row)), key = lambda x: row[x])
        summary.append(["Best "+key,algos_dict[algos[max_index]]])
    runtime = []
    for val in algos:
        runtime.append(collated_summary[val]["trainingTime"])
    max_runtime_index = __builtin__.max(xrange(len(runtime)), key = lambda x: runtime[x])
    summary.append(["Best Runtime",algos_dict[algos[max_runtime_index]]])
    inner_html = []
    for val in summary:
        inner_html.append("<li>{} : {}</li>".format(val[0],val[1]))
    summary_html = "<ul class='list-unstyled bullets_primary'>{}{}{}{}</ul>".format(inner_html[0],inner_html[1],inner_html[2],inner_html[3])
    summaryData = HtmlData(data = summary_html)


    modelTable = TableData()
    modelTable.set_table_data([list(x) for x in np.transpose(out)])
    modelTable.set_table_type("circularChartTable")
    if len(algos) == 1:
        summaryData = None
    return modelTable,summaryData

def get_feature_importance(collated_summary):
    feature_importance = collated_summary["randomforest"]["featureImportance"]
    feature_importance_list = [[k,v] for k,v in feature_importance.items()]
    sorted_feature_importance_list = sorted(feature_importance_list,key = lambda x:x[1],reverse=True)
    feature_importance_data = [{"name":x[0],"value":x[1]} for x in sorted_feature_importance_list]
    mapeChartData = NormalChartData(data=feature_importance_data)
    chart_json = ChartJson()
    chart_json.set_data(mapeChartData.get_data())
    chart_json.set_chart_type("bar")
    chart_json.set_axes({"x":"name","y":"value"})
    chart_json.set_subchart(False)
    chart_json.set_yaxis_number_format(".2f")
    card3Chart = C3ChartData(data=chart_json)
    return card3Chart

def get_total_models_classification(collated_summary):
    algos = collated_summary.keys()
    n_model = 1
    algorithm_name = []
    for val in algos:
        trees = collated_summary[val].get("nTrees")
        algorithm_name.append(collated_summary[val].get("algorithmName"))
        if trees:
            n_model += trees
    output = "<p>mAdvisor has built {} models using {} algorithms ({}) to predict {} and \
        has come up with the following results:</p>".format(n_model,len(algos),",".join(algorithm_name),collated_summary[algos[0]]["targetVariable"])
    return output

def get_total_models_regression(collated_summary):
    algos = collated_summary.keys()
    n_model = 0
    algorithm_name = []
    for val in algos:
        trees = collated_summary[val].get("nTrees")
        algorithm_name.append(collated_summary[val].get("algorithmDisplayName"))
    n_model = len(algorithm_name)
    output = "<p>mAdvisor has built {} regression models using {} algorithms ({}) to predict {} and \
        has come up with the following results:</p>".format(n_model,len(algos),", ".join(algorithm_name),collated_summary[algos[0]]["targetVariable"])
    return output

def create_model_folders(model_slug, basefoldername, subfolders=None):
    if subfolders is None:
        subfolders = []
    home_dir = os.path.expanduser("~")
    filepath = home_dir+"/"+basefoldername
    if not os.path.isdir(filepath):
        os.mkdir(filepath)
    if os.path.isdir(filepath+"/"+model_slug):
        shutil.rmtree(filepath+"/"+model_slug)
    os.mkdir(filepath+"/"+model_slug)
    for foldername in subfolders:
        os.mkdir(filepath+"/"+model_slug+"/"+foldername)
    return filepath+"/"+model_slug+"/"

def create_scored_data_folder(score_slug,basefoldername):
    home_dir = os.path.expanduser("~")
    filepath = home_dir+"/"+basefoldername
    if not os.path.isdir(filepath):
        os.mkdir(filepath)
    if os.path.isdir(filepath+"/"+score_slug):
        shutil.rmtree(filepath+"/"+score_slug)
    os.mkdir(filepath+"/"+score_slug)
    return filepath+"/"+score_slug+"/"

def reformat_confusion_matrix(confusion_matrix):
    levels = confusion_matrix.keys()
    confusion_matrix_data = [[""]+levels]
    for outer in levels:
        inner_list = [outer]
        for inner in levels:
            inner_list.append(confusion_matrix[inner][outer])
        confusion_matrix_data.append(inner_list)
    return [list(x) for x in np.array(confusion_matrix_data).T]


def create_model_summary_cards(modelSummaryClass):
    if modelSummaryClass.get_model_type() == None or modelSummaryClass.get_model_type() == "classification":
        modelSummaryCard1 = NormalCard()
        modelSummaryCard1Data = []
        modelSummaryCard1Data.append(HtmlData(data="<h4 class = 'sm-mb-20'>{}</h4>".format(modelSummaryClass.get_algorithm_display_name())))
        modelSummaryCard1Data.append(HtmlData(data="<h5>Summary</h5>"))
        modelSummaryCard1Data.append(HtmlData(data="<p>Target Variable - {}</p>".format(modelSummaryClass.get_target_variable())))
        modelSummaryCard1Data.append(HtmlData(data="<p>Independent Variable Chosen - {}</p>".format(len(modelSummaryClass.get_model_features()))))
        modelSummaryCard1Data.append(HtmlData(data="<h5>Predicted Distribution</h5>"))
        prediction_split_array = sorted([(k,v) for k,v in modelSummaryClass.get_prediction_split().items()],key=lambda x:x[1],reverse=True)
        for val in prediction_split_array:
            modelSummaryCard1Data.append(HtmlData(data="<p>{} - {}%</p>".format(val[0],val[1])))
        modelSummaryCard1Data.append(HtmlData(data="<p>Algorithm - {}</p>".format(modelSummaryClass.get_algorithm_name())))
        if modelSummaryClass.get_num_trees():
            modelSummaryCard1Data.append(HtmlData(data="<p>Total Trees - {}</p>".format(modelSummaryClass.get_num_trees())))
        if modelSummaryClass.get_num_rules():
            modelSummaryCard1Data.append(HtmlData(data="<p>Total Rules - {}</p>".format(modelSummaryClass.get_num_rules())))
        modelSummaryCard1Data.append(HtmlData(data="<p>Validation Method - {}</p>".format(modelSummaryClass.get_validation_method())))
        modelSummaryCard1Data.append(HtmlData(data="<p>Model Accuracy - {}</p>".format(modelSummaryClass.get_model_accuracy())))
        modelSummaryCard1.set_card_data(modelSummaryCard1Data)
        modelSummaryCard1.set_card_width(50)

        modelSummaryCard2 = NormalCard()
        modelSummaryCard2Data = []
        modelSummaryCard2Data.append(HtmlData(data="<h4 class = 'sm-ml-15 sm-pb-10'>Confusion Matrix</h4>"))
        modelSummaryCard2Table = TableData()
        modelSummaryCard2Table.set_table_data(reformat_confusion_matrix(modelSummaryClass.get_confusion_matrix()))
        modelSummaryCard2Table.set_table_type("confusionMatrix")
        modelSummaryCard2Table.set_table_top_header("Actual")
        modelSummaryCard2Table.set_table_left_header("Predicted")
        modelSummaryCard2Data.append(modelSummaryCard2Table)
        modelSummaryCard2.set_card_data(modelSummaryCard2Data)
        modelSummaryCard2.set_card_width(50)
        return [modelSummaryCard1,modelSummaryCard2]
    elif modelSummaryClass.get_model_type() == "regression":
        targetVariable = modelSummaryClass.get_target_variable()
        modelSummaryCard1 = NormalCard()
        modelSummaryCard1.set_card_width(50)
        modelSummaryCard1Data = []
        modelSummaryCard1Data.append(HtmlData(data="<h4><center>Algorithm Parameters </center></h4>"))
        modelSummaryCard1Data.append(HtmlData(data="<p>Target Variable - {}</p>".format(targetVariable)))
        # modelSummaryCard1Data.append(HtmlData(data="<p>Independent Variable Chosen - {}</p>".format(len(modelSummaryClass.get_model_features()))))
        # modelSummaryCard1Data.append(HtmlData(data="<h5>Predicted Distribution</h5>"))
        modelParams = modelSummaryClass.get_model_params()
        print modelParams
        count = 0
        for k,v in modelParams.items():
            k = k.capitalize()
            count += 1
            if count <= 4 :
                modelSummaryCard1Data.append(HtmlData(data="<p>{} - {}</p>".format(k,v)))
            else:
                htmlDataObj = HtmlData(data="<p>{} - {}</p>".format(k,v))
                htmlDataObj.set_class_tag("hidden")
                modelSummaryCard1Data.append(htmlDataObj)
        modelSummaryCard1.set_card_data(modelSummaryCard1Data)

        quantileSummaryArr = modelSummaryClass.get_quantile_summary()
        quantileTableData = []
        quantileTableTopRow = ["Distribution of Quartiles","Average Value"]
        quantileTableData.append(quantileTableTopRow)

        for quantileSummaryObj in quantileSummaryArr:
            qunatileRow = []
            if quantileSummaryObj[0] == 0:
                qunatileRow = ["Bottom 25% observations",round(quantileSummaryObj[1]["mean"],2)]
            if quantileSummaryObj[0] == 1:
                qunatileRow = ["25% to 50% observations",round(quantileSummaryObj[1]["mean"],2)]
            if quantileSummaryObj[0] == 2:
                qunatileRow = ["50% to 75% observations",round(quantileSummaryObj[1]["mean"],2)]
            if quantileSummaryObj[0] == 3:
                qunatileRow = ["Top 25% observations",round(quantileSummaryObj[1]["mean"],2)]
            if len(qunatileRow) > 0:
                quantileTableData.append(qunatileRow)

        quantileTable = TableData({'tableType':'normal','tableData':quantileTableData})
        quantileTable.set_table_top_header("Distribution of Predicted Values")

        modelSummaryCard2 = NormalCard()
        modelSummaryCard2.set_card_width(50)
        modelSummaryCard2Data = []
        modelSummaryCard2Data.append(HtmlData(data="<h4 class = 'sm-mb-20'><b>{}</b><br /><small>Summary</small></h4>".format(modelSummaryClass.get_algorithm_display_name())))
        modelSummaryCard2Data.append(HtmlData(data="<h4><center>Distribution of predicted values</center></h4>"))
        modelSummaryCard2Data.append(quantileTable)
        modelSummaryCard2.set_card_data(modelSummaryCard2Data)

        ######################MAPE CHART#######################################

        mapeChartData = []
        chartDataValues = []
        mapeStatsArr = modelSummaryClass.get_mape_stats()
        for val in mapeStatsArr:
            chartDataValues.append(val[1]["count"])
            if val[1]["splitRange"][0] == 0:
                mapeChartData.append({"key":"<{}%".format(val[1]["splitRange"][1]),"value":val[1]["count"]})
            elif val[1]["splitRange"][1] == 100:
                mapeChartData.append({"key":">{}%".format(val[1]["splitRange"][0]),"value":val[1]["count"]})
            else:
                mapeChartData.append({"key":"{}-{}%".format(val[1]["splitRange"][0],val[1]["splitRange"][1]),"value":val[1]["count"]})
        mapeChartJson = ChartJson()
        mapeChartJson.set_data(mapeChartData)
        mapeChartJson.set_chart_type("bar")
        mapeChartJson.set_label_text({'x':' ','y':'No of Observations'})
        mapeChartJson.set_axes({"x":"key","y":"value"})
        mapeChartJson.set_title('Distribution of Errors')
        # mapeChartJson.set_yaxis_number_format(".4f")
        # mapeChartJson.set_yaxis_number_format(CommonUtils.select_y_axis_format(chartDataValues))

        modelSummaryMapeChart = C3ChartData(data=mapeChartJson)

        ######################Actual Vs Predicted CHART#########################

        sampleData = modelSummaryClass.get_sample_data()
        sampleData = pd.DataFrame(sampleData)
        sampleData.reset_index(inplace=True)
        actualVsPredictedData = sampleData[[targetVariable,"prediction"]].T.to_dict().values()
        actualVsPredictedData = sorted(actualVsPredictedData,key=lambda x:x[targetVariable])
        actualVsPredictedChartJson = ChartJson()
        actualVsPredictedChartJson.set_chart_type("scatter")
        actualVsPredictedChartJson.set_data({"data":actualVsPredictedData})
        actualVsPredictedChartJson.set_axes({"x":targetVariable,"y":"predicted"})
        actualVsPredictedChartJson.set_label_text({'x':'Actual Values','y':'Predicted Values'})
        actualVsPredictedChartJson.set_title('Actual vs Predicted')


        actualVsPredictedChart = C3ChartData(data=actualVsPredictedChartJson)

        ##################### Residual Chart #####################################
        residualData = sampleData[["index","difference"]].T.to_dict().values()
        residualData = sorted(residualData,key=lambda x:x["index"])
        residualChartJson = ChartJson()
        residualChartJson.set_chart_type("scatter")
        residualChartJson.set_data({"data":residualData})
        residualChartJson.set_axes({"x":"index","y":"difference"})
        residualChartJson.set_label_text({'x':' ','y':'Residuals'})
        residualChart = C3ChartData(data=residualChartJson)
        residualButton = PopupData()
        residualButton.set_data(residualChart)
        residualButton.set_name("View Residuals")

        modelSummaryCard3 = NormalCard()
        modelSummaryCard3.set_card_width(50)
        # modelSummaryCard3.set_card_data([modelSummaryMapeChart,actualVsPredictedChart,residualButton])
        modelSummaryCard3.set_card_data([actualVsPredictedChart,residualButton])

        modelSummaryCard4 = NormalCard()
        modelSummaryCard4.set_card_width(50)
        mapeDummyData = HtmlData(data="<br/><br/><br/>")
        modelSummaryCard4.set_card_data([mapeDummyData,modelSummaryMapeChart])
        return [modelSummaryCard2,modelSummaryCard4,modelSummaryCard1,modelSummaryCard3]
        # return [modelSummaryCard1,modelSummaryCard2]


def collated_model_summary_card(result_setter,prediction_narrative,appType,appid=None):
    if appType == "CLASSIFICATION":
        collated_summary = result_setter.get_model_summary()
        card1 = NormalCard()
        card1Data = [HtmlData(data="<h3>Model Summary</h3>")]
        card1Data.append(HtmlData(data = get_total_models_classification(collated_summary)))
        card1.set_card_data(card1Data)
        card1 = json.loads(CommonUtils.convert_python_object_to_json(card1))

        try:
            featureImportanceC3Object = get_feature_importance(collated_summary)
        except:
            featureImportanceC3Object = None
        if featureImportanceC3Object != None:
            card2 = NormalCard()
            card2_elements = get_model_comparison(collated_summary)
            if card2_elements[1] == None:
                card2Data = [card2_elements[0]]
            else:
                card2Data = [card2_elements[0],card2_elements[1]]

            card2.set_card_data(card2Data)
            card2.set_card_width(50)

            card3 = NormalCard()
            if appid == None:
                card3Data = [HtmlData(data="<h4 class = 'sm-ml-15 sm-pb-10'>Feature Importance</h4>")]
            else:
                try:
                    card3Data = [HtmlData(data="<h4 class = 'sm-ml-15 sm-pb-10'>{}</h4>".format(GLOBALSETTINGS.APPS_ID_MAP[appid]["heading"]))]
                except:
                    card3Data = [HtmlData(data="<h4 class = 'sm-ml-15 sm-pb-10'>Feature Importance</h4>")]
            card3Data.append(featureImportanceC3Object)
            card3.set_card_data(card3Data)
            card3.set_card_width(50)
            # prediction_narrative.insert_card_at_given_index(card3,2)
            card3 = json.loads(CommonUtils.convert_python_object_to_json(card3))
        else:
            card2 = NormalCard()
            card2_elements = get_model_comparison(collated_summary)
            card2Data = [card2_elements[0]]
            card2.set_card_data(card2Data)
            card2.set_card_width(50)
            if card2_elements[1] != None:
                card3 = NormalCard()
                card3Data = [card2_elements[1]]
                card3.set_card_data(card3Data)
                card3.set_card_width(50)
            else:
                card3 = None

        modelResult = CommonUtils.convert_python_object_to_json(prediction_narrative)
        modelResult = json.loads(modelResult)
        existing_cards = modelResult["listOfCards"]
        existing_cards = result_setter.get_all_classification_cards()
        # print "existing_cards",existing_cards
        # modelResult["listOfCards"] = [card1,card2,card3] + existing_cards
        card2 = json.loads(CommonUtils.convert_python_object_to_json(card2))
        all_cards = [card1,card2,card3] + existing_cards
        all_cards = [x for x in all_cards if x != None]
        modelResult = NarrativesTree()
        modelResult.add_cards(all_cards)
        modelResult = CommonUtils.convert_python_object_to_json(modelResult)
        modelJsonOutput = ModelSummary()
        modelJsonOutput.set_model_summary(json.loads(modelResult))
        ####
        rfModelSummary = result_setter.get_random_forest_model_summary()
        lrModelSummary = result_setter.get_logistic_regression_model_summary()
        xgbModelSummary = result_setter.get_xgboost_model_summary()
        svmModelSummary = result_setter.get_svm_model_summary()

        model_dropdowns = []
        model_hyperparameter_summary = []
        model_features = {}
        model_configs = {}
        labelMappingDict = {}
        targetVariableLevelcount = {}
        target_variable = collated_summary[collated_summary.keys()[0]]["targetVariable"]
        allAlgorithmTable = []
        allAlgorithmTableHeaderRow = ["#","Model Id","Algorithm Name","Optimization Method","Metric","Precision","Recall","Accuracy","ROC-AUC","Run Time(Secs)"]
        allAlgorithmTable.append(allAlgorithmTableHeaderRow)
        counter = 1
        hyperParameterFlagDict = {}
        hyperParameterFlag = False
        for obj in [rfModelSummary,lrModelSummary,xgbModelSummary,svmModelSummary]:
            if obj != None:
                if result_setter.get_hyper_parameter_results(obj["slug"]) != None:
                    hyperParameterFlagDict[obj["slug"]] = True
                    hyperParameterFlag = True
                else:
                    hyperParameterFlagDict[obj["slug"]] = False
        for obj in [rfModelSummary,lrModelSummary,xgbModelSummary,svmModelSummary]:
            if obj != None:
                model_dropdowns.append(obj["dropdown"])
                model_features[obj["slug"]] = obj["modelFeatureList"]
                labelMappingDict[obj["slug"]] = obj["levelMapping"]
                if targetVariableLevelcount == {}:
                    targetVariableLevelcount = obj["levelcount"][target_variable]
                if hyperParameterFlag == True:
                    if hyperParameterFlagDict[obj["slug"]] == True:
                        hyperParamSummary = result_setter.get_hyper_parameter_results(obj["slug"])
                        algoRows = []
                        for rowDict in hyperParamSummary:
                            row = []
                            for key in allAlgorithmTableHeaderRow:
                                if key == "#":
                                    row.append(counter)
                                elif key == "Algorithm Name":
                                    row.append(obj["name"])
                                elif key == "Optimization Method":
                                    row.append("Grid Search")
                                elif key == "Metric":
                                    row.append(rowDict["comparisonMetricUsed"])
                                else:
                                    row.append(rowDict[key])
                            algoRows.append(row)
                            counter += 1

                        allAlgorithmTable += algoRows

                        algoCard = NormalCard(name=obj["name"],slug=obj["slug"])
                        parallelCoordinateMetaData = result_setter.get_metadata_parallel_coordinates(obj["slug"])
                        masterIgnoreList = parallelCoordinateMetaData["ignoreList"]
                        ignoreList = [x for x in masterIgnoreList if x in hyperParamSummary[0]]
                        hideColumns = parallelCoordinateMetaData["hideColumns"]
                        metricColName = parallelCoordinateMetaData["metricColName"]
                        columnOrder = parallelCoordinateMetaData["columnOrder"]
                        algoCard.set_card_data([ParallelCoordinateData(data=hyperParamSummary,ignoreList=ignoreList,hideColumns=hideColumns,metricColName=metricColName,columnOrder=columnOrder)])
                        algoCardJson = CommonUtils.convert_python_object_to_json(algoCard)
                        model_hyperparameter_summary.append(json.loads(algoCardJson))
        if hyperParameterFlag == True:
            algoSummaryCard = NormalCard(name="Top Performing Models",slug="FIRSTCARD")
            allAlgorithmTable = [allAlgorithmTable[0]] + sorted(allAlgorithmTable[1:],key=lambda x: x[allAlgorithmTableHeaderRow.index("Accuracy")] ,reverse=True)
            totalModels = len(allAlgorithmTable) - 1
            allAlgorithmTable = allAlgorithmTable[:GLOBALSETTINGS.MAX_NUMBER_OF_MODELS_IN_SUMMARY+1]
            allAlgorithmTableModified = [allAlgorithmTable[0]]
            for idx,row in enumerate(allAlgorithmTable[1:]):
                row[0] = idx+1
                allAlgorithmTableModified.append(row)
            allAlgorithmTable = allAlgorithmTableModified
            bestModel = allAlgorithmTable[1][allAlgorithmTableHeaderRow.index("Model Id")]
            evalMetric = allAlgorithmTable[1][allAlgorithmTableHeaderRow.index("Metric")]
            bestMetric = allAlgorithmTable[1][allAlgorithmTableHeaderRow.index(evalMetric)]
            bestAlgo = allAlgorithmTable[1][allAlgorithmTableHeaderRow.index("Algorithm Name")]
            if bestMetric == "NA":
                evalMetric = GLOBALSETTINGS.SKLEARN_EVAL_METRIC_NAME_DISPLAY_MAP[GLOBALSETTINGS.CLASSIFICATION_MODEL_EVALUATION_METRIC]
                bestMetric = allAlgorithmTable[1][allAlgorithmTableHeaderRow.index(evalMetric)]

            htmlData = HtmlData(data = "mAdvisor has built {} models by changing the input parameter specifications \
                            and the following are the top {} models based on chosen evaluation metric. {} which is \
                            built using {} algorithm is the best performing model with an {} of {}."\
                            .format(totalModels,GLOBALSETTINGS.MAX_NUMBER_OF_MODELS_IN_SUMMARY,bestModel,bestAlgo,evalMetric,bestMetric))
            allAlgorithmTable = TableData({'tableType':'normal','tableData':allAlgorithmTable})
            algoSummaryCard.set_card_data([htmlData,allAlgorithmTable])
            algoSummaryCardJson = CommonUtils.convert_python_object_to_json(algoSummaryCard)
            algoSummaryCardDict = json.loads(algoSummaryCardJson)
            model_hyperparameter_summary.insert(0,algoSummaryCardDict)
        model_configs = {"target_variable":[target_variable]}
        model_configs["modelFeatures"] = model_features
        model_configs["labelMappingDict"] = labelMappingDict
        model_configs["targetVariableLevelcount"] = [targetVariableLevelcount]
        model_dropdowns = [x for x in model_dropdowns if x != None]
        modelJsonOutput.set_model_dropdown(model_dropdowns)
        print model_dropdowns
        print "="*100
        modelJsonOutput.set_model_config(model_configs)
        if hyperParameterFlag == True:
            modelJsonOutput.set_model_hyperparameter_summary(model_hyperparameter_summary)
        modelJsonOutput = modelJsonOutput.get_json_data()
        return modelJsonOutput
    else:
        collated_summary = result_setter.get_model_summary()
        targetVariable = collated_summary[collated_summary.keys()[0]]["targetVariable"]
        card1 = NormalCard()
        # card1Data = [HtmlData(data="<h4><b>Predicting {}</b></h4>".format(targetVariable))]
        card1Data = [HtmlData(data="<h3>Model Summary</h3>")]
        card1Data.append(HtmlData(data = get_total_models_regression(collated_summary)))
        card1.set_card_data(card1Data)
        card1 = json.loads(CommonUtils.convert_python_object_to_json(card1))

        card2 = None
        if "linearregression" in collated_summary:
            card2 = NormalCard()
            coefficientsArray = sorted(collated_summary["linearregression"]["coefficinetsArray"],key=lambda x:abs(x[1]),reverse=True)
            coefficientsArray = [{"key":tup[0],"value":tup[1]} for tup in coefficientsArray]
            coefficientsArray = normalize_coefficients(coefficientsArray)
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
            card2Data = [HtmlData(data="<h4>Influence of Key Features on {}</h4>".format(targetVariable.capitalize())),coefficientsChart]
            card2.set_card_data(card2Data)
            card2 = json.loads(CommonUtils.convert_python_object_to_json(card2))

        card3 = None
        if "rfregression" in collated_summary:
            card3 = NormalCard()
            featureImportanceArray = sorted(collated_summary["rfregression"]["featureImportance"],key=lambda x:x[1],reverse=True)
            featureImportanceArray = [{"key":tup[0],"value":tup[1]} for tup in featureImportanceArray]
            chartDataValues = [x["value"] for x in featureImportanceArray]
            featureChartJson = ChartJson()
            featureChartJson.set_data(featureImportanceArray)
            featureChartJson.set_chart_type("bar")
            featureChartJson.set_label_text({'x':' ','y':'Feature Importance'})
            featureChartJson.set_axes({"x":"key","y":"value"})
            featureChartJson.set_title('Feature Importance')
            # featureChartJson.set_yaxis_number_format(".4f")
            featureChartJson.set_yaxis_number_format(CommonUtils.select_y_axis_format(chartDataValues))
            featureChart = C3ChartData(data=featureChartJson)
            # card3Data = [HtmlData(data="<h4><b><center>Feature Importance</center></b></h4>"),featureChart]
            card3Data = [featureChart]
            card3.set_card_data(card3Data)
            card3.set_card_width(50)
            card3 = json.loads(CommonUtils.convert_python_object_to_json(card3))

        card4 = NormalCard()
        allMetricsData = []
        metricNamesMapping = {
                            "mse" : "Mean Square Error",
                            "mae" : "Mean Absolute Error",
                            "r2" : "R-Squared",
                            "rmse" : "Root Mean Square Error"
                            }
        metricNames = collated_summary[collated_summary.keys()[0]]["modelEvaluationMetrics"].keys()
        full_names = map(lambda x: metricNamesMapping[x],metricNames)
        metricTableTopRow = ["Algorithm"]+full_names
        allMetricsData.append(metricTableTopRow)
        # print "collated_summary : ", collated_summary
        for algoName,dataObj in collated_summary.items():
            algoRow = []
            algoRow.append(collated_summary[algoName]['algorithmDisplayName'])
            for val in metricNames:
                algoRow.append(CommonUtils.round_sig(dataObj["modelEvaluationMetrics"][val],2))
            allMetricsData.append(algoRow)

        evaluationMetricsTable = TableData({'tableType':'normal','tableData':allMetricsData})
        evaluationMetricsTable.set_table_top_header("Model Comparison")
        card4Data = [HtmlData(data="<h4><center>Model Comparison</center></h4>"),evaluationMetricsTable]
        card4.set_card_data(card4Data)
        card4.set_card_width(50)

        card4 = json.loads(CommonUtils.convert_python_object_to_json(card4))

        existing_cards = result_setter.get_all_regression_cards()
        # print "existing_cards",existing_cards
        # modelResult["listOfCards"] = [card1,card2,card3] + existing_cards
        all_cards = [card1,card4,card3,card2] + existing_cards
        all_cards = [x for x in all_cards if x != None]

        modelResult = NarrativesTree()
        modelResult.add_cards(all_cards)
        modelResult = CommonUtils.convert_python_object_to_json(modelResult)
        modelJsonOutput = ModelSummary()
        modelJsonOutput.set_model_summary(json.loads(modelResult))
        ####

        model_dropdowns = []
        model_hyperparameter_summary = []
        model_features = {}
        model_configs = {}
        target_variable = collated_summary[collated_summary.keys()[0]]["targetVariable"]
        allRegressionModelSummary = result_setter.get_all_regression_model_summary()
        allAlgorithmTable = []
        allAlgorithmTableHeaderRow = ["#","Model Id","Algorithm Name","Optimization Method","Metric","RMSE","MAE","MSE","R-Squared","Run Time(Secs)"]
        allAlgorithmTable.append(allAlgorithmTableHeaderRow)
        counter = 1
        hyperParameterFlagDict = {}
        hyperParameterFlag = False
        for obj in allRegressionModelSummary:
            if obj != None:
                if result_setter.get_hyper_parameter_results(obj["slug"]) != None:
                    hyperParameterFlagDict[obj["slug"]] = True
                    hyperParameterFlag = True
                else:
                    hyperParameterFlagDict[obj["slug"]] = False
        for obj in allRegressionModelSummary:
            if obj != None:
                print obj["dropdown"]
                model_dropdowns.append(obj["dropdown"])
                model_features[obj["slug"]] = obj["modelFeatureList"]
                if hyperParameterFlag == True:
                    if hyperParameterFlagDict[obj["slug"]] == True:
                        hyperParamSummary = result_setter.get_hyper_parameter_results(obj["slug"])
                        algoRows = []
                        for rowDict in hyperParamSummary:
                            row = []
                            for key in allAlgorithmTableHeaderRow:
                                if key == "#":
                                    row.append(counter)
                                elif key == "Algorithm Name":
                                    row.append(obj["name"])
                                elif key == "Optimization Method":
                                    row.append("Grid Search")
                                elif key == "Metric":
                                    row.append(rowDict["comparisonMetricUsed"])
                                else:
                                    row.append(rowDict[key])
                            algoRows.append(row)
                            counter += 1

                        allAlgorithmTable += algoRows

                        algoCard = NormalCard(name=obj["name"],slug=obj["slug"])
                        parallelCoordinateMetaData = result_setter.get_metadata_parallel_coordinates(obj["slug"])
                        masterIgnoreList = parallelCoordinateMetaData["ignoreList"]
                        ignoreList = [x for x in masterIgnoreList if x in hyperParamSummary[0]]
                        hideColumns = parallelCoordinateMetaData["hideColumns"]
                        metricColName = parallelCoordinateMetaData["metricColName"]
                        columnOrder = parallelCoordinateMetaData["columnOrder"]
                        print "="*50
                        print columnOrder
                        print "="*50
                        algoCard.set_card_data([ParallelCoordinateData(data=hyperParamSummary,ignoreList=ignoreList,hideColumns=hideColumns,metricColName=metricColName,columnOrder=columnOrder)])
                        algoCardJson = CommonUtils.convert_python_object_to_json(algoCard)
                        model_hyperparameter_summary.append(json.loads(algoCardJson))

        if hyperParameterFlag == True:
            algoSummaryCard = NormalCard(name="Top Performing Models",slug="FIRSTCARD")
            allAlgorithmTable = [allAlgorithmTable[0]] + sorted(allAlgorithmTable[1:],key=lambda x: x[allAlgorithmTableHeaderRow.index("R-Squared")] ,reverse=True)
            totalModels = len(allAlgorithmTable) - 1
            allAlgorithmTable = allAlgorithmTable[:GLOBALSETTINGS.MAX_NUMBER_OF_MODELS_IN_SUMMARY+1]
            allAlgorithmTableModified = [allAlgorithmTable[0]]
            allAlgorithmTableModified[0][-1] = "Run Time(Secs)"
            for idx,row in enumerate(allAlgorithmTable[1:]):
                row[0] = idx+1
                allAlgorithmTableModified.append(row)
            allAlgorithmTable = allAlgorithmTableModified
            bestModel = allAlgorithmTable[1][allAlgorithmTableHeaderRow.index("Model Id")]
            evalMetric = allAlgorithmTable[1][allAlgorithmTableHeaderRow.index("Metric")]
            bestMetric = allAlgorithmTable[1][allAlgorithmTableHeaderRow.index(evalMetric)]
            bestAlgo = allAlgorithmTable[1][allAlgorithmTableHeaderRow.index("Algorithm Name")]
            htmlData = HtmlData(data = "mAdvisor has built {} models by changing the input parameter specifications \
                            and the following are the top {} models based on chosen evaluation metric. {} which is \
                            built using {} algorithm is the best performing model with an {} of {}."\
                            .format(totalModels,GLOBALSETTINGS.MAX_NUMBER_OF_MODELS_IN_SUMMARY,bestModel,bestAlgo,evalMetric,bestMetric))
            allAlgorithmTable = TableData({'tableType':'normal','tableData':allAlgorithmTable})
            algoSummaryCard.set_card_data([htmlData,allAlgorithmTable])
            algoSummaryCardJson = CommonUtils.convert_python_object_to_json(algoSummaryCard)
            algoSummaryCardDict = json.loads(algoSummaryCardJson)
            model_hyperparameter_summary.insert(0,algoSummaryCardDict)

        model_configs = {"target_variable":[target_variable]}
        model_configs["modelFeatures"] = model_features
        model_configs["labelMappingDict"] = {}
        model_configs["targetVariableLevelcount"] = []
        print model_dropdowns
        print "="*100
        model_dropdowns = [x for x in model_dropdowns if x != None]
        modelJsonOutput.set_model_dropdown(model_dropdowns)
        modelJsonOutput.set_model_config(model_configs)
        if hyperParameterFlag == True:
            modelJsonOutput.set_model_hyperparameter_summary(model_hyperparameter_summary)
        modelJsonOutput = modelJsonOutput.get_json_data()
        return modelJsonOutput

def get_mape_stats(df,colname):
    df = df.na.drop(subset=colname)
    splits = GLOBALSETTINGS.MAPEBINS
    splitRanges = [(splits[idx],splits[idx+1]) for idx,x in enumerate(splits) if idx < len(splits)-1]
    print splitRanges
    st = time.time()
    bucketizer = Bucketizer(inputCol=colname,outputCol="mapeGULSHAN")
    bucketizer.setSplits(splits)
    df = bucketizer.transform(df)
    # print df.show()
    print "mape bucketizer in",time.time()-st
    quantileGrpDf = df.groupby("mapeGULSHAN").agg(FN.count(colname).alias('count'))
    splitDict = {}
    for val in quantileGrpDf.collect():
        splitDict[str(int(val[0]))] = {"count":val[1]}
    for idx,val in enumerate(splitRanges):
        if str(idx) in splitDict:
            splitDict[str(idx)].update({"splitRange":val})
    return splitDict

def get_quantile_summary(df,colname):
    df = df.na.drop(subset=colname)
    st = time.time()
    # df = df.orderBy(colname)
    dfDesc = df.describe().toPandas()
    descrDict = dict(zip(dfDesc["summary"],dfDesc[colname]))
    quantiles = df.stat.approxQuantile(colname,[0.25,0.5,0.75],0.0)
    biasVal = 1
    splits = [float(descrDict["min"])-biasVal]+quantiles+[float(descrDict["max"])+biasVal]
    splitRanges = [(splits[idx],splits[idx+1]) for idx,x in enumerate(splits) if idx < len(splits)-1]
    print splitRanges
    try:
        bucketizer = Bucketizer(inputCol=colname,outputCol="buckGULSHAN")
        bucketizer.setSplits(splits)
        df = bucketizer.transform(df)
        # print df.show()
    except:
        print "using bias splitRange"
        splitRanges[0] = (splitRanges[0][0]+biasVal,splitRanges[0][1])
        splitRanges[-1] = (splitRanges[-1][0]+biasVal,splitRanges[-1][1]-biasVal)
        bucketizer = Bucketizer(inputCol=colname,outputCol="buckGULSHAN")
        bucketizer.setSplits(splits)
        df = bucketizer.transform(df)
        # print df.show()

    quantileGrpDf = df.groupby("buckGULSHAN").agg(FN.sum(colname).alias('sum'),FN.mean(colname).alias('mean'),FN.count(colname).alias('count'))
    splitDict = {}
    for val in quantileGrpDf.collect():
        splitDict[str(int(val[0]))] = {"sum":val[1],"mean":val[2],"count":val[3]}
    for idx,val in enumerate(splitRanges):
        if str(idx) in splitDict:
            splitDict[str(idx)].update({"splitRange":val})
    return splitDict

def get_scored_data_summary(scoredCol,outlierConstant=1.5):
    maxVal = np.max(scoredCol)
    sumVal = np.sum(scoredCol)
    avgVal = np.mean(scoredCol)
    nObs = len(scoredCol)
    sd = np.std(scoredCol,axis=0)
    upper_quartile = np.percentile(scoredCol, 75)
    lower_quartile = np.percentile(scoredCol, 25)
    IQR = (upper_quartile - lower_quartile) * outlierConstant
    quartileSet = (lower_quartile - IQR, upper_quartile + IQR)
    resultList = [x for x in scoredCol if x < quartileSet[0] or x > quartileSet[1]]
    nOutliers = len(resultList)
    out = []
    out.append({"name":"totalCount","value":nObs,"text":"Number of Observations"})
    out.append({"name":"totalSum","value":round(sumVal,2),"text":"Sum of Predicted Values"})
    out.append({"name":"maxValue","value":round(maxVal,2),"text":"Maximum of Predicted Values"})
    out.append({"name":"meanValue","value":round(avgVal,2),"text":"Average of Predicted Values"})
    out.append({"name":"outlierCount","value":nOutliers,"text":"Number of Outliers"})
    return out



#-------- VIF based feature selection for Linear regression (on sparkdf) --------------#

def vif_cal_spark(df):
    xvar_names=df.columns
    vif_ser = pd.Series(index=xvar_names)
    for i in range(0,len(xvar_names)):
        y_col=[xvar_names[i]]
        x_col=list(set(xvar_names)-set(y_col))
        vectorAssembler = VectorAssembler(inputCols=x_col, outputCol='features')
        train_df = vectorAssembler.transform(df)
        train_df = train_df.select(['features',y_col[0]])
        lin_reg = LinearRegression(featuresCol = 'features', labelCol=y_col[0])
        lin_reg_model = lin_reg.fit(train_df)
        predictions = lin_reg_model.transform(train_df)
        lr_evaluator = RegressionEvaluator(predictionCol="prediction",labelCol=y_col[0],metricName="r2")
        rsq =lr_evaluator.evaluate(predictions)
        if rsq == 1:
            rsq=0.999
        vif=round(1/(1-rsq),2)
        vif_ser[xvar_names[i]] = vif
    return vif_ser

def feature_selection_vif_spark(df,vif_thr=5):
    temp_vif = vif_cal_spark(df)
    check = (temp_vif>vif_thr).sum()
    print temp_vif
    if check == 0:
        return df
    else:
        all_col = df.columns
        while check !=0:
            print "In While"
            mx_col =temp_vif.idxmax()
            col2use = list(set(all_col)-set([mx_col]))
            temp_df = df.select(col2use)
            print "\ncolumn dropped : " + mx_col
            all_col = col2use
            temp_vif = vif_cal_spark(temp_df)
            print temp_vif
            check = (temp_vif>vif_thr).sum()
        return df.select(col2use)


#-------- VIF based feature selection for Linear regression (on Pandas df) --------------#

def vif_cal(df):
    xvar_names=df.columns
    vif_ser = pd.Series(index=xvar_names)
    for i in range(0,len(xvar_names)):
        y_col=[xvar_names[i]]
        x_col=list(set(xvar_names)-set(y_col))
        lin_reg = linear_model.LinearRegression()
        lin_reg.fit(df[x_col],df[y_col[0]])
        y_prd = lin_reg.predict(df[x_col])
        rsq = r2_score(df[y_col[0]],y_prd)
        if rsq == 1:
            rsq=0.999
        vif=round(1/(1-rsq),2)
        vif_ser[xvar_names[i]] = vif
    return vif_ser

def feature_selection_vif(df,vif_thr=5):
    temp_vif = vif_cal(df)
    check = (temp_vif>vif_thr).sum()
    print temp_vif
    if check == 0:
        return df
    else:
        all_col = df.columns
        while check !=0:
            print "In While"
            mx_col =temp_vif.idxmax()
            col2use = list(set(all_col)-set([mx_col]))
            temp_df = df[col2use]
            print "\ncolumn dropped : " + mx_col
            all_col = col2use
            temp_vif = vif_cal(temp_df)
            print temp_vif
            check = (temp_vif>vif_thr).sum()
        return df[col2use]



def stock_sense_overview_card(data_dict_overall):
    overviewCard = NormalCard()
    overviewCard.set_card_name("Overview")
    overviewCardData = []
    summaryData = [
        {
          "name":"Total Articles",
          "value":str(data_dict_overall["number_articles"])
        },
        {
          "name": "Total Sources",
          "value": str(data_dict_overall["number_sources"])
        },
        {
          "name": "Average Sentiment Score",
          "value": str(CommonUtils.round_sig(data_dict_overall["avg_sentiment_score"],sig=2))
        },
        {
          "name": "Overall Stock % Change",
          "value": str(CommonUtils.round_sig(data_dict_overall["stock_percent_change"],sig=2))
        },
        {
          "name": "Max Increase in Price",
          "value": "{} ({})".format(data_dict_overall["max_value_change_overall"][1],data_dict_overall["max_value_change_overall"][0])
        },
        {
          "name": "Max Decrease in Price",
          "value": "{} ({})".format(data_dict_overall["min_value_change_overall"][1],data_dict_overall["min_value_change_overall"][0])
        }
    ]
    summaryDataClass = DataBox(data=summaryData)
    overviewCardData.append(summaryDataClass)

    articlesByStockCardData = data_dict_overall["number_articles_by_stock"]
    plotData = []
    for k,v in articlesByStockCardData.items():
        plotData.append({"name":k,"value":v})
    plotData = sorted(plotData,key=lambda x:x["value"],reverse=True)
    articlesByStockData = NormalChartData(data=plotData)
    chart_json = ChartJson()
    chart_json.set_data(articlesByStockData.get_data())
    chart_json.set_chart_type("bar")
    chart_json.set_axes({"x":"name","y":"value"})
    chart_json.set_label_text({'x':'Stock','y':'No. of Articles'})
    chart_json.set_title("Articles by Stock")
    chart_json.set_subchart(False)
    chart_json.set_yaxis_number_format(".2s")
    articlesByStockChart = C3ChartData(data=chart_json)
    articlesByStockChart.set_width_percent(50)
    overviewCardData.append(articlesByStockChart)

    articlesByConceptCardData = data_dict_overall["number_articles_by_concept"]
    valuesTotal = __builtin__.sum(articlesByConceptCardData.values())
    articlesByConceptCardData = {k:round(float(v)*100/valuesTotal,2) for k,v in articlesByConceptCardData.items()}
    articlesByConceptData = NormalChartData(data=[articlesByConceptCardData])
    chart_json = ChartJson()
    chart_json.set_data(articlesByConceptData.get_data())
    chart_json.set_chart_type("pie")
    chart_json.set_title("Articles by Concept")
    chart_json.set_subchart(False)
    chart_json.set_yaxis_number_format(".2s")
    articlesByConceptChart = C3ChartData(data=chart_json)
    articlesByConceptChart.set_width_percent(50)
    overviewCardData.append(articlesByConceptChart)

    # print data_dict_overall["price_trend"]
    priceTrendData = NormalChartData(data=data_dict_overall["price_trend"])
    chart_json = ChartJson()
    chart_json.set_data(priceTrendData.get_data())
    chart_json.set_subchart(True)
    chart_json.set_title("Stock Performance Analysis")
    chart_json.set_label_text({"x":"DATE","Y":" "})
    chart_json.set_chart_type("line")
    chart_json.set_yaxis_number_format(".2f")
    chart_json.set_axes({"x":"date","y":" "})
    trendChart = C3ChartData(data=chart_json)
    overviewCardData.append(trendChart)

    articlesBySourceCardData = data_dict_overall["number_articles_per_source"]
    plotData = []
    for k,v in articlesBySourceCardData.items():
        plotData.append({"name":k,"value":v})
    plotData = sorted(plotData,key=lambda x:x["value"],reverse=True)
    articlesBySourceData = NormalChartData(data=plotData)
    chart_json = ChartJson()
    chart_json.set_data(articlesBySourceData.get_data())
    chart_json.set_chart_type("bar")
    chart_json.set_axes({"x":"name","y":"value"})
    chart_json.set_label_text({'x':'Source','y':'No. of Articles'})
    chart_json.set_title("Top Sources")
    chart_json.set_subchart(False)
    chart_json.set_yaxis_number_format(".2s")
    articlesBySourceChart = C3ChartData(data=chart_json)
    articlesBySourceChart.set_width_percent(50)
    overviewCardData.append(articlesBySourceChart)



    sentimentByStockCardData = data_dict_overall["stocks_by_sentiment"]
    plotData = []
    for k,v in sentimentByStockCardData.items():
        plotData.append({"name":k,"value":v})
    plotData = sorted(plotData,key=lambda x:x["value"],reverse=True)
    sentimentByStockData = NormalChartData(data=plotData)
    chart_json = ChartJson()
    chart_json.set_data(sentimentByStockData.get_data())
    chart_json.set_chart_type("bar")
    chart_json.set_axes({"x":"name","y":"value"})
    chart_json.set_label_text({'x':'Stock','y':'Avg. Sentiment Score'})
    chart_json.set_title("Sentiment Score by Stocks")
    chart_json.set_subchart(False)
    chart_json.set_yaxis_number_format(".2f")
    sentimentByStockDataChart = C3ChartData(data=chart_json)
    sentimentByStockDataChart.set_width_percent(50)
    overviewCardData.append(sentimentByStockDataChart)

    overviewCard.set_card_data(overviewCardData)
    return overviewCard

def aggregate_concept_stats(conceptDictArray):
    # {"concept":k,"articles":v["articlesCount"],"avgSentiment":v["avgSentiment"]}
    concepts = list(set([obj["concept"].split("__")[0] for obj in conceptDictArray]))
    articlesDict = dict(zip(concepts,[0]*len(concepts)))
    sentimentDict = dict(zip(concepts,[0]*len(concepts)))
    for conceptDict in conceptDictArray:
        for concept in concepts:
            if conceptDict["concept"].split("__")[0] == concept:
                articlesDict[concept] += conceptDict["articles"]
                sentimentDict[concept] += conceptDict["articles"]*conceptDict["avgSentiment"]
    outArray = []
    conceptTableDict = dict(zip(concepts,[[]]*len(concepts)))
    for obj in conceptDictArray:
        conceptName,subConcept = obj["concept"].split("__")
        tableDict = {"text":subConcept,"value":obj["avgSentiment"]}
        existingVal = copy.deepcopy(conceptTableDict[conceptName])
        newVal = existingVal + [tableDict]
        conceptTableDict[conceptName] = newVal
    conceptOrder = sorted([(k,len(v)) for k,v in conceptTableDict.items()],key=lambda x:x[1],reverse=True)
    maxNoSubConcepts = max([len(v) for k,v in conceptTableDict.items()])
    conceptTable = [[x[0] for x in conceptOrder]]
    for idx,val in enumerate(concepts):
        if len(conceptTableDict[val]) < maxNoSubConcepts:
            conceptTableDict[val] += [{"text":"","value":0}]*(maxNoSubConcepts-len(conceptTableDict[val]))
        if articlesDict[val] != 0:
            obj = {"concept":val,"articles":articlesDict[val],"avgSentiment":round(sentimentDict[val]/articlesDict[val],2)}
        else:
            obj = {"concept":val,"articles":articlesDict[val],"avgSentiment":0.0}
        outArray.append(obj)
    outArray = sorted(outArray,key=lambda x:x["articles"],reverse=True)

    conceptTableRows = [list(obj) for obj in np.column_stack(tuple([sorted(conceptTableDict[x[0]],key=lambda k:k["value"] if k["text"] != "" else -99999,reverse=True) for x in conceptOrder]))]
    conceptTable += conceptTableRows
    return outArray,conceptTable

def stock_sense_individual_stock_cards(stockDict):
    allStockNodes = []
    for stockName,dataDict in stockDict.items():
        stockNode = NarrativesTree()
        stockNode.set_name(stockName)
        analysisOverviewCard = NormalCard()
        analysisOverviewCard.set_card_name("Analysis Overview")

        overviewCardData = []
        summaryData = [
            {
              "name":"Total Articles",
              "value":str(dataDict["numArticles"])
            },
            {
              "name": "Total Sources",
              "value": str(dataDict["numSources"])
            },
            {
              "name": "Average Sentiment Score",
              "value": str(CommonUtils.round_sig(dataDict["avgSentimetScore"],sig=2))
            },
            {
              "name": "Change in Stock Value",
              "value": str(CommonUtils.round_sig(dataDict["stockValueChange"],sig=2))
            },
            {
              "name": "Change in Sentiment Score",
              "value": str(CommonUtils.round_sig(dataDict["changeInSentiment"],sig=2))
            },
            {
              "name": "Percent Change in Stock value",
              "value": str(CommonUtils.round_sig(dataDict["stockValuePercentChange"],sig=2))
            }
        ]
        summaryDataClass = DataBox(data=summaryData)
        overviewCardData.append(summaryDataClass)

        sentimentNdArticlesBySource = NormalChartData(data=dataDict["articlesAndSentimentsPerSource"])
        chart_json = ChartJson()
        chart_json.set_data(sentimentNdArticlesBySource.get_data())
        chart_json.set_chart_type("combination")
        chart_json.set_axes({"x":"source","y":"articles","y2":"avgSentiment"})
        chart_json.set_label_text({'x':'Source','y':'No. of Articles',"y2":"Average Sentiment Score"})
        chart_json.set_types({"source":"line","articles":"bar","avgSentiment":"line"})
        chart_json.set_title("Sentiment Score by Source")
        chart_json.set_subchart(False)
        chart_json.set_yaxis_number_format(".2s")
        chart_json.set_y2axis_number_format(".2f")
        sentimentNdArticlesBySourceChart = C3ChartData(data=chart_json)
        sentimentNdArticlesBySourceChart.set_width_percent(50)
        overviewCardData.append(sentimentNdArticlesBySourceChart)

        conceptData = dataDict["articlesAndSentimentsPerConcept"]
        chartData = []
        for k,v in dataDict["articlesAndSentimentsPerConcept"].items():
            chartData.append({"concept":k,"articles":v["articlesCount"],"avgSentiment":v["avgSentiment"]})
        # chartData = sorted(chartData,key=lambda x:x["articles"],reverse=True)
        chartData,conceptSubConceptTableData = aggregate_concept_stats(chartData)
        sentimentNdArticlesByConcept = NormalChartData(data=chartData)
        chart_json = ChartJson()
        chart_json.set_data(sentimentNdArticlesByConcept.get_data())
        chart_json.set_chart_type("combination")
        chart_json.set_axes({"x":"concept","y":"articles","y2":"avgSentiment"})
        chart_json.set_label_text({'x':'concept','y':'No. of Articles',"y2":"Average Sentiment Score"})
        chart_json.set_types({"concept":"line","articles":"bar","avgSentiment":"line"})
        chart_json.set_title("Sentiment Score by Concept")
        chart_json.set_subchart(False)
        chart_json.set_yaxis_number_format(".2s")
        chart_json.set_y2axis_number_format(".2f")
        sentimentNdArticlesByConceptChart = C3ChartData(data=chart_json)
        sentimentNdArticlesByConceptChart.set_width_percent(50)
        overviewCardData.append(sentimentNdArticlesByConceptChart)

        priceAndSentimentTrendData = NormalChartData(data=dataDict["stockPriceAndSentimentTrend"])
        chart_json = ChartJson()
        chart_json.set_data(priceAndSentimentTrendData.get_data())
        chart_json.set_subchart(True)
        chart_json.set_title("Stock Performance Vs Sentiment Score")
        chart_json.set_axes({"x":"date","y":"close","y2":"overallSentiment"})
        chart_json.set_label_text({"x":"Date","Y":"Stock Value","y2":"Sentiment Score"})
        chart_json.set_chart_type("line")
        chart_json.set_yaxis_number_format(".2f")
        chart_json.set_y2axis_number_format(".2f")
        priceAndSentimentTrendChart = C3ChartData(data=chart_json)
        overviewCardData.append(priceAndSentimentTrendChart)

        overviewCardData.append(HtmlData(data="<h3>Top Entities</h3>"))
        wordCloudData = WordCloud(data=dataDict["topEntities"])
        overviewCardData.append(wordCloudData)

        analysisOverviewCard.set_card_data(overviewCardData)
        stockNode.add_a_card(analysisOverviewCard)

        eventAnalysisCard = NormalCard()
        eventAnalysisCard.set_card_name("Event Analysis")
        eventAnalysisCardData = []
        eventAnalysisCardData.append(HtmlData(data="<h3>Key Days and Impactful Articles</h3>"))
        keyDaysTable = TableData()
        keyDaysTableData = dataDict["keyDays"]
        keyDaysTable.set_table_data(keyDaysTableData)
        keyDaysTable.set_table_type("normal")
        eventAnalysisCardData.append(keyDaysTable)
        eventAnalysisCardData.append(HtmlData(data="<h3>Top Articles</h3>"))
        topArticlesTable = TableData()
        topArticlesTableData = dataDict["keyArticles"]
        topArticlesTable.set_table_data(topArticlesTableData)
        topArticlesTable.set_table_type("normal")
        eventAnalysisCardData.append(topArticlesTable)
        eventAnalysisCard.set_card_data(eventAnalysisCardData)
        stockNode.add_a_card(eventAnalysisCard)

        impactAnalysisCard = NormalCard()
        impactAnalysisCard.set_card_name("Impact Analysis")
        impactAnalysisCardData = []
        impactAnalysisCardData.append(HtmlData(data="<h4>Sentiment by Concept</h4>"))
        conceptImpactTable = TableData()
        conceptImpactTable.set_table_type("textHeatMapTable")
        conceptImpactTable.set_table_data(conceptSubConceptTableData)
        impactAnalysisCardData.append(conceptImpactTable)
        impactAnalysisCardData.append(HtmlData(data="<h4>Impact on Stock Price</h4>"))
        impactCoefficients = dataDict["regCoefficient"]
        coefficientsArray = normalize_coefficients(impactCoefficients)
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
        impactAnalysisCardData.append(coefficientsChart)

        if stockDict[stockName].get('recommendations'):
            impactAnalysisCardData.append(HtmlData(data="<h4>Recommendations</h4>"))
        # recommndation_html = "<ul class='list-unstyled bullets_primary'>{}{}{}</ul>".format(stockDict[stockName]['recommendations'][0],stockDict[stockName]['recommendations'][1],stockDict[stockName]['recommendations'][2])
            recommndation_html = "<ul class='list-unstyled bullets_primary'>{}</ul>".format(stockDict[stockName]['recommendations'])

            htmlData = HtmlData(data = recommndation_html)
            impactAnalysisCardData.append(htmlData)
        impactAnalysisCard.set_card_data(impactAnalysisCardData)
        stockNode.add_a_card(impactAnalysisCard)

        allStockNodes.append(stockNode)

    return allStockNodes
