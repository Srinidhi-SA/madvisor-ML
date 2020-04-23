from bi.narratives import utils as NarrativesUtils


class ChiSquareAnalysis:
    def __init__ (self, chisquare_result, target_dimension, analysed_dimension, significant_variables, num_analysed_variables,base_dir, appid=None):
        self._chisquare_result = chisquare_result
        self._target_dimension = target_dimension
        self._analysed_dimension = analysed_dimension
        self._significant_variables =  significant_variables
        self._num_analysed_variables = num_analysed_variables
        self._table = chisquare_result.get_contingency_table()
        self.card1 = {}
        self._base_dir = base_dir
        self._generate_narratives()

    def _generate_narratives(self):
        self._generate_narratives_card1()

    #TODO FIX first parameter should be self
    def _get_top_and_bottom_levels(level_names, level_contributions, tops = None, bottoms = None):
        sorted_ = sorted(zip(level_names,level_contributions,range(len(level_names))),reverse=True,key = lambda x: x[1])
        level_names,level_contributions, level_indices = zip(*sorted_)
        diffs = [0.0]+[level_contributions[i]-level_contributions[i+1] for i in range(len(level_names)-1)]
        if tops == None:
            tops = level_contributions.index(max(level_contributions))
        if bottoms == None:
            bottoms = -1
        return {'sorted_levels': level_names,
                'sorted_contributions': level_contributions,
                'sorted_indices': level_indices,
                'num_tops':tops}

    def _generate_narratives_card1(self):
        chisquare_result = self._chisquare_result
        target_dimension = self._target_dimension
        analysed_dimension = self._analysed_dimension
        significant_variables = self._significant_variables
        num_analysed_variables = self._num_analysed_variables
        table = self._table
        total = self._table.get_total()
        table_counts = self._table.table
        table_percent = self._table.table_percent
        #row is target dimension and column is analysed dimension when created
        table_percent_by_row = self._table.table_percent_by_row
        table_percent_by_column = self._table.table_percent_by_column
        target_distribution = self._table.get_row_total()
        analysed_dimension_distribution = self._table.get_column_total()
        sorted_ = sorted(enumerate(target_distribution), reverse=True, key = lambda x: x[1])
        top_target_index,second_top_target_index = [x[0] for x in sorted_[:2]]



        levels = self._table.get_column_two_levels()
        level_counts = self._table.get_column_total()
        levels_count_sum = sum(level_counts)
        levels_percentages = [i*100.0/levels_count_sum for i in level_counts]
        sorted_levels = sorted(zip(level_counts,levels),reverse=True)
        level_differences = [0.0]+[sorted_levels[i][0]-sorted_levels[i+1][0] for i in range(len(sorted_levels)-1)]
        top_dims = [j for i,j in sorted_levels[:level_differences.index(max(level_differences))]]
        top_dims_contribution = sum([i for i,j in sorted_levels[:level_differences.index(max(level_differences))]])
        bottom_dim = sorted_levels[-1][1]
        bottom_dim_contribution = sorted_levels[-1][0]

        target_levels = self._table.get_column_one_levels()
        target_counts = self._table.get_row_total()
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
        if len(top_target_differences)>4:
            tops = 2
            bottoms = -2
        elif len(top_target_differences)==4:
            tops = 2
            bottoms = -1
        else:
            tops = 1
            bottoms = -1
        sorted_ = sorted(enumerate(top_target_differences), key = lambda x: x[1],reverse=True)
        best_top_difference_indices = [x for x,y in sorted_[:tops]]
        worst_top_difference_indices = [x for x,y in sorted_[bottoms:]]

        top_target_shares = [x*100.0/y for x,y in zip(top_target_contributions,level_counts)]
        best_top_target_share_index = top_target_shares.index(max(top_target_shares))
        worst_top_target_share_index = top_target_shares.index(min(top_target_shares))
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
        sorted_ = sorted(enumerate(second_target_differences), key = lambda x: x[1])
        best_second_difference_indices = [x for x,y in sorted_[:tops]]
        worst_second_difference_indices = [x for x,y in sorted_[bottoms:]]

        second_target_shares = [x*100.0/y for x,y in zip(second_target_contributions,level_counts)]
        best_second_target_share_index = second_target_shares.index(max(second_target_shares))
        worst_second_target_share_index = second_target_shares.index(min(second_target_shares))
        overall_second_percentage = sum_second_target*100.0/total

        data_dict = {}
        data_dict['best_second_difference'] = best_second_difference_indices[0]
        data_dict['worst_second_difference'] = worst_second_difference_indices[0]
        data_dict['best_top_difference']=best_top_difference_indices[0]
        data_dict['worst_top_difference'] = worst_top_difference_indices[0]
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
        data_dict['target'] = target_dimension
        data_dict['top_levels'] = top_dims
        data_dict['top_levels_percent'] = NarrativesUtils.round_number(top_dims_contribution*100.0/total)
        data_dict['bottom_level'] = bottom_dim
        data_dict['bottom_level_percent'] = round(bottom_dim_contribution,2)
        data_dict['second_target']=second_target
        data_dict['second_target_top_dims'] = second_target_top_dims
        data_dict['second_target_top_dims_contribution'] = second_target_top_dims_contribution
        data_dict['second_target_bottom_dim']=second_target_bottom_dim
        data_dict['second_target_bottom_dim_contribution']=second_target_bottom_dim_contribution
        data_dict['best_second_target'] = levels[best_second_target_index]
        data_dict['best_second_target_count'] = second_target_contributions[best_second_target_index]
        data_dict['best_second_target_percent'] = round(second_target_contributions[best_second_target_index]*100.0/total,2)
        data_dict['worst_second_target'] = levels[worst_second_target_index]
        data_dict['worst_second_target_percent'] = round(second_target_contributions[worst_second_target_index]*100.0/total,2)

        data_dict['top_target']=top_target
        data_dict['top_target_top_dims'] = top_target_top_dims
        data_dict['top_target_top_dims_contribution'] = top_target_top_dims_contribution
        data_dict['top_target_bottom_dim']=top_target_bottom_dim
        data_dict['top_target_bottom_dim_contribution']=top_target_bottom_dim_contribution
        data_dict['best_top_target'] = levels[best_top_target_index]
        data_dict['best_top_target_count'] = top_target_contributions[best_top_target_index]
        data_dict['best_top_target_percent'] = round(top_target_contributions[best_top_target_index]*100.0/total,2)
        data_dict['worst_top_target'] = levels[worst_top_target_index]
        data_dict['worst_top_target_percent'] = round(top_target_contributions[worst_top_target_index]*100.0/total,2)


        output = NarrativesUtils.paragraph_splitter(NarrativesUtils.get_template_output(self._base_dir,'card1.html',data_dict))
        self.card1['heading'] = 'Relationship between '+ self._target_dimension + '  and '+self._analysed_dimension
        self.card1['paragraphs'] = output
        self.card1['chart']=[]
        self.card1['heat_map']=self._table
        self.generate_card1_chart()

        # self.card2['heading']='Distribution of ' + self._target_dimension + ' (' + second_target + ') across ' + self._analysed_dimension
        # chart,bubble=self.generate_distribution_card_chart(top_target, top_target_contributions, levels, level_counts, total)
        # self.card2['chart'] = chart
        # self.card2['bubble_data'] = bubble
        # output2 = NarrativesUtils.paragraph_splitter(NarrativesUtils.get_template_output(self._base_dir,'card2.html',data_dict))
        # self.card2['paragraphs'] = output2

        # self.card4['heading']='Distribution of ' + self._target_dimension + ' (' + top_target + ') across ' + self._analysed_dimension
        # chart,bubble=self.generate_distribution_card_chart(second_target, second_target_contributions, levels, level_counts, total)
        # self.card4['chart'] = chart
        # self.card4['bubble_data'] = bubble
        # output4 = NarrativesUtils.paragraph_splitter(NarrativesUtils.get_template_output(self._base_dir,'card4.html',data_dict))
        # self.card4['paragraphs'] = output4

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
        chart_data = {'label':label,
                                'data':data}
        bubble_data1 = {}
        bubble_data2 = {}
        bubble_data1['value'] = str(NarrativesUtils.round_number(max(__target_contributions)*100.0/total,2))+'%'
        m_index = __target_contributions.index(max(__target_contributions))
        bubble_data1['text'] = 'Overall '+__target+' comes from '+ levels[m_index]

        bubble_data2['value'] = NarrativesUtils.round_number(max(__target_percentages),2)+'%'
        m_index = __target_percentages.index(max(__target_percentages))
        bubble_data2['text'] = levels[m_index] + ' has the highest rate of '+__target

        bubble_data = [bubble_data1,bubble_data2]
        return chart_data, bubble_data

    def generate_card1_chart(self):
        table = self._table.table
        table_percent = self._table.table_percent
        table_percent_by_row = self._table.table_percent_by_row
        table_percent_by_column = self._table.table_percent_by_column
        target_levels = self._table.get_column_one_levels()
        dim_levels = self._table.get_column_two_levels()

        header1 = [self._analysed_dimension] + target_levels + ['Total']
        header = ['State','Active','Churn','Total'] #TODO remove
        data = []

        for idx, lvl in enumerate(dim_levels):
            data1 = header+['Tag']

            col_2_vals = zip(*table)[idx]
            data2 = [lvl] + list(col_2_vals) + [sum(col_2_vals)] + ['bold']
            dict_ = dict(zip(data1, data2))
            data.append(dict_)

            col_2_vals = zip(*table_percent_by_column)[idx]
            data2 = ['As % within '+self._analysed_dimension] + list(col_2_vals) + [100.0] + ['']
            dict_ = dict(zip(data1, data2))
            data.append(dict_)

            col_2_vals = zip(*table_percent_by_row)[idx]
            col_2_vals1 = zip(*table_percent)[idx]
            data2 = ['As % within '+self._target_dimension] + list(col_2_vals) + [round(sum(col_2_vals1),2)] + ['']
            dict_ = dict(zip(data1, data2))
            data.append(dict_)

            # col_2_vals = zip(*table_percent)[idx]
            data2 = ['As % of Total'] + list(col_2_vals1) + [round(sum(col_2_vals1),2)] + ['']
            dict_ = dict(zip(data1, data2))
            data.append(dict_)

        self.card1['chart']={'header':header1,
                            'data':data,
                            'label':self._analysed_dimension}
