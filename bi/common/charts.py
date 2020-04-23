class ScatterChartData:
    """
    Data Wrapper for Scatter Plots

    Example Data:
    #### data structure for scatter chart
    ```json
    {
      "data":{
          "a1": [
                 {
                    "k1": "value",
                    "k2": "value"
                 },
                 {
                    "k1": "value",
                    "k2": "value"
                 }
                ],
          "b1": [
                 {
                    "k1": "value",
                    "k2": "value"
                 },
                 {
                    "k1": "value",
                    "k2": "value"
                 }
                ]
          },
      "axes":{"x":"k1","y":"k2"},
      "label_text":{"x":"x label name","y":"y label name"},
      "legend":{"a1":"Actual","b1":"predicted"},
      "chart_type":"scatter"
    }
    ```
    ###### used for time series prediction
    ```json
    {
      "data":{
          "a1": [
                 {
                    "k1": "value",
                    "k2": "value"
                 },
                 {
                    "k1": "value",
                    "k2": "value"
                 }
                ],
          "b1": [
                 {
                    "k1": "value",
                    "k2": "value"
                 },
                 {
                    "k1": "value",
                    "k2": "value"
                 }
                ]
          },
      "axes":{"x":"k1","y":"k2"},
      "label_text":{"x":"x label name","y":"y label name"},
      "legend":{"a1":"Actual","b1":"predicted"},
      "chart_type":"scatter_line"
    }
    ```
    """
    def __init__(self, data=None):
        if data is None:
            data = {}
        self.data = data

    def set_data(self,data):
        self.data = data

    def get_data(self):
        return self.data

    def get_outer_keys(self):
        return self.data.keys()

    def get_inner_keys(self):
        keys = self.data.keys()
        return self.data[keys[0]][0].keys()

class NormalChartData:
    """
    Data Wrapper Class for Charts other than scatter charts
    #### data structure for line chart
    ```json
    {
      "data":[
                 {
                    "k1": 3,
                    "k2": 5,
                    "k3": 18
                 },

                {
                   "k1": 3,
                   "k2": 5,
                   "k3": 18
                },
                ],
      "axes":{"x":"k1","y":"k2","y2":"k3"},
      "label_text":{"x":"x label name","y":"y label name","y2":"y2 label name"},
      "legend":{"k1":"Month","k2":"Sales","k3":"Cost"},
      "chart_type":"line"
    }
    ```
    #### data structure for bar chart
    ```json
    {
      "data":[
                 {
                    "k1": 3,
                    "k2": 5,
                    "k3": 18
                 },

                {
                   "k1": 3,
                   "k2": 5,
                   "k3": 18
                },
                ],
      "axes":{"x":"k1","y":"k2","y2":"k3"},
      "label_text":{"x":"x label name","y":"y label name","y2":"y2 label name"},
      "legend":{"k1":"Month","k2":"Sales","k3":"Cost"},
      "chart_type":"bar"
    }
    ```

    #### data structure for combination chart
    ```json
    {
      "data":[
                 {
                    "k1": 3,
                    "k2": 5,
                    "k3": 18
                 },

                {
                   "k1": 3,
                   "k2": 5,
                   "k3": 18
                },
                ],
      "axes":{"x":"k1","y":"k2","y2":"k3"},
      "label_text":{"x":"x label name","y":"y label name","y2":"y2 label name"},
      "legend":{"k1":"Month","k2":"Sales","k3":"Cost"},
      "types":{"k1":"line","k2":"bar","k3":"bar"},
      "chart_type":"combination"
    }
    ```

    """
    def __init__(self, data=None):
        if data is None:
            data = []
        self.data = data

    def set_data(self,data):
        self.data = data

    def get_data(self):
        return self.data

    def get_keys(self):
        if len(self.data) != 0:
            return self.data[0].keys()
        else:
            return []

class ChartJson:
    """
    formats = ['.2s','$','$,'.2f']
    """
    def __init__(self, data = None, axes=None, label_text=None, legend=None, chart_type = None, types = None):
        if axes is None:
            axes = {}
        if label_text is None:
            label_text = {}
        if legend is None:
            legend = {}
        self.data = data
        self.axes = axes
        self.label_text = label_text
        self.legend = legend
        self.chart_type = chart_type
        self.types = types
        self.axisRotation = False
        self.yAxisNumberFormat = '.2s'
        self.y2AxisNumberFormat = ''
        self.subchart = True
        self.show_legend = True
        self.hide_xtick = False
        self.title = None


    def get_dict_object(self):
        out = {
            "data":self.data,
            "axes":self.axes,
            "label_text":self.label_text,
            "legend":self.legend,
            "chart_type":self.chart_type,
            "types":self.types,
            "axisRotation":self.axisRotation,
            "yAxisNumberFormat":self.yAxisNumberFormat,
            "y2AxisNumberFormat":self.y2AxisNumberFormat,
            "subchart":self.subchart,
            "show_legend":self.show_legend,
            "hide_xtick":self.hide_xtick,
            "title":self.title,
        }
        return out
    def set_data(self,data):
        """
            data can be of array type or dictionary
        """
        self.data = data

    def set_axis_rotation(self,data):
        self.axisRotation = data

    def set_axes(self,data):
        self.axes = data

    def set_label_text(self,data):
        self.label_text = data

    def set_legend(self,data):
        self.legend = data

    def set_chart_type(self,data):
        self.chart_type = data

    def set_types(self,data):
        """ this is only used in combination charts"""
        self.types = data

    def set_yaxis_number_format(self,data):
        self.yAxisNumberFormat = data

    def set_y2axis_number_format(self,data):
        self.y2AxisNumberFormat = data

    def set_subchart(self,data):
        self.subchart = data

    def set_show_legend(self,data):
        self.show_legend = data

    def set_hide_xtick(self,data):
        self.hide_xtick = data

    def set_title(self,data):
        self.title=data
