import json
import json
import random

from pyspark.sql.functions import col

from bi.common import NormalCard, NarrativesTree, HtmlData, C3ChartData, TableData, ToggleData,DataFrameHelper
from bi.common import NormalChartData, ChartJson
from bi.common import utils as CommonUtils
from bi.narratives import utils as NarrativesUtils
from bi.settings import setting as GLOBALSETTINGS
from bi.transformations import Binner
from pyspark.sql import functions as F

class ChiSquareAnalysis:
    def __init__ (self, df_context, df_helper,chisquare_result, target_dimension, analysed_dimension, significant_variables, num_analysed_variables, data_frame, measure_columns,base_dir,appid=None,target_chisquare_result=None):
        self._blockSplitter = "|~NEWBLOCK~|"
        self._highlightFlag = "|~HIGHLIGHT~|"
        self._dimensionNode = NarrativesTree()
        self._dimensionNode.set_name(target_dimension)
        self._data_frame = data_frame
        self._dataframe_context = df_context
        self._dataframe_helper = df_helper
        self._chisquare_result = chisquare_result
        self._target_dimension = target_dimension
        self._analysed_dimension = analysed_dimension
        self._significant_variables =  significant_variables
        self._target_chisquare_result = target_chisquare_result
        self._measure_columns = self._dataframe_helper.get_numeric_columns()
        self._chiSquareLevelLimit = GLOBALSETTINGS.CHISQUARELEVELLIMIT

        self._num_analysed_variables = num_analysed_variables
        self._chiSquareTable = chisquare_result.get_contingency_table()

        significant_variables=list(set(significant_variables) - {analysed_dimension})
        if len(significant_variables)<=20:
            if len(significant_variables)<=3:
                self._second_level_dimensions = list(significant_variables)
            else:
                self._second_level_dimensions = list(significant_variables)[:3]
        else:
            self._second_level_dimensions = list(significant_variables)[:5]

        print self._second_level_dimensions

        self._appid = appid
        self._card1 = NormalCard()
        self._targetCards = []
        self._base_dir = base_dir

        self._binTargetCol = False
        self._binAnalyzedCol = False
        print "--------Chi-Square Narratives for ", analysed_dimension, "---------"
        if self._dataframe_context.get_custom_analysis_details() != None:
            binnedColObj = [x["colName"] for x in self._dataframe_context.get_custom_analysis_details()]
            print "analysed_dimension : ", self._analysed_dimension
            if binnedColObj != None and self._target_dimension in binnedColObj:
                self._binTargetCol = True
            if binnedColObj != None and (self._analysed_dimension in binnedColObj or self._analysed_dimension in self._measure_columns):
                self._binAnalyzedCol = True


        if self._appid == None:
            self._generate_narratives()
            self._dimensionNode.add_cards([self._card1]+self._targetCards)
            self._dimensionNode.set_name("{}".format(analysed_dimension))
        elif self._appid == "2":
            self._generate_narratives()
            self._dimensionNode.add_cards([self._card1])
            self._dimensionNode.set_name("{}".format(analysed_dimension))
        elif self._appid == "1":
            self._generate_narratives()
            self._dimensionNode.add_cards([self._card1])
            self._dimensionNode.set_name("{}".format(analysed_dimension))

    def get_dimension_node(self):
        return json.loads(CommonUtils.convert_python_object_to_json(self._dimensionNode))

    def get_dimension_card1(self):
        return self._card1

    def _generate_narratives(self):
          chisquare_result = self._chisquare_result
          target_dimension = self._target_dimension
          analysed_dimension = self._analysed_dimension
          significant_variables = self._significant_variables
          num_analysed_variables = self._num_analysed_variables
          table = self._chiSquareTable
          total = self._chiSquareTable.get_total()

          levels = self._chiSquareTable.get_column_two_levels()
          level_counts = self._chiSquareTable.get_column_total()
          levels_count_sum = sum(level_counts)
          levels_percentages = [i*100.0/levels_count_sum for i in level_counts]
          sorted_levels = sorted(zip(level_counts,levels),reverse=True)
          level_differences = [0.0]+[sorted_levels[i][0]-sorted_levels[i+1][0] for i in range(len(sorted_levels)-1)]

          top_dims = [j for i,j in sorted_levels[:level_differences.index(max(level_differences))]]
          top_dims_contribution = sum([i for i,j in sorted_levels[:level_differences.index(max(level_differences))]])
          bottom_dim = sorted_levels[-1][1]
          bottom_dim_contribution = sorted_levels[-1][0]
          bottom_dims = [y for x,y in sorted_levels if x==bottom_dim_contribution]

          target_levels = self._chiSquareTable.get_column_one_levels()

          target_counts = self._chiSquareTable.get_row_total()
          sorted_target_levels = sorted(zip(target_counts,target_levels),reverse=True)

          top_target_count, top_target = sorted_target_levels[0]
          second_target_count, second_target = sorted_target_levels[1]

          top_target_contributions = [table.get_value(top_target,i) for i in levels]
          sum_top_target = sum(top_target_contributions)

          sorted_levels = sorted(zip(top_target_contributions,levels), reverse=True)
          level_differences = [0.0] + [sorted_levels[i][0]-sorted_levels[i+1][0] for i in range(len(sorted_levels)-1)]
          top_target_top_dims = [j for i,j in sorted_levels[:level_differences.index(max(level_differences))]]
          top_target_top_dims_contribution = sum([i for i,j in sorted_levels[:level_differences.index(max(level_differences))]])
          top_target_bottom_dim = sorted_levels[-1][1]
          top_target_bottom_dim_contribution = sorted_levels[-1][0]

          top_target_percentages = [i*100.0/sum_top_target for i in top_target_contributions]
          best_top_target_index = top_target_contributions.index(max(top_target_contributions))
          worst_top_target_index = top_target_contributions.index(min(top_target_contributions))
          top_target_differences = [x-y for x,y in zip(levels_percentages,top_target_percentages)]
          if len(top_target_differences)>6:
              tops = 2
              bottoms = -2
          elif len(top_target_differences)>4:
              tops = 2
              bottoms = -1
          else:
              tops = 1
              bottoms = -1
          sorted_ = sorted(enumerate(top_target_differences), key = lambda x: x[1],reverse=True)
          best_top_difference_indices = [x for x,y in sorted_[:tops]]
          worst_top_difference_indices = [x for x,y in sorted_[bottoms:]]

          top_target_shares = [x*100.0/y for x,y in zip(top_target_contributions,level_counts)]
          max_top_target_shares = max(top_target_shares)
          best_top_target_share_index = [idx for idx,val in enumerate(top_target_shares) if val==max_top_target_shares]
          level_counts_threshold = sum(level_counts)*0.05/len(level_counts)
          min_top_target_shares = min([x for x,y in zip(top_target_shares,level_counts) if y>=level_counts_threshold])
          worst_top_target_share_index = [idx for idx,val in enumerate(top_target_shares) if val==min_top_target_shares]
          overall_top_percentage = sum_top_target*100.0/total

          second_target_contributions = [table.get_value(second_target,i) for i in levels]
          sum_second_target = sum(second_target_contributions)

          sorted_levels = sorted(zip(second_target_contributions,levels), reverse=True)
          level_differences = [0.0] + [sorted_levels[i][0]-sorted_levels[i+1][0] for i in range(len(sorted_levels)-1)]
          second_target_top_dims = [j for i,j in sorted_levels[:level_differences.index(max(level_differences))]]
          second_target_top_dims_contribution = sum([i for i,j in sorted_levels[:level_differences.index(max(level_differences))]])
          second_target_bottom_dim = sorted_levels[-1][1]
          second_target_bottom_dim_contribution = sorted_levels[-1][0]

          second_target_percentages = [i*100.0/sum_second_target for i in second_target_contributions]
          best_second_target_index = second_target_contributions.index(max(second_target_contributions))
          worst_second_target_index = second_target_contributions.index(min(second_target_contributions))
          second_target_differences = [x-y for x,y in zip(levels_percentages,second_target_percentages)]
          if len(second_target_differences)>6:
              tops = 2
              bottoms = -2
          elif len(second_target_differences)>4:
              tops = 2
              bottoms = -1
          else:
              tops = 1
              bottoms = -1
          sorted_ = sorted(enumerate(second_target_differences), key = lambda x: x[1], reverse=True)
          best_second_difference_indices = [x for x,y in sorted_[:tops]]
          worst_second_difference_indices = [x for x,y in sorted_[bottoms:]]

          second_target_shares = [x*100.0/y for x,y in zip(second_target_contributions,level_counts)]
          max_second_target_shares = max(second_target_shares)
          best_second_target_share_index = [idx for idx,val in enumerate(second_target_shares) if val==max_second_target_shares]
          level_counts_threshold = sum(level_counts)*0.05/len(level_counts)
          min_second_target_shares = min([x for x,y in zip(second_target_shares,level_counts) if y>=level_counts_threshold])
          # worst_second_target_share_index = second_target_shares.index(min_second_target_shares)
          worst_second_target_share_index = [idx for idx,val in enumerate(second_target_shares) if val==min_second_target_shares]
          overall_second_percentage = sum_second_target*100.0/total

          targetCardDataDict = {}
          targetCardDataDict['target'] = target_dimension
          targetCardDataDict['colname'] = analysed_dimension
          targetCardDataDict['num_significant'] = len(significant_variables)
          targetCardDataDict['plural_colname'] = NarrativesUtils.pluralize(analysed_dimension)

          targetCardDataDict["blockSplitter"] = self._blockSplitter
          targetCardDataDict["binTargetCol"] = self._binTargetCol
          targetCardDataDict["binAnalyzedCol"] = self._binAnalyzedCol
          targetCardDataDict['highlightFlag'] = self._highlightFlag
          targetCardDataDict['levels'] = levels

          data_dict = {}
          data_dict['best_second_difference'] = best_second_difference_indices ##these changed
          data_dict['worst_second_difference'] = worst_second_difference_indices
          data_dict['best_top_difference']=best_top_difference_indices
          data_dict['worst_top_difference'] = worst_top_difference_indices
          data_dict['levels_percentages'] = levels_percentages
          data_dict['top_target_percentages'] = top_target_percentages
          data_dict['second_target_percentages'] = second_target_percentages
          data_dict['levels'] = levels
          data_dict['best_top_share'] = best_top_target_share_index
          data_dict['worst_top_share'] = worst_top_target_share_index
          data_dict['best_second_share'] = best_second_target_share_index
          data_dict['worst_second_share'] = worst_second_target_share_index
          data_dict['top_target_shares'] = top_target_shares
          data_dict['second_target_shares'] = second_target_shares
          data_dict['overall_second'] = overall_second_percentage
          data_dict['overall_top'] = overall_top_percentage

          data_dict['num_significant'] = len(significant_variables)
          data_dict['colname'] = analysed_dimension
          data_dict['plural_colname'] = NarrativesUtils.pluralize(analysed_dimension)
          data_dict['target'] = target_dimension
          data_dict['top_levels'] = top_dims
          data_dict['top_levels_percent'] = round(top_dims_contribution*100.0/total,1)
          data_dict['bottom_level'] = bottom_dim
          data_dict['bottom_levels'] = bottom_dims
          data_dict['bottom_level_percent'] = round(bottom_dim_contribution*100/sum(level_counts),2)
          data_dict['second_target']=second_target
          data_dict['second_target_top_dims'] = second_target_top_dims
          data_dict['second_target_top_dims_contribution'] = second_target_top_dims_contribution*100.0/sum(second_target_contributions)
          data_dict['second_target_bottom_dim']=second_target_bottom_dim
          data_dict['second_target_bottom_dim_contribution']=second_target_bottom_dim_contribution
          data_dict['best_second_target'] = levels[best_second_target_index]
          data_dict['best_second_target_count'] = second_target_contributions[best_second_target_index]
          data_dict['best_second_target_percent'] = round(second_target_contributions[best_second_target_index]*100.0/sum(second_target_contributions),2)
          data_dict['worst_second_target'] = levels[worst_second_target_index]
          data_dict['worst_second_target_percent'] = round(second_target_contributions[worst_second_target_index]*100.0/sum(second_target_contributions),2)

          data_dict['top_target']=top_target
          data_dict['top_target_top_dims'] = top_target_top_dims
          data_dict['top_target_top_dims_contribution'] = top_target_top_dims_contribution*100.0/sum(top_target_contributions)
          data_dict['top_target_bottom_dim']=top_target_bottom_dim
          data_dict['top_target_bottom_dim_contribution']=top_target_bottom_dim_contribution
          data_dict['best_top_target'] = levels[best_top_target_index]
          data_dict['best_top_target_count'] = top_target_contributions[best_top_target_index]
          data_dict['best_top_target_percent'] = round(top_target_contributions[best_top_target_index]*100.0/sum(top_target_contributions),2)
          data_dict['worst_top_target'] = levels[worst_top_target_index]
          data_dict['worst_top_target_percent'] = round(top_target_contributions[worst_top_target_index]*100.0/sum(top_target_contributions),2)

          data_dict["blockSplitter"] = self._blockSplitter
          data_dict["binTargetCol"] = self._binTargetCol
          data_dict["binAnalyzedCol"] = self._binAnalyzedCol
          data_dict['highlightFlag'] = self._highlightFlag


          ###############
          #     CARD1   #
          ###############

          print "self._binTargetCol & self._binAnalyzedCol : ", self._binTargetCol, self._binAnalyzedCol
          if (self._binTargetCol == True & self._binAnalyzedCol == False):
              print "Only Target Column is Binned, : ", self._binTargetCol
              output = NarrativesUtils.block_splitter(NarrativesUtils.get_template_output(self._base_dir,'card1_binned_target.html',data_dict),self._blockSplitter,highlightFlag=self._highlightFlag)
          elif (self._binTargetCol == True & self._binAnalyzedCol == True):
              print "Target Column and IV is Binned : ", self._binTargetCol, self._binAnalyzedCol
              output = NarrativesUtils.block_splitter(NarrativesUtils.get_template_output(self._base_dir,'card1_binned_target_and_IV.html',data_dict),self._blockSplitter,highlightFlag=self._highlightFlag)
          else:
              output = NarrativesUtils.block_splitter(NarrativesUtils.get_template_output(self._base_dir,'card1.html',data_dict),self._blockSplitter,highlightFlag=self._highlightFlag)

          targetDimCard1Data = []
          targetDimcard1Heading = '<h3>Relationship between '+ self._target_dimension + '  and '+self._analysed_dimension+"</h3>"

          toggledata = ToggleData()

          targetDimTable1Data = self.generate_card1_table1()
          targetDimCard1Table1 = TableData()
          targetDimCard1Table1.set_table_type("heatMap")
          targetDimCard1Table1.set_table_data(targetDimTable1Data)
          toggledata.set_toggleon_data({"data":{"tableData":targetDimTable1Data,"tableType":"heatMap"},"dataType":"table"})

          targetDimTable2Data = self.generate_card1_table2()
          targetDimCard1Table2 = TableData()
          targetDimCard1Table2.set_table_type("normal")
          table2Data = targetDimTable2Data["data1"]
          table2Data = [innerList[1:] for innerList in table2Data if innerList[0].strip() != ""]
          targetDimCard1Table2.set_table_data(table2Data)

          toggledata.set_toggleoff_data({"data":{"tableData":table2Data,"tableType":"heatMap"},"dataType":"table"})

          targetDimCard1Data.append(HtmlData(data=targetDimcard1Heading))
          targetDimCard1Data.append(toggledata)
          targetDimCard1Data += output

          self._card1.set_card_data(targetDimCard1Data)
          self._card1.set_card_name("{}: Relationship with {}".format(self._analysed_dimension,self._target_dimension))

          ###############
          #     CARD2   #
          ###############

          if self._appid == None:
 
              key_factors = ''
              num_key_factors = len(self._second_level_dimensions)

              if len(self._second_level_dimensions)==5:
                  key_factors = ', '.join(self._second_level_dimensions[:4]) + ' and ' + self._second_level_dimensions[4]
              elif len(self._second_level_dimensions)==4:
                  key_factors = ', '.join(self._second_level_dimensions[:3]) + ' and ' + self._second_level_dimensions[3]
              elif len(self._second_level_dimensions)==3:
                  key_factors = ', '.join(self._second_level_dimensions[:2]) + ' and ' + self._second_level_dimensions[2]
              elif len(self._second_level_dimensions)==2:
                  key_factors = ' and '.join(self._second_level_dimensions)
              elif len(self._second_level_dimensions)==1:
                  key_factors = self._second_level_dimensions[0]

              targetCardDataDict['num_key_factors'] = num_key_factors
              targetCardDataDict['key_factors'] = key_factors
              dict_for_test = {}
              for tupleObj in sorted_target_levels[:self._chiSquareLevelLimit]:
                  targetLevel = tupleObj[1]

                  targetCardDataDict['random_card2'] = random.randint(1,100)
                  targetCardDataDict['random_card4'] = random.randint(1,100)

                  second_target_contributions = [table.get_value(targetLevel,i) for i in levels]
                  sum_second_target = sum(second_target_contributions)

                  sorted_levels = sorted(zip(second_target_contributions,levels), reverse=True)
       
                  level_differences = [0.0] + [sorted_levels[i][0]-sorted_levels[i+1][0] for i in range(len(sorted_levels)-1)]
                  second_target_top_dims = [j for i,j in sorted_levels[:level_differences.index(max(level_differences))]]
                  second_target_top_dims_contribution = sum([i for i,j in sorted_levels[:level_differences.index(max(level_differences))]])
                  second_target_bottom_dim = sorted_levels[-1][1]
                  second_target_bottom_dim_contribution = sorted_levels[-1][0]

                  second_target_percentages = [i*100.0/sum_second_target for i in second_target_contributions]
                  best_second_target_index = second_target_contributions.index(max(second_target_contributions))
                  worst_second_target_index = second_target_contributions.index(min(second_target_contributions))
                  second_target_differences = [x-y for x,y in zip(levels_percentages,second_target_percentages)]
                  if len(second_target_differences)>6:
                      tops = 2
                      bottoms = -2
                  elif len(second_target_differences)>4:
                      tops = 2
                      bottoms = -1
                  else:
                      tops = 1
                      bottoms = -1
                  sorted_ = sorted(enumerate(second_target_differences), key = lambda x: x[1], reverse=True)
                  best_second_difference_indices = [x for x,y in sorted_[:tops]]
                  worst_second_difference_indices = [x for x,y in sorted_[bottoms:]]

                  second_target_shares = [x*100.0/y for x,y in zip(second_target_contributions,level_counts)]
                  max_second_target_shares = max(second_target_shares)
                  best_second_target_share_index = [idx for idx,val in enumerate(second_target_shares) if val==max_second_target_shares]
                  level_counts_threshold = sum(level_counts)*0.05/len(level_counts)
                  min_second_target_shares = min([x for x,y in zip(second_target_shares,level_counts) if y>=level_counts_threshold])
                  worst_second_target_share_index = [idx for idx,val in enumerate(second_target_shares) if val==min_second_target_shares]
                  overall_second_percentage = sum_second_target*100.0/total

                  # DataFrame for contribution calculation

                  df_second_target = self._data_frame.filter(col(self._target_dimension)==targetLevel).\
                                          filter(col(self._analysed_dimension)==second_target_top_dims[0]).\
                                          select(self._second_level_dimensions).toPandas()
                  df_second_dim = self._data_frame.filter(col(self._analysed_dimension)==second_target_top_dims[0]).\
                                      select(self._second_level_dimensions).toPandas()

                  # if self._chisquare_result.get_splits():
                  #     splits = self._chisquare_result.get_splits()
                  #     idx = self._chiSquareTable.get_bin_names(splits).index(second_target_top_dims[0])
                  #     idx1 = self._chiSquareTable.get_bin_names(splits).index(top_target_top_dims[0])
                  #     splits[len(splits)-1] = splits[len(splits)-1]+1
                  #     df_second_target = self._data_frame.filter(col(self._target_dimension)==targetLevel).\
                  #                         filter(col(self._analysed_dimension)>=splits[idx]).filter(col(self._analysed_dimension)<splits[idx+1]).\
                  #                         select(self._second_level_dimensions).toPandas()
                  #     df_second_dim = self._data_frame.filter(col(self._analysed_dimension)>=splits[idx]).\
                  #                     filter(col(self._analysed_dimension)<splits[idx+1]).\
                  #                     select(self._second_level_dimensions).toPandas()
                  # else:
                  #     df_second_target = self._data_frame.filter(col(self._target_dimension)==targetLevel).\
                  #                         filter(col(self._analysed_dimension)==second_target_top_dims[0]).\
                  #                         select(self._second_level_dimensions).toPandas()
                  #     df_second_dim = self._data_frame.filter(col(self._analysed_dimension)==second_target_top_dims[0]).\
                  #                     select(self._second_level_dimensions).toPandas()

                  # print self._data_frame.select('Sales').show()

                  distribution_second = []
                  for d in self._second_level_dimensions:

                    grouped = df_second_target.groupby(d).agg({d:'count'}).sort_values(d,ascending=False)
                    contributions = df_second_dim.groupby(d).agg({d:'count'})
                    contribution_index = list(contributions.index)
                    contributions_val = contributions[d].tolist()
                    contributions_list = dict(zip(contribution_index,contributions_val))
                    index_list = list(grouped.index)
                    grouped_list = grouped[d].tolist()
                    contributions_percent_list = [round(y*100.0/contributions_list[x],2) for x,y in zip(index_list,grouped_list)]
                    sum_ = grouped[d].sum()
                    diffs = [0]+[grouped_list[i]-grouped_list[i+1] for i in range(len(grouped_list)-1)]
                    max_diff = diffs.index(max(diffs))

                    index_txt=''
                    if max_diff == 1:
                        index_txt = index_list[0]
                    elif max_diff == 2:
                        index_txt = index_list[0]+'('+str(round(grouped_list[0]*100.0/sum_,1))+'%)' + ' and ' + index_list[1]+'('+str(round(grouped_list[1]*100.0/sum_,1))+'%)'
                    elif max_diff>2:
                        index_txt = 'including ' + index_list[0]+'('+str(round(grouped_list[0]*100.0/sum_,1))+'%)' + ' and ' + index_list[1]+'('+str(round(grouped_list[1]*100.0/sum_,1))+'%)'
                    distribution_second.append({'contributions':[round(i*100.0/sum_,2) for i in grouped_list[:max_diff]],\
                                            'levels': index_list[:max_diff],'variation':random.randint(1,100),\
                                            'index_txt': index_txt, 'd':d,'contributions_percent':contributions_percent_list})

                  targetCardDataDict['distribution_second'] = distribution_second
                  targetCardDataDict['second_target']=targetLevel
                  targetCardDataDict['second_target_top_dims'] = second_target_top_dims
                  targetCardDataDict['second_target_top_dims_contribution'] = second_target_top_dims_contribution*100.0/sum(second_target_contributions)
                  targetCardDataDict['second_target_bottom_dim']=second_target_bottom_dim
                  targetCardDataDict['second_target_bottom_dim_contribution']=second_target_bottom_dim_contribution
                  targetCardDataDict['best_second_target'] = levels[best_second_target_index]
                  targetCardDataDict['best_second_target_count'] = second_target_contributions[best_second_target_index]
                  targetCardDataDict['best_second_target_percent'] = round(second_target_contributions[best_second_target_index]*100.0/sum(second_target_contributions),2)
                  targetCardDataDict['worst_second_target'] = levels[worst_second_target_index]
                  targetCardDataDict['worst_second_target_percent'] = round(second_target_contributions[worst_second_target_index]*100.0/sum(second_target_contributions),2)

                  card2Data = []
                  targetLevelContributions = [table.get_value(targetLevel,i) for i in levels]
                  card2Heading = '<h3>Distribution of ' + self._target_dimension + ' (' + targetLevel + ') across ' + self._analysed_dimension+"</h3>"
                  chart,bubble = self.generate_distribution_card_chart(targetLevel, targetLevelContributions, levels, level_counts, total)
                  card2ChartData = NormalChartData(data=chart["data"])
                  card2ChartJson = ChartJson()
                  card2ChartJson.set_data(card2ChartData.get_data())
                  card2ChartJson.set_chart_type("combination")
                  card2ChartJson.set_types({"total":"bar","percentage":"line"})
                  card2ChartJson.set_legend({"total":"# of "+targetLevel,"percentage":"% of "+targetLevel})
                  card2ChartJson.set_axes({"x":"key","y":"total","y2":"percentage"})
                  card2ChartJson.set_label_text({"x":" ","y":"Count","y2":"Percentage"})
                  print "self._binTargetCol & self._binAnalyzedCol : ", self._binTargetCol, self._binAnalyzedCol
                  if (self._binTargetCol == True & self._binAnalyzedCol == False):
                      print "Only Target Column is Binned"
                      output2 = NarrativesUtils.block_splitter(NarrativesUtils.get_template_output(self._base_dir,'card2_binned_target.html',targetCardDataDict),self._blockSplitter)
                  elif (self._binTargetCol == True & self._binAnalyzedCol == True):
                      print "Target Column and IV is Binned"
                      output2 = NarrativesUtils.block_splitter(NarrativesUtils.get_template_output(self._base_dir,'card2_binned_target_and_IV.html',targetCardDataDict),self._blockSplitter)
                  else:
                      print "In Else, self._binTargetCol should be False : ", self._binTargetCol
                      output2 = NarrativesUtils.block_splitter(NarrativesUtils.get_template_output(self._base_dir,'card2.html',targetCardDataDict),self._blockSplitter)

                  card2Data.append(HtmlData(data=card2Heading))
                  statistical_info_array=[
                     ("Test Type","Chi-Square"),
                     ("Chi-Square statistic",str(round(self._chisquare_result.get_stat(),3))),
                     ("P-Value",str(round(self._chisquare_result.get_pvalue(),3))),
                     ("Inference","Chi-squared analysis shows a significant association between {} (target) and {}.".format(self._target_dimension,self._analysed_dimension) )
                     ]
                  statistical_info_array = NarrativesUtils.statistical_info_array_formatter(statistical_info_array)

                  card2Data.append(C3ChartData(data=card2ChartJson,info=statistical_info_array))
                  card2Data += output2
                  card2BubbleData = "<div class='col-md-6 col-xs-12'><h2 class='text-center'><span>{}</span><br /><small>{}</small></h2></div><div class='col-md-6 col-xs-12'><h2 class='text-center'><span>{}</span><br /><small>{}</small></h2></div>".format(bubble[0]["value"],bubble[0]["text"],bubble[1]["value"],bubble[1]["text"])
                  card2Data.append(HtmlData(data=card2BubbleData))
                  targetCard = NormalCard()
                  targetCard.set_card_data(card2Data)
                  targetCard.set_card_name("{} : Distribution of {}".format(self._analysed_dimension,targetLevel))
                  self._targetCards.append(targetCard)
                  dict_for_test[targetLevel] = targetCardDataDict
          out = {'data_dict' : data_dict,
                'target_dict':dict_for_test}  

          return out

    # def generate_card2_narratives(self):

    def generate_distribution_card_chart(self, __target, __target_contributions, levels, levels_count, total):
        chart = {}
        label = {'total' : '# of '+__target,
                  'percentage': '% of '+__target}
        label_text = {'x':self._analysed_dimension,
                      'y':'# of '+__target,
                      'y2':'% of '+__target,}
        data = {}
        data['total'] = dict(zip(levels,__target_contributions))
        __target_percentages = [x*100.0/y for x,y in zip(__target_contributions,levels_count)]
        data['percentage'] = dict(zip(levels,__target_percentages))
        chartData = []
        for val in zip(levels,__target_contributions,__target_percentages):
            chartData.append({"key":val[0],"total":val[1],"percentage":val[2]})
        # c3_data = [levels,__target_contributions,__target_percentages]
        chart_data = {'label':label,
                                'data':chartData}
        bubble_data1 = {}
        bubble_data2 = {}
        bubble_data1['value'] = str(round(max(__target_contributions)*100.0/sum(__target_contributions),1))+'%'
        m_index = __target_contributions.index(max(__target_contributions))
        bubble_data1['text'] = 'Overall '+__target+' comes from '+ levels[m_index]

        bubble_data2['value'] = str(round(max(__target_percentages),1))+'%'
        m_index = __target_percentages.index(max(__target_percentages))
        bubble_data2['text'] = levels[m_index] + ' has the highest rate of '+__target

        bubble_data = [bubble_data1,bubble_data2]
        return chart_data, bubble_data

    def generate_card1_table1(self):
        table_percent_by_column = self._chiSquareTable.table_percent_by_column
        column_two_values = self._chiSquareTable.column_two_values
        header_row = [self._analysed_dimension] + self._chiSquareTable.get_column_one_levels()
        all_columns = [column_two_values]+table_percent_by_column
        other_rows = zip(*all_columns)
        other_rows = [list(tup) for tup in other_rows]
        table_data = [header_row]+other_rows
        return table_data

    def generate_card1_table2(self):
        table = self._chiSquareTable.table
        table_percent = self._chiSquareTable.table_percent
        table_percent_by_row = self._chiSquareTable.table_percent_by_row
        table_percent_by_column = self._chiSquareTable.table_percent_by_column
        target_levels = self._chiSquareTable.get_column_one_levels()
        dim_levels = self._chiSquareTable.get_column_two_levels()

        header1 = [self._analysed_dimension] + target_levels + ['Total']
        header = ['State','Active','Churn','Total'] #TODO remove
        data = []
        data1=[['Tag']+header1]

        for idx, lvl in enumerate(dim_levels):
            first_row = ['Tag']+header
            col_2_vals = zip(*table)[idx]
            data2 = ['bold'] + [lvl] + list(col_2_vals) + [sum(col_2_vals)]

            dict_ = dict(zip(first_row, data2))
            data.append(dict_)
            data1.append(data2)

            col_2_vals = zip(*table_percent_by_column)[idx]
            data2 = [''] + ['As % within '+self._analysed_dimension] + list(col_2_vals) + [100.0]
            dict_ = dict(zip(first_row, data2))
            data.append(dict_)
            data1.append(data2)

            col_2_vals = zip(*table_percent_by_row)[idx]
            col_2_vals1 = zip(*table_percent)[idx]
            data2 = [''] + ['As % within '+self._target_dimension] + list(col_2_vals) + [round(sum(col_2_vals1),2)]
            dict_ = dict(zip(first_row, data2))
            data.append(dict_)
            data1.append(data2)
            # col_2_vals = zip(*table_percent)[idx]
            data2 = [''] + ['As % of Total'] + list(col_2_vals1) + [round(sum(col_2_vals1),2)]
            dict_ = dict(zip(first_row, data2))
            data.append(dict_)
            data1.append(data2)

        out = { 'header':header,
                'header1':header1,
                'data':data,
                'label':self._analysed_dimension,
                'data1':data1
              }
        return out
