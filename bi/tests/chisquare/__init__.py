
import unittest

from bi.common import utils as CommonUtils
from bi.common import NarrativesTree
from bi.narratives.chisquare import ChiSquareNarratives
from bi.narratives.chisquare import ChiSquareAnalysis
from bi.stats.chisquare import ChiSquare
from bi.common import DataLoader,MetaParser, DataFrameHelper,ContextSetter,ResultSetter

import bi.master_helper as MasterHelper
from bi.parser import configparser
from bi.settings import *


# Expected Ouputs

# Chisq_exp_op = {'dimension' : {'pval':0.315275,'effect_size':0.031872,'stats':20.316691,'v_value':0.031872},
# 				'measure' :{'pval':0.0,'effect_size':0.18938170922,'stats':717.30863574,'v_value':0.18938170922}}

# 0.218540231193

exp_values = {'pval' : {'Price_Range-Deal_Type':0.218540231193,'Price_Range-Discount_Range':0.0,'Price_Range-Source':0.315275240154,'Price_Range-Platform':0.22681006213,
						'Price_Range-Buyer_Age':0.200865796163,'Price_Range-Buyer-Gender':0.0330065858455,'Price_Range-Tenure_in_Days':0.10226883755,
						'Price_Range-Sales':0.0,'Price_Range-Marketing_Cost':0.0,'Price_Range-Shipping_Cost':0.0,'Price_Range-Last_Transaction':0.0},
			'effect_size': {'Price_Range-Deal_Type':0.0333986132269,'Price_Range-Discount_Range':0.101640637499,'Price_Range-Source':0.0318721598859,'Price_Range-Platform':0.0208378180847,
							'Price_Range-Buyer_Age':0.0310568881639,'Price_Range-Buyer-Gender':0.0295576603474,'Price_Range-Tenure_in_Days':0.0303854760878,'Price_Range-Sales':0.0991956373975,
							'Price_Range-Marketing_Cost':0.18938170922,'Price_Range-Shipping_Cost':0.121797494416,'Price_Range-Last_Transaction':0.0860596433083},
			'stats' :  {'Price_Range-Deal_Type':22.3093473096,'Price_Range-Discount_Range':206.616383823,'Price_Range-Source':20.3166915159,'Price_Range-Platform':4.34214662532,
						'Price_Range-Buyer_Age':19.2906060485,'Price_Range-Buyer-Gender':8.73655285213,'Price_Range-Tenure_in_Days':18.4655431416,'Price_Range-Sales':196.795489574,
						'Price_Range-Marketing_Cost':717.30863574,'Price_Range-Shipping_Cost':296.692592919,'Price_Range-Last_Transaction':148.125244127},
			'v_value' : {'Price_Range-Deal_Type':0.0333986132269,'Price_Range-Discount_Range':0.101640637499,'Price_Range-Source':0.0318721598859,'Price_Range-Platform':0.0208378180847,
						'Price_Range-Buyer_Age':0.0310568881639,'Price_Range-Buyer-Gender':0.0295576603474,'Price_Range-Tenure_in_Days':0.0303854760878,'Price_Range-Sales':0.0991956373975,
						'Price_Range-Marketing_Cost':0.18938170922,'Price_Range-Shipping_Cost':0.121797494416,'Price_Range-Last_Transaction':0.0860596433083}}


exp_data_dict ={'highlightFlag': '|~HIGHLIGHT~|', 'plural_colname': 'Buyer_Genders', 'best_second_target_count': 406.0,'best_second_share': [1], 'worst_second_target': 'Female',
				'second_target_bottom_dim_contribution': 370.0, 'worst_second_share': [0], 'best_top_difference': [0], 'bottom_levels': ['Female'], 'second_target': u'51 to 100',
				'best_second_difference': [0], 'worst_top_target_percent': 49.23, 'second_target_percentages': [47.68041237113402, 52.31958762886598], 'bottom_level_percent': 49.44,
				'worst_top_target': 'Female', 'best_top_share': [1], 'worst_second_target_percent': 47.68, 'best_top_target_count': 1815.0, 'binAnalyzedCol': False, 'best_second_target': 'Male',
				'top_target_shares': [71.19741100323624, 71.79588607594937], 'worst_second_difference': [1], 'worst_top_difference': [1], 'bottom_level': 'Female', 'top_target_percentages': [49.23076923076923, 50.76923076923077],
				'best_second_target_percent': 52.32, 'top_levels': ['Male'], 'colname': 'Buyer_Gender', 'top_target': u'101 to 500', 'levels_percentages': [49.44, 50.56], 'levels': ['Female', 'Male'], 'binTargetCol': False,
				'top_target_bottom_dim_contribution': 1760.0, 'second_target_top_dims_contribution': 52.31958762886598, 'second_target_bottom_dim': 'Female', 'top_target_top_dims_contribution': 50.76923076923077,
				'top_levels_percent': 50.6, 'best_top_target_percent': 50.77, 'target': 'Price_Range', 'blockSplitter': '|~NEWBLOCK~|', 'best_top_target': 'Male', 'second_target_shares': [14.967637540453074, 16.060126582278482],
				'overall_second': 15.52, 'worst_top_share': [0], 'overall_top': 71.5, 'num_significant': 6, 'top_target_top_dims': ['Male'], 'second_target_top_dims': ['Male'], 'top_target_bottom_dim': 'Female'}



exp_target_dict   = {'11 to 50':{'binTargetCol': False, 'plural_colname': 'Buyer_Genders', 'best_second_target_count': 18.0, 'key_factors': 'Discount_Range', 'second_target_bottom_dim_contribution': 6.0, 'second_target': u'0 to 10',
								'blockSplitter': '|~NEWBLOCK~|', 'distribution_second': [{'index_txt': '', 'd': 'Discount_Range', 'contributions_percent': [3.58], 'variation': 30, 'levels': [], 'contributions': []}], 'worst_second_target_percent': 25.0, 'binAnalyzedCol': False,
								'best_second_target': 'Female', 'worst_second_target': 'Male', 'num_significant': 6, 'colname': 'Buyer_Gender', 'levels': ['Female', 'Male'], 'num_key_factors': 1, 'second_target_top_dims_contribution': 75.0, 'second_target_bottom_dim': 'Male',
								'target': 'Price_Range', 'random_card2': 29, 'highlightFlag': '|~HIGHLIGHT~|', 'random_card4': 96, 'best_second_target_percent': 75.0, 'second_target_top_dims': ['Female']}, u'51 to 100': {'binTargetCol': False, 'plural_colname': 'Buyer_Genders',
								'best_second_target_count': 18.0, 'key_factors': 'Discount_Range', 'second_target_bottom_dim_contribution': 6.0, 'second_target': u'0 to 10', 'blockSplitter': '|~NEWBLOCK~|', 'distribution_second': [{'index_txt': '', 'd': 'Discount_Range', 'contributions_percent': [3.58],
								'variation': 30, 'levels': [], 'contributions': []}], 'worst_second_target_percent': 25.0, 'binAnalyzedCol': False, 'best_second_target': 'Female', 'worst_second_target': 'Male', 'num_significant': 6, 'colname': 'Buyer_Gender', 'levels': ['Female', 'Male'],
								'num_key_factors': 1, 'second_target_top_dims_contribution': 75.0, 'second_target_bottom_dim': 'Male', 'target': 'Price_Range', 'random_card2': 29, 'highlightFlag': '|~HIGHLIGHT~|', 'random_card4': 96, 'best_second_target_percent': 75.0, 'second_target_top_dims': ['Female']},
					'101 to 500': {'binTargetCol': False, 'plural_colname': 'Buyer_Genders', 'best_second_target_count': 18.0, 'key_factors': 'Discount_Range', 'second_target_bottom_dim_contribution': 6.0, 'second_target': u'0 to 10', 'blockSplitter': '|~NEWBLOCK~|',
									'distribution_second': [{'index_txt': '', 'd': 'Discount_Range', 'contributions_percent': [3.58], 'variation': 30, 'levels': [], 'contributions': []}], 'worst_second_target_percent': 25.0, 'binAnalyzedCol': False, 'best_second_target': 'Female', 'worst_second_target': 'Male',
									'num_significant': 6, 'colname': 'Buyer_Gender', 'levels': ['Female', 'Male'], 'num_key_factors': 1, 'second_target_top_dims_contribution': 75.0, 'second_target_bottom_dim': 'Male', 'target': 'Price_Range', 'random_card2': 29, 'highlightFlag': '|~HIGHLIGHT~|', 'random_card4': 96,
									'best_second_target_percent': 75.0, 'second_target_top_dims': ['Female']},
					'0 to 10': {'binTargetCol': False, 'plural_colname': 'Buyer_Genders', 'best_second_target_count': 18.0, 'key_factors': 'Discount_Range', 'second_target_bottom_dim_contribution': 6.0, 'second_target': u'0 to 10',
								'blockSplitter': '|~NEWBLOCK~|', 'distribution_second': [{'index_txt': '', 'd': 'Discount_Range', 'contributions_percent': [3.58], 'variation': 30, 'levels': [], 'contributions': []}], 'worst_second_target_percent': 25.0, 'binAnalyzedCol': False, 'best_second_target': 'Female',
								'worst_second_target': 'Male', 'num_significant': 6, 'colname': 'Buyer_Gender', 'levels': ['Female', 'Male'], 'num_key_factors': 1, 'second_target_top_dims_contribution': 75.0, 'second_target_bottom_dim': 'Male', 'target': 'Price_Range', 'random_card2': 29, 'highlightFlag': '|~HIGHLIGHT~|',
								'random_card4': 96, 'best_second_target_percent': 75.0, 'second_target_top_dims': ['Female']}}


class TestChiSquare(unittest.TestCase):

	# def __init__(self):
	# 	pass

	def setUp(self):
		APP_NAME = "test"
		spark = CommonUtils.get_spark_session(app_name=APP_NAME,hive_environment=False)
		spark.sparkContext.setLogLevel("ERROR")
		# spark.conf.set("spark.sql.execution.arrow.enabled", "true")

		configJson = get_test_configs("testCase",testFor = "chisquare")

		config = configJson["config"]
		jobConfig = configJson["job_config"]
		jobType = jobConfig["job_type"]
		jobName = jobConfig["job_name"]
		jobURL = jobConfig["job_url"]
		messageURL = jobConfig["message_url"]
		try:
			errorURL = jobConfig["error_reporting_url"]
		except:
			errorURL = None
		if "app_id" in jobConfig:
			appid = jobConfig["app_id"]
		else:
			appid = None
		debugMode = True
		LOGGER = {}

		configJsonObj = configparser.ParserConfig(config)
		configJsonObj.set_json_params()
		configJsonObj = configparser.ParserConfig(config)
		configJsonObj.set_json_params()

		dataframe_context = ContextSetter(configJsonObj)
		dataframe_context.set_job_type(jobType)                                     #jobType should be set before set_params call of dataframe_context
		dataframe_context.set_params()
		dataframe_context.set_message_url(messageURL)
		dataframe_context.set_app_id(appid)
		dataframe_context.set_debug_mode(debugMode)
		dataframe_context.set_job_url(jobURL)
		dataframe_context.set_app_name(APP_NAME)
		dataframe_context.set_error_url(errorURL)
		dataframe_context.set_logger(LOGGER)
		dataframe_context.set_xml_url(jobConfig["xml_url"])
		dataframe_context.set_job_name(jobName)
		dataframe_context.set_environment("debugMode")
		dataframe_context.set_message_ignore(True)
		dataframe_context.set_analysis_name("Descriptive analysis")

		df = MasterHelper.load_dataset(spark,dataframe_context)
		metaParserInstance = MasterHelper.get_metadata(df,spark,dataframe_context)
		df,df_helper = MasterHelper.set_dataframe_helper(df,dataframe_context,metaParserInstance)
		targetVal = dataframe_context.get_result_column()

		self.result_setter = ResultSetter(dataframe_context)
		self.story_narrative = NarrativesTree()
		self.story_narrative.set_name("{} Performance Report".format(targetVal))
		self.data_frame = df
		self.df_helper = df_helper
		self.df_context = dataframe_context
		self.meta_parser = metaParserInstance
		self.measure_columns = df_helper.get_numeric_columns()
		self.base_dir = "/chisquare/"
		self.significant_variables = ['Buyer_Gender','Sales','Discount_Range','Shipping_Cost','Last_Transaction','Marketing_Cost']
		self.measure_columns = ['Tenure_in_Days','Sales','Marketing_Cost','Shipping_Cost','Last_Transaction']
		self.df_chisquare_obj = ChiSquare(self.data_frame,self.df_helper,self.df_context,self.meta_parser).test_all(dimension_columns=(self.df_context.get_result_column(),))
		self.df_chisquare_result = self.df_chisquare_obj.get_result()
		self.num_analysed_variables = 11

	def test_chisquare_dimension(self):
		test_dimension = ChiSquare(self.data_frame,self.df_helper,self.df_context,self.meta_parser).test_dimension('Price_Range','Source')
		self.assertAlmostEqual(test_dimension.get_pvalue(),exp_values['pval']['Price_Range-Source'],places=5)
		self.assertAlmostEqual(test_dimension.get_effect_size(),exp_values['effect_size']['Price_Range-Source'],places=5)
		self.assertAlmostEqual(test_dimension.get_stat(),exp_values['stats']['Price_Range-Source'],places=5)
		self.assertAlmostEqual(test_dimension.get_v_value(),exp_values['v_value']['Price_Range-Source'],places=5)

	def test_chisquare_measure(self):
		test_measures = ChiSquare(self.data_frame,self.df_helper,self.df_context,self.meta_parser).test_measures('Price_Range','Marketing_Cost')
		self.assertAlmostEqual(test_measures.get_pvalue(),exp_values['pval']['Price_Range-Marketing_Cost'],places=5)
		self.assertAlmostEqual(test_measures.get_effect_size(), exp_values['effect_size']['Price_Range-Marketing_Cost'],places=5)
		self.assertAlmostEqual(test_measures.get_stat(), exp_values['stats']['Price_Range-Marketing_Cost'],places=5)
		self.assertAlmostEqual(test_measures.get_v_value(), exp_values['v_value']['Price_Range-Marketing_Cost'],places=5)

	def test_chisquare_all(self):

		#PVal-Test
		self.assertAlmostEqual(self.df_chisquare_obj.get_chisquare_result('Price_Range','Deal_Type').get_pvalue(),exp_values['pval']['Price_Range-Deal_Type'])
		self.assertAlmostEqual(self.df_chisquare_obj.get_chisquare_result('Price_Range','Discount_Range').get_pvalue(),exp_values['pval']['Price_Range-Discount_Range'])
		self.assertAlmostEqual(self.df_chisquare_obj.get_chisquare_result('Price_Range','Source').get_pvalue(),exp_values['pval']['Price_Range-Source'])
		self.assertAlmostEqual(self.df_chisquare_obj.get_chisquare_result('Price_Range','Platform').get_pvalue(),exp_values['pval']['Price_Range-Platform'])
		self.assertAlmostEqual(self.df_chisquare_obj.get_chisquare_result('Price_Range','Buyer_Age').get_pvalue(),exp_values['pval']['Price_Range-Buyer_Age'])
		self.assertAlmostEqual(self.df_chisquare_obj.get_chisquare_result('Price_Range','Buyer_Gender').get_pvalue(),exp_values['pval']['Price_Range-Buyer-Gender'])
		self.assertAlmostEqual(self.df_chisquare_obj.get_chisquare_result('Price_Range','Tenure_in_Days').get_pvalue(),exp_values['pval']['Price_Range-Tenure_in_Days'])
		self.assertAlmostEqual(self.df_chisquare_obj.get_chisquare_result('Price_Range','Sales').get_pvalue(),exp_values['pval']['Price_Range-Sales'])
		self.assertAlmostEqual(self.df_chisquare_obj.get_chisquare_result('Price_Range','Marketing_Cost').get_pvalue(),exp_values['pval']['Price_Range-Marketing_Cost'])
		self.assertAlmostEqual(self.df_chisquare_obj.get_chisquare_result('Price_Range','Shipping_Cost').get_pvalue(),exp_values['pval']['Price_Range-Shipping_Cost'])
		self.assertAlmostEqual(self.df_chisquare_obj.get_chisquare_result('Price_Range','Last_Transaction').get_pvalue(),exp_values['pval']['Price_Range-Last_Transaction'])

		#EffectSize_Test
		self.assertAlmostEqual(self.df_chisquare_obj.get_chisquare_result('Price_Range','Deal_Type').get_effect_size(),exp_values['effect_size']['Price_Range-Deal_Type'])
		self.assertAlmostEqual(self.df_chisquare_obj.get_chisquare_result('Price_Range','Discount_Range').get_effect_size(),exp_values['effect_size']['Price_Range-Discount_Range'])
		self.assertAlmostEqual(self.df_chisquare_obj.get_chisquare_result('Price_Range','Source').get_effect_size(),exp_values['effect_size']['Price_Range-Source'])
		self.assertAlmostEqual(self.df_chisquare_obj.get_chisquare_result('Price_Range','Platform').get_effect_size(),exp_values['effect_size']['Price_Range-Platform'])
		self.assertAlmostEqual(self.df_chisquare_obj.get_chisquare_result('Price_Range','Buyer_Age').get_effect_size(),exp_values['effect_size']['Price_Range-Buyer_Age'])
		self.assertAlmostEqual(self.df_chisquare_obj.get_chisquare_result('Price_Range','Buyer_Gender').get_effect_size(),exp_values['effect_size']['Price_Range-Buyer-Gender'])
		self.assertAlmostEqual(self.df_chisquare_obj.get_chisquare_result('Price_Range','Tenure_in_Days').get_effect_size(),exp_values['effect_size']['Price_Range-Tenure_in_Days'])
		self.assertAlmostEqual(self.df_chisquare_obj.get_chisquare_result('Price_Range','Sales').get_effect_size(),exp_values['effect_size']['Price_Range-Sales'])
		self.assertAlmostEqual(self.df_chisquare_obj.get_chisquare_result('Price_Range','Marketing_Cost').get_effect_size(),exp_values['effect_size']['Price_Range-Marketing_Cost'])
		self.assertAlmostEqual(self.df_chisquare_obj.get_chisquare_result('Price_Range','Shipping_Cost').get_effect_size(),exp_values['effect_size']['Price_Range-Shipping_Cost'])
		self.assertAlmostEqual(self.df_chisquare_obj.get_chisquare_result('Price_Range','Last_Transaction').get_effect_size(),exp_values['effect_size']['Price_Range-Last_Transaction'])

		#Stats_Test
		self.assertAlmostEqual(self.df_chisquare_obj.get_chisquare_result('Price_Range','Deal_Type').get_stat(),exp_values['stats']['Price_Range-Deal_Type'])
		self.assertAlmostEqual(self.df_chisquare_obj.get_chisquare_result('Price_Range','Discount_Range').get_stat(),exp_values['stats']['Price_Range-Discount_Range'])
		self.assertAlmostEqual(self.df_chisquare_obj.get_chisquare_result('Price_Range','Source').get_stat(),exp_values['stats']['Price_Range-Source'])
		self.assertAlmostEqual(self.df_chisquare_obj.get_chisquare_result('Price_Range','Platform').get_stat(),exp_values['stats']['Price_Range-Platform'])
		self.assertAlmostEqual(self.df_chisquare_obj.get_chisquare_result('Price_Range','Buyer_Age').get_stat(),exp_values['stats']['Price_Range-Buyer_Age'])
		self.assertAlmostEqual(self.df_chisquare_obj.get_chisquare_result('Price_Range','Buyer_Gender').get_stat(),exp_values['stats']['Price_Range-Buyer-Gender'])
		self.assertAlmostEqual(self.df_chisquare_obj.get_chisquare_result('Price_Range','Tenure_in_Days').get_stat(),exp_values['stats']['Price_Range-Tenure_in_Days'])
		self.assertAlmostEqual(self.df_chisquare_obj.get_chisquare_result('Price_Range','Sales').get_stat(),exp_values['stats']['Price_Range-Sales'])
		self.assertAlmostEqual(self.df_chisquare_obj.get_chisquare_result('Price_Range','Marketing_Cost').get_stat(),exp_values['stats']['Price_Range-Marketing_Cost'])
		self.assertAlmostEqual(self.df_chisquare_obj.get_chisquare_result('Price_Range','Shipping_Cost').get_stat(),exp_values['stats']['Price_Range-Shipping_Cost'])
		self.assertAlmostEqual(self.df_chisquare_obj.get_chisquare_result('Price_Range','Last_Transaction').get_stat(),exp_values['stats']['Price_Range-Last_Transaction'])

		# #VVal-Test
		self.assertAlmostEqual(self.df_chisquare_obj.get_chisquare_result('Price_Range','Deal_Type').get_v_value(),exp_values['v_value']['Price_Range-Deal_Type'])
		self.assertAlmostEqual(self.df_chisquare_obj.get_chisquare_result('Price_Range','Discount_Range').get_v_value(),exp_values['v_value']['Price_Range-Discount_Range'])
		self.assertAlmostEqual(self.df_chisquare_obj.get_chisquare_result('Price_Range','Source').get_v_value(),exp_values['v_value']['Price_Range-Source'])
		self.assertAlmostEqual(self.df_chisquare_obj.get_chisquare_result('Price_Range','Platform').get_v_value(),exp_values['v_value']['Price_Range-Platform'])
		self.assertAlmostEqual(self.df_chisquare_obj.get_chisquare_result('Price_Range','Buyer_Age').get_v_value(),exp_values['v_value']['Price_Range-Buyer_Age'])
		self.assertAlmostEqual(self.df_chisquare_obj.get_chisquare_result('Price_Range','Buyer_Gender').get_v_value(),exp_values['v_value']['Price_Range-Buyer-Gender'])
		self.assertAlmostEqual(self.df_chisquare_obj.get_chisquare_result('Price_Range','Tenure_in_Days').get_v_value(),exp_values['v_value']['Price_Range-Tenure_in_Days'])
		self.assertAlmostEqual(self.df_chisquare_obj.get_chisquare_result('Price_Range','Sales').get_v_value(),exp_values['v_value']['Price_Range-Sales'])
		self.assertAlmostEqual(self.df_chisquare_obj.get_chisquare_result('Price_Range','Marketing_Cost').get_v_value(),exp_values['v_value']['Price_Range-Marketing_Cost'])
		self.assertAlmostEqual(self.df_chisquare_obj.get_chisquare_result('Price_Range','Shipping_Cost').get_v_value(),exp_values['v_value']['Price_Range-Shipping_Cost'])
		self.assertAlmostEqual(self.df_chisquare_obj.get_chisquare_result('Price_Range','Last_Transaction').get_v_value(),exp_values['v_value']['Price_Range-Last_Transaction'])

	def test_chisquare_analysis(self):
		target_chisquare_result = self.df_chisquare_result['Price_Range']
		chisquare_result = self.df_chisquare_obj.get_chisquare_result('Price_Range','Buyer_Gender')
		out = ChiSquareAnalysis(self.df_context,self.df_helper,chisquare_result, 'Price_Range', 'Buyer_Gender', self.significant_variables, self.num_analysed_variables, self.data_frame, self.measure_columns,self.base_dir, None,target_chisquare_result)._generate_narratives()

		self.assertEqual(out['data_dict'],exp_data_dict)
		self.assertEqual(out['target_dict']['11 to 50'],out['target_dict']['11 to 50'])
		self.assertEqual(out['target_dict']['101 to 500'],out['target_dict']['101 to 500'])
		self.assertEqual(out['target_dict']['0 to 10'],out['target_dict']['0 to 10'])

		# print chisquare_narratives




if __name__ == '__main__':
	unittest.main()
