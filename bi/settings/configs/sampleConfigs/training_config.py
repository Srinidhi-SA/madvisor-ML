def get_training_config():
    trainConfigClassification = {
      "config": {
        "COLUMN_SETTINGS": {
          "variableSelection": [
            {
              "polarity": None,
              "setVarAs": None,
              "columnType": "measure",
              "name": "age",
              "selected": True,
              "actualColumnType": "measure",
              "slug": "4027162c25bc426791ad5ea5b86f66c4",
              "targetColSetVarAs": None,
              "dateSuggestionFlag": False,
              "targetColumn": False,
              "uidCol": False
            },
            {
              "polarity": None,
              "setVarAs": None,
              "columnType": "dimension",
              "name": "workclass",
              "selected": True,
              "actualColumnType": "dimension",
              "slug": "360fae82dac34befaef1959cbc48f958",
              "targetColSetVarAs": None,
              "dateSuggestionFlag": False,
              "targetColumn": False,
              "uidCol": False
            },
            {
              "polarity": None,
              "setVarAs": None,
              "columnType": "measure",
              "name": "fnlwgt",
              "selected": True,
              "actualColumnType": "measure",
              "slug": "9a63bb9fe2fa4cfea24680e9285230d5",
              "targetColSetVarAs": None,
              "dateSuggestionFlag": False,
              "targetColumn": False,
              "uidCol": False
            },
            {
              "polarity": None,
              "setVarAs": None,
              "columnType": "dimension",
              "name": "education",
              "selected": True,
              "actualColumnType": "dimension",
              "slug": "ffad161b78434353917c7af7baaf714c",
              "targetColSetVarAs": None,
              "dateSuggestionFlag": False,
              "targetColumn": False,
              "uidCol": False
            },
            {
              "polarity": None,
              "setVarAs": None,
              "columnType": "measure",
              "name": "education-num",
              "selected": True,
              "actualColumnType": "measure",
              "slug": "1f3a3cecacb14ff3bdcb6a19dfa3ec5e",
              "targetColSetVarAs": None,
              "dateSuggestionFlag": False,
              "targetColumn": False,
              "uidCol": False
            },
            {
              "polarity": None,
              "setVarAs": None,
              "columnType": "dimension",
              "name": "marital-status",
              "selected": True,
              "actualColumnType": "dimension",
              "slug": "88dc82c43a234afaa13c79c0b75b4a6d",
              "targetColSetVarAs": None,
              "dateSuggestionFlag": False,
              "targetColumn": False,
              "uidCol": False
            },
            {
              "polarity": None,
              "setVarAs": None,
              "columnType": "dimension",
              "name": "occupation",
              "selected": True,
              "actualColumnType": "dimension",
              "slug": "867e002a86424293a1bdedd5d1842258",
              "targetColSetVarAs": None,
              "dateSuggestionFlag": False,
              "targetColumn": False,
              "uidCol": False
            },
            {
              "polarity": None,
              "setVarAs": None,
              "columnType": "dimension",
              "name": "relationship",
              "selected": True,
              "actualColumnType": "dimension",
              "slug": "9f56667995ef4d069faf5c7dc73a36a2",
              "targetColSetVarAs": None,
              "dateSuggestionFlag": False,
              "targetColumn": False,
              "uidCol": False
            },
            {
              "polarity": None,
              "setVarAs": None,
              "columnType": "dimension",
              "name": "race",
              "selected": True,
              "actualColumnType": "dimension",
              "slug": "57922dd2d8174751ac4ec2b038c5b249",
              "targetColSetVarAs": None,
              "dateSuggestionFlag": False,
              "targetColumn": False,
              "uidCol": False
            },
            {
              "polarity": None,
              "setVarAs": None,
              "columnType": "dimension",
              "name": "sex",
              "selected": True,
              "actualColumnType": "dimension",
              "slug": "ffa0bb5e67c04111b60cfdb307b31246",
              "targetColSetVarAs": None,
              "dateSuggestionFlag": False,
              "targetColumn": False,
              "uidCol": False
            },
            {
              "polarity": None,
              "setVarAs": None,
              "columnType": "measure",
              "name": "Capital-gain",
              "selected": True,
              "actualColumnType": "measure",
              "slug": "a0a5e768300249cdb71a783703bad23c",
              "targetColSetVarAs": None,
              "dateSuggestionFlag": False,
              "targetColumn": False,
              "uidCol": False
            },
            {
              "polarity": None,
              "setVarAs": None,
              "columnType": "measure",
              "name": "Capital-loss",
              "selected": True,
              "actualColumnType": "measure",
              "slug": "f53b09062c3c4ba1a8529c8a0ab3c545",
              "targetColSetVarAs": None,
              "dateSuggestionFlag": False,
              "targetColumn": False,
              "uidCol": False
            },
            {
              "polarity": None,
              "setVarAs": None,
              "columnType": "measure",
              "name": "hours-per-week",
              "selected": True,
              "actualColumnType": "measure",
              "slug": "410e68f42c5d4c1782aa4664e471d546",
              "targetColSetVarAs": None,
              "dateSuggestionFlag": False,
              "targetColumn": False,
              "uidCol": False
            },
            {
              "polarity": None,
              "setVarAs": None,
              "columnType": "dimension",
              "name": "native-country",
              "selected": True,
              "actualColumnType": "dimension",
              "slug": "2274768114cd49fbb4dabb5a88668d34",
              "targetColSetVarAs": None,
              "dateSuggestionFlag": False,
              "targetColumn": False,
              "uidCol": False
            },
            {
              "polarity": None,
              "setVarAs": None,
              "columnType": "dimension",
              "name": "class_label",
              "selected": True,
              "actualColumnType": "dimension",
              "slug": "1e829e7c75ec4bffbe4ab9c0b3fbbf76",
              "targetColSetVarAs": None,
              "dateSuggestionFlag": False,
              "targetColumn": True,
              "uidCol": False
            }
          ]
        },
        "ALGORITHM_SETTING": [
          {
            "description": "A statistical method to predict the likely outcome of any qualitative attribute. It is invariably used for predicting binary outcomes (such as Yes or No).",
            "parameters": [
              {
                "expectedDataType": [
                  "bool"
                ],
                "displayName": "Fit Intercept",
                "name": "fit_intercept",
                "paramType": "list",
                "defaultValue": [
                  {
                    "selected": False,
                    "displayName": "False",
                    "name": "False"
                  },
                  {
                    "selected": True,
                    "displayName": "True",
                    "name": "True"
                  }
                ],
                "hyperpatameterTuningCandidate": True,
                "uiElemType": "checkbox",
                "description": "Specifies if a constant(a.k.a bias or intercept) should be added to the decision function",
                "display": True,
                "allowedDataType": [
                  "bool"
                ]
              },
              {
                "expectedDataType": [
                  "string"
                ],
                "displayName": "Solver Used",
                "name": "solver",
                "paramType": "list",
                "defaultValue": [
                  {
                    "penalty": "l2",
                    "selected": False,
                    "displayName": "newton-cg",
                    "name": "newton-cg"
                  },
                  {
                    "selected": True,
                    "displayName": "lbfgs",
                    "name": "lbfgs"
                  },
                  {
                    "penalty": "l2",
                    "selected": False,
                    "displayName": "sag",
                    "name": "sag"
                  },
                  {
                    "penalty": "l1",
                    "selected": False,
                    "displayName": "saga",
                    "name": "saga"
                  }
                ],
                "hyperpatameterTuningCandidate": True,
                "uiElemType": "checkbox",
                "description": "Algorithm to use in the Optimization",
                "display": True,
                "allowedDataType": [
                  "string"
                ]
              },
              {
                "expectedDataType": [
                  "string"
                ],
                "displayName": "Multiclass Option",
                "name": "multi_class",
                "paramType": "list",
                "defaultValue": [
                  {
                    "selected": True,
                    "displayName": "One Vs Rest",
                    "name": "ovr"
                  },
                  {
                    "selected": False,
                    "displayName": "Multinomial",
                    "name": "multinomial"
                  }
                ],
                "hyperpatameterTuningCandidate": False,
                "uiElemType": "checkbox",
                "description": "Optimization Strategy to use for multi class Target values",
                "display": True,
                "allowedDataType": [
                  "string"
                ]
              },
              {
                "expectedDataType": [
                  "int"
                ],
                "displayName": "Maximum Solver Iterations",
                "description": "Maximum number of iterations taken for the solvers to converge",
                "display": True,
                "paramType": "number",
                "acceptedValue": None,
                "valueRange": [
                  10,
                  400
                ],
                "hyperpatameterTuningCandidate": True,
                "uiElemType": "slider",
                "allowedDataType": [
                  "int"
                ],
                "defaultValue": 100,
                "name": "max_iter"
              },
              {
                "expectedDataType": [
                  "int"
                ],
                "displayName": "No Of Jobs",
                "description": "Number of CPU cores used when parallelizing over classes",
                "display": True,
                "paramType": "number",
                "acceptedValue": None,
                "valueRange": [
                  -1,
                  4
                ],
                "hyperpatameterTuningCandidate": False,
                "uiElemType": "slider",
                "allowedDataType": [
                  "int"
                ],
                "defaultValue": 1,
                "name": "n_jobs"
              },
              {
                "expectedDataType": [
                  "bool"
                ],
                "displayName": "Warm Start",
                "name": "warm_start",
                "paramType": "list",
                "defaultValue": [
                  {
                    "selected": True,
                    "displayName": "False",
                    "name": "False"
                  },
                  {
                    "selected": False,
                    "displayName": "True",
                    "name": "True"
                  }
                ],
                "hyperpatameterTuningCandidate": False,
                "uiElemType": "checkbox",
                "description": "When set to True, reuse the solution of the previous call to fit as initialization, otherwise, just erase the previous solution. Useless for liblinear solver",
                "display": True,
                "allowedDataType": [
                  "bool"
                ]
              },
              {
                "expectedDataType": [
                  "int"
                ],
                "displayName": "Random Seed",
                "description": "The seed of the pseudo random number generator to use when shuffling the data",
                "display": True,
                "paramType": "number",
                "acceptedValue": None,
                "valueRange": [
                  1,
                  100
                ],
                "hyperpatameterTuningCandidate": False,
                "uiElemType": "textBox",
                "allowedDataType": [
                  "int"
                ],
                "defaultValue": None,
                "name": "random_state"
              },
              {
                "expectedDataType": [
                  "int"
                ],
                "displayName": "Convergence tolerance of iterations(e^-n)",
                "description": "Tolerance for stopping criteria",
                "display": True,
                "paramType": "number",
                "acceptedValue": None,
                "valueRange": [
                  3,
                  10
                ],
                "hyperpatameterTuningCandidate": True,
                "uiElemType": "slider",
                "allowedDataType": [
                  "int"
                ],
                "defaultValue": 4,
                "name": "tol"
              },
              {
                "expectedDataType": [
                  "float",
                  "int"
                ],
                "displayName": "Inverse of regularization strength",
                "description": "Must be a positive float, Smaller values specify stronger regularization",
                "display": True,
                "paramType": "number",
                "acceptedValue": None,
                "valueRange": [
                  0.1,
                  20
                ],
                "hyperpatameterTuningCandidate": True,
                "uiElemType": "textBox",
                "allowedDataType": [
                  "float"
                ],
                "defaultValue": 1,
                "name": "C"
              }
            ],
            "selected": True,
            "algorithmSlug": "f77631ce2ab24cf78c55bb6a5fce4db8lr",
            "algorithmName": "Logistic Regression",
            "hyperParameterSetting": [
              {
                "displayName": "Grid Search",
                "selected": False,
                "params": [
                  {
                    "expectedDataType": [
                      None,
                      "string"
                    ],
                    "displayName": "Metric Used for Optimization",
                    "name": "evaluationMetric",
                    "paramType": "list",
                    "display": True,
                    "uiElemType": "dropDown",
                    "defaultValue": [
                      {
                        "selected": True,
                        "displayName": "Accuracy",
                        "name": "accuracy"
                      },
                      {
                        "selected": False,
                        "displayName": "Precision",
                        "name": "precision"
                      },
                      {
                        "selected": False,
                        "displayName": "Recall",
                        "name": "recall"
                      },
                      {
                        "selected": False,
                        "displayName": "ROC-AUC",
                        "name": "roc_auc"
                      }
                    ]
                  },
                  {
                    "expectedDataType": [
                      None,
                      "int"
                    ],
                    "displayName": "No Of Folds to Use",
                    "name": "kFold",
                    "display": True,
                    "paramType": "number",
                    "acceptedValue": None,
                    "valueRange": [
                      2,
                      10
                    ],
                    "uiElemType": "slider",
                    "defaultValue": 3
                  }
                ],
                "name": "gridsearchcv"
              },
              {
                "displayName": "None",
                "selected": True,
                "params": None,
                "name": "none"
              }
            ]
          },
          {
            "description": "A meta estimator that uses averaging predictive power of a number of decision tree\n                classification models. This is very effective in predicting the likelihood in multi-class\n                classifications and also to control overfitting.",
            "parameters": [
              {
                "expectedDataType": [
                  "string"
                ],
                "displayName": "Criterion",
                "name": "criterion",
                "paramType": "list",
                "defaultValue": [
                  {
                    "selected": True,
                    "displayName": "Gini Impurity",
                    "name": "gini"
                  },
                  {
                    "selected": False,
                    "displayName": "Entropy",
                    "name": "entropy"
                  }
                ],
                "hyperpatameterTuningCandidate": True,
                "uiElemType": "checkbox",
                "description": "The function to measure the quality of a split",
                "display": True,
                "allowedDataType": [
                  "string"
                ]
              },
              {
                "expectedDataType": [
                  "int",
                  None
                ],
                "displayName": "Max Depth",
                "description": "The maximum depth of the tree",
                "display": True,
                "paramType": "number",
                "acceptedValue": None,
                "valueRange": [
                  2,
                  20
                ],
                "hyperpatameterTuningCandidate": True,
                "uiElemType": "slider",
                "allowedDataType": [
                  "int",
                  None
                ],
                "defaultValue": None,
                "name": "max_depth"
              },
              {
                "expectedDataType": [
                  "int"
                ],
                "displayName": "Minimum Instances For Split",
                "description": "The minimum number of samples required to split an internal node",
                "display": True,
                "paramType": "number",
                "acceptedValue": None,
                "valueRange": [
                  2,
                  10
                ],
                "hyperpatameterTuningCandidate": True,
                "uiElemType": "slider",
                "allowedDataType": [
                  "int",
                  "float"
                ],
                "defaultValue": 2,
                "name": "min_samples_split"
              },
              {
                "expectedDataType": [
                  "int"
                ],
                "displayName": "Minimum Instances For Leaf Node",
                "description": "The minimum number of samples required to be at a leaf node",
                "display": True,
                "paramType": "number",
                "acceptedValue": None,
                "valueRange": [
                  1,
                  100
                ],
                "hyperpatameterTuningCandidate": True,
                "uiElemType": "slider",
                "allowedDataType": [
                  "int",
                  "float"
                ],
                "defaultValue": 1,
                "name": "min_samples_leaf"
              },
              {
                "expectedDataType": [
                  "int",
                  None
                ],
                "displayName": "Max Leaf Nodes",
                "description": "The maximum of number of leaf nodes",
                "display": True,
                "paramType": "number",
                "acceptedValue": None,
                "valueRange": [

                ],
                "hyperpatameterTuningCandidate": False,
                "uiElemType": "textBox",
                "allowedDataType": [
                  "int",
                  None
                ],
                "defaultValue": None,
                "name": "max_leaf_nodes"
              },
              {
                "expectedDataType": [
                  "float"
                ],
                "displayName": "Impurity Decrease cutoff for Split",
                "description": "A node will be split if this split induces a decrease of the impurity greater than or equal to this value",
                "display": True,
                "paramType": "number",
                "acceptedValue": None,
                "valueRange": [
                  0,
                  1
                ],
                "hyperpatameterTuningCandidate": True,
                "uiElemType": "slider",
                "allowedDataType": [
                  "float"
                ],
                "defaultValue": 0,
                "name": "min_impurity_decrease"
              },
              {
                "expectedDataType": [
                  "int",
                  None
                ],
                "displayName": "Random Seed",
                "description": "The seed of the pseudo random number generator to use when shuffling the data",
                "display": True,
                "paramType": "number",
                "acceptedValue": None,
                "valueRange": [
                  1,
                  100
                ],
                "hyperpatameterTuningCandidate": False,
                "uiElemType": "textBox",
                "allowedDataType": [
                  "int",
                  None
                ],
                "defaultValue": None,
                "name": "random_state"
              },
              {
                "expectedDataType": [
                  "int"
                ],
                "displayName": "No of Estimators",
                "description": "The number of trees in the forest",
                "display": True,
                "paramType": "number",
                "acceptedValue": None,
                "valueRange": [
                  10,
                  1000
                ],
                "hyperpatameterTuningCandidate": True,
                "uiElemType": "slider",
                "allowedDataType": [
                  "int"
                ],
                "defaultValue": 10,
                "name": "n_estimators"
              },
              {
                "expectedDataType": [
                  "bool"
                ],
                "displayName": "Bootstrap Sampling",
                "name": "bootstrap",
                "paramType": "list",
                "defaultValue": [
                  {
                    "selected": False,
                    "displayName": "False",
                    "name": "False"
                  },
                  {
                    "selected": True,
                    "displayName": "True",
                    "name": "True"
                  }
                ],
                "hyperpatameterTuningCandidate": True,
                "uiElemType": "checkbox",
                "description": "It defines whether bootstrap samples are used when building trees",
                "display": True,
                "allowedDataType": [
                  "bool"
                ]
              },
              {
                "expectedDataType": [
                  "bool"
                ],
                "displayName": "use out-of-bag samples",
                "name": "oob_score",
                "paramType": "list",
                "defaultValue": [
                  {
                    "selected": True,
                    "displayName": "False",
                    "name": "False"
                  },
                  {
                    "selected": False,
                    "displayName": "True",
                    "name": "True"
                  }
                ],
                "hyperpatameterTuningCandidate": False,
                "uiElemType": "checkbox",
                "description": "It defines whether to use out-of-bag samples to estimate the R^2 on unseen data",
                "display": False,
                "allowedDataType": [
                  "bool"
                ]
              },
              {
                "expectedDataType": [
                  "int"
                ],
                "displayName": "No Of Jobs",
                "description": "The number of jobs to run in parallel for both fit and predict",
                "display": True,
                "paramType": "number",
                "acceptedValue": None,
                "valueRange": [
                  -1,
                  4
                ],
                "hyperpatameterTuningCandidate": False,
                "uiElemType": "slider",
                "allowedDataType": [
                  "int"
                ],
                "defaultValue": 1,
                "name": "n_jobs"
              },
              {
                "expectedDataType": [
                  "bool"
                ],
                "displayName": "Warm Start",
                "name": "warm_start",
                "paramType": "list",
                "defaultValue": [
                  {
                    "selected": True,
                    "displayName": "False",
                    "name": "False"
                  },
                  {
                    "selected": False,
                    "displayName": "True",
                    "name": "True"
                  }
                ],
                "hyperpatameterTuningCandidate": False,
                "uiElemType": "checkbox",
                "description": "When set to True, reuse the solution of the previous call to fit as initialization",
                "display": False,
                "allowedDataType": [
                  "bool"
                ]
              }
            ],
            "selected": True,
            "algorithmSlug": "f77631ce2ab24cf78c55bb6a5fce4db8rf",
            "algorithmName": "Random Forest",
            "hyperParameterSetting": [
              {
                "displayName": "Grid Search",
                "selected": False,
                "params": [
                  {
                    "expectedDataType": [
                      None,
                      "string"
                    ],
                    "displayName": "Metric Used for Optimization",
                    "name": "evaluationMetric",
                    "paramType": "list",
                    "display": True,
                    "uiElemType": "dropDown",
                    "defaultValue": [
                      {
                        "selected": True,
                        "displayName": "Accuracy",
                        "name": "accuracy"
                      },
                      {
                        "selected": False,
                        "displayName": "Precision",
                        "name": "precision"
                      },
                      {
                        "selected": False,
                        "displayName": "Recall",
                        "name": "recall"
                      },
                      {
                        "selected": False,
                        "displayName": "ROC-AUC",
                        "name": "roc_auc"
                      }
                    ]
                  },
                  {
                    "expectedDataType": [
                      None,
                      "int"
                    ],
                    "displayName": "No Of Folds to Use",
                    "name": "kFold",
                    "display": True,
                    "paramType": "number",
                    "acceptedValue": None,
                    "valueRange": [
                      2,
                      10
                    ],
                    "uiElemType": "slider",
                    "defaultValue": 3
                  }
                ],
                "name": "gridsearchcv"
              },
              {
                "displayName": "None",
                "selected": True,
                "params": None,
                "name": "none"
              }
            ]
          },
          {
            "description": "A machine learning technique that produces an ensemble of multiple decision tree\n                models to predict categorical variables. It is highly preferred to leverage\n                computational power to build scalable and accurate models.",
            "parameters": [
              {
                "expectedDataType": [
                  "string"
                ],
                "displayName": "Booster Function",
                "name": "booster",
                "paramType": "list",
                "defaultValue": [
                  {
                    "selected": True,
                    "displayName": "gbtree",
                    "name": "gbtree"
                  },
                  {
                    "selected": False,
                    "displayName": "dart",
                    "name": "dart"
                  },
                  {
                    "selected": False,
                    "displayName": "gblinear",
                    "name": "gblinear"
                  }
                ],
                "hyperpatameterTuningCandidate": True,
                "uiElemType": "checkbox",
                "description": "The booster function to be used",
                "display": True,
                "allowedDataType": [
                  "string"
                ]
              },
              {
                "expectedDataType": [
                  "int"
                ],
                "displayName": "Print Messages on Console",
                "name": "silent",
                "paramType": "list",
                "defaultValue": [
                  {
                    "selected": False,
                    "displayName": "True",
                    "name": 0
                  },
                  {
                    "selected": True,
                    "displayName": "False",
                    "name": 1
                  }
                ],
                "hyperpatameterTuningCandidate": False,
                "uiElemType": "checkbox",
                "description": "Runtime Message Printing",
                "display": False,
                "allowedDataType": [
                  "int"
                ]
              },
              {
                "expectedDataType": [
                  "float"
                ],
                "displayName": "Learning Rate",
                "description": "It is the step size shrinkage used to prevent Overfitting",
                "display": True,
                "paramType": "number",
                "acceptedValue": None,
                "valueRange": [
                  0,
                  1
                ],
                "hyperpatameterTuningCandidate": True,
                "uiElemType": "slider",
                "allowedDataType": [
                  "float"
                ],
                "defaultValue": 0.3,
                "name": "eta"
              },
              {
                "expectedDataType": [
                  "int"
                ],
                "displayName": "Minimum Loss Reduction",
                "description": "It is the minimum loss reduction required to make a further partition on a leaf node of the tree",
                "display": True,
                "paramType": "number",
                "acceptedValue": None,
                "valueRange": [
                  0,
                  100
                ],
                "hyperpatameterTuningCandidate": True,
                "uiElemType": "slider",
                "allowedDataType": [
                  "int"
                ],
                "defaultValue": 0,
                "name": "gamma"
              },
              {
                "expectedDataType": [
                  "int"
                ],
                "displayName": "Maximum Depth",
                "description": "The maximum depth of a tree",
                "display": True,
                "paramType": "number",
                "acceptedValue": None,
                "valueRange": [
                  0,
                  100
                ],
                "hyperpatameterTuningCandidate": True,
                "uiElemType": "slider",
                "allowedDataType": [
                  "int"
                ],
                "defaultValue": 6,
                "name": "max_depth"
              },
              {
                "expectedDataType": [
                  "int"
                ],
                "displayName": "Minimum Child Weight",
                "description": "The Minimum sum of Instance weight needed in a child node",
                "display": True,
                "paramType": "number",
                "acceptedValue": None,
                "valueRange": [
                  0,
                  100
                ],
                "hyperpatameterTuningCandidate": False,
                "uiElemType": "slider",
                "allowedDataType": [
                  "int"
                ],
                "defaultValue": 1,
                "name": "min_child_weight"
              },
              {
                "expectedDataType": [
                  "float"
                ],
                "displayName": "Subsampling Ratio",
                "description": "It is the subsample ratio of the training instance",
                "display": True,
                "paramType": "number",
                "acceptedValue": None,
                "valueRange": [
                  0.1,
                  1
                ],
                "hyperpatameterTuningCandidate": True,
                "uiElemType": "slider",
                "allowedDataType": [
                  "float"
                ],
                "defaultValue": 1,
                "name": "subsample"
              },
              {
                "expectedDataType": [
                  "float"
                ],
                "displayName": "subsample ratio of columns for each tree",
                "description": "It is the subsample ratio of columns when constructing each tree",
                "display": True,
                "paramType": "number",
                "acceptedValue": None,
                "valueRange": [
                  0.1,
                  1
                ],
                "hyperpatameterTuningCandidate": True,
                "uiElemType": "slider",
                "allowedDataType": [
                  "float"
                ],
                "defaultValue": 1,
                "name": "colsample_bytree"
              },
              {
                "expectedDataType": [
                  "float"
                ],
                "displayName": "subsample ratio of columns for each split",
                "description": "Subsample ratio of columns for each split in each level",
                "display": True,
                "paramType": "number",
                "acceptedValue": None,
                "valueRange": [
                  0.1,
                  1
                ],
                "hyperpatameterTuningCandidate": False,
                "uiElemType": "slider",
                "allowedDataType": [
                  "float"
                ],
                "defaultValue": 1,
                "name": "colsample_bylevel"
              },
              {
                "expectedDataType": [
                  "string"
                ],
                "displayName": "Tree Construction Algorithm",
                "name": "tree_method",
                "paramType": "list",
                "defaultValue": [
                  {
                    "selected": True,
                    "displayName": "auto",
                    "name": "auto"
                  },
                  {
                    "selected": False,
                    "displayName": "exact",
                    "name": "exact"
                  },
                  {
                    "selected": False,
                    "displayName": "approx",
                    "name": "approx"
                  },
                  {
                    "selected": False,
                    "displayName": "hist",
                    "name": "hist"
                  },
                  {
                    "selected": False,
                    "displayName": "gpu_exact",
                    "name": "gpu_exact"
                  },
                  {
                    "selected": False,
                    "displayName": "gpu_hist",
                    "name": "gpu_hist"
                  }
                ],
                "hyperpatameterTuningCandidate": True,
                "uiElemType": "checkbox",
                "description": "The Tree construction algorithm used in XGBoost",
                "display": True,
                "allowedDataType": [
                  "string"
                ]
              },
              {
                "expectedDataType": [
                  "string"
                ],
                "displayName": "Type of Predictor Algorithm",
                "name": "predictor",
                "paramType": "list",
                "defaultValue": [
                  {
                    "selected": True,
                    "displayName": "Multicore CPU prediction algorithm",
                    "name": "cpu_predictor"
                  },
                  {
                    "selected": True,
                    "displayName": "Prediction using GPU",
                    "name": "gpu_predictor"
                  }
                ],
                "hyperpatameterTuningCandidate": False,
                "uiElemType": "checkbox",
                "description": "The type of predictor algorithm to use",
                "display": False,
                "allowedDataType": [
                  "string"
                ]
              },
              {
                "expectedDataType": [
                  "string"
                ],
                "displayName": "Process Type",
                "name": "process_type",
                "paramType": "list",
                "defaultValue": [
                  {
                    "selected": True,
                    "displayName": "Create New Trees",
                    "name": "default"
                  },
                  {
                    "selected": True,
                    "displayName": "Update Trees",
                    "name": "update"
                  }
                ],
                "hyperpatameterTuningCandidate": False,
                "uiElemType": "checkbox",
                "description": "Boosting process to run",
                "display": True,
                "allowedDataType": [
                  "string"
                ]
              }
            ],
            "selected": True,
            "algorithmSlug": "f77631ce2ab24cf78c55bb6a5fce4db8xgb",
            "algorithmName": "XGBoost",
            "hyperParameterSetting": [
              {
                "displayName": "Grid Search",
                "selected": False,
                "params": [
                  {
                    "expectedDataType": [
                      None,
                      "string"
                    ],
                    "displayName": "Metric Used for Optimization",
                    "name": "evaluationMetric",
                    "paramType": "list",
                    "display": True,
                    "uiElemType": "dropDown",
                    "defaultValue": [
                      {
                        "selected": True,
                        "displayName": "Accuracy",
                        "name": "accuracy"
                      },
                      {
                        "selected": False,
                        "displayName": "Precision",
                        "name": "precision"
                      },
                      {
                        "selected": False,
                        "displayName": "Recall",
                        "name": "recall"
                      },
                      {
                        "selected": False,
                        "displayName": "ROC-AUC",
                        "name": "roc_auc"
                      }
                    ]
                  },
                  {
                    "expectedDataType": [
                      None,
                      "int"
                    ],
                    "displayName": "No Of Folds to Use",
                    "name": "kFold",
                    "display": True,
                    "paramType": "number",
                    "acceptedValue": None,
                    "valueRange": [
                      2,
                      10
                    ],
                    "uiElemType": "slider",
                    "defaultValue": 3
                  }
                ],
                "name": "gridsearchcv"
              },
              {
                "displayName": "None",
                "selected": True,
                "params": None,
                "name": "none"
              }
            ]
          }
        ],
        "DATA_SOURCE": {
          "datasource_type": "fileUpload",
          "datasource_details": ""
        },
        "FILE_SETTINGS": {
          "app_type": "classification",
          "validationTechnique": [
            {
              "displayName": "K Fold Validation",
              "name": "kFold",
              "value": 2
            }
          ],
          "targetLevel": " <=50K",
          "modelpath": [
            "loki2-2wzcbpxdlj"
          ],
          "analysis_type": [
            "training"
          ],
          "inputfile": [
            "file:///home/gulshan/marlabs/datasets/sampleDatasets/demography.csv"
          ],
          "metadata": {
            "url": "madvisor2.marlabsai.com:80/api/get_metadata_for_mlscripts/",
            "slug_list": [
              "demographycsv-ffxzl7yc2u"
            ]
          }
        }
      },
      "job_config": {
        "message_url": "http://madvisor2.marlabsai.com:80/api/messages/Job_model-loki2-2wzcbpxdlj-ddem4fahih_123/",
        "get_config": {
          "action": "get_config",
          "method": "GET"
        },
        "error_reporting_url": "http://madvisor2.marlabsai.com:80/api/set_job_report/model-loki2-2wzcbpxdlj-ddem4fahih/",
        "set_result": {
          "action": "result",
          "method": "PUT"
        },
        "job_url": "http://madvisor2.marlabsai.com:80/api/job/model-loki2-2wzcbpxdlj-ddem4fahih/",
        "job_type": "training",
        "job_name": "loki2",
        "xml_url": "http://madvisor2.marlabsai.com:80/api/xml/model-loki2-2wzcbpxdlj-ddem4fahih/",
        "app_id": 2
      }
    }
    trainingConfigRegression = {
      "config": {
        "COLUMN_SETTINGS": {
          "variableSelection": [
            {
              "polarity": None,
              "setVarAs": None,
              "columnType": "measure",
              "name": "age",
              "selected": True,
              "actualColumnType": "measure",
              "slug": "4027162c25bc426791ad5ea5b86f66c4",
              "targetColSetVarAs": None,
              "dateSuggestionFlag": False,
              "targetColumn": True,
              "uidCol": False
            },
            {
              "polarity": None,
              "setVarAs": None,
              "columnType": "dimension",
              "name": "workclass",
              "selected": True,
              "actualColumnType": "dimension",
              "slug": "360fae82dac34befaef1959cbc48f958",
              "targetColSetVarAs": None,
              "dateSuggestionFlag": False,
              "targetColumn": False,
              "uidCol": False
            },
            {
              "polarity": None,
              "setVarAs": None,
              "columnType": "measure",
              "name": "fnlwgt",
              "selected": True,
              "actualColumnType": "measure",
              "slug": "9a63bb9fe2fa4cfea24680e9285230d5",
              "targetColSetVarAs": None,
              "dateSuggestionFlag": False,
              "targetColumn": False,
              "uidCol": False
            },
            {
              "polarity": None,
              "setVarAs": None,
              "columnType": "dimension",
              "name": "education",
              "selected": True,
              "actualColumnType": "dimension",
              "slug": "ffad161b78434353917c7af7baaf714c",
              "targetColSetVarAs": None,
              "dateSuggestionFlag": False,
              "targetColumn": False,
              "uidCol": False
            },
            {
              "polarity": None,
              "setVarAs": None,
              "columnType": "measure",
              "name": "education-num",
              "selected": True,
              "actualColumnType": "measure",
              "slug": "1f3a3cecacb14ff3bdcb6a19dfa3ec5e",
              "targetColSetVarAs": None,
              "dateSuggestionFlag": False,
              "targetColumn": False,
              "uidCol": False
            },
            {
              "polarity": None,
              "setVarAs": None,
              "columnType": "dimension",
              "name": "marital-status",
              "selected": True,
              "actualColumnType": "dimension",
              "slug": "88dc82c43a234afaa13c79c0b75b4a6d",
              "targetColSetVarAs": None,
              "dateSuggestionFlag": False,
              "targetColumn": False,
              "uidCol": False
            },
            {
              "polarity": None,
              "setVarAs": None,
              "columnType": "dimension",
              "name": "occupation",
              "selected": True,
              "actualColumnType": "dimension",
              "slug": "867e002a86424293a1bdedd5d1842258",
              "targetColSetVarAs": None,
              "dateSuggestionFlag": False,
              "targetColumn": False,
              "uidCol": False
            },
            {
              "polarity": None,
              "setVarAs": None,
              "columnType": "dimension",
              "name": "relationship",
              "selected": True,
              "actualColumnType": "dimension",
              "slug": "9f56667995ef4d069faf5c7dc73a36a2",
              "targetColSetVarAs": None,
              "dateSuggestionFlag": False,
              "targetColumn": False,
              "uidCol": False
            },
            {
              "polarity": None,
              "setVarAs": None,
              "columnType": "dimension",
              "name": "race",
              "selected": True,
              "actualColumnType": "dimension",
              "slug": "57922dd2d8174751ac4ec2b038c5b249",
              "targetColSetVarAs": None,
              "dateSuggestionFlag": False,
              "targetColumn": False,
              "uidCol": False
            },
            {
              "polarity": None,
              "setVarAs": None,
              "columnType": "dimension",
              "name": "sex",
              "selected": True,
              "actualColumnType": "dimension",
              "slug": "ffa0bb5e67c04111b60cfdb307b31246",
              "targetColSetVarAs": None,
              "dateSuggestionFlag": False,
              "targetColumn": False,
              "uidCol": False
            },
            {
              "polarity": None,
              "setVarAs": None,
              "columnType": "measure",
              "name": "Capital-gain",
              "selected": True,
              "actualColumnType": "measure",
              "slug": "a0a5e768300249cdb71a783703bad23c",
              "targetColSetVarAs": None,
              "dateSuggestionFlag": False,
              "targetColumn": False,
              "uidCol": False
            },
            {
              "polarity": None,
              "setVarAs": None,
              "columnType": "measure",
              "name": "Capital-loss",
              "selected": True,
              "actualColumnType": "measure",
              "slug": "f53b09062c3c4ba1a8529c8a0ab3c545",
              "targetColSetVarAs": None,
              "dateSuggestionFlag": False,
              "targetColumn": False,
              "uidCol": False
            },
            {
              "polarity": None,
              "setVarAs": None,
              "columnType": "measure",
              "name": "hours-per-week",
              "selected": True,
              "actualColumnType": "measure",
              "slug": "410e68f42c5d4c1782aa4664e471d546",
              "targetColSetVarAs": None,
              "dateSuggestionFlag": False,
              "targetColumn": False,
              "uidCol": False
            },
            {
              "polarity": None,
              "setVarAs": None,
              "columnType": "dimension",
              "name": "native-country",
              "selected": True,
              "actualColumnType": "dimension",
              "slug": "2274768114cd49fbb4dabb5a88668d34",
              "targetColSetVarAs": None,
              "dateSuggestionFlag": False,
              "targetColumn": False,
              "uidCol": False
            },
            {
              "polarity": None,
              "setVarAs": None,
              "columnType": "dimension",
              "name": "class_label",
              "selected": True,
              "actualColumnType": "dimension",
              "slug": "1e829e7c75ec4bffbe4ab9c0b3fbbf76",
              "targetColSetVarAs": None,
              "dateSuggestionFlag": False,
              "targetColumn": False,
              "uidCol": False
            }
          ]
        },
        "ALGORITHM_SETTING": [
          {
            "description": "fill in the blanks",
            "parameters": [
              {
                "expectedDataType": [
                  "int"
                ],
                "displayName": "No Of Jobs",
                "description": "Number of CPU cores used when parallelizing over classes",
                "paramType": "number",
                "acceptedValue": None,
                "valueRange": [
                  -1,
                  4
                ],
                "hyperpatameterTuningCandidate": False,
                "uiElemType": "slider",
                "allowedDataType": [
                  "int"
                ],
                "display": True,
                "name": "n_jobs"
              },
              {
                "expectedDataType": [
                  "bool"
                ],
                "displayName": "Fit Intercept",
                "name": "fit_intercept",
                "paramType": "list",
                "defaultValue": [
                  {
                    "selected": False,
                    "displayName": "False",
                    "name": "False"
                  },
                  {
                    "selected": True,
                    "displayName": "True",
                    "name": "True"
                  }
                ],
                "hyperpatameterTuningCandidate": True,
                "uiElemType": "checkbox",
                "description": "It specifies whether to calculate the intercept for this model. If set to False, no intercept will be used in calculations",
                "display": True,
                "allowedDataType": [
                  "bool"
                ]
              },
              {
                "expectedDataType": [
                  "bool"
                ],
                "displayName": "Normalize",
                "name": "normalize",
                "paramType": "list",
                "defaultValue": [
                  {
                    "selected": True,
                    "displayName": "False",
                    "name": "False"
                  },
                  {
                    "selected": False,
                    "displayName": "True",
                    "name": "True"
                  }
                ],
                "hyperpatameterTuningCandidate": True,
                "uiElemType": "checkbox",
                "description": "If True, the regressors X will be normalized before regression",
                "display": True,
                "allowedDataType": [
                  "bool"
                ]
              },
              {
                "expectedDataType": [
                  "bool"
                ],
                "displayName": "Copy X",
                "name": "copy_X",
                "paramType": "list",
                "defaultValue": [
                  {
                    "selected": False,
                    "displayName": "False",
                    "name": "False"
                  },
                  {
                    "selected": True,
                    "displayName": "True",
                    "name": "True"
                  }
                ],
                "hyperpatameterTuningCandidate": True,
                "uiElemType": "checkbox",
                "description": "If True, X will be copied; else, it may be overwritten",
                "display": True,
                "allowedDataType": [
                  "bool"
                ]
              }
            ],
            "selected": True,
            "algorithmSlug": "f77631ce2ab24cf78c55bb6a5fce4db8linr",
            "algorithmName": "Linear Regression",
            "hyperParameterSetting": [
              {
                "displayName": "Grid Search",
                "selected": False,
                "params": [
                  {
                    "expectedDataType": [
                      None,
                      "string"
                    ],
                    "displayName": "Metric Used for Optimization",
                    "name": "evaluationMetric",
                    "paramType": "list",
                    "display": True,
                    "uiElemType": "dropDown",
                    "defaultValue": [
                      {
                        "selected": True,
                        "displayName": "R-Squared",
                        "name": "r2"
                      },
                      {
                        "selected": False,
                        "displayName": "MAE",
                        "name": "neg_mean_absolute_error"
                      },
                      {
                        "selected": False,
                        "displayName": "MSE",
                        "name": "neg_mean_squared_error"
                      },
                      {
                        "selected": False,
                        "displayName": "MSE(log)",
                        "name": "neg_mean_squared_log_error"
                      }
                    ]
                  },
                  {
                    "expectedDataType": [
                      None,
                      "int"
                    ],
                    "displayName": "No Of Folds to Use",
                    "name": "kFold",
                    "display": True,
                    "paramType": "number",
                    "acceptedValue": None,
                    "valueRange": [
                      2,
                      10
                    ],
                    "uiElemType": "slider",
                    "defaultValue": 3
                  }
                ],
                "name": "gridsearchcv"
              },
              {
                "displayName": "None",
                "selected": True,
                "params": None,
                "name": "none"
              }
            ]
          },
          {
            "description": "fill in the blanks",
            "parameters": [
              {
                "expectedDataType": [
                  "string"
                ],
                "displayName": "Loss Function",
                "name": "loss",
                "paramType": "list",
                "defaultValue": [
                  {
                    "selected": True,
                    "displayName": "Least Squares Regression",
                    "name": "ls"
                  },
                  {
                    "selected": False,
                    "displayName": "Least Absolute Deviation",
                    "name": "lad"
                  },
                  {
                    "selected": False,
                    "displayName": "Huber",
                    "name": "huber"
                  },
                  {
                    "selected": False,
                    "displayName": "Quantile Regression",
                    "name": "quantile"
                  }
                ],
                "hyperpatameterTuningCandidate": True,
                "uiElemType": "checkbox",
                "description": "It is the loss function to be optimized",
                "display": True,
                "allowedDataType": [
                  "string"
                ]
              },
              {
                "expectedDataType": [
                  "float"
                ],
                "displayName": "Alpha-Quantile",
                "description": "The alpha-quantile of the huber loss function and the quantile loss function",
                "display": False,
                "paramType": "number",
                "acceptedValue": None,
                "valueRange": [
                  0.1,
                  1
                ],
                "hyperpatameterTuningCandidate": False,
                "uiElemType": "slider",
                "dependentOnDict": {
                  "loss": [
                    "huber",
                    "quantile"
                  ]
                },
                "allowedDataType": [
                  "float"
                ],
                "defaultValue": 0.9,
                "name": "alpha"
              },
              {
                "expectedDataType": [
                  "float"
                ],
                "displayName": "Learning Rate",
                "description": "It shrinks the contribution of each tree by learning_rate",
                "display": True,
                "paramType": "number",
                "acceptedValue": None,
                "valueRange": [
                  0.1,
                  1
                ],
                "hyperpatameterTuningCandidate": True,
                "uiElemType": "slider",
                "allowedDataType": [
                  "float"
                ],
                "defaultValue": 0.1,
                "name": "learning_rate"
              },
              {
                "expectedDataType": [
                  "bool"
                ],
                "displayName": "Warm Start",
                "name": "warm_start",
                "paramType": "list",
                "defaultValue": [
                  {
                    "selected": True,
                    "displayName": "False",
                    "name": "False"
                  },
                  {
                    "selected": False,
                    "displayName": "True",
                    "name": "True"
                  }
                ],
                "hyperpatameterTuningCandidate": False,
                "uiElemType": "checkbox",
                "description": "When set to True, reuse the solution of the previous call to fit as initialization",
                "display": True,
                "allowedDataType": [
                  "bool"
                ]
              }
            ],
            "selected": True,
            "algorithmSlug": "f77631ce2ab24cf78c55bb6a5fce4db8gbtr",
            "algorithmName": "Gradient Boosted Tree Regression",
            "hyperParameterSetting": [
              {
                "displayName": "Grid Search",
                "selected": False,
                "params": [
                  {
                    "expectedDataType": [
                      None,
                      "string"
                    ],
                    "displayName": "Metric Used for Optimization",
                    "name": "evaluationMetric",
                    "paramType": "list",
                    "display": True,
                    "uiElemType": "dropDown",
                    "defaultValue": [
                      {
                        "selected": True,
                        "displayName": "R-Squared",
                        "name": "r2"
                      },
                      {
                        "selected": False,
                        "displayName": "MAE",
                        "name": "neg_mean_absolute_error"
                      },
                      {
                        "selected": False,
                        "displayName": "MSE",
                        "name": "neg_mean_squared_error"
                      },
                      {
                        "selected": False,
                        "displayName": "MSE(log)",
                        "name": "neg_mean_squared_log_error"
                      }
                    ]
                  },
                  {
                    "expectedDataType": [
                      None,
                      "int"
                    ],
                    "displayName": "No Of Folds to Use",
                    "name": "kFold",
                    "display": True,
                    "paramType": "number",
                    "acceptedValue": None,
                    "valueRange": [
                      2,
                      10
                    ],
                    "uiElemType": "slider",
                    "defaultValue": 3
                  }
                ],
                "name": "gridsearchcv"
              },
              {
                "displayName": "None",
                "selected": True,
                "params": None,
                "name": "none"
              }
            ]
          },
          {
            "description": "fill in the blanks",
            "parameters": [
              {
                "expectedDataType": [
                  "int"
                ],
                "displayName": "No. Of Estimators",
                "description": "The number of trees in the forest",
                "display": True,
                "paramType": "number",
                "acceptedValue": None,
                "valueRange": [
                  10,
                  1000
                ],
                "hyperpatameterTuningCandidate": True,
                "uiElemType": "slider",
                "allowedDataType": [
                  "int"
                ],
                "defaultValue": 10,
                "name": "n_estimators"
              },
              {
                "expectedDataType": [
                  "int",
                  None
                ],
                "displayName": "Max Depth Of Trees",
                "description": "The maximum depth of the tree",
                "display": True,
                "paramType": "number",
                "acceptedValue": None,
                "valueRange": [
                  2,
                  20
                ],
                "hyperpatameterTuningCandidate": True,
                "uiElemType": "slider",
                "allowedDataType": [
                  "int",
                  None
                ],
                "defaultValue": 3,
                "name": "max_depth"
              },
              {
                "expectedDataType": [
                  "string"
                ],
                "displayName": "Measure For quality of a split",
                "name": "criterion",
                "paramType": "list",
                "defaultValue": [
                  {
                    "selected": True,
                    "displayName": "Friedman Mse",
                    "name": "friedman_mse"
                  },
                  {
                    "selected": False,
                    "displayName": "Mean Squared Error",
                    "name": "mse"
                  },
                  {
                    "selected": False,
                    "displayName": "Mean Absolute Error",
                    "name": "mae"
                  }
                ],
                "hyperpatameterTuningCandidate": True,
                "uiElemType": "checkbox",
                "description": "The function to measure the quality of a split",
                "display": True,
                "allowedDataType": [
                  "string"
                ]
              },
              {
                "expectedDataType": [
                  "int"
                ],
                "displayName": "Minimum Instances For Split",
                "description": "The minimum number of samples required to split an internal node",
                "display": True,
                "paramType": "number",
                "acceptedValue": None,
                "valueRange": [
                  2,
                  10
                ],
                "hyperpatameterTuningCandidate": True,
                "uiElemType": "slider",
                "allowedDataType": [
                  "int",
                  "float"
                ],
                "defaultValue": 2,
                "name": "min_samples_split"
              },
              {
                "expectedDataType": [
                  "int"
                ],
                "displayName": "Minimum Instances For Leaf Node",
                "description": "The minimum number of samples required to be at a leaf node",
                "display": True,
                "paramType": "number",
                "acceptedValue": None,
                "valueRange": [
                  1,
                  100
                ],
                "hyperpatameterTuningCandidate": True,
                "uiElemType": "slider",
                "allowedDataType": [
                  "int",
                  "float"
                ],
                "defaultValue": 1,
                "name": "min_samples_leaf"
              },
              {
                "expectedDataType": [
                  "float"
                ],
                "displayName": "Sub Sampling Rate",
                "description": "It is the subsample ratio of the training instance",
                "display": True,
                "paramType": "number",
                "acceptedValue": None,
                "valueRange": [
                  0.1,
                  1
                ],
                "hyperpatameterTuningCandidate": True,
                "uiElemType": "slider",
                "allowedDataType": [
                  "float"
                ],
                "defaultValue": 1,
                "name": "subsample"
              },
              {
                "expectedDataType": [
                  "float"
                ],
                "displayName": "Maximum Features for Split",
                "description": "The number of features to consider when looking for the best split",
                "display": True,
                "paramType": "number",
                "acceptedValue": None,
                "valueRange": [
                  0.1,
                  1
                ],
                "hyperpatameterTuningCandidate": True,
                "uiElemType": "slider",
                "allowedDataType": [
                  "float",
                  "int",
                  "string",
                  None
                ],
                "defaultValue": None,
                "name": "max_features"
              },
              {
                "expectedDataType": [
                  "int",
                  None
                ],
                "displayName": "Maximum Number of Leaf Nodes",
                "description": "The maximum of number of leaf nodes",
                "display": True,
                "paramType": "number",
                "acceptedValue": None,
                "valueRange": [

                ],
                "hyperpatameterTuningCandidate": False,
                "uiElemType": "textBox",
                "allowedDataType": [
                  "int",
                  None
                ],
                "defaultValue": None,
                "name": "max_leaf_nodes"
              },
              {
                "expectedDataType": [
                  "float"
                ],
                "displayName": "Impurity Decrease cutoff for Split",
                "description": "A node will be split if this split induces a decrease of the impurity greater than or equal to this value",
                "display": True,
                "paramType": "number",
                "acceptedValue": None,
                "valueRange": [
                  0,
                  1
                ],
                "hyperpatameterTuningCandidate": False,
                "uiElemType": "slider",
                "allowedDataType": [
                  "float"
                ],
                "defaultValue": 0,
                "name": "min_impurity_decrease"
              },
              {
                "expectedDataType": [
                  "int",
                  None
                ],
                "displayName": "Random Seed",
                "description": "The seed of the pseudo random number generator to use when shuffling the data",
                "display": True,
                "paramType": "number",
                "acceptedValue": None,
                "valueRange": [
                  1,
                  100
                ],
                "hyperpatameterTuningCandidate": False,
                "uiElemType": "textBox",
                "allowedDataType": [
                  "int",
                  None
                ],
                "defaultValue": None,
                "name": "random_state"
              },
              {
                "expectedDataType": [
                  "string"
                ],
                "displayName": "Node Split Strategy",
                "name": "splitter",
                "paramType": "list",
                "defaultValue": [
                  {
                    "selected": False,
                    "displayName": "Best split",
                    "name": "best"
                  },
                  {
                    "selected": True,
                    "displayName": "Best random split",
                    "name": "random"
                  }
                ],
                "hyperpatameterTuningCandidate": True,
                "uiElemType": "checkbox",
                "description": "The strategy used to choose the split at each node",
                "display": True,
                "allowedDataType": [
                  "string"
                ]
              }
            ],
            "selected": True,
            "algorithmSlug": "f77631ce2ab24cf78c55bb6a5fce4db8dtreer",
            "algorithmName": "Decision Tree Regression",
            "hyperParameterSetting": [
              {
                "displayName": "Grid Search",
                "selected": False,
                "params": [
                  {
                    "expectedDataType": [
                      None,
                      "string"
                    ],
                    "displayName": "Metric Used for Optimization",
                    "name": "evaluationMetric",
                    "paramType": "list",
                    "display": True,
                    "uiElemType": "dropDown",
                    "defaultValue": [
                      {
                        "selected": True,
                        "displayName": "R-Squared",
                        "name": "r2"
                      },
                      {
                        "selected": False,
                        "displayName": "MAE",
                        "name": "neg_mean_absolute_error"
                      },
                      {
                        "selected": False,
                        "displayName": "MSE",
                        "name": "neg_mean_squared_error"
                      },
                      {
                        "selected": False,
                        "displayName": "MSE(log)",
                        "name": "neg_mean_squared_log_error"
                      }
                    ]
                  },
                  {
                    "expectedDataType": [
                      None,
                      "int"
                    ],
                    "displayName": "No Of Folds to Use",
                    "name": "kFold",
                    "display": True,
                    "paramType": "number",
                    "acceptedValue": None,
                    "valueRange": [
                      2,
                      10
                    ],
                    "uiElemType": "slider",
                    "defaultValue": 3
                  }
                ],
                "name": "gridsearchcv"
              },
              {
                "displayName": "None",
                "selected": True,
                "params": None,
                "name": "none"
              }
            ]
          },
          {
            "description": "fill in the blanks",
            "parameters": [
              {
                "expectedDataType": [
                  "int"
                ],
                "displayName": "No. Of Estimators",
                "description": "The number of trees in the forest",
                "display": True,
                "paramType": "number",
                "acceptedValue": None,
                "valueRange": [
                  10,
                  1000
                ],
                "hyperpatameterTuningCandidate": True,
                "uiElemType": "slider",
                "allowedDataType": [
                  "int"
                ],
                "defaultValue": 10,
                "name": "n_estimators"
              },
              {
                "expectedDataType": [
                  "int",
                  None
                ],
                "displayName": "Max Depth Of Trees",
                "description": "The maximum depth of the tree",
                "display": True,
                "paramType": "number",
                "acceptedValue": None,
                "valueRange": [
                  2,
                  20
                ],
                "hyperpatameterTuningCandidate": True,
                "uiElemType": "slider",
                "allowedDataType": [
                  "int",
                  None
                ],
                "defaultValue": 3,
                "name": "max_depth"
              },
              {
                "expectedDataType": [
                  "string"
                ],
                "displayName": "Measure For quality of a split",
                "name": "criterion",
                "paramType": "list",
                "defaultValue": [
                  {
                    "selected": True,
                    "displayName": "Friedman Mse",
                    "name": "friedman_mse"
                  },
                  {
                    "selected": False,
                    "displayName": "Mean Squared Error",
                    "name": "mse"
                  },
                  {
                    "selected": False,
                    "displayName": "Mean Absolute Error",
                    "name": "mae"
                  }
                ],
                "hyperpatameterTuningCandidate": True,
                "uiElemType": "checkbox",
                "description": "The function to measure the quality of a split",
                "display": True,
                "allowedDataType": [
                  "string"
                ]
              },
              {
                "expectedDataType": [
                  "int"
                ],
                "displayName": "Minimum Instances For Split",
                "description": "The minimum number of samples required to split an internal node",
                "display": True,
                "paramType": "number",
                "acceptedValue": None,
                "valueRange": [
                  2,
                  10
                ],
                "hyperpatameterTuningCandidate": True,
                "uiElemType": "slider",
                "allowedDataType": [
                  "int",
                  "float"
                ],
                "defaultValue": 2,
                "name": "min_samples_split"
              },
              {
                "expectedDataType": [
                  "int"
                ],
                "displayName": "Minimum Instances For Leaf Node",
                "description": "The minimum number of samples required to be at a leaf node",
                "display": True,
                "paramType": "number",
                "acceptedValue": None,
                "valueRange": [
                  1,
                  100
                ],
                "hyperpatameterTuningCandidate": True,
                "uiElemType": "slider",
                "allowedDataType": [
                  "int",
                  "float"
                ],
                "defaultValue": 1,
                "name": "min_samples_leaf"
              },
              {
                "expectedDataType": [
                  "float"
                ],
                "displayName": "Sub Sampling Rate",
                "description": "It is the subsample ratio of the training instance",
                "display": True,
                "paramType": "number",
                "acceptedValue": None,
                "valueRange": [
                  0.1,
                  1
                ],
                "hyperpatameterTuningCandidate": True,
                "uiElemType": "slider",
                "allowedDataType": [
                  "float"
                ],
                "defaultValue": 1,
                "name": "subsample"
              },
              {
                "expectedDataType": [
                  "float"
                ],
                "displayName": "Maximum Features for Split",
                "description": "The number of features to consider when looking for the best split",
                "display": True,
                "paramType": "number",
                "acceptedValue": None,
                "valueRange": [
                  0.1,
                  1
                ],
                "hyperpatameterTuningCandidate": True,
                "uiElemType": "slider",
                "allowedDataType": [
                  "float",
                  "int",
                  "string",
                  None
                ],
                "defaultValue": None,
                "name": "max_features"
              },
              {
                "expectedDataType": [
                  "int",
                  None
                ],
                "displayName": "Maximum Number of Leaf Nodes",
                "description": "The maximum of number of leaf nodes",
                "display": True,
                "paramType": "number",
                "acceptedValue": None,
                "valueRange": [

                ],
                "hyperpatameterTuningCandidate": False,
                "uiElemType": "textBox",
                "allowedDataType": [
                  "int",
                  None
                ],
                "defaultValue": None,
                "name": "max_leaf_nodes"
              },
              {
                "expectedDataType": [
                  "float"
                ],
                "displayName": "Impurity Decrease cutoff for Split",
                "description": "A node will be split if this split induces a decrease of the impurity greater than or equal to this value",
                "display": True,
                "paramType": "number",
                "acceptedValue": None,
                "valueRange": [
                  0,
                  1
                ],
                "hyperpatameterTuningCandidate": False,
                "uiElemType": "slider",
                "allowedDataType": [
                  "float"
                ],
                "defaultValue": 0,
                "name": "min_impurity_decrease"
              },
              {
                "expectedDataType": [
                  "int",
                  None
                ],
                "displayName": "Random Seed",
                "description": "The seed of the pseudo random number generator to use when shuffling the data",
                "display": True,
                "paramType": "number",
                "acceptedValue": None,
                "valueRange": [
                  1,
                  100
                ],
                "hyperpatameterTuningCandidate": False,
                "uiElemType": "textBox",
                "allowedDataType": [
                  "int",
                  None
                ],
                "defaultValue": None,
                "name": "random_state"
              },
              {
                "expectedDataType": [
                  "bool"
                ],
                "displayName": "Bootstrap Sampling",
                "name": "bootstrap",
                "paramType": "list",
                "defaultValue": [
                  {
                    "selected": False,
                    "displayName": "False",
                    "name": "False"
                  },
                  {
                    "selected": True,
                    "displayName": "True",
                    "name": "True"
                  }
                ],
                "hyperpatameterTuningCandidate": True,
                "uiElemType": "checkbox",
                "description": "It defines whether bootstrap samples are used when building trees",
                "display": True,
                "allowedDataType": [
                  "bool"
                ]
              },
              {
                "expectedDataType": [
                  "bool"
                ],
                "displayName": "use out-of-bag samples",
                "name": "oob_score",
                "paramType": "list",
                "defaultValue": [
                  {
                    "selected": False,
                    "displayName": "False",
                    "name": "False"
                  },
                  {
                    "selected": True,
                    "displayName": "True",
                    "name": "True"
                  }
                ],
                "hyperpatameterTuningCandidate": False,
                "uiElemType": "checkbox",
                "description": "It defines whether to use out-of-bag samples to estimate the R^2 on unseen data",
                "display": False,
                "allowedDataType": [
                  "bool"
                ]
              },
              {
                "expectedDataType": [
                  "int"
                ],
                "displayName": "No Of Jobs",
                "description": "The number of jobs to run in parallel for both fit and predict",
                "display": True,
                "paramType": "number",
                "acceptedValue": None,
                "valueRange": [
                  -1,
                  4
                ],
                "hyperpatameterTuningCandidate": False,
                "uiElemType": "slider",
                "allowedDataType": [
                  "int"
                ],
                "defaultValue": 1,
                "name": "n_jobs"
              },
              {
                "expectedDataType": [
                  "bool"
                ],
                "displayName": "Warm Start",
                "name": "warm_start",
                "paramType": "list",
                "defaultValue": [
                  {
                    "selected": True,
                    "displayName": "False",
                    "name": "False"
                  },
                  {
                    "selected": False,
                    "displayName": "True",
                    "name": "True"
                  }
                ],
                "hyperpatameterTuningCandidate": False,
                "uiElemType": "checkbox",
                "description": "When set to True, reuse the solution of the previous call to fit as initialization",
                "display": True,
                "allowedDataType": [
                  "bool"
                ]
              }
            ],
            "selected": True,
            "algorithmSlug": "f77631ce2ab24cf78c55bb6a5fce4db8rfr",
            "algorithmName": "Random Forest Regression",
            "hyperParameterSetting": [
              {
                "displayName": "Grid Search",
                "selected": False,
                "params": [
                  {
                    "expectedDataType": [
                      None,
                      "string"
                    ],
                    "displayName": "Metric Used for Optimization",
                    "name": "evaluationMetric",
                    "paramType": "list",
                    "display": True,
                    "uiElemType": "dropDown",
                    "defaultValue": [
                      {
                        "selected": True,
                        "displayName": "R-Squared",
                        "name": "r2"
                      },
                      {
                        "selected": False,
                        "displayName": "MAE",
                        "name": "neg_mean_absolute_error"
                      },
                      {
                        "selected": False,
                        "displayName": "MSE",
                        "name": "neg_mean_squared_error"
                      },
                      {
                        "selected": False,
                        "displayName": "MSE(log)",
                        "name": "neg_mean_squared_log_error"
                      }
                    ]
                  },
                  {
                    "expectedDataType": [
                      None,
                      "int"
                    ],
                    "displayName": "No Of Folds to Use",
                    "name": "kFold",
                    "display": True,
                    "paramType": "number",
                    "acceptedValue": None,
                    "valueRange": [
                      2,
                      10
                    ],
                    "uiElemType": "slider",
                    "defaultValue": 3
                  }
                ],
                "name": "gridsearchcv"
              },
              {
                "displayName": "None",
                "selected": True,
                "params": None,
                "name": "none"
              }
            ]
          }
        ],
        "DATA_SOURCE": {
          "datasource_type": "fileUpload",
          "datasource_details": ""
        },
        "FILE_SETTINGS": {
          "app_type": "regression",
          "validationTechnique": [
            {
              "displayName": "K Fold Validation",
              "name": "kFold",
              "value": 2
            }
          ],
          "targetLevel": None,
          "modelpath": [
            "nmm-qjvzzooq5k"
          ],
          "analysis_type": [
            "training"
          ],
          "inputfile": [
            "file:///home/gulshan/marlabs/datasets/sampleDatasets/demography.csv"
          ],
          "metadata": {
            "url": "madvisor2.marlabsai.com:80/api/get_metadata_for_mlscripts/",
            "slug_list": [
              "demographycsv-ffxzl7yc2u"
            ]
          }
        }
      },
      "job_config": {
        "message_url": "http://madvisor2.marlabsai.com:80/api/messages/Job_model-nmm-qjvzzooq5k-3pc9nk4a8u_123/",
        "get_config": {
          "action": "get_config",
          "method": "GET"
        },
        "error_reporting_url": "http://madvisor2.marlabsai.com:80/api/set_job_report/model-nmm-qjvzzooq5k-3pc9nk4a8u/",
        "set_result": {
          "action": "result",
          "method": "PUT"
        },
        "job_url": "http://madvisor2.marlabsai.com:80/api/job/model-nmm-qjvzzooq5k-3pc9nk4a8u/",
        "job_type": "training",
        "job_name": "nmm",
        "xml_url": "http://madvisor2.marlabsai.com:80/api/xml/model-nmm-qjvzzooq5k-3pc9nk4a8u/",
        "app_id": 13
      }
    }
    return trainConfigClassification
