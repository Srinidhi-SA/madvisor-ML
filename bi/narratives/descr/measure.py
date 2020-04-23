import humanize

from bi.common import NormalCard, SummaryCard, NarrativesTree, C3ChartData, TableData
from bi.common import NormalChartData, ChartJson
from bi.common import utils as CommonUtils
from bi.narratives import utils as NarrativesUtils
from bi.settings import setting as GLOBALSETTINGS


class MeasureColumnNarrative:

    MAX_FRACTION_DIGITS = 2

    def __init__(self, column_name, measure_descr_stats, df_helper, df_context, result_setter, story_narrative,scriptWeight=None, analysisName=None):
        self._story_narrative = story_narrative
        self._result_setter = result_setter
        self._column_name = column_name.lower()
        self._capitalized_column_name = "%s%s" % (column_name[0].upper(), column_name[1:])
        self._measure_descr_stats = measure_descr_stats
        self._five_point_summary_stats = measure_descr_stats.get_five_point_summary_stats()
        # self._histogram = measure_descr_stats.get_histogram()
        # self._num_columns = context.get_column_count()
        # self._num_rows = context.get_row_count()
        # self._measures = context.get_measures()
        # self._dimensions = context.get_dimensions()
        # self._time_dimensions = context.get_time_dimension()
        self._dataframe_helper = df_helper
        self._dataframe_context = df_context
        self._storyOnScoredData = self._dataframe_context.get_story_on_scored_data()
        self.title = None
        self.heading = self._capitalized_column_name + ' Performance Analysis'
        self.sub_heading = "Distribution of " + self._capitalized_column_name
        self.summary = None
        self._analysis1 = None
        self._analysis2 = None
        self.analysis = None
        self.take_away = None
        self.card2 = ''
        self._blockSplitter = GLOBALSETTINGS.BLOCKSPLITTER
        self._highlightFlag = "|~HIGHLIGHT~|"
        self._base_dir = "/descriptive/"
        self.num_measures = len(self._dataframe_helper.get_numeric_columns())
        self.num_dimensions = len(self._dataframe_helper.get_string_columns())
        self.num_time_dimensions = len(self._dataframe_helper.get_timestamp_columns())

        self._completionStatus = self._dataframe_context.get_completion_status()
        self._messageURL = self._dataframe_context.get_message_url()
        if analysisName == None:
            self._analysisName = self._dataframe_context.get_analysis_name()
        else:
            self._analysisName = analysisName
        if scriptWeight == None:
            self._scriptWeightDict = self._dataframe_context.get_measure_analysis_weight()
        else:
            self._scriptWeightDict = scriptWeight
        self._scriptStages = {
            "statNarrativeStart":{
                "summary":"Started the Descriptive Stats Narratives",
                "weight":0
                },
            "statNarrativeEnd":{
                "summary":"Narratives for descriptive Stats Finished",
                "weight":10
                },
            }

        CommonUtils.create_update_and_save_progress_message(self._dataframe_context,self._scriptWeightDict,self._scriptStages,self._analysisName,"statNarrativeStart","info",display=False,emptyBin=False,customMsg=None,weightKey="narratives")


        self._measureSummaryNode = NarrativesTree()
        self._headNode = NarrativesTree()
        self._headNode.set_name("Overview")
        self._generate_narratives()
        self._story_narrative.add_a_node(self._measureSummaryNode)
        self._result_setter.set_head_node(self._headNode)
        self._result_setter.set_distribution_node(self._measureSummaryNode)

        CommonUtils.create_update_and_save_progress_message(self._dataframe_context,self._scriptWeightDict,self._scriptStages,self._analysisName,"statNarrativeEnd","info",display=False,emptyBin=False,customMsg=None,weightKey="narratives")


    def _get_c3_histogram(self):
        data = self._measure_descr_stats.get_histogram()
        data_c3 = []
        for bin in data:
            data_c3.append({'bin_name':'< '+ humanize.intcomma(round(bin['end_value'],2)),
                            'Count':bin['num_records']})

        data_c3 = NormalChartData(data_c3)
        chartObj = ChartJson(data=data_c3.get_data(), axes={'x':'bin_name','y':'Count'},label_text={'x':'','y':'No. of Observations'},chart_type='bar')
        chartObj.set_yaxis_number_format(".2s")
        return chartObj
    def _generate_narratives(self):
        lines = []
        self._generate_title()
        if self._storyOnScoredData != True:
            self._generate_summary()
        self._analysis1 = self._generate_analysis_para1()
        self._analysis2 = self._generate_analysis_para2()
        lines += NarrativesUtils.block_splitter(self._analysis1,self._blockSplitter)
        lines += [C3ChartData(self._get_c3_histogram())]
        self._tableData = [['Minimum','Quartile 1','Median','Quartile 3','Maximum'],
                            [NarrativesUtils.round_number(self._measure_descr_stats.get_min()),
                             NarrativesUtils.round_number(self._five_point_summary_stats.get_q1_split()),
                             NarrativesUtils.round_number(self._five_point_summary_stats.get_q2_split()),
                             NarrativesUtils.round_number(self._five_point_summary_stats.get_q3_split()),
                             NarrativesUtils.round_number(self._measure_descr_stats.get_max())]]
        lines += [TableData({'tableType':'normal','tableData':self._tableData})]
        lines += NarrativesUtils.block_splitter(self._analysis2,self._blockSplitter)
        if self.card2 != '':
            lines += self.card2['data']['content']
        measureCard1 = NormalCard(name=self.sub_heading,slug=None,cardData = lines)
        self._measureSummaryNode.add_a_card(measureCard1)
        self._measureSummaryNode.set_name("Overview")
        self.analysis = [self._analysis1, self._analysis2]
        self.take_away = self._generate_take_away()

    def _generate_title(self):
        self.title = '%s Performance Report' % (self._capitalized_column_name,)

    def _generate_summary(self):

        ignored_columns = self._dataframe_context.get_ignore_column_suggestions()
        if ignored_columns == None:
            ignored_columns = []

        data_dict = {"n_c" : self._dataframe_helper.get_num_columns(),
                    "n_m" : len(self._dataframe_helper.get_numeric_columns()),
                    "n_d" : len(self._dataframe_helper.get_string_columns()),
                    "n_td" : len(self._dataframe_helper.get_timestamp_columns()),
                    "c" : self._column_name,
                    "d" : self._dataframe_helper.get_string_columns(),
                    "m" : self._dataframe_helper.get_numeric_columns(),
                    "td" : self._dataframe_helper.get_timestamp_columns(),
                    "observations" : self._dataframe_helper.get_num_rows(),
                    "ignorecolumns" : ignored_columns,
                    "n_t" : len(self._dataframe_helper.get_string_columns())+len(self._dataframe_helper.get_numeric_columns())+len(self._dataframe_helper.get_timestamp_columns())
                    # "n_t" : self._dataframe_helper.get_num_columns()+len(ignored_columns)
        }
        self.summary = NarrativesUtils.get_template_output(self._base_dir,\
                                        'descr_stats_summary.html',data_dict)
        MeasureSummaryCard = SummaryCard(name='Summary',slug=None,cardData = None)
        MeasureSummaryCard.set_no_of_measures(data_dict["n_m"])
        MeasureSummaryCard.set_no_of_dimensions(data_dict["n_d"])
        MeasureSummaryCard.set_no_of_time_dimensions(data_dict["n_td"])
        MeasureSummaryCard.set_summary_html(NarrativesUtils.block_splitter(self.summary,self._blockSplitter))
        self._story_narrative.add_a_card(MeasureSummaryCard)
        self._headNode.add_a_card(MeasureSummaryCard)

    def _generate_analysis_para1(self):
        output = 'Para1 entered'
        data_dict = {"cols" : self._dataframe_helper.get_num_columns(),
                    "min" : NarrativesUtils.round_number(self._measure_descr_stats.get_min(), 0),
                    "max" : NarrativesUtils.round_number(self._measure_descr_stats.get_max(), 0),
                    "n" : self._five_point_summary_stats.get_num_outliers(),
                    "l" : self._five_point_summary_stats.get_left_outliers(),
                    "r" : self._five_point_summary_stats.get_right_outliers(),
                    "m" : self._dataframe_helper.get_numeric_columns(),
                    "total" : NarrativesUtils.round_number(self._measure_descr_stats.get_total(), 0),
                    "avg" : NarrativesUtils.round_number(self._measure_descr_stats.get_mean(), 2),
                    "o": self._five_point_summary_stats.get_num_outliers(),
                    "col_name": self._column_name,
                    'rows': self._dataframe_helper.get_num_rows()
        }
        output = NarrativesUtils.get_template_output(self._base_dir,\
                                        'distribution_narratives.html',data_dict)
        return output

    def _generate_analysis_para2(self):
        output = 'Para2 entered'
        histogram_buckets = self._measure_descr_stats.get_histogram()
        print histogram_buckets
        print "$"*200
        threshold = self._dataframe_helper.get_num_rows() * 0.75
        s = 0
        start = 0
        end = len(histogram_buckets)
        flag = 0
        for bin_size in range(1,len(histogram_buckets)):
            s_t = 0
            for i in range(len(histogram_buckets)-bin_size+1):
                s_t = 0
                for j in range(i,i+bin_size):
                    s_t = s_t + histogram_buckets[j]['num_records']
                if(s_t >= threshold) and (s_t > s):
                    s = s_t
                    start = i
                    end = i + bin_size - 1
                    flag = 1
            if (flag == 1):
                break
        bin_size_75 = (end - start + 1)*100/len(histogram_buckets)
        s = s*100/self._dataframe_helper.get_num_rows()
        print histogram_buckets
        print "="*120
        start_value = histogram_buckets[start]['start_value']
        print start,end
        if end >= len(histogram_buckets):
            end = len(histogram_buckets)-1
        print start,end
        end_value = histogram_buckets[end]['end_value']
        if len(histogram_buckets) > 2:
            lowest = min(histogram_buckets[0]['num_records'],histogram_buckets[1]['num_records'],histogram_buckets[2]['num_records'])
            highest = max(histogram_buckets[0]['num_records'],histogram_buckets[1]['num_records'],histogram_buckets[2]['num_records'])
        else:
            lowest = min(histogram_buckets[0]['num_records'],histogram_buckets[1]['num_records'])
            highest = max(histogram_buckets[0]['num_records'],histogram_buckets[1]['num_records'])

        quartile_sums = self._five_point_summary_stats.get_sums()
        quartile_means = self._five_point_summary_stats.get_means()
        print quartile_means
        quartile_frequencies = self._five_point_summary_stats.get_frequencies()
        total = self._measure_descr_stats.get_total()
        avg = self._measure_descr_stats.get_mean()
        counts = self._measure_descr_stats.get_num_values()

        data_dict = {"histogram" : histogram_buckets,
                    "per_cont_hist1" : NarrativesUtils.round_number(histogram_buckets[0]['num_records']*100/self._measure_descr_stats.get_total(), MeasureColumnNarrative.MAX_FRACTION_DIGITS),
                    "per_cont_hist2" : NarrativesUtils.round_number(histogram_buckets[1]['num_records']*100/self._measure_descr_stats.get_total(), MeasureColumnNarrative.MAX_FRACTION_DIGITS),
                    "lowest_cont" : NarrativesUtils.round_number(lowest*100/self._measure_descr_stats.get_total(), MeasureColumnNarrative.MAX_FRACTION_DIGITS),
                    "highest_cont" : NarrativesUtils.round_number(highest*100/self._measure_descr_stats.get_total(), MeasureColumnNarrative.MAX_FRACTION_DIGITS),
                    "num_bins" : len(histogram_buckets),
                    "seventy_five" : bin_size_75,
                    "col_name" : self._column_name,
                    "skew" : self._measure_descr_stats.get_skew(),
                    "three_quarter_percent" : round(s,2),
                    "start_value" : start_value,
                    "end_value" : end_value,
                    "measure_colname":self._column_name,
                    "q4_cont" : NarrativesUtils.round_number(quartile_frequencies['q4']*100.0/counts, 2),
                    "q1_cont" : NarrativesUtils.round_number(quartile_frequencies['q1']*100.0/counts, 2),
                    "q4_frac" : NarrativesUtils.round_number(quartile_sums['q4']*100.0/total, 2),
                    "q1_frac" : NarrativesUtils.round_number(quartile_sums['q1']*100.0/total, 2),
                    "q4_sum" : NarrativesUtils.round_number(quartile_sums['q4'], 2),
                    "q4_mean" : NarrativesUtils.round_number(quartile_means['q4'], 2),
                    "q1_sum" : NarrativesUtils.round_number(quartile_sums['q1'], 2),
                    "q4_overall_mean" : round(quartile_means['q4']*1.0/avg, 2),
                    "total" : NarrativesUtils.round_number(total,2),
                    "avg" : NarrativesUtils.round_number(avg,2),
                    "highlightFlag":self._highlightFlag,
                    "blockSplitter":self._blockSplitter
        }
        try:
            data_dict["q4_q1_mean"] = round(quartile_means['q4']*1.0/quartile_means['q1'] - 1, 1)
        except:
            data_dict["q4_q1_mean"] = None

        self._result_setter.update_executive_summary_data({"skew":data_dict["skew"]})
        if abs(self._measure_descr_stats.get_skew())>0.1:
            content = NarrativesUtils.get_template_output(self._base_dir,\
                                            'descriptive_card2.html',data_dict)
            blocks = NarrativesUtils.block_splitter(content,self._blockSplitter,highlightFlag=self._highlightFlag)
            self.card2 = {}
            self.card2['data'] = {
                                    'heading': 'Concentration of High & Low segments',
                                    'content': blocks
                                }
            quartiles = ['q1','q2','q3','q4']
            observations = [0.0] + [quartile_frequencies[i]*100.0/counts for i in quartiles]
            totals = [0.0] + [quartile_sums[i]*100.0/total for i in quartiles]
            chart = {'x-label': '% of Observations',
                    'y-label': '% of Total '+self._column_name+' (Cumulative)',
                    'x': list(NarrativesUtils.accumu(observations)),
                    'y': list(NarrativesUtils.accumu(totals))}
            self.card2['chart'] = chart
        output = NarrativesUtils.get_template_output(self._base_dir,\
                                        'histogram_narrative.html',data_dict)
        return output

    def _generate_take_away(self):
        output = 'Takeaway entered'
        histogram_buckets = self._measure_descr_stats.get_histogram()
        threshold = self._dataframe_helper.get_num_rows() * 0.75
        s = 0
        start = 0
        end = len(histogram_buckets)
        flag = 0
        for bin_size in range(1,len(histogram_buckets)):
            s_t = 0
            for i in range(len(histogram_buckets)-bin_size+1):
                s_t = 0
                for j in range(i,i+bin_size):
                    s_t = s_t + histogram_buckets[j]['num_records']
                if(s_t >= threshold) and (s_t > s):
                    s = s_t
                    start = i
                    end = i + bin_size - 1
                    flag = 1
            if (flag == 1):
                break
        bin_size_75 = (end - start + 1)*100/len(histogram_buckets)
        s = s*100/self._dataframe_helper.get_num_rows()
        start_value = histogram_buckets[start]['start_value']
        if end >= len(histogram_buckets):
            end = len(histogram_buckets)-1
        end_value = histogram_buckets[end]['end_value']
        data_dict = {"num_bins" : len(histogram_buckets),
                    "seventy_five" : bin_size_75,
                    "col_name" : self._column_name,
                    "c_col_name" : self._capitalized_column_name,
                    "skew" : self._measure_descr_stats.get_skew(),
                    "start": start_value,
                    "end": end_value
                    }
        if (len(histogram_buckets)>3):
            output = NarrativesUtils.get_template_output(self._base_dir,\
                                            'histogram_takeaway.html',data_dict)
        return output
