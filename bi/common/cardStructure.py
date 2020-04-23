# -*- coding: utf-8 -*-
from bi.common.decorators import accepts
"""
This module contains Card Structure for Narratives
"""

class NarrativesTree:
    """
    Functionalities:

    add single node => add_a_node
    add multiple node => add_nodes
    add single card => add_a_card
    add multiple card => add_cards
    set name => set_name
    get name => get_name
    """

    def __init__(self, name=None, slug=None, listOfNodes=None, listOfCards=None):
        if listOfNodes is None:
            listOfNodes = []
        if listOfCards is None:
            listOfCards = []
        self.name = '' if name==None else str(name)
        self.slug = '' if slug==None else str(slug)
        self.listOfNodes = list(listOfNodes)
        self.listOfCards = list(listOfCards)

    def set_name(self,name):
        self.name = str(name)

    def add_a_node(self,newNode):
        self.listOfNodes.append(newNode)

    def add_nodes(self,nodeList):
        self.listOfNodes += nodeList

    def add_a_card(self,newCard):
        self.listOfCards.append(newCard)

    def add_cards(self,cardList):
        self.listOfCards += cardList

    def insert_card_at_given_index(self,data,idx):
        self.listOfCards.insert(idx,data)

    def get_name(self):
        return self.name

    def get_all_cards(self):
        return self.listOfCards

    def get_all_nodes(self):
        return self.listOfNodes

    def get_card_count(self):
        return len(self.listOfCards)

    def get_node_count(self):
        return len(self.listOfNodes)

    def reorder_nodes(self,ordered_node_list):
        orderedNodeList = []
        nodeList = self.listOfNodes
        print nodeList
        existingName = [node.get_name() for node in nodeList]
        print existingName
        for val in ordered_node_list:
            print val
            try:
                index_value = existingName.index(44)
                print index_value
                print nodeList[index_value]
                orderedNodeList.append(nodeList[index_value])
            except ValueError:
                index_value = -1
        print orderedNodeList
        self.listOfNodes = orderedNodeList
        print self.listOfNodes


class NormalCard:
    """
    Defines the structure for a normal Card
    cardData is always an array of HtmlData or C3ChartData

    ## Normal Card
      - Normal card will have 2 components
        1. html component
    	2. c3Charts

    ```json
    {
    	"cardType": "normal",
    	"name": "Sales Analysis",
    	"slug": "jdsdsdsds",
    	"cardData": [
    		{
    			"dataType": "html",
    			"data": "html content with <b>tags</b>"
    		},
    		{
    			"dataType": "c3Chart",
    			"data":  "chartjson object to be added"
    		},
    		{
    			"dataType": "html",
    			"data": "html content with <b>tags</b>"
    		}
    	]
    }
    ```
    """

    def __init__(self, name=None, slug=None, cardData=None):
        if cardData is None:
            cardData = []
        self.cardType = "normal"
        self.name = name
        self.slug = slug
        self.cardData = list(cardData)
        self.cardWidth = 100
        self.centerAlign = False

    def set_cente_alignment(self,data):
        self.centerAlign = data

    def set_card_data(self,data):
        self.cardData = list(data)

    def add_card_data(self,data):
        self.cardData += list(data)

    def set_card_name(self,name):
        self.name = name

    def set_card_width(self,data):
        self.cardWidth = data

    def insert_card_data(self,idx,data):
        self.cardData.insert(idx,data)

    def get_card_data(self):
        return self.cardData

    def get_card_name(self):
        return self.name

    def get_card_type(self):
        return self.cardType


class SummaryCard:
    """
    Defines the structure for a Summary Card
    cardData is always an array of HtmlData or C3ChartData
    # Sample Object
    ```json
        {
            "cardType": "summary",
        	"name": "Sales Analysis",
        	"slug": "jdsdsdsds",
        	"cardData": {
                    "noOfDimensions": 8,
                    "noOfMeasures": 10,
                    "noOfTimeDimensions": 2,
                    "summaryHtml": "summary with HTML <b>tags</b>",
                    "quotesHtml": "Quote that comes on the right side"
                }
        }
    ```
    """

    def __init__(self, name=None, slug=None, cardData=None):
        if cardData is None:
            cardData = {}
        self.cardType = "summary"
        self.name = name
        self.slug = slug
        self.cardWidth = 100
        self.cardData = {
                            "noOfDimensions":None,
                            "noOfMeasures":None,
                            "summaryHtml":None,
                            "quotesHtml":None,
                            "noOfTimeDimensions":None
                        }

    def set_no_of_dimensions(self,data):
        self.cardData["noOfDimensions"] = data

    def set_no_of_measures(self,data):
        self.cardData["noOfMeasures"] = data

    def set_no_of_time_dimensions(self,data):
        self.cardData["noOfTimeDimensions"] = data

    def set_summary_html(self,data):
        self.cardData["summaryHtml"] = data

    def set_quote_html(self,data):
        self.cardData["quotesHtml"] = data

    def set_card_data(self,data):
        self.cardData = data

    def set_card_name(self,name):
        self.name = name

    def set_card_width(self,data):
        self.cardWidth = data

    def insert_card_data(self,idx,data):
        self.cardData.insert(idx,data)

    def get_card_data(self):
        return self.cardData

    def get_card_name(self):
        return self.name

    def get_card_type(self):
        return self.cardType

class HtmlData:

    def __init__(self,data=None,classTag=None):
        self.dataType = "html"
        self.data = data
        self.classTag = None

    def set_data(self,data):
        self.data = data

    def get_data(self):
        return self.data

    def get_data_type(self):
        return self.dataType

    def set_class_tag(self,data):
        self.classTag = data

    def get_class_tag(self):
        return self.classTag

class TreeData:

    def __init__(self,data=None, datatype = 'tree'):
        self.dataType = datatype
        self.data = data

    def set_data(self,data):
        self.data = data

    def get_data(self):
        return self.data

    def get_data_type(self):
        return self.dataType

class TableData:

    def __init__(self, data=None):
        if data is None:
            data = {}
        self.dataType = "table"
        self.data = data
        self.tableWidth = 100

    def set_data(self,data):
        self.data = data

    def set_table_width(self,data):
        self.tableWidth = data

    def set_table_data(self,data):
        self.data["tableData"] = data

    def set_table_type(self,data):
        self.data["tableType"] = data

    def set_table_top_header(self,data):
        self.data["topHeader"] = data

    def set_table_left_header(self,data):
        self.data["leftHeader"] = data

    def get_data(self):
        return self.data

    def get_data_type(self):
        return self.dataType


class C3ChartData:
    def __init__(self, data=None, info=None):
        if info is None:
            info = []
        self.dataType = "c3Chart"
        self.data = data
        self.widthPercent=100
        self.chartInfo = info
        # self.chartInfo = ["Statistical Test : Avova","Variables : Call Volume","Effect Size : 0.2"]
    def get_dict_object(self):
        out = {
            "dataType":self.dataType,
            "widthPercent":self.widthPercent,
            "chartInfo":self.chartInfo,
        }
        if isinstance(self.data,dict):
            out["data"] = self.data
        else:
            out["data"] = self.data.get_dict_object()
        return out

    def set_data(self,data):
        self.data = data

    def set_width_percent(self,data):
        self.widthPercent = data

    def set_chart_info(self,data):
        self.chartInfo = data

    def get_data(self):
        return self.data

    def get_data_type(self):
        return self.dataType

class ToggleData:
    def __init__(self,data=None):
        self.dataType = "toggle"
        self.data = {"toggleon":None,"toggleoff":None}

    @accepts(object,data=TableData)
    def set_toggleon_data(self,data):
        self.data["toggleon"] = data

    @accepts(object,data=TableData)
    def set_toggleoff_data(self,data):
        self.data["toggleoff"] = data

    def get_data(self):
        return self.data

    def get_data_type(self):
        return self.dataType

class PopupData:
    def __init__(self,data=None):
        self.dataType = "button"
        self.widthPercent = 100
        self.data = None
        self.name = ""

    # @accepts(object,data=TableData)
    def set_data(self,data):
        self.data = data

    def set_name(self,data):
        self.name = data

    def set_width_percent(self,data):
        self.widthPercent = data

    def get_data(self):
        return self.data

    def get_data_type(self):
        return self.dataType

class KpiData:
    def __init__(self,data=None, datatype = 'kpi', widthPercent = 20):
        self.dataType = datatype
        self.data = data
        self.widthPercent = widthPercent

    def set_data(self,data):
        self.data = data

    def get_data(self):
        return self.data

    def get_data_type(self):
        return self.dataType

    def set_width_percent(self,data):
        self.widthPercent = data

class ParallelCoordinateData:

    def __init__(self,data=None,ignoreList=[],hideColumns=[],metricColName=None,columnOrder=[]):
        self.dataType = "parallelCoordinates"
        self.data = data
        self.evaluationMetricColName = metricColName
        self.ignoreList = ignoreList
        self.columnOrder = columnOrder
        self.hideColumns = hideColumns

    def set_data(self,data):
        self.data = data

    def get_data(self):
        return self.data

    def get_data_type(self):
        return self.dataType

    def set_ignore_list(self,data):
        self.ignoreList = data

    def get_ignore_list(self):
        return self.ignoreList

    def set_column_order(self,data):
        self.columnOrder = data

    def get_column_order(self):
        return self.columnOrder

    def set_hide_columns(self,data):
        self.hideColumns = data

    def get_hide_columns(self):
        return self.hideColumns

    def set_metric_colname(self,data):
        self.evaluationMetricColName = data

    def get_metric_colname(self):
        return self.evaluationMetricColName

class DataBox:
    """
                sampleData = [{
                      "name": "Total Articles",
                      "value": "128"
                    },
                    {
                      "name": "Total Source",
                      "value": "26"
                    },
                    {
                      "name": "Average Sentiment Score",
                      "value": "0.31"
                    }]
    """
    def __init__(self,data=[]):
        self.data = data
        self.dataType = "dataBox"

    def set_data(self,data):
        self.data = data
    def get_data():
        return self.data

class WordCloud:
    """
    sampleData = [
                    {
                      "text": "Alphabet",
                      "value": "58"
                    },
                    {
                      "text": "mobile interface",
                      "value": "48"
                    }
                ]
    """
    def __init__(self,data=[]):
        self.data = data
        self.dataType = "wordCloud"

    def set_data(self,data):
        self.data = data
    def get_data():
        return self.data
