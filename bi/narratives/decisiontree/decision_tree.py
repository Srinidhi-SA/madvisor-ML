import json
import json

import humanize

from bi.common import NormalCard, NarrativesTree, C3ChartData, TableData
from bi.common import NormalChartData, ChartJson
from bi.common import utils as CommonUtils
from bi.narratives import utils as NarrativesUtils
from bi.settings import setting as GLOBALSETTINGS


class DecisionTreeNarrative:
    MAX_FRACTION_DIGITS = 2

    def _get_new_table(self):
        self._decisionTreeCard1Table = [["PREDICTION","RULES","PERCENTAGE"]]
        for keys in self._table.keys():
            self._new_table[keys]={}
            self._new_table[keys]['rules'] = self._table[keys]
            self._new_table[keys]['probability'] = [round(i,2) for i in self.success_percent[keys]]
            keyTable = [keys,self._new_table[keys]['rules'],self._new_table[keys]['probability']]
            self._decisionTreeCard1Table.append(keyTable)

    # @accepts(object, (str, basestring), DecisionTreeResult,DataFrameHelper,ContextSetter,ResultSetter,NarrativesTree,basestring,dict)
    def __init__(self, column_name, decision_tree_rules,df_helper,df_context,meta_parser,result_setter,story_narrative=None,analysisName=None,scriptWeight=None):
        self._story_narrative = story_narrative
        self._metaParser = meta_parser
        self._dataframe_context = df_context
        self._ignoreMsg = self._dataframe_context.get_message_ignore()
        self._result_setter = result_setter
        self._blockSplitter = GLOBALSETTINGS.BLOCKSPLITTER
        self._column_name = column_name.lower()
        self._colname = column_name

        self._capitalized_column_name = "%s%s" % (column_name[0].upper(), column_name[1:])
        self._decision_rules_dict = decision_tree_rules.get_decision_rules()
        self._decision_tree_json = CommonUtils.as_dict(decision_tree_rules)
        self._decision_tree_raw = self._decision_rules_dict
        # self._decision_tree_raw = {"tree":{"children":None}}
        # self._decision_tree_raw['tree']["children"] = self._decision_tree_json['tree']["children"]
        self._table = decision_tree_rules.get_table()
        self._new_table={}
        self.successful_predictions=decision_tree_rules.get_success()
        self.total_predictions=decision_tree_rules.get_total()
        self.success_percent= decision_tree_rules.get_success_percent()
        self._important_vars = decision_tree_rules.get_significant_vars()
        self._target_distribution = decision_tree_rules.get_target_contributions()
        self._get_new_table()
        self._df_helper = df_helper
        self.subheader = None
        #self.table = {}
        self.dropdownComment = None
        self.dropdownValues = None
        self._base_dir = "/decisiontree/"


        self._completionStatus = self._dataframe_context.get_completion_status()
        if analysisName == None:
            self._analysisName = self._dataframe_context.get_analysis_name()
        else:
            self._analysisName = analysisName
        self._messageURL = self._dataframe_context.get_message_url()
        if scriptWeight == None:
            self._scriptWeightDict = self._dataframe_context.get_dimension_analysis_weight()
        else:
            self._scriptWeightDict = scriptWeight
        self._scriptStages = {
            "dtreeNarrativeStart":{
                "summary":"Started the Decision Tree Narratives",
                "weight":0
                },
            "dtreeNarrativeEnd":{
                "summary":"Narratives for Decision Tree Finished",
                "weight":10
                },
            }
        self._completionStatus += self._scriptWeightDict[self._analysisName]["narratives"]*self._scriptStages["dtreeNarrativeStart"]["weight"]/10
        progressMessage = CommonUtils.create_progress_message_object(self._analysisName,\
                                    "dtreeNarrativeStart",\
                                    "info",\
                                    self._scriptStages["dtreeNarrativeStart"]["summary"],\
                                    self._completionStatus,\
                                    self._completionStatus)
        CommonUtils.save_progress_message(self._messageURL,progressMessage,ignore=self._ignoreMsg)
        self._dataframe_context.update_completion_status(self._completionStatus)

        self._decisionTreeNode = NarrativesTree()
        self._decisionTreeNode.set_name("Prediction")
        self._generate_narratives()
        # self._story_narrative.add_a_node(self._decisionTreeNode)
        self._result_setter.set_decision_tree_node(self._decisionTreeNode)
        self._result_setter.set_score_dtree_cards(json.loads(CommonUtils.convert_python_object_to_json(self._decisionTreeNode.get_all_cards())))

        self._completionStatus = self._dataframe_context.get_completion_status()
        self._completionStatus += self._scriptWeightDict[self._analysisName]["narratives"]*self._scriptStages["dtreeNarrativeEnd"]["weight"]/10
        progressMessage = CommonUtils.create_progress_message_object(self._analysisName,\
                                    "dtreeNarrativeEnd",\
                                    "info",\
                                    self._scriptStages["dtreeNarrativeEnd"]["summary"],\
                                    self._completionStatus,\
                                    self._completionStatus)
        CommonUtils.save_progress_message(self._messageURL,progressMessage,ignore=self._ignoreMsg)
        self._dataframe_context.update_completion_status(self._completionStatus)


    def _generate_narratives(self):
        self._generate_summary()

    # def _generate_summary(self):
    #     rules = self._decision_rules_dict
    #     colname = self._colname
    #     data_dict = {"dimension_name":self._colname}
    #     data_dict["plural_colname"] = NarrativesUtils.pluralize(data_dict["dimension_name"])
    #     data_dict["significant_vars"] = []
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
    #     data_dict["blockSplitter"] = self._blockSplitter
    #     data_dict['rules'] = self.condensedTable
    #     data_dict['success'] = self.success_percent
    #     data_dict['significant_vars'] = list(set(itertools.chain.from_iterable(self._important_vars.values())))
    #     data_dict['significant_vars'] = self._important_vars
    #     # print '*'*16
    #     # print data_dict['rules']
    #     # print self._new_table
    #     self.card2_data = NarrativesUtils.paragraph_splitter(NarrativesUtils.get_template_output(self._base_dir,\
    #                                                 'decision_tree_card2.html',data_dict))
    #     self.card2_chart = self._target_distribution
    #
    #     self.dropdownComment = NarrativesUtils.get_template_output(self._base_dir,\
    #                                                 'decision_rule_summary.html',data_dict)
    #     main_card = NormalCard()
    #     main_card_data = []
    #     main_card_narrative = NarrativesUtils.block_splitter(self.dropdownComment,self._blockSplitter)
    #     main_card_data += main_card_narrative
    #     main_card_data.append(TreeData(data=self._decision_tree_raw))
    #     main_card_table = TableData()
    #     main_card_table.set_table_data(self._decisionTreeCard1Table)
    #     main_card_table.set_table_type("decisionTreeTable")
    #     main_card_data.append(main_card_table)
    #     main_card.set_card_data(main_card_data)
    #     main_card.set_card_name("Predicting Key Drivers of {}".format(self._colname))
    #     card2 = NormalCard()
    #     card2Data = NarrativesUtils.block_splitter(NarrativesUtils.get_template_output(self._base_dir,\
    #                                                 'decision_tree_card2.html',data_dict),self._blockSplitter)
    #     card2ChartData = []
    #     for k,v in self._target_distribution.items():
    #         card2ChartData.append({"key":k,"value":v})
    #     card2ChartData = NormalChartData(data=card2ChartData)
    #     card2ChartJson = ChartJson()
    #     card2ChartJson.set_data(card2ChartData.get_data())
    #     card2ChartJson.set_chart_type("bar")
    #     card2ChartJson.set_axes({"x":"key","y":"value"})
    #     card2Data.insert(1,C3ChartData(data=card2ChartJson))
    #     card2.set_card_data(card2Data)
    #     card2.set_card_name("Decision Rules for {}".format(self._colname))
    #     self._decisionTreeNode.add_a_card(main_card)
    #     self._decisionTreeNode.add_a_card(card2)
    #     self.subheader = NarrativesUtils.get_template_output(self._base_dir,\
    #                                     'decision_tree_summary.html',data_dict)

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
        targetLevel = self._dataframe_context.get_target_level_for_model()
        probabilityArrayAll = []

        self._completionStatus = self._dataframe_context.get_completion_status()
        progressMessage = CommonUtils.create_progress_message_object(self._analysisName,"custom","info","Generating Prediction rules",self._completionStatus,self._completionStatus,display=True)
        CommonUtils.save_progress_message(self._messageURL,progressMessage,ignore=False)
        self._dataframe_context.update_completion_status(self._completionStatus)
        targetValues = [x for x in rules_dict.keys() if x==targetLevel]+[x for x in rules_dict.keys() if x!=targetLevel]
        for idx,target in enumerate(targetValues):
            if idx == 0:
                if self._dataframe_context.get_story_on_scored_data() != True:
                    dropdownData.append({"displayName":target,"name":target,"selected":True,"id":idx+1})
                else:
                    dropdownData.append({"displayName":"{} : {}".format(self._colname,target),"name":target,"selected":True,"id":idx+1})
            else:
                if self._dataframe_context.get_story_on_scored_data() != True:
                    dropdownData.append({"displayName":target,"name":target,"selected":False,"id":idx+1})
                else:
                    dropdownData.append({"displayName":"{} : {}".format(self._colname,target),"name":target,"selected":False,"id":idx+1})
            rulesArray = rules_dict[target]
            probabilityArray = [round(x,2) for x in self.success_percent[target]]
            probabilityArrayAll += probabilityArray
            groupArray = ["strong" if x>=probabilityCutoff else "mixed" for x in probabilityArray]
            for idx2,obj in enumerate(probabilityGroups):
                grpCount = len([x for x in probabilityArray if x >= obj["range"][0] and x <= obj["range"][1]])
                obj["count"] += grpCount
                probabilityGroups[idx2] = obj
            predictionArray = [target]*len(rulesArray)
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
            # targetArray = zip(richRulesArray,probabilityArray,predictionArray,freqArray,groupArray)
            targetArray = zip(crudeRuleArray,probabilityArray,predictionArray,freqArray,groupArray,richRulesArray)
            targetArray = [list(x) for x in targetArray]
            tableArray += targetArray

        donutChartMaxLevel = 10
        if self._dataframe_context.get_story_on_scored_data() == True:
            chartDict = {}
            probabilityRangeForChart = GLOBALSETTINGS.PROBABILITY_RANGE_FOR_DONUT_CHART
            chartDict = dict(zip(probabilityRangeForChart.keys(),[0]*len(probabilityRangeForChart)))
            for val in probabilityArrayAll:
                for grps,grpRange in probabilityRangeForChart.items():
                    if val > grpRange[0] and val <= grpRange[1]:
                        chartDict[grps] = chartDict[grps]+1
            chartDict = {k:v for k,v in chartDict.items() if v != 0}
        else:
            chartDict = dict([(k,sum(v)) for k,v in self.total_predictions.items()])
            chartDict = {k:v for k,v in chartDict.items() if v != 0}
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
        if self._dataframe_context.get_story_on_scored_data() != True:
            maincardSummary = NarrativesUtils.get_template_output(self._base_dir,\
                                                        'decisiontreesummary.html',data_dict)
        else:
            predictedLevelcountArray = [(x[2],x[3]) for x in tableArray[1:]]
            predictedLevelCountDict  = {}
            # predictedLevelcountDict = defaultdict(predictedLevelcountArray)
            for val in predictedLevelcountArray:
                predictedLevelCountDict.setdefault(val[0], []).append(val[1])

            levelCountDict = {}
            for k,v in predictedLevelCountDict.items():
                levelCountDict[k] = sum(v)
            # levelCountDict = self._metaParser.get_unique_level_dict(self._colname)
            total = float(sum([x for x in levelCountDict.values() if x != None]))
            levelCountTuple = [{"name":k,"count":v,"percentage":round(v*100/total,2)} for k,v in levelCountDict.items() if v != None]
            percentageArray = [x["percentage"] for x in levelCountTuple]
            percentageArray = NarrativesUtils.ret_smart_round(percentageArray)
            levelCountTuple = [{"name":obj["name"],"count":obj["count"],"percentage":str(percentageArray[idx])+"%"} for idx,obj in enumerate(levelCountTuple)]
            data_dict["nlevel"] = len(levelCountDict)
            print "levelCountTuple",levelCountTuple
            print "levelCountDict",levelCountDict
            if targetLevel in levelCountDict:
                data_dict["topLevel"] = [x for x in levelCountTuple if x["name"]==targetLevel][0]
                if len(levelCountTuple) > 1:
                    data_dict["secondLevel"] = max([x for x in levelCountTuple if x["name"]!=targetLevel],key=lambda x:x["count"])
                else:
                    data_dict["secondLevel"] = None
            else:
                data_dict["topLevel"] = levelCountTuple[0]
                if len(levelCountTuple) > 1:
                    data_dict["secondLevel"] = levelCountTuple[1]
                else:
                    data_dict["secondLevel"] = None
            print data_dict
            maincardSummary = NarrativesUtils.get_template_output(self._base_dir,'decisiontreescore.html',data_dict)
        main_card = NormalCard()
        main_card_data = []
        main_card_narrative = NarrativesUtils.block_splitter(maincardSummary,self._blockSplitter)
        main_card_data += main_card_narrative

        main_card_data.append(mainCardChart)
        main_card_data.append(dropdownDict)

        main_card_table = TableData()
        if self._dataframe_context.get_story_on_scored_data() == True:
            main_card_table.set_table_width(75)
        main_card_table.set_table_data(tableArray)
        main_card_table.set_table_type("popupDecisionTreeTable")
        main_card_data.append(main_card_table)
        uidTable = self._result_setter.get_unique_identifier_table()
        if uidTable != None:
            main_card_data.append(uidTable)
        else:
            main_card_table.set_table_width(100)
        main_card.set_card_data(main_card_data)
        main_card.set_card_name("Predicting Key Drivers of {}".format(self._colname))
        self._decisionTreeNode.add_a_card(main_card)
