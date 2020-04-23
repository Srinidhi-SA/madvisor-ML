from pySparkMLClassificationParams import *
from pySparkMLRegressionParams import *
from sklearnMLClassificationParams import *
from sklearnMLRegressionParams import *
import copy

ALGORITHMRANDOMSLUG = "f77631ce2ab24cf78c55bb6a5fce4db8"
MLENVIRONMENT = "python" #can be python or spark

SKLEARN_CLASSIFICATION_EVALUATION_METRICS = [
        {
            "name":"accuracy",
            "selected":True,
            "displayName":"Accuracy"
        },
        {
            "name":"precision",
            "selected":False,
            "displayName":"Precision"
        },
        {
            "name":"recall",
            "selected":False,
            "displayName":"Recall"
        },
        {
            "name":"roc_auc",
            "selected":False,
            "displayName":"ROC-AUC"
        }
       ]

SKLEARN_REGRESSION_EVALUATION_METRICS = [
        {
            "name":"r2",
            "selected":True,
            "displayName":"R-Squared"
        },
        {
            "name":"neg_mean_absolute_error",
            "selected":False,
            "displayName":"MAE"
        },
        {
            "name":"neg_mean_squared_error",
            "selected":False,
            "displayName":"MSE"
        },
        # {
        #     "name":"neg_mean_squared_log_error",
        #     "selected":False,
        #     "displayName":"MSE(log)"
        # }
       ]

SKLEARN_GRIDSEARCH_PARAMS = [
            {
                "name":"evaluationMetric",
                "displayName":"Metric Used for Optimization",
                "defaultValue":None,
                "paramType":"list",
                "uiElemType":"dropDown",
                "display":True,
                "expectedDataType":[None,"string"]
            },
            # {
            #     "name":"iidAssumption",
            #     "displayName":"Independent and Identical Distributed",
            #      "defaultValue":[
            #             {
            #                 "name":"true",
            #                 "selected":True,
            #                 "displayName":"True"
            #             },
            #             {
            #                 "name":"false",
            #                 "selected":False,
            #                 "displayName":"False"
            #             }
            #            ],
            #     "paramType":"list",
            #     "uiElemType":"dropDown",
            #     "display":True,
            #     "expectedDataType":["string"]
            # },
            {
                "name":"kFold",
                "displayName":"No Of Folds to Use",
                "defaultValue":3,
                "acceptedValue":None,
                "valueRange":[2,10],
                "paramType":"number",
                "uiElemType":"slider",
                "display":True,
                "expectedDataType":[None,"int"]
            }
]
SKLEARN_RANDOMSEARCH_PARAMS = [
            {
                "name":"evaluationMetric",
                "displayName":"Metric Used for Optimization",
                "defaultValue":None,
                "paramType":"list",
                "uiElemType":"dropDown",
                "display":True
            },
            # {
            #     "name":"iidAssumption",
            #     "displayName":"Independent and Identical Distributed",
            #      "defaultValue":[
            #             {
            #                 "name":"true",
            #                 "selected":True,
            #                 "displayName":"True"
            #             },
            #             {
            #                 "name":"false",
            #                 "selected":False,
            #                 "displayName":"False"
            #             }
            #            ],
            #     "paramType":"list",
            #     "uiElemType":"dropDown",
            #     "display":True
            # },
            {
                "name":"kFold",
                "displayName":"No Of Folds to Use",
                "defaultValue":3,
                "acceptedValue":None,
                "valueRange":[2,10],
                "paramType":"number",
                "uiElemType":"slider",
                "display":True
            }
]
SKLEARN_NONE_PARAMS = [
            {
                "name":"evaluationMetric",
                "displayName":"Metric Used for Optimization",
                "defaultValue":[
                       ],
                "paramType":"list",
                "uiElemType":"dropDown",
                "display":True
            },
            # {
            #     "name":"iidAssumption",
            #     "displayName":"Independent and Identical Distributed",
            #      "defaultValue":[
            #            ],
            #     "paramType":"list",
            #     "uiElemType":"dropDown",
            #     "display":True
            # },
            {
                "name":"kFold",
                "displayName":"No Of Folds to Use",
                "defaultValue":3,
                "acceptedValue":None,
                "valueRange":[2,10],
                "paramType":"number",
                "uiElemType":"slider",
                "display":True

            }
]
EMPTY_SKLEARN_HYPERPARAMETER_OBJECT = []

SKLEARN_HYPERPARAMETER_OBJECT = [
    {
        "name":"gridsearchcv",
        "params":SKLEARN_GRIDSEARCH_PARAMS,
        "displayName":"Grid Search",
        "selected":False
    },
    # {
    #     "name":"randomsearchcv",
    #     "params":SKLEARN_RANDOMSEARCH_PARAMS,
    #     "displayName":"Random Search",
    #     "selected": False
    # },
    {
        "name":"none",
        "params":None,
        "displayName":"None",
        "selected": True
    }
]
EMPTY_SKLEARN_HYPERPARAMETER_OBJECT_CLASSIFICATION = copy.deepcopy(EMPTY_SKLEARN_HYPERPARAMETER_OBJECT)
SKLEARN_HYPERPARAMETER_OBJECT_CLASSIFICATION = copy.deepcopy(SKLEARN_HYPERPARAMETER_OBJECT)
SKLEARN_HYPERPARAMETER_OBJECT_CLASSIFICATION[0]["params"][0]["defaultValue"] = SKLEARN_CLASSIFICATION_EVALUATION_METRICS
SKLEARN_HYPERPARAMETER_OBJECT_REGRESSION = copy.deepcopy(SKLEARN_HYPERPARAMETER_OBJECT)
SKLEARN_HYPERPARAMETER_OBJECT_REGRESSION[0]["params"][0]["defaultValue"] = SKLEARN_REGRESSION_EVALUATION_METRICS

PYSPARK_HYPERPARAMETER_OBJECT = [
    {
        "name":"gridsearchcv",
        "params":SKLEARN_GRIDSEARCH_PARAMS,
        "displayName":"Grid Search",
        "selected":False
    },
    {
        "name":"randomsearchcv",
        "params":SKLEARN_RANDOMSEARCH_PARAMS,
        "displayName":"Random Search",
        "selected": False

    },
    {
        "name":"none",
        "params":None,
        "displayName":"None",
        "selected": True
    }
]

if MLENVIRONMENT == "spark":
    ALGORITHM_LIST_REGRESSION={
        "ALGORITHM_SETTING":[
          {
            "algorithmName": "Linear Regression",
            "selected": True,
            "parameters": PYSPARK_ML_LINEAR_REGRESSION_PARAMS,
            "algorithmSlug": ALGORITHMRANDOMSLUG+"linr",
            "hyperParameterSetting": PYSPARK_HYPERPARAMETER_OBJECT,
            "description":"fill in the blanks"
          },
          {
            "algorithmName": "Gradient Boosted Tree Regression",
            "selected": True,
            "parameters": PYSPARK_ML_GBT_REGRESSION_PARAMS,
            "algorithmSlug": ALGORITHMRANDOMSLUG+"gbtr",
            "hyperParameterSetting": PYSPARK_HYPERPARAMETER_OBJECT,
            "description":"fill in the blanks"
          },
          {
            "algorithmName": "Decision Tree Regression",
            "selected": True,
            "parameters": PYSPARK_ML_DTREE_REGRESSION_PARAMS,
            "algorithmSlug": ALGORITHMRANDOMSLUG+"dtreer",
            "hyperParameterSetting": PYSPARK_HYPERPARAMETER_OBJECT,
            "description":"fill in the blanks"
          },
          {
            "algorithmName": "Random Forest Regression",
            "selected": True,
            "parameters": PYSPARK_ML_RF_REGRESSION_PARAMS,
            "algorithmSlug": ALGORITHMRANDOMSLUG+"rfr",
            "hyperParameterSetting": PYSPARK_HYPERPARAMETER_OBJECT,
            "description":"fill in the blanks"
          }
        ]
    }
    ALGORITHM_LIST_CLASSIFICATION = {
        "ALGORITHM_SETTING": [
            # {
            #     "algorithmName": "Logistic Regression",
            #     "selected": True,
            #     "parameters": PYSPARK_ML_LINEAR_REGRESSION_PARAMS,
            #     "algorithmSlug": ALGORITHMRANDOMSLUG + "linr",
            # "hyperParameterSetting": PYSPARK_HYPERPARAMETER_OBJECT,
            # "description":"fill in the blanks"
            # },
            # {
            #     "algorithmName": "Random Forest",
            #     "selected": True,
            #     "parameters": PYSPARK_ML_GBT_REGRESSION_PARAMS,
            #     "algorithmSlug": ALGORITHMRANDOMSLUG + "gbtr",
            # "hyperParameterSetting": PYSPARK_HYPERPARAMETER_OBJECT,
            # "description":"fill in the blanks"
            # },
            # {
            #     "algorithmName": "XGBoost",
            #     "selected": True,
            #     "parameters": PYSPARK_ML_DTREE_REGRESSION_PARAMS,
            #     "algorithmSlug": ALGORITHMRANDOMSLUG + "dtreer",
            #     "hyperParameterSetting": PYSPARK_HYPERPARAMETER_OBJECT,
            # "description":"fill in the blanks"
            # },
            # {
            #     "algorithmName": "SVM",
            #     "selected": True,
            #     "parameters": PYSPARK_ML_RF_REGRESSION_PARAMS,
            #     "algorithmSlug": ALGORITHMRANDOMSLUG + "rfr",
            # "hyperParameterSetting": PYSPARK_HYPERPARAMETER_OBJECT,
            # "description":"fill in the blanks"
            # }
        ]
    }
else:
    ALGORITHM_LIST_REGRESSION={
        "ALGORITHM_SETTING":[
          {
            "algorithmName": "Linear Regression",
            "selected": True,
            "parameters": SKLEARN_ML_LINEAR_REGRESSION_PARAMS,
            "algorithmSlug": ALGORITHMRANDOMSLUG+"linr",
            "hyperParameterSetting":SKLEARN_HYPERPARAMETER_OBJECT_REGRESSION,
            "description":"A statistical method to predict the likely outcome of any quantitative attribute. It is invariably used for estimating values of any numeric variables like sales, number of products, etc."
          },
          {
            "algorithmName": "Gradient Boosted Tree Regression",
            "selected": True,
            "parameters": SKLEARN_ML_GBT_REGRESSION_PARAMS,
            "algorithmSlug": ALGORITHMRANDOMSLUG+"gbtr",
            "hyperParameterSetting": SKLEARN_HYPERPARAMETER_OBJECT_REGRESSION,
            "description":"A machine learning technique that produces an ensemble of multiple decision tree models to predict numeric variables. It is highly preferred to leverage computational power to build scalable and accurate models."

          },
          {
            "algorithmName": "Decision Tree Regression",
            "selected": True,
            "parameters": SKLEARN_ML_DTREE_REGRESSION_PARAMS,
            "algorithmSlug": ALGORITHMRANDOMSLUG+"dtreer",
            "hyperParameterSetting": SKLEARN_HYPERPARAMETER_OBJECT_REGRESSION,
            "description":"A machine learning technique that produces an ensemble of multiple decision tree models to predict numeric variables. It is highly preferred to leverage computational power to build scalable and accurate models."
          },
          {
            "algorithmName": "Random Forest Regression",
            "selected": True,
            "parameters": SKLEARN_ML_RF_REGRESSION_PARAMS,
            "algorithmSlug": ALGORITHMRANDOMSLUG+"rfr",
            "hyperParameterSetting": SKLEARN_HYPERPARAMETER_OBJECT_REGRESSION,
            "description":"A meta estimator that uses averaging predictive power of a number of decision tree classification models. This is very effective in predicting the expected values of numeric variables and also to control overfitting."
          }
        ]
    }
    ALGORITHM_LIST_CLASSIFICATION = {
        "ALGORITHM_SETTING": [
            {
                "algorithmName": "Logistic Regression",
                "selected": True,
                "parameters": SKLEARN_ML_LOGISTIC_REGRESSION_PARAMS,
                "algorithmSlug": ALGORITHMRANDOMSLUG + "lr",
                "hyperParameterSetting": SKLEARN_HYPERPARAMETER_OBJECT_CLASSIFICATION,
                "description":"A statistical method to predict the likely outcome of any qualitative attribute. It is invariably used for predicting binary outcomes (such as Yes or No)."
            },
            {
                "algorithmName": "Random Forest",
                "selected": True,
                "parameters": SKLEANR_ML_RF_CLASSIFICATION_PARAMS,
                "algorithmSlug": ALGORITHMRANDOMSLUG + "rf",
                "hyperParameterSetting": SKLEARN_HYPERPARAMETER_OBJECT_CLASSIFICATION,
                "description":"""A meta estimator that uses averaging predictive power of a number of decision tree
                classification models. This is very effective in predicting the likelihood in multi-class
                classifications and also to control overfitting."""
            },
            {
                "algorithmName": "XGBoost",
                "selected": True,
                "parameters": SKLEARN_ML_XGBOOST_CLASSIFICATION_PARAMS,
                "algorithmSlug": ALGORITHMRANDOMSLUG + "xgb",
                "hyperParameterSetting": SKLEARN_HYPERPARAMETER_OBJECT_CLASSIFICATION,
                "description":"""A machine learning technique that produces an ensemble of multiple decision tree
                models to predict categorical variables. It is highly preferred to leverage
                computational power to build scalable and accurate models."""
            },
            {
                "algorithmName": "naivebayesmul",
                "selected": True,
                "parameters": SKLEARN_ML_NAIVE_BAYES_PARAMS,
                "algorithmSlug": ALGORITHMRANDOMSLUG + "nb",
                "hyperParameterSetting": SKLEARN_HYPERPARAMETER_OBJECT_CLASSIFICATION,
                "description": """The multinomial Naive Bayes classifier is suitable for classification with discrete 
                features (e.g., word counts for text classification). 
                The multinomial distribution normally requires integer feature counts. 
                However, in practice, fractional counts such as tf-idf may also work."""
            },
            # {
            #     "algorithmName": "SVM",
            #     "selected": False,
            #     "parameters": SKLEARN_ML_RF_REGRESSION_PARAMS,
            #     "algorithmSlug": ALGORITHMRANDOMSLUG + "rfr",
            #     "hyperParameterSetting": SKLEARN_HYPERPARAMETER_OBJECT_CLASSIFICATION,
            # "description":"fill in the blanks"
            # }
        ]
    }
