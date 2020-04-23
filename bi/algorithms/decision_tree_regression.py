import json
import re

from pyspark.mllib.regression import LabeledPoint
from pyspark.mllib.tree import DecisionTree

from bi.common.datafilterer import DataFrameFilterer
from bi.common.decorators import accepts
from bi.common.results import DecisionTreeResult

from bi.algorithms import utils as MLUtils
from bi.common import utils as CommonUtils
from bi.algorithms import KmeansClustering
from bi.settings import setting as GLOBALSETTINGS

from bi.common import DataLoader
from bi.common import DataFrameHelper

"""
Decision Tree
"""


class DecisionTreeRegression:

    #@accepts(object, DataFrame)
    def __init__(self, data_frame, df_context, df_helper, spark, meta_parser,scriptWeight=None, analysisName=None):
        self._spark = spark
        self._metaParser = meta_parser
        self._data_frame = data_frame
        self._data_frame1 = data_frame
        self._dataframe_helper = df_helper
        self._dataframe_context = df_context
        self._measure_columns = self._dataframe_helper.get_numeric_columns()
        self._dimension_columns = self._dataframe_helper.get_string_columns()
        self._date_columns = self._dataframe_context.get_date_columns()
        self._uid_col = self._dataframe_context.get_uid_column()
        if self._metaParser.check_column_isin_ignored_suggestion(self._uid_col):
            self._dimension_columns = list(set(self._dimension_columns) - {self._uid_col})
        if len(self._date_columns) >0 :
            self._dimension_columns = list(set(self._dimension_columns)-set(self._date_columns))
        self._mapping_dict = {}
        self._new_rules = {}
        self._total = {}
        self._success = {}
        self._probability = {}
        self._alias_dict = {}
        self._important_vars = {}
        self._numCluster = None

        self._data_frame = self._dataframe_helper.fill_missing_values(self._data_frame)
        self._data_frame1 = self._dataframe_helper.fill_missing_values(self._data_frame1)

        self._completionStatus = self._dataframe_context.get_completion_status()
        self._messageURL = self._dataframe_context.get_message_url()
        if analysisName == None:
            self._analysisName = self._dataframe_context.get_analysis_name()
        else:
            self._analysisName = analysisName
        if scriptWeight == None:
            self._scriptWeightDict = self._dataframe_context.get_measure_analysis_weight()
        else:
            self._scriptWeightDict = scriptWeight
        self._scriptStages = {
            "dtreeTrainingStart":{
                "summary":"Started the Decision Tree Regression Script",
                "weight":0
                },
            "dtreeTrainingEnd":{
                "summary":"Decision Tree Regression Learning Finished",
                "weight":10
                },
            }

        CommonUtils.create_update_and_save_progress_message(self._dataframe_context,self._scriptWeightDict,self._scriptStages,self._analysisName,"dtreeTrainingStart","info",weightKey="script")



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
                    # print "block2",block2
                    # print self._mapping_dict[df.columns[0]]
                    # print [int(float(block2.split(':')[1].strip()))]
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
        target = self._reverse_map[target]
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
                var,levels = re.split(' not in ',rule)
                levels=levels[1:-1].split(",")
                levels = [self._alias_dict[x] for x in levels]
                DFF.values_not_in(var,levels)
            elif ' in ' in rule:
                var,levels = re.split(' in ',rule)
                levels=levels[1:-1].split(",")
                levels = [self._alias_dict[x] for x in levels]
                DFF.values_in(var,levels)
            important_vars.append(var)
        for rows in DFF.get_aggregated_result(colname,target):
            if(rows[0]==target):
                success = rows[1]
            total = total + rows[1]
        target = self._mapping_dict[self._target_dimension][target]
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

    def transform_data_frames(self):
        self._data_frame, self._mapping_dict = MLUtils.add_string_index(self._data_frame, self._dimension_columns)
        # self._data_frame, clusters = MLUtils.cluster_by_column(self._data_frame, self._target_dimension)
        # self._data_frame1, self._aggr_data = MLUtils.cluster_by_column(self._data_frame1, self._target_dimension, get_aggregation=True)
        # self._data_frame, clusters = MLUtils.bin_column(self._data_frame, self._target_dimension)
        self._data_frame, clusters, splitRanges = MLUtils.bin_column(self._data_frame, self._target_dimension)

        self._data_frame1, self._aggr_data = MLUtils.bin_column(self._data_frame1, self._target_dimension, get_aggregation=True)
        self._cluster_order = [x[1] for x in sorted(zip(clusters,[0,1,2]))]
        displayArray = zip(GLOBALSETTINGS.DECISIONTREERKMEANSTARGETNAME,splitRanges)
        displayArray = [x[0]+" : "+x[1] for x in displayArray]
        self._mapping_dict[self._target_dimension] = dict(zip(self._cluster_order,displayArray))
        self._reverse_map = {}
        for k,v in self._mapping_dict[self._target_dimension].iteritems():
            self._reverse_map[v] = k
        self.set_alias_dict()


    # def transform_data_frames(self):
    #     self._data_frame, self._mapping_dict = MLUtils.add_string_index(self._data_frame, self._dimension_columns)
    #     kmeans_obj = KmeansClustering(self._data_frame, self._dataframe_helper, self._dataframe_context, self._metaParser, self._spark)
    #     kmeans_obj.kmeans_pipeline([self._target_dimension],cluster_count=3)
    #     kmeans_result = {"stats":kmeans_obj.get_kmeans_result(),"data":kmeans_obj.get_prediction_data()}
    #     self._aggr_data = kmeans_obj.get_aggregated_summary(self._target_dimension)
    #     print "kmeans_result",kmeans_result
    #     clusterCenters = sorted([x[0] for x in kmeans_result["stats"]["centers"]])
    #     self._numCluster = len(clusterCenters)
    #     print dict(zip(range(len(clusterCenters)),GLOBALSETTINGS.DECISIONTREERKMEANSTARGETNAME))
    #     self._mapping_dict[self._target_dimension] = dict(zip(range(len(clusterCenters)),GLOBALSETTINGS.DECISIONTREERKMEANSTARGETNAME))
    #     self._reverse_map = {}
    #     for k,v in self._mapping_dict[self._target_dimension].iteritems():
    #         self._reverse_map[v] = k
    #     predictedDf = kmeans_obj.get_prediction_data()
    #     print "predictedDf"*3
    #     print predictedDf.show(3)
    #     self._data_frame = predictedDf.select([x for x in self._data_frame.columns if x != self._target_dimension]+["prediction"])
    #     self._data_frame = self._data_frame.withColumnRenamed("prediction",self._target_dimension)
    #     self.set_alias_dict()

    def set_alias_dict(self):
        mapping_dict = self._mapping_dict
        for k,v in mapping_dict.items():
            temp = {}
            for k1,v1 in v.items():
                self._alias_dict[v1.replace(",","")] = v1
                temp[k1] = v1.replace(",","")
            mapping_dict[k] = temp
        self._mapping_dict = mapping_dict

    @accepts(object, measure_columns=(list, tuple), dimension_columns=(list, tuple))
    def test_all(self, measure_columns=None, dimension_columns=None):
        if dimension_columns is None:
            dimensions = self._dimension_columns
        self._target_dimension = measure_columns[0]
        dimension = self._target_dimension
        max_num_levels = GLOBALSETTINGS.DTREE_TARGET_DIMENSION_MAX_LEVEL
        max_num_levels = min(max_num_levels, round(self._dataframe_helper.get_num_rows()**0.5))
        # all_dimensions = [dim for dim in self._dimension_columns if self._dataframe_helper.get_num_unique_values(dim) <= max_num_levels]
        all_dimensions = [dim for dim in self._dimension_columns if self._metaParser.get_num_unique_values(dim) <= max_num_levels]
        all_measures = [x for x in self._measure_columns if x!=self._target_dimension]
        self.transform_data_frames()
        decision_tree_result = DecisionTreeResult()
        cat_feature_info = [len(self._mapping_dict[c]) for c in all_dimensions]
        if len(cat_feature_info)>0:
            max_length = max(cat_feature_info)
        else:
            max_length=32
        cat_feature_info = dict(enumerate(cat_feature_info))
        # print cat_feature_info
        dimension_classes = self._data_frame.select(dimension).distinct().count()
        self._data_frame = self._data_frame[[dimension] + all_dimensions + all_measures]
        data = self._data_frame.rdd.map(lambda x: LabeledPoint(x[0], x[1:]))
        (trainingData, testData) = data.randomSplit([1.0, 0.0])
        # TO DO : set maxBins at least equal to the max level of categories in dimension column
        model = DecisionTree.trainClassifier(trainingData, numClasses=dimension_classes, categoricalFeaturesInfo=cat_feature_info, impurity='gini', maxDepth=3, maxBins=max_length)
        output_result = model.toDebugString()
        print "output_result",output_result
        decision_tree = self.tree_json(output_result, self._data_frame)
        self._new_tree = self.generate_new_tree(decision_tree)
        self._new_tree = self.wrap_tree(self._new_tree)
        # self._new_tree = utils.recursiveRemoveNullNodes(self._new_tree)
        # decision_tree_result.set_params(self._new_tree, self._new_rules, self._total, self._success, self._probability)
        decision_tree_result.set_params(self._new_tree, self._new_rules, self._total, self._success, self._probability)
        decision_tree_result.set_target_map(self._mapping_dict[self._target_dimension], self._aggr_data, self._important_vars)

        # self._completionStatus += self._scriptWeightDict[self._analysisName]["script"]*self._scriptStages["dtreeTrainingStart"]["weight"]/10
        # progressMessage = CommonUtils.create_progress_message_object(self._analysisName,\
        #                             "dtreeTrainingEnd",\
        #                             "info",\
        #                             self._scriptStages["dtreeTrainingEnd"]["summary"],\
        #                             self._completionStatus,\
        #                             self._completionStatus)
        # CommonUtils.save_progress_message(self._messageURL,progressMessage)
        # self._dataframe_context.update_completion_status(self._completionStatus)
        CommonUtils.create_update_and_save_progress_message(self._dataframe_context,self._scriptWeightDict,self._scriptStages,self._analysisName,"dtreeTrainingEnd","info",weightKey="script")

        # print decision_tree_result
        return decision_tree_result
