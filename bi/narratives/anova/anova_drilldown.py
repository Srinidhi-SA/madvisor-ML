from pyspark.sql import functions as FN

from bi.narratives import utils as NarrativesUtils


class AnovaDrilldownNarratives:

    def __init__(self, measure_column, dimension_columns, df_helper, anova_narratives,base_dir):
        self.measure_column = measure_column
        self.dimension_columns = dimension_columns
        self.anova_narratives = anova_narratives
        self._base_dir = base_dir
        self.df = df_helper.get_data_frame()
        self.analysis = {}
        self._generate_analysis()


    def get_aggregared_count(self, df, dimension_columns):
        grouped_data = {}
        for col in dimension_columns:
            agg_df = df.groupBy(col).agg(FN.count(col).alias("count")).toPandas()
            grouped_data[col] = dict(zip(agg_df[col],agg_df["count"]))
        return grouped_data

    def get_aggregared_sum(self, df, dimension_columns):
        grouped_data = {}
        for col in dimension_columns:
            agg_df = df.groupBy(col).agg(FN.sum(col).alias("count")).toPandas()
            grouped_data[col] = dict(zip(agg_df[col],agg_df["count"]))
        return grouped_data

    def get_aggregared_avg(self, df, dimension_columns):
        grouped_data = {}
        for col in dimension_columns:
            agg_df = df.groupBy(col).agg(FN.mean(col).alias("count")).toPandas()
            grouped_data[col] = dict(zip(agg_df[col],agg_df["count"]))
        return grouped_data

    def get_top_dimensions_to_drilldown(self, dimension_columns, overall_aggregation, level_aggregation, n_top=2):
        output = []
        for col in dimension_columns:
            overall_level_freq = overall_aggregation[col]
            subset_level_freq = level_aggregation[col]
            diff_list = []
            for key in subset_level_freq.keys():
                diff_list.append((subset_level_freq[key]-overall_level_freq[key],key))
            k = (col,max(diff_list,key=lambda x:x[0]))
            output.append(k)
        sorted_output = sorted(output,key=lambda x:x[1][0],reverse=True)
        return sorted_output

    def generate_inner_data_dict(self,highest_level,df_avg,dim,dimension_columns,overall_aggregation,anova_narr):
        avg_dict = {}
        level_aggregation_avg = self.get_aggregared_count(df_avg,dimension_columns)
        dd_avg = self.get_top_dimensions_to_drilldown(dimension_columns,
                                                    overall_aggregation,
                                                    level_aggregation_avg, n_top=2)
        # print dd_avg
        top_dd_avg = [x[0] for x in dd_avg]
        top_dd_avg_level = [x[1][1] for x in dd_avg]
        avg_dict["dim2"] = top_dd_avg[0]
        avg_dict["dim3"] = top_dd_avg[1]
        avg_dict["dim1_top_level"] = highest_level
        avg_dict["dim1_top_level_percent_cont"] = round(anova_narr.group_by_mean[highest_level]*100/float(sum(anova_narr.group_by_mean.values())),2)
        dim2_data = level_aggregation_avg[top_dd_avg[0]]
        dim2_data_max = max(dim2_data,key=dim2_data.get)
        dim2_overall_agg = overall_aggregation[top_dd_avg[0]]
        avg_dict["dim2_top_level"] = dim2_data_max
        avg_dict["dim2_top_level_percent_cont"] = round(dim2_data[dim2_data_max]*100/float(sum(dim2_data.values())),2)
        avg_dict["dim2_top_level_overall_per"] = round(dim2_overall_agg[dim2_data_max]*100/float(sum(dim2_overall_agg.values())),2)
        avg_dict["subset1_avg"] = 199
        avg_dict["subset1_sum"] = 199
        avg_dict["dim2_top_diff_level"] = top_dd_avg_level[0]
        avg_dict["dim2_top_diff_percent_cont"] = round(dim2_data[top_dd_avg_level[0]]*100/float(sum(dim2_data.values())),2)
        avg_dict["dim2_top_diff_overall_per"] = round(dim2_overall_agg[top_dd_avg_level[0]]*100/float(sum(dim2_overall_agg.values())),2)
        avg_dict["dim2_subset_avg_diff"] = 100
        avg_dict["dim2_subset_sum_diff"] = 100

        dim3_data = level_aggregation_avg[top_dd_avg[1]]
        dim3_data_max = max(dim3_data,key=dim3_data.get)
        dim3_overall_agg = overall_aggregation[top_dd_avg[1]]
        avg_dict["dim3_top_level"] = dim3_data_max
        avg_dict["dim3_top_level_percent_cont"] = round(dim3_data[dim3_data_max]*100/float(sum(dim3_data.values())),2)
        avg_dict["dim3_top_level_overall_per"] = round(dim3_overall_agg[dim3_data_max]*100/float(sum(dim3_overall_agg.values())),2)
        avg_dict["subset_avg"] = 100
        avg_dict["dim3_top_diff_level"] = top_dd_avg_level[1]
        avg_dict["dim3_top_diff_percent_cont"] = round(dim3_data[top_dd_avg_level[1]]*100/float(sum(dim3_data.values())),2)
        avg_dict["dim3_top_diff_overall_per"] = round(dim3_overall_agg[top_dd_avg_level[1]]*100/float(sum(dim3_overall_agg.values())),2)
        avg_dict["dim3_subset_avg_diff"] = 100
        avg_dict["dim3_subset_sum_diff"] = 100
        return avg_dict

    def _generate_analysis(self):
        overall_aggregation = self.get_aggregared_count(self.df, self.dimension_columns)
        df1 = self.df.select(*self.dimension_columns+[self.measure_column])
        for dim in self.dimension_columns:
            data_dict = {"dim1":dim}
            anova_narr = self.anova_narratives[dim]
            highest_level_by_avg = max(anova_narr.group_by_mean,key=anova_narr.group_by_mean.get)
            highest_level_by_sum = max(anova_narr.group_by_total,key=anova_narr.group_by_total.get)
            # print highest_level_by_avg,highest_level_by_sum
            self.analysis[dim] = {"sum":"","avg":""}
            if highest_level_by_avg != highest_level_by_sum:
                df_avg = df1.filter(df1[dim] == highest_level_by_avg)
                inner_dict_avg = self.generate_inner_data_dict(highest_level_by_avg,df_avg,dim,self.dimension_columns,overall_aggregation,anova_narr)
                inner_dict_avg["dim1"] = dim
                inner_dict_avg["measure_column"] = self.measure_column
                inner_dict_avg["highest_level_by_avg"] = highest_level_by_avg
                data_dict["avg"] = inner_dict_avg
                df_sum = df1.filter(df1[dim] == highest_level_by_sum)
                inner_dict_sum = self.generate_inner_data_dict(highest_level_by_sum,df_sum,dim,self.dimension_columns,overall_aggregation,anova_narr)
                inner_dict_sum["dim1"] = dim
                inner_dict_sum["measure_column"] = self.measure_column
                inner_dict_sum["highest_level_by_sum"] = highest_level_by_sum
                data_dict["sum"] = inner_dict_sum
                self.analysis[dim]["avg"] = \
                        NarrativesUtils.get_template_output(self._base_dir,'anova_drilldown_avg.html',data_dict['avg'])
                self.analysis[dim]["sum"] = \
                        NarrativesUtils.get_template_output(self._base_dir,'anova_drilldown_avg.html',data_dict['sum'])
            else:
                df_avg = df1.filter(df1[dim] == highest_level_by_avg)
                inner_dict = self.generate_inner_data_dict(highest_level_by_avg,df_avg,dim,self.dimension_columns,overall_aggregation,anova_narr)
                inner_dict["dim1"] = dim
                inner_dict["highest_level_by_avg"] = highest_level_by_avg
                data_dict["avg"] = inner_dict
                data_dict["sum"] = data_dict["avg"]
                self.analysis[dim]["avg"] = \
                        NarrativesUtils.get_template_output(self._base_dir,'anova_drilldown_avg.html',data_dict['avg'])
