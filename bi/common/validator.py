
class ConfigValidator:
    """
    class for validating the config being passed for runnning Jobs

    "config" : {
        "COLUMN_SETTINGS" : {
            "analysis_type" : [
                "measure"
            ],
            "consider_columns" : [
                "Sales Office",
                "Brand",
                "Category",
                "Sub Category",
                "Product",
                "Sales Quantity",
                "Sales Value",
                "Gross Margin",
                "Date"
            ],
            "consider_columns_type" : [
                "including"
            ],
            "dateTimeSuggestions" : [
                {}
            ],
            "date_columns" : [
                "Date"
            ],
            "date_format" : None,
            "ignore_column_suggestion" : [],
            "polarity" : [
                "positive"
            ],
            "result_column" : [
                "Sales Quantity"
            ],
            "utf8_column_suggestions" : []
        },
        "FILE_SETTINGS" : {
            "inputfile" : [
                "file:///home/gulshan/marlabs/datasets/BIDCO_Local_v4.csv"
            ],
            "script_to_run" : [
                "Descriptive analysis",
                "Measure vs. Measure",
                "Predictive modeling",
                "Trend",
                "Descriptive analysis",
                "Measure vs. Dimension",
                "Predictive modeling",
                "Trend"
            ]
        }
    },
    "job_config" : {
        "get_config" : {
            "action" : "get_config",
            "method" : "GET"
        },
        "job_type" : "story",
        "job_url" : "http://madvisor.marlabsai.com:80/api/job/insight-bidco-sales-znlfl79g9e-w1kb64gs73/",
        "set_result" : {
            "action" : "result",
            "method" : "PUT"
        }
    },
    """
    def __init__(self,configObj):
        self._validate = False
        self._configObj = configObj

    def check_subset_list(self,requiredList,availableList):
        if set(requiredList) < set(availableList):
            # Some value is missing in the availableList
            return True
        else:
            return False

    def validate_object_keys(self):
        rootkeys = ["config","job_config"]
        existingKeys = self._configObj.keys()
        self._rootKeysValidation = self.check_subset_list(rootkeys,existingKeys)
        
    def validate_job_config_keys(self):
        jobConfigKeys = ["job_type","job_url","get_config","set_result"]
        existingKeys = self._configObj["job_config"].keys()
        self._jobconfigKeysValidation = self.check_subset_list(jobConfigKeys,existingKeys)
