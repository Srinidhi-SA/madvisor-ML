import json

from bi.algorithms import LinearRegression
from bi.common import NarrativesTree, NormalCard, HtmlData, C3ChartData, TableData
from bi.common import NormalChartData, ChartJson
from bi.common import utils as CommonUtils
from bi.narratives import utils as NarrativesUtils
from bi.settings import setting as GLOBALSETTINGS
from linear_regression import LinearRegressionNarrative


class RegressionNarrative:
    def __init__(self, df_helper, df_context, result_setter, spark, df_regression_result, correlations,story_narrative,meta_parser):
        self._metaParser = meta_parser
        self._result_setter = result_setter
        self._story_narrative = story_narrative
        self._df_regression_result = df_regression_result
        self._correlations = correlations
        self._dataframe_helper = df_helper
        self._dataframe_context = df_context
        self._blockSplitter = GLOBALSETTINGS.BLOCKSPLITTER

        # self._result_setter.set_trend_section_name("regression")
        self._measure_columns = self._dataframe_helper.get_numeric_columns()
        self._dimension_columns = self._dataframe_helper.get_string_columns()
        self._date_columns = self._dataframe_context.get_date_columns()
        self._uid_col = self._dataframe_context.get_uid_column()
        if self._metaParser.check_column_isin_ignored_suggestion(self._uid_col):
            self._dimension_columns = list(set(self._dimension_columns) - {self._uid_col})
        if len(self._date_columns) >0 :
            self._dimension_columns = list(set(self._dimension_columns)-set(self._date_columns))
        self._spark = spark
        self.measures = []
        self.result_column = self._dataframe_helper.resultcolumn

        self.all_coefficients = self._df_regression_result.get_all_coeff()
        all_coeff = [(x,self.all_coefficients[x]) for x in self.all_coefficients.keys()]
        all_coeff = sorted(all_coeff,key = lambda x:abs(x[1]["coefficient"]),reverse = True)
        self._all_coeffs = all_coeff
        self.significant_measures = [x[0] for x in all_coeff if x[1]['p_value']<=0.05]
        print self.significant_measures
        print "regression narratives started"
        self.narratives = {"heading": self.result_column + "Performance Report",
                           "main_card":{},
                           "cards":[]
                        }
        self._base_dir = "/regression/"
        self._run_dimension_level_regression = False

        # self._dim_regression = self.run_regression_for_dimension_levels()
        self._regressionNode = NarrativesTree()

        self._completionStatus = self._dataframe_context.get_completion_status()
        self._analysisName = self._dataframe_context.get_analysis_name()
        self._messageURL = self._dataframe_context.get_message_url()
        self._scriptWeightDict = self._dataframe_context.get_measure_analysis_weight()
        self._scriptStages = {
            "regressionNarrativeStart":{
                "summary":"Started the Regression Narratives",
                "weight":1
                },
            "regressionNarrativeEnd":{
                "summary":"Narratives for Regression Finished",
                "weight":0
                },
            }
        self._completionStatus += self._scriptWeightDict[self._analysisName]["narratives"]*self._scriptStages["regressionNarrativeStart"]["weight"]/10
        progressMessage = CommonUtils.create_progress_message_object(self._analysisName,\
                                    "regressionNarrativeStart",\
                                    "info",\
                                    self._scriptStages["regressionNarrativeStart"]["summary"],\
                                    self._completionStatus,\
                                    self._completionStatus)
        CommonUtils.save_progress_message(self._messageURL,progressMessage)
        self._dataframe_context.update_completion_status(self._completionStatus)

        self.generate_narratives()
        self._regressionNode.set_name("Influencers")
        self._result_setter.set_regression_node(self._regressionNode)

        self._completionStatus += self._scriptWeightDict[self._analysisName]["narratives"]*self._scriptStages["regressionNarrativeEnd"]["weight"]/10
        progressMessage = CommonUtils.create_progress_message_object(self._analysisName,\
                                    "regressionNarrativeEnd",\
                                    "info",\
                                    self._scriptStages["regressionNarrativeEnd"]["summary"],\
                                    self._completionStatus,\
                                    self._completionStatus)
        CommonUtils.save_progress_message(self._messageURL,progressMessage)
        self._dataframe_context.update_completion_status(self._completionStatus)


    def generate_narratives(self):
        regression_narrative_obj = LinearRegressionNarrative(
                                    self._df_regression_result,
                                    self._correlations,
                                    self._dataframe_helper,
                                    self._dataframe_context,
                                    self._metaParser,
                                    self._spark
                                    )
        main_card_data = regression_narrative_obj.generate_main_card_data()
        main_card_narrative = NarrativesUtils.get_template_output(self._base_dir,\
                                                        'regression_main_card.html',main_card_data)
        self.narratives['main_card'] = {}
        self.narratives["main_card"]['paragraphs'] = NarrativesUtils.paragraph_splitter(main_card_narrative)
        self.narratives["main_card"]['header'] = 'Key Measures that affect ' + self.result_column
        self.narratives["main_card"]['chart'] = {}
        self.narratives["main_card"]['chart']['heading'] = ''
        self.narratives["main_card"]['chart']['data'] = [[i for i,j in self._all_coeffs],
                                                         [j['coefficient'] for i,j in self._all_coeffs]]
        self.narratives["main_card"]['chart']['label'] = {'x':'Measure Name',
                                                            'y': 'Change in ' + self.result_column + ' per unit increase'}

        main_card = NormalCard()
        main_card_header = HtmlData(data = '<h3>Key Measures that affect ' + self.result_column+"</h3>")
        main_card_paragraphs = NarrativesUtils.block_splitter(main_card_narrative,self._blockSplitter)
        main_card_chart_data = [{"key":val[0],"value":val[1]} for val in zip([i for i,j in self._all_coeffs],[j['coefficient'] for i,j in self._all_coeffs])]
        main_card_chart = NormalChartData(data=main_card_chart_data)
        mainCardChartJson = ChartJson()
        mainCardChartJson.set_data(main_card_chart.get_data())
        mainCardChartJson.set_label_text({'x':'Influencing Factors','y': 'Change in ' + self.result_column + ' per unit increase'})
        mainCardChartJson.set_chart_type("bar")
        mainCardChartJson.set_axes({"x":"key","y":"value"})
        mainCardChartJson.set_yaxis_number_format(".2f")
        # st_info = ["Test : Regression","Threshold for p-value: 0.05", "Effect Size: Regression Coefficient"]
        chart_data = sorted(main_card_chart_data,key=lambda x:x["value"],reverse=True)
        statistical_info_array=[
            ("Test Type","Regression"),
            ("Effect Size","Coefficients"),
            ("Max Effect Size",chart_data[0]["key"]),
            ("Min Effect Size",chart_data[-1]["key"]),
            ]
        statistical_inferenc = ""
        if len(chart_data) == 1:
            statistical_inference = "{} is the only variable that have significant influence over {} (Target) having an \
             Effect size of {}".format(chart_data[0]["key"],self._dataframe_context.get_result_column(),round(chart_data[0]["value"],4))
        elif len(chart_data) == 2:
            statistical_inference = "There are two variables ({} and {}) that have significant influence over {} (Target) and the \
             Effect size ranges are {} and {} respectively".format(chart_data[0]["key"],chart_data[1]["key"],self._dataframe_context.get_result_column(),round(chart_data[0]["value"],4),round(chart_data[1]["value"],4))
        else:
            statistical_inference = "There are {} variables that have significant influence over {} (Target) and the \
             Effect size ranges from {} to {}".format(len(chart_data),self._dataframe_context.get_result_column(),round(chart_data[0]["value"],4),round(chart_data[-1]["value"],4))
        if statistical_inference != "":
            statistical_info_array.append(("Inference",statistical_inference))
        statistical_info_array = NarrativesUtils.statistical_info_array_formatter(statistical_info_array)
        main_card.set_card_data(data = [main_card_header]+main_card_paragraphs+[C3ChartData(data=mainCardChartJson,info=statistical_info_array)])
        main_card.set_card_name("Key Influencers")
        self._regressionNode.add_a_card(main_card)


        count = 0
        for measure_column in self.significant_measures:
            sigMeasureNode = NarrativesTree()
            sigMeasureNode.set_name(measure_column)
            measureCard1 = NormalCard()
            measureCard1.set_card_name("{}: Impact on {}".format(measure_column,self.result_column))
            measureCard1Data = []
            if self._run_dimension_level_regression:
                measureCard2 = NormalCard()
                measureCard2.set_card_name("Key Areas where it Matters")
                measureCard2Data = []

            measure_column_cards = {}
            card0 = {}
            card1data = regression_narrative_obj.generate_card1_data(measure_column)
            card1heading = "<h3>Impact of "+measure_column+" on "+self.result_column+"</h3>"
            measureCard1Header = HtmlData(data=card1heading)
            card1data.update({"blockSplitter":self._blockSplitter})
            card1narrative = NarrativesUtils.get_template_output(self._base_dir,\
                                                            'regression_card1.html',card1data)

            card1paragraphs = NarrativesUtils.block_splitter(card1narrative,self._blockSplitter)
            card0 = {"paragraphs":card1paragraphs}
            card0["charts"] = {}
            card0['charts']['chart2']={}
            # card0['charts']['chart2']['data']=card1data["chart_data"]
            # card0['charts']['chart2']['heading'] = ''
            # card0['charts']['chart2']['labels'] = {}
            card0['charts']['chart1']={}
            card0["heading"] = card1heading
            measure_column_cards['card0'] = card0

            measureCard1Header = HtmlData(data=card1heading)
            measureCard1Data += [measureCard1Header]
            measureCard1para = card1paragraphs
            measureCard1Data += measureCard1para

            if self._run_dimension_level_regression:
                print "running narratives for key area dict"
                self._dim_regression = self.run_regression_for_dimension_levels()
                card2table, card2data=regression_narrative_obj.generate_card2_data(measure_column,self._dim_regression)
                card2data.update({"blockSplitter":self._blockSplitter})
                card2narrative = NarrativesUtils.get_template_output(self._base_dir,\
                                                            'regression_card2.html',card2data)
                card2paragraphs = NarrativesUtils.block_splitter(card2narrative,self._blockSplitter)

                card1 = {'tables': card2table, 'paragraphs' : card2paragraphs,
                        'heading' : 'Key Areas where ' + measure_column + ' matters'}
                measure_column_cards['card1'] = card1

                measureCard2Data += card2paragraphs
                if "table1" in card2table:
                    table1data = regression_narrative_obj.convert_table_data(card2table["table1"])
                    card2Table1 = TableData()
                    card2Table1.set_table_data(table1data)
                    card2Table1.set_table_type("heatMap")
                    card2Table1.set_table_top_header(card2table["table1"]["heading"])
                    card2Table1Json = json.loads(CommonUtils.convert_python_object_to_json(card2Table1))
                    # measureCard2Data.insert(3,card2Table1)
                    measureCard2Data.insert(3,card2Table1Json)

                if "table2" in card2table:
                    table2data = regression_narrative_obj.convert_table_data(card2table["table2"])
                    card2Table2 = TableData()
                    card2Table2.set_table_data(table2data)
                    card2Table2.set_table_type("heatMap")
                    card2Table2.set_table_top_header(card2table["table2"]["heading"])
                    # measureCard2Data.insert(5,card2Table2)
                    card2Table2Json = json.loads(CommonUtils.convert_python_object_to_json(card2Table2))
                    # measureCard2Data.append(card2Table2)
                    measureCard2Data.append(card2Table2Json)


            # self._result_setter.set_trend_section_data({"result_column":self.result_column,
            #                                             "measure_column":measure_column,
            #                                             "base_dir":self._base_dir
            #                                             })
            # trend_narratives_obj = TimeSeriesNarrative(self._dataframe_helper, self._dataframe_context, self._result_setter, self._spark, self._story_narrative)
            # card2 =  trend_narratives_obj.get_regression_trend_card_data()
            # if card2:
            #     measure_column_cards['card2'] = card2
            #
            #
            # card3 = {}
            progressMessage = CommonUtils.create_progress_message_object(self._analysisName,"custom","info","Analyzing key influencers",self._completionStatus,self._completionStatus,display=True)
            CommonUtils.save_progress_message(self._messageURL,progressMessage,ignore=False)
            card4data = regression_narrative_obj.generate_card4_data(self.result_column,measure_column)
            card4data.update({"blockSplitter":self._blockSplitter})
            # card4heading = "Sensitivity Analysis: Effect of "+self.result_column+" on Segments of "+measure_column
            card4narrative = NarrativesUtils.get_template_output(self._base_dir,\
                                                                'regression_card4.html',card4data)
            card4paragraphs = NarrativesUtils.block_splitter(card4narrative,self._blockSplitter)
            # card3 = {"paragraphs":card4paragraphs}
            card0['paragraphs'] = card1paragraphs+card4paragraphs
            card4Chart = card4data["charts"]
            # st_info = ["Test : Regression", "Variables : "+ self.result_column +", "+measure_column,"Intercept : "+str(round(self._df_regression_result.get_intercept(),2)), "Regression Coefficient : "+ str(round(self._df_regression_result.get_coeff(measure_column),2))]
            statistical_info_array=[
                ("Test Type","Regression"),
                ("Coefficient",str(round(self._df_regression_result.get_coeff(measure_column),2))),
                ("P-Value","<= 0.05"),
                ("Intercept",str(round(self._df_regression_result.get_intercept(),2))),
                ("R Square ",str(round(self._df_regression_result.get_rsquare(),2))),
                ]
            inferenceTuple = ()
            coeff = self._df_regression_result.get_coeff(measure_column)
            if coeff > 0:
                inferenceTuple = ("Inference","For every additional unit of increase in {} there will be an increase of {} units in {} (target).".format(measure_column,str(round(coeff,2)),self._dataframe_context.get_result_column()))
            else:
                inferenceTuple = ("Inference","For every additional unit of decrease in {} there will be an decrease of {} units in {} (target).".format(measure_column,str(round(coeff,2)),self._dataframe_context.get_result_column()))
            if len(inferenceTuple) > 0:
                statistical_info_array.append(inferenceTuple)
            statistical_info_array = NarrativesUtils.statistical_info_array_formatter(statistical_info_array)

            card4paragraphs.insert(2,C3ChartData(data=card4Chart,info=statistical_info_array))
            measureCard1Data += card4paragraphs

            self.narratives['cards'].append(measure_column_cards)

            if count == 0:
                card4data.pop("charts")
                self._result_setter.update_executive_summary_data(card4data)
            count += 1
            measureCard1.set_card_data(measureCard1Data)
            if self._run_dimension_level_regression:
                measureCard2.set_card_data(measureCard2Data)
                sigMeasureNode.add_cards([measureCard1,measureCard2])
            sigMeasureNode.add_cards([measureCard1])
            self._regressionNode.add_a_node(sigMeasureNode)
        # self._result_setter.set_trend_section_completion_status(True)
        self._story_narrative.add_a_node(self._regressionNode)


    def run_regression_for_dimension_levels(self):
        print "Running regression for Dimension Levels"
        significant_dimensions = self._dataframe_helper.get_significant_dimension()
        print "significant_dimensions:",significant_dimensions
        if significant_dimensions != {}:
            sig_dims = [(x,significant_dimensions[x]) for x in significant_dimensions.keys()]
            sig_dims = sorted(sig_dims,key=lambda x:x[1],reverse=True)
            cat_columns = [x[0] for x in sig_dims[:5]]
        else:
            cat_columns = self._dimension_columns[:5]
        cat_columns= [x for x in cat_columns if x != "Agent Name"]
        print "Running regression for below 5 dimensions"
        print cat_columns
        regression_result_dimension_cols = dict(zip(cat_columns,[{}]*len(cat_columns)))
        for col in cat_columns:
            print "For Column:",col
            # column_levels = self._dataframe_helper.get_all_levels(col)
            column_levels = self._metaParser.get_unique_level_dict(col).keys()
            level_regression_result = dict(zip(column_levels,[{}]*len(column_levels)))
            print "No of levels in this column",len(column_levels)
            for level in column_levels:
                print "Filtering data for level:",level
                filtered_df = self._dataframe_helper.filter_dataframe(col,level)
                result = LinearRegression(filtered_df, self._dataframe_helper, self._dataframe_context,self._metaParser,self._spark).fit(self._dataframe_context.get_result_column())
                if result == None:
                    result = {"intercept" : 0.0,
                              "rmse" : 0.0,
                              "rsquare" : 0.0,
                              "coeff" : 0.0
                              }
                else:
                    result = {"intercept" : result.get_intercept(),
                              "rmse" : result.get_root_mean_square_error(),
                              "rsquare" : result.get_rsquare(),
                              "coeff" : result.get_all_coeff()
                              }
                level_regression_result[level] = result
            regression_result_dimension_cols[col] = level_regression_result
        # print json.dumps(regression_result_dimension_cols,indent=2)
        return regression_result_dimension_cols


__all__ = [
    'LinearRegressionNarrative',
    'RegressionNarrative'
]
