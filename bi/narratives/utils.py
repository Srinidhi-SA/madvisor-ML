
"""
Utility functions to be used by various narrative objects
"""
import math
import random
import re
import time
from datetime import datetime

import enchant
import humanize
import jinja2
import numpy as np
import pattern
import pyspark.sql.functions as PysparkFN
from pyspark.sql import DataFrame
from pyspark.sql.types import *

from bi.common import HtmlData
from bi.common import utils as CommonUtils
from bi.common.decorators import accepts


# def round_number(num, digits=2, as_string=True):
#     millions = 0
#     thousands = 0
#     billions = 0
#     if(num//1000000000 > 0) and (as_string):
#         num = num/1000000000.0
#         billions =1
#         digits = 2
#     elif(num//1000000 > 0) and (as_string):
#         num = num/1000000.0
#         millions =1
#         digits = 2
#     elif(num//1000 > 0) and (as_string):
#         num = num/1000.0
#         thousands = 1
#         digits = 2
#     elif (abs(num)<1) and (num!=0):
#         digits = digits + int(abs(math.log(num,10)))
#     result = float(format(num, '0.%df' %(digits,)))
#     if as_string:
#         result = str(result)
#         decs = result[result.find('.'):]
#         result = result[:result.find('.')]
#         temp = len(str(result))
#         if temp>3:
#             for insertions in range(len(result)-3,0,-3):
#                 result = result[:insertions]+','+result[insertions:]
#         if billions ==1:
#             return result+decs+' Billion'
#         if millions ==1:
#             return result+decs+' Million'
#         if thousands == 1:
#             return result+decs+'K'
#         return result+decs
#     return result

def round_number(n, digits = 2, as_string = True):
    if type(n) != int:
        n = float(n)
    if abs(n)>1 and as_string:
        return humanize.intcomma(humanize.intword(n)).title()
    elif type(n)==float:
        return round(n,digits)
    elif (abs(n)<1) and (n!=0):
        digits = digits + int(abs(math.log(n,10)))
        return float(format(n, '0.%df' %(digits,)))
    else:
        return n

def paragraph_splitter(summary):
    output = []
    paragraphs = summary.split("PARASEPARATOR")
    for val in paragraphs:
        if val != "":
            temp = {"header":"","content":[""]}
            if "PARAHEADER" in val:
                parts = val.split("PARAHEADER")
                temp["header"] = parts[0]
                temp["content"] = [parts[1]]
            else:
                temp["content"] = [val]
            output.append(temp)
    return output

def block_splitter(summary,blockSplitter,highlightFlag=None):
    output = []
    paragraphs = summary.split(blockSplitter)
    for val in paragraphs:
        if highlightFlag != None:
            if highlightFlag in val:
                highlightBlocks = val.split(highlightFlag)
                for text in highlightBlocks:
                    if text.strip() != "":
                        htmlObj = HtmlData(data=text)
                        htmlObj.set_class_tag("highlight")
                        output.append(htmlObj)
            else:
                output.append(HtmlData(data=val))
        else:
            output.append(HtmlData(data=val))
    return output

def clean_narratives(output):
    output = re.sub('\n',' ',output)
    output = re.sub(' +',' ',output)
    output = re.sub(' ,',',',output)
    output = re.sub(' \.','.',output)
    output = re.sub('\( ','(',output)
    return output

# def get_template_output(base_dir, template_file, data_dict):
#     templateLoader = jinja2.FileSystemLoader( searchpath=base_dir)
#     templateEnv = jinja2.Environment( loader=templateLoader )
#     templateEnv.filters['round_number'] = round_number
#     templateEnv.filters['intcomma'] = humanize.intcomma
#     templateEnv.filters['pluralize']=pluralize
#     template = templateEnv.get_template(template_file)
#     output = template.render(data_dict)
#     return clean_narratives(output)

def get_template_output(base_dir, template_file, data_dict):
    templateEnv = jinja2.Environment(loader=jinja2.PackageLoader('bi','templates'))
    templateEnv.filters['round_number'] = round_number
    templateEnv.filters['intcomma'] = humanize.intcomma
    templateEnv.filters['pluralize']=pluralize
    template = templateEnv.get_template(base_dir+template_file)
    output = template.render(data_dict)
    return clean_narratives(output)

def clean_result_text(text):
    return str.replace("\n", "")

def get_plural_word(text):
    d = enchant.Dict("en_US")
    if text == text.upper():
        plural = text.lower()
        plural = pattern.en.pluralize(plural)
        if d.check(plural):
            plural = plural.upper()
        else:
            plural = text
    elif text == text.title():
        plural = text.lower()
        plural = pattern.en.pluralize(plural)
        if d.check(plural):
            plural = plural.title()
        else:
            plural = text
    else:
        plural = pattern.en.pluralize(text)
        if not d.check(plural):
            plural = text
    return plural

def pluralize(text):
    matches=[m.start() for m in re.finditer('[^a-zA-Z]', text)]
    if(len(matches)>0):
        br = matches[-1]+1
        text = text[:br]+get_plural_word(text[br:])
    else:
        text = get_plural_word(text)
    return text


def parse_leaf_name(name):
    return name[9:]

def check_leaf_node(node):
    if len(node['children']) == 1:
        return parse_leaf_name(node['children'][0]['name'])
    else:
        return False

def get_leaf_nodes(node):
    leaves = []
    leaf_node = check_leaf_node(node)
    if leaf_node != False:
        leaves += [leaf_node]
        return leaves
    else:
        for child_node in node['children']:
            leaves += get_leaf_nodes(child_node)
        return leaves

def generate_rule_text(rule_path_list,separator):
    return separator.join(rule_path_list[:-1])

def get_rules_dictionary(rules):
    key_dimensions = {}
    key_measures = {}
    rules_list = re.split(r',\s*(?![^()]*\))',rules)
    for rx in rules_list:
        if ' <= ' in rx:
            var,limit = re.split(' <= ',rx)
            if not key_measures.has_key(var):
                key_measures[var] ={}
            key_measures[var]['upper_limit'] = limit
        elif ' > ' in rx:
            var,limit = re.split(' > ',rx)
            if not key_measures.has_key(var):
                key_measures[var] = {}
            key_measures[var]['lower_limit'] = limit
        elif ' not in ' in rx:
            var,levels = re.split(' not in ',rx)
            if not key_dimensions.has_key(var):
                key_dimensions[var]={}
            key_dimensions[var]['not_in'] = levels
        elif ' in ' in rx:
            var,levels = re.split(' in ',rx)
            if not key_dimensions.has_key(var):
                key_dimensions[var]={}
            key_dimensions[var]['in'] = levels
    return [key_dimensions,key_measures]

def generate_leaf_rule_dict(rule_list,separator):
    out = {}
    leaf_list = list(set([x[-1] for x in rule_list]))
    for leaf in leaf_list:
        out[leaf] = [generate_rule_text(x,separator) for x in rule_list if x[-1] == leaf]
    return out

def generate_condensed_rule_dict(rule_list):
    out = {}
    leaf_list = list(set([x[-1] for x in rule_list]))
    for leaf in leaf_list:
        out[leaf] = [",".join(x) for x in rule_list if x[-1] == leaf]
    return out

def flatten_rules(result_tree, current_rule_list=None, all_rules=None):
    if current_rule_list is None:
        current_rule_list = []
    if all_rules is None:
        all_rules = []
    if len(result_tree) == 1:
        current_rule_list.append(parse_leaf_name(result_tree[0]['name']))
        all_rules.append(current_rule_list)
        return
    for val in result_tree:
        new_rule_list = current_rule_list[:]
        new_rule_list.append(val['name'])
        flatten_rules(val['children'], new_rule_list, all_rules)
    return all_rules

def return_template_output(base_dir,filename,data_dict):
    """
    base_dir => path to the folder where templates are stored.
    filename => template file name.
    data_dict => dictionary containing variables used in template file as key and their corresponding values.

    Returns object is the generated sentence
    """
    templateLoader = jinja2.FileSystemLoader( searchpath=base_dir)
    templateEnv = jinja2.Environment( loader=templateLoader )
    template = templateEnv.get_template(filename)
    output = template.render(data_dict)
    return output

def get_bin_names (splits):
    bin_names = []
    start = splits[0]
    for i in splits[1:]:
        bin_names.append(str(start) + ' to ' + str(i))
        start = i
    return bin_names


def longestRun(s):
    output = {"P":None,"N":None}
    if len(s) == 0: return output
    pos = []
    neg = []
    for x,y in zip(s,s[1:]):
        if x == y and x == "P":
            pos.append("*")
        else:
            pos.append(' ')
        if x == y and x == "N":
            neg.append("*")
        else:
            neg.append(' ')
    posruns = ''.join(pos)
    negruns = ''.join(neg)
#     posruns = ''.join('*' if x == y and x == "P" else ' ' for x,y in zip(s,s[1:]))
    starStrings = posruns.split()
    if len(starStrings) == 0:
        output["P"] = 1
        return output
    output["P"] = 1 + max(len(stars) for stars in starStrings)

    starStrings = negruns.split()
    if len(starStrings) == 0:
        output["N"] = 1
        return output
    output["N"] = 1 + max(len(stars) for stars in starStrings)
    return output

def accumu(lis):
    total = 0
    for x in lis:
        total += x
        yield total

def continuous_streak(aggData, direction="increase"):
    data = aggData.T.to_dict().values()
    if len(data) < 2:
        return len(data)
    else:
        start, streaks = -1, []
        for idx, (x, y) in enumerate(zip(data, data[1:])):
            if direction == "increase":
                if x['value'] > y['value']:
                    # streaks.append(idx - start)
                    streaks.append(data[start+1:idx+1])
                    start = idx
            elif direction == "decrease":
                if x['value'] < y['value']:
                    # streaks.append(idx - start)
                    streaks.append(data[start+1:idx+1])
                    start = idx
        else:
            # streaks.append(idx - start + 1)
            streaks.append(data[start+1:idx+1])

        return streaks

def get_max_min_stats(df,dataLevel,trend = "positive", stat_type = "percentage"):
    output = {}
    if stat_type == "percentage":
        col = "perChange"
    elif stat_type == "absolute":
        col = "value"
    if trend == "positive":
        index = df[col].argmax()
    elif trend == "negative":
        index = df[col].argmin()
    if dataLevel == "day":
        period = str(df["key"][index])
    else:
        period = df["year_month"][index]
    if stat_type == "percentage":
        change = str(abs(round(df[col][index],2)))+"%"
    elif stat_type == "absolute":
        change = str(round(df[col][index],2))
    if index != 0:
        changeValues = (df["value"][index-1],df["value"][index])
    else:
        changeValues = (0,df["value"][index])
    if trend == "positive":
        output = {"increase":"Largest ("+stat_type.title()+")","period":period,"increased_by":change,"range":str(changeValues[0])+" to "+str(changeValues[1])}
    else:
        output = {"decrease":"Largest ("+stat_type.title()+")","period":period,"decreased_by":change,"range":str(changeValues[0])+" to "+str(changeValues[1])}
    return output

def get_streak_data(df,trendString,maxRuns,trend,dataLevel):
    output = {}
    if trend == "positive":
        streak_start_index = trendString.index("P"*maxRuns["P"])
        if streak_start_index != 0:
            streak_start_index = streak_start_index-1
        streak_end_index = streak_start_index + maxRuns["P"]
        # print streak_start_index,streak_end_index
        if streak_end_index == df.shape[0]:
            streak_end_index = streak_end_index-1
    else:
        streak_start_index = trendString.index("P"*maxRuns["P"])
        if streak_start_index != 0:
            streak_start_index = streak_start_index-1
        streak_end_index = streak_start_index + maxRuns["P"]
        if streak_end_index == df.shape[0]:
            streak_end_index = streak_end_index-1
    end_streak_value = round(df["value"][streak_end_index],2)
    start_streak_value = round(df["value"][streak_start_index],2)
    if dataLevel == "day":
        streak_end_month = str(df.iloc[streak_end_index]["key"])
        streak_start_month = str(df.iloc[streak_start_index]["key"])
    elif dataLevel == "month":
        streak_end_month = df.iloc[streak_end_index]["year_month"]
        streak_start_month = df.iloc[streak_start_index]["year_month"]
    change = end_streak_value-start_streak_value
    streak_range = str(start_streak_value)+" to "+str(end_streak_value)

    output = ["Longest Streak",streak_start_month+" to "+streak_end_month,change,streak_range]
    if trend == "positive":
        output = {"increase":"Longest Streak","period":streak_start_month+" to "+streak_end_month,"increased_by":change,"range":streak_range}
    else:
        output = {"decrease":"Longest Streak","period":streak_start_month+" to "+streak_end_month,"decreased_by":change,"range":streak_range}
    return output

# def calculate_dimension_contribution(level_cont):
#     data_dict = {}
#     dimension_contribution = []
#     for k,v in level_cont["summary"].items():
#         for x in v:
#             if not isinstance(v[x]['growth'], float):
#                 v[x]['growth'] = 0.0
#             elif math.isinf(v[x]['growth']) or math.isnan(v[x]['growth']):
#                 v[x]['growth'] = 0.0
#         max_level = max(v,key=lambda x: v[x]["growth"])
#         while v[max_level]["contribution"] < 5:
#             del(v[max_level])
#             if len(v.keys()) > 1:
#                 max_level = max(v,key=lambda x: v[x]["growth"])
#             else:
#                 max_level = None
#                 break
#         if max_level != None:
#             dimension_contribution.append((k,max_level,v[max_level]["growth"],v[max_level]["contribution"]))
#
#     ordered_dim_contribution = sorted(dimension_contribution,key=lambda x:x[2],reverse=True)
#     data_dict["HighestSigDimension"] = ordered_dim_contribution[0][0]
#     data_dict["SecondHighestSigDimension"] = ordered_dim_contribution[1][0]
#     k1 = level_cont["summary"][data_dict["HighestSigDimension"]]
#     sorted_k1 = sorted(k1.items(),key = lambda x: x[1]["growth"],reverse=True)
#     k2 = level_cont["summary"][data_dict["SecondHighestSigDimension"]]
#     sorted_k2 = sorted(k1.items(),key = lambda x: x[1]["growth"],reverse=True)
#     data_dict["HighestSigDimensionL1"] = [sorted_k1[0][0],sorted_k1[0][1]["growth"]]
#     data_dict["HighestSigDimensionL2"] = [sorted_k1[1][0],sorted_k1[1][1]["growth"]]
#     data_dict["SecondHighestSigDimensionL1"] = [sorted_k2[0][0],sorted_k2[0][1]["growth"]]
#     data_dict["SecondHighestSigDimensionL2"] = [sorted_k2[1][0],sorted_k2[1][1]["growth"]]
#
#     for k,v in level_cont["summary"].items():
#         min_level = max(v,key=lambda x: v[x]["growth"])
#         while v[min_level]["contribution"] < 5:
#             del(v[min_level])
#             if len(v.keys()) > 1:
#                 min_level = max(v,key=lambda x: v[x]["growth"])
#             else:
#                 min_level = None
#                 break
#         if min_level != None:
#             dimension_contribution.append((k,min_level,v[min_level]["growth"],v[min_level]["contribution"]))
#
#     ordered_dim_contribution = sorted(dimension_contribution,key=lambda x:x[2])
#     data_dict["negativeHighestSigDimension"] = ordered_dim_contribution[0][0]
#     data_dict["negativeSecondHighestSigDimension"] = ordered_dim_contribution[1][0]
#     k1 = level_cont["summary"][data_dict["negativeHighestSigDimension"]]
#     sorted_k1 = sorted(k1.items(),key = lambda x: x[1]["growth"])
#     k2 = level_cont["summary"][data_dict["negativeSecondHighestSigDimension"]]
#     sorted_k2 = sorted(k1.items(),key = lambda x: x[1]["growth"])
#     if len(sorted_k1) >= 2:
#         data_dict["negativeHighestSigDimensionL1"] = [sorted_k1[0][0],sorted_k1[0][1]["growth"]]
#         data_dict["negativeHighestSigDimensionL2"] = [sorted_k1[1][0],sorted_k1[1][1]["growth"]]
#     elif len(sorted_k1) ==1:
#         data_dict["negativeHighestSigDimensionL1"] = [sorted_k1[0][0],sorted_k1[0][1]["growth"]]
#         data_dict["negativeHighestSigDimensionL1"] = None
#     if len(sorted_k2) >=2:
#         data_dict["negativeSecondHighestSigDimensionL1"] = [sorted_k2[0][0],sorted_k2[0][1]["growth"]]
#         data_dict["negativeSecondHighestSigDimensionL2"] = [sorted_k2[1][0],sorted_k2[1][1]["growth"]]
#     elif len(sorted_k2) ==1:
#         data_dict["negativeSecondHighestSigDimensionL1"] = [sorted_k2[0][0],sorted_k2[0][1]["growth"]]
#         data_dict["negativeSecondHighestSigDimensionL1"] = None
#     return data_dict
def calculate_dimension_contribution(levelContObject):
    output = {"posGrowthArray":None,"negGrowthArray":None}
    dataArray= []
    for k,v in levelContObject.items():
        for k1,v1 in v.items():
            new_key = (k,k1)
            if v1["diff"] != None :
                dataArray.append((new_key, v1))
    decreasingDataArray = sorted(dataArray,key=lambda x:x[1]["diff"],reverse=True)
    increasingDataArray = sorted(dataArray,key=lambda x:x[1]["diff"],reverse=False)
    output["posGrowthArray"] = [x for x in decreasingDataArray if x[1]["growth"] != None and float(x[1]["growth"]) > 0][:2]
    output["negGrowthArray"] = [x for x in increasingDataArray if x[1]["growth"] != None and float(x[1]["growth"]) < 0][:2]
    return output

def calculate_level_contribution(sparkdf,columns,index_col,dateColDateFormat,value_col,max_time, meta_parser):
    """
    calculates level contribution dictionary for each level each column
    sample Dict = {
                "overall_avg":overall average",
                "excluding_avg":"average excluding the max_time",
                "minval":None,
                "maxval":None,
                "diff":",max val - excluding avg",
                "contribution":"percent contribution",
                "growth":None
                }

    """
    # print "index_col",index_col
    # print "dateColDateFormat",dateColDateFormat
    # print "value_col",value_col
    # print "max_time",max_time
    out = {}
    for column_name in columns:
        print "-"*100
        print "calculate_level_contribution for ",column_name
        data_dict = {
                    "overall_avg":None,
                    "excluding_avg":None,
                    "minval":None,
                    "maxval":None,
                    "diff":None,
                    "contribution":None,
                    "growth":None
                    }
        try:
            column_levels = meta_parser.get_unique_level_names(column_name)
        except:
            column_levels = [x[0] for x in sparkdf.select(column_name).distinct().collect()]
        out[column_name] = dict(zip(column_levels,[data_dict]*len(column_levels)))
        # st = time.time()
        pivotdf = sparkdf.groupBy(index_col).pivot(column_name).sum(value_col)
        # print "time for pivot",time.time()-st
        # pivotdf = pivotdf.na.fill(0)
        # pivotdf = pivotdf.withColumn('total', sum([pivotdf[col] for col in pivotdf.columns if col != index_col]))
        # st=time.time()
        # print "converting to pandas"
        k = pivotdf.toPandas()
        # print "time taken for pandas conversion of pivotdf",time.time()-st
        k["total"] = k.sum(axis=1)
        k[index_col] = k[index_col].apply(str)
        k["rank"] = k[index_col].apply(lambda x: datetime.strptime(x,dateColDateFormat) if x != 'None' else None)
        k = k.sort_values(by="rank", ascending=True)
        occurance_index = np.where(k[index_col] == max_time)
        # print "occurance_index",occurance_index
        # print "max_time",max_time
        if len(occurance_index[0]) > 0:
            max_index = occurance_index[0][0]
        else:
            max_index = None
        for level in column_levels:
            try:
                # print "calculations for level",level
                if level != None:
                    data_dict = {"overall_avg":None,"excluding_avg":None,"minval":None,"maxval":None,"diff":None,"contribution":None,"growth":None}
                    data_dict["contribution"] = float(np.nansum(k[level]))*100/np.nansum(k["total"])
                    data = list(k[level])
                    growth_data = [x for x in data if np.isnan(x) != True and x != 0]
                    data_dict["growth"] = (growth_data[-1]-growth_data[0])*100/growth_data[0]
                    k["percentLevel"] = (k[level]/k["total"])*100
                    data = list(k["percentLevel"])
                    data_dict["overall_avg"] = np.nanmean(data)
                    data_dict["maxval"] = np.nanmax(data)
                    data_dict["minval"] = np.nanmin(data)
                    if max_index:
                        del(data[max_index])
                    data_dict["excluding_avg"] = np.nanmean(data)
                    data_dict["diff"] = (data_dict["maxval"] - data_dict["excluding_avg"])*100/float(data_dict["excluding_avg"])
                    out[column_name][level] = data_dict
            except:
                pass
    return out

def get_level_cont_dict(level_cont):
    levelContributionSummary = level_cont
    output = []
    # k is the dimension name
    for k,valdict in levelContributionSummary.items():
        v = {k1:v1 for (k1,v1) in valdict.items() if v1["contribution"] >= 5}
        if len(v) == 0:
            print "#"*200
            print "all levels have contribution less than 5"
            v = valdict
        max_level = max(v,key=lambda x: v[x]["diff"])
        contribution_dict = {}
        for level,value in levelContributionSummary[k][max_level].items():
            contribution_dict[level] = value
            contribution_dict.update({"level":max_level})
        output.append(contribution_dict)
    out_dict = dict(zip(levelContributionSummary.keys(),output))
    out_data = {"category_flag":True}
    out_dict_without_none = dict((item,out_dict[item])for item in out_dict if out_dict[item]["diff"] is not None )
    if len(out_dict_without_none) >0:
        out_data["highest_contributing_variable"] = max(out_dict_without_none,key=lambda x:out_dict[x]["diff"])
        print "highest_contributing_variable",out_data["highest_contributing_variable"]
        if "category" in out_data["highest_contributing_variable"].lower():
            out_data["category_flag"] = False
        out_data["highest_contributing_level"] = out_dict[out_data["highest_contributing_variable"]]["level"]
        out_data["highest_contributing_level_increase"] = out_dict[out_data["highest_contributing_variable"]]["diff"]
        out_data["highest_contributing_level_range"] = str(round(out_dict[out_data["highest_contributing_variable"]]["maxval"],2))+" vis-a-vis "+str(round(out_dict[out_data["highest_contributing_variable"]]["excluding_avg"],2))
    else:
        out_data["highest_contributing_variable"] = None

    output = []
    for k,valdict in levelContributionSummary.items():
        v = {k1:v1 for (k1,v1) in valdict.items() if v1["contribution"] >= 5}
        if len(v) == 0:
            print "#"*200
            print "all levels have contribution less than 5"
            v = valdict
        min_level = min(v,key=lambda x: v[x]["diff"] if v[x]["diff"] != None else 9999999999999999999)
        t_dict = {}
        for k1,v1 in levelContributionSummary[k][min_level].items():
            t_dict[k1] = v1
            t_dict.update({"level":min_level})
        output.append(t_dict)
    out_dict = dict(zip(levelContributionSummary.keys(),output))
    # out_data["lowest_contributing_variable"] = min(out_dict,key=lambda x:out_dict[x]["diff"])
    out_dict_without_none = dict((item,out_dict[item])for item in out_dict if out_dict[item]["diff"] is not None )
    if len(out_dict_without_none) >0:
        out_data["lowest_contributing_variable"] = min(out_dict_without_none,key=lambda x:out_dict[x]["diff"])
        print "lowest_contributing_variable",out_data["lowest_contributing_variable"]
        out_data["lowest_contributing_level"] = out_dict[out_data["lowest_contributing_variable"]]["level"]
        out_data["lowest_contributing_level_decrease"] = out_dict[out_data["lowest_contributing_variable"]]["diff"]
        out_data["lowest_contributing_level_range"] = str(round(out_dict[out_data["lowest_contributing_variable"]]["minval"],2))+" vis-a-vis "+str(round(out_dict[out_data["lowest_contributing_variable"]]["excluding_avg"],2))
    else:
        out_data["lowest_contributing_variable"] = None
    return out_data

def calculate_bucket_data(grouped_data,dataLevel):
    print "calculating bucket data"
    df = grouped_data
    min_streak = 2
    max_streak = 9
    if df.shape[0]*0.3 < 9:
        max_streak = int(math.floor(df.shape[0]*0.3))
        if max_streak <= 2:
            max_streak = 2
    streak_range = range(min_streak,max_streak+1)
    max_dict = {}
    for val in streak_range:
        df[str(val)] = df["value"].rolling(val).sum()/val
        temp_dict = {}
        temp_dict["id_max"] = df[str(val)].idxmax()
        temp_dict["max_val"] = round(df.loc[temp_dict["id_max"],str(val)],2)

        if dataLevel == "day":
            start_id = temp_dict["id_max"]-val+1
            start_id = 0 if start_id < 0 else start_id
            temp_dict["start_streak"] = list(df["key"])[start_id]
            temp_dict["end_streak"] = df["key"][temp_dict["id_max"]]
        elif dataLevel == "month":
            start_id = temp_dict["id_max"]-val+1
            start_id = 0 if start_id < 0 else start_id
            temp_dict["start_streak"] = list(df["year_month"])[start_id]
            temp_dict["end_streak"] = df["year_month"][temp_dict["id_max"]]
        temp_dict["start_streak_value"] = df["value"][start_id]
        temp_dict["end_streak_value"] = df["value"][temp_dict["id_max"]]
        if temp_dict["id_max"]+1 <= len(df[str(val)]):
            temp_dict["contribution"] = df["value"].iloc[start_id:temp_dict["id_max"]+1].sum()
        else:
            start_id = 0 if start_id < 0 else start_id
            temp_dict["contribution"] = df["value"].iloc[start_id:len(df[str(val)])].sum()

        temp_dict["ratio"] = round(temp_dict["contribution"]*100/float(df[str(val)].sum()),2)
        temp_dict["average"] = df[str(val)].mean()
        max_dict[str(val)] = temp_dict
        # print max_dict
    return max_dict

def get_bucket_data_dict(bucket_dict):
    # max_bucket = max(max_dict,key = lambda x: max_dict[x]["max_val"])
    zip_list = []
    for k,v in bucket_dict.items():
        if v["max_val"] >= v["average"]:
            zip_list.append([int(k),v["max_val"]])
    zip_list = sorted(zip_list, key=lambda x:x[1],reverse=True)
    # zip_list = sorted(zip_list, key=lambda x:x[0],reverse=False)
    out = {}
    out["bucket_length"] = zip_list[0][0]
    key = str(zip_list[0][0])
    out["bucket_contribution"] = round(bucket_dict[key]["contribution"],2)
    out["bucket_start"] = bucket_dict[key]["start_streak"]
    out["bucket_end"] = bucket_dict[key]["end_streak"]
    # print "end_streak",bucket_dict[key]["end_streak"]
    out["bucket_start_value"] = bucket_dict[key]["start_streak_value"]
    out["bucket_end_value"] = bucket_dict[key]["end_streak_value"]
    out["bucket_duration"] = str(bucket_dict[key]["start_streak"])+" to "+str(bucket_dict[key]["end_streak"])
    ratio = bucket_dict[key]["ratio"]
    if ratio < 20:
        out["ratio_string"] = ""
    elif ratio > 20 and ratio <=30:
        out["ratio_string"] = "one fourth"
    elif ratio > 30 and ratio <=40:
        out["ratio_string"] = "one third"
    elif ratio > 40 and ratio <=55:
        out["ratio_string"] = "half"
    elif ratio > 55 and ratio <=70:
        out["ratio_string"] = "two third"
    elif ratio >70 and ratio <=80:
        out["ratio_string"] = "three fourth"
    else:
        out["ratio_string"] = str(ratio)
    # print out
    return out

# def get_level_cont_dict(level_cont):
#     dk = level_cont["summary"]
#     output = []
#     for k,v in dk.items():
#         level_list = v.keys()
#         max_level = max(v,key=lambda x: v[x]["diff"])
#         t_dict = {}
#         for k1,v1 in dk[k][max_level].items():
#             t_dict[k1] = v1
#             t_dict.update({"level":max_level})
#         output.append(t_dict)
#     out_dict = dict(zip(dk.keys(),output))
#     out_data = {}
#     out_data["highest_contributing_variable"] = max(out_dict,key=lambda x:out_dict[x]["diff"])
#     out_data["highest_contributing_level"] = out_dict[out_data["highest_contributing_variable"]]["level"]
#     out_data["highest_contributing_level_increase"] = out_dict[out_data["highest_contributing_variable"]]["diff"]
#     out_data["highest_contributing_level_range"] = str(out_dict[out_data["highest_contributing_variable"]]["max_avg"])+" vis-a-vis "+str(out_dict[out_data["highest_contributing_variable"]]["excluding_avg"])
#     output = []


def date_formats_mapping_dict():
    dateFormatConversionDict = {
        "mm/dd/YYYY":"%m/%d/%Y",
        "dd/mm/YYYY":"%d/%m/%Y",
        "YYYY/mm/dd":"%Y/%m/%d",
        "dd <month> YYYY":"%d %b,%Y",
        "%b-%y":"%b-%y"
    }
    return dateFormatConversionDict

def get_date_conversion_formats(self, primary_date,dateColumnFormatDict,requestedDateFormat):
    dateFormatConversionDict = date_formats_mapping_dict()
    if primary_date in dateColumnFormatDict.keys():
        existingDateFormat = dateColumnFormatDict[primary_date]
    else:
        existingDateFormat = None

    if requestedDateFormat != None:
        requestedDateFormat = dateFormatConversionDict[requestedDateFormat]
    else:
        requestedDateFormat = existingDateFormat

def streak_data(df,peak_index,low_index,percentage_change_column,value_column):
    dataDict = {}
    k = peak_index
    while k != -1 and df[percentage_change_column][k] >= 0:
        k = k-1
    # print "peak_index:",peak_index,"KK:",k
    l = low_index
    while l != -1 and df[percentage_change_column][l] < 0:
        l = l-1
    k = 0 if k == -1 else k
    l = 0 if l == -1 else l
    if peak_index - k > 0:
        dataDict["upStreakDuration"] = peak_index - k
    else:
        dataDict["upStreakDuration"] = 0
    if low_index - l > 0:
        dataDict["downStreakDuration"] = low_index - l
    else:
        dataDict["downStreakDuration"] = 0
    # print "STREAK"
    # print l,k
    # print dataDict["downStreakDuration"],dataDict["upStreakDuration"]
    if dataDict["downStreakDuration"] >=2 :
        dataDict["downStreakBeginMonth"] = df["year_month"][l]
        dataDict["downStreakBeginValue"] = df[value_column][l]
        dataDict["downStreakEndMonth"] = df["year_month"][l+dataDict["downStreakDuration"]]
        dataDict["downStreakEndValue"] = df[value_column][l+dataDict["downStreakDuration"]]
        dataDict["downStreakContribution"] = sum(df[value_column].iloc[l:low_index])*100/sum(df[value_column])
    if dataDict["upStreakDuration"] >=2 :
        dataDict["upStreakBeginMonth"] = df["year_month"][k]
        dataDict["upStreakBeginValue"] = df[value_column][k]
        dataDict["upStreakEndMonth"] = df["year_month"][k+dataDict["upStreakDuration"]]
        dataDict["upStreakEndValue"] = df[value_column][k+dataDict["upStreakDuration"]]
        dataDict["upStreakContribution"] = sum(df[value_column].iloc[k:peak_index])*100/sum(df[value_column])

    return dataDict


def get_significant_digit_settings(param):
    data = {"trend":1}
    if param in data:
        return data[param]
    else:
        return 2

def get_level_pivot(df,dataLevel,value_col,pivot_col,index_col=None):
    if index_col == None:
        if dataLevel == "day":
            index_col = "suggestedDate"
        elif dataLevel == "month":
            index_col = "year_month"
    pivotdf = df.groupBy(index_col).pivot(pivot_col).sum(value_col)
    if dataLevel == "day":
        pivotdf = pivotdf.orderBy("suggestedDate",ascending=True)
        pivotdf = pivotdf.withColumnRenamed(pivotdf.columns[0],"key")
        pivotdf = pivotdf.toPandas()
    elif dataLevel == "month":
        pivotdf = pivotdf.withColumn("suggestedDate",PysparkFN.udf(lambda x:datetime.strptime(x,"%b-%y") if x != None else None)("year_month"))
        pivotdf = pivotdf.orderBy("suggestedDate",ascending=True)
        pivotdf = pivotdf.withColumnRenamed("suggestedDate","key")
        pivotdf = pivotdf.toPandas()
        pivotdf["key"] = pivotdf["year_month"].apply(lambda x: datetime.strptime(x,"%b-%y").date() if x!= None else None)
    return pivotdf

@accepts(df=DataFrame,dataLevel=basestring,resultCol=basestring,analysistype=basestring)
def get_grouped_data_for_trend(df,dataLevel,resultCol,analysistype):
    if dataLevel == "day":
        if analysistype == "measure":
            grouped_data = df.groupBy("suggestedDate").agg({ resultCol : 'sum'})
        elif analysistype == "dimension":
            grouped_data = df.groupBy("suggestedDate").agg({ resultCol : 'count'})
        grouped_data = grouped_data.withColumnRenamed(grouped_data.columns[-1],"value")
        grouped_data = grouped_data.withColumn("year_month",PysparkFN.udf(lambda x:x.strftime("%b-%y") if x != None else None)("suggestedDate"))
        grouped_data = grouped_data.orderBy("suggestedDate",ascending=True)
        grouped_data = grouped_data.withColumnRenamed(grouped_data.columns[0],"key")
        grouped_data = grouped_data.toPandas()
    elif dataLevel == "month":
        if analysistype == "measure":
            grouped_data = df.groupBy("year_month").agg({ resultCol : 'sum'})
        elif analysistype == "dimension":
            grouped_data = df.groupBy("year_month").agg({ resultCol : 'count'})
        grouped_data = grouped_data.withColumnRenamed(grouped_data.columns[-1],"value")
        grouped_data = grouped_data.withColumn("suggestedDate",PysparkFN.udf(lambda x:datetime.strptime(x,"%b-%y") if x != None else None)("year_month"))
        grouped_data = grouped_data.orderBy("suggestedDate",ascending=True)
        grouped_data = grouped_data.withColumnRenamed("suggestedDate","key")
        grouped_data = grouped_data.select(["key","value","year_month"]).toPandas()
        grouped_data["key"] = grouped_data["year_month"].apply(lambda x: datetime.strptime(x,"%b-%y").date() if x != None else None)
    return grouped_data

@accepts(df=DataFrame,dataLevel=basestring,resultCol=basestring)
def get_grouped_count_data_for_dimension_trend(df,dataLevel,resultCol):
    if dataLevel == "day":
        overall_count = df.groupBy("suggestedDate").agg({ resultCol : 'count'})
        overall_count = overall_count.withColumnRenamed(overall_count.columns[-1],"totalCount")
        overall_count = overall_count.orderBy("suggestedDate",ascending=True)
        overall_count = overall_count.withColumnRenamed("suggestedDate","key")
        overall_count = overall_count.toPandas()
    elif dataLevel == "month":
        overall_count = df.groupBy("year_month").agg({ resultCol : 'count'})
        overall_count = overall_count.withColumnRenamed(overall_count.columns[-1],"totalCount")
        overall_count = overall_count.withColumn("suggestedDate",PysparkFN.udf(lambda x:datetime.strptime(x,"%b-%y") if x != None else None)("year_month"))
        overall_count = overall_count.orderBy("suggestedDate",ascending=True)
        overall_count = overall_count.withColumnRenamed("suggestedDate","key")
        overall_count = overall_count.select(["key","totalCount","year_month"]).toPandas()
        overall_count["key"] = overall_count["year_month"].apply(lambda x: datetime.strptime(x,"%b-%y").date() if x != None else None)
        overall_count = overall_count.loc[:,[c for c in overall_count.columns if c != "year_month"]]
    return overall_count

@accepts(selectedDateColumns=(list,tuple),timeDimensionCols=(list,tuple),dateColumnFormatDict=dict,dateFormatConversionDict=dict,requestedDateFormat=(None,basestring))
def check_date_column_formats(selectedDateColumns,timeDimensionCols,dateColumnFormatDict,dateFormatConversionDict,requestedDateFormat):
    dateFormatDetected = False
    trendOnTdCol = False
    existingDateFormat = None
    requestedDateFormat = None
    suggested_date_column = None
    if selectedDateColumns != None and len(selectedDateColumns) > 0:
        suggested_date_column = selectedDateColumns[0]
        existingDateFormat = None
        if suggested_date_column not in timeDimensionCols:
            if suggested_date_column in dateColumnFormatDict:
                existingDateFormat = dateColumnFormatDict[suggested_date_column]
                dateFormatDetected = True
            if requestedDateFormat != None:
                requestedDateFormat = dateFormatConversionDict[requestedDateFormat]
            else:
                requestedDateFormat = existingDateFormat
        else:
            trendOnTdCol = True
            existingDateFormat = "%Y-%m-%d"
            dateFormatDetected = True
            if requestedDateFormat != None:
                requestedDateFormat = dateFormatConversionDict[requestedDateFormat]
            else:
                requestedDateFormat = existingDateFormat
    else:
        if timeDimensionCols != None:
            if len(timeDimensionCols) > 0:
                trendOnTdCol = True
                suggested_date_column = timeDimensionCols[0]
                existingDateFormat = "%Y-%m-%d"
                dateFormatDetected = True
                if requestedDateFormat != None:
                    requestedDateFormat = dateFormatConversionDict[requestedDateFormat]
                else:
                    requestedDateFormat = existingDateFormat


    output = {
        "dateFormatDetected":dateFormatDetected,
        "requestedDateFormat":requestedDateFormat,
        "existingDateFormat":existingDateFormat,
        "trendOnTdCol":trendOnTdCol,
        "suggestedDateColumn":suggested_date_column}


    return output

@accepts(df=DataFrame,existingDateFormat=(basestring,None),dateColToBeUsedForAnalysis=basestring,trendOnTdCol=bool)
def calculate_data_range_stats(df,existingDateFormat,dateColToBeUsedForAnalysis,trendOnTdCol):
    """
    dateColToBeUsedForAnalysis: date column selected for analysis
    """

    if trendOnTdCol == False:
        date_format = existingDateFormat
        print "date_format : ", date_format
        string_to_date = PysparkFN.udf(lambda x: datetime.strptime(x,date_format) if x != None else None, DateType())
        date_to_month_year = PysparkFN.udf(lambda x: datetime.strptime(x,date_format).strftime("%b-%y") if x != None else None, StringType())
        df = df.withColumn("suggestedDate", string_to_date(dateColToBeUsedForAnalysis))
        df = df.withColumn("year_month", date_to_month_year(dateColToBeUsedForAnalysis))
        df = df.orderBy(["suggestedDate"],ascending=[True])
        df = df.withColumn("_id_", PysparkFN.monotonically_increasing_id())
    else:
        df = df.withColumn("suggestedDate", PysparkFN.udf(lambda x:x.date() if x != None else None,DateType())(dateColToBeUsedForAnalysis))
        df = df.withColumn("year_month", PysparkFN.udf(lambda x:x.date().strftime("%b-%y") if x != None else None,StringType())(dateColToBeUsedForAnalysis))
        df = df.orderBy(["suggestedDate"],ascending=[True])
        df = df.withColumn("_id_", PysparkFN.monotonically_increasing_id())

    dfForRange = df.select(["_id_","suggestedDate"]).na.drop(subset=["suggestedDate"])
    first_date = dfForRange.select("suggestedDate").first()[0]
    #####  This is a Temporary fix
    try:
        print "TRY BLOCK STARTED"
        id_max = dfForRange.select(PysparkFN.max("_id_")).first()[0]
        last_date = dfForRange.where(PysparkFN.col("_id_") == id_max).select("suggestedDate").first()[0]
    except:
        print "ENTERING EXCEPT BLOCK"
        pandas_df = dfForRange.select(["suggestedDate"]).distinct().toPandas()
        pandas_df.sort_values(by="suggestedDate",ascending=True,inplace=True)
        last_date = pandas_df["suggestedDate"].iloc[-1]
    if last_date == None:
        print "IF Last date none:-"
        pandas_df = dfForRange.select(["suggestedDate"]).distinct().toPandas()
        pandas_df.sort_values(by="suggestedDate",ascending=True,inplace=True)
        last_date = pandas_df["suggestedDate"].iloc[-1]
    print "first_date : ", first_date
    dataRange = (last_date-first_date).days
    if dataRange <= 180:
        duration = dataRange
        dataLevel = "day"
        durationString = str(duration)+" days"
    elif dataRange > 180 and dataRange <= 1095:
        duration = df.select("year_month").distinct().count()
        dataLevel = "month"
        durationString = str(duration)+" months"
    else:
        duration = df.select("year_month").distinct().count()
        dataLevel = "month"
        durationString = CommonUtils.get_duration_string(dataRange)
    outDict = {
        "duration":duration,
        "durationString":durationString,
        "dataLevel":dataLevel,
        "firstDate":first_date,
        "lastDate":last_date
        }
    return (df,outDict)


def restructure_donut_chart_data(dataDict,nLevels=None):
    if nLevels == None:
        nLevels = 10
    dataTuple = [(k,v) for k,v in dataDict.items()]
    dataTuple = sorted(dataTuple,key=lambda x:x[1],reverse=True)
    mainData = dataTuple[:nLevels-1]
    otherData = [x[1] for x in dataTuple[nLevels-1:]]
    finalData = mainData+[("Others",sum(otherData))]
    return dict(finalData)

def generate_rules(colname,target,rules, total, success, success_percent,analysisType,binFlag=False):
    key_dimensions,key_measures = get_rules_dictionary(rules)
    temp_narrative = ''
    crude_narrative = ''

    customSeparator = "|~%%~| "
    for var in key_measures.keys():
        if key_measures[var].has_key('upper_limit') and key_measures[var].has_key('lower_limit'):
            temp_narrative = temp_narrative + 'the value of ' + var + ' is between ' + key_measures[var]['lower_limit'] + ' to ' + key_measures[var]['upper_limit']+customSeparator
            crude_narrative = crude_narrative + 'value of ' + var + ' is between ' + key_measures[var]['lower_limit'] + ' to ' + key_measures[var]['upper_limit']+customSeparator
        elif key_measures[var].has_key('upper_limit'):
            temp_narrative = temp_narrative + 'the value of ' + var + ' is less than or equal to ' + key_measures[var]['upper_limit']+customSeparator
            crude_narrative = crude_narrative + 'value of ' + var + ' is less than or equal to ' + key_measures[var]['upper_limit']+customSeparator
        elif key_measures[var].has_key('lower_limit'):
            temp_narrative = temp_narrative + 'the value of ' + var + ' is greater than ' + key_measures[var]['lower_limit']+customSeparator
            crude_narrative = crude_narrative + 'value of ' + var + ' is greater than ' + key_measures[var]['lower_limit']+customSeparator
    # crude_narrative = temp_narrative
    for var in key_dimensions.keys():
        if key_dimensions[var].has_key('in'):
            key_dimensions_tuple = tuple(map(str.strip, str(key_dimensions[var]['in']).replace('(', '').replace(')','').split(',')))
            if len(key_dimensions_tuple) > 5:

                if (len(key_dimensions_tuple)-5) == 1:
                    key_dims = key_dimensions_tuple[:5] + ("and " + str(len(key_dimensions_tuple)-5) + " other",)
                else:
                    key_dims = key_dimensions_tuple[:5] + ("and " + str(len(key_dimensions_tuple)-5) + " others",)

                temp_narrative = temp_narrative + 'the ' + var + ' falls among ' + str(key_dims) + customSeparator
                crude_narrative = crude_narrative + var + ' falls among ' + key_dimensions[var]['in'] + customSeparator

            else:
                temp_narrative = temp_narrative + 'the ' + var + ' falls among ' + key_dimensions[var]['in'] + customSeparator
                crude_narrative = crude_narrative + var + ' falls among ' + key_dimensions[var]['in'] + customSeparator

        elif key_dimensions[var].has_key('not_in'):
            key_dimensions_tuple = tuple(map(str.strip, str(key_dimensions[var]['not_in']).replace('(', '').replace(')','').split(',')))
            if len(key_dimensions_tuple) > 5:

                if (len(key_dimensions_tuple)-5) == 1:
                    key_dims = key_dimensions_tuple[:5] + ("and " + str(len(key_dimensions_tuple)-5) + " other",)
                else:
                    key_dims = key_dimensions_tuple[:5] + ("and " + str(len(key_dimensions_tuple)-5) + " others",)

                temp_narrative = temp_narrative + 'the ' + var + ' does not fall in ' + str(key_dims) + customSeparator
                crude_narrative = crude_narrative + var + ' does not fall in ' + key_dimensions[var]['not_in'] + customSeparator

            else:
                temp_narrative = temp_narrative + 'the ' + var + ' does not fall in ' + key_dimensions[var]['not_in'] + customSeparator
                crude_narrative = crude_narrative +  var + ' does not fall in ' + key_dimensions[var]['not_in'] + customSeparator

    temp_narrative_arr = temp_narrative.split(customSeparator)[:-1]
    if len(temp_narrative_arr) > 2:
        temp_narrative = ", ".join(temp_narrative_arr[:-2])+" and "+temp_narrative_arr[-1]
    elif len(temp_narrative_arr) == 2:
        temp_narrative = temp_narrative_arr[0]+" and "+temp_narrative_arr[1]
    else:
        temp_narrative = ", ".join(temp_narrative_arr)

    crude_narrative_arr = crude_narrative.split(customSeparator)[:-1]
    if len(crude_narrative_arr) > 2:
        crude_narrative = ", ".join(crude_narrative_arr[:-2])+" and "+crude_narrative_arr[-1]
    elif len(crude_narrative_arr) == 2:
        crude_narrative = crude_narrative_arr[0]+" and "+crude_narrative_arr[1]
    else:
        crude_narrative = ", ".join(crude_narrative_arr)
    if temp_narrative == '':
        temp_narrative = ""
    else:
        r = random.randint(0,99)%5
        if binFlag != True:
            if r == 0:
                narrative = 'If ' +temp_narrative+ ' then there is a  <b>' + str(round_number(success_percent))+ '% ' + \
                            ' <b>probability that the ' + colname +' is '+ target+'.'
            elif r == 1:
                narrative = 'If ' +temp_narrative+ ' it is  <b>' + str(round_number(success_percent))+ '% ' + \
                            ' <b>likely that the ' + colname +' is '+ target+'.'
            elif r == 2:
                narrative = 'When ' +temp_narrative+ ' the probability of '+target+ ' is  <b>' + str(round_number(success_percent)) + ' % <b>.'
            elif r == 3:
                narrative = 'If ' + temp_narrative +' then there is  <b>' + str(round_number(success_percent))+ '% ' + \
                            ' <b>probability that the ' + colname + ' would be ' + target +'.'
            else:
                narrative = 'When ' +temp_narrative+ ' then there is  <b>' + str(round_number(success_percent))+ '% ' + \
                            ' <b>chance that '+ colname + ' would be ' + target +'.'
        else:
            if r == 0:
                narrative = 'If ' +temp_narrative+ ' then there is a  <b>' + str(round_number(success_percent))+ '% ' + \
                            ' <b>probability that the ' + colname +' range will be '+ target+'.'
            elif r == 1:
                narrative = 'If ' +temp_narrative+ ' it is  <b>' + str(round_number(success_percent))+ '% ' + \
                            ' <b>likely that the ' + colname +' range will be '+ target+'.'
            elif r == 2:
                narrative = 'When ' +temp_narrative+ ' the probability of <b>'+colname+" range being "+target+ '</b> is <b>' + str(round_number(success_percent)) + ' % <b>.'
            elif r == 3:
                narrative = 'If ' + temp_narrative +' then there is  <b>' + str(round_number(success_percent)) + '% ' + \
                            ' <b>probability that the ' + colname + ' range would be ' + target +'.'
            else:
                narrative = 'When ' +temp_narrative+ ' then there is  <b>' + str(round_number(success_percent)) + '% ' + \
                            ' <b>chance that '+ colname + 'range would be ' + target +'.'
        return narrative,crude_narrative

def statistical_info_array_formatter(st_array):
    outArray = []
    if len(st_array) > 0:
        maxLen = max([len(x[0]) for x in st_array[:-1]])
        if maxLen < len("inference"):
            maxLen = len("inference")
        maxLen += 2
        for val in st_array:
            size = len(val[0])
            sent = (str(val[0])+" "*(maxLen-size)+" : "+str(val[1]))
            outArray.append(sent)
    return outArray

def select_y_axis_format(dataArray):
    if len(dataArray)>0:
        minval = min(dataArray)
        if minval >= 0.01:
            return ".2f"
        elif minval < 0.01:
            return ".4f"
    else:
        return ".2f"

def reformat_level_count_tuple(levelCountTuple):
    percentArray = [val["percentage"] for val in levelCountTuple]
    newPercentArray = []
    for perCent in percentArray:
        if perCent < 99:
            perCent = math.ceil(perCent)
            newPercentArray.append(perCent)
        else:
            newPercentArray.append(99)
    if sum(newPercentArray) > 100:
        newPercentArray[-1] = newPercentArray[-1]-1
    output = []
    for idx,obj in enumerate(levelCountTuple):
        obj.update({"percentage":newPercentArray[idx]})
        output.append(obj)
    return output

def ret_smart_round(n):
    """
    sumit's legacy
    """
    n_int = np.floor(n)
    n_dec = n-n_int
    sum_n = sum(n)
    sum_int = sum(n_int)
    while sum_int != 100:
        n_int[np.argmax(n_dec)] = np.round(n[np.argmax(n_dec)])
        n_dec = n-n_int
        sum_int = sum(n_int)
    return [int(x) for x in n_int]
