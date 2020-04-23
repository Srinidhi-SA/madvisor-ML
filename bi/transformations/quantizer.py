import time

from pyspark.ml.feature import QuantileDiscretizer
from pyspark.sql import functions as FN

from bi.common import BIException
from bi.common.results import FivePointSummary


class Quantizer:
    QUANTIZATION_OUTPUT_COLUMN = '__quant'
    QUANTIZATION_RELATIVE_ERROR = 0.0001
    APPROX_ERROR = 0.10
    QUARTILE_PERCENTAGES = [0.25,0.5,0.75]

    @staticmethod
    def quantize(data_frame, measure_column, dataframe_helper):
        if not dataframe_helper.is_numeric_column(measure_column):
            raise BIException.non_numeric_column(measure_column)

        quantile_discretizer = QuantileDiscretizer(numBuckets=4, inputCol=measure_column,
                                                   outputCol=Quantizer.QUANTIZATION_OUTPUT_COLUMN,
                                                   relativeError=Quantizer.QUANTIZATION_RELATIVE_ERROR)
        bucketizer = quantile_discretizer.fit(data_frame)
        # splits have these values [-Inf, Q1, Median, Q3, Inf]
        splits = bucketizer.getSplits()
        if len(splits) < 5:
            q1 = splits[1]
            median = splits[1]
            q3 = splits[1]
            iqr = (q3 - q1)
            left_hinge = (q1 - 1.5 * iqr)
            right_hinge = (q3 + 1.5 * iqr)
        else:
            q1 = splits[1]
            median = splits[2]
            q3 = splits[3]
            iqr = (q3 - q1)
            left_hinge = (q1 - 1.5 * iqr)
            right_hinge = (q3 + 1.5 * iqr)

        mean = data_frame.select(FN.mean(measure_column)).collect()[0][0]
        column = FN.column(measure_column)
        num_left_outliers = data_frame.filter(column < left_hinge).count()
        num_right_outliers = data_frame.filter(column > right_hinge).count()
        # q1_freq = data_frame.filter(column < q1).count()
        # q2_freq = data_frame.filter(column >= q1).filter(column < median).count()
        # q3_freq = data_frame.filter(column >= median).filter(column < q3).count()
        # q4_freq = data_frame.filter(column >= q3).count()
        q1_stats = data_frame.filter(column < q1).agg(FN.sum(column).alias('sum'), FN.count(column).alias('count')).collect()
        q2_stats = data_frame.filter(column >= q1).filter(column < median).agg(FN.sum(column).alias('sum'), FN.count(column).alias('count')).collect()
        q3_stats = data_frame.filter(column >= median).filter(column < q3).agg(FN.sum(column).alias('sum'), FN.count(column).alias('count')).collect()
        q4_stats = data_frame.filter(column >= q3).agg(FN.sum(column).alias('sum'), FN.count(column).alias('count')).collect()

        q1_freq = q1_stats[0]['count']
        q2_freq = q2_stats[0]['count']
        q3_freq = q3_stats[0]['count']
        q4_freq = q4_stats[0]['count']

        quartile_sums = {}
        quartile_sums['q1'] = q1_stats[0]['sum']
        quartile_sums['q2'] = q2_stats[0]['sum']
        quartile_sums['q3'] = q3_stats[0]['sum']
        quartile_sums['q4'] = q4_stats[0]['sum']

        quartile_means = {}
        quartile_means['q1'] = q1_stats[0]['sum']/q1_stats[0]['count']
        quartile_means['q2'] = q2_stats[0]['sum']/q2_stats[0]['count']
        quartile_means['q3'] = q3_stats[0]['sum']/q3_stats[0]['count']
        quartile_means['q4'] = q4_stats[0]['sum']/q4_stats[0]['count']

        FPS = FivePointSummary(left_hinge_value=left_hinge, q1_value=q1, median=median, q3_value=q3,
                                right_hinge_value=right_hinge, num_left_outliers=num_left_outliers,
                                num_right_outliers=num_right_outliers, q1_freq=q1_freq, q2_freq=q2_freq,
                                q3_freq=q3_freq, q4_freq=q4_freq)
        FPS.set_means(quartile_means)
        FPS.set_sums(quartile_sums)

        return FPS
    @staticmethod
    def approxQuantize(data_frame, measure_column, dataframe_helper):
        if not dataframe_helper.is_numeric_column(measure_column):
            raise BIException.non_numeric_column(measure_column)
        st = time.time()
        data_frame = data_frame.select(measure_column)
        splits = data_frame.approxQuantile(measure_column,Quantizer.QUARTILE_PERCENTAGES, Quantizer.APPROX_ERROR)
        print splits
        print "bucketizer",time.time()-st
        q1 = splits[0]
        median = splits[1]
        q3 = splits[2]
        iqr = (q3 - q1)
        left_hinge = (q1 - 1.5 * iqr)
        right_hinge = (q3 + 1.5 * iqr)
        # print q1,median,q3,iqr,left_hinge,right_hinge

        mean = data_frame.select(FN.mean(measure_column)).collect()[0][0]
        column = FN.column(measure_column)
        num_left_outliers = data_frame.filter(column < left_hinge).count()
        num_right_outliers = data_frame.filter(column > right_hinge).count()

        q1_stats = data_frame.filter(column < q1).agg(FN.sum(column).alias('sum'), FN.count(column).alias('count')).collect()
        q2_stats = data_frame.filter(column >= q1).filter(column < median).agg(FN.sum(column).alias('sum'), FN.count(column).alias('count')).collect()
        q3_stats = data_frame.filter(column >= median).filter(column < q3).agg(FN.sum(column).alias('sum'), FN.count(column).alias('count')).collect()
        q4_stats = data_frame.filter(column >= q3).agg(FN.sum(column).alias('sum'), FN.count(column).alias('count')).collect()

        q1_freq = q1_stats[0]['count']
        q2_freq = q2_stats[0]['count']
        q3_freq = q3_stats[0]['count']
        q4_freq = q4_stats[0]['count']

        quartile_sums = {}
        quartile_sums['q1'] = q1_stats[0]['sum'] if q1_stats[0]['sum'] != None else 0
        quartile_sums['q2'] = q2_stats[0]['sum'] if q1_stats[0]['sum'] != None else 0
        quartile_sums['q3'] = q3_stats[0]['sum'] if q3_stats[0]['sum'] != None else 0
        quartile_sums['q4'] = q4_stats[0]['sum'] if q4_stats[0]['sum'] != None else 0

        quartile_means = {}
        quartile_means['q1'] = quartile_sums['q1']/q1_stats[0]['count'] if q1_stats[0]['count'] != 0 else None
        quartile_means['q2'] = quartile_sums['q2']/q2_stats[0]['count'] if q2_stats[0]['count'] != 0 else None
        quartile_means['q3'] = quartile_sums['q3']/q3_stats[0]['count'] if q2_stats[0]['count'] != 0 else None
        quartile_means['q4'] = quartile_sums['q4']/q4_stats[0]['count'] if q2_stats[0]['count'] != 0 else None

        FPS = FivePointSummary(left_hinge_value=left_hinge, q1_value=q1, median=median, q3_value=q3,
                                right_hinge_value=right_hinge, num_left_outliers=num_left_outliers,
                                num_right_outliers=num_right_outliers, q1_freq=q1_freq, q2_freq=q2_freq,
                                q3_freq=q3_freq, q4_freq=q4_freq)
        FPS.set_means(quartile_means)
        FPS.set_sums(quartile_sums)

        return FPS
