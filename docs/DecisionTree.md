
1. **Decision Tree**: builds the decision tree and generates the rules for the given dimensioncolumn
    * script: [bi.scripts.decision_tree.py](https://github.com/rammohan/marlabs-bi/blob/mitali_dev/bi/scripts/decision_tree.py)
    * params:
        + *--input*: HDFS location of input csv file
        + *--result* HDFS output location to store descriptive stats result as JSON
        + *--narratives*: HDFS output location to store narratives result as JSON
        + *--ignorecolumn*: column name which has to be excluded from the computations (like columns with Id)
        + *--dimensioncolumn*: dimension column to generate the decision tree for
    * result JSON format: a dictionary with the following information:
        + **tree**: a dict containing the tree objects
            + **name** : The name of the parent node.
                + **children** : The children nodes given in a list.
* The name and children nodes are present in  nested manner based on the tree generated.
* sample result:

    ```javascript
        {
          "tree": {
            "name": "Root",
            "children": [
              {
                "name": "Marketing_Cost <= 8.2",
                "children": [
                  {
                    "name": "Discount_Range in (31 to 40 percent,0 to 10 percent,41 to 50 percent,21 to 30 percent)",
                    "children": [
                      {
                        "name": "Marketing_Cost <= 4.9",
                        "children": [
                          {
                            "name": "Sales <= 48.0",
                            "children": [
                              {
                                "name": "Buyer_Age in (55 to 64,35 to 44)",
                                "children": [
                                  {
                                    "name": "Predict: At Home"
                                  }
                                ]
                              },
                            }
                          ]
                        }
                      ]
                    }
                  ]
                }
              ]
            }
          }

    ```
  ```
  Decision Tree Visualization :
  ![](tree.png?raw=true)

  ```

* Narratives JSON format: a dictionary with the following information:
    + **dropdownComment**: sentence to be shown above dropdown to select the various levels of the dimension column.
    + **subheader**: sub header line.
    + **table**: a dictionary, keys are the levels of the dimension column and value is a list containing rules.
    so for filtering you need to get the value from dropdown columns and use them as key.
    + **condensedTable**: a dictionary, keys are the levels of the dimension column and value is a list containing merged rules.
    + **dropdownValues**: a list, values to be shown in dropdown. the table or rules will be filtered based on the selected value from this dropdown.

* sample narrative`:
    ```javascript
    {
      "subheader": "The decision tree diagram helps us identify the key variable that explains categorization of Deal Type.And, it showcase the key variable and how it influences classification of observations into specific Deal Type.",
      "table": {
        "Local Deals": [
          "Sales <= 16.0, Buyer Age not in (55 to 64,35 to 44), Marketing Cost  <= 3.6, Buyer Age in (45 to 54), Source in (Direct),Local Deals",
          "Sales <= 16.0, Buyer Age not in (55 to 64,35 to 44), Marketing Cost  > 3.6,Previous Month's Transaction  <= 16.0, Buyer Age not in (45 to 54),Local Deals",
          "Sales > 16.0,Sales > 63.0, Discount Range not in (0 to 10 percent,41 to 50 percent,21 to 30 percent), Tenure in Days  <= 121.0, Marketing Cost  <= 1.9,Local Deals"
        ],
        "Families": [
          "Sales <= 16.0, Buyer Age in (55 to 64,35 to 44), Discount Range in (41 to 50 percent), Buyer Age not in (35 to 44), Tenure in Days  <= 82.0,Families",
          "Sales > 16.0,Sales > 63.0, Discount Range in (0 to 10 percent,41 to 50 percent,21 to 30 percent), Marketing Cost  > 10.8, Tenure in Days  > 486.0,Families"
        ],
        "Adventures": [
          "Sales <= 16.0, Buyer Age not in (55 to 64,35 to 44), Marketing Cost  > 3.6,Previous Month's Transaction  <= 16.0, Buyer Age in (45 to 54),Adventures",
          "Sales > 16.0,Sales <= 63.0, Discount Range in (41 to 50 percent),Previous Month's Transaction  <= 246.0,Sales <= 21.0,Adventures",
          "Sales > 16.0,Sales > 63.0, Discount Range not in (0 to 10 percent,41 to 50 percent,21 to 30 percent), Tenure in Days  <= 121.0, Marketing Cost  > 1.9,Adventures",
          "Sales > 16.0,Sales > 63.0, Discount Range not in (0 to 10 percent,41 to 50 percent,21 to 30 percent), Tenure in Days  > 121.0, Tenure in Days  > 516.0,Adventures"
        ]
      },
      "dropdownComment": "Please select any Deal Type from the drop down below to view it's most significant decision rules.These rules capture sets of observations that are most likely to be from the chosen Deal Type.",
      "dropdownValues":[
                         'Local Deals',
                         'Families',
                         'Escapes',
                         'Gourmet',
                         'National',
                         'At Home',
                         'Adventures'
           ],
      "condensedTable": {
        "Local Deals": [
          "Sales <= 16.0, Buyer Age not in (55 to 64,35 to 44), Marketing Cost  <= 3.6, Buyer Age in (45 to 54), Source in (Direct),Local Deals",
          "Sales <= 16.0, Buyer Age not in (55 to 64,35 to 44), Marketing Cost  > 3.6,Previous Month's Transaction  <= 16.0, Buyer Age not in (45 to 54),Local Deals",
          "Sales > 16.0,Sales > 63.0, Discount Range not in (0 to 10 percent,41 to 50 percent,21 to 30 percent), Tenure in Days  <= 121.0, Marketing Cost  <= 1.9,Local Deals"
        ],
        "Families": [
          "Sales <= 16.0, Buyer Age in (55 to 64,35 to 44), Discount Range in (41 to 50 percent), Buyer Age not in (35 to 44), Tenure in Days  <= 82.0,Families",
          "Sales > 16.0,Sales > 63.0, Discount Range in (0 to 10 percent,41 to 50 percent,21 to 30 percent), Marketing Cost  > 10.8, Tenure in Days  > 486.0,Families"
        ],
        "Adventures": [
          "Sales <= 16.0, Buyer Age not in (55 to 64,35 to 44), Marketing Cost  > 3.6,Previous Month's Transaction  <= 16.0, Buyer Age in (45 to 54),Adventures",
          "Sales > 16.0,Sales <= 63.0, Discount Range in (41 to 50 percent),Previous Month's Transaction  <= 246.0,Sales <= 21.0,Adventures",
          "Sales > 16.0,Sales > 63.0, Discount Range not in (0 to 10 percent,41 to 50 percent,21 to 30 percent), Tenure in Days  <= 121.0, Marketing Cost  > 1.9,Adventures",
          "Sales > 16.0,Sales > 63.0, Discount Range not in (0 to 10 percent,41 to 50 percent,21 to 30 percent), Tenure in Days  > 121.0, Tenure in Days  > 516.0,Adventures"
        ]
      }
    }


    ```
