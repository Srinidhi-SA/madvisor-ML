from bi.common.exception import BIException
from bi.common.utils import accepts


class RegressionResult:
    INTERCEPT = 'intercept'
    COEFFICIENTS = 'coefficients'
    COEFF = 'coefficient'
    RMSE = 'rmse'
    R2 = 'r2'
    T_VALUE = 't_value'
    P_VALUE = 'p_value'

    @accepts(object, (str, basestring), (tuple, list))
    def __init__(self, output_column, input_columns):
        self.output_column = output_column
        self._input_columns = input_columns
        self.input_columns = []
        self.sample_data = {}
        self.stats = {
            RegressionResult.INTERCEPT: 0.0,
            RegressionResult.RMSE: 0.0,
            RegressionResult.R2: 0.0,
            RegressionResult.COEFFICIENTS: {}
        }

    # @accepts(object, intercept=(int, long, float), coefficients=(tuple, list), rmse=(int, long, float),
    #     r2=(int, long, float), t_values=(tuple, list), p_values=(tuple, list), sample_data_dict=(dict), lr_dimension=dict)

    def set_params(self, intercept=None, coefficients=None, rmse=None, r2=None, t_values=None, p_values=None,
                   sample_data_dict=None, lr_dimension=None):
        """"""
        if p_values is None:
            p_values = []
        if t_values is None:
            t_values = []
        if r2 is None:
            r2 = []
        if rmse is None:
            rmse = []
        if coefficients is None:
            coefficients = []
        if intercept is None:
            intercept = []
        if sample_data_dict is None:
            sample_data_dict = {}
        if lr_dimension is None:
            lr_dimension = {}

        self.stats[RegressionResult.INTERCEPT] = intercept
        self.stats[RegressionResult.RMSE] = rmse
        self.stats[RegressionResult.R2] = r2
        self.MVD_analysis = lr_dimension
        indexed_coefficients = [(self._input_columns[index], coefficients[index], index) \
                                for index in range(0, len(coefficients)) if coefficients[index] != 0.0]
        sorted_indexed_coefficients = sorted(indexed_coefficients, key=lambda x: abs(x[1]),reverse=True)
        for coeff_tuple in sorted_indexed_coefficients:
            input_col = coeff_tuple[0]
            self.sample_data[input_col] = sample_data_dict[input_col]
            self.input_columns.append(input_col)
            coeff = coeff_tuple[1]
            index = coeff_tuple[2]
            self.stats[RegressionResult.COEFFICIENTS][input_col] = {
                RegressionResult.COEFF: coeff,
                RegressionResult.P_VALUE: p_values[index], #p_values[index],
                RegressionResult.T_VALUE: 0.0 #t_values[index]
            }


    def get_output_column(self):
        return self.output_column

    def get_input_columns(self):
        return self.input_columns

    def get_intercept(self):
        return self.stats.get(RegressionResult.INTERCEPT)

    def get_root_mean_square_error(self):
        return self.stats.get(RegressionResult.RMSE)

    def get_rsquare(self):
        return self.stats.get(RegressionResult.R2)

    def get_coeff(self, input_column):
        if input_column not in self.input_columns:
            raise BIException('Input column(%s) has no impact on output column(%s)' \
                              %(input_column, self.output_column))

        return self.stats.get(RegressionResult.COEFFICIENTS).get(input_column).get(RegressionResult.COEFF)

    def get_all_coeff(self):
        return self.stats[RegressionResult.COEFFICIENTS]

class DFRegressionResult:
    def __init__(self):
        self.measures = []
        self.results = {}

    @accepts(object, RegressionResult)
    def add_regression_result(self, regression_result):
        output_column = regression_result.get_output_column()
        if output_column not in self.measures:
            self.measures.append(output_column)
        self.results[output_column] = regression_result

    def get_measures(self):
        return self.measures

    def get_regression_result(self, output_column):
        if output_column not in self.measures:
            raise BIException('No regression result found for column(%s)' %(output_column,))

        return self.results.get(output_column)
