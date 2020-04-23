#### API updated on 14/Jan/2017

1. **Descriptive statistics**: collects descriptive stats for a *measure* column.
    * script: [bi.scripts.descr_stats.py](https://github.com/rammohan/marlabs-bi/blob/master/bi/scripts/descr_stats.py)
    * params:
        + *--input*: HDFS location of input csv file
        + *--result* HDFS output location to store descriptive stats result as JSON
        + *--narratives*: HDFS output location to store narratives result as JSON
        + *--measurecolumn*: measure column to generate the descriptive stats for
    * result JSON format: a dictionary with the following information:
        + **kurtosis**: kurtosis value
        + **max**: maximum value
        + **min**: minimum value
        + **mean**: mean value
        + **total**: sum of all values
        + **n**: number of observations
        + **skew**: skew
        + **var**: sample variance
        + **std_dev**: sample standard deviation
        + **raw_data**: list of all values in this column
        + **five_point_summary**: dict with the following information:
            + **freq**: dictionary containing number of values in each of the four quarters *q1*, *q2*, *q3*, and *q4*.
            + **outliers**: dict, store number of *left* and *right* outliers
            + **splits**: column value of qartile splits, a dict
                + **left_hinge**: left hinge value, equals to q1 - 1.5 * Inter_Quartile_Range, value less than this are considers outliers
                + **q1**: all observations with value less than this fall in quarter 1.
                + **q2** / **median**: roughly divides all values in to two equal sized sets, one containing values above this and other set containing values below it.
                + **q3**: all observation with value more this this fall in quarter 4. ~75% of observations have value less than this.
                + **right_hinge**: equals to q3 + 1.5 * Inter_Quartile_Range, values more than this are considered outliers
        + **histogram**: a dict with following information
            + *column_name*: name of the column
            + *num_records*: total number of records
            + *bins*: orderd list of bins by range of values a bin contains, bins number start from 0. Each bin is dict with the following information:
                + *bin_number*: bin number 
                + *start_value*: start value of bin, inclusive
                + *end_value*: end envalue of the bin, eclusive
                + *num_values*: number of records with values in *[start_value, end_value)*

    * sample result:
        ```javascript
        {
            'total': 876.5000000000002, 
            'min': 4.3, 
            'max': 7.9, 
            'skew': 0.31175305850229657, 
            'n': 150, 
            'var': 0.6856935123042518, 
            'std_dev': 0.8280661279778637, 
            'raw_data': [6.3, 6.1, 6.4, 5.9, ...], 
            'five_point_summary': {
                'freq': { 'q1': 32, 'q3': 35, 'q2': 41, 'q4': 42}, 
                'outliers': {'right': 0, 'left': 0}, 
                'splits': {
                    'q1': 5.1, 
                    'q3': 6.4, 
                    'q2': 5.8, 
                    'left_hinge': 3.1499999999999986, 
                    'median': 5.8, 
                    'right_hinge': 8.350000000000001
                }
            }, 
            'histogram': {
                'num_records': 150, 
                'bins': [
                    {'start_value': 3.96, 'end_value': 4.32, 'num_records': 1, 'bin_number': '0'}, 
                    {'start_value': 4.32, 'end_value': 4.68, 'num_records': 8, 'bin_number': '1'}, 
                    {'start_value': 4.68, 'end_value': 5.04, 'num_records': 23, 'bin_number': '2'},
                    {'start_value': 5.04, 'end_value': 5.4, 'num_records': 14, 'bin_number': '3'}, 
                    {'start_value': 5.4, 'end_value': 5.76, 'num_records': 27, 'bin_number': '4'}, 
                    {'start_value': 5.76, 'end_value': 6.12, 'num_records': 22, 'bin_number': '5'}, 
                    {'start_value': 6.12, 'end_value': 6.48, 'num_records': 20, 'bin_number': '6'}, 
                    {'start_value': 6.48, 'end_value': 6.84, 'num_records': 18, 'bin_number': '7'}, 
                    {'start_value': 6.84, 'end_value': 7.2, 'num_records': 6, 'bin_number': '8'},
                    {'start_value': 7.2, 'end_value': 7.56, 'num_records': 5, 'bin_number': '9'}, 
                    {'start_value': 7.56, 'end_value': 7.92, 'num_records': 6, 'bin_number': '10'}
                ], 
                'column_name': 'SepalLengthCm'
            }, 
            'kurtosis': -0.5735679489249783, 
            'mean': 5.843333333333335
        }
        ```
    * narratives JSON format: dict containing narratives for one measure column
        + **title**: title of the report
        + **summary**: two line summary just below title
        + **analysis**: two paras of analysis as a list
        + **take_away**: key takeaway para
    * sample narratives:
        ```javascript
        {
            'take_away': 'Key takeaway is yet to be generated...', 
            'summary': "mAdvisor has analyzed sepallengthcm factoring 5 variables for this report. Please find the insights below.",
            'analysis': [
                'The sepallengthcm values range from a minimimum of 4.3 and all the way upto a maximum of 7.9. The total sepallengthcm amount to 876.5 with the average sepallengthcm per transaction being 5.84. And, no outliers are found in the dataset that contains 150 observations.', 
                'The histogram shows the distribution of sepallengthcm, divided into 10 buckets. The plot indicates that the sales figures are heavily concentrated around few buckets. The distribution is positively skewed, which implies that there is a significant chunk of high-value sepallengthcm transactions. About one-fourth of the sepallengthcm transactions have a value of 6.4 or more.'
            ], 
            'title': 'SepalLengthCm Performance Report'
        }
        ```
