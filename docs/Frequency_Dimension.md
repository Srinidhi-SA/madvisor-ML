
1. **Frequency Calculation**: calculate frequency of occurrence of each of the categories for the given dimension
    * script: [bi.scripts.frequency_dimensions.py](https://github.com/rammohan/marlabs-bi/blob/mitali_dev/bi/scripts/frequency_dimensions.py)
    * params:
        + *--input*: HDFS location of input csv file
        + *--result* HDFS output location to store descriptive stats result as JSON
        + *--narratives*: HDFS output location to store narratives result as JSON
        + *--dimensioncolumn*: dimension column to generate the frequency counts for
    * result JSON format: a dictionary with the following information:
        + **frequency_table**: a dict of categories in column and their counts
            + **<dimensioncolumn>**: a dict, name of the dimension column is used as key. Values is dict with the following two keys:
                + **<dimensioncolumn>**: a dict, name of the dimension column is used as key. Values is dict with key as category numbers like 0,1..,n and values of this dict are the names of the categories in the input dimensioncolumn.
                + **count**: a dict, for capturing the counts. Values is a dict with key as category numbers like 0,1..,n and values of this dict are the counts of the categories in the input dimensioncolumn.

    * sample result:
        ```javascript
        {
            "frequency_table": {
                "Deal_Type": {
                    "Deal_Type": {
                        "0": "Gourmet",
                        "1": "At Home",
                        "2": "Families",
                        "3": "Escapes",
                        "4": "National",
                        "5": "Local Deals",
                        "6": "Adventures"
                    },
                    "count": {
                        "0": 812,
                        "1": 668,
                        "2": 642,
                        "3": 702,
                        "4": 691,
                        "5": 735,
                        "6": 750
                    }
                }
            }
        }
        ```
      * Narratives JSON format: a dictionary with the following information:
          + **header**: header content.
          + **subheader**: sub header line.
          + **count**: a dict, for showing the percent contributions.
          + **analysis**: a list, list of sentences.
          + **summary**: a list, list of sentences.
          + **vartype**: a dictionary, keys are the different variable types present and values are their counts.
          + **frequency_dict**: a nested dictionary, key is the dimension name, value is another dictionary       containing dimension name and count as keys. see the below example for more details.

      * sample narrative`:
          ```javascript
          {
              "subheader": "top 5 Deal Types account for more than three quarters (0) of observations.",
              "count": {
                "smallest": [
                  " 642 is the smallest with 642 observations",
                  0.13
                ],
                "largest": [
                  " 812 is the largest with 812 observations",
                  0.16
                ]
              },
              "analysis": [
                " There are 7 Deal Types in the dataset. Gourmet is the largest with 812 obseravations,where as Families is the smallest Deal Type with just 642 observations.",
                " The top 5 Deal Types including Gourmet,At Home and Families account for more than three quarters (0.69%) of the overall observations. The average number of observations per Deal Type is 714.29 and there are 3 Deal Types that have observations more than average. Gourmet is about 1.14 times bigger than the average and almost 1.26 times as big as the smallest city, which is Families."
              ],
              "summary": [
                "mAdvisor has analyzed the dataset and it contains<b> 12 variables</b>: 5 measures,and 7 dimension. ",
                "Please find below the insights from our analysis of <b>deal type</b> factoring the other variables)"
              ],
              "header": "Deal Type Performance Report",
              "vartype": {
                "Time Dimension": 0,
                "Measures": 5,
                "Dimensions": 7
              },
              "frequency_dict": {
                "Deal Type": {
                  "count": {
                    "0": 812,
                    "1": 668,
                    "2": 642,
                    "3": 702,
                    "4": 691,
                    "5": 735,
                    "6": 750
                  },
                  "Deal Type": {
                    "0": "Gourmet",
                    "1": "At Home",
                    "2": "Families",
                    "3": "Escapes",
                    "4": "National",
                    "5": "Local Deals",
                    "6": "Adventures"
                  }
                }
              }
            }

          ```
