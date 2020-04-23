
from bi.common.decorators import accepts

class Histogram:

    BIN_NUMBER = 'bin_number'
    BIN_START_VALUE = 'start_value'
    BIN_END_VALUE = 'end_value'
    BIN_NUM_OF_RECORDS = 'num_records'

    @accepts(object, (str, basestring), (int, long))
    def __init__(self, column_name, num_records):
        self.column_name = column_name
        self.num_records = num_records
        self.bins = []
        self._un_ordered_bins = []

    @accepts(object, int, (int, long, float), (int, long, float), (int, long, float))
    def add_bin(self, bin_number, start_value, end_value, num_records):
        bin_data = {
            Histogram.BIN_NUMBER: str(bin_number),
            Histogram.BIN_START_VALUE: start_value,
            Histogram.BIN_END_VALUE: end_value,
            Histogram.BIN_NUM_OF_RECORDS: num_records
        }
        if bin_data in self._un_ordered_bins:
            return

        self._un_ordered_bins.append(bin_data)
        self.bins = sorted(self._un_ordered_bins, key=lambda x: int(x.get(Histogram.BIN_NUMBER)))

    def get_bins(self):
        return self.bins

    def get_column_name(self):
        return self.column_name

class DataFrameHistogram:

    def __init__(self):
        self.histograms = {}

    @accepts(object, (Histogram, None))
    def add_histogram(self, histogram):
        column_name = histogram.get_column_name()
        self.histograms[column_name] = histogram
