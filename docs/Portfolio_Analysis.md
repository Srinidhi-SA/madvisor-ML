1. **Portfolio Analysis**: analyze the portfolio data.
    * script: [bi.scripts.portfolio_analysis.py](https://github.com/rammohan/marlabs-bi/blob/feature/templates/docs/Portfolio_Analysis.md)
    * params:
        + *--input1*: HDFS location of input csv file (Client Data)
        + *--input2*: HDFS location of input csv file (Historical NAV)
        + *--input3*: HDFS location of input csv file (Market Outlook)
        + *--result* HDFS output location to store descriptive stats result as JSON
        + *--narratives*: HDFS output location to store narratives result as JSON
        <!-- + *--ignorecolumn*: column name which has to be excluded from the computations (like columns with Id) -->

    * result JSON format: a dictionary with the following information:
        + **portfolio_summary**: a list of dictionaries containing the top level stats.
            + **name** : The name/Text of the analyzed statistics.
            + **value** : The value of the analyzed stats.
        + **portfolio_performance**: a dict containing the performance of different portfolios keys are the name of the portfolios.
              value is a list of dictionaries.
              "scaled_total" key represents the overall trend.
              "sensex" key represents the trend of sensex durint he same timeframe

              + **date** : date in "YYYY-MM-dd" format.
              + **val** : The scaled value.
        + **sector_performance**: a nested dictionary with "sector_data" and "sector_order" as keys
            + **sector_data**: a dictionary where keys are the category names.
              + **allocation**: category allocation percentage
              + **return**: category return percentage
              + **outcome**: Underperformed, Outperformed or stable
            + **sector_order**: a list containing the increasing order of sectors as per allocation value.
        + **portfolio_snapshot**: a dictionary.it contains snapshot of portfolio across different class and category.
            + **sector**: distribution across different sector like large cap mid cap.
              + **order_increasing**: a list containing increasing order of sectors
              + **values**: a dictionary where keys are different sectors and values are the portfolio amount for that sector.
            + **class**
              + **order_increasing**: a list containing increasing order of class
              + **values**: a dictionary where keys are different classes and values are the portfolio amount for that class.


* sample result:

```javascript
        {
            "portfolio_summary": [
                {
                    "name": "Total Net Investments",
                    "value": "1.39M"
                },
                {
                    "name": "Current Market Value",
                    "value": "1.48M"
                },
                {
                    "name": "Compounded Annual Growth",
                    "value": "13.81%"
                }
            ],
            "portfolio_performance": {
                "IDFC - Cash Fund Reg (G)": [
                    {
                        "date": "2016-06-01",
                        "val": 100.0
                    },  
                    {
                        "date": "2016-11-28",
                        "val": 103.29764453961457
                    },
                    {
                        "date": "2016-11-29",
                        "val": 103.31370449678801
                    }
                ],
                "scaled_total": [
                    {
                        "date": "2016-06-01",
                        "val": 100.0
                    },
                    {
                        "date": "2016-06-02",
                        "val": 100.74719329281305
                    },  
                    {
                        "date": "2016-11-28",
                        "val": 99.809329763142145
                    },
                    {
                        "date": "2016-11-29",
                        "val": 99.252462537084341
                    }
                ],
                "sensex": [
                    {
                        "date": "2016-06-01",
                        "val": 100.0
                    },
                    {
                        "date": "2016-06-02",
                        "val": 100.81358437073511
                    },
                    {
                        "date": "2016-06-03",
                        "val": 101.79116744456091
                    },
                    {
                        "date": "2016-06-06",
                        "val": 102.33858380522234
                    }
                ],
                "S&P BSE Sensex 30": [
                    {
                        "date": "2016-06-01",
                        "val": 100.0
                    },
                    {
                        "date": "2016-06-02",
                        "val": 100.81358437073511
                    },
                    {
                        "date": "2016-11-29",
                        "val": 98.915346508524166
                    }
                ],
                "Franklin - India Bluechip Fund (G)": [
                    {
                        "date": "2016-06-01",
                        "val": 100.0
                    },
                    {
                        "date": "2016-06-02",
                        "val": 99.097127222982223
                    },
                    {
                        "date": "2016-11-28",
                        "val": 101.99726402188783
                    },
                    {
                        "date": "2016-11-29",
                        "val": 101.34062927496579
                    }
                ],
                "Birla SL - Frontline Equity Fund Reg (G)": [
                    {
                        "date": "2016-06-01",
                        "val": 100.0
                    },
                    {
                        "date": "2016-06-02",
                        "val": 100.11607661056297
                    },
                    {
                        "date": "2016-11-28",
                        "val": 102.84387695879278
                    },
                    {
                        "date": "2016-11-29",
                        "val": 101.56703424260012
                    }
                ],
                "IDFC - Premier Equity Fund Reg (G)": [
                    {
                        "date": "2016-06-01",
                        "val": 100.0
                    },
                    {
                        "date": "2016-06-02",
                        "val": 105.04648074369189
                    },
                    ...
                    ...
                    {
                        "date": "2016-11-28",
                        "val": 100.0
                    },
                    {
                        "date": "2016-11-29",
                        "val": 97.609561752988043
                    }
                ],
                "Franklin - India High Growth Companies Fund (G)": [
                    {
                        "date": "2016-06-01",
                        "val": 100.0
                    },
                    {
                        "date": "2016-06-02",
                        "val": 100.68965517241379
                    },
                    ...
                    ...
                    {
                        "date": "2016-11-28",
                        "val": 105.51724137931035
                    },
                    {
                        "date": "2016-11-29",
                        "val": 106.20689655172416
                    }
                ],
                "Franklin - India Ultra Short Bond Super Ins (G)": [
                    {
                        "date": "2016-06-01",
                        "val": 100.0
                    },
                    {
                        "date": "2016-06-02",
                        "val": 100.0
                    },
                    {
                        "date": "2016-06-14",
                        "val": 100.0
                    },
                    {
                        "date": "2016-06-15",
                        "val": 100.0
                    },
                    ...
                    ...
                    ...
                    {
                        "date": "2016-11-29",
                        "val": 104.83091787439614
                    }
                ]
            },
            "sector_performance": {
                "sector_data": {
                    "Telecom": {
                        "allocation": 2.0,
                        "outcome": "Outperform",
                        "return": 2.0
                    },
                    "Automobile": {
                        "allocation": 6.0,
                        "outcome": "Stable",
                        "return": 6.0
                    },
                    "Oil & Gas": {
                        "allocation": 13.0,
                        "outcome": "Stable",
                        "return": 13.0
                    },
                    "Metals": {
                        "allocation": 5.0,
                        "outcome": "Stable",
                        "return": 5.0
                    },
                    "Construction": {
                        "allocation": 5.0,
                        "outcome": "Underperform",
                        "return": 5.0
                    },
                    "Financial Services": {
                        "allocation": 22.0,
                        "outcome": "Outperform",
                        "return": 22.0
                    },
                    "Healthcare": {
                        "allocation": 12.0,
                        "outcome": "Stable",
                        "return": 12.0
                    },
                    "FMCG": {
                        "allocation": 28.000000000000004,
                        "outcome": "Underperform",
                        "return": 28.000000000000004
                    },
                    "Technology": {
                        "allocation": 6.0,
                        "outcome": "Outperform",
                        "return": 6.0
                    }
                },
                "sector_order": [
                    "Telecom",
                    "Metals",
                    "Construction",
                    "Automobile",
                    "Technology",
                    "Healthcare",
                    "Oil & Gas",
                    "Financial Services",
                    "FMCG"
                ]
            },
            "portfolio_snapshot": {
                "sector": {
                    "order_increasing": [
                        "Liquid",
                        "Large Cap",
                        "Ultra Short Term",
                        "Multi Cap"
                    ],
                    "values": {
                      "Large Cap": 406779,
                      "Ultra Short Term": 414203,
                      "Multi Cap": 565693,
                      "Liquid": 97235
                    }
                },
                "class": {
                    "order_increasing": [
                        "Cash",
                        "Debt",
                        "Equity"
                    ],
                    "values": {
                        "Debt": 28.000000000000004,
                        "Cash": 7.0000000000000009,
                        "Equity": 66.0
                    }
                }
            }
        }

```

* Narrative JSON format: a dictionary with the following information:
    + **overall**: a dictionary containing the top level summary.
        + **summary** : list of summary text
    + **snapshot**: a dictionary containing the snapshot narrative.
        + **summary** : list of summary text
    + **performance**: a dictionary containing the performance of different portfurint he same timeframe
        + **sub_heading** : sub heading.
        + **summary** : list of summary text.
    + **growth**: a dictionary containing the narrative of portfolio growth
        + **sub_heading** : sub heading
        + **sub_sub_heading** : sentence
        + **summary** : type dictionary
          + **outperformers**: sentence talking about outperformenrs
          + **underperformers**: sentnece talking about underperformers
          + **comments**: list of sentences

    + **projection**: a dictionary.it contains snapshot of portfolio across different class and category.
        + **sub_heading** : sub heading.
        + **summary** : list of sentences.

    + **recommendations**: a dictionary. It contans the recommendation summary from our analysis
        + **sub_heading** : sub heading
        + **sub_sub_heading** : sentence
        + **summary** : list of sentences


* sample narrative: will update this with actual output

``` javascript
    {
        "narratives": {
            "overall": {
                "summary": [
                  "content 1",
                  "content 2"
                ]
            },
            "snapshot": {
                "summary": [
                  "content 1",
                  "content 2"
                ]
            },
            "performance": {
                "sub_heading": "sub heading text",
                "summary": [
                  "content 1",
                  "content 2"
                ]
            },
            "growth": {
                "sub_heading": "sub heading text",
                "sub_sub_heading": "sub sub heading text",
                "summary": {
                  "outperformers":"outperformers content",
                  "underperformers":"underperformers content",
                  "comments":[
                    "comment 1",
                    "comment 2",
                    "comment 3"
                  ]
                }
            },
            "projection": {
                "sub_heading": "sub heading text",
                "summary": [
                  "content 1"
                ]
            },
            "recommendation": {
                "sub_heading": "sub heading text",
                "sub_sub_heading": "sub sub heading text",
                "summary": [
                    "comment 1",
                    "comment 2",
                    "comment 3"
                  ]
            }
        }
    }

```
