
#### API updated on 14/Jan/2017

1. **One way Anova**: performs one way ANOVA test to understand the imapct of all *dimension* variables on one *measure* variable.
    * script: [bi.scripts.one_way_anova.py](https://github.com/rammohan/marlabs-bi/blob/master/bi/scripts/one_way_anova.py)
    * params:
        + *--input*: HDFS location of input csv file
        + *--result* HDFS output location to store Anova result as JSON
        + *--narratives*: HDFS output location to store narratives result as JSON
        + *--measurecolumn*: measure column to use for one way ANOVA test based on every dimension colun in the data set 
    * result JSON format: dict
        + **measures**: list of all measure columns one way ANOVA test is applied on
        + **results**: dict containing results of all ANOVA tests. Measure column names are the keys, and value is again a dict with dimension column names as key, value is a dict following ANOVA test info:
            + **effect_size**: a value in the range[0, 1) indicating the effect size of a dimension on a measure variable. Higher the effect size, more preferable a dimension compared to other dimensions.
            + **f_value**: a statistic
            + **p_value**: a statistic
            + **sse**: sum of squares error, a statistic
            + **msse**: mean sum of squares error, a statistic
            + **ssb**: sum of squares between groups, a statistic
            + **mssb**: mean sum of squares between, a statistic
            + **n**: total number of rows
            + **groups**: a list of descriptive stat objects for each unique value in the dimension varibale
                + **column_names**: a list contains the dimension variable name
                + **column_values**: a list contains a unique value for all dimension columns in *column_names* list above
                + **descr_stats**: descriptive stats for measure column for a unique dimension column value

    * sample result:
        ```javascript
        {
            "measures": ["Id", "SepalLengthCm", "SepalWidthCm", "PetalLengthCm", "PetalWidthCm" ],

            "results": {
                    "Id": {
                        "Species": {
                            "df1": 2,
                            "df2": 147,
                            "effect_size": 0.1791760169861184,
                            "f_value": 588.2352941176471,
                            "groups": [
                                {   "column_names": ["Species"],
                                    "column_values": ["Iris-virginica"],
                                    "descr_stats": {
                                        "five_point_summary": {
                                            "freq":{ "q1": 12, "q2": 12, "q3": 13, "q4": 13},
                                            "outliers": {"left": 0, "right": 0},
                                            "splits": {
                                                "left_hinge": 75.5,
                                                "median": 125.0,
                                                "q1": 113.0,
                                                "q2": 125.0,
                                                "q3": 138.0,
                                                "right_hinge": 175.5
                                            }
                                        },
                                        "kurtosis": -1.2009603841536616,
                                        "max": 150,
                                        "mean": 125.5,
                                        "min": 101,
                                        "n": 50,
                                        "raw_data":[101.0,102.0,103.0,...],
                                        "skew": 0.0,
                                        "std_dev": 14.577379737113251,
                                        "total": 6275,
                                        "var": 212.5
                                    }
                                },
                                {   "column_names": ["Species"],
                                    "column_values": ["Iris-setosa"], 
                                    "descr_stats": {
                                        "five_point_summary": {
                                            "freq": {"q1": 12,"q2": 12,"q3": 13,"q4": 13},
                                            "outliers": {"left": 0,"right": 0},
                                            "splits": {
                                                "left_hinge": -24.5,
                                                "median": 25.0,
                                                "q1": 13.0,
                                                "q2": 25.0,
                                                "q3": 38.0,
                                                "right_hinge": 75.5
                                            }
                                        },
                                        "kurtosis": -1.2009603841536616,
                                        "max": 50,
                                        "mean": 25.5,
                                        "min": 1,
                                        "n": 50,
                                        "raw_data":[46.0,47.0,48.0,...],
                                        "skew": 0.0,
                                        "std_dev": 14.577379737113251,
                                        "total": 1275,
                                        "var": 212.5
                                    }
                                },
                                {   "column_names": ["Species"],
                                    "column_values": ["Iris-versicolor"],
                                    "descr_stats": {
                                        "five_point_summary": {
                                            "freq": {"q1": 12,"q2": 12,"q3": 13,"q4": 13},
                                            "outliers":{"left": 0,"right": 0},
                                            "splits": {
                                                "left_hinge": 25.5,
                                                "median": 75.0,
                                                "q1": 63.0,
                                                "q2": 75.0,
                                                "q3": 88.0,
                                                "right_hinge": 125.5
                                            }
                                        },
                                        "kurtosis": -1.2009603841536616,
                                        "max": 100,
                                        "mean": 75.5,
                                        "min": 51,
                                        "n": 50,
                                        "raw_data":[86.0,87.0,88,...],
                                        "skew": 0.0,
                                        "std_dev": 14.577379737113251,
                                        "total": 3775,
                                        "var": 212.5
                                    }
                                }
                            ],
                            "mssb": 125000.0,
                            "msse": 212.5,
                            "n": 150,
                            "p_value": 7.896352208899345E-72,
                            "ssb": 250000.0,
                            "sse": 31237.5
                        },

                        "...": {...}
                    }
                }
        }
        ```
    * narratives JSON format: dict containing narratives for various ANOVA results
        + **measures**: list of measure columns with some narratives
        + **narratives**: a dict containing all narratives. Keys are measure column names. Value dict has the following keys:
            + **summary**: overall summary about the measure column considering all significantly influencing dimension columns
            + **narratives**: a dict with narratives for each influencing dimension column, dimension column names are keys, and value dict has the following keys:
                + **title**: title for analysis if measure by this dimnesion
                + **analysis**: Analysis result as a para of text.

    * sample narratives:
        ```javascript
        {
            "measures": ["Id", "SepalLengthCm", "SepalWidthCm", "PetalLengthCm", "PetalWidthCm"],
            "narrtives": {
                "Id": {
                    "narratives": {
                        "Species":{
                            "analysis": "The top 2 Species account for about 89% of the total Id. Being the larget contributor, Iris-virginica contributes to 55% of the total. And, it also has the highest average Id of 125.500000. On the other hand, Iris-setosa contributes just 11% to the total Id with the average being 25.500000 Interestingly, the effect of Species on Id is significant as the average Id seem to be different across various Species values. ",
                            "title": "Impact of Species on Id"
                        }
                    },
                    "summary": "Of the 1 dimensions in the dataset, 1 variables show high variance in Id and the bar chart below displays key dimensions by effect size"
                },
                
                "PetalLengthCm": {
                    "narratives": {
                        "Species": {
                            "analysis": "The top 2 Species account for about 87% of the total PetalLengthCm. Being the larget contributor, Iris-virginica contributes to 49% of the total. And, it also has the highest average PetalLengthCm of 5.552000. On the other hand, Iris-setosa contributes just 13% to the total PetalLengthCm with the average being 1.464000 Interestingly, the effect of Species on PetalLengthCm is significant as the average PetalLengthCm seem to be different across various Species values. ",
                            "title": "Impact of Species on PetalLengthCm"
                        }
                    },
                    "summary": "Of the 1 dimensions in the dataset, 1 variables show high variance in PetalLengthCm and the bar chart below displays key dimensions by effect size"
                },
                
                "PetalWidthCm": {
                    "narratives": {
                        "Species": {
                            "analysis": "The top 2 Species account for about 93% of the total PetalWidthCm. Being the larget contributor, Iris-virginica contributes to 56% of the total. And, it also has the highest average PetalWidthCm of 2.026000. On the other hand, Iris-setosa contributes just 7% to the total PetalWidthCm with the average being 0.244000 Interestingly, the effect of Species on PetalWidthCm is significant as the average PetalWidthCm seem to be different across various Species values. ",
                            "title": "Impact of Species on PetalWidthCm"
                        }
                    },
                    "summary": "Of the 1 dimensions in the dataset, 1 variables show high variance in PetalWidthCm and the bar chart below displays key dimensions by effect size"
                },
                
                "SepalLengthCm": {
                    "narratives": {
                        "Species": {
                            "analysis":"The top 2 Species account for about 71% of the total SepalLengthCm. Being the larget contributor, Iris-virginica contributes to 38% of the total. And, it also has the highest average SepalLengthCm of 6.588000. On the other hand, Iris-setosa contributes just 29% to the total SepalLengthCm with the average being 5.006000 Interestingly, the effect of Species on SepalLengthCm is significant as the average SepalLengthCm seem to be different across various Species values. ",
                            "title": "Impact of Species on SepalLengthCm"
                        }
                    },
                    "summary": "Of the 1 dimensions in the dataset, 1 variables show high variance in SepalLengthCm and the bar chart below displays key dimensions by effect size"
                },
                
                "SepalWidthCm": {
                    "narratives": {
                        "Species": {
                            "analysis": "The top 2 Species account for about 70% of the total SepalWidthCm. Being the larget contributor, Iris-setosa contributes to 37% of the total. And, it also has the highest average SepalWidthCm of 3.418000. On the other hand, Iris-versicolor contributes just 30% to the total SepalWidthCm with the average being 2.770000 Interestingly, the effect of Species on SepalWidthCm is significant as the average SepalWidthCm seem to be different across various Species values. ",
                            "title": "Impact of Species on SepalWidthCm"
                        }
                    },
                    "summary": "Of the 1 dimensions in the dataset, 1 variables show high variance in SepalWidthCm and the bar chart below displays key dimensions by effect size"
                }
            }
        }
        ```
