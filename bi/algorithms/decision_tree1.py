import json
import re

from pyspark.mllib.regression import LabeledPoint
from pyspark.mllib.tree import DecisionTree

from bi.common.datafilterer import DataFrameFilterer
from bi.common.decorators import accepts
from bi.common.results import DecisionTreeResult

"""
Decision Tree
"""


class DecisionTrees:

    #@accepts(object, DataFrame)
    def __init__(self, data_frame, dataframe_helper, spark):
        self._spark = spark
        self._data_frame = data_frame
        self._data_frame1 = data_frame
        #self._data_frame_filterer = DataFrameFilterer(data_frame)
        self._measure_columns = dataframe_helper.get_numeric_columns()
        self._dimension_columns = dataframe_helper.get_string_columns()
        self._mapping_dict = {}
        self._new_rules = {}
        self._total = {}
        self._success = {}
        self._probability = {}

    def parse(self, lines, df):
        block = []
        while lines :

            if lines[0].startswith('If'):
                bl = ' '.join(lines.pop(0).split()[1:]).replace('(', '').replace(')', '')
                if "feature" in bl:
                    feature_mapping = df.columns[int(bl.split()[1]) + 1]
                    bl = "%s %s" % (feature_mapping, ' '.join(bl.split()[2:]))
                    if "{" in bl:
                        sub_mappings = json.loads(bl.split()[-1].strip().replace('{', '[').replace('}', ']'))
                        sub_mappings_string = '(' +  ','.join(list(self._mapping_dict[feature_mapping][int(x)] for x in sub_mappings)) + ')'
                        bl = "%s in %s" % (feature_mapping, sub_mappings_string)
                block.append({'name':bl, 'children':self.parse(lines, df)})
                if lines[0].startswith('Else'):
                    be = ' '.join(lines.pop(0).split()[1:]).replace('(', '').replace(')', '')
                    if "feature" in be:
                        feature_mapping = df.columns[int(be.split()[1]) + 1]
                        be = "%s %s" % (feature_mapping, ' '.join(be.split()[2:]))
                        if "{" in be:
                            sub_mappings = json.loads(be.split()[-1].strip().replace('{', '[').replace('}', ']'))
                            sub_mappings_string = '(' + ','.join(list(self._mapping_dict[feature_mapping][int(x)] for x in sub_mappings)) + ')'
                            be = "%s not in %s" % (feature_mapping, sub_mappings_string)
                    block.append({'name':be, 'children':self.parse(lines, df)})
            elif not lines[0].startswith(('If','Else')):
                block2 = lines.pop(0)
                if "feature" in block2:
                    block2 = "%s %s" % (df.columns[int(block2.split()[1])], ' '.join(block2.split()[2:]))
                if "Predict" in block2:
                    outcome = self._mapping_dict[df.columns[0]][int(float(block2.split(':')[1].strip()))]
                    block2 = "Predict: %s" % (outcome)
                block.append({'name':block2})
            else:
                break
        return block


    def tree_json(self, tree, df):
        data = []
        for line in tree.splitlines() :
            if line.strip():
                line = line.strip()
                data.append(line)
            else : break
            if not line : break
        res = []
        res.append({'name': 'Root', 'children':self.parse(data[1:], df)})
        return res[0]



    @accepts(object, rules = dict, colname = str, rule_list=list)
    def extract_rules(self, rules, colname, rule_list=None):
        if rule_list is None:
            rule_list = []
        case = 0
        var = ''
        limit = None
        levels = ''
        return_value = False
        new_tree = {}
        new_tree['name'] = rules['name']

        if rules.has_key('children'):
            new_tree['children'] = []
            for children in rules['children']:
                new_tree['children'].append(self.extract_rules(rules=children, colname = colname, rule_list = rule_list+[rules['name']]))
            return new_tree
        else:
            DFF = DataFrameFilterer(self._data_frame1)
            success = 0
            total = 0
            target = rules['name'][9:]
            for rule in rule_list:
                if ' <= ' in rule:
                    var,limit = re.split(' <= ',rule)
                    DFF.values_below(var,limit)
                elif ' > ' in rule:
                    var,limit = re.split(' > ',rule)
                    DFF.values_above(var,limit)
                elif ' not in ' in rule:
                    var,levels = re.split(' not in ',rule)
                    DFF.values_not_in(var,levels)
                elif ' in ' in rule:
                    var,levels = re.split(' in ',rule)
                    DFF.values_in(var,levels)
            for rows in DFF.get_aggregated_result(colname,target):
                if(rows[0]==target):
                    success = rows[1]
                total = total + rows[1]
            if (total > 0):
                if not self._new_rules.has_key(target):
                    self._new_rules[target] = []
                    self._total[target] = []
                    self._success[target] = []
                    self._probability[target] = []
                self._new_rules[target].append(','.join(rule_list))
                self._total[target].append(total)
                self._success[target].append(success)
                self._probability[target].append(success*100.0/total)
                return new_tree

    @accepts(object, decision_tree = dict, target = str)
    def generate_probabilities(self, decision_tree, target):
        colname = target
        self._new_tree = {}
        self._new_tree['name'] = decision_tree['name']
        for rules in decision_tree['children']:
            if self._new_tree.has_key('children'):
                self._new_tree['children'].append(self.extract_rules(rules=rules, colname=colname))
            else:
                self._new_tree['children']=[]

    @accepts(object, measure_columns=(list, tuple), dimension_columns=(list, tuple))
    def test_all(self, measure_columns=None, dimension_columns=None):
        measures = measure_columns
        if measure_columns is None:
            measures = self._measure_columns
        dimension = dimension_columns[0]
        all_dimensions = self._dimension_columns
        all_measures = self._measure_columns
        cat_feature_info = []
        columns_without_dimension = list(x for x in all_dimensions if x != dimension)
        mapping_dict = {}
        masterMappingDict = {}
        decision_tree_result = DecisionTreeResult()
        for column in all_dimensions:
            mapping_dict[column] = dict(enumerate(self._data_frame.select(column).distinct().rdd.map(lambda x: str(x[0])).collect()))
        # for c in mapping_dict:
        #     name = c
        #     reverseMap = {v: k for k, v in mapping_dict[c].iteritems()}
        #     udf = UserDefinedFunction(lambda x: reverseMap[x], StringType())
        #     self._data_frame = self._data_frame.select(*[udf(column).alias(name) if column == name else column for column in self._data_frame.columns])

        # converting spark dataframe to pandas for transformation and then back to spark dataframe
        pandasDataFrame = self._data_frame.toPandas()
        for key in mapping_dict:
            pandasDataFrame[key] = pandasDataFrame[key].apply(lambda x: 'None' if x==None else x)
            reverseMap = {v: k for k, v in mapping_dict[key].iteritems()}
            pandasDataFrame[key] = pandasDataFrame[key].apply(lambda x: reverseMap[x])
        # sqlCtx = SQLContext(self._spark)
        self._data_frame = self._spark.createDataFrame(pandasDataFrame)
        self._mapping_dict = mapping_dict
        for c in columns_without_dimension:
            cat_feature_info.append(self._data_frame.select(c).distinct().count())
        if len(cat_feature_info)>0:
            max_length = max(cat_feature_info)
        else:
            max_length=32
        cat_feature_info = dict(enumerate(cat_feature_info))
        dimension_classes = self._data_frame.select(dimension).distinct().count()
        self._data_frame = self._data_frame[[dimension] + columns_without_dimension + all_measures]
        data = self._data_frame.rdd.map(lambda x: LabeledPoint(x[0], x[1:]))
        (trainingData, testData) = data.randomSplit([1.0, 0.0])
        # TO DO : set maxBins at least equal to the max level of categories in dimension column
        model = DecisionTree.trainClassifier(trainingData, numClasses=dimension_classes, categoricalFeaturesInfo=cat_feature_info, impurity='gini', maxDepth=3, maxBins=max_length)
        output_result = model.toDebugString()
        decision_tree = self.tree_json(output_result, self._data_frame)
        self.generate_probabilities(decision_tree, dimension)
        # self._new_tree = utils.recursiveRemoveNullNodes(self._new_tree)
        # decision_tree_result.set_params(self._new_tree, self._new_rules, self._total, self._success, self._probability)
        decision_tree_result.set_params(decision_tree, self._new_rules, self._total, self._success, self._probability)

        return decision_tree_result
