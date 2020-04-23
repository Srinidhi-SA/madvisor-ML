import math

import pyspark.sql.functions as FN

from bi.common.exception import BIException
from bi.stats.util import Stats
from ..common import DataFrameHelper


class IndependentSampleTTest:
    """
    Class implements independent sampling t-test
        Ref: https://en.wikipedia.org/wiki/Student's_t-test
    """

    def __init__(self, data_frame, independent_var, dependent_var, independent_var_levels=None):
        """
        :param data_frame:  data frame to use for tests
        :param independent_var: a string type column with at least two levels
        :param dependent_var:   a measure type column
        :param independent_var_levels:  if independent_var has exactly two levels this parameter can be omitted,
                    otherwise two levels in independent_var need to be supplied as a tuple
        """
        dataframe_helper = DataFrameHelper(data_frame)
        # ensure data_frame is valid
        if not dataframe_helper.is_valid_data_frame():
            raise BIException.dataframe_invalid()

        # ensure data_frame contains a column by name independent_var
        if not dataframe_helper.has_column(independent_var):
            raise BIException.column_does_not_exist(independent_var)
        # ensure column, independent_var, is of type string
        if not dataframe_helper.is_string_column(independent_var):
            raise BIException.non_string_column(independent_var)

        # ensure data_frame contains a column by name dependent_var
        if not dataframe_helper.has_column(dependent_var):
            raise BIException.column_does_not_exist(dependent_var)
        # ensure column, dependent_var, is of numeric type
        if not dataframe_helper.is_numeric_column(dependent_var):
            raise BIException.non_numeric_column(dependent_var)

        self._data_frame = data_frame
        self._independent_var = independent_var
        self._dependent_var = dependent_var
        self._independent_var_levels = self._get_independent_var_levels()
        if independent_var_levels != None and type(independent_var_levels) in [list, tuple]:
            if len(independent_var_levels) != 2:
                raise BIException("independent_var_levels should only contain two levels")
            for level in independent_var_levels:
                if level not in self._independent_var_levels:
                    raise BIException('Column, %s, does not have level "%s"' % (self._independent_var, level))
            self._independent_var_levels = independent_var_levels
        else:
            if len(self._independent_var_levels) != 2:
                raise BIException('Column, %s, should have exactly two levels, but it has %d levels' % (
                    self._independent_var, len(self._independent_var_levels)))

    def _get_independent_var_levels(self):
        """
        Get all levels in column, self._independent_var
        :return:
        """
        independent_column = FN.col(self._independent_var)
        levels = []
        for row in self._data_frame.select(independent_column).distinct().collect():
            levels.append(row[0])

        return levels

    def test(self):
        """
        Perform Independent sample t-test
        :return:
        """
        indep_col = FN.col(self._independent_var)
        dep_col = FN.col(self._dependent_var)
        sample1 = self._data_frame.select(dep_col).filter(indep_col == self._independent_var_levels[0])
        sample2 = self._data_frame.select(dep_col).filter(indep_col == self._independent_var_levels[1])

        sample1_size = sample1.count()
        sample2_size = sample2.count()

        sample1_variance = Stats.variance(sample1, self._dependent_var)
        sample2_variance = Stats.variance(sample2, self._dependent_var)

        if sample1_variance == sample2_variance:
            if sample1_size == sample2_size:
                return self._ttest_equal_size_samples_with_same_variance(sample1_size, sample1, sample2,
                                                                         sample1_variance, sample2_variance)
            else:
                return self._ttest_unequal_size_samples_with_same_variance(sample1, sample2, sample1_variance,
                                                                           sample2_variance)

        return self._ttest_with_different_sample_variances(sample1, sample2, sample1_variance, sample2_variance)

    def _ttest_equal_size_samples_with_same_variance(self, sample_size, sample1, sample2, sample1_variance,
                                                     sample2_variance):
        sample1_mean = Stats.mean(sample1, self._dependent_var)
        sample2_mean = Stats.mean(sample2, self._dependent_var)
        pooled_standard_deviation = math.sqrt((sample1_variance + sample2_variance) / 2)
        standard_error = pooled_standard_deviation * math.sqrt(2.0 / sample_size)
        t_value = (sample1_mean - sample2_mean) / standard_error
        degrees_of_freedom = 2 * sample_size - 2
        p_value = Stats.t_distribution_critical_value(t_value, df=degrees_of_freedom)

        return IndependentSampleTTestResult(indep_variable=self._independent_var, dep_variable=self._dependent_var,
                                            sample1_level=self._independent_var_levels[0], sample1_mean=sample1_mean,
                                            sample1_variance=sample1_variance,
                                            sample2_level=self._independent_var_levels[1],
                                            sample2_mean=sample2_mean, sample2_variance=sample2_variance,
                                            t_value=t_value,
                                            p_value=p_value, df=degrees_of_freedom)

    def _ttest_unequal_size_samples_with_same_variance(self, sample1, sample2, sample1_variance, sample2_variance):
        sample1_size = sample1.count()
        sample2_size = sample2.count()
        sample1_mean = Stats.mean(sample1, self._dependent_var)
        sample2_mean = Stats.mean(sample2, self._dependent_var)
        degrees_of_freedom = sample1_size + sample2_size - 2
        pooled_std_dev = math.sqrt(
            ((sample1_size - 1) * sample1_variance + (sample2_size - 1) * sample2_variance) / degrees_of_freedom)
        std_err = pooled_std_dev * math.sqrt((1 / sample1_size) + (1 / sample2_size))
        t_value = (sample1_mean - sample2_mean) / std_err
        p_value = Stats.t_distribution_critical_value(t_value, df=degrees_of_freedom)

        return IndependentSampleTTestResult(indep_variable=self._independent_var, dep_variable=self._dependent_var,
                                            sample1_level=self._independent_var_levels[0], sample1_mean=sample1_mean,
                                            sample1_variance=sample1_variance,
                                            sample2_level=self._independent_var_levels[1],
                                            sample2_mean=sample2_mean, sample2_variance=sample2_variance,
                                            t_value=t_value,
                                            p_value=p_value, df=degrees_of_freedom)

    def _ttest_with_different_sample_variances(self, sample1, sample2, sample1_variance, sample2_variance):
        # Welch's t-test
        sample1_size = sample1.count()
        sample2_size = sample2.count()
        sample1_mean = Stats.mean(sample1, self._dependent_var)
        sample2_mean = Stats.mean(sample2, self._dependent_var)
        degrees_of_freedom = (math.pow((sample1_variance / sample1_size) + (sample2_variance / sample2_size), 2)) / (
            (math.pow(sample1_variance, 2) / (math.pow(sample1_size, 2) * (sample1_size - 1))) + (
                math.pow(sample2_variance, 2) / (math.pow(sample2_size, 2) * (sample2_size - 1))))
        t_value = (sample1_mean - sample2_mean) / math.sqrt(
            (sample1_variance / sample1_size) + (sample2_variance / sample2_size))
        p_value = Stats.t_distribution_critical_value(t_value, df=degrees_of_freedom)

        return IndependentSampleTTestResult(indep_variable=self._independent_var, dep_variable=self._dependent_var,
                                            sample1_level=self._independent_var_levels[0], sample1_mean=sample1_mean,
                                            sample1_variance=sample1_variance,
                                            sample2_level=self._independent_var_levels[1],
                                            sample2_mean=sample2_mean, sample2_variance=sample2_variance,
                                            t_value=t_value,
                                            p_value=p_value, df=degrees_of_freedom)


class DependentSampleTTest:
    """
    Class implements dependent sampling t-test (paired t-test)
        Ref: https://en.wikipedia.org/wiki/Student's_t-test
    """

    def __init__(self, data_frame, column1, column2):
        dataframe_helper = DataFrameHelper(data_frame)

        if not dataframe_helper.is_valid_data_frame():
            raise BIException.dataframe_invalid()

        if not dataframe_helper.has_column(column1):
            raise BIException.column_does_not_exist(column1)
        if not dataframe_helper.is_numeric_column(column1):
            raise BIException.non_numeric_column(column1)

        if not dataframe_helper.has_column(column2):
            raise BIException.column_does_not_exist(column2)
        if not dataframe_helper.is_numeric_column(column2):
            raise BIException.non_numeric_column(column2)

        self._data_frame = data_frame
        self._column1 = column1
        self._column2 = column2

    def test(self):
        column1 = FN.col(self._column1)
        column2 = FN.col(self._column2)
        diff_column_name = 'diff'
        diff_expr = (column2 - column1).alias(diff_column_name)
        sample_of_differences = self._data_frame.select(diff_expr)
        sample_size = sample_of_differences.count()
        sample_mean = Stats.mean(sample_of_differences, diff_column_name)
        sample_sd = Stats.standard_deviation(sample_of_differences, diff_column_name)
        t_value = float(sample_mean) / (sample_sd / math.sqrt(sample_size))
        degree_of_freedom = sample_size - 1
        p_value = Stats.t_distribution_critical_value(t_value, df=degree_of_freedom)

        return DependentSampleTtestResult(column1=self._column1, column2=self._column2, sample_size=sample_size,
                                          mean_of_differences=sample_mean, df=degree_of_freedom, t_value=t_value,
                                          p_value=p_value)


class IndependentSampleTTestResult:
    """
    Model for t-test result
    """

    def __init__(self, indep_variable=None, dep_variable=None, sample1_level=None, sample2_level=None, sample1_mean=0.0,
                 sample2_mean=0.0, sample1_variance=0.0, sample2_variance=0.0, t_value=0.0, p_value=0.0, df=0):
        self._independent_variable = indep_variable
        self._dependent_variable = dep_variable
        self._sample1_level = sample1_level
        self._sample2_level = sample2_level
        self._sample1_mean = sample1_mean
        self._sample2_mean = sample2_mean
        self._sample1_variance = sample1_variance
        self._sample2_variance = sample2_variance
        self._t_value = t_value
        self._p_value = p_value
        self._df = df

    def get_independent_variable(self):
        return self._independent_variable

    def get_dependent_variable(self):
        return self._dependent_variable

    def get_sample1_level(self):
        return self._sample1_level

    def get_sample2_level(self):
        return self._sample2_level

    def get_sample1_mean(self):
        return self._sample1_mean

    def get_sample2_mean(self):
        return self._sample2_mean

    def get_sample1_variance(self):
        return self._sample1_variance

    def get_sample2_variance(self):
        return self._sample2_variance

    def get_t_value(self):
        return self._t_value

    def get_p_value(self):
        return self._p_value

    def get_df(self):
        return self._df

    def __str__(self):
        return '''
        Mean difference of %s
            1. %s-%s mean:%f var:%f
            2. %s-%s mean:%f var:%f

            t-value: %f, p-value: %f, df: %d
        ''' % (self._dependent_variable, self._independent_variable, self._sample1_level, self._sample1_mean,
               self._sample1_variance, self._independent_variable, self._sample2_level, self._sample2_mean,
               self._sample2_variance, self._t_value, self._p_value, self._df)


class DependentSampleTtestResult:
    """
    Paired t-test / dependent sample t-test result
    """

    def __init__(self, column1=None, column2=None, sample_size=0, mean_of_differences=0.0, t_value=0.0, df=0,
                 p_value=0.0):
        self._column1 = column1
        self._column2 = column2
        self._sample_size = sample_size
        self._mean_of_differences = mean_of_differences
        self._t_value = t_value
        self._df = df
        self._p_value = p_value

    def get_column1(self):
        return self._column1

    def get_column2(self):
        return self._column2

    def get_sample_size(self):
        return self._sample_size

    def get_mean_of_differences(self):
        return self._mean_of_differences

    def get_t_value(self):
        return self._t_value

    def get_df(self):
        return self._df

    def get_p_value(self):
        return self._p_value

    def __str__(self):
        return """Paired t-test
        data: %s and %s
        n = %d, t = %f, df = %d, p-value = %f
        mean of the differences: %f
        """ % (self._column1, self._column2, self._sample_size, self._t_value, self._df, self._p_value,
               self._mean_of_differences)
