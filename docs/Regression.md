
#### Last update on: 14/Jan/2017


1. **Linear Regression**: performs linear regression of a measure column with all other measure columns, in the dataset.
    
    * script: [bi.scripts.regression.py](https://github.com/rammohan/marlabs-bi/blob/master/bi/scripts/regression.py)
    * params:
        + *--input*: HDFS location of input csv file
        + *--result* HDFS output location to store Anova result as JSON
        + *--narratives*: HDFS output location to store narratives result as JSON
        * *--measurecolumn*: measure column to be used as output column in the regression 
    * result JSON format: dict
        + **output_column**: output column
        + **input_column**: list of input columns with non-zero influence on output column
        + **stats**: a dict of statistics
            + **intercept**: intercept term
            + **rmse**: root mean square error
            + **r2**: r-square value
        + **coefficients**: coefficients of various input columns as a dict with input column name as key. Value ahs the following info:
            + **coefficient**: coefficient value
            + **p_value**: p value
            + **t_value**: t value

    * sample result:
        ```javascript
        {
            'output_column': 'SepalLengthCm', 
            'input_columns': ['SepalWidthCm', 'PetalLengthCm'],
            'stats': {
                'intercept': 3.844958769681915, 
                'r2': 0.789319933193868, 
                'coefficients': {
                    'SepalWidthCm': {
                        'coefficient': 0.19609986928828294, 
                        'p_value': 0.0, 
                        't_value': 0.0
                    }, 
                    'PetalLengthCm': {
                        'coefficient': 0.3723356410548958, 
                        'p_value': 0.0, 't_value': 0.0
                    }
                }, 
                'rmse': 0.37881245396755264
            }
        }
        ```
    * narratives JSON format: a dict with the following information:
        + **summary**: summary of regression test
        + **analysis**: two paras of analysis

    * sample narratives:
        ```javascript
        {
            'analysis': [
                'The SepalLengthCm figures are positively & strongly correlated with PetalLengthCm. As PetalLengthCm increase, SepalLengthCm also increases sharply.', 
                'SepalWidthCm, andPetalLengthCm are the top influencers that explain a great magnitude of change in SepalLengthCm. One unit increase in PetalLengthCm results in 0.3723 units of increase in SepalLengthCm. One unit increase in SepalWidthCm results in 0.1961 units of increase in SepalLengthCm.'
            ], 
            'summary': 'Though there are 4 measures in the dataset, only 2 of them have a significant influence on SepalLengthCm. Let us take deeper look at to what extent they explain change in SepalLengthCm'
        }
        ```
