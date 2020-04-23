import unittest

from bi.common import utils as CommonUtils
from bi.narratives.chisquare import ChiSquareNarratives
from bi.stats.chisquare import ChiSquare


# Exexted Ouputs

Chi_exp_op = {'dim_pval' : 0.315275240154,
			'meas_p_val' :0.0 }


class TestChiSquare(unittest.TestCase):

	def __init__(self,data_frame,df_helper,df_context,meta_parser):
		self.data_frame = data_frame
		self.df_helper = df_helper
		self.df_context = df_context
		self.meta_parser = meta_parser
		self.test_dimension = ChiSquare(self.data_frame,self.df_helper,self.df_context,self.meta_parser).test_dimension('Price_Range','Source')
	
	def test_upper(self):
		self.assertEqual('foo'.upper(), 'FOO')

	def setup(self):
		pass

	def run_chisquare_test(self):
		# TestCase for test_dimension function
		self.assertEqual(self.test_dimension.get_pvalue(), Chi_exp_op['dim_pval'])

		# # print test_dimension.get_effect_size()
		# # print test_dimension.get_stat()
		# # print test_dimension.get_v_value()

		# # TestCase for test_dimension function
		# test_measures = ChiSquare(self.data_frame,self.df_helper,self.df_context,self.meta_parser).test_measures('Price_Range','Marketing_Cost')

		# print test_measures.get_pvalue()





		# print test_measures.get_effect_size()
		# print test_measures.get_stat()
		# print test_measures.get_v_value()

# if __name__ == '__main__':
#     unittest.main()

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestChiSquare)
    unittest.TextTestRunner(verbosity=2).run(suite)
