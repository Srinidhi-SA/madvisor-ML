import humanize

from bi.common import NormalCard, NarrativesTree, C3ChartData, TableData
from bi.common import NormalChartData, ChartJson
from bi.common import utils as CommonUtils
from bi.narratives import utils as NarrativesUtils
from bi.settings import setting as GLOBALSETTINGS


class DecisionTreeRegNarrative:
    MAX_FRACTION_DIGITS = 2

    def _get_new_table(self):
        self.card1Table = [["PREDICTION","RULES","PERCENTAGE"]]
        for keys in self._table.keys():
            self.new_table[keys]={}
            self.new_table[keys]['rules'] = self._table[keys]
            self.new_table[keys]['probability'] = [round(i,2) for i in self.success_percent[keys]]
            keyTable = [keys,self.new_table[keys]['rules'],self.new_table[keys]['probability']]
            self.card1Table.append(keyTable)

    # @accepts(object, (str, basestring), DecisionTreeResult,DataFrameHelper,ResultSetter)
    def __init__(self, column_name, decision_tree_rules,df_helper,df_context,result_setter,story_narrative,scriptWeight=None, analysisName=None):
        self._story_narrative = story_narrative
        self._result_setter = result_setter
        self._dataframe_context = df_context
        self._column_name = column_name.lower()
        self._colname = column_name
        self._capitalized_column_name = "%s%s" % (column_name[0].upper(), column_name[1:])
        self._decision_rules_dict = decision_tree_rules.get_decision_rules()
        self._table = decision_tree_rules.get_table()
        self.new_table={}
        self.successful_predictions=decision_tree_rules.get_success()
        self.total_predictions=decision_tree_rules.get_total()
        self.success_percent= decision_tree_rules.get_success_percent()
        self._important_vars = decision_tree_rules.get_significant_vars()
        self._target_distribution = decision_tree_rules.get_target_contributions()
        self._get_new_table()
        self._df_helper = df_helper
        self.subheader = None
        self.dropdownComment = None
        self.dropdownValues = None
        self._blockSplitter = GLOBALSETTINGS.BLOCKSPLITTER
        self._base_dir = "/decisiontree/"
        self._decisionTreeNode = NarrativesTree(name='Prediction')
        # self._decisionTreeNode.set_name("Decision Tree Regression")

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
            "dtreeNarrativeStart":{
                "summary":"Started the Decision Tree Regression Narratives",
                "weight":0
                },
            "dtreeNarrativeEnd":{
                "summary":"Narratives for Decision Tree Regression Finished",
                "weight":10
                },
            }
        # self._completionStatus += self._scriptWeightDict[self._analysisName]["narratives"]*self._scriptStages["dtreeNarrativeStart"]["weight"]/10
        # progressMessage = CommonUtils.create_progress_message_object(self._analysisName,\
        #                             "dtreeNarrativeStart",\
        #                             "info",\
        #                             self._scriptStages["dtreeNarrativeStart"]["summary"],\
        #                             self._completionStatus,\
        #                             self._completionStatus)
        # CommonUtils.save_progress_message(self._messageURL,progressMessage)
        # self._dataframe_context.update_completion_status(self._completionStatus)
        CommonUtils.create_update_and_save_progress_message(self._dataframe_context,self._scriptWeightDict,self._scriptStages,self._analysisName,"dtreeNarrativeStart","info",weightKey="narratives")



        self._generate_narratives()
        self._story_narrative.add_a_node(self._decisionTreeNode)
        self._result_setter.set_decision_tree_node(self._decisionTreeNode)

        # self._completionStatus = self._dataframe_context.get_completion_status()
        # self._completionStatus += self._scriptWeightDict[self._analysisName]["narratives"]*self._scriptStages["dtreeNarrativeEnd"]["weight"]/10
        # progressMessage = CommonUtils.create_progress_message_object(self._analysisName,\
        #                             "dtreeNarrativeEnd",\
        #                             "info",\
        #                             self._scriptStages["dtreeNarrativeEnd"]["summary"],\
        #                             self._completionStatus,\
        #                             self._completionStatus)
        # CommonUtils.save_progress_message(self._messageURL,progressMessage)
        # self._dataframe_context.update_completion_status(self._completionStatus)
        CommonUtils.create_update_and_save_progress_message(self._dataframe_context,self._scriptWeightDict,self._scriptStages,self._analysisName,"dtreeNarrativeEnd","info",weightKey="narratives")




    def _generate_narratives(self):
        # self._decisionTreeCard1 = NormalCard(name = 'Predicting key drivers of '+self._capitalized_column_name)
        # self._decisionTreeCard2 = NormalCard(name = 'Decision Rules of '+self._capitalized_column_name)
        self._generate_summary()
        # self._decisionTreeNode.add_cards([self._decisionTreeCard1,self._decisionTreeCard2])

    # def _generate_summary(self):
    #     rules = self._decision_rules_dict
    #     colname = self._colname
    #     data_dict = {"dimension_name":self._colname}
    #     data_dict["plural_colname"] = NarrativesUtils.pluralize(data_dict["dimension_name"])
    #     data_dict["significant_vars"] = []
    #     if "High" in self._important_vars:
    #         data_dict['significant_vars_high'] = self._important_vars['High']
    #     if "Low" in self._important_vars:
    #         data_dict['significant_vars_low'] = self._important_vars['Low']
    #     rules_dict = self._table
    #     self.condensedTable={}
    #     for target in rules_dict.keys():
    #         self.condensedTable[target]=[]
    #         total = self.total_predictions[target]
    #         success = self.successful_predictions[target]
    #         success_percent = self.success_percent[target]
    #         for idx,rule in enumerate(rules_dict[target]):
    #             rules1 = NarrativeUtils.generate_rules(target,rule, total[idx], success[idx], success_percent[idx])
    #             self.condensedTable[target].append(rules1)
    #     self.dropdownValues = rules_dict.keys()
    #     lines2 = []
    #     lines2 += NarrativesUtils.block_splitter('Most Significant Rules for Price :',self._blockSplitter)
    #     lines2 += [TreeData(data=self.condensedTable,datatype='dropdown')]
    #     self._decisionTreeCard2.add_card_data(lines2)
    #     if "High" in self.condensedTable:
    #         data_dict['rules_list_high'] = self.condensedTable['High']
    #     if "Low" in self.condensedTable:
    #         data_dict['rules_list_low'] = self.condensedTable['Low']
    #     print self._target_distribution.keys()
    #     if "High" in self._target_distribution:
    #         data_dict['count_percent_high'] = NarrativesUtils.round_number(self._target_distribution['High']['count_percent'],2)
    #         data_dict['sum_percent_high'] =  NarrativesUtils.round_number(self._target_distribution['High']['sum_percent'],2)
    #         data_dict['sum_high'] =  NarrativesUtils.round_number(self._target_distribution['High']['sum'],2)
    #         data_dict['average_high_group'] = self._target_distribution['High']['sum']*1.0/self._target_distribution['High']['count']
    #     if "Low" in self._target_distribution:
    #         data_dict['count_percent_low'] =  NarrativesUtils.round_number(self._target_distribution['Low']['count_percent'],2)
    #         data_dict['sum_percent_low'] =  NarrativesUtils.round_number(self._target_distribution['Low']['sum_percent'],2)
    #     data_dict['average_overall'] = sum([self._target_distribution[i]['sum'] for i in self._target_distribution])*1.0/sum([self._target_distribution[i]['count'] for i in self._target_distribution])
    #     data_dict['high_vs_overall'] = data_dict['average_high_group']*100.0/data_dict['average_high_group'] - 100
    #     self.card2_data = NarrativesUtils.paragraph_splitter(NarrativesUtils.get_template_output(self._base_dir,\
    #                                                 'decision_reg_card2.html',data_dict))
    #     self.card2_chart = {'sum' : dict([(k,v['sum']) for k,v in self._target_distribution.items()]),
    #                         'mean': dict([(k,v['sum']*1.0/v['count']) for k,v in self._target_distribution.items()]),
    #                         'legends': {'sum': self._capitalized_column_name+' Total',
    #                                     'mean': self._capitalized_column_name+' Avg'}}
    #     self.subheader = NarrativesUtils.get_template_output(self._base_dir,\
    #                                     'decision_tree_summary.html',data_dict)
    #     lines = []
    #     lines += NarrativesUtils.block_splitter(self.subheader,self._blockSplitter)
    #     tableData = TableData(data={"tableType" : "decisionTreeTable",'tableData':self.card1Table})
    #     lines += [TreeData(data=self._decision_rules_dict),tableData]
    #     self._decisionTreeCard1.add_card_data(lines)
    #     # executive_summary_data = {"rules_list_high":data_dict['rules_list_high'],
    #     #                           "average_high_group" : data_dict["average_high_group"],
    #     #                           "average_overall" : data_dict["average_overall"],
    #     #                           "high_vs_overall" : data_dict["high_vs_overall"]
    #     #                          }
    #     # self._result_setter.update_executive_summary_data(executive_summary_data)

    def _generate_summary(self):
        data_dict = {}
        rules_dict = self._table
        data_dict["blockSplitter"] = self._blockSplitter
        data_dict["targetcol"] = self._colname
        groups = rules_dict.keys()
        probabilityCutoff = 75
        probabilityGroups=[{"probability":probabilityCutoff,"count":0,"range":[probabilityCutoff,100]},{"probability":probabilityCutoff-1,"count":0,"range":[0,probabilityCutoff-1]}]
        tableArray = [[
                "Prediction Rule",
                "Probability",
                "Prediction",
                "Freq",
                "group",
                "richRules"
              ]]
        dropdownData = []
        chartDict = {}
        self._completionStatus = self._dataframe_context.get_completion_status()
        progressMessage = CommonUtils.create_progress_message_object(self._analysisName,"custom","info","Generating Prediction rules",self._completionStatus,self._completionStatus,display=True)
        CommonUtils.save_progress_message(self._messageURL,progressMessage,ignore=False)

        for idx,target in enumerate(rules_dict.keys()):
            targetToDisplayInTable = target.split(":")[0].strip()
            if idx == 0:
                dropdownData.append({"displayName":target,"name":targetToDisplayInTable,"searchTerm":targetToDisplayInTable,"selected":True,"id":idx+1})
            else:
                dropdownData.append({"displayName":target,"name":targetToDisplayInTable,"searchTerm":targetToDisplayInTable,"selected":False,"id":idx+1})
            rulesArray = rules_dict[target]
            probabilityArray = [round(x,2) for x in self.success_percent[target]]
            groupArray = ["strong" if x>=probabilityCutoff else "mixed" for x in probabilityArray]
            for idx2,obj in enumerate(probabilityGroups):
                grpCount = len([x for x in probabilityArray if x >= obj["range"][0] and x <= obj["range"][1]])
                obj["count"] += grpCount
                probabilityGroups[idx2] = obj
            predictionArray = [targetToDisplayInTable]*len(rulesArray)
            freqArray = self.total_predictions[target]
            chartDict[target] = sum(freqArray)
            success = self.successful_predictions[target]
            success_percent = self.success_percent[target]
            richRulesArray = []
            crudeRuleArray = []
            analysisType = self._dataframe_context.get_analysis_type()
            targetCol = self._dataframe_context.get_result_column()
            binFlag = False
            if self._dataframe_context.get_custom_analysis_details() != None:
                binnedColObj = [x["colName"] for x in self._dataframe_context.get_custom_analysis_details()]
                if binnedColObj != None and targetCol in binnedColObj:
                    binFlag = True
            for idx2,crudeRule in enumerate(rulesArray):
                richRule,crudeRule = NarrativesUtils.generate_rules(self._colname,target,crudeRule, freqArray[idx2], success[idx2], success_percent[idx2],analysisType,binFlag=binFlag)
                richRulesArray.append(richRule)
                crudeRuleArray.append(crudeRule)
            probabilityArray = map(lambda x:humanize.apnumber(x)+"%" if x >=10 else str(int(x))+"%" ,probabilityArray)
            # targetArray = zip(rulesArray,probabilityArray,predictionArray,freqArray,groupArray)
            targetArray = zip(crudeRuleArray,probabilityArray,predictionArray,freqArray,groupArray,richRulesArray)
            targetArray = [list(x) for x in targetArray]
            tableArray += targetArray

        donutChartMaxLevel = 10
        if len(chartDict) > donutChartMaxLevel:
            chartDict = NarrativesUtils.restructure_donut_chart_data(chartDict,nLevels=donutChartMaxLevel)
        chartData = NormalChartData([chartDict]).get_data()
        chartJson = ChartJson(data=chartData)
        chartJson.set_title(self._colname)
        chartJson.set_chart_type("donut")
        mainCardChart = C3ChartData(data=chartJson)
        mainCardChart.set_width_percent(45)
        # mainCardChart = {"dataType": "c3Chart","widthPercent":33 ,"data": {"data": [chartDict],"title":self._colname,"axes":{},"label_text":{},"legend":{},"yAxisNumberFormat": ".2s","types":None,"axisRotation":False, "chart_type": "donut"}}


        dropdownDict = {
          "dataType": "dropdown",
          "label": "Showing prediction rules for",
          "data": dropdownData
        }

        data_dict["probabilityGroups"] = probabilityGroups

        maincardSummary = NarrativesUtils.get_template_output(self._base_dir,\
                                                    'decisiontreesummary.html',data_dict)
        main_card = NormalCard()
        main_card_data = []
        main_card_narrative = NarrativesUtils.block_splitter(maincardSummary,self._blockSplitter)
        main_card_data += main_card_narrative

        main_card_data.append(mainCardChart)
        main_card_data.append(dropdownDict)

        main_card_table = TableData()
        main_card_table.set_table_data(tableArray)
        main_card_table.set_table_type("popupDecisionTreeTable")
        main_card_data.append(main_card_table)
        main_card.set_card_data(main_card_data)
        main_card.set_card_name("Predicting Key Drivers of {}".format(self._colname))
        self._decisionTreeNode.add_a_card(main_card)
