import json
import re

from pyspark.mllib.regression import LabeledPoint
from pyspark.mllib.tree import DecisionTree
from pyspark.sql import functions as FN
from pyspark.sql.functions import col

from bi.common.datafilterer import DataFrameFilterer
from bi.common.decorators import accepts
from bi.common.results import DecisionTreeResult
from bi.narratives import utils as NarrativesUtils

"""
Decision Tree
"""


class DecisionTreeRegression:

    #@accepts(object, DataFrame)
    def __init__(self, data_frame, df_context, dataframe_helper, spark):
        self._spark = spark
        self._data_frame = data_frame
        self._data_frame1 = data_frame
        #self._data_frame_filterer = DataFrameFilterer(data_frame)
        self._measure_columns = dataframe_helper.get_numeric_columns()
        self._dimension_columns = dataframe_helper.get_string_columns()
        self.date_columns = df_context.get_date_columns()
        if self.date_columns != None:
            self._dimension_columns = list(set(self._dimension_columns)-set(self.date_columns))
        self._mapping_dict = {}
        self._new_rules = {}
        self._total = {}
        self._success = {}
        self._probability = {}
        self._predicts = []
        self._map = {}

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
                    temp = float(block2.split(':')[1].strip())
                    self._predicts.append(temp)
                    self._predicts.sort()
                #     outcome = self._mapping_dict[df.columns[0]][int(float(block2.split(':')[1].strip()))]
                #     block2 = "Predict: %s" % (outcome)
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
        measure_column_name = self._target_column
        self._splits = []
        start = self._data_frame.filter(col(measure_column_name).isNotNull()).select(FN.min(measure_column_name)).collect()[0][0]
        self._splits.append(start)
        self._label_code = {}
        label_code = 0.0
        self._coding = []
        for idx in range(len(self._predicts)):
            if idx == len(self._predicts) - 1:
                end = self._data_frame.filter(col(measure_column_name).isNotNull()).select(FN.max(measure_column_name)).collect()[0][0]
            else:
                end = (self._predicts[idx]+self._predicts[idx+1])/2
            group_name = NarrativesUtils.round_number(start,2) + ' to ' + NarrativesUtils.round_number(end,2)
            self._map[self._predicts[idx]] ={'start':start, 'end': end, 'group': group_name}
            self._label_code[label_code] = group_name
            start = end
            label_code = label_code+1
            self._splits.append(start)
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
            self._splits.sort()
            self._splits = list(set(self._splits))
            binned_colname = DFF.bucketize(self._splits, colname)
            target = self._map[float(target.strip())]['group']
            agg_result = DFF.get_aggregated_result(binned_colname,target)
            for rows in agg_result:
                if(self._label_code[rows[0]]==target):
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
                key = float(new_tree['name'][9:])
                new_tree['name'] = 'Predict: ' + self._map[key]['group']
                return new_tree

    @accepts(object, decision_tree = dict, target = str)
    def generate_probabilities(self, decision_tree, target):
        colname = target
        self._new_tree = {}
        self._new_tree['name'] = decision_tree['name']
        # self._new_tree['children']=[]
        for rules in decision_tree['children']:
            if not self._new_tree.has_key('children'):
                self._new_tree['children']=[]
            self._new_tree['children'].append(self.extract_rules(rules=rules, colname=colname))
            # else:
            #     self._new_tree['children']=[]

    @accepts(object, measure_columns=(list, tuple), dimension_columns=(list, tuple))
    def test_all(self, measure_columns=None, dimension_columns=None):
        measures = measure_columns[0]
        self._target_column = measures
        #dimension = dimension_columns[0]
        all_dimensions = self._dimension_columns
        all_measures = list(x for x in self._measure_columns if x != measures)
        cat_feature_info = []
        #columns_without_dimension = list(x for x in all_dimensions if x != dimension)
        columns_without_dimension = all_dimensions
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
        #dimension_classes = self._data_frame.select(dimension).distinct().count()
        self._data_frame = self._data_frame[[measures] + columns_without_dimension + all_measures]
        data = self._data_frame.rdd.map(lambda x: LabeledPoint(x[0], x[1:]))
        (trainingData, testData) = data.randomSplit([1.0, 0.0])
        # TO DO : set maxBins at least equal to the max level of categories in dimension column
        model = DecisionTree.trainRegressor(trainingData,  categoricalFeaturesInfo=cat_feature_info, impurity='variance', maxDepth=3, maxBins=max_length)
        output_result = model.toDebugString()
        decision_tree = self.tree_json(output_result, self._data_frame)
        self.generate_probabilities(decision_tree, measures)
        decision_tree_result.set_params(self._new_tree, self._new_rules, self._total, self._success, self._probability)
        return decision_tree_result
