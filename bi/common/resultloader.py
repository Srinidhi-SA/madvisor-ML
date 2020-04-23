from bi.common import utils as CommonUtils
import json

class ResultSetter:
    """
    Provides helper method to store all the different result and narratives.
    """

    def __init__(self, df_context):
        self.executiveSummaryDataDict = {}
        self.trend_subsection_name = None
        self.trend_subsection_data = None
        self.trend_subsection_complete = False
        self.model_summary = {}
        self.distributionNode = None
        self.chisquareNode = None
        self.trendNode = None
        self.decisionTreeNode = None
        self.regressionNode = None
        self.anovaNode = None
        self.headNode = None
        self.randomForestModelSummary = None
        self.xgboostModelSummary = None
        self.logisticRegressionModelSummary = None
        self.svmModelSummary = None
        self.linearRegressionModelSummary = None
        self.generalizedLinearRegressionModelSummary = None
        self.gbtRegressionModelSummary = None
        self.dtreeRegressionModelSummary = None
        self.rfRegressionModelSummary = None
        self.rfcards = []
        self.lrcards = []
        self.svmcards = []
        self.xgbcards = []
        self.linrcards = []
        self.glinrcards = []
        self.gbtrcards = []
        self.rfrcards = []
        self.dtreercards = []
        self.scorefreqcard = []
        self.scorechicards = []
        self.scoredtreecards = []
        self.stockAdvisorNode = None
        self.uidTable = None
        self.pmmlObjects = {}
        self.anovaCardsRegScore = []
        self.kpiCardScore = None
        self.hyperParameterResultDict = {}
        self.parallelCooridnateMetaData = {}
        self.hideTableColumns = []
        self.coeffCardScore = None
        self.anovaNarrativeOnScoredData = {}
        self.anovaChartOnScoredData = {}

    def set_anova_narrative_on_scored_data(self,dataDict):
        self.anovaNarrativeOnScoredData.update(dataDict)

    def set_anova_chart_on_scored_data(self,dataDict):
        self.anovaChartOnScoredData.update(dataDict)

    def get_anova_narratives_scored_data(self):
        return self.anovaNarrativeOnScoredData

    def get_anova_charts_scored_data(self):
        return self.anovaChartOnScoredData

    def set_metadata_parallel_coordinates(self,slug,data):
        self.parallelCooridnateMetaData[slug] = data

    def get_metadata_parallel_coordinates(self,slug):
        return self.parallelCooridnateMetaData[slug]

    def set_hyper_parameter_results(self,slug,data):
        self.hyperParameterResultDict[slug] = data
    def get_hyper_parameter_results(self,slug):
        return self.hyperParameterResultDict[slug]
    def update_pmml_object(self,data):
        self.pmmlObjects.update(data)
    def get_pmml_object(self):
        return self.pmmlObjects
    def get_score_cards(self):
        return self.scoredtreecards
    def set_score_dtree_cards(self,data):
        self.scoredtreecards = data
    def set_score_freq_card(self,data):
        self.scorefreqcard  = data
    def get_score_freq_card(self):
        return self.scorefreqcard
    def set_score_chi_cards(self,data):
        self.scorechicards = data
    def add_a_score_chi_card(self,data):
        self.scorechicards.append(data)
    def get_score_chi_cards(self):
        return self.scorechicards
    def set_lr_cards(self,data):
        self.lrcards = data
    def set_rf_cards(self,data):
        self.rfcards = data
    def set_linr_cards(self,data):
        self.linrcards = data
    def set_glinr_cards(self,data):
        self.glinrcards = data
    def set_gbtr_cards(self,data):
        self.gbtrcards = data
    def set_rfr_cards(self,data):
        self.rfrcards = data
    def set_dtreer_cards(self,data):
        self.dtreercards = data
    def set_xgb_cards(self,data):
        self.xgbcards = data
    def set_svm_cards(self,data):
        self.svmcards = data
    def get_all_classification_cards(self):
        return self.rfcards + self.lrcards + self.xgbcards

    def get_all_regression_cards(self):
        return self.linrcards+self.gbtrcards+self.dtreercards+self.rfrcards+self.glinrcards

    def set_random_forest_model_summary(self,data):
        self.randomForestModelSummary = data
    def set_xgboost_model_summary(self,data):
        self.xgboostModelSummary = data
    def set_logistic_regression_model_summary(self,data):
        self.logisticRegressionModelSummary = data
    def set_svm_model_summary(self,data):
        self.svmModelSummary = data
    def set_linear_regression_model_summary(self,data):
        self.linearRegressionModelSummary = data
    def set_generalized_linear_regression_model_summary(self,data):
        self.generalizedLinearRegressionModelSummary = data
    def set_gbt_regression_model_summart(self,data):
        self.gbtRegressionModelSummary = data
    def set_dtree_regression_model_summart(self,data):
        self.dtreeRegressionModelSummary = data
    def set_rf_regression_model_summart(self,data):
        self.rfRegressionModelSummary = data
    def get_random_forest_model_summary(self):
        return self.randomForestModelSummary
    def get_xgboost_model_summary(self):
        return self.xgboostModelSummary
    def get_logistic_regression_model_summary(self):
        return self.logisticRegressionModelSummary
    def get_svm_model_summary(self):
        return self.svmModelSummary
    def get_linear_regression_model_summary(self):
        return self.linearRegressionModelSummary
    def get_gbt_regression_model_summart(self):
        return self.gbtRegressionModelSummary
    def get_dtree_regression_model_summart(self):
        return self.dtreeRegressionModelSummary
    def get_rf_regression_model_summart(self):
        return self.rfRegressionModelSummary
    def get_generalized_linear_regression_model_summary(self):
        return self.generalizedLinearRegressionModelSummary

    def get_all_regression_model_summary(self):
        allRegressionModelSummary = [self.linearRegressionModelSummary,self.gbtRegressionModelSummary,self.dtreeRegressionModelSummary,self.rfRegressionModelSummary,self.generalizedLinearRegressionModelSummary]
        allRegressionModelSummary = [x for x in allRegressionModelSummary if x != None]
        return allRegressionModelSummary

    def set_head_node(self,node):
        self.headNode = json.loads(CommonUtils.convert_python_object_to_json(node))
    def set_trend_node(self,node):
        self.trendNode = json.loads(CommonUtils.convert_python_object_to_json(node))
    def set_chisquare_node(self,node):
        self.chisquareNode = json.loads(CommonUtils.convert_python_object_to_json(node))
    def set_distribution_node(self,node):
        self.distributionNode = json.loads(CommonUtils.convert_python_object_to_json(node))
    def set_decision_tree_node(self,node):
        self.decisionTreeNode = json.loads(CommonUtils.convert_python_object_to_json(node))
    def set_anova_node(self,node):
        self.anovaNode = json.loads(CommonUtils.convert_python_object_to_json(node))
    def set_regression_node(self,node):
        self.regressionNode = json.loads(CommonUtils.convert_python_object_to_json(node))
    def get_head_node(self):
        return self.headNode
    def get_trend_node(self):
        return self.trendNode
    def get_chisquare_node(self):
        return self.chisquareNode
    def get_distribution_node(self):
        return self.distributionNode
    def get_decision_tree_node(self):
        return self.decisionTreeNode
    def get_anova_node(self):
        return self.anovaNode
    def get_regression_node(self):
        return self.regressionNode

    def update_executive_summary_data(self,data_dict):
        if data_dict != None:
            self.executiveSummaryDataDict.update(data_dict)

    def get_executive_summary_data(self):
        return self.executiveSummaryDataDict

    def set_trend_section_name(self,name):
        self.trend_subsection_name = name

    def set_trend_section_completion_status(self,status):
        self.trend_subsection_complete = status

    def set_model_summary(self,data):
        """data will be a key value dictionary
        {"model_name":"model_summary"}
        """
        self.model_summary.update(data)

    def get_trend_section_name(self):
        return self.trend_subsection_name

    def set_trend_section_data(self,dataDict):
        self.trend_subsection_data = dataDict

    def get_trend_section_data(self):
        return self.trend_subsection_data

    def get_trend_section_completion_status(self):
        return self.trend_subsection_complete

    def get_model_summary(self):
        return self.model_summary

    def set_unique_identifier_table(self,data):
        self.uidTable = data

    def get_unique_identifier_table(self):
        return self.uidTable

    def get_kpi_card_regression_score(self):
        return self.kpiCardScore

    def set_kpi_card_regression_score(self,kpiCardScore):
        self.kpiCardScore = kpiCardScore

    def get_anova_cards_regression_score(self):
        return self.anovaCardsRegScore

    def set_anova_cards_regression_score(self,data):
        self.anovaCardsRegScore.append(data)

    def get_coeff_card_regression_score(self):
        return self.coeffCardScore

    def set_coeff_card_regression_score(self,coeffCardScore):
        self.coeffCardScore = coeffCardScore
