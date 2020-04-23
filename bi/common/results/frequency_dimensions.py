# -*- coding: utf-8 -*-
"""This module contains result object for FreqDimension test"""


class FreqDimensionResult:
    """
    Encapsulates results of Frequency Calculation
    """

    def __init__(self):
        self.frequency_table = {}


    def set_params(self, frequency_table):
        self.frequency_table = frequency_table

    def get_frequency_dict(self):
        return self.frequency_table
