
############################    Classification    ###############################
SKLEARN_ML_SUPPORTED_PENALTY_CLASSIFICATION = [
    {"name":"gini","selected":False,"displayName":"Gini Impurity"},
    {"name":"entropy","selected":False,"displayName":"Entropy"},
]
SKLEARN_ML_SUPPORTED_MULTICLASS_OPTION = [
    {"name":"ovr","selected":False,"displayName":"One Vs Rest"},
    {"name":"multinomial","selected":False,"displayName":"Multinomial"}
]
SKLEARN_ML_SUPPORTED_SOLVER_CLASSIFICATION = [
    {"name":"newton-cg","selected":False,"displayName":"newton-cg","penalty":"l2"},
    {"name":"lbfgs","selected":False,"displayName":"lbfgs","penalty":"l2"},
    {"name":"sag","selected":False,"displayName":"sag","penalty":"l2"},
    # {"name":"liblinear","selected":False,"displayName":"liblinear","penalty":"l1"},
    {"name":"saga","selected":False,"displayName":"saga","penalty":"l1"},

]
SKLEARN_ML_SUPPORTED_SPLIT_CRITERION_CLASSIFICATION = [
    {"name":"gini","selected":False,"displayName":"Gini Impurity"},
    {"name":"entropy","selected":False,"displayName":"Entropy"},
]

SKLEARN_ML_SUPPORTED_MAX_FEATURES = [
    {"name":"auto","selected":False,"displayName":"sqrt(n_features)"},
    {"name":"sqrt","selected":False,"displayName":"sqrt(n_features)"},
    {"name":"log2","selected":False,"displayName":"log2(n_features)"},
    {"name":None,"selected":False,"displayName":"n_features"}
]


SKLEARN_ML_TREE_BASED_CLASSIFICATION_COMMON_PARAMS = [
                {
                    "name":"criterion",
                    "displayName":"Criterion",
                    "description":"The function to measure the quality of a split",
                    "defaultValue":[obj if obj["name"] != "gini" else {"name":obj["name"],"selected":True,"displayName":obj["displayName"]} for obj in SKLEARN_ML_SUPPORTED_SPLIT_CRITERION_CLASSIFICATION],
                    "paramType":"list",
                    "uiElemType":"checkbox",
                    "display":True,
                    "hyperpatameterTuningCandidate":True,
                    "expectedDataType":["string"],
                    "allowedDataType":["string"]
                },
                {
                    "name":"max_depth",
                    "displayName":"Max Depth",
                    "description":"The maximum depth of the tree",
                    "defaultValue":None,
                    "acceptedValue":None,
                    "valueRange":[2,20],
                    "paramType":"number",
                    "uiElemType":"slider",
                    "display":True,
                    "hyperpatameterTuningCandidate":True,
                    "expectedDataType": ["int",None],
                    "allowedDataType":["int",None]
                },
                {
                    "name":"min_samples_split",
                    "displayName":"Minimum Instances For Split",
                    "description":"The minimum number of samples required to split an internal node",
                    "defaultValue":2,
                    "acceptedValue":None,
                    "valueRange":[2,10],
                    "paramType":"number",
                    "uiElemType":"slider",
                    "display":True,
                    "hyperpatameterTuningCandidate":True,
                    "expectedDataType": ["int"],
                    "allowedDataType":["int", "float"]
                },
                {
                    "name":"min_samples_leaf",
                    "displayName":"Minimum Instances For Leaf Node",
                    "description":"The minimum number of samples required to be at a leaf node",
                    "defaultValue":1,
                    "acceptedValue":None,
                    "valueRange":[1,100],
                    "paramType":"number",
                    "uiElemType":"slider",
                    "display":True,
                    "hyperpatameterTuningCandidate":True,
                    "expectedDataType": ["int"],
                    "allowedDataType": ["int", "float"]
                },
                {
                    "name":"max_leaf_nodes",
                    "displayName":"Max Leaf Nodes",
                    "description":"The maximum of number of leaf nodes",
                    "defaultValue":None,
                    "acceptedValue":None,
                    "valueRange":[],
                    "paramType":"number",
                    "uiElemType":"textBox",
                    "display":True,
                    "hyperpatameterTuningCandidate":False,
                    "expectedDataType": ["int", None],
                    "allowedDataType": ["int",None]
                },
                {
                    "name":"min_impurity_decrease",
                    "displayName":"Impurity Decrease cutoff for Split",
                    "description":"A node will be split if this split induces a decrease of the impurity greater than or equal to this value",
                    "defaultValue":0.0,
                    "acceptedValue":None,
                    "valueRange":[0.0,1.0],
                    "paramType":"number",
                    "uiElemType":"slider",
                    "display":True,
                    "hyperpatameterTuningCandidate":True,
                    "expectedDataType": ["float"],
                    "allowedDataType": ["float"]
                },
                {
                 "name":"random_state",
                 "displayName":"Random Seed",
                 "description":"The seed of the pseudo random number generator to use when shuffling the data",
                 "defaultValue":None,
                 "acceptedValue":None,
                 "valueRange":[1,100],
                 "paramType":"number",
                 "uiElemType":"textBox",
                 "display":True,
                 "hyperpatameterTuningCandidate":False,
                 "expectedDataType": ["int", None],
                 "allowedDataType": ["int", None]
                }
]

SKLEARN_ML_DTREE_CLASSIFICATION_PARAMS = SKLEARN_ML_TREE_BASED_CLASSIFICATION_COMMON_PARAMS + [
        {
            "name":"max_features",
            "displayName":"Maximum Features for Split",
            "description":"The number of features to consider when looking for the best split",
            "defaultValue":[obj if obj["name"] != None else {"name":obj["name"],"selected":True,"displayName":obj["displayName"]} for obj in SKLEARN_ML_SUPPORTED_MAX_FEATURES],
            "paramType":"list",
            "uiElemType":"checkbox",
            "display":True,
            "hyperpatameterTuningCandidate":True,
            "expectedDataType":["string"],
            "allowedDataType":["string"]
        },
        {
            "name":"splitter",
            "displayName":"Node Split Strategy",
            "description":"The strategy used to choose the split at each node",
            "defaultValue":[
             {
                 "name":"best",
                 "selected":True,
                 "displayName":"Best split"
             },
             {
                 "name":"random",
                 "selected":False,
                 "displayName":"Best random split"
             }
            ],
            "paramType":"list",
            "uiElemType":"checkbox",
            "display":True,
            "hyperpatameterTuningCandidate":False,
            "expectedDataType": ["string"],
            "allowedDataType":["bool"]
        },
        {
             "name":"presort",
             "displayName":"Pre Sort",
             "description":"Presort the data to speed up the finding of best splits in fitting",
             "defaultValue":[
             {
                 "name":"false",
                 "selected":True,
                 "displayName":"False"
             },
             {
                 "name":"true",
                 "selected":False,
                 "displayName":"True"
             }
            ],
            "paramType":"list",
            "uiElemType":"checkbox",
            "display":False,
            "hyperpatameterTuningCandidate":False,
            "expectedDataType": ["bool"],
            "allowedDataType":["bool"]
         },


]

SKLEANR_ML_RF_CLASSIFICATION_PARAMS = SKLEARN_ML_TREE_BASED_CLASSIFICATION_COMMON_PARAMS + [
        {
            "name":"n_estimators",
            "displayName":"No of Estimators",
            "description":"The number of trees in the forest",
            "defaultValue":10,
            "acceptedValue":None,
            "valueRange":[10,1000],
            "paramType":"number",
            "uiElemType":"slider",
            "display":True,
            "hyperpatameterTuningCandidate":True,
            "expectedDataType": ["int"],
            "allowedDataType":["int"]
        },
        {
            "name":"bootstrap",
            "displayName":"Bootstrap Sampling",
            "description":"It defines whether bootstrap samples are used when building trees",
            "defaultValue":[
             {
                 "name":"false",
                 "selected":False,
                 "displayName":"False"
             },
             {
                 "name":"true",
                 "selected":True,
                 "displayName":"True"
             }
            ],
            "paramType":"list",
            "uiElemType":"checkbox",
            "display":True,
            "hyperpatameterTuningCandidate":True,
            "expectedDataType": ["bool"],
            "allowedDataType": ["bool"]
        },
        {
            "name":"oob_score",
            "displayName":"use out-of-bag samples",
            "description":"It defines whether to use out-of-bag samples to estimate the R^2 on unseen data",
            "defaultValue":[
             {
                 "name":"false",
                 "selected":True,
                 "displayName":"False"
             },
             {
                 "name":"true",
                 "selected":False,
                 "displayName":"True"
             }
            ],
            "paramType":"list",
            "uiElemType":"checkbox",
            "display":False,
            "hyperpatameterTuningCandidate":False,
            "expectedDataType": ["bool"],
            "allowedDataType": ["bool"]
        },
        {
            "name":"n_jobs",
            "displayName":"No Of Jobs",
            "description":"The number of jobs to run in parallel for both fit and predict",
            "defaultValue":1,
            "acceptedValue":None,
            "valueRange":[-1,4],
            "paramType":"number",
            "uiElemType":"slider",
            "display":True,
            "hyperpatameterTuningCandidate":False,
            "expectedDataType": ["int"],
            "allowedDataType": ["int"]
        },
        {
            "name":"warm_start",
            "displayName":"Warm Start",
            "description":"When set to True, reuse the solution of the previous call to fit as initialization",
            "defaultValue":[
             {
                 "name":"false",
                 "selected":True,
                 "displayName":"False"
             },
             {
                 "name":"true",
                 "selected":False,
                 "displayName":"True"
             }
            ],
            "paramType":"list",
            "uiElemType":"checkbox",
            "display":False,
            "hyperpatameterTuningCandidate":False,
            "expectedDataType": ["bool"],
            "allowedDataType": ["bool"]
        },
]

SKLEARN_ML_LOGISTIC_REGRESSION_PARAMS = [
        {
            "name":"fit_intercept",
            "displayName":"Fit Intercept",
            "description":"Specifies if a constant(a.k.a bias or intercept) should be added to the decision function",
            "defaultValue":[
                 {
                     "name":"false",
                     "selected":False,
                     "displayName":"False"
                 },
                 {
                     "name":"true",
                     "selected":True,
                     "displayName":"True"
                 }
            ],
            "paramType":"list",
            "uiElemType":"checkbox",
            "display":True,
            "hyperpatameterTuningCandidate":True,
            "expectedDataType": ["bool"],
            "allowedDataType":["bool"]
         },
        {
            "name":"solver",
            "displayName":"Solver Used",
            "description": "Algorithm to use in the Optimization",
            "defaultValue":[obj if obj["name"] != "lbfgs" else {"name":obj["name"],"selected":True,"displayName":obj["displayName"]} for obj in SKLEARN_ML_SUPPORTED_SOLVER_CLASSIFICATION],
            "paramType":"list",
            "uiElemType":"checkbox",
            "display":True,
            "hyperpatameterTuningCandidate":True,
            "expectedDataType": ["string"],
            "allowedDataType":["string"]
        },
        {
            "name":"multi_class",
            "displayName":"Multiclass Option",
            "defaultValue":[obj if obj["name"] != "ovr" else {"name":obj["name"],"selected":True,"displayName":obj["displayName"]} for obj in SKLEARN_ML_SUPPORTED_MULTICLASS_OPTION],
            "paramType":"list",
            "uiElemType":"checkbox",
            "display":True,
            "hyperpatameterTuningCandidate":False,
            "expectedDataType": ["string"],
            "allowedDataType":["string"]
        },
        {
            "name":"max_iter",
            "displayName":"Maximum Solver Iterations",
            "defaultValue":100,
            "acceptedValue":None,
            "valueRange":[10,400],
            "paramType":"number",
            "uiElemType":"slider",
            "display":True,
            "hyperpatameterTuningCandidate":True,
            "expectedDataType": ["int"],
            "allowedDataType":["int"]
        },
        {
            "name":"n_jobs",
            "displayName":"No Of Jobs",
            "defaultValue":1,
            "acceptedValue":None,
            "valueRange":[-1,4],
            "paramType":"number",
            "uiElemType":"slider",
            "display":True,
            "hyperpatameterTuningCandidate":False,
            "expectedDataType": ["int"],
            "allowedDataType":["int"]
        },
        {
            "name":"warm_start",
            "displayName":"Warm Start",
            "defaultValue":[
             {
                 "name":"false",
                 "selected":True,
                 "displayName":"False"
             },
             {
                 "name":"true",
                 "selected":False,
                 "displayName":"True"
             }
            ],
            "paramType":"list",
            "uiElemType":"checkbox",
            "display":True,
            "hyperpatameterTuningCandidate":False,
            "expectedDataType": ["bool"],
            "allowedDataType":["bool"]
        },
         {
             "name":"random_state",
             "displayName":"Random Seed",
             "defaultValue":None,
             "acceptedValue":None,
             "valueRange":[1,100],
             "paramType":"number",
             "uiElemType":"textBox",
             "display":True,
             "hyperpatameterTuningCandidate":False,
             "expectedDataType": ["int"],
             "allowedDataType":["int"]
         },
         {
             "name":"tol",
             "displayName":"Convergence tolerance of iterations(e^-n)",
             "defaultValue":4,
             "acceptedValue":None,
             "valueRange":[3,10],
             "paramType":"number",
             "uiElemType":"slider",
             "display":True,
             "hyperpatameterTuningCandidate":True,
             "expectedDataType": ["int"],
             "allowedDataType":["int"]

         },
         {
             "name":"C",
             "displayName":"Inverse of regularization strength",
             "defaultValue":1.0,
             "acceptedValue":None,
             "valueRange":[0.1,20.0],
             "paramType":"number",
             "uiElemType":"textBox",
             "display":True,
             "hyperpatameterTuningCandidate":True,
             "expectedDataType": ["float","int"],
             "allowedDataType":["float"]
         },
]

SKLEARN_ML_SUPPORTED_XGB_BOOSTER = [
    {"name":"gbtree","selected":False,"displayName":"gbtree"},
    {"name":"dart","selected":False,"displayName":"dart"},
    {"name":"gblinear","selected":False,"displayName":"gblinear"},
]

SKLEARN_ML_SUPPORTED_XGB_TREE_ALGORITHMS = [
    {"name":"auto","selected":False,"displayName":"auto"},
    {"name":"exact","selected":False,"displayName":"exact"},
    {"name":"approx","selected":False,"displayName":"approx"},
    {"name":"hist","selected":False,"displayName":"hist"},
    {"name":"gpu_exact","selected":False,"displayName":"gpu_exact"},
    {"name":"gpu_hist","selected":False,"displayName":"gpu_hist"},

]

SKLEARN_ML_XGBOOST_CLASSIFICATION_PARAMS = [
    {
        "name":"booster",
        "displayName" : "Booster Function",
        "description" : "The booster function to be used",
        "defaultValue":[obj if obj["name"] != "gbtree" else {"name":obj["name"],"selected":True,"displayName":obj["displayName"]} for obj in SKLEARN_ML_SUPPORTED_XGB_BOOSTER],
        "paramType":"list",
        "uiElemType":"checkbox",
        "display":True,
        "hyperpatameterTuningCandidate":True,
        "expectedDataType": ["string"],
        "allowedDataType":["string"]
    },
    {
        "name":"silent",
        "displayName":"Print Messages on Console",
        "description" : "Runtime Message Printing",
        "defaultValue":[{"name":0,"selected":False,"displayName":"True"},{"name":1,"selected":True,"displayName":"False"}],
        "paramType":"list",
        "uiElemType":"checkbox",
        "display":False,
        "hyperpatameterTuningCandidate":False,
        "expectedDataType": ["int"],
        "allowedDataType":["int"]
    },
    {
        "name":"eta",
        "displayName":"Learning Rate",
        "description" : "It is the step size shrinkage used to prevent Overfitting",
        "defaultValue":0.3,
        "acceptedValue":None,
        "valueRange":[0.0,1.0],
        "paramType":"number",
        "uiElemType":"slider",
        "display":True,
        "hyperpatameterTuningCandidate":True,
        "expectedDataType": ["float"],
        "allowedDataType":["float"]
    },
    {
        "name":"gamma",
        "displayName":"Minimum Loss Reduction",
        "description" : "It is the minimum loss reduction required to make a further partition on a leaf node of the tree",
        "defaultValue":0,
        "acceptedValue":None,
        "valueRange":[0,100],
        "paramType":"number",
        "uiElemType":"slider",
        "display":True,
        "hyperpatameterTuningCandidate":True,
        "expectedDataType": ["int"],
        "allowedDataType":["int"]
    },
    {
        "name":"max_depth",
        "displayName":"Maximum Depth",
        "description" : "The maximum depth of a tree",
        "defaultValue":6,
        "acceptedValue":None,
        "valueRange":[0,100],
        "paramType":"number",
        "uiElemType":"slider",
        "display":True,
        "hyperpatameterTuningCandidate":True,
        "expectedDataType": ["int"],
        "allowedDataType":["int"]
    },
    {
        "name":"min_child_weight",
        "displayName":"Minimum Child Weight",
        "description":"The Minimum sum of Instance weight needed in a child node",
        "defaultValue":1,
        "acceptedValue":None,
        "valueRange":[0,100],
        "paramType":"number",
        "uiElemType":"slider",
        "display":True,
        "hyperpatameterTuningCandidate":False,
        "expectedDataType": ["int"],
        "allowedDataType":["int"]
    },
    {
        "name":"subsample",
        "displayName":"Subsampling Ratio",
        "description":"It is the subsample ratio of the training instance",
        "defaultValue":1.0,
        "acceptedValue":None,
        "valueRange":[0.1,1.0],
        "paramType":"number",
        "uiElemType":"slider",
        "display":True,
        "hyperpatameterTuningCandidate":True,
        "expectedDataType": ["float"],
        "allowedDataType":["float"]
    },
    {
        "name":"colsample_bytree",
        "displayName":"subsample ratio of columns for each tree",
        "description":"It is the subsample ratio of columns when constructing each tree",
        "defaultValue":1.0,
        "acceptedValue":None,
        "valueRange":[0.1,1.0],
        "paramType":"number",
        "uiElemType":"slider",
        "display":True,
        "hyperpatameterTuningCandidate":True,
        "expectedDataType": ["float"],
        "allowedDataType":["float"]
    },
    {
        "name":"colsample_bylevel",
        "displayName":"subsample ratio of columns for each split",
        "description":"Subsample ratio of columns for each split in each level",
        "defaultValue":1.0,
        "acceptedValue":None,
        "valueRange":[0.1,1.0],
        "paramType":"number",
        "uiElemType":"slider",
        "display":True,
        "hyperpatameterTuningCandidate":False,
        "expectedDataType": ["float"],
        "allowedDataType":["float"]
    },
    {
        "name":"tree_method",
        "displayName":"Tree Construction Algorithm",
        "description":"The Tree construction algorithm used in XGBoost",
        "defaultValue":[obj if obj["name"] != "auto" else {"name":obj["name"],"selected":True,"displayName":obj["displayName"]} for obj in SKLEARN_ML_SUPPORTED_XGB_TREE_ALGORITHMS],
        "paramType":"list",
        "uiElemType":"checkbox",
        "display":True,
        "hyperpatameterTuningCandidate":True,
        "expectedDataType": ["string"],
        "allowedDataType": ["string"]
    },
    {
        "name":"predictor",
        "displayName":"Type of Predictor Algorithm",
        "description":"The type of predictor algorithm to use",
        "defaultValue":[{"name":"cpu_predictor","selected":True,"displayName":"Multicore CPU prediction algorithm"},
                {"name":"gpu_predictor","selected":True,"displayName":"Prediction using GPU"}
            ],
        "paramType":"list",
        "uiElemType":"checkbox",
        "display":False,
        "hyperpatameterTuningCandidate":False,
        "expectedDataType": ["string"],
        "allowedDataType": ["string"]

    },
    {
        "name":"process_type",
        "displayName":"Process Type",
        "description":"Boosting process to run",
        "defaultValue":[{"name":"default","selected":True,"displayName":"Create New Trees"},
                {"name":"update","selected":True,"displayName":"Update Trees"}
            ],
        "paramType":"list",
        "uiElemType":"checkbox",
        "display":True,
        "hyperpatameterTuningCandidate":False,
        "expectedDataType": ["string"],
        "allowedDataType": ["string"]
    },

]
