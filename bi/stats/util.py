
import pattern.en
from pyspark.sql import functions as FN
from scipy.stats import f as FDistribution
from scipy.stats import norm as NormalDistribution
from scipy.stats import t as TDistribution
from statsmodels.stats.libqsturng import qsturng


class Stats:
    """
    Statistical utility functions
    """
    @staticmethod
    def t_distribution_critical_value(t_value, df=150, two_sided=True):
        """
        Gets critical value of t-Distribution
        :param t_value:
        :param df:  degrees of freedom, default value of 150 referes to INF
        :param two_sided: is it a two sided test, False indicates a one sided test
        :return: p-value - its numpy.float64 type, convert it to python float type
        """
        if two_sided:
            return float(TDistribution.pdf(t_value, df=df))

        return float(TDistribution.pdf(t_value, df=df)/2)


    @staticmethod
    def f_distribution_critical_value(f_value, df_numerator, df_denominator, loc=0, scale=1):
        """
        Gets critical value of a f-distribution
        :param f_value: observed f-value
        :param df_numerator:    degrees of freedom of numerator
        :param df_denominator:  degrees of freedom of denominator
        :param loc:
        :param scale:
        :return:
        """
        return float(FDistribution.pdf(f_value, df_numerator, df_denominator, loc, scale))

    @staticmethod
    def studentized_range(alpha=0.05, samples=10, df=140):
        """
        Get critical value from a studentized range distribution. Used in Tukey posthoc tests etc.
        :param alpha:   alpha in [0,1]
        :param samples: number of samples(groups)
        :param df:  degrees of freedom
        :return:
        """
        return float(qsturng(1-alpha, samples, df))

    @staticmethod
    def normal_distribution_percentile_point_function(alpha=0.05):
        """
        Get a value such that cumulative distribution contains exactly 100*(1-alpha/2) percentile
        of whole distribution

        :param alpha:
        :return:
        """
        percentile = (1-alpha/2.0)
        return NormalDistribution.ppf(percentile)

    #####
    ## Measure column stat functions....
    #####

    @staticmethod
    def min(data_frame, measure_column_name):
        return data_frame.select(FN.min(measure_column_name)).collect()[0][0]

    @staticmethod
    def max(data_frame, measure_column_name):
        return data_frame.select(FN.max(measure_column_name)).collect()[0][0]

    @staticmethod
    def total(data_frame, measure_column_name):
        return data_frame.select(FN.sum(measure_column_name)).collect()[0][0]

    @staticmethod
    def mean(data_frame, measure_column_name):
        return data_frame.select(FN.mean(measure_column_name)).collect()[0][0]

    @staticmethod
    def variance(data_frame, measure_column_name):
        return data_frame.select(FN.var_samp(measure_column_name)).collect()[0][0]

    @staticmethod
    def std_dev(data_frame, measure_column_name):
        return data_frame.select(FN.stddev_samp(measure_column_name)).collect()[0][0]

    @staticmethod
    def skew(data_frame, measure_column_name):
        return data_frame.select(FN.skewness(measure_column_name)).collect()[0][0]

    @staticmethod
    def kurtosis(data_frame, measure_column_name):
        return data_frame.select(FN.kurtosis(measure_column_name)).collect()[0][0]
