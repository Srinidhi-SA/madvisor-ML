from anova_drilldown import AnovaDrilldownNarratives
from bi.common import NormalCard, NarrativesTree, C3ChartData,HtmlData
from bi.common import NormalChartData, ChartJson
from bi.common import utils as CommonUtils
from bi.narratives import utils as NarrativesUtils
from bi.narratives.anova.anova import OneWayAnovaNarratives
from bi.settings import setting as GLOBALSETTINGS


class AnovaNarratives:
    ALPHA = 0.05

    KEY_SUMMARY = 'summary'
    KEY_NARRATIVES = 'narratives'
    KEY_TAKEAWAY = 'key_takeaway'
    DRILL_DOWN = 'drill_down_narrative'
    KEY_CARD = 'card'
    KEY_HEADING = 'heading'
    KEY_SUBHEADING = 'header'
    KEY_CHART = 'charts'
    KEY_PARAGRAPH = 'paragraphs'
    KEY_PARA_HEADER = 'header'
    KEY_PARA_CONTENT = 'content'
    KEY_BUBBLE = 'bubble_data'

    # @accepts(object, DFAnovaResult, DataFrameHelper)
    def __init__(self, df_anova_result, df_helper, df_context, result_setter,story_narrative,scriptWeight=None, analysisName=None):
        self._story_narrative = story_narrative
        self._result_setter = result_setter
        self._dataframe_context = df_context
        self._df_anova_result = df_anova_result
        self._df_helper = df_helper
        self.narratives = {}
        self.narratives['variables'] = ''
        self._blockSplitter = GLOBALSETTINGS.BLOCKSPLITTER
        self._base_dir = "/anova/"

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
            "anovaNarrativeStart":{
                "summary":"Started the Anova Narratives",
                "weight":0
                },
            "anovaNarrativeEnd":{
                "summary":"Narratives for Anova Finished",
                "weight":10
                },
            }
        # self._completionStatus += self._scriptWeightDict[self._analysisName]["narratives"]*self._scriptStages["anovaNarrativeStart"]["weight"]/10
        # progressMessage = CommonUtils.create_progress_message_object(self._analysisName,\
        #                             "anovaNarrativeStart",\
        #                             "info",\
        #                             self._scriptStages["anovaNarrativeStart"]["summary"],\
        #                             self._completionStatus,\
        #                             self._completionStatus)
        # CommonUtils.save_progress_message(self._messageURL,progressMessage)
        # self._dataframe_context.update_completion_status(self._completionStatus)
        CommonUtils.create_update_and_save_progress_message(self._dataframe_context,self._scriptWeightDict,self._scriptStages,self._analysisName,"anovaNarrativeStart","info",display=False,emptyBin=False,customMsg=None,weightKey="narratives")



        self._generate_narratives()

        # self._completionStatus += self._scriptWeightDict[self._analysisName]["narratives"]*self._scriptStages["anovaNarrativeEnd"]["weight"]/10
        # progressMessage = CommonUtils.create_progress_message_object(self._analysisName,\
        #                             "anovaNarrativeEnd",\
        #                             "info",\
        #                             self._scriptStages["anovaNarrativeEnd"]["summary"],\
        #                             self._completionStatus,\
        #                             self._completionStatus)
        # CommonUtils.save_progress_message(self._messageURL,progressMessage)
        # self._dataframe_context.update_completion_status(self._completionStatus)
        CommonUtils.create_update_and_save_progress_message(self._dataframe_context,self._scriptWeightDict,self._scriptStages,self._analysisName,"anovaNarrativeEnd","info",display=False,emptyBin=False,customMsg=None,weightKey="narratives")


        if self._anovaNodes.get_card_count() > 0:
            self._story_narrative.add_a_node(self._anovaNodes)
            #self._generate_take_away()
            self._result_setter.set_anova_node(self._anovaNodes)

    def _generate_narratives(self):
        self._anovaNodes = NarrativesTree()
        self._anovaNodes.set_name("Performance")
        for measure_column in self._df_anova_result.get_measure_columns():
            measure_anova_result = self._df_anova_result.get_measure_result(measure_column)
            significant_dimensions_dict, insignificant_dimensions = measure_anova_result.get_OneWayAnovaSignificantDimensions()
            significant_dimensions = [k for k,v in sorted(significant_dimensions_dict.items(), key=lambda x: -x[1])]
            num_significant_dimensions = len(significant_dimensions)
            num_insignificant_dimensions = len(insignificant_dimensions)
            print "num_significant_dimensions",num_significant_dimensions
            if num_significant_dimensions > 0:
                mainCard = NormalCard(name = "Overview of Key Factors")
                data_c3 = []
                for sig_dim in significant_dimensions:
                    data_c3.append({'dimension':sig_dim, 'effect_size':float(significant_dimensions_dict[sig_dim])})
                self.narratives = {}
                self.narratives[AnovaNarratives.KEY_HEADING] = "%s Performance Analysis" % (measure_column,)
                self.narratives['main_card'] = {}
                self.narratives['cards'] = []
                self.narratives['main_card'][AnovaNarratives.KEY_SUBHEADING] = "Relationship between %s and other Dimensions" % (measure_column)
                self.narratives['main_card'][AnovaNarratives.KEY_PARAGRAPH] = []
                data_dict = { \
                                'significant_dimensions' : significant_dimensions,
                                'insignificant_dimensions' : insignificant_dimensions,
                                'num_significant_dimensions' : num_significant_dimensions,
                                'num_insignificant_dimensions' : num_insignificant_dimensions,
                                'num_dimensions' : num_significant_dimensions+num_insignificant_dimensions,
                                'target' : measure_column \
                            }
                output = {'header' : ''}
                output['content'] = NarrativesUtils.get_template_output(self._base_dir,'anova_template_1.html',data_dict)
                self.narratives['main_card'][AnovaNarratives.KEY_PARAGRAPH].append(output)
                output1 = {'header' : ''}
                output1['content'] = NarrativesUtils.get_template_output(self._base_dir,'anova_template_2.html',data_dict)
                lines = []
                lines += NarrativesUtils.block_splitter(output['content'],self._blockSplitter)
                data_c3 = NormalChartData(data_c3)
                chart_data = data_c3.get_data()
                chartDataValues = []
                for obj in chart_data:
                    chartDataValues.append(obj["effect_size"])
                chart_json = ChartJson(data = chart_data,axes={'x':'dimension','y':'effect_size'},
                                        label_text={'x':'','y':'Effect Size'},chart_type='bar')
                chart_json.set_axis_rotation(True)
                # chart_json.set_yaxis_number_format(".4f")
                chart_json.set_yaxis_number_format(NarrativesUtils.select_y_axis_format(chartDataValues))
                # st_info = ["Test : ANOVA", "Threshold for p-value : 0.05", "Effect Size : Tukey's HSD"]
                statistical_info_array=[
                    ("Test Type","ANOVA"),
                    ("Effect Size","ETA squared"),
                    ("Max Effect Size",chart_data[0]["dimension"]),
                    ("Min Effect Size",chart_data[-1]["dimension"]),
                    ]
                statistical_inferenc = ""
                if len(chart_data) == 1:
                    statistical_inference = "{} is the only variable that have significant association with the {} (Target) having an \
                     Effect size of {}".format(chart_data[0]["dimension"],self._dataframe_context.get_result_column(),round(chart_data[0]["effect_size"],4))
                elif len(chart_data) == 2:
                    statistical_inference = "There are two variables ({} and {}) that have significant association with the {} (Target) and the \
                     Effect size ranges are {} and {} respectively".format(chart_data[0]["dimension"],chart_data[1]["dimension"],self._dataframe_context.get_result_column(),round(chart_data[0]["effect_size"],4),round(chart_data[1]["effect_size"],4))
                else:
                    statistical_inference = "There are {} variables that have significant association with the {} (Target) and the \
                     Effect size ranges from {} to {}".format(len(chart_data),self._dataframe_context.get_result_column(),round(chart_data[0]["effect_size"],4),round(chart_data[-1]["effect_size"],4))
                if statistical_inference != "":
                    statistical_info_array.append(("Inference",statistical_inference))
                statistical_info_array = NarrativesUtils.statistical_info_array_formatter(statistical_info_array)
                lines += [C3ChartData(data=chart_json,info=statistical_info_array)]
                lines += NarrativesUtils.block_splitter(output1['content'],self._blockSplitter)
                mainCard.set_card_data(lines)
                self._anovaNodes.add_a_card(mainCard)
                self.narratives['main_card'][AnovaNarratives.KEY_PARAGRAPH].append(output1)
                self.narratives['main_card'][AnovaNarratives.KEY_CHART] = {}
                effect_size_chart = { 'heading' : '',
                                      'labels' : {'Dimension':'Effect Size'},
                                      'data' : significant_dimensions_dict}
                print significant_dimensions_dict
                self.narratives['main_card'][AnovaNarratives.KEY_CHART]['effect_size'] = effect_size_chart
                progressMessage = CommonUtils.create_progress_message_object(self._analysisName,"custom","info","Analyzing key drivers",self._completionStatus,self._completionStatus,display=True)
                CommonUtils.save_progress_message(self._messageURL,progressMessage,ignore=False)
                self._generate_dimension_narratives(significant_dimensions, measure_anova_result, measure_column)
            else:
                mainCard = NormalCard(name = "Overview of Key Factors")
                cardText=HtmlData("There are no dimensions in the dataset that have significant influence on {}".format(measure_column))
                mainCard.set_card_data([cardText])
                self._anovaNodes.add_a_card(mainCard)


    def _generate_dimension_narratives(self,significant_dimensions, measure_anova_result, measure):
        self.narratives['cards'] = []
        anova_trend_result = measure_anova_result.get_trend_data()
        if len(significant_dimensions) == 0:
            self.narratives['cards'].append({'card1':'', 'card2':'', 'card3':''})
        self.narratives['variables'] = significant_dimensions
        for dimension in significant_dimensions:
            dimensionNode = NarrativesTree(name = dimension)
            narratives = OneWayAnovaNarratives(self._dataframe_context,measure, dimension, measure_anova_result, anova_trend_result,self._result_setter,dimensionNode,self._base_dir)
            self._anovaNodes.add_a_node(dimensionNode)
            self.narratives['cards'].append(narratives)
