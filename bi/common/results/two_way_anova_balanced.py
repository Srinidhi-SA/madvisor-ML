from scipy import stats

class DFTwoWayAnovaResult:
    def __init__(self):
        self.result = {}
    def add_measure_result(self,measure,Measure_Anova_Result):
        self.result[measure] = Measure_Anova_Result
    def get_measure_result(self, measure):
        return self.result[measure]

class MeasureAnovaResult:
    def __init__(self, var):
        self._n_mean2 = var[0] * var[1]**2
        self._mean = var[1]
        self._sum_x2 = var[2]
        self.df = var[0] - 1
        self.sst = self._sum_x2 - self._n_mean2
        self.OneWayAnovaResult = {}
        self.TwoWayAnovaResult = {}

    def set_OneWayAnovaResult(self, dimension, var):
        self.OneWayAnovaResult[dimension] = OneWayAnovaResult(var)
        self.OneWayAnovaResult[dimension].set_results(self._n_mean2, self._sum_x2)

    def get_OneWayAnovaResult(self, dimension):
        return self.OneWayAnovaResult[dimension]

    def set_TwoWayAnovaResult(self, dimension1,dimension2, var):
        if not self.TwoWayAnovaResult.has_key(dimension1):
            self.TwoWayAnovaResult[dimension1]={}
        self.TwoWayAnovaResult[dimension1][dimension2] = TwoWayAnovaResult(var)
        self.TwoWayAnovaResult[dimension1][dimension2].set_results(self._n_mean2, self._sum_x2, self.OneWayAnovaResult[dimension1], self.OneWayAnovaResult[dimension2])

    def get_TwoWayAnovaResult(self, dimension1,dimension2):
        if self.TwoWayAnovaResult.has_key(dimension1):
            if self.TwoWayAnovaResult[dimension1].has_key(dimension2):
                return self.TwoWayAnovaResult[dimension1][dimension2]
        if self.TwoWayAnovaResult.has_key(dimension2):
            if self.TwoWayAnovaResult[dimension2].has_key(dimension1):
                return self.TwoWayAnovaResult[dimension2][dimension1]

class TwoWayAnovaResult:
    def __init__(self, var):
        self._n_mean2 = var.var5.sum()
        self.set_dim_table(var)

    def set_dim_table(self, var):
        """Sets dim table and won't return anything"""
        self._dim_table = {}
        self._dim_table['level1'] = var.level1.tolist()
        self._dim_table['level2'] = var.level2.tolist()
        self._dim_table['counts'] = var.counts.tolist()
        self._dim_table['means'] = var.means.tolist()
        self._dim_table['total'] = var.total.tolist()

    def set_results(self, var1, var2, anova_row, anova_column):
        self.ss_row = anova_row.get_ss_between()
        self.df_row = anova_row.get_df_between()
        self.ms_row = self.ss_row/self.df_row

        self.ss_total = anova_row.get_ss_total()
        self.df_total = anova_row.get_df_total()
        self.ms_total = self.ss_total/self.df_total

        self.ss_column = anova_column.get_ss_between()
        self.df_column = anova_column.get_df_between()
        self.ms_column = self.ss_column/self.df_column

        self.ss_interaction = self._n_mean2 - self.ss_row - self.ss_column - var1
        self.df_interaction = self.df_row * self.df_column
        self.ms_interaction = self.ss_interaction/self.df_interaction

        self.ss_error = var2 - self._n_mean2
        self.df_error = self.df_total - (self.df_row+1)*(self.df_column+1) + 1
        self.ms_error = self.ss_error/self.df_error

        self.f_row = self.ms_row/self.ms_error
        self.f_column = self.ms_column/self.ms_error
        self.f_interaction = self.ms_interaction/self.ms_error

        '''
        self.p_row = Stats.f_distribution_critical_value(self.f_row, self.df_row, self.df_error)
        self.p_column = Stats.f_distribution_critical_value(self.f_column, self.df_column, self.df_error)
        self.p_interaction = Stats.f_distribution_critical_value(self.f_interaction, self.df_interaction, self.df_error)
        '''
        #'''
        self.p_row = 1 - stats.f.cdf(self.f_row, self.df_row,self.df_error)
        self.p_column = 1 - stats.f.cdf(self.f_column, self.df_column,self.df_error)
        self.p_interaction = 1 - stats.f.cdf(self.f_interaction, self.df_interaction,self.df_error)
        #'''
        self.effect_size_interaction = self.ss_interaction/self.ss_error
        self.effect_size_row = self.ss_row/self.ss_error
        self.effect_size_column = self.ss_column/self.ss_error

class OneWayAnovaResult:
    def __init__(self, var):
        self._n_mean2 = var.var3.sum()
        self.df_total = var.counts.sum() - 1
        self.df_between = len(var.index) - 1
        self.df_within = self.df_total - self.df_between
        self.set_dim_table(var)

    def set_dim_table(self, var):
        """sets dim table"""
        self._dim_table = {}
        self._dim_table['levels']=var.levels.tolist()
        self._dim_table['counts']=var.counts.tolist()
        self._dim_table['means']=var.means.tolist()
        self._dim_table['total']=var.total.tolist()

    def set_results(self,var1, var2):
        self.ss_total = var2 - var1
        self.ss_between = self._n_mean2 - var1
        self.ss_within = var2 - self._n_mean2
        if self.ss_within > 0:
            self.effect_size = self.ss_between/self.ss_within
        else:
            self.effect_size = 0
        self.ms_between = self.ss_between/self.df_between
        self.ms_within = self.ss_within/self.df_within
        self.f_stat = self.ms_between/self.ms_within
        self.p_value = 1 - stats.f.cdf(self.f_stat, self.df_between, self.df_within)

    def get_ss_total(self):
        return self.ss_total

    def get_ss_between(self):
        return self.ss_between

    def get_df_between(self):
        return self.df_between

    def get_df_total(self):
        return self.df_total
