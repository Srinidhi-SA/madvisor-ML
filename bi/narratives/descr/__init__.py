from bi.common.utils import accepts

from measure import MeasureColumnNarrative
# from bi.common import DataframeContext


class DescriptiveStatsNarrative:
    def __init__(self):
        self.measures = {}
        self.dimensions = {}
        self.time_dimensions = {}

    @accepts(object, (str, basestring), MeasureColumnNarrative)
    def add_measure_narrtaive(self, column_name, measure_column_narrative):
        self.measures[column_name] = measure_column_narrative

    @staticmethod
    # @accepts(DataFrameDescriptiveStats, DataframeContext)
    def generate_narratives(data_frame_descr_stats, context):
        descr_stats_narrative = DescriptiveStatsNarrative()
        num_columns = data_frame_descr_stats.get_num_columns()
        # generate narratives for measure columns
        for measure_column in data_frame_descr_stats.get_measure_columns():
            measure_col_narrative = MeasureColumnNarrative(measure_column,
                data_frame_descr_stats.get_measure_column_stats(measure_column), num_columns, context)
            descr_stats_narrative.add_measure_narrtaive(measure_column, measure_col_narrative)
        # generate narratives for dimension columns
        # generate narratives for timediemsnion columns
        return descr_stats_narrative
