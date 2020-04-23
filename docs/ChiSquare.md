
1. **Chi Square Test**: calculate the chi square test between given column and all other columns.
    * script: [bi.scripts.chisquare.py](https://github.com/rammohan/marlabs-bi/blob/mitali_dev/bi/scripts/chisquare.py)
    * params:
        + *--input*: HDFS location of input csv file
        + *--result* HDFS output location to store descriptive stats result as JSON
        + *--narratives*: HDFS output location to store narratives result as JSON
        + *--ignorecolumn*: its an **optional** parameter, column name which has to be excluded from the computations (like columns with Id's)
        + *--dimensioncolumn*: dimension column to generate the chi square test for

    * result JSON format: a dictionary with the following information:
        + **dimensions**: list of all columns, chi square test is performed between each of these against *dimensioncolumn*
        + **results**: dict containing only one key, name of the *dimensioncolumn* supplied to the script. Value associated with the only key is a dictionary, keys are names of columns, and value are chisquare test result object between *dimensioncolumn* and column by name *key*. The innermost value object has the following information:
            + **cramers_v**: value of cramers v, used for finding effect size
            + **dof**: degrees of freedom
            + **method**: name of the chisquare test method
            + **nh**: null hypothesis statement
            + **pv**: p value
            + **stats**: statistical score
            + **contigency_table** & **percentage_table**: they both represent 2 dimensional contingency tables. These dictionaries have three keys:
                + **column_one_values**: list of unique values of a column to be used in the first column of contingency table
                + **column_two_values**: list of unique values of a columns, used in the first row of contingency table
                + **table**: a two dimensional array of numbers storing cell value for every combination of *column_one* and *column_two* values

    * Sample Result:
        ```javascript
        {
            "dimensions": [ " Price Range", " Discount Range", " Source",
                            " Platform", " Buyer Age", " Buyer Gender", " Tenure in Days ",
                            "Sales", " Marketing Cost ", " Shipping Cost ", "Previous Month's Transaction "
                        ],

            "results": {
                "Deal Type": {
                    " Buyer Age": {
                        "contingency_table": {
                            "column_one_values": ["Gourmet", "At Home", "Local Deals", "Families",
                                                    "National", "Escapes","Adventures"],
                            "column_two_values": ["18 to 24", "25 to 34", "35 to 44", "45 to 54",
                                                    "55 to 64", "65+"],
                            "table": [
                                [128.0, 147.0, 124.0, 147.0, 121.0, 145.0],
                                [117.0, 128.0, 82.0, 110.0, 108.0, 123.0],
                                [116.0, 165.0, 97.0, 126.0, 102.0, 129.0],
                                [118.0, 124.0, 87.0, 103.0, 113.0, 97.0],
                                [118.0, 114.0, 105.0, 112.0, 103.0, 139.0],
                                [110.0, 140.0, 99.0, 119.0, 99.0, 135.0],
                                [158.0, 133.0, 100.0, 120.0, 109.0, 130.0]
                            ]
                        },
                        "cramers_v": 0.033406176604356096,
                        "dof": 30,
                        "method": "pearson",
                        "nh": "the occurrence of the outcomes is statistically independent.",
                        "percentage_table": {
                            "column_one_values": ["Gourmet", "At Home", "Local Deals", "Families",
                                                    "National", "Escapes", "Adventures"],
                            "column_two_values": ["18 to 24", "25 to 34", "35 to 44", "45 to 54",
                                                    "55 to 64", "65+"],
                            "table": [
                                [2.56, 2.94, 2.48, 2.94, 2.42, 2.9],
                                [2.34, 2.56, 1.64, 2.2, 2.16, 2.46],
                                [2.32, 3.3, 1.94, 2.52, 2.04, 2.58],
                                [2.36, 2.48, 1.74, 2.06, 2.26, 1.94],
                                [2.36, 2.28, 2.1, 2.24, 2.06, 2.78],
                                [2.2, 2.8, 1.98, 2.38, 1.98, 2.7],
                                [3.16, 2.66, 2.0, 2.4, 2.18, 2.6]
                            ]
                        },
                        "pv": 0.30212910450114805,
                        "stat": 33.47917905964286
                    },

                    " Buyer Gender": { .... }
                }
            }
        }
        ```

    * Narrative Json Format: a dict with 'narratives' as the only key, the value is again dict with only one key - name of the *dimensioncolumn* supplied to the script. The value object has three reserved keys *heading*, *sub_heading*, and *summary*. Other keys are names columns against which chisquare tests are run. The inner most object has the following information:
        + **analysis**: dictionary with *analysis1*, *analysis2*, *title1*, and *title2* information
        + **effect_size**: a statistical score
        + **sub_headings**:
        + **table**: contains similar information as in result object


    * Sample Narrative JSON:

    ```javascript
    {
        "narratives": {
            "Deal Type": {
              "heading": "Deal_Type Performance Analysis",
              "sub_heading": "Relationship with other variables",
              "summary": [
                  " There are 11 other variables and three of them (Sales, and Marketing_Cost) have significant association with Deal_Type. They display intriguing variation in distribution across Deal_Type. ",
                  " The chart above displays the strength of relationship between Deal_Type and those three key variables, as measured by effect size. Let us take a deeper look at all three of them. "
                ],
              " Discount Range": {
                    "analysis": {
                        "analysis1":" 21 to 30 percent and 31 to 40 percent accounts for more than half (60.86%) of the total observations, whereas 0 to 10 percent has just 6.14% of the total. Being the largest segment, 21 to 30 percent in Gourmet has about 289.0 observations, covering 5.78% of total. On the other hand, 11 to 20 percent in National represents just 1.38% of the total observations. ",
                        "analysis2":" There is an association between Deal Type and Discount Range and the distribution of Discount Range seems to be significantly differenr across Deal Type. Looking at the distribution of Discount Range within Deal Type reveals how interesting some of their relationships are. Local Deals seems to be relatively less diversified, with 38.7755102041% of the total observations coming from 21 to 30 percent alone. On the other hand, Local Deals is found to be relatively spread across all Discount Range.",
                        "title1":"Concentration of  Discount Range",
                        "title2":"Relationship between  Discount Range and Deal Type"
                      },
                    "effect_size": 0.04197331341462242,
                    "sub_heading":" 21 to 30 percent and 31 to 40 percent accounts for more than half (60.86%) of the total observations",
                    "table": {
                        "column_one_values": ["Gourmet", "At Home", "Local Deals", "Families",
                                                "National", "Escapes", "Adventures"],
                        "column_two_values": ["0 to 10 percent","11 to 20 percent", "21 to 30 percent",
                                        "31 to 40 percent", "41 to 50 percent"],
                        "table": [
                            [0.96, 2.12, 5.78, 4.14, 3.24],
                            [0.88, 1.68, 4.66, 3.48, 2.66],
                            [0.98, 1.62, 5.32, 3.8, 2.98],
                            [0.88, 2.12, 4.36, 3.0, 2.48],
                            [0.68, 1.38, 4.72, 3.6, 3.44],
                            [1.0, 1.5, 5.16, 3.6, 2.78],
                            [0.76, 2.1, 4.58, 4.66, 2.9]
                        ]
                    }
            },

            " Marketing Cost ": { ....
            }
        }
    }
    ```
