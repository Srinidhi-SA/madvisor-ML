# -*- coding: utf-8 -*-
"""Gathers descriptive stats for all columns in a dataframe"""
from bi.common import utils as CommonUtils
from bi.narratives.executive_summary import ExecutiveSummaryNarrative


class ExecutiveSummaryScript:
    def __init__(self, df_helper, df_context, result_setter, spark):
        self._dataframe_helper = df_helper
        self._dataframe_context = df_context
        self._result_setter = result_setter
        self._spark = spark

    def Run(self):
        print "executive summary script called"
        executive_summary_obj = ExecutiveSummaryNarrative(self._dataframe_helper,self._dataframe_context,self._result_setter,self._spark)
        executive_summary = CommonUtils.as_dict(executive_summary_obj)
        # print 'Narratives: %s' % (json.dumps(executive_summary, indent=2))
        # DataWriter.write_dict_as_json(self._spark, executive_summary, self._dataframe_context.get_narratives_file()+'ExecutiveSummary/')
