import json
import re

from pyspark.mllib.regression import LabeledPoint
from pyspark.mllib.tree import DecisionTree

from bi.algorithms import utils as MLUtils
from bi.common import utils as CommonUtils
from bi.common.datafilterer import DataFrameFilterer
from bi.common.decorators import accepts
from bi.common.results import DecisionTreeResult
from bi.settings import setting as GLOBALSETTINGS
"""
Decision Tree
"""


class DecisionTrees:

    # @accepts(object, DataFrame)
    def __init__(self, data_frame, df_helper, df_context, spark, meta_parser,scriptWeight=None, analysisName=None):
        self._spark = spark
        self._maxDepth = 5
        self._metaParser = meta_parser
        self._dataframe_helper = df_helper
        self._dataframe_context = df_context
        self._ignoreMsg = self._dataframe_context.get_message_ignore()
        self._measure_columns = self._dataframe_helper.get_numeric_columns()
        self._dimension_columns = self._dataframe_helper.get_string_columns()
        self._date_columns = self._dataframe_context.get_date_columns()
        self._uid_col = self._dataframe_context.get_uid_column()
        if self._metaParser.check_column_isin_ignored_suggestion(self._uid_col):
            self._dimension_columns = list(set(self._dimension_columns) - {self._uid_col})
        if len(self._date_columns) >0 :
            self._dimension_columns = list(set(self._dimension_columns)-set(self._date_columns))
        self._data_frame = MLUtils.bucket_all_measures(data_frame,self._measure_columns,self._dimension_columns)
        self._data_frame1 = self._data_frame
        self._mapping_dict = {}
        self._new_rules = {}
        self._total = {}
        self._success = {}
        self._probability = {}
        self._alias_dict = {}
        self._important_vars = {}

        self._completionStatus = self._dataframe_context.get_completion_status()
        if analysisName == None:
            self._analysisName = self._dataframe_context.get_analysis_name()
        else:
            self._analysisName = analysisName
        self._messageURL = self._dataframe_context.get_message_url()
        if scriptWeight == None:
            self._scriptWeightDict = self._dataframe_context.get_dimension_analysis_weight()
        else:
            self._scriptWeightDict = scriptWeight

        self._scriptStages = {
            "initialization":{
                "summary":"Initialized the Decision Tree Script",
                "weight":0
                },
            "treegeneration":{
                "summary":"Decision tree generation finished",
                "weight":10
                }
            }
        self._completionStatus += self._scriptWeightDict[self._analysisName]["script"]*self._scriptStages["initialization"]["weight"]/10
        progressMessage = CommonUtils.create_progress_message_object(self._analysisName,\
                                    "initialization",\
                                    "info",\
                                    self._scriptStages["initialization"]["summary"],\
                                    self._completionStatus,\
                                    self._completionStatus)
        CommonUtils.save_progress_message(self._messageURL,progressMessage,ignore=self._ignoreMsg)
        self._dataframe_context.update_completion_status(self._completionStatus)

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



    @accepts(object, rule_list=list,target=str)
    def extract_rules(self, rule_list, target):
        if not self._important_vars.has_key(target):
            self._important_vars[target] = []
        DFF = DataFrameFilterer(self._data_frame1)
        colname = self._target_dimension
        success = 0
        total = 0
        important_vars = []
        for rule in rule_list:
            if ' <= ' in rule:
                var,limit = re.split(' <= ',rule)
                DFF.values_below(var,limit)
            elif ' > ' in rule:
                var,limit = re.split(' > ',rule)
                DFF.values_above(var,limit)
            elif ' not in ' in rule:
                var,levels = rule.split(' not in (')
                levels=levels[0:-1].split(",")
                levels = [self._alias_dict[x] for x in levels]
                DFF.values_not_in(var,levels)
            elif ' in ' in rule:
                var,levels = rule.split(' in (')
                levels=levels[0:-1].split(",")
                levels = [self._alias_dict[x] for x in levels]
                DFF.values_in(var,levels)
            important_vars.append(var)
        for rows in DFF.get_aggregated_result(colname,target):
            if(rows[0]==target):
                success = rows[1]
            total = total + rows[1]
        self._important_vars[target] = list(set(self._important_vars[target] + important_vars))
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
            return success



    def generate_new_tree(self, rules, rule_list=None):
        if rule_list is None:
            rule_list = []
        rules_list=rule_list
        new_rules = {'name':rules['name']}
        if rules.has_key('children'):
            for rule in rules['children']:
                if rules['name']!='Root':
                    val = self.generate_new_tree(rule,rule_list=rules_list+[rules['name']])
                else:
                    val = self.generate_new_tree(rule,rule_list=rules_list)
                if val!=None:
                    if not new_rules.has_key('children'):
                        new_rules['children'] = []
                    new_rules['children'].append(val)
            return new_rules
        else:
            target = rules['name'][9:]
            num_success = self.extract_rules(rules_list,target)
            if 'Predict:' in rules['name'] and num_success>0:
                return new_rules

    def wrap_tree(self, tree):
        new_tree = {}
        if "children" in tree.keys() and len(tree['children'])>0:
            new_tree['name'] = tree['name']
            for child in tree['children']:
                val = self.wrap_tree(child)
                if val!= None:
                    if not new_tree.has_key('children'):
                        new_tree['children']=[]
                    new_tree['children'].append(val)
            if new_tree.has_key('children'):
                if len(new_tree['children'])>0:
                    return new_tree
        elif 'Predict: ' in tree['name'] or 'Root' in tree['name']:
            new_tree['name'] = tree['name']
            return new_tree



    @accepts(object, measure_columns=(list, tuple), dimension_columns=(list, tuple))
    def test_all(self, measure_columns=None, dimension_columns=None):
        measures = measure_columns
        if measure_columns is None:
            measures = self._measure_columns
        self._target_dimension = dimension_columns[0]
        dimension = self._target_dimension
        max_num_levels = GLOBALSETTINGS.DTREE_TARGET_DIMENSION_MAX_LEVEL
        max_num_levels = min(max_num_levels, round(self._dataframe_helper.get_num_rows()**0.5))
        # all_dimensions = [dim for dim in self._dimension_columns if self._dataframe_helper.get_num_unique_values(dim) <= max_num_levels]
        all_dimensions = [dim for dim in self._dimension_columns if self._metaParser.get_num_unique_values(dim) <= max_num_levels]
        all_measures = self._measure_columns
        cat_feature_info = []
        columns_without_dimension = [x for x in all_dimensions if x != dimension]
        mapping_dict = {}
        masterMappingDict = {}
        decision_tree_result = DecisionTreeResult()
        decision_tree_result.set_freq_distribution(self._metaParser.get_unique_level_dict(self._target_dimension), self._important_vars)
        self._data_frame, mapping_dict = MLUtils.add_string_index(self._data_frame, all_dimensions)
        print self._data_frame.show(1)
        # standard_measure_index = {0.0:'Low',1.0:'Medium',2.0:'High'}
        standard_measure_index = {0.0:'Low',1.0:'Below Average',2.0:'Average',3.0:'Above Average',4.0:'High'}
        for measure in all_measures:
            mapping_dict[measure] = standard_measure_index

        for k,v in mapping_dict.items():
            temp = {}
            for k1,v1 in v.items():
                self._alias_dict[v1.replace(",","")] = v1
                temp[k1] = v1.replace(",","")
            mapping_dict[k] = temp

        self._mapping_dict = mapping_dict

        for c in columns_without_dimension:
            cat_feature_info.append(self._data_frame.select(c).distinct().count())
        for c in all_measures:
            cat_feature_info.append(5)
        columns_without_dimension = columns_without_dimension+all_measures
        all_measures = []
        if len(cat_feature_info)>0:
            max_length = max(cat_feature_info)
        else:
            max_length=32
        cat_feature_info = dict(enumerate(cat_feature_info))
        try:
            dimension_classes = self._metaParser.get_num_unique_values(dimension)
        except:
            dimension_classes = self._data_frame.select(dimension).distinct().count()
        self._data_frame = self._data_frame[[dimension] + columns_without_dimension + all_measures]
        print "="*200
        print self._data_frame.rdd.first()
        print "numClasses",dimension_classes
        print "maxDepth",self._maxDepth
        print "maxBins",max_length
        print "="*200
        data = self._data_frame.rdd.map(lambda x: LabeledPoint(x[0], x[1:]))
        (trainingData, testData) = data.randomSplit([1.0, 0.0])
        # TO DO : set maxBins at least equal to the max level of categories in dimension column
        model = DecisionTree.trainClassifier(trainingData, numClasses=dimension_classes, categoricalFeaturesInfo=cat_feature_info, impurity='gini', maxDepth=self._maxDepth, maxBins=max_length)
        output_result = model.toDebugString()
        decision_tree = self.tree_json(output_result, self._data_frame)
        self._new_tree = self.generate_new_tree(decision_tree)
        self._new_tree = self.wrap_tree(self._new_tree)
        # self._new_tree = utils.recursiveRemoveNullNodes(self._new_tree)
        # decision_tree_result.set_params(self._new_tree, self._new_rules, self._total, self._success, self._probability)
        print self._new_rules.keys()
        print "==="*40
        decision_tree_result.set_params(self._new_tree, self._new_rules, self._total, self._success, self._probability)
        self._completionStatus += self._scriptWeightDict[self._analysisName]["script"]*self._scriptStages["treegeneration"]["weight"]/10
        progressMessage = CommonUtils.create_progress_message_object(self._analysisName,\
                                    "treegeneration",\
                                    "info",\
                                    self._scriptStages["treegeneration"]["summary"],\
                                    self._completionStatus,\
                                    self._completionStatus)
        CommonUtils.save_progress_message(self._messageURL,progressMessage,ignore=self._ignoreMsg)
        self._dataframe_context.update_completion_status(self._completionStatus)
        return decision_tree_result
