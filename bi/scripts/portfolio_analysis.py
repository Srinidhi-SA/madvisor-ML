# -*- coding: utf-8 -*-
import argparse
import json
import sys
from collections import Counter

import pandas as pd
from datetime import datetime

from bi.common import DataLoader
from bi.common import DataWriter
from bi.common import utils as CommonUtils


def get_argument_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input1', type=str, help='HDFS location of input1 csv file(Client Data)')
    parser.add_argument('--input2', type=str, help='HDFS location of input2 csv file (Historical NAV)')
    parser.add_argument('--input3', type=str, help='HDFS location of input3 csv file (Market Outlook) ')
    parser.add_argument('--result', type=str, help='HDFS output location to store descriptive stats')
    parser.add_argument('--narratives', type=str, help='HDFS output location to store narratives')
    # parser.add_argument('--ignorecolumn', type=str, help='Column to be ignored in all computations')

    return parser

if __name__ == '__main__':

    APP_NAME = "PortfolioAnalysis"

    argument_parser = get_argument_parser()
    arguments = argument_parser.parse_args()
    if arguments.input1 is None \
            or arguments.input2 is None \
            or arguments.input3 is None \
            or arguments.result is None \
            or arguments.narratives is None:
        print 'One of the aguments --input1 / --input2 / --input3 / --result / --narratives is missing'
        sys.exit(-1)

    spark = CommonUtils.get_spark_session(app_name=APP_NAME)
    spark.sparkContext.setLogLevel("ERROR")

    input1 = arguments.input1
    input2 = arguments.input2
    input3 = arguments.input3

    RESULT_FILE = arguments.result
    NARRATIVES_FILE = arguments.narratives

    df1 = DataLoader.load_csv_file(spark, input1)
    print "File loaded: ", input1
    df2 = DataLoader.load_csv_file(spark, input2)
    print "File loaded: ", input2
    df3 = DataLoader.load_csv_file(spark, input3)
    print "File loaded: ", input3

    base_dir = "/home/gulshan/projects/portfolio/"
    time_format = "%b %d, %Y"
    def time_difference(start_time,end_time,time_format):
        """
        Calculate differene between 2 timestamps and return difference in days
        """
        t1 = datetime.strptime(start_time,time_format)
        t2 = datetime.strptime(end_time,time_format)
        delta = t2-t1
        return delta.days

    def human_format(num):
        magnitude = 0
        while abs(num) >= 1000:
            magnitude += 1
            num /= 1000.0
        return '%.2f%s' % (num, ['', 'K', 'M', 'G', 'T', 'P'][magnitude])

    def format_date(df,colname,time_format):
        f = lambda x: datetime.strptime(x,time_format).date()
        df[colname] = df[colname].apply(f)
        df['month'] = df[colname].apply(lambda x: int(x.strftime("%m")))

    def convert_numpy64_to_float(arr):
        out = [float(x) for x in arr]
        return out
    def convert_dict_to_float(dict):
        out = {}
        for x in dict.keys():
            out[x] = float(dict[x])
        return out


    def calculate_group_by_stats(df,dimension_colname,measure_colname):
        class_grp = df[[dimension_colname,measure_colname]].groupby(dimension_colname)[measure_colname].sum()
        k = class_grp.to_frame()
        k['cum_sum'] = class_grp.cumsum()
        k['cum_per'] = (k['cum_sum']/k[measure_colname].sum()).apply(lambda x:round(x,2)*100)
        k['per_con'] = (k[measure_colname]/k[measure_colname].sum()).apply(lambda x:round(x,2)*100)
        # k['cum_per'] = map(lambda x:round(x,2),convert_numpy64_to_float(k['cum_per']))
        # k['per_con'] = map(lambda x:round(x,2),convert_numpy64_to_float(k['per_con']))
        # k['cum_sum'] = map(lambda x:round(x,2),convert_numpy64_to_float(k['cum_sum']))

        k['cum_per'] = convert_numpy64_to_float(k['cum_per'])
        k['per_con'] = convert_numpy64_to_float(k['per_con'])
        k['cum_sum'] = convert_numpy64_to_float(k['cum_sum'])

        dict_k = k.to_dict()
        val_dict = k[measure_colname].to_dict()
        val_dict= {k:int(val_dict[k]) for k in val_dict.keys()}
        dict_k['order_increasing'] = sorted(val_dict, key = val_dict.get)
        return dict_k

    def parse_numeric_string(s):
        if isinstance(s, basestring):
            return s.replace(",","")
        else:
            return s

    def scale_column(df,colname,scale):
        first_val = float(parse_numeric_string(df[colname][0]))
        scaled_col = df[colname].map(lambda x: (x/first_val)*scale)
        # scaled_col = convert_numpy64_to_float(scaled_col)
        return scaled_col

    def performance_gain(series):
        ls = list(series)
        return ((ls[-1]/ls[0])-1)*100

    def month_on_month_performance(df,dimension_column,measure_column,):
        k = df[[dimension_column,measure_column]]
        k[measure_column] = k[measure_column].map(lambda x: float(parse_numeric_string(x)))
        grps = k.groupby(dimension_column)[measure_column]
        for val in grps:
            print (val[0],performance_gain(val[1]))

    def portfolio_performance_data(df,colnames,sensex_colname,scale):
        output = {}
        date_series = df["Date"].map(str)
        df['total'] = 0
        for col in colnames:
            df['total'] = df['total'] + df[col]
        df['scaled_total'] = scale_column(df,'total',100)
        for col in colnames:
            scaled_cols = scale_column(df,col,100)
            output[col] = [{"date":x,"val":y} for x, y in zip(date_series,scaled_cols)]
        output['scaled_total'] = [{"date":x,"val":y} for x, y in zip(date_series,df['scaled_total'])]
        output['sensex'] = [{"date":x,"val":y} for x, y in zip(date_series,scale_column(df,sensex_colname,100))]
        return output

    def calculate_sector_performance(df,sector_map,measure_col):
        total_amount_by_cat = [{"sector":val,"sector_contribution":float(sum(df[sector_map[val]['colname']]*df[measure_col]))} for val in sector_map.keys()[1:]]
        return total_amount_by_cat

    def create_sector_mapping(df):
        output = {}
        for idx,val in enumerate(df["Sector"]):
            output[val] = {"benchmark":df.iloc[idx,1],"performance":df.iloc[idx,2]}
        return output

    client_data = df1.toPandas()
    historical_nav = df2.toPandas()
    portfolio_maps = df3.toPandas()
    result_object = {}
    # narrative_data = sample_narrative
    narrative_data = {"narratives":None}

    format_date(historical_nav,"Date",time_format)
    historical_nav.sort_values(by="Date")
    analysis_duration = (historical_nav['Date'].max()-historical_nav['Date'].min()).days/30
    fund_names = list(client_data["Fund Name"])
    sensex_colname = "S&P BSE Sensex 30"
    fund_names.append(sensex_colname)
    for colname in fund_names:
        historical_nav[colname] = historical_nav[colname].map(lambda x: float(parse_numeric_string(x)))

    # ##############################
    # Client Data Summary
    # ##############################

    client_data_summary = []
    purchase_value = {"name":"Total Net Investments","value":human_format(client_data["Purchase Value"].sum())}
    current_value = {"name":"Current Market Value","value":human_format(client_data["Current Value"].sum())}
    growth = round(((client_data["Current Value"].sum()/float(client_data["Purchase Value"].sum())-1)/analysis_duration)*12*100,2)
    annual_growth = {"name":"Compounded Annual Growth","value":str(growth)+"%"}
    client_data_summary = [purchase_value,current_value,annual_growth]
    result_object['portfolio_summary']=client_data_summary


    line1 = "<b>mAdvisor</b> has analysed your investment portfolio over the <b>last "+str(analysis_duration)+" months</b>. "
    text2 = "This report presents an overview of your current portfolio, how various asset categories have performed over time, an outlook on what you can expect for the next quarter, and our recommendations to maximize return."
    text2 = "Please find the insights from our analysis in the next section."
    overall = {"summary":[line1+text2,text2]}
    narrative_data["narratives"] = {"overall": overall}


    # ##############################
    # Class and category splits
    # ##############################
    class_distribution = calculate_group_by_stats(client_data,"Class","Current Value")
    category_distribution = calculate_group_by_stats(client_data,"Category","Current Value")
    result_object['portfolio_snapshot'] = {
                                            "class":
                                            {
                                             "values":convert_dict_to_float(class_distribution["per_con"]),
                                             "order_increasing":class_distribution["order_increasing"]
                                            },
                                            "sector":
                                            {
                                            "values":convert_dict_to_float(category_distribution["Current Value"]),
                                             "order_increasing":category_distribution["order_increasing"]
                                            }
                                          }
    temp = result_object['portfolio_snapshot']["class"]["values"]
    result_object['portfolio_snapshot']["class"]["values"] = {x:round(float(temp[x]),2) for x in temp.keys()}
    temp = result_object['portfolio_snapshot']["sector"]["values"]
    result_object['portfolio_snapshot']["sector"]["values"] = {x:round(float(temp[x]),2) for x in temp.keys()}

    # Narratives snapshot section

    def get_cross_tab_list(df,dim1,dim2):
        dim1 = list(df[dim1])
        dim2 = list(df[dim2])
        out = {key: [] for key in list(set(dim1))}
        for val in zip(dim1,dim2):
            out[val[0]].append(val[1])
        return out

    class_cats = get_cross_tab_list(client_data,"Class","Category")
    equity_cat = {k:category_distribution["per_con"][k] for k in list(set(class_cats["Equity"]))}
    max_cat_equity = max(equity_cat,key = equity_cat.get)
    debt_cat = {k:category_distribution["per_con"][k] for k in list(set(class_cats["Debt"]))}
    max_cat_debt = max(debt_cat,key = equity_cat.get)

    snapshot_data = {
                "Equity": {
                    "per" : class_distribution["per_con"]["Equity"],
                    "cat" : list(set(class_cats["Equity"])),
                    "max_cat" : category_distribution["per_con"][max_cat_equity],
                    "cat_sum" : category_distribution["Current Value"]
                },
                "Debt":{
                    "per" : class_distribution["per_con"]["Debt"],
                    "cat" : list(set(class_cats["Debt"])),
                    "max_cat" : category_distribution["per_con"][max_cat_debt]
                }
            }
    def generate_snapshot_summary_equity(snapshot_data):
        line1 = None
        line2 = None
        per = snapshot_data["Equity"]["per"]
        n_cat = len(snapshot_data["Equity"]["cat"])
        cats = snapshot_data["Equity"]["cat"]
        cat_sum = snapshot_data["Equity"]["cat_sum"]
        max_cat = snapshot_data["Equity"]["max_cat"]
        if per >= 75:
          line1 = "The portfolio has a <b>significantly high exposure to equity</b>, as it has more than <b>three quarters</b> "+str(per)+"% of the total investment."
        elif per >= 65 and per < 75:
          line1 = "The portfolio has a <b>very high exposure to equity</b>, as it has almost <b>two-thirds</b> "+str(per)+"% of the total investment."
        elif per >= 50 and per < 65:
          line1 = "The portfolio has a <b>high exposure to equity</b>, as it has more than <b>half</b> "+str(per)+"% of the total investment."
        elif per >= 30 and per < 50:
          line1 = "The portfolio has a <b>moderate level of exposure to equity</b>, as it has about <b>"+str(per)+"% </b>of the total investment."
        elif per < 30:
          line1 = "The portfolio <b>does not have significant exposure to equity</b>, as it has just about <b>"+str(per)+"%</b> of the total investment."

        if n_cat ==2:
            if max_cat < 70:
                line2 = "And it is diversified across <b>"+cats[0]+"</b> and <b>"+cats[1]+"</b>, with INR "+str(cat_sum[cats[0]])+" and INR "+str(cat_sum[cats[1]])+" respectively."
            elif max_cat >= 70:
                line2 = "And it is split across <b>"+cats[0]+"</b> and <b>"+cats[1]+"</b>, with INR "+str(cat_sum[cats[0]])+" and INR "+str(cat_sum[cats[1]])+" respectively."
        elif n_cat > 2:
            if max_cat < 60:
                line2 = "And it is diversified across <b>"+cats[0]+","+cats[1]+"</b> and <b>"+cats[2]+"</b>, with INR "+str(cat_sum[cats[0]])+","+str(cat_sum[cats[1]])+" and INR "+str(cat_sum[cats[2]])+" respectively."
            elif max_cat >= 60:
                line2 = "And it is split across <b>"+cats[0]+","+cats[1]+"</b> and <b>"+cats[2]+"</b>, with INR "+str(cat_sum[cats[0]])+","+str(cat_sum[cats[1]])+" and INR "+str(cat_sum[cats[2]])+" respectively."
        else:
            line2 = "No Narrative"

        out = line1+line2
        return out

    def generate_snapshot_summary_debt(snapshot_data):
        line1 = None
        per = snapshot_data["Debt"]["per"]
        n_cat = len(snapshot_data["Debt"]["cat"])
        cats = snapshot_data["Debt"]["cat"]
        max_cat = snapshot_data["Debt"]["max_cat"]
        text1,text2,text3 = "","",""
        if per >= 75:
            text1 = "But the portfolio has <b>significantly high exposure to debt</b> instruments."
            text2 = "The debt portion of the portfolio accounts for more than <b>three quarters</b> "+str(per)+"% of the total investment."
        elif per >= 65 and per < 75:
            text1 = "But the portfolio has <b>very high exposure to debt</b> instruments."
            text2 = "The debt portion of the portfolio accounts for more than <b>two-thirds</b> "+str(per)+"% of the total investment."
        elif per >= 50 and per < 65:
            text1 = "But the portfolio has <b>high exposure to debt</b> instruments."
            text2 = "The debt portion of the portfolio accounts for more than <b>half</b> "+str(per)+"% of the total investment."
        elif per >= 30 and per < 50:
            text1 = "It also has a <b>moderate</b> level of investment on <b>debt</b> instruments as well."
            text2 = "The debt portion of the portfolio accounts for about <b>"+str(per)+"%</b> of the total investment."
        elif per < 30:
            text1 = "The portfolio has very <b>little</b> exposure to <b>debt</b> instruments."
            text2 = "The debt portion of the portfolio accounts for about <b>"+str(per)+"%</b> of the total investment."
        if n_cat == 1:
            text3 = "And, the entire debt portfolio is solely focused on <b>"+cats[0]+"</b>"
        else:
            text3 = "It is predominantly into <b>"+cats[0]+"</b>."

        return text1+text2+text3

    snapshot_nar_summary = [generate_snapshot_summary_equity(snapshot_data),generate_snapshot_summary_debt(snapshot_data)]
    narrative_data["narratives"]["snapshot"] = {"summary":snapshot_nar_summary}




    # ##############################
    # Portfolio Performance trends
    # ##############################

    portfolio_performance = portfolio_performance_data(historical_nav,fund_names,sensex_colname,100)
    result_object['portfolio_performance'] = portfolio_performance
    def change_to_float(list_of_dict,key):
        out = []
        for val in list_of_dict:
            val[key] = round(float(val[key]),2)
            out.append(val)
        return out
    for key in portfolio_performance.keys():
        result_object['portfolio_performance'][key] = change_to_float(portfolio_performance[key],"val")

    ############################Performance Narrative ####################################3333
    def calculate_streak_months(portfolio_growth,max_length):
        streak = ""
        months = portfolio_growth.keys()
        for month in portfolio_growth.keys():
            if portfolio_growth[month] > 0:
                streak+="P"
            else:
                streak+="N"

        longest_seq_len = 1
        for i in range(1,max_length):
            if "P"*i in streak or "N"*i in streak:
                longest_seq_len = i
            else:
                break
        pos_streak_months = []
        neg_streak_months = []
        if "P"*longest_seq_len in streak:
            index = streak.index("P"*longest_seq_len)
            pos_streak_months =  portfolio_growth.keys()[index,index+longest_seq_len]
        else:
            index = streak.index("N"*longest_seq_len)
            neg_streak_months = months[index:index+longest_seq_len]

        return {"streak":streak,"longest":longest_seq_len,"pos":pos_streak_months,"neg":neg_streak_months}

    portfolio = 0
    for col in fund_names:
        portfolio = portfolio + historical_nav[col]
    portfolio = [x*100/portfolio[0] for x in portfolio]
    sensex = list(scale_column(historical_nav,sensex_colname,100))
    month_list = list(historical_nav["month"])
    sensex_month = {key: [] for key in list(set(month_list))}
    for val in zip(month_list,sensex):
        sensex_month[val[0]].append(val[1])
    portfolio_month = {key: [] for key in list(set(month_list))}
    for val in zip(month_list,portfolio):
        portfolio_month[val[0]].append(val[1])

    month_diff = {}
    for val in list(set(month_list)):
        month_diff[val] = 100*(portfolio_month[val][-1]-sensex_month[val][-1])/sensex_month[val][-1]

    portfolio_growth = {}
    for month in portfolio_month.keys():
        portfolio_growth[month] = portfolio_month[month][-1]-portfolio_month[month][0]


    overall_growth = {"pv":sum(client_data["Purchase Value"]),"cv":sum(client_data["Current Value"])}
    overall_growth["change"] = round(overall_growth["cv"]/float(overall_growth["pv"]),2)

    streak_data = calculate_streak_months(portfolio_growth,11)

    month_string = {1:"Jan",2:"Feb",3:"Mar",4:"Apr",5:"May",6:"Jun",7:"Jul",8:"Aug",9:"Sep",10:"Oct",11:"Nov",12:"Dec"}

    final_diff = portfolio[-1]-sensex[-1]
    pos_diff_months = [k for k in portfolio_growth.keys() if portfolio_growth[k]>0]
    neg_diff_months = [k for k in portfolio_growth.keys() if portfolio_growth[k]<0]



    def generate_performance_narrative(overall_growth,month_string,portfolio_month,streak_data,final_diff,pos_diff_months,neg_diff_months,analysis_duration):
        out = overall_growth

        t1 = "The portfolio, with the <b>total investment</b> of INR <b>%s</b>, is now worth INR <b>%s</b> "%(str(out["pv"]),str(out["cv"]))
        if out["change"] <= 10:
            t2 = "This indicates a <b>moderate growth</b> of <b>%s</b> over the last %d months. " %(str(out["change"])+"%",analysis_duration)
        elif out["change"] > 10 and out["change"] < 15:
            t2 = "This indicates a <b>significant growth</b> of <b>%s</b> over the last %d months. " %(str(out["change"])+"%",analysis_duration)
        else:
            t2 = "This indicates a <b>extremely robust growth</b> of <b>%s</b> over the last %d months. " %(str(out["change"])+"%",analysis_duration)

        if len(streak_data["pos"]) > 0:
            if portfolio_month[streak_data["pos"][-1]][-1] > portfolio_month[streak_data["pos"][0]][-1]:
                s1 = "The portfolio <b>grew significantly</b> between <b>%s and %s</b>, and remained <b>relatively flat</b> since then. "%(month_string[streak_data["pos"][0]],month_string[streak_data["pos"][-1]])
            else:
                s1 = "The portfolio <b>grew significantly</b> between <b>%s and %s</b>, but <b>lost some of the gains</b> since then. "%(month_string[streak_data["pos"][0]],month_string[streak_data["pos"][-1]])
        else:
            if portfolio_month[streak_data["neg"][-1]][-1] > portfolio_month[streak_data["neg"][0]][-1]:
                s1 = "The portfolio <b>shrunk significantly</b> between <b>%s and %s</b>, but <b>made some gain</b> since then. "%(month_string[streak_data["neg"][0]],month_string[streak_data["neg"][-1]])
            else:
                s1 = "The portfolio <b>shrunk significantly</b> between <b>%s and %s</b>, and remained <b>relatively flat</b> since then. "%(month_string[streak_data["neg"][0]],month_string[streak_data["neg"][-1]])

        if final_diff > 0:
            if len(pos_diff_months) >=2:
                d1 = "It has <b>outperformed</b> the benchmark index sensex, with most of the gain made during %s and %s. "%(month_string[pos_diff_months[0]],month_string[pos_diff_months[1]])
            else:
                d1 = "It has <b>outperformed</b> the benchmark index sensex, with most of the gain made during %s. "%(month_string[pos_diff_months[0]])

        else:
            if len(neg_diff_months) >=2:
                d1 = "It has <b>underperformed</b> the benchmark index sensex, with most of the loss occured during %s and %s. "%(month_string[neg_diff_months[0]],month_string[neg_diff_months[1]])
            else:
                d1 = "It has <b>underperformed</b> the benchmark index sensex, with most of the loss occured during %s. "%(month_string[neg_diff_months[0]])

        return [t1+t2,s1+d1]

    performance_summary = generate_performance_narrative(overall_growth,month_string,portfolio_month,streak_data,final_diff,pos_diff_months,neg_diff_months,analysis_duration)

    narrative_data["narratives"]["performance"] = {"summary":"","sub_heading":""}
    narrative_data["narratives"]["performance"]["sub_heading"] = "How is your portfolio performing ?"
    narrative_data["narratives"]["performance"]["summary"] = performance_summary



    ##### ########### narratives Growth
    def calculate_fund_growth(df,colnames):
        output = {}
        for col in colnames:
            out = {}
            data = list(df[col])
            out["diff"] = round(data[1]-data[0],3)
            out["per"] = round(out["diff"]/float(data[0])*100,2)
            out["growth_type"] = "pos" if out["diff"] > 0.0 else "neg" if out["diff"] < 0.0 else "zero"
            out["cagr"] = round(out["per"]/analysis_duration*12,2)
            output[col] = out
        return output

    def get_top_performer(fund_dict):
        #     funds = [x for x in fund_dict.keys() if fund_dict[x]["growth_type"] == growth_type]
        subset = {k:fund_dict[k]["diff"] for k in fund_dict.keys()}
        out = {"top":[],"bot":[]}
        if len(subset.keys()) > 2:
            max_key = max(subset,key = subset.get)
            s_keys = subset.keys()
            s_keys.remove(max_key)
            subset1 = {k:subset[k] for k in s_keys}
            max_key_2 = max(subset1,key = subset1.get)
            first = fund_dict[max_key]
            first["name"] = max_key
            second = fund_dict[max_key_2]
            second["name"] = max_key_2
            out["top"] = [first,second]

            min_key = min(subset,key = subset.get)
            s_keys = subset.keys()
            s_keys.remove(min_key)
            subset1 = {k:subset[k] for k in s_keys}
            min_key_2 = min(subset1,key = subset1.get)
            first = fund_dict[min_key]
            first["name"] = min_key
            second = fund_dict[min_key_2]
            second["name"] = min_key_2
            out["bot"] = [first,second]
        return out

    def reverse_list(arr):
        x = len(arr)
        if x > 1:
            out =[]
            while x > 0:
                out.append(arr[x])
                x-=1
            return out
        else:
            return arr
    def get_class_type_statement(class_dict,fund_growth):
        mf_list = fund_growth.values()
        keys = class_dict.keys()
        out = ""
        if len(keys) == 1:
            if len(mf_list) == 2:
                out = "both in "+keys[0]
            else:
                out = "and all of them are in "+keys[0]
        elif len(keys) >= 2:
            l1 = []
            for val in keys:
                l1.append(str(class_dict[val])+" "+val)
            out = ",".join(l1)
        return out

    def get_pos_neg_fundnames(fund_growth):
        fund_names = fund_growth.keys()
        out = {"pos":[],"neg":[]}
        for val in fund_names:
            if fund_growth[val]["growth_type"] == "pos":
                out["pos"].append(val)
            elif fund_growth[val]["growth_type"] == "neg":
                out["neg"].append(val)
        return out


    def generate_growth_summary_statement(fund_growth,class_dict):
        class_type_text = get_class_type_statement(class_dict,fund_growth)
        pos_neg_funds = get_pos_neg_fundnames(fund_growth)

        keys = class_dict.keys()
        total = sum(class_dict.values())
        outperformer_statement = ""
        underperformer_statement = ""
        plural_dict = {"Debt":"Debts","Equity":"Equities","Cash":"Cash"}
        plural_keys = [plural_dict[x] for x in keys]
        if total == 1:
            mf_dict = fund_growth.values[0]
            if mf_dict["growth_type"] == "pos":
                out = "You have been investing in Only one mutual fund (i.e %s) and %s has grown by %s during the %d month period,resulting in CAGR of %s"%(class_dict.keys()[0],fund_growth.keys()[0],str(mf_dict["per"])+"%",analysis_duration,str(mf_dict["cagr"])+"%")
                outperformer_statement = "The %s fund has grown by %s during the %d month period, CAGR of %s."%(fund_growth.keys()[0],str(mf_dict["per"])+"%",analysis_duration,str(mf_dict["cagr"])+"%")
            elif mf_dict["growth_type"] == "neg":
                out = "You have been investing in Only one mutual fund (i.e %s) and %s has shrunken by %s during the %d month period,resulting in annual decline of %s"%(class_dict.keys()[0],fund_growth.keys()[0],str(mf_dict["per"])+"%",analysis_duration,str(mf_dict["cagr"])+"%")
                underperformer_statement = "The %s fund has shrunk by %s during the %d month period, annual decline of %s."%(fund_growth.keys()[0],str(mf_dict["per"])+"%",analysis_duration,str(mf_dict["cagr"])+"%")
        elif total == 2:
            if len(pos_neg_funds["pos"]) == 2:
                out = "You have been investing in two mutual funds (%s) and both have grown over the last %d months"%(class_type_text,analysis_duration)
            elif len(pos_neg_funds["neg"]) == 2:
                out = "You have been investing in two mutual funds (%s) and both have shrunk over the last %d months"%(class_type_text,analysis_duration)
            else:
                out = "You have been investing in two mutual funds (%s).%s grown over the last %d months while %s has shrunken"%(class_type_text,pos_neg_funds["pos"][0],analysis_duration,pos_neg_funds["neg"][0])
    #     elif total == 3:
        elif total > 3:
            if len(pos_neg_funds["pos"]) == 0 :
                out = "You have been investing in %d mutual funds (%s) and all of these have shrunken significantly the last %d months"%(total,class_type_text,analysis_duration)
            elif len(pos_neg_funds["neg"]) == 0:
                out = "You have been investing in %d mutual funds (%s) and all of these have grown significantly the last %d months"%(total,class_type_text,analysis_duration)
            else:
                out = "You have been investing in %d mutual funds (%s).%d have grown over the last %d months while remaining %d has shrunken"%(total,class_type_text,len(pos_neg_funds["pos"]),analysis_duration,len(pos_neg_funds["neg"]))
        return out

    def get_over_under_performers(fund_growth):
        top_bot = get_top_performer(fund_growth)
        top2 = top_bot["top"]
        bot2 = top_bot["bot"]
        outperformer = ""
        underperformer = ""
        if top2[0]["class"] == top2[1]["class"]:
            if bot2[0]["class"] == bot2[1]["class"]:
                data_tuple = (top2[0]["name"],top2[1]["name"],top2[0]["class"],top2[0]["name"],str(top2[0]["per"])+"%",analysis_duration,str(top2[0]["cagr"])+"%",top2[1]["name"],str(top2[1]["per"])+"%",analysis_duration,str(top2[1]["cagr"])+"%")
                outperformer = "The most significant among them are <b>%s and %s</b> and both of them are from the same portfolios ie %s . %s has grown by %s during the %d month period , resulting in CAGR of %s and %s by %s during the %d month period , resulting in CAGR of %s ."%data_tuple

                data_tuple = (bot2[0]["name"],bot2[1]["name"],analysis_duration,str(bot2[0]["per"])+"%",str(bot2[1]["per"])+"%",bot2[0]["class"])
                underperformer = "<b>%s and %s</b> Funds have been under-performing over the last %d month, growing just around %s and %s . Given the portfolio’s very high exposure to %s, these two have significantly dragged the performance down."%data_tuple
            else:
                data_tuple = (top2[0]["name"],top2[1]["name"],top2[0]["class"],top2[0]["name"],str(top2[0]["per"])+"%",analysis_duration,str(top2[0]["cagr"])+"%",top2[1]["name"],str(top2[1]["per"])+"%",analysis_duration,str(top2[1]["cagr"])+"%")
                outperformer = "The most significant among them are <b>%s and %s</b> and both of them are from the same portfolios ie %s . %s has grown by %s during the %d month period , resulting in CAGR of %s and %s by %s during the %d month period , resulting in CAGR of %s ."%data_tuple

                data_tuple = (bot2[0]["name"],bot2[1]["name"],analysis_duration,str(bot2[0]["per"])+"%",str(bot2[1]["per"])+"%")
                underperformer = "<b>%s and %s</b> Funds have been under-performing over the last %d month, growing just around %s and %s."%data_tuple
        else:
            if bot2[0]["class"] == bot2[1]["class"]:
                data_tuple = (top2[0]["name"],top2[0]["class"],str(top2[0]["per"])+"%",analysis_duration,str(top2[0]["cagr"])+"%",top2[1]["name"],str(top2[1]["per"])+"%",analysis_duration,str(top2[1]["cagr"])+"%")
                outperformer = "The most significant among them is <b>%s</b> from %s portfolio, which has grown by %s during the %d month period, resulting in CAGR of %s. and the next best fund is %s and it has grown by %s during the %d month period, resulting in CAGR of %s ."%data_tuple

                data_tuple = (bot2[0]["name"],bot2[1]["name"],analysis_duration,str(bot2[0]["per"])+"%",str(bot2[1]["per"])+"%",bot2[0]["class"])
                underperformer = "<b>%s and %s</b> Funds have been under-performing over the last %d month, growing just around %s and %s . Given the portfolio’s very high exposure to %s, these two have significantly dragged the performance down."%data_tuple

            else:
                data_tuple = (top2[0]["name"],top2[0]["class"],str(top2[0]["per"])+"%",analysis_duration,str(top2[0]["cagr"])+"%",top2[1]["name"],str(top2[1]["per"])+"%",analysis_duration,str(top2[1]["cagr"])+"%")
                outperformer = "The most significant among them is <b>%s</b> from %s portfolio, which has grown by %s during the %d month period, resulting in CAGR of %s. and the next best fund is %s and it has grown by %s during the %d month period, resulting in CAGR of %s ."%data_tuple

                data_tuple = (bot2[0]["name"],bot2[1]["name"],analysis_duration,str(bot2[0]["per"])+"%",str(bot2[1]["per"])+"%")
                underperformer = "<b>%s and %s</b> Funds have been under-performing over the last %d month, growing just around %s and %s."%data_tuple


        return underperformer,outperformer


    narrative_data["narratives"]["growth"] = {"summary":"","sub_heading":"","sub_sub_heading":""}
    narrative_data["narratives"]["growth"] = {"sub_heading":"What is driving your protfolio growth ?"}

    fund_class = dict(zip(client_data["Fund Name"],client_data["Class"]))
    fund_cls_dict = dict(Counter(client_data["Class"]))
    fund_growth = calculate_fund_growth(historical_nav,fund_names[:-1])
    for key in fund_growth.keys():
        fund_growth[key]["class"] = fund_class[key]

    class_type = get_class_type_statement(fund_cls_dict,fund_growth)
    narrative_data["narratives"]["growth"]["sub_sub_heading"] = generate_growth_summary_statement(fund_growth,fund_cls_dict)

    perform_stat = get_over_under_performers(fund_growth)
    narrative_data["narratives"]["growth"]["summary"] = {"outperformers":perform_stat[1],"underperformers":perform_stat[0],"comments":["comment1","comment2","comment3"]}

    def sector_summary(top_sectors,bot_sectors,percent_contribution):
        para1 = ""
        para2 = ""
        para3 = ""
        top_sectors_total_cont = 0
        np_sectors_total_cont = 0
        less_than_10 = []
        nt10 = []

        for sec in top_sectors:
            top_sectors_total_cont += percent_contribution[sec[0]]
            if sec[1] <= 10:
                less_than_10.append(sec)
        for sec in bot_sectors:
            np_sectors_total_cont += percent_contribution[sec[0]]
            if sec[1] >= 10:
                nt10.append(sec)

        s1 = "The portfolio seems to be well diversified as investments have been made in a wide range of sectors. "
        if len(top_sectors) == 1:
            if top_sectors_total_cont >= 50 and top_sectors_total_cont < 65:
                data_tuple = (top_sectors[0][0],str(top_sectors[0][1])+"%")
                s2 = "However, the investments in equity market seem to <b>depend heavily upon a sector</b>, as <b>%s</b> accounts for more than half %s of the equity allocation."%data_tuple
            elif top_sectors_total_cont >= 65 and top_sectors_total_cont < 75:
                data_tuple = (top_sectors[0][0],str(top_sectors[0][1])+"%")
                s2 = "However, the investments in equity market seem to <b>depend heavily upon a sector</b>, as <b>%s</b> accounts for more than two-thirds %s of the equity allocation."%data_tuple

            elif top_sectors_total_cont > 75:
                data_tuple = (top_sectors[0][0],str(top_sectors[0][1])+"%")
                s2 = "However, the investments in equity market seem to depend <b>heavily upon a sector</b>, as <b>%s</b> accounts for more than three-quarters %s of the equity allocation."%data_tuple

            if len(less_than_10) == 0:
                l1 = "The table below displays the sector allocation of all equity funds and how each sector has performed over the last %d months. "%(analysis_duration)
                l2 = "The key sectors that the portfolio is betting on, have done <b>relatively well</b> (%s has grown by %s)."%(top_sectors[0][0],str(top_sectors[0][1])+"%")
        elif len(top_sectors) == 2:
            if top_sectors_total_cont >= 50 and top_sectors_total_cont < 65:
                data_tuple = (top_sectors[0][0],top_sectors[1][0],str(top_sectors_total_cont)+"%")
                s2 = "However, the investments in equity market seem to <b>depend heavily upon couple of sectors</b>, as %s and %s accounts for more than <b>half</b> %s of the equity allocation."%data_tuple
            elif top_sectors_total_cont >= 65 and top_sectors_total_cont < 75:
                data_tuple = (top_sectors[0][0],top_sectors[1][0],str(top_sectors_total_cont)+"%")
                s2 = "However, the investments in equity market seem to <b>depend heavily upon couple of sectors</b>, as %s and %s accounts for more than <b>two-thirds</b> %s of the equity allocation."%data_tuple
            elif top_sectors_total_cont > 75:
                data_tuple = (top_sectors[0][0],top_sectors[1][0],str(top_sectors_total_cont)+"%")
                s2 = "However, the investments in equity market seem to <b>depend heavily upon couple of sectors</b>, as %s and %s accounts for more than <b>three-quarters</b> %s of the equity allocation."%data_tuple
            if len(less_than_10) == 0:
                data_tuple = (top_sectors[0][0],top_sectors[1][0],str(top_sectors[0][1])+"%",str(top_sectors[1][1])+"%")
                l1 = "The table below displays the sector allocation of all equity funds and how each sector has performed over the last %d months. "%(analysis_duration)
                l2 = "The key sectors that the portfolio is betting on, have done <b>relatively well</b> (%s and %s have grown by  %s and %s respectively)."%data_tuple

        elif len(top_sectors) == 3:
            if top_sectors_total_cont >= 50 and top_sectors_total_cont < 65:
                data_tuple = (top_sectors[0][0],top_sectors[1][0],top_sectors[2][0],str(top_sectors_total_cont)+"%")
                s2 = "However, the investments in equity market seem to <b>depend heavily upon three sectors</b>, as %s,%s and %s accounts for more than <b>half</b> %s of the equity allocation."%data_tuple
            elif top_sectors_total_cont >= 65 and top_sectors_total_cont < 75:
                data_tuple = (top_sectors[0][0],top_sectors[1][0],top_sectors[2][0],str(top_sectors_total_cont)+"%")
                s2 = "However, the investments in equity market seem to <b>depend heavily upon three sectors</b>, as %s,%s and %s accounts for more than <b>two-thirds</b> %s of the equity allocation."%data_tuple
            elif top_sectors_total_cont > 75:
                data_tuple = (top_sectors[0][0],top_sectors[1][0],top_sectors[2][0],str(top_sectors_total_cont)+"%")
                s2 = "However, the investments in equity market seem to <b>depend heavily upon three sectors</b>, as %s,%s and %s accounts for more than <b>three-quarters</b> %s of the equity allocation."%data_tuple
            if len(less_than_10) == 0:
                data_tuple = (top_sectors[0][0],top_sectors[1][0],top_sectors[2][0],str(top_sectors[0][1])+"%",str(top_sectors[1][1])+"%",str(top_sectors[0][1])+"%")
                l1 = "The table below displays the sector allocation of all equity funds and how each sector has performed over the last %d months. "%(analysis_duration)
                l2 = "The key sectors that the portfolio is betting on, have done <b>relatively well</b> (%s, %s, and %s have grown by %s, %s, and %s respectively)."%data_tuple

        elif len(top_sectors) > 3:
            if top_sectors_total_cont >= 50 and top_sectors_total_cont < 65:
                data_tuple = (top_sectors[0][0],top_sectors[1][0],top_sectors[2][0],str(top_sectors_total_cont)+"%")
                s2 = "However, the investments in equity market seem to <b>depend heavily upon few sectors</b>, as the top %d sectors including %s,%s and %s accounts for more than <b>half</b> %s of the equity allocation."%data_tuple
            elif top_sectors_total_cont >= 65 and top_sectors_total_cont < 75:
                data_tuple = (top_sectors[0][0],top_sectors[1][0],top_sectors[2][0],str(top_sectors_total_cont)+"%")
                s2 = "However, the investments in equity market seem to <b>depend heavily upon few sectors</b>, as the top %d sectors including %s,%s and %s accounts for more than <b>two-thirds</b> %s of the equity allocation."%data_tuple
            elif top_sectors_total_cont > 75:
                data_tuple = (len(top_sectors),top_sectors[0][0],top_sectors[1][0],top_sectors[2][0],str(top_sectors_total_cont)+"%")
                s2 = "However, the investments in equity market seem to <b>depend heavily upon few sectors</b>, as the top %d sectors including %s,%s and %s accounts for more than <b>three-quarters</b> %s of the equity allocation."%data_tuple
            if len(less_than_10) > 0:
                data_tuple = (less_than_10[0][0],str(less_than_10[0][1])+"%")
                l1 = "The table below displays the sector allocation of all equity funds and how each sector has performed over the last %d months. "%(analysis_duration)
                l2 = "However %s has generated only %s return over the period, which significatnly undermines the portfolio's overall perofrmance.."%data_tuple
        if len(nt10) == 1:
            m1 = "It is also very important to note that the existing portfolio <b>does not have adequate exposure</b> to other well-performing sectors."
            m2 = "<b>%s</b> has <b>grown remarkably</b>, producing return of over %s. "%(nt10[0][0],str(nt10[0][1])+"%")
            m3 = "But the portfolio allocation (%s on %s) limits scope for leveraging the booming sector."%(str(nt10[0][1])+"%",nt10[0][0])
        elif len(nt10) == 2:
            m1 = "It is also very important to note that the existing portfolio <b>does not have adequate exposure</b> to other well-performing sectors."
            m2 = "<b>%s and %s</b> has <b>grown remarkably</b>, producing return of over %s. "%(nt10[0][0],nt10[1][0],str(nt10[1][1])+"%")
            m3 = "But the portfolio allocation (%s on %s) limits scope for leveraging the booming sector."%(str(nt10[0][1])+"%",nt10[0][0])

        elif len(nt10) == 3:
            m1 = "It is also very important to note that the existing portfolio <b>does not have adequate exposure</b> to other well-performing sectors."
            m2 = "<b>%s,%s and %s</b> has <b>grown remarkably</b>, producing return of over %s. "%(nt10[0][0],nt10[1][0],nt10[2][0],str(nt10[2][1])+"%")
            m3 = "But the portfolio allocation (%s on %s) limits scope for leveraging the booming sector."%(str(nt10[0][1])+"%",nt10[0][0])

        elif len(nt10) > 3:
            m1 = "It is also very important to note that the existing portfolio <b>does not have adequate exposure</b> to other well-performing sectors."
            m2 = "sectors such as <b>%s,%s, and %s</b> has <b>grown remarkably</b>, producing return of over %s. "%(nt10[0][0],nt10[1][0],nt10[2][0],str(nt10[2][1])+"%")
            m3 = "But the portfolio allocation (%s on %s) limits scope for leveraging the booming sector."%(str(nt10[0][1])+"%",nt10[0][0])

        para1 = s1+s2
        para2 = l1+l2
        para3 = m1+m2+m3

        return [para1,"influence of sectors on portfolio growth",para2,para3]




    # ##############################
    # Portfolio distribution across sectors
    # ##############################



    sector_mapping = create_sector_mapping(portfolio_maps)
    [sector_mapping[val].update({'colname':"Allocation % "+val}) for val in sector_mapping.keys()]
    sector_performance = pd.DataFrame(calculate_sector_performance(client_data,sector_mapping,"Amount"))
    sector_performance_stats = calculate_group_by_stats(sector_performance,"sector","sector_contribution")

    returns = {}
    for key in sector_mapping.keys():
        data = [float(parse_numeric_string(x)) for x in list(historical_nav[sector_mapping[key]["benchmark"]])]
        rev = round(((data[-1]/data[0])-1)*(12/analysis_duration),2)*100
        returns[key] = rev

    per_con = sector_performance_stats["per_con"]
    top_sector_cutoff = 20
    top_sectors = [(x,per_con[x]) for x in per_con.keys() if per_con[x] >= top_sector_cutoff]
    top_sectors.sort(key=lambda x: int(x[1]))

    bot_sectors = [(x,per_con[x]) for x in per_con.keys() if per_con[x] < top_sector_cutoff]
    bot_sectors.sort(key=lambda x: int(x[1]))

    out = {"sector_data":{},"sector_order":sector_performance_stats['order_increasing']}
    for val in out['sector_order']:
        out["sector_data"][val] = {"allocation":round(float(sector_performance_stats["per_con"][val]),2),
                                   "return":round(float(returns[val]),2),
                                   "outcome":sector_mapping[val]['performance']}

    result_object['sector_performance'] = out

    comment_list = sector_summary(top_sectors,bot_sectors,per_con)
    narrative_data["narratives"]["growth"]["summary"]["comments"] = comment_list

    stable = []
    underperform = []
    outperform = []
    for val in sector_mapping.keys():
        if sector_mapping[val]["performance"] == "Stable":
            stable.append(val)
        elif sector_mapping[val]["performance"] == "Underperform":
            underperform.append(val)
        elif sector_mapping[val]["performance"] == "Outperform":
            outperform.append(val)

    def generate_projection_summary(outperform,underperform,stable):
        projection_summary = ""
        p1 = ""
        p2 = ""
        p3 = ""
        if len(outperform) == 1:
            p1 = "<b>%s</b> is expected to <b>outperform</b> the overall market, "%(outperform[0])
        elif len(outperform) == 2:
            p1 = "<b>%s and %s</b> are expected to <b>outperform</b> the overall market, "%(outperform[0],outperform[1])
        elif len(outperform) >= 3:
            p1 = "<b>%s, %s and %s</b> are expected to <b>outperform</b> the overall market, "%(outperform[0],outperform[1],outperform[2])

        if len(stable) == 1:
            p2 = "whereas <b>%s</b> is very likely to <b>remain stable</b>, "%(stable[0])
        elif len(stable) == 2:
            p2 = "whereas <b>%s and %s</b> are very likely to <b>remain stable</b>, "%(stable[0],stable[1])
        elif len(stable) >= 3:
            p2 = "whereas <b>%s,%s and %s</b> are very likely to <b>remain stable</b>, "%(stable[0],stable[1],stable[2])

        if len(underperform) == 1:
            p3 = "On the other hand, <b>%s</b> seems to <b>underperform</b> compared to other sectors. "%(underperform[0])
        elif len(underperform) == 2:
            p3 = "On the other hand, <b>%s and %s</b> seems to <b>underperform</b> compared to other sectors. "%(underperform[0],underperform[1])
        elif len(underperform) >= 3:
            p3 = "On the other hand, <b>%s,%s and %s</b> seems to <b>underperform</b> compared to other sectors. "%(underperform[0],underperform[1],underperform[2])

        chart_comment = "The chart below displays the sector allocation of the current portfolio, mapped with projected outlook for the sectors."
        projection_summary = p1+p2+p3+chart_comment
        return projection_summary

    narrative_data["narratives"]["projection"] = {
        "sub_heading": "How is the portfolio projected to perform",
        "summary": [str(generate_projection_summary(outperform,underperform,stable))]
    }


    def generate_recommendations(fund_growth):
        top_performers = get_top_performer(fund_growth)
        bot_funds_equity = [x for x in top_performers["top"] if x["class"]=="Equity"]
        top_funds_debt = [x for x in top_performers["bot"] if x["class"]=="Debt"]

        st1 = ""
        if len(bot_funds_equity) == 0:
            st1 = "<b>Reallocate investments</b> from some of the underperforming funds such as %s: Our suggestion is that you can diversify by investing in low-risk asset classes, such as %s. "%(bot_funds_equity[0]['name'],top_funds_debt[0]['name'])
        else:
            st1 = "<b>Reallocate investments</b> from some of the low-performing assets such as %s: Our suggestion is that you can maximize returns by investing more in other existing equity funds."%(top_funds_debt[0]['name'])

        st2 = "Invest in funds that are going to outperform, <b>Technology and Telecom</b> equity funds. Our suggestion is that you consider investing in ICICI Prudential Large Cap Fund, top performer in Technology, which has an annual return of 25.4%."
        st3 = "<b>Consider investing in Tax Saver</b> equity funds that would help you manage taxes more effectively and save more money."
        return [st1,st2,st3]

    s_head = "Our recommendations to maximize your wealth"
    ss_head = "Based on analysis of your portfolio composition, performance of various funds, and the projected outlook, mAdvisor recommends the following."
    narrative_data["narratives"]["recommendation"] = {
        "sub_heading": s_head,
        "sub_sub_heading": ss_head,
        "summary": generate_recommendations(fund_growth)
    }


    print 'RESULT: %s' % (json.dumps(result_object, indent=2))
    print 'NARRATIVES: %s' %(json.dumps(narrative_data, indent=2))

    DataWriter.write_dict_as_json(spark, result_object, RESULT_FILE)
    DataWriter.write_dict_as_json(spark, narrative_data, NARRATIVES_FILE)

    spark.stop()
