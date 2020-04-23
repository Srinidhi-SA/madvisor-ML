def get_subsetting_config():
    subsettingConfig = {
      "config": {
        "FILTER_SETTINGS": {
          "measureColumnFilters": [
            {
              "filterType": "valueRange",
              "lowerBound": 9,
              "colname": "education-num",
              "upperBound": 9
            }
          ],
          "dimensionColumnFilters": [

          ],
          "timeDimensionColumnFilters": [

          ]
        },
        "DATA_SOURCE": {
          "datasource_type": "fileUpload",
          "datasource_details": ""
        },
        "COLUMN_SETTINGS": {
          "analysis_type": [
            "metaData"
          ]
        },
        "TRANSFORMATION_SETTINGS": {
          "existingColumns": [
            {
              "slug": "0f37d194687f43e09573aa07326c26b2",
              "name": "age",
              "columnSetting": [
                {
                  "status": False,
                  "actionName": "unique_identifier",
                  "displayName": "Unique Identifier"
                },
                {
                  "status": False,
                  "actionName": "delete",
                  "displayName": "Delete Column"
                },
                {
                  "status": False,
                  "actionName": "rename",
                  "displayName": "Rename Column",
                  "newName": None
                },
                {
                  "status": False,
                  "actionName": "replace",
                  "replaceTypeList": [
                    {
                      "displayName": "Contains",
                      "name": "contains"
                    },
                    {
                      "displayName": "Equal To",
                      "name": "equals"
                    },
                    {
                      "displayName": "Starts With",
                      "name": "startsWith"
                    },
                    {
                      "displayName": "Ends With",
                      "name": "endsWith"
                    }
                  ],
                  "displayName": "Replace Values",
                  "replacementValues": [

                  ]
                },
                {
                  "status": False,
                  "actionName": "data_type",
                  "displayName": "Change Datatype",
                  "listOfActions": [
                    {
                      "status": True,
                      "displayName": "Numeric",
                      "name": "numeric"
                    },
                    {
                      "status": False,
                      "displayName": "Text",
                      "name": "text"
                    }
                  ]
                },
                {
                  "status": False,
                  "actionName": "set_variable",
                  "displayName": "Set Variable as",
                  "listOfActions": [
                    {
                      "status": True,
                      "displayName": "General Numeric",
                      "name": "general_numeric"
                    },
                    {
                      "status": False,
                      "displayName": "Percentage",
                      "name": "percentage"
                    },
                    {
                      "status": False,
                      "displayName": "Index",
                      "name": "index"
                    },
                    {
                      "status": False,
                      "displayName": "Average",
                      "name": "average"
                    }
                  ]
                },
                {
                  "status": False,
                  "actionName": "set_polarity",
                  "displayName": "Set Polarity as",
                  "listOfActions": [
                    {
                      "status": True,
                      "displayName": "Positive",
                      "name": "positive"
                    },
                    {
                      "status": False,
                      "displayName": "Negative",
                      "name": "negative"
                    }
                  ]
                },
                {
                  "status": False,
                  "actionName": "ignore_suggestion",
                  "displayName": "Ignore for Analysis",
                  "previous_status": False
                }
              ]
            },
            {
              "slug": "26dbb1f77f614106bd1a704c9c0c4bb8",
              "name": "education",
              "columnSetting": [
                {
                  "status": False,
                  "actionName": "unique_identifier",
                  "displayName": "Unique Identifier"
                },
                {
                  "status": False,
                  "actionName": "delete",
                  "displayName": "Delete Column"
                },
                {
                  "status": False,
                  "actionName": "rename",
                  "displayName": "Rename Column",
                  "newName": None
                },
                {
                  "status": False,
                  "actionName": "replace",
                  "replaceTypeList": [
                    {
                      "displayName": "Contains",
                      "name": "contains"
                    },
                    {
                      "displayName": "Equal To",
                      "name": "equals"
                    },
                    {
                      "displayName": "Starts With",
                      "name": "startsWith"
                    },
                    {
                      "displayName": "Ends With",
                      "name": "endsWith"
                    }
                  ],
                  "displayName": "Replace Values",
                  "replacementValues": [

                  ]
                },
                {
                  "status": False,
                  "actionName": "ignore_suggestion",
                  "displayName": "Ignore for Analysis",
                  "previous_status": False
                }
              ]
            },
            {
              "slug": "bf209c718c3b406aac15df355030cae3",
              "name": "education-num",
              "columnSetting": [
                {
                  "status": False,
                  "actionName": "unique_identifier",
                  "displayName": "Unique Identifier"
                },
                {
                  "status": False,
                  "actionName": "delete",
                  "displayName": "Delete Column"
                },
                {
                  "status": False,
                  "actionName": "rename",
                  "displayName": "Rename Column",
                  "newName": None
                },
                {
                  "status": False,
                  "actionName": "replace",
                  "replaceTypeList": [
                    {
                      "displayName": "Contains",
                      "name": "contains"
                    },
                    {
                      "displayName": "Equal To",
                      "name": "equals"
                    },
                    {
                      "displayName": "Starts With",
                      "name": "startsWith"
                    },
                    {
                      "displayName": "Ends With",
                      "name": "endsWith"
                    }
                  ],
                  "displayName": "Replace Values",
                  "replacementValues": [

                  ]
                },
                {
                  "status": False,
                  "actionName": "data_type",
                  "displayName": "Change Datatype",
                  "listOfActions": [
                    {
                      "status": True,
                      "displayName": "Numeric",
                      "name": "numeric"
                    },
                    {
                      "status": False,
                      "displayName": "Text",
                      "name": "text"
                    }
                  ]
                },
                {
                  "status": False,
                  "actionName": "set_variable",
                  "displayName": "Set Variable as",
                  "listOfActions": [
                    {
                      "status": True,
                      "displayName": "General Numeric",
                      "name": "general_numeric"
                    },
                    {
                      "status": False,
                      "displayName": "Percentage",
                      "name": "percentage"
                    },
                    {
                      "status": False,
                      "displayName": "Index",
                      "name": "index"
                    },
                    {
                      "status": False,
                      "displayName": "Average",
                      "name": "average"
                    }
                  ]
                },
                {
                  "status": False,
                  "actionName": "set_polarity",
                  "displayName": "Set Polarity as",
                  "listOfActions": [
                    {
                      "status": True,
                      "displayName": "Positive",
                      "name": "positive"
                    },
                    {
                      "status": False,
                      "displayName": "Negative",
                      "name": "negative"
                    }
                  ]
                },
                {
                  "status": False,
                  "actionName": "ignore_suggestion",
                  "displayName": "Ignore for Analysis",
                  "previous_status": False
                }
              ]
            },
            {
              "slug": "c89d460d3d57463e89ec68743687416a",
              "name": "relationship",
              "columnSetting": [
                {
                  "status": False,
                  "actionName": "unique_identifier",
                  "displayName": "Unique Identifier"
                },
                {
                  "status": False,
                  "actionName": "delete",
                  "displayName": "Delete Column"
                },
                {
                  "status": False,
                  "actionName": "rename",
                  "displayName": "Rename Column",
                  "newName": None
                },
                {
                  "status": False,
                  "actionName": "replace",
                  "replaceTypeList": [
                    {
                      "displayName": "Contains",
                      "name": "contains"
                    },
                    {
                      "displayName": "Equal To",
                      "name": "equals"
                    },
                    {
                      "displayName": "Starts With",
                      "name": "startsWith"
                    },
                    {
                      "displayName": "Ends With",
                      "name": "endsWith"
                    }
                  ],
                  "displayName": "Replace Values",
                  "replacementValues": [

                  ]
                },
                {
                  "status": False,
                  "actionName": "ignore_suggestion",
                  "displayName": "Ignore for Analysis",
                  "previous_status": False
                }
              ]
            },
            {
              "slug": "722123903acd4850b83a0b39de91bcc1",
              "name": "race",
              "columnSetting": [
                {
                  "status": False,
                  "actionName": "unique_identifier",
                  "displayName": "Unique Identifier"
                },
                {
                  "status": False,
                  "actionName": "delete",
                  "displayName": "Delete Column"
                },
                {
                  "status": False,
                  "actionName": "rename",
                  "displayName": "Rename Column",
                  "newName": None
                },
                {
                  "status": False,
                  "actionName": "replace",
                  "replaceTypeList": [
                    {
                      "displayName": "Contains",
                      "name": "contains"
                    },
                    {
                      "displayName": "Equal To",
                      "name": "equals"
                    },
                    {
                      "displayName": "Starts With",
                      "name": "startsWith"
                    },
                    {
                      "displayName": "Ends With",
                      "name": "endsWith"
                    }
                  ],
                  "displayName": "Replace Values",
                  "replacementValues": [

                  ]
                },
                {
                  "status": False,
                  "actionName": "ignore_suggestion",
                  "displayName": "Ignore for Analysis",
                  "previous_status": False
                }
              ]
            },
            {
              "slug": "e55473c7a15245b5b24af14a160914bb",
              "name": "sex",
              "columnSetting": [
                {
                  "status": False,
                  "actionName": "unique_identifier",
                  "displayName": "Unique Identifier"
                },
                {
                  "status": False,
                  "actionName": "delete",
                  "displayName": "Delete Column"
                },
                {
                  "status": False,
                  "actionName": "rename",
                  "displayName": "Rename Column",
                  "newName": None
                },
                {
                  "status": False,
                  "actionName": "replace",
                  "replaceTypeList": [
                    {
                      "displayName": "Contains",
                      "name": "contains"
                    },
                    {
                      "displayName": "Equal To",
                      "name": "equals"
                    },
                    {
                      "displayName": "Starts With",
                      "name": "startsWith"
                    },
                    {
                      "displayName": "Ends With",
                      "name": "endsWith"
                    }
                  ],
                  "displayName": "Replace Values",
                  "replacementValues": [

                  ]
                },
                {
                  "status": False,
                  "actionName": "ignore_suggestion",
                  "displayName": "Ignore for Analysis",
                  "previous_status": False
                }
              ]
            },
            {
              "slug": "b768943ae03f4093ab5f0395325afb19",
              "name": "Capital-gain",
              "columnSetting": [
                {
                  "status": False,
                  "actionName": "unique_identifier",
                  "displayName": "Unique Identifier"
                },
                {
                  "status": False,
                  "actionName": "delete",
                  "displayName": "Delete Column"
                },
                {
                  "status": False,
                  "actionName": "rename",
                  "displayName": "Rename Column",
                  "newName": None
                },
                {
                  "status": False,
                  "actionName": "replace",
                  "replaceTypeList": [
                    {
                      "displayName": "Contains",
                      "name": "contains"
                    },
                    {
                      "displayName": "Equal To",
                      "name": "equals"
                    },
                    {
                      "displayName": "Starts With",
                      "name": "startsWith"
                    },
                    {
                      "displayName": "Ends With",
                      "name": "endsWith"
                    }
                  ],
                  "displayName": "Replace Values",
                  "replacementValues": [

                  ]
                },
                {
                  "status": False,
                  "actionName": "data_type",
                  "displayName": "Change Datatype",
                  "listOfActions": [
                    {
                      "status": True,
                      "displayName": "Numeric",
                      "name": "numeric"
                    },
                    {
                      "status": False,
                      "displayName": "Text",
                      "name": "text"
                    }
                  ]
                },
                {
                  "status": False,
                  "actionName": "set_variable",
                  "displayName": "Set Variable as",
                  "listOfActions": [
                    {
                      "status": True,
                      "displayName": "General Numeric",
                      "name": "general_numeric"
                    },
                    {
                      "status": False,
                      "displayName": "Percentage",
                      "name": "percentage"
                    },
                    {
                      "status": False,
                      "displayName": "Index",
                      "name": "index"
                    },
                    {
                      "status": False,
                      "displayName": "Average",
                      "name": "average"
                    }
                  ]
                },
                {
                  "status": False,
                  "actionName": "set_polarity",
                  "displayName": "Set Polarity as",
                  "listOfActions": [
                    {
                      "status": True,
                      "displayName": "Positive",
                      "name": "positive"
                    },
                    {
                      "status": False,
                      "displayName": "Negative",
                      "name": "negative"
                    }
                  ]
                },
                {
                  "status": False,
                  "actionName": "ignore_suggestion",
                  "displayName": "Ignore for Analysis",
                  "previous_status": False
                }
              ]
            },
            {
              "slug": "b3a2a40c6ffc403999f5c31312963ffa",
              "name": "class_label",
              "columnSetting": [
                {
                  "status": False,
                  "actionName": "unique_identifier",
                  "displayName": "Unique Identifier"
                },
                {
                  "status": False,
                  "actionName": "delete",
                  "displayName": "Delete Column"
                },
                {
                  "status": False,
                  "actionName": "rename",
                  "displayName": "Rename Column",
                  "newName": None
                },
                {
                  "status": False,
                  "actionName": "replace",
                  "replaceTypeList": [
                    {
                      "displayName": "Contains",
                      "name": "contains"
                    },
                    {
                      "displayName": "Equal To",
                      "name": "equals"
                    },
                    {
                      "displayName": "Starts With",
                      "name": "startsWith"
                    },
                    {
                      "displayName": "Ends With",
                      "name": "endsWith"
                    }
                  ],
                  "displayName": "Replace Values",
                  "replacementValues": [

                  ]
                },
                {
                  "status": False,
                  "actionName": "ignore_suggestion",
                  "displayName": "Ignore for Analysis",
                  "previous_status": False
                }
              ]
            }
          ]
        },
        "FILE_SETTINGS": {
          "outputfile": [
            #"gAAAAABaxGdWjSShSd8sbTDAo_7Jj8MvNP8Th9zCneWRxjeZw0GHNTZg2GLs9ebK6zJbC_uGbyqhkrOD0AsfwFgSsRQC8JI2EVIiBOmRXy6iKpLqQYWyrsbKm2Wl9BuTPgIQg7ngO_m6fS73C2ZBiUxiEwkfGSi8bUlCznZBRCI45vgQu0tIvBtrtWAKKQ5rbEplWxpUtjoG"
            "file:///home/gulshan/marlabs/csvout/data"
          ],
          "metadata": {
            "url": "34.196.204.54:9012/api/get_metadata_for_mlscripts/",
            "slug_list": [
              "demography100csv-jhgb0uix28"
            ]
          },
          "inputfile": [
            "file:///home/gulshan/marlabs/datasets/sampleDatasets/demography100.csv"
          ]
        },
        "DATE_SETTINGS": {

        }
      },
      "job_config": {
        "message_url": "http://34.196.204.54:9012/api/messages/Job_subsetting-gul-sub-ayju8x9s4m-rs4kp1im0t_123/",
        "get_config": {
          "action": "get_config",
          "method": "GET"
        },
        "error_reporting_url": "http://34.196.204.54:9012/api/set_job_report/subsetting-gul-sub-ayju8x9s4m-rs4kp1im0t/",
        "set_result": {
          "action": "result",
          "method": "PUT"
        },
        "job_url": "http://34.196.204.54:9012/api/job/subsetting-gul-sub-ayju8x9s4m-rs4kp1im0t/",
        "job_type": "subSetting",
        "job_name": "gul-sub",
        "xml_url": "http://34.196.204.54:9012/api/xml/subsetting-gul-sub-ayju8x9s4m-rs4kp1im0t/",
        "app_id": None
      }
    }
    return subsettingConfig
