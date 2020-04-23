from bi.common.decorators import accepts


class CorrelationStats:
    STANDARD_ERROR = 'std_err'
    T_VALUE = 't_value'
    P_VALUE = 'p_value'
    DEGREES_OF_FREEDOM = 'df'
    COEFFICIENT_OF_DETERMINATION = 'coeff_determination'

    @accepts(object, correlation=(int, float), std_error=(int, float), t_value=(int, float), p_value=(int, float),
             degrees_of_freedom=(int, long), coeff_determination=(int, float))
    def __init__(self, correlation=0.0, std_error=0.0, t_value=0.0, p_value=0.0, degrees_of_freedom=1,
                 coeff_determination=0.0):
        self.correlation = correlation
        self.stat_significance = {
            CorrelationStats.STANDARD_ERROR: std_error,
            CorrelationStats.T_VALUE: t_value,
            CorrelationStats.P_VALUE: p_value,
            CorrelationStats.DEGREES_OF_FREEDOM: degrees_of_freedom,
        }
        self.effect_size = {
            CorrelationStats.COEFFICIENT_OF_DETERMINATION: coeff_determination
        }
        self.confidence_intervals = {}

    @accepts(object, (int, float), (int, float), (int, float))
    def set_confidence_interval(self, alpha, lower_bound, upper_bound):
        self.confidence_intervals[str(alpha)] = (lower_bound, upper_bound)

    def get_correlation(self):
        return self.correlation

    def get_standard_error(self):
        return self.stat_significance.get(CorrelationStats.STANDARD_ERROR)

    def get_t_value(self):
        return self.stat_significance.get(CorrelationStats.T_VALUE)

    def get_p_value(self):
        return self.stat_significance.get(CorrelationStats.P_VALUE)

    def get_degrees_of_freedom(self):
        return self.stat_significance.get(CorrelationStats.DEGREES_OF_FREEDOM)

    def get_coeff_of_determination(self):
        return self.effect_size.get(CorrelationStats.COEFFICIENT_OF_DETERMINATION)


class ColumnCorrelations:
    """Correlations of a measure column with all other measure columns
    """
    @accepts(object, (str, basestring))
    def __init__(self, column_name):
        self.column_name = column_name
        self.correlations = {}
    
    @accepts(object, (str, basestring), CorrelationStats)
    def add_correlation(self, measure_column, correlation_stats):
        self.correlations[measure_column] = correlation_stats

    def get_column_name(self):
        return self.column_name

    def get_correlations(self):
        return self.correlations

    def get_correlation(self, column_name):
        return self.correlations[column_name]

class Correlations:
    """Correlation among all measure columsn in a a dataframe
    """
    def __init__(self):
        self.correlations = {}

    @accepts(object, column_correlations=ColumnCorrelations)
    def add_correlation(self, column_correlations):
        column_name = column_correlations.get_column_name()
        self.correlations[column_name] = column_correlations.get_correlations()

    def get_correlation_stats(self, measure_column):
        return self.correlations.get(measure_column)
