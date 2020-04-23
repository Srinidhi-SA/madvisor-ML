from pySparkMLClassificationParams import *
from pySparkMLRegressionParams import *
from sklearnMLClassificationParams import *
from sklearnMLRegressionParams import *

UNIQUE_VALUES_COUNT_CUTOFF_CLASSIFICATION = 20
MODEL_NAME_MAX_LENGTH = 4
CLASSIFICATION_MODEL_EVALUATION_METRIC = "accuracy"
REGRESSION_MODEL_EVALUATION_METRIC = "r2"
SKLEARN_EVAL_METRIC_NAME_DISPLAY_MAP = {
    "r2":"R-Squared",
    "neg_mean_absolute_error":"MAE",
    "neg_mean_squared_error":"MSE",
    "neg_mean_squared_log_error":"MSE(log)",
    "accuracy":"Accuracy",
    "precision":"Precision",
    "recall":"Recall",
    "roc_auc":"ROC-AUC"
}

MAX_NUMBER_OF_MODELS_IN_SUMMARY = 10
REG_SCORE_HIGHLIGHT = False
REG_SCORE_ANOVA_KEY_FACTORS = False

CHISQUARELEVELLIMIT = 10
CHISQUARESIGNIFICANTDIMENSIONTOSHOW = 8

DTREE_TARGET_DIMENSION_MAX_LEVEL = 10
DTREE_OTHER_DIMENSION_MAX_LEVEL = 50

DECISIONTREERKMEANSTARGETNAME = ['Low','Medium','High']
MAPEBINS = [0,5,15,25,100]
HDFS_SECRET_KEY = "xfBmEcr_hFHGqVrTo2gMFpER3ks9x841UcvJbEQJesI="
ALGORITHMRANDOMSLUG = "f77631ce2ab24cf78c55bb6a5fce4db8"
ANOVAMAXLEVEL = 200
BLOCKSPLITTER = "|~NEWBLOCK~|"
BASEFOLDERNAME_MODELS = "mAdvisorModels"
BASEFOLDERNAME_SCORES = "mAdvisorScores"
PROBABILITY_RANGE_FOR_DONUT_CHART = {"0-10":(0,10),"10-20":(10,20),"20-30":(20,30),"30-40":(30,40),"40-50":(40,50),"50-60%":(50,60),"60-70%":(60,70),"70-80%":(70,80),"80-90%":(80,90),"90-100%":(90,100)}

DEFAULT_VALIDATION_OBJECT = {
         "name":"trainAndtest",
         "displayName":"Train and Test",
         "value":0.8
       }

APPS_ID_MAP = {
    '1': {
      'displayName': 'Opportunity Scoring',
      'type': 'CLASSIFICATION',
      'name': 'opportunity_scoring',
      'heading': 'Factors influencing Opportunity Score'
    },
    '2': {
      'displayName': 'Automated Prediction',
      'type': 'CLASSIFICATION',
      'name': 'automated_prediction',
      'heading': 'Feature Importance'
    },
    '3': {
      'displayName': 'Robo Advisor',
      'type': 'ROBO',
      'name': 'robo_advisor_insights',
      'heading': None
    },
    '4': {
      'displayName': 'Speech Analytics',
      'type': 'SPEECH',
      'name': 'speech_analytics',
      'heading': None
    },
    '5': {
      'displayName': 'Stock Sense',
      'type': 'STOCK_SENSE',
      'name': 'stock_sense',
      'heading': None
    },
    '6': {
      'displayName': 'Churn Prediction',
      'type': 'CLASSIFICATION',
      'name': 'churn_prediction',
      'heading': 'Factors influencing Churn'
    },
    '7': {
      'displayName': 'Re-admission Prediction',
      'type': 'CLASSIFICATION',
      'name': 're_admission_prediction',
      'heading': 'Factors influencing Re-admission'
    },
    '8': {
      'displayName': 'Physician Attrition',
      'type': 'CLASSIFICATION',
      'name': 'physician_attrition',
      'heading': 'Factors influencing Attrition'
    },
    '9': {
      'displayName': 'Credit Card Fraud',
      'type': 'CLASSIFICATION',
      'name': 'credit_card_fraud',
      'heading': 'Factors influencing Fraud'
    },
    '10': {
      'displayName': 'Claims Prediction',
      'type': 'CLASSIFICATION',
      'name': 'claims_prediction',
      'heading': 'Factors influencing Claims'
    },
  '11': {
    'displayName': 'Asset Health Prediction',
    'type': 'CLASSIFICATION',
    'name': 'asset_health_prediction',
    'heading': 'Factors influencing Asset Health'
  },
  '12': {
    'displayName': 'Employee Attrition',
    'type': 'CLASSIFICATION',
    'name': 'employee_attrition',
    'heading': 'Factors influencing Attrition'
  },
  '13': {
    'displayName': 'Automated Prediction',
    'type': 'REGRESSION',
    'name': 'regression_app',
    'heading': 'Feature Importance'
  }
}


SLUG_MODEL_MAPPING = {
            ALGORITHMRANDOMSLUG+"rf":"randomforest",
            ALGORITHMRANDOMSLUG+"lr":"logisticregression",
            ALGORITHMRANDOMSLUG+"xgb":"xgboost",
            ALGORITHMRANDOMSLUG+"svm":"svm",
            ALGORITHMRANDOMSLUG+"linr":"linearregression",
            ALGORITHMRANDOMSLUG+"gbtr":"gbtregression",
            ALGORITHMRANDOMSLUG+"dtreer":"dtreeregression",
            ALGORITHMRANDOMSLUG+"rfr":"rfregression"
            }
MODEL_SLUG_MAPPING = {
            "randomforest":ALGORITHMRANDOMSLUG+"rf",
            "logisticregression":ALGORITHMRANDOMSLUG+"lr",
            "xgboost":ALGORITHMRANDOMSLUG+"xgb",
            "svm":ALGORITHMRANDOMSLUG+"svm",
            "linearregression":ALGORITHMRANDOMSLUG+"linr",
            "generalizedlinearregression":ALGORITHMRANDOMSLUG+"linr",
            "gbtregression":ALGORITHMRANDOMSLUG+"gbtr",
            "dtreeregression":ALGORITHMRANDOMSLUG+"dtreer",
            "rfregression":ALGORITHMRANDOMSLUG+"rfr"
            }

SLUG_MODEL_DISPLAY_NAME_MAPPING = {
            ALGORITHMRANDOMSLUG+"rf":"Random Forest",
            ALGORITHMRANDOMSLUG+"lr":"Logistic Regression",
            ALGORITHMRANDOMSLUG+"xgb":"Xgboost",
            ALGORITHMRANDOMSLUG+"svm":"SVM",
            ALGORITHMRANDOMSLUG+"linr":"Linear Regression",
            ALGORITHMRANDOMSLUG+"gbtr":"Gradient Boosted Trees",
            ALGORITHMRANDOMSLUG+"dtreer":"Decision Tree",
            ALGORITHMRANDOMSLUG+"rfr":"Random Forest"
            }

scriptsMapping = {
    "overview" : "Descriptive analysis",
    "performance" : "Measure vs. Dimension",
    "influencer" : "Measure vs. Measure",
    "prediction" : "Predictive modeling",
    "trend" : "Trend",
    "association" : "Dimension vs. Dimension"
}
measureAnalysisRelativeWeight = {
    "initialization":0.25,
    "Descriptive analysis":1,
    "Measure vs. Dimension":3,
    "Measure vs. Measure":3,
    "Trend":1.5,
    "Predictive modeling":1.5
}
dimensionAnalysisRelativeWeight = {
    "initialization":0.25,
    "Descriptive analysis":1,
    "Dimension vs. Dimension":4,
    "Trend":2.5,
    "Predictive modeling":2.5
}



classificationTrainingInitialScriptWeight = {"initialization":{"total":10}}

regressionTrainingInitialScriptWeight = {"initialization":{"total":10}}

mlModelPredictionWeight = {
    "initialization":{"total":10,"script":5,"narratives":5},
    "Descriptive analysis":{"total":20,"script":10,"narratives":10},
    "Measure vs. Dimension":{"total":30,"script":20,"narratives":10},
    "Predictive modeling":{"total":20,"script":10,"narratives":10},
    "algoSlug":{"total":20,"script":10,"narratives":10}
}


regressionAlgoRelativeWeight = {
    ALGORITHMRANDOMSLUG+"linr"  : 1,
    ALGORITHMRANDOMSLUG+"gbtr" : 1,
    ALGORITHMRANDOMSLUG+"rfr"  : 1,
    ALGORITHMRANDOMSLUG+"dtreer" : 1
}

classificationAlgoRelativeWeight = {
    ALGORITHMRANDOMSLUG+"rf"  : 1,
    ALGORITHMRANDOMSLUG+"xgb" : 1,
    ALGORITHMRANDOMSLUG+"lr"  : 1,
    ALGORITHMRANDOMSLUG+"svm" : 2
}

metadataScriptWeight = {
    "initialization":{"total":3,"script":2,"narratives":1},
}
subsettingScriptWeight = {
    "initialization":{"total":3,"script":2,"narratives":1},
}


SUPPORTED_DATETIME_FORMATS = {
            "formats": (
                    '%m/%d/%Y %H:%M', '%d/%m/%Y %H:%M', '%m/%d/%y %H:%M', '%d/%m/%y %H:%M',
                    '%m-%d-%Y %H:%M', '%d-%m-%Y %H:%M', '%m-%d-%y %H:%M', '%d-%m-%y %H:%M',
                    '%b/%d/%Y %H:%M', '%d/%b/%Y %H:%M', '%b/%d/%y %H:%M', '%d/%b/%y %H:%M',
                    '%b-%d-%Y %H:%M', '%d-%b-%Y %H:%M', '%b-%d-%y %H:%M', '%d-%b-%y %H:%M',
                    '%B/%d/%Y %H:%M', '%d/%B/%Y %H:%M', '%B/%d/%y %H:%M', '%d/%B/%y %H:%M',
                    '%B-%d-%Y %H:%M', '%d-%B-%Y %H:%M', '%B-%d-%y %H:%M', '%d-%B-%y %H:%M',
                    '%Y-%m-%d %H:%M', '%Y/%m/%d %H:%M', '%Y-%b-%d %H:%M', '%Y-%B-%d %H:%M',
                    '%m-%d-%Y %r', '%d-%m-%Y %r', '%m-%d-%Y %R',
                    '%d-%m-%Y %R', '%m-%d-%y %r', '%d-%m-%y %r', '%m-%d-%y %R',
                    '%d-%m-%y %R', '%b-%d-%Y %r', '%d-%b-%Y %r', '%Y-%b-%d %r', '%b-%d-%Y %R',
                    '%d-%b-%Y %R', '%b-%d-%y %r', '%d-%b-%y %r', '%b-%d-%y %R', '%d-%b-%y %R',
                    '%B-%d-%Y %r', '%d-%B-%Y %r', '%B-%d-%Y %R', '%d-%B-%y %R',
                    '%d-%B-%Y %R', '%B-%d-%y %r', '%d-%B-%y %r', '%B-%d-%y %R',
                    '%y-%m-%d %R', '%y-%m-%d %r', '%Y-%m-%d %r', '%Y-%B-%d %r',
                    '%d %B %Y', '%d %B %y', '%d %b %y', '%d %b %Y',
                    '%m/%d/%Y', '%d/%m/%Y', '%m/%d/%y', '%d/%m/%y',
                    '%m-%d-%Y', '%d-%m-%Y', '%m-%d-%y', '%d-%m-%y',
                    '%b/%d/%Y', '%d/%b/%Y', '%b/%d/%y', '%d/%b/%y',
                    '%b-%d-%Y', '%d-%b-%Y', '%b-%d-%y', '%d-%b-%y',
                    '%B/%d/%Y', '%d/%B/%Y', '%B/%d/%y', '%d/%B/%y',
                    '%B-%d-%Y', '%d-%B-%Y', '%B-%d-%y', '%d-%B-%y',
                    '%Y-%m-%d', '%Y/%m/%d', '%Y-%b-%d', '%Y-%B-%d',
                    '%b %d, %Y', '%B %d, %Y', '%B %d %Y', '%m/%d/%Y',
                    '%d %B, %Y', '%d %B, %y', '%d %b, %Y', '%d %b, %y',
                    '%m/%d/%y', '%b %Y', '%B %y', '%m/%y', '%m/%Y',
                    '%B%Y', '%b %d,%Y', '%m.%d.%Y', '%m.%d.%y', '%b/%y',
                    '%m - %d - %Y', '%m - %d - %y', '%B %d, %y', '%b %d, %y',
                    '%d-%B', '%d-%b', '%b,%y', '%B,%y', '%b,%Y', '%B,%Y',
                    '%b %Y', '%b %y', '%B %Y', '%B %y', '%b-%y', '%b/%Y', '%b-%Y'),
             "dual_checks": (
                    '%m/%d/%Y %H:%M', '%m/%d/%y %H:%M', '%m-%d-%Y %H:%M', '%m-%d-%y %H:%M',
                    '%m-%d-%Y %r', '%m-%d-%Y %R', '%m-%d-%y %r','%m-%d-%y %R',
                    '%m/%d/%Y %r', '%m/%d/%Y %R', '%m/%d/%y %r', '%m/%d/%y %R',
                    '%m/%d/%Y', '%m/%d/%y', '%m-%d-%Y', '%m-%d-%y',
                    '%m.%d.%Y', '%m.%d.%y', '%m - %d - %Y','%m - %d - %y')
                    }
