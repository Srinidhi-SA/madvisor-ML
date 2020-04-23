import operator
import time

import numpy as np
import pyspark.sql.functions as FN
from pyspark.ml.feature import Bucketizer
from pyspark.sql.types import DoubleType

# from nltk import tokenize
from bi.algorithms import LinearRegression
from bi.common import ScatterChartData, ChartJson
from bi.common import utils as CommonUtils
from bi.narratives import utils as NarrativesUtils
from bi.stats.util import Stats


class LinearRegressionNarrative:
    STRONG_CORRELATION = 0.7
    MODERATE_CORRELATION = 0.3


    def __init__(self, regression_result, column_correlations, df_helper,df_context,meta_parser,spark):
        self._dataframe_helper = df_helper
        self._dataframe_context = df_context
        self._metaParser = meta_parser
        self._regression_result = regression_result
        self._data_frame = self._dataframe_helper.get_data_frame()
        self._spark = spark
        self._measure_columns = self._dataframe_helper.get_numeric_columns()
        self._result_column = self._dataframe_helper.resultcolumn
        self._column_correlations = column_correlations
        self._dataframe_context.set_ignore_msg_regression_elasticity(True)

        self._sample_size = min(int(df_helper.get_num_rows()*0.8),2000)
        self.heading = '%s Performance Analysis'%(self._result_column)
        self.sub_heading = 'Analysis by Measure'
        self.output_column_sample = None
        self.summary = None
        self.key_takeaway = None
        self.narratives = {}
        self._base_dir = "/regression/"

    def generate_main_card_data(self):
        all_x_variables = [x for x in self._measure_columns if x != self._regression_result.get_output_column()]
        significant_measures = self._regression_result.get_input_columns()
        non_sig_measures = [x for x in all_x_variables if x not in significant_measures]
        data_dict = {
                    "n_m" : len(self._measure_columns),
                    "n_d" : len(self._dataframe_helper.get_string_columns()),
                    "n_td" : len(self._dataframe_helper.get_timestamp_columns()),
                    "all_measures" : self._measure_columns,
                    "om" : all_x_variables,
                    "n_o_m" : len(all_x_variables),
                    'sm': significant_measures,
                    'n_s_m' : len(significant_measures),
                    'n_ns_m': len(non_sig_measures),
                    'nsm': non_sig_measures,
                    "cm": self._regression_result.get_output_column()
        }

        return data_dict

    def generate_card1_data(self,measure_column):
        data_dict = {}
        data_dict["measure_column"] = measure_column
        data_dict["result_column"] = self._result_column
        data_dict["significant_measures"] = self._regression_result.get_input_columns()
        data_dict["n_sig_measures"] = len(data_dict["significant_measures"])
        data_dict["coefficient"] = round(self._regression_result.get_all_coeff()[measure_column]["coefficient"],2)
        data_dict["correlation"] = self._data_frame.corr(self._result_column,measure_column)
        # input_cols = [self._result_column,measure_column]
        # df = self._data_frame
        # kmeans_obj = KmeansClustering(df, self._dataframe_helper, self._dataframe_context, self._spark)
        # kmeans_obj.kmeans_pipeline(input_cols,cluster_count=None,max_cluster=5)
        # kmeans_result = {"stats":kmeans_obj.get_kmeans_result(),"data":kmeans_obj.get_prediction_data()}
        # data_dict["n_cluster"] = kmeans_result["stats"]["cluster_count"]
        # cluster_data_dict = self.generateClusterDataDict(measure_column,kmeans_result)
        # data_dict["cluster_details"] = cluster_data_dict["grp_data"]
        # # cluster_data_dict["chart_data"] = self.sort_chart_date(cluster_data_dict["chart_data"])
        # data_dict["chart_data"] = cluster_data_dict["chart_data"]
        return data_dict

    def sort_chart_date(self, data):
        x,y,color, cluster = data
        x_label = x[0]
        y_label = y[0]
        color_label = color[0]
        all_data = sorted(zip(y[1:],x[1:],color[1:]))
        y = [y_label]+[i[0] for i in all_data]
        x = [x_label]+[i[1] for i in all_data]
        color = [color_label]+[i[2] for i in all_data]
        return [x,y,color,cluster]


    def generate_card2_data(self,measure_column,dim_col_regression):
        dimension_data_dict = self.keyAreasDict(dim_col_regression,measure_column)
        grouped_output = self.generateGroupedMeasureDataDict(measure_column)
        df = grouped_output["data"]
        bins = grouped_output["bins"]
        # print json.dumps(dimension_data_dict,indent=2)
        category_dict = dict(zip(bins.keys(),[str(bins[x][0])+" to "+str(bins[x][1]) for x in bins.keys()]))
        table_data = {}
        for val in dimension_data_dict.keys():
            dimension_data_dict[val]['dimension'] = val
            dimension_data_dict[val]['num_levels'] = len(dimension_data_dict[val]['levels'])
            data = df.groupby(df["BINNED_INDEX"]).pivot(val).avg(self._result_column).toPandas()
            agg_by_dimension = df.groupby(val).agg({self._result_column:'mean'}).collect()
            dimension_data_dict[val]['highest_average'] = max(agg_by_dimension,key=operator.itemgetter(1))[0]
            data = data.fillna(0)
            data.sort_values(by="BINNED_INDEX", inplace=True)
            data.reset_index( drop=True,inplace=True)
            data["BINNED_INDEX"] = data["BINNED_INDEX"].apply(lambda x:category_dict[x])
            colnames = data.columns[1:]
            table_data[val] = {}
            # headers = ['header'+str(i) for i in range(1,len(data.columns)+1)]
            # table_data[val]['header'] = [dict(zip(headers,['Category']+list(colnames)))]
            # table_data[val]['tableData'] = [dict(zip(headers,row)) for row in data.values.tolist()]
            headers = ['header'+str(i) for i in range(1,len(data.index)+2)]
            table_data[val]['header'] = [dict(zip(headers,['Category']+list(data['BINNED_INDEX'])))]
            table_data[val]['tableData'] = [dict(zip(headers,[col]+[round(i,2) for i in data[col].tolist()])) for col in colnames]
        ranked_dimensions = [(dimension_data_dict[dim]['rank'], dim) for dim in dimension_data_dict]
        ranked_dimensions = sorted(ranked_dimensions)
        ranked_dimensions = [dim for rank,dim in ranked_dimensions]
        data_dict = {}
        chart_data = {}
        if len(ranked_dimensions)>0:
            data_dict['dim1'] = dimension_data_dict[ranked_dimensions[0]]
            chart_data['table1']={}
            chart_data['table1']['heading'] = 'Average '+self._result_column
            chart_data['table1']['data'] = table_data[ranked_dimensions[0]]
        else:
            data_dict['dim1'] = ''
            chart_data['table1'] = ''
        if len(ranked_dimensions)>1:
            data_dict['dim2'] = dimension_data_dict[ranked_dimensions[1]]
            chart_data['table2'] = {}
            chart_data['table2']['heading'] = 'Average '+self._result_column
            chart_data['table2']['data'] = table_data[ranked_dimensions[1]]
        else:
            data_dict['dim2'] = {'num_levels':0}
            chart_data['table2'] = ''

        # dimension_data_dict['ranked_dimensions'] = ranked_dimensions
        data_dict['target'] = self._result_column
        data_dict['measure'] = measure_column
        return chart_data, data_dict

    def generate_card3_chart(self, agg_data):
        chart_data = []
        count = 1
        for col in agg_data.columns:
            vals = agg_data[col].tolist()
            if count == 1:
                chart_data.append(['x']+vals)
                count = 0
            else:
                chart_data.append([col]+vals)
        return chart_data

    def generate_card3_data(self, agg_data, measure_column):
        date_column = agg_data.columns[0]
        data_dict = {}
        data_dict['target'] = self._result_column
        data_dict['measure'] = measure_column
        data_dict['total_measure'] = agg_data[measure_column].sum()
        data_dict['total_target'] = agg_data[self._result_column].sum()
        data_dict['fold'] = round(data_dict['total_measure']*100/data_dict['total_target'] - 100.0, 1)
        data_dict['num_dates'] = len(agg_data.index)
        data_dict['start_date'] = agg_data[date_column].iloc[0]
        data_dict['end_date'] = agg_data[date_column].iloc[-1]
        data_dict['start_value'] = round(agg_data[measure_column].iloc[0],2)
        data_dict['end_value'] = round(agg_data[measure_column].iloc[-1],2)
        # data_dict['target_start_value'] = agg_data[self._result_column].iloc[0]
        # data_dict['target_end_value'] = agg_data[self._result_column].iloc[-1]
        data_dict['change_percent'] = NarrativesUtils.round_number(agg_data[measure_column].iloc[-1]*100/agg_data[measure_column].iloc[0] - 100,2)
        data_dict['correlation'] = NarrativesUtils.round_number(agg_data[measure_column].corr(agg_data[self._result_column]),2)
        peak_index = agg_data[measure_column].argmax()
        data_dict['peak_value'] = NarrativesUtils.round_number(agg_data[measure_column].ix[peak_index],2)
        data_dict['peak_date'] = agg_data[date_column].ix[peak_index]
        lowest_index = agg_data[measure_column].argmin()
        data_dict['lowest_value'] = NarrativesUtils.round_number(agg_data[measure_column].ix[lowest_index],2)
        data_dict['lowest_date'] = agg_data[date_column].ix[lowest_index]
        return data_dict

    def generate_card4_data(self,col1,col2):
        #col1 result_column col2 is measure column
        fs = time.time()
        data_dict = {}
        significant_dimensions = self._dataframe_helper.get_significant_dimension()
        print
        print "-"*100
        print "Target Column : ", col1
        print "Measure Column : ", col2
        print "significant_dimensions : ", significant_dimensions
        if significant_dimensions != {}:
            sig_dims = [(x,significant_dimensions[x]) for x in significant_dimensions.keys()]
            sig_dims = sorted(sig_dims,key=lambda x:x[1],reverse=True)
            cat_columns = [x[0] for x in sig_dims[:10]]
        else:
            cat_columns = self._dataframe_helper.get_string_columns()[:10]

        col1_mean = Stats.mean(self._data_frame,col1)
        col2_mean = Stats.mean(self._data_frame,col2)
        print "col1=>",col1," | col2=>",col2
        print col1_mean,col2_mean
        low1low2 = self._data_frame.filter(FN.col(col1) < col1_mean).filter(FN.col(col2) < col2_mean)
        low1high2 = self._data_frame.filter(FN.col(col1) < col1_mean).filter(FN.col(col2) >= col2_mean)
        high1high2 = self._data_frame.filter(FN.col(col1) >= col1_mean).filter(FN.col(col2) >= col2_mean)
        high1low2 = self._data_frame.filter(FN.col(col1) >= col1_mean).filter(FN.col(col2) < col2_mean)
        low1low2Count = low1low2.count()
        low1high2Count = low1high2.count()
        high1high2Count = high1high2.count()
        high1low2Count = high1low2.count()
        contribution = {}
        freq = {}
        elasticity_dict = {}
        print "low1low2:", low1low2Count
        print "low1high2:", low1high2Count
        print "high1high2:", high1high2Count
        print "high1low2:", high1low2Count
        print "quadrant dataframe creation Done in ", time.time() - fs, " seconds."

        dfs = []
        labels = []
        if low1low2Count > 0:
            fs = time.time()
            freq["low1low2"] = self.get_freq_dict(low1low2,cat_columns)[:3]
            print "get_freq_dict Analysis Done in ", time.time() - fs, " seconds."
            contribution["low1low2"] = str(round(low1low2Count*100/self._data_frame.count()))+"%"
            fs = time.time()
            elasticity_dict["low1low2"] = self.run_regression(low1low2,col2)
            print "run_regression(elasticity) Analysis Done in ", time.time() - fs, " seconds."
            dfs.append("low1low2")
            labels.append("Low %s with Low %s"%(col1,col2))
        if low1high2Count > 0:
            fs = time.time()
            freq["low1high2"] = self.get_freq_dict(low1high2,cat_columns)[:3]
            print "get_freq_dict Analysis Done in ", time.time() - fs, " seconds."
            contribution["low1high2"] = str(round(low1high2Count*100/self._data_frame.count()))+"%"
            fs = time.time()
            elasticity_dict["low1high2"] = self.run_regression(low1high2,col2)
            print "run_regression(elasticity) Analysis Done in ", time.time() - fs, " seconds."
            dfs.append("low1high2")
            labels.append("Low %s with High %s"%(col1,col2))
        if high1high2Count > 0:
            fs = time.time()
            freq["high1high2"] = self.get_freq_dict(high1high2,cat_columns)[:3]
            print "get_freq_dict Analysis Done in ", time.time() - fs, " seconds."
            contribution["high1high2"] = str(round(high1high2Count*100/self._data_frame.count()))+"%"
            fs = time.time()
            elasticity_dict["high1high2"] = self.run_regression(high1high2,col2)
            print "run_regression(elasticity) Analysis Done in ", time.time() - fs, " seconds."
            dfs.append("high1high2")
            labels.append("High %s with High %s"%(col1,col2))
        if high1low2Count > 0:
            fs = time.time()
            freq["high1low2"] = self.get_freq_dict(high1low2,cat_columns)[:3]
            print "get_freq_dict Analysis Done in ", time.time() - fs, " seconds."
            contribution["high1low2"] = str(round(high1low2Count*100/self._data_frame.count()))+"%"
            fs = time.time()
            elasticity_dict["high1low2"] = self.run_regression(high1low2,col2)
            print "run_regression(elasticity) Analysis Done in ", time.time() - fs, " seconds."
            dfs.append("high1low2")
            labels.append("High %s with Low %s"%(col1,col2))
        fs = time.time()
        # overall_coeff = self._regression_result.get_coeff(col2)
        overall_coeff = self._regression_result.get_all_coeff()[col2]["coefficient"]
        elasticity_value = overall_coeff * Stats.mean(self._data_frame,col1)/Stats.mean(self._data_frame,col2)
        data_dict["overall_elasticity"] = elasticity_value
        label_dict = dict(zip(dfs,labels))

        data_dict["measure_column"] = col2
        data_dict["result_column"] = col1
        data_dict["label_dict"] = label_dict
        data_dict["elastic_grp_list"] = []
        data_dict["inelastic_grp_list"] = []
        data_dict["elastic_count"] = 0
        data_dict["inelastic_count"] = 0
        for val in dfs:
            elastic_data = elasticity_dict[val]
            if elastic_data["elasticity_value"] > 1:
                data_dict["elastic_count"] += 1
                data_dict["elastic_grp_list"].append((label_dict[val],elastic_data["elasticity_value"]))
            else:
                data_dict["inelastic_count"] += 1
                data_dict["inelastic_grp_list"].append((label_dict[val],elastic_data["elasticity_value"]))

        data_dict["freq"] = freq
        data_dict["contribution"] = contribution
        data_dict["charts"] = {"heading":"","data":[]}

        col1_data = [col1]
        col2_data = [col2]
        color_data = ["Colors"]
        plotColors = []
        if low1low2Count > 0:
            sample_rows = min(100.0, float(low1low2Count))
            low1low2 = low1low2.sample(False, sample_rows/low1low2Count, seed = 50)
            low1low2_col1 = [x[0] for x in low1low2.select(col1).collect()]
            low1low2_col2 = [x[0] for x in low1low2.select(col2).collect()]
            low1low2_color = ["#DD2E1F"]*len(low1low2_col2)
            col1_data += low1low2_col1
            col2_data += low1low2_col2
            color_data += low1low2_color
            plotColors.append("#DD2E1F")
        if low1high2Count > 0:
            sample_rows = min(100.0, float(low1high2Count))
            low1high2 = low1high2.sample(False, sample_rows/low1high2Count, seed = 50)
            low1high2_col1 = [x[0] for x in low1high2.select(col1).collect()]
            low1high2_col2 = [x[0] for x in low1high2.select(col2).collect()]
            low1high2_color = ["#7C5BBB"]*len(low1high2_col2)
            col1_data += low1high2_col1
            col2_data += low1high2_col2
            color_data += low1high2_color
            plotColors.append("#7C5BBB")
        if high1high2Count > 0:
            sample_rows = min(100.0, float(high1high2Count))
            high1high2 = high1high2.sample(False, sample_rows/high1high2Count, seed = 50)
            high1high2_col1 = [x[0] for x in high1high2.select(col1).collect()]
            high1high2_col2 = [x[0] for x in high1high2.select(col2).collect()]
            high1high2_color = ["#00AEB3"]*len(high1high2_col2)
            col1_data += high1high2_col1
            col2_data += high1high2_col2
            color_data += high1high2_color
            plotColors.append("#00AEB3")
        if high1low2Count > 0:
            sample_rows = min(100.0, float(high1low2Count))
            high1low2 = high1low2.sample(False, sample_rows/high1low2Count, seed = 50)
            high1low2_col1 = [x[0] for x in high1low2.select(col1).collect()]
            high1low2_col2 = [x[0] for x in high1low2.select(col2).collect()]
            high1low2_color = ["#EC640C"]*len(high1low2_col2)
            col1_data += high1low2_col1
            col2_data += high1low2_col2
            color_data += high1low2_color
            plotColors.append("#EC640C")


        plot_labels = dict(zip(plotColors,labels))
        all_data = sorted(zip(col2_data[1:],col1_data[1:],color_data[1:]),key=lambda x:x[1])

        scatterData = ScatterChartData()
        data_obj = dict(zip(labels,[[] for i in range(len(labels))]))
        for val in all_data:
            col = val[2]
            obj = {col1:val[1],col2:val[0]}
            key = plot_labels[col]
            data_obj[key].append(obj)
        scatterData.set_data(data_obj)
        scatterChart = ChartJson()
        scatterChart.set_data(scatterData.get_data())
        scatterChart.set_legend(plot_labels)
        scatterChart.set_label_text({"x":col2,"y":col1})
        scatterChart.set_axes({"x":col2,"y":col1})
        scatterChart.set_chart_type("scatter")
        data_dict["charts"] = scatterChart
        print "dsa Analysis Done in ", time.time() - fs, " seconds."
        return data_dict

    #### functions to calculate data dicts for different cards

    def get_freq_dict(self,df,columns):
        # print columns
        column_tuple = zip(columns,[{}]*len(columns))
        output = []
        for val in column_tuple:
            freq_df = df.groupby(val[0]).count().toPandas()
            freq_dict = dict(zip(freq_df[val[0]],freq_df["count"]))
            print freq_dict
            if freq_dict != {}:
                max_level = max(freq_dict,key=freq_dict.get)
                max_val = freq_dict[max_level]
                output.append((val[0],freq_dict,max_level,max_val))
            else:
                print freq_dict
                # print df.select(val[0]).toPandas()
        sorted_output = sorted(output,key=lambda x:x[3],reverse=True)
        return sorted_output



    def run_regression(self,df,measure_column):
        output = {}
        result_column = self._result_column
        result = LinearRegression(df, self._dataframe_helper, self._dataframe_context,self._metaParser,self._spark).fit(result_column)
        result = {"intercept" : result.get_intercept(),
                  "rmse" : result.get_root_mean_square_error(),
                  "rsquare" : result.get_rsquare(),
                  "coeff" : result.get_all_coeff()
                  }
        if measure_column in result["coeff"].keys():
            output["coeff"] = result["coeff"][measure_column]["coefficient"]
            try:
                output["elasticity_value"] = output["coeff"] * Stats.mean(df,result_column)/Stats.mean(df,measure_column)
            except:
                output["elasticity_value"] = 0
        else:
            output["coeff"] = 0
            output["elasticity_value"] = 0
        return output


    def keyAreasDict(self,dim_col_regression,measure_col):
        data = dim_col_regression
        dimension_data_dict = {}
        dims = data.keys()
        dimension_level_coeff_dict = {}
        all_coeff_list = []
        highest_coeff = {}
        lowest_coeff = {}
        for dim in dims:
            levels = data[dim].keys()
            try:
                coeff_list = [(x,round(data[dim][x]["coeff"][measure_col]["coefficient"],2)) if (isinstance(data[dim][x]['coeff'],dict) and data[dim][x]["coeff"].has_key(measure_col)) else (x,0.0) for x in levels ]
            except:
                continue
            coeff_list = sorted(coeff_list,key=lambda x:abs(x[1]),reverse=True)
            highest_coeff[dim] = coeff_list[0]
            lowest_coeff[dim] = coeff_list[-1]
            all_coeff_list.append([coeff_list[0],dim])
        all_coeff_list = sorted(all_coeff_list,key=lambda x:abs(x[0][1]),reverse=True)
        print "all_coeff_list"
        print all_coeff_list
        top2_dims = [x[1] for x in all_coeff_list[:2]]
        dimension_data_dict = dict(zip(top2_dims,[{}]*len(top2_dims)))
        for val in top2_dims:
            temp_dict = {}
            temp_dict["levels"] = data[val].keys()
            temp_dict["highest_impact_level"] = highest_coeff[val]
            temp_dict["lowest_impact_level"] = lowest_coeff[val]
            dimension_data_dict[val] = temp_dict
        print '*'*100
        print 'TOP 2 DIMS  :  ',top2_dims
        print 'Dimension Data Dict  :  ',dimension_data_dict
        dimension_data_dict[top2_dims[0]]["rank"] = 1
        if len(top2_dims)>1:
            dimension_data_dict[top2_dims[1]]["rank"] = 2
        return dimension_data_dict

    def generateGroupedMeasureDataDict(self,measure_column):
        splits_data = self.get_measure_column_splits(self._data_frame,measure_column, 4)
        splits = splits_data["splits"]
        double_df = self._data_frame.withColumn(measure_column, self._data_frame[measure_column].cast(DoubleType()))
        bucketizer = Bucketizer(inputCol=measure_column,
                        outputCol="BINNED_INDEX")
        bucketizer.setSplits(splits)
        binned_df = bucketizer.transform(double_df)
        unique_bins = binned_df.select("BINNED_INDEX").distinct().collect()
        unique_bins = [int(x[0]) for x in unique_bins]
        binned_index_dict = dict(zip(unique_bins,splits_data["splits_range"]))
        output = {"bins":binned_index_dict,"data":binned_df}
        return output

    def get_measure_column_splits(self,df,colname,n_split = 5):
        """
        n_split = number of splits required -1
        splits = [0.0, 23.0, 46.0, 69.0, 92.0, 115.0]
        splits_range = [(0.0, 23.0), (23.0, 46.0), (46.0, 69.0), (69.0, 92.0), (92.0, 115.0)]
        """
        n_split = 5
        minimum_val = Stats.min(df,colname)
        maximum_val = Stats.max(df,colname)
        splits  = CommonUtils.frange(minimum_val,maximum_val,num_steps=n_split)
        splits = sorted(splits)
        splits_range = [(splits[idx],splits[idx+1]) for idx in range(len(splits)-1)]
        output = {"splits":splits,"splits_range":splits_range}
        return output


    def generateClusterDataDict(self,measure_column,kmeans_result):
        kmeans_stats = kmeans_result["stats"]
        input_columns = kmeans_stats["inputCols"]
        kmeans_df = kmeans_result["data"]
        cluster_data_dict = {"chart_data":None,"grp_data":None}
        grp_df = kmeans_df.groupBy("prediction").count().toPandas()
        grp_counts = zip(grp_df["prediction"], grp_df["count"])
        grp_counts = sorted(grp_counts,key=lambda x:x[1],reverse=True)
        grp_dict = dict(grp_counts)

        colors = ["red","blue","green","yellow","black"]
        cluster_ids = list(grp_df["prediction"])
        color_dict = dict(zip(cluster_ids,colors[:len(cluster_ids)]))

        chart_data = {"heading":"","data":[]}
        result_col_data = [self._result_column]
        measure_col_data = [measure_column]
        color_data = ["Colors"]
        plot_labels = ["Cluster Labels"]

        grp_data = []
        total = float(sum(grp_dict.values()))
        for grp_id in list(grp_df["prediction"]):
            data = {}
            data["group_number"] = grp_id+1
            data["count"] = grp_dict[grp_id]
            data["contribution"] = round(grp_dict[grp_id]*100/total,2)
            df = kmeans_df.filter(FN.col("prediction") == grp_id)
            data["columns"] = dict(zip(input_columns,[{}]*len(input_columns)))
            for val in input_columns:
                data["columns"][val]["avg"] = round(Stats.mean(df,val),2)
            grp_data.append(data)
            # preparing chart data
            grp_result_data = [x[0] for x in df.select(self._result_column).collect()]
            result_col_data += grp_result_data
            grp_measure_data = [x[0] for x in df.select(measure_column).collect()]
            measure_col_data += grp_measure_data
            color_list = [color_dict[grp_id]]*len(grp_measure_data)
            color_data += color_list
            label_list = ["Cluster "+str(int(grp_id))]
            plot_labels += label_list

        grp_data = sorted(grp_data,key=lambda x:x["contribution"],reverse=True)
        chart_data = [measure_col_data,result_col_data,color_data,plot_labels]
        cluster_data_dict["grp_data"] = grp_data
        cluster_data_dict["chart_data"] = chart_data
        return cluster_data_dict



    def headers_to_cols(self,data):
        headers = sorted(data.keys())
        out = []
        for key in headers:
            out.append(data[key])
        return out

    def convert_table_data(self,tabledata):
        column_data = []
        first_col = self.headers_to_cols(tabledata["data"]["header"][0])
        other_cols = [self.headers_to_cols(obj) for obj in tabledata["data"]["tableData"]]
        column_data.append(first_col)
        column_data += other_cols
        out = np.column_stack(column_data)
        out = [list(row) for row in out]
        return out
