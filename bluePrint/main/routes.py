from main import main_bp
from . import main_bp
from flask import Flask, send_file, render_template, json, request, redirect, Response,url_for, jsonify, session
from flask_caching import Cache
import cx_Oracle
import datetime
import json
from collections import defaultdict
from collections import Counter
import csv
from datetime import datetime, timedelta
#import configparer
#import shutil
port_flask = 5009
username = "readonly"
password = "re6d0n1y"
dsn = cx_Oracle.makedsn("patdbtdsprd05.li.lumentuminc.net", 1522, "TDSPRD05")

with open('part_number_config.json') as f:
    namePart_numbers = json.load(f)

@main_bp.route('/')
def main():

    connection = cx_Oracle.connect(username, password, dsn)
    cursor = connection.cursor()

    txt_query = '''
        SELECT header.SERIALNUMBER,header.PARTNUMBER,header.OPERATION,header.OPERATIONID,header.TESTSTATION,header.STARTTIME,header.RESULT,header.OPERATORID,SYSTIMESTAMP - header.ENDTIME, header.ENDTIME
    FROM testheader_v header WHERE header.productfamilyname ='PicoBlade3' AND header.starttime >= SYSDATE - INTERVAL '14' DAY
        '''

    cursor.execute(txt_query)
    new_last_tested_units_list = cursor.fetchall()
    # data index
    # 0. serial number
    # 1. part number
    # 2. operation name
    # 3. operation id
    # 4. test station id
    # 5. start time
    # 6. result
    # 7. operator id
    # 8. time diff in minute
    # print new_last_tested_units_list
    # Close the cursor and the connection
    cursor.close()
    connection.close()

    last_tested_dict = {}
    length_of_last_tested = 0
    if new_last_tested_units_list != []:
        count = 0
        for single_row in new_last_tested_units_list:
            last_tested_dict[count] = single_row
            #print(single_row)
            count = count + 1
        length_of_last_tested = count
        #print(length_of_last_tested)

    # setting new dict of sn keys that will have completion % , will be define later as
    # dict_of_sn_completion = {}
    # if new_last_tested_units_list != []:
    # count = 0
    # for single_row in new_last_tested_units_list:
    # dict_of_sn_completion[single_row[0]] = single_row[5]
    # print (dict_of_sn_completion)
    # print(dict_of_sn_completion)
    # SN:PASS

    # find the dates from last week
    list_of_last_week_dates = []
    if new_last_tested_units_list != []:
        count = 0
        for single_row in new_last_tested_units_list:
            date_time_string = single_row[5].strftime('%Y-%m-%d')
            if date_time_string not in list_of_last_week_dates:
                list_of_last_week_dates.append(date_time_string)

        # list_of_last_week_dates = set(list_of_last_week_dates)
        print(list_of_last_week_dates)

    # find the models from last week:
    list_of_last_week_models = []
    # new: create a table of s/n per model, for this the below dict is needed.
    dict_of_sn_per_model = {}
    if new_last_tested_units_list != []:
        count = 0
        for single_row in new_last_tested_units_list:
            temp_model = single_row[1]
            list_of_last_week_models.append(temp_model)
            if temp_model in dict_of_sn_per_model:
                # temp_list = dict_of_sn_per_model[temp_model]
                dict_of_sn_per_model[temp_model].append(single_row[0])

            else:
                dict_of_sn_per_model[temp_model] = [(single_row[0])]

        list_of_last_week_models = set(list_of_last_week_models)
        # print(list_of_last_week_models)
        # print(dict_of_sn_per_model)

    # remove duplicates from the new dict of sn per model:
    for key, dict_index in dict_of_sn_per_model.iteritems():
        dict_of_sn_per_model[key] = list(set(dict_index))
        max_list_length = [k for k in dict_of_sn_per_model.iterkeys() if
                           len(dict_of_sn_per_model.get(k)) == max([len(n) for n in dict_of_sn_per_model.values()])]
    try:
        max_list_length2 = max_list_length[0]
        length_of_longest_sn_list = len(dict_of_sn_per_model[max_list_length2])
    except:
        max_list_length2 = 0
        length_of_longest_sn_list = 0
        print('max_list_length', max_list_length)

    # print(dict_of_sn_per_model)

    # reset_models dict with 0 to be used as counters     :
    dict_of_models = {}
    dict_of_lists_of_model_data = {}
    for ind_model in list_of_last_week_models:
        dict_of_models[ind_model] = 0
        dict_of_lists_of_model_data[ind_model] = []
    # print(dict_of_lists_of_model_data)

    # find model in date
    dates_execution_dict = {}
    dict_of_models_in_dict_of_dates = {}
    if new_last_tested_units_list != []:

        for single_date in list_of_last_week_dates:
            # init every date key with a new dict of zeros for each model:
            dict_of_models_in_dict_of_dates[single_date] = {}
            single_date_count = 0
            for single_row in new_last_tested_units_list:
                if single_date in single_row[5].strftime('%Y-%m-%d'):
                    dates_execution_dict[single_date] = single_date_count + 1
                    single_date_count = single_date_count + 1
                    model_lookup = single_row[1]
                    # using try in case it is empty  and there no key with the model name
                    try:
                        dict_of_models_in_dict_of_dates[single_date][model_lookup] = \
                        dict_of_models_in_dict_of_dates[single_date][model_lookup] + 1
                    except:
                        dict_of_models_in_dict_of_dates[single_date][model_lookup] = 1

    # print(dict_of_models_in_dict_of_dates)
    # thispart is for the larger plot, in order to create lists of numbers per model , each var in the list represent a date...

    if new_last_tested_units_list != []:
        # count = 0
        for single_date in list_of_last_week_dates:
            for ind_model in list_of_last_week_models:
                # this try is because there may be days that some models were not inserted to dict_of_models_in_dict_of_dates, in this case we append 0
                try:
                    dict_of_lists_of_model_data[ind_model].append(
                        dict_of_models_in_dict_of_dates[single_date][ind_model])
                except:
                    dict_of_lists_of_model_data[ind_model].append(0)
                    # print ind_model
                    # print dict_of_lists_of_model_data

    # print (dict_of_lists_of_model_data)

    # ******************************************************************************************
    # This part will calculate a dict for  plot
    # find the op from last period
    # print("=========================op vs cycle time=======================")
    # print(single_date)
    list_of_last_period_ops = set(single_row[2] for single_row in new_last_tested_units_list)

        # print('list_of_last_period_ops ====', list_of_last_period_ops)
    # reset the dict
    # find operation vs cycle time, skip as this time still not available
    op_vs_cycle_list_dict = defaultdict(list)
    op_vs_cycle_max_dict = {}

    if new_last_tested_units_list:
        for single_op in list_of_last_period_ops:
            list_of_cycle_t_per_op = []
            for single_row in new_last_tested_units_list:
                if single_op in str(single_row[2]):
                    start_time = single_row[5]
                    end_time = single_row[9]
                    minute_time = (end_time - start_time).total_seconds() / 60
                    list_of_cycle_t_per_op.append(minute_time)

            op_vs_cycle_list_dict[single_op] = list_of_cycle_t_per_op
            # print(op_vs_cycle_list_dict[single_op])
    # print ('op_vs_cycle_list_dict ====', op_vs_cycle_list_dict)

    # write the MAX of cycle time from each list
    if new_last_tested_units_list != []:
        # count = 0
        for single_op in list_of_last_period_ops:
            if op_vs_cycle_list_dict[single_op] != []:
                op_vs_cycle_max_dict[single_op] = round(
                    sum(op_vs_cycle_list_dict[single_op]) / len(op_vs_cycle_list_dict[single_op]), 1)
                # if we want to use MAX cycle time instead replace with below:
                # op_vs_cycle_max_dict[single_op] = (max(op_vs_cycle_list_dict[single_op]))
    # sort the this dict to show only the highest xxx of operations, since this plot may get very large for 21 days
    list_of_sorted_top_cycle_ops = sorted(op_vs_cycle_max_dict.iterkeys(), key=lambda k: op_vs_cycle_max_dict[k],reverse=True)
    # print('list_of_sorted_top_cycle_ops', list_of_sorted_top_cycle_ops)

    # end of a dict for op vs cycle time plot
    # ******************************************************************************************


    # ******************************************************************************************
    # This part will calculate a dict for bench vs execution plot
    # find the benches from last period
    list_of_last_period_bench = set(row[4] for row in new_last_tested_units_list)
    # print(list_of_last_period_bench)

    # count the execution for each bench:
    bench_execution_dict = {}

    # print op_id__per_model_list
    if new_last_tested_units_list:
        bench_execution_dict = {single_bench: sum(1 for single_row in new_last_tested_units_list if single_bench in single_row[4]) for single_bench in list_of_last_period_bench}
        list_of_sorted_bench_executions = sorted(bench_execution_dict, key=lambda k: bench_execution_dict[k], reverse=True)

    
    # for k, d in last_tested_dict.iteritems():
    #     print()
     
    # print(bench_execution_dict)

    # end of dict for bench vs execution plot
    # ******************************************************************************************
    return render_template('main.html', list_of_sorted_bench_executions=list_of_sorted_bench_executions,
                           bench_execution_dict=bench_execution_dict,
                           length_of_last_tested=length_of_last_tested, last_tested_dict=
                           last_tested_dict, dates_execution_dict=
                           dates_execution_dict, dict_of_models_in_dict_of_dates=
                           dict_of_models_in_dict_of_dates, list_of_last_week_dates=list_of_last_week_dates,
                           dict_of_lists_of_model_data=dict_of_lists_of_model_data,
                           dict_of_sn_per_model=dict_of_sn_per_model,
                           length_of_longest_sn_list=length_of_longest_sn_list
                           , namePart_numbers = namePart_numbers
                           , list_of_sorted_top_cycle_ops = list_of_sorted_top_cycle_ops
                           , op_vs_cycle_max_dict = op_vs_cycle_max_dict
                           )
