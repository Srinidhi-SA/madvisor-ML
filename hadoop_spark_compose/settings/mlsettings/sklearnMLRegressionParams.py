############################      Regression      ###############################
SKLEARN_ML_LINEAR_REGRESSION_PARAMS = [
            {
                "name":"n_jobs",
                "displayName":"No Of Jobs",
                "description":"Number of CPU cores used when parallelizing over classes",
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
                 "name":"fit_intercept",
                 "displayName":"Fit Intercept",
                 "description":"It specifies whether to calculate the intercept for this model. If set to False, no intercept will be used in calculations",
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
                 "name":"normalize",
                 "displayName":"Normalize",
                 "description":"If True, the regressors X will be normalized before regression",
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
                 "hyperpatameterTuningCandidate":True,
                 "expectedDataType": ["bool"],
                 "allowedDataType":["bool"]

             },
             {
                 "name":"copy_X",
                 "displayName":"Copy X",
                 "description":"If True, X will be copied; else, it may be overwritten",
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

             }
]

SKLEARN_ML_GENERALIZED_LINEAR_REGRESSION_PARAMS = [

]

SKLEARN_SGD_LEARNING_RATES = [
    {"name":"invscaling","selected":True,"displayName":"Inverse Scaling"},
    {"name":"optimal","selected":False,"displayName":"Optimal"},
    {"name":"constant","selected":False,"displayName":"Constant"},
]

SKLEARN_ML_SUPPORTED_LOSS = [
    {"name":"ls","selected":True,"displayName":"Least Squares Regression"},
    {"name":"lad","selected":False,"displayName":"Least Absolute Deviation"},
    {"name":"huber","selected":False,"displayName":"Huber"},
    {"name":"quantile","selected":False,"displayName":"Quantile Regression"},
]
SKLEARN_ML_SUPPORTED_SPLIT_CRITERION_REGRESSION = [
    {"name":"friedman_mse","selected":True,"displayName":"Friedman Mse"},
    {"name":"mse","selected":False,"displayName":"Mean Squared Error"},
    {"name":"mae","selected":False,"displayName":"Mean Absolute Error"},
]

SKLEARN_ML_TREE_BASED_REGRESSION_COMMON_PARAMS = [
                {
                    "name":"n_estimators",
                    "displayName":"No. Of Estimators",
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
                    "name":"max_depth",
                    "displayName":"Max Depth Of Trees",
                    "description":"The maximum depth of the tree",
                    "defaultValue":3,
                    "acceptedValue":None,
                    "valueRange":[2,20],
                    "paramType":"number",
                    "uiElemType":"slider",
                    "display":True,
                    "hyperpatameterTuningCandidate":True,
                    "expectedDataType": ["int", None],
                    "allowedDataType":["int",None]

                },

                {
                    "name":"criterion",
                    "displayName":"Measure For quality of a split",
                    "description":"The function to measure the quality of a split",
                    "defaultValue":[{"name":obj["name"],"selected":obj["selected"],"displayName":obj["displayName"]} for obj in SKLEARN_ML_SUPPORTED_SPLIT_CRITERION_REGRESSION],
                    "paramType":"list",
                    "uiElemType":"checkbox",
                    "display":True,
                    "hyperpatameterTuningCandidate":True,
                    "expectedDataType": ["string"],
                    "allowedDataType":["string"]

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
                    "name":"subsample",
                    "displayName":"Sub Sampling Rate",
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
                    "name":"max_features",
                    "displayName":"Maximum Features for Split",
                    "description":"The number of features to consider when looking for the best split",
                    "defaultValue":None,
                    "acceptedValue":None,
                    "valueRange":[0.1,1.0],
                    "paramType":"number",
                    "uiElemType":"slider",
                    "display":True,
                    "hyperpatameterTuningCandidate":True,
                    "expectedDataType":["float"],
                    "allowedDataType": ["float", "int","string", None]
                },
                {
                    "name":"max_leaf_nodes",
                    "displayName":"Maximum Number of Leaf Nodes",
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
                    "hyperpatameterTuningCandidate":False,
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

SKLEARN_ML_GBT_REGRESSION_PARAMS = [
        {
            "name":"loss",
            "displayName":"Loss Function",
            "description":"It is the loss function to be optimized",
            "defaultValue":[{"name":obj["name"],"selected":obj["selected"],"displayName":obj["displayName"]} for obj in SKLEARN_ML_SUPPORTED_LOSS],
            "paramType":"list",
            "uiElemType":"checkbox",
            "display":True,
            "hyperpatameterTuningCandidate":True,
            "expectedDataType": ["string"],
            "allowedDataType": ["string"]

        },
        {
            "name":"alpha",
            "displayName":"Alpha-Quantile",
            "description":"The alpha-quantile of the huber loss function and the quantile loss function",
            "defaultValue":0.9,
            "acceptedValue":None,
            "valueRange":[0.1,1.0],
            "paramType":"number",
            "uiElemType":"slider",
            "display":False,
            "dependentOnDict":{"loss":["huber","quantile"]},
            "hyperpatameterTuningCandidate":False,
            "expectedDataType": ["float"],
            "allowedDataType": ["float"]

        },
        {
            "name":"learning_rate",
            "displayName":"Learning Rate",
            "description":"It shrinks the contribution of each tree by learning_rate",
            "defaultValue":0.1,
            "acceptedValue":None,
            "valueRange":[0.1,1.0],
            "paramType":"number",
            "uiElemType":"slider",
            "display":True,
            "hyperpatameterTuningCandidate":True,
            "expectedDataType": ["float"],
            "allowedDataType": ["float"]
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
            "display":True,
            "hyperpatameterTuningCandidate":False,
            "expectedDataType": ["bool"],
            "allowedDataType": ["bool"]

        },

]

SKLEARN_ML_RF_REGRESSION_PARAMS = SKLEARN_ML_TREE_BASED_REGRESSION_COMMON_PARAMS + [
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
            "display":True,
            "hyperpatameterTuningCandidate":False,
        "expectedDataType": ["bool"],
        "allowedDataType": ["bool"]
    },
]

SKLEARN_ML_DTREE_REGRESSION_PARAMS = SKLEARN_ML_TREE_BASED_REGRESSION_COMMON_PARAMS + [
        {
            "name":"splitter",
            "displayName":"Node Split Strategy",
            "description":"The strategy used to choose the split at each node",
            "defaultValue":[
             {
                 "name":"best",
                 "selected":False,
                 "displayName":"Best split"
             },
             {
                 "name":"random",
                 "selected":True,
                 "displayName":"Best random split"
             }
            ],
            "paramType":"list",
            "uiElemType":"checkbox",
            "display":True,
            "hyperpatameterTuningCandidate":True,
            "expectedDataType": ["string"],
            "allowedDataType": ["string"]
        },

]
