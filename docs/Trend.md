

1. **Trend Analysis**: analysis of trend in all measure varaibles by a date column
    * script: [bi.scripts.trend.py](https://github.com/rammohan/marlabs-bi/blob/master/bi/scripts/trend.py)
    * params:
        + *--input*: HDFS location of input csv file
        + *--result* HDFS output location to store Anova result as JSON
        + *--narratives*: HDFS output location to store narratives result as JSON
    * result JSON format: dict
        + **measures**: list of all measure columns trend analysis is on
        + **trends**: a dict of trend results for all measure columns by various date columns. Measure column names are used as keys, value is a dict whose keys are date column names, and values have the following information:
            + **data**: sum of measure column for every time window

    * sample result:
        ```javascript
        {
            "measures": ["sales", "profit", "tax"],
            "trends": {
                "sales": {
                    "week": {
                        "granularity": "weekly",
                        "data": [("week1", 1250), ("week2", 1300), ...., ("week53", 960)]
                    },
                    "month": {
                        "granularity": "monthly",
                        "data": [("Jan 2016", 4500), ("Feb 2016", 5200), ...., ("Dec 2016", 2990)]
                    }
                },
                "profit": {
                    "month": {
                        "granularity": "monthly",
                        "data": [("Jan 2016", 1200), ("Feb 2016", -800), ...., ("Dec 2016", 210)]
                    }
                },
                "tax": {
                    "financial_year": {
                        "granularity": "yearly",
                        "data": [("2014", 23450), ("2015", 21000), ("2016", 12000), ("2017", 10250)]
                    }
                }
            } 
        }
        ```
    * narratives JSON format: dict containing narratives for various trend results
        + **measures**: list of output measure columns with narratives
        + **narratuves**: a dict of narratives for all measure column in the above list. Measure column names are the keys, and value dict has date/time dimension columns as keys. Value associated with date/time dimension column is a dict with the following information:
            + **analysis**: a list of paras

    * sample narratives:
        ```javascript
        {
            "measures": ["sales", "profit", "tax"],
            "narratives": {
                "sales": {
                    "week": {
                        "analysis" : ["analysis para1", "analysis para 2"]
                    }
                },
                "profit": {
                    "quarter": {
                        "analysis": ["analysis para1", "analysis para2", "analysis para3"]
                    }
                },
                "tax": {
                    "financial_year": {
                        "analysis": ["analysis para 1", "analysis para2"]
                    }
                }

            }
        }
        ```
