
1. **DataFrame Metadata**: metadata about a data frame
    * script: [bi.scripts.metadata.py](https://github.com/rammohan/marlabs-bi/blob/master/bi/scripts/metadata.py)
    * params:
        + *--input*: HDFS location of input csv file
        + *--result* HDFS output location to store descriptive stats result as JSON
    * result JSON format: a dictionary with the following information:
        + **columns**: a dict of columns by type. Keys are column types:
            + **measure_columns**: a dict, names of measure columns are used as keys. Values is dict with the following two keys:
                + **num_nulls**: number of null values
                + **num_non_nulls**: number of non null values
            + **dimension_columns**: a dict, names of dimension columns are used as keys. Values is dict with the following two keys: 
                + **num_nulls**: number of null values
                + **num_non_nulls**: number of non null values
            + **time_dimension_columns**: a dict, names of time dimension columns are used as keys. Values is dict with the following two keys:
                + **num_nulls**: number of null values
                + **num_non_nulls**: number of non null values
        + **total_columns**: total number of columns in the input dataframe
        + **total_rows**: #rows in the dataframe 
    * sample result:
        ```javascript
        {
            'total_columns': 6, 
            'total_rows': 150, 
            'columns': {
                'time_dimension_columns': {}, 
                'dimension_columns': {
                    'Species': {'num_nulls': 1, 'num_non_nulls': 149}
                }, 
                'measure_columns': {
                    'PetalWidthCm': {'num_nulls': 2, 'num_non_nulls': 148}, 
                    'SepalWidthCm': {'num_nulls': 2, 'num_non_nulls': 148}, 
                    'Id': {'num_nulls': 2, 'num_non_nulls': 148}, 
                    'SepalLengthCm': {'num_nulls': 2, 'num_non_nulls': 148}, 
                    'PetalLengthCm': {'num_nulls': 2, 'num_non_nulls': 148}
                }
            }
        }
        ```
