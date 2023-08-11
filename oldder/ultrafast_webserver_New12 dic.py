from flask import Flask, send_file, render_template, json, request, redirect, Response,url_for, jsonify, session
from flask_caching import Cache
import cx_Oracle
import datetime
from collections import defaultdict
#import configparer
#import shutil
port_flask = 5009
username = "readonly"
password = "re6d0n1y"
dsn = cx_Oracle.makedsn("patdbtdsprd05.li.lumentuminc.net", 1522, "TDSPRD05")
'''
#######################################################
CONFIG_PATH = "C:\\PicoBase\\config\\main_config.ini"
main_config = configparser.ConfigParser()
main_config.read(CONFIG_PATH)

# Load config from main_config.ini --------------------------------------
database_name = main_config['MAIN_CONFIG']['database_name']
server_name = main_config['MAIN_CONFIG']['server_name']
USER = main_config['MAIN_CONFIG']['USER']
PASSWORD = main_config['MAIN_CONFIG']['PASSWORD']
server_address = main_config['MAIN_CONFIG']['server_address']
port_flask = int(main_config['MAIN_CONFIG']['port_flask'])
db_port = int(main_config['MAIN_CONFIG']['port_db'])
custom_days_to_query = main_config['MAIN_CONFIG']['custom_days']
prod_family = main_config['MAIN_CONFIG']['product_family']
'''
####################################################################


app = Flask(__name__, static_url_path='/static')
# cache = Cache(app)
#CORS(app)
#Define the path to the upload folder
app.config['UPLOAD_FOLDER'] = 'static/uploads/'
app.config['CACHE_TYPE'] = 'simple'
# cache.init_app(app)

# app.config['CACHE_TYPE'] = 'simple'
# app.config['CACHE_DEFAULT_TIMEOUT'] = 300
###################################################################
'''
def find_model_per_sn (sn_input):
    section_1 = ""
    section_2 = ""
    section_3 = ""
    section_4 = ""
    list_section_1 = []
    list_section_2 = []
    list_section_3 = []
    list_section_4 = []
    length_section_1 = 0
    length_section_2 = 0
    length_section_3 = 0
    length_section_4 = 0
    combined_classified_list = []

    if ("N1" in sn_input):
        model = "SPA"
        section_1 = "ENGINE INTEGRATION"
        section_2 = "FINAL TEST PRE-BURN-IN"
        section_3 = "FINAL TEST POST-BURN-IN"
        section_4 = "OPTIONAL TEST"
        list_section_1 = ['679', '671', '304', '683', '305', '367', '220', '218']
        list_section_2 = ['314', '401', '402', '303']
        list_section_3 = ['680', '223', '673', '368', '322', '219', '711', '347', '348', '302', '366', '712']
        list_section_4 = ['744', '749', '750', '817']
        length_section_1 = len(list_section_1)
        length_section_2 = len(list_section_2)
        length_section_3 = len(list_section_3)
        length_section_4 = len(list_section_4)
        combined_classified_list = list_section_1 + list_section_2 + list_section_3 + list_section_4

    return model, section_1, section_2, section_3, section_4, list_section_1, list_section_2, list_section_3, list_section_4, length_section_1, length_section_2, length_section_3, length_section_4, combined_classified_list
'''


@app.route('/')
# @cache.cached()
#@app.route('/', methods=['POST'])
def main():

    connection = cx_Oracle.connect(username, password, dsn)
    cursor = connection.cursor()

    txt_query = '''
        SELECT header.SERIALNUMBER,header.PARTNUMBER,header.OPERATION,header.OPERATIONID,header.TESTSTATION,header.STARTTIME,header.RESULT,header.OPERATORID,SYSTIMESTAMP - header.STARTTIME
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

    print (dict_of_lists_of_model_data)
    '''
    # ******************************************************************************************
    # This part will calculate a dict for op vs cycle time plot
    # find the op from last period
    list_of_last_period_ops = []
    if new_last_tested_units_list != []:
        count = 0
        for single_row in new_last_tested_units_list:
            if single_row[2] not in list_of_last_period_ops:
                list_of_last_period_ops.append(str(single_row[2]))
        list_of_last_period_ops = set(list_of_last_period_ops)
        print(list_of_last_period_ops)
    # reset the dict
    # find operation vs cycle time, skip as this time still not available
    op_vs_cycle_list_dict = {}
    op_vs_cycle_max_dict = {}
    if new_last_tested_units_list != []:
        # count = 0
        for single_op in list_of_last_period_ops:
            # init every date key with a new dict of zeros for each model:
            dict_of_models_in_dict_of_dates[single_date] = {}
            list_of_cycle_t_per_op = []
            single_date_count = 0
            for single_row in new_last_tested_units_list:
                if single_op in str(single_row[3]) and str(single_row[6]) == 'PASS':
                    list_of_cycle_t_per_op.append(float(single_row[7]))
            # append the list to the dict
            op_vs_cycle_list_dict[single_op] = (list_of_cycle_t_per_op)
    print (op_vs_cycle_list_dict)

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
    print(list_of_sorted_top_cycle_ops)

    # end of a dict for op vs cycle time plot
    # ******************************************************************************************
    '''

    # ******************************************************************************************
    # This part will calculate a dict for bench vs execution plot
    # find the benches from last period
    list_of_last_period_bench = []
    if new_last_tested_units_list != []:
        count = 0
        for single_row in new_last_tested_units_list:
            if single_row[4] not in list_of_last_period_bench:
                list_of_last_period_bench.append(single_row[4])

        list_of_last_period_bench = set(list_of_last_period_bench)
    print(list_of_last_period_bench)

    # count the execution for each bench:
    bench_execution_dict = {}

    # print op_id__per_model_list
    if new_last_tested_units_list != []:
        # count = 0
        for single_bench in list_of_last_period_bench:

            single_bench_count = 0
            for single_row in new_last_tested_units_list:
                if single_bench in single_row[4]:
                    single_bench_count = single_bench_count + 1
                    bench_execution_dict[single_bench] = single_bench_count

    list_of_sorted_bench_executions = sorted(bench_execution_dict.iterkeys(), key=lambda k: bench_execution_dict[k],
                                             reverse=True)
    
    # for k, d in last_tested_dict.iteritems():
    #     print()
     
    # print(bench_execution_dict)

    # end of dict for bench vs execution plot
    # ******************************************************************************************
    return render_template('index_list_ultra.html', list_of_sorted_bench_executions=list_of_sorted_bench_executions,
                           bench_execution_dict=bench_execution_dict,
                           length_of_last_tested=length_of_last_tested, last_tested_dict=
                           last_tested_dict, dates_execution_dict=
                           dates_execution_dict, dict_of_models_in_dict_of_dates=
                           dict_of_models_in_dict_of_dates, list_of_last_week_dates=list_of_last_week_dates,
                           dict_of_lists_of_model_data=dict_of_lists_of_model_data,
                           dict_of_sn_per_model=dict_of_sn_per_model,
                           length_of_longest_sn_list=length_of_longest_sn_list
                           )

@app.route('/showSignUp', methods=['POST','GET', 'DELETE'])
# @app.route('/showSignUp')

def showSignUp():

    from collections import defaultdict
    dic_allL2 = defaultdict(dict)

    ser_num = request.form['text']
    username = "readonly"
    password = "re6d0n1y"
    dsn = cx_Oracle.makedsn("patdbtdsprd05.li.lumentuminc.net", 1522, "TDSPRD05")

    completion_percentage = 0
    all_header_per_sn_list = []
    connection = cx_Oracle.connect(username, password, dsn)
    cursor = connection.cursor()

    txt_query_L2 = '''
                SELECT header.testheaderid, header.SERIALNUMBER,header.PARTNUMBER,header.OPERATION,header.OPERATIONID,header.TESTSTATION,header.OPERATORID,header.STARTTIME,header.ENDTIME,header.RESULT
                FROM testheader_v       header where header.SERIALNUMBER = '{0}'ORDER BY header.STARTTIME
                '''.format(ser_num)

    cursor.execute(txt_query_L2)
    data = cursor.fetchall()
    for i in data:
        print(i)

    for row in data:
        IDL2 = row[4]
        dic_allL2.setdefault(IDL2, {})
        dic_allL2[IDL2].setdefault(row[1], {
            "testheaderid": row[0],
            "serialnumber": row[1],
            "partnumber": row[2],
            "operation": row[3],
            "operationid": row[4],
            "teststation": row[5],
            "operatorid": row[6],
            "starttime": row[7],
            "endtime": row[8],
            "result": row[9],
            "attempts": 1
        })
    dic_allL2[IDL2][row[1]]["attempts"] += 1
    # print(dic_allL2)


    from collections import Counter

    count_dict = Counter(item[3] for item in data)
    print("count_dict")
    print(count_dict.most_common())  # MODEL: many of MODEL
    print("--------------------------------")


    updated_data = [item + (count_dict[item[3]],) for item in data]
    # print(updated_data) # all data
    updated_data = list(set(updated_data))
    

    deduplicatedL2 = {item[4]: item for item in updated_data}
    # print(deduplicatedL2)
    
    # Retrieve the de-duplicated list of tuples
    all_header_per_sn_list = list(deduplicatedL2.values())

    print("DUT = {}".format(ser_num))
    PartNumber_item = next(iter(deduplicatedL2.values()))[2]
    print("Model = {}".format(PartNumber_item))
    num = len(data)  
    ("Attempts = {} Attempts".format(num))

    num_of_passed = sum(item[9] == 'Passed' for item in data)
    num_of_failed = sum(item[9] == 'Failed' for item in data)
    num_of_aborted = sum(item[9] not in ['Passed', 'Failed'] for item in data)
    if num_of_passed >= num_of_failed and num_of_passed >= num_of_aborted:
        result_of_DUT = "PASS"
    elif num_of_failed > num_of_passed and num_of_failed >= num_of_aborted:
        result_of_DUT = "FAIL"
    else:
        result_of_DUT = "ABORT"

    print("All Result = pass:{} failed:{} aborted:{}".format(num_of_passed, num_of_failed, num_of_aborted))

    #CT_Time
    section = []
    def find_CT_Time():
        for item in deduplicatedL2.values():
            start_time = item[7]
            end_time = item[8]
            minute_time = int((end_time - start_time).total_seconds() / 60)
            section_title = "{} minutes".format(minute_time)
            section.append(section_title)
    find_CT_Time()

    num_attempts = []
    def findAttempts():
        deduplicatedL2_values = deduplicatedL2.values()  
        append_to_num_attempts = num_attempts.append  
        for i in deduplicatedL2_values:
            item_num_attempts = i[10]
            append_to_num_attempts(item_num_attempts)
    findAttempts()

    # check
    check_item = []
    for item in deduplicatedL2.values():
        check_item.append(item[8])

    print("show signup page ",ser_num)

    last_serItem = []
    for item in all_header_per_sn_list:
        # print(item[0])
        last_serItem.append(item[0])



    # -----------------------------------------------------------------------------------------------------------
    # L3 after click green botton

    lst_stepName = []
    section_st = []
    dic_allL3 = defaultdict(dict)
    for IDL3 in last_serItem:

        keyL3 = '''
                select step.testheaderid, step.testheaderstepid, step.serialnumber,step.operationname,step.steptype,step.operationstepname,step.result, step.starttime, step.endtime from testheaderstep_v   step
                where step.testheaderid = :IDL3
                '''
        cursor.execute(keyL3, IDL3=IDL3)
        dataL3 = cursor.fetchall()

        for row in dataL3:
            dic_allL3[IDL3][row[1]] = {
                "testheaderid": row[0],
                "testheaderstepid": row[1],
                "serialnumber": row[2],
                "operationname": row[3],
                "steptype": row[4],
                "operationstepname": row[5],
                "result": row[6],
                "starttime": row[7],
                "endtime": row[8]
            }
        # print(dic_allL3)

        num_data = 0
        for item in dataL3:
            lst_stepName.append(item)
            num_data += 1


    count_prints = 0; lst_stepID = []
    for key, value in dic_allL3.items():
        for inner_key, inner_value in value.items():
            if 'testheaderstepid' in inner_value:
                # print(inner_value['testheaderid'])
                count_prints += 1
                lst_stepID.append(inner_value['testheaderstepid'])
    # print("Total prints:", count_prints)
    # print(lst_stepID)

    

    # -----------------------------------------------------------------------------------------------------------
    # L4 after click Step name



    from collections import defaultdict
    
    dic_allL4 = defaultdict(dict)

    for L4 in lst_stepID:
        # Numeric
        numeric_query = '''
            select param.testheaderstepid, param.parametername, param.steptype, param.valuemean, param.units, param.specmin, param.specmax, param.status, param.compoperator
            from measurementparameter_v param
            where param.testheaderstepid = :L4
        '''
        cursor.execute(numeric_query, L4=L4)
        rows = cursor.fetchall()
        for row in rows:
            dic_allL4[L4][row[1]] = {
                "testheaderstepid": row[0],
                "parametername": row[1],
                "steptype": row[2],
                "valuemean": row[3],
                "units": row[4],
                "specmin": row[5],
                "specmax": row[6],
                "status": row[7],
                "compoperator": row[8]
            }

        # String
        string_query = '''
            select str_param.testheaderstepid, str_param.parametername, str_param.steptype, str_param.valuestring, str_param.result, str_param.units, str_param.status
            from stringmeasurement_v str_param
            where str_param.testheaderstepid = :L4
        '''
        cursor.execute(string_query, L4=L4)
        rows = cursor.fetchall()
        for row in rows:
            dic_allL4[L4][row[1]] = {
                "testheaderstepid": row[0],
                "parametername": row[1],
                "steptype": row[2],
                "valuestring": row[3],
                "result": row[4],
                "units": row[5],
                "status": row[6]
            }

        # Image
        image_query = '''
            select image_param.testheaderstepid, image_param.imageid, image_param.imagename, image_param.filenamelong, image_param.operationstepname, image_param.status
            from imagedata_v image_param
            where image_param.testheaderstepid = :L4
        '''
        cursor.execute(image_query, L4=L4)
        rows = cursor.fetchall()
        for row in rows:
            dic_allL4[L4][row[2]] = {
                "testheaderstepid": row[0],
                "imageid": row[1],
                "imagename": row[2],
                "filenamelong": row[3],
                "operationstepname": row[4],
                "status": row[5]
            }

    cursor.close()
    connection.close()

    empty_keys = [key for key, value in dic_allL4.items() if not value]
    for key in empty_keys:
        del dic_allL4[key]

    json_strL2 = json.dumps(dic_allL2, indent=4)
    # print("json_strL2")
    # print(json_strL2)
#     {
#     "22169499": {
#         "993": {
#             "endtime": "Tue, 11 Jul 2023 11:24:12 GMT",
#             "operation": "Glue Optic M510",
#             "operationid": 993,
#             "operatorid": "84177",
#             "partnumber": "22169499",
#             "result": "Aborted",
#             "serialnumber": "22169499",
#             "starttime": "Tue, 11 Jul 2023 11:22:56 GMT",
#             "testheaderid": 37855315,
#             "teststation": "689R5Z1"
#         },
#         "995": {
#             "endtime": "Tue, 11 Jul 2023 11:21:33 GMT",
#             "operation": "Glue Optic M514",
#             "operationid": 995,
#             "operatorid": "84177",
#             "partnumber": "22169499",
#             "result": "Aborted",
#             "serialnumber": "22169499",
#             "starttime": "Tue, 11 Jul 2023 11:20:43 GMT",
#             "testheaderid": 37854723,
#             "teststation": "689R5Z1"
#         },
#         "7969": {
#             "endtime": "Tue, 11 Jul 2023 11:20:31 GMT",
#             "operation": "CalibrateCarrier",
#             "operationid": 7969,
#             "operatorid": "84177",
#             "partnumber": "22169499",
#             "result": "Passed",
#             "serialnumber": "22169499",
#             "starttime": "Tue, 11 Jul 2023 11:16:06 GMT",
#             "testheaderid": 37854721,
#             "teststation": "689R5Z1"
#         }
#     }
# }
    count_dic_allL2 = sum('operationid' in inner_value for value in dic_allL2.values() for inner_value in value.values())
    # print("Total count_dic_allL2:", count_dic_allL2)

    json_strL3 = json.dumps(dic_allL3, indent=4)
    # print("json_strL3")
    # print(json_strL3)
#     {
#     "37854721": {
#         "45170052": {
#             "endtime": "Tue, 11 Jul 2023 11:20:31 GMT",
#             "operationname": "CalibrateCarrier",
#             "operationstepname": "Watch Probe Tool Process",
#             "result": "Passed",
#             "serialnumber": "22169499",
#             "starttime": "Tue, 11 Jul 2023 11:16:06 GMT",
#             "steptype": "SequenceCall",
#             "testheaderid": 37854721,
#             "testheaderstepid": 45170052
#         },
#         "45170053": {
#             "endtime": "Tue, 11 Jul 2023 11:20:31 GMT",
#             "operationname": "CalibrateCarrier",
#             "operationstepname": "watch carrier calibration  process",
#             "result": "Passed",
#             "serialnumber": "22169499",
#             "starttime": "Tue, 11 Jul 2023 11:16:06 GMT",
#             "steptype": "SequenceCall",
#             "testheaderid": 37854721,
#             "testheaderstepid": 45170053
#         },
#         "45170054": {
#             "endtime": "Tue, 11 Jul 2023 11:20:31 GMT",
#             "operationname": "CalibrateCarrier",
#             "operationstepname": "Watch Probe Tool Process",
#             "result": "Passed",
#             "serialnumber": "22169499",
#             "starttime": "Tue, 11 Jul 2023 11:16:06 GMT",
#             "steptype": "SequenceCall",
#             "testheaderid": 37854721,
#             "testheaderstepid": 45170054
#         },
#         "45170055": {
#             "endtime": "Tue, 11 Jul 2023 11:20:31 GMT",
#             "operationname": "CalibrateCarrier",
#             "operationstepname": "watch carrier calibration  process",
#             "result": "Passed",
#             "serialnumber": "22169499",
#             "starttime": "Tue, 11 Jul 2023 11:16:06 GMT",
#             "steptype": "SequenceCall",
#             "testheaderid": 37854721,
#             "testheaderstepid": 45170055
#         }
#     },
#     "37854723": {
#         "45170063": {
#             "endtime": "Tue, 11 Jul 2023 11:21:33 GMT",
#             "operationname": "Glue Optic M514",
#             "operationstepname": "Select Optic",
#             "result": "Done",
#             "serialnumber": "22169499",
#             "starttime": "Tue, 11 Jul 2023 11:20:43 GMT",
#             "steptype": "Action",
#             "testheaderid": 37854723,
#             "testheaderstepid": 45170063
#         },
#         "45170064": {
#             "endtime": "Tue, 11 Jul 2023 11:21:33 GMT",
#             "operationname": "Glue Optic M514",
#             "operationstepname": "Define Optic",
#             "result": "Done",
#             "serialnumber": "22169499",
#             "starttime": "Tue, 11 Jul 2023 11:20:43 GMT",
#             "steptype": "Action",
#             "testheaderid": 37854723,
#             "testheaderstepid": 45170064
#         },
#         "45170065": {
#             "endtime": "Tue, 11 Jul 2023 11:21:33 GMT",
#             "operationname": "Glue Optic M514",
#             "operationstepname": "Set Dispense Time",
#             "result": "Done",
#             "serialnumber": "22169499",
#             "starttime": "Tue, 11 Jul 2023 11:20:43 GMT",
#             "steptype": "Action",
#             "testheaderid": 37854723,
#             "testheaderstepid": 45170065
#         },
#         "45170066": {
#             "endtime": "Tue, 11 Jul 2023 11:21:33 GMT",
#             "operationname": "Glue Optic M514",
#             "operationstepname": "Call Configure Robot",
#             "result": "Done",
#             "serialnumber": "22169499",
#             "starttime": "Tue, 11 Jul 2023 11:20:43 GMT",
#             "steptype": "Action",
#             "testheaderid": 37854723,
#             "testheaderstepid": 45170066
#         },
#         "45170067": {
#             "endtime": "Tue, 11 Jul 2023 11:21:33 GMT",
#             "operationname": "Glue Optic M514",
#             "operationstepname": "Configure Robot Process",
#             "result": "Passed",
#             "serialnumber": "22169499",
#             "starttime": "Tue, 11 Jul 2023 11:20:43 GMT",
#             "steptype": "SequenceCall",
#             "testheaderid": 37854723,
#             "testheaderstepid": 45170067
#         },
#         "45170068": {
#             "endtime": "Tue, 11 Jul 2023 11:21:33 GMT",
#             "operationname": "Glue Optic M514",
#             "operationstepname": "Call Pickup Optic",
#             "result": "Done",
#             "serialnumber": "22169499",
#             "starttime": "Tue, 11 Jul 2023 11:20:43 GMT",
#             "steptype": "Action",
#             "testheaderid": 37854723,
#             "testheaderstepid": 45170068
#         },
#         "45170069": {
#             "endtime": "Tue, 11 Jul 2023 11:21:33 GMT",
#             "operationname": "Glue Optic M514",
#             "operationstepname": "Set Released",
#             "result": "Aborted",
#             "serialnumber": "22169499",
#             "starttime": "Tue, 11 Jul 2023 11:20:43 GMT",
#             "steptype": "Statement",
#             "testheaderid": 37854723,
#             "testheaderstepid": 45170069
#         }
#     },
#     "37855315": {
#         "45170877": {
#             "endtime": "Tue, 11 Jul 2023 11:24:12 GMT",
#             "operationname": "Glue Optic M510",
#             "operationstepname": "Select Optic",
#             "result": "Done",
#             "serialnumber": "22169499",
#             "starttime": "Tue, 11 Jul 2023 11:22:56 GMT",
#             "steptype": "Action",
#             "testheaderid": 37855315,
#             "testheaderstepid": 45170877
#         },
#         "45170878": {
#             "endtime": "Tue, 11 Jul 2023 11:24:12 GMT",
#             "operationname": "Glue Optic M510",
#             "operationstepname": "Define Optic",
#             "result": "Done",
#             "serialnumber": "22169499",
#             "starttime": "Tue, 11 Jul 2023 11:22:56 GMT",
#             "steptype": "Action",
#             "testheaderid": 37855315,
#             "testheaderstepid": 45170878
#         },
#         "45170879": {
#             "endtime": "Tue, 11 Jul 2023 11:24:12 GMT",
#             "operationname": "Glue Optic M510",
#             "operationstepname": "Set Dispense Time",
#             "result": "Done",
#             "serialnumber": "22169499",
#             "starttime": "Tue, 11 Jul 2023 11:22:56 GMT",
#             "steptype": "Action",
#             "testheaderid": 37855315,
#             "testheaderstepid": 45170879
#         },
#         "45170880": {
#             "endtime": "Tue, 11 Jul 2023 11:24:12 GMT",
#             "operationname": "Glue Optic M510",
#             "operationstepname": "Call Configure Robot",
#             "result": "Done",
#             "serialnumber": "22169499",
#             "starttime": "Tue, 11 Jul 2023 11:22:56 GMT",
#             "steptype": "Action",
#             "testheaderid": 37855315,
#             "testheaderstepid": 45170880
#         },
#         "45170881": {
#             "endtime": "Tue, 11 Jul 2023 11:24:12 GMT",
#             "operationname": "Glue Optic M510",
#             "operationstepname": "Configure Robot Process",
#             "result": "Passed",
#             "serialnumber": "22169499",
#             "starttime": "Tue, 11 Jul 2023 11:22:56 GMT",
#             "steptype": "SequenceCall",
#             "testheaderid": 37855315,
#             "testheaderstepid": 45170881
#         },
#         "45170882": {
#             "endtime": "Tue, 11 Jul 2023 11:24:12 GMT",
#             "operationname": "Glue Optic M510",
#             "operationstepname": "Call Pickup Optic",
#             "result": "Done",
#             "serialnumber": "22169499",
#             "starttime": "Tue, 11 Jul 2023 11:22:56 GMT",
#             "steptype": "Action",
#             "testheaderid": 37855315,
#             "testheaderstepid": 45170882
#         },
#         "45170883": {
#             "endtime": "Tue, 11 Jul 2023 11:24:12 GMT",
#             "operationname": "Glue Optic M510",
#             "operationstepname": "Pickup Optic Process",
#             "result": "Passed",
#             "serialnumber": "22169499",
#             "starttime": "Tue, 11 Jul 2023 11:22:56 GMT",
#             "steptype": "SequenceCall",
#             "testheaderid": 37855315,
#             "testheaderstepid": 45170883
#         },
#         "45170884": {
#             "endtime": "Tue, 11 Jul 2023 11:24:12 GMT", 
#             "operationname": "Glue Optic M510",
#             "operationstepname": "Call Measure Height",
#             "result": "Done",
#             "serialnumber": "22169499",
#             "starttime": "Tue, 11 Jul 2023 11:22:56 GMT",
#             "steptype": "Action",
#             "testheaderid": 37855315,
#             "testheaderstepid": 45170884
#         },
#         "45170885": {
#             "endtime": "Tue, 11 Jul 2023 11:24:12 GMT",
#             "operationname": "Glue Optic M510",
#             "operationstepname": "Set Released",
#             "result": "Aborted",
#             "serialnumber": "22169499",
#             "starttime": "Tue, 11 Jul 2023 11:22:56 GMT",
#             "steptype": "Statement",
#             "testheaderid": 37855315,
#             "testheaderstepid": 45170885
#         }
#     }
# }
    count_dic_allL3 = sum('testheaderstepid' in inner_value for value in dic_allL3.values() for inner_value in value.values())
    # print("Total count_dic_allL3:", count_dic_allL3)

    json_strL4 = json.dumps(dic_allL4, indent=4)
    # print("json_strL4")
    # print(json_strL4)
#     {
#     "45170063": {
#         "Amp1_D__A_": {
#             "compoperator": "LOG",
#             "parametername": "Amp1_D__A_",
#             "specmax": null,
#             "specmin": null,
#             "status": null,
#             "steptype": "Action",
#             "testheaderstepid": 45170063,
#             "units": "NA",
#             "valuemean": 0
#         },
#         "Amp2_D__A_": {
#             "compoperator": "LOG",
#             "parametername": "Amp2_D__A_",
#             "specmax": null,
#             "specmin": null,
#             "status": null,
#             "steptype": "Action",
#             "testheaderstepid": 45170063,
#             "units": "NA",
#             "valuemean": 0
#         },
#         "Amp3_D1__A_": {
#             "compoperator": "LOG",
#             "parametername": "Amp3_D1__A_",
#             "specmax": null,
#             "specmin": null,
#             "status": null,
#             "steptype": "Action",
#             "testheaderstepid": 45170063,
#             "units": "NA",
#             "valuemean": 0
#         },
#         "Amp3_D2__A_": {
#             "compoperator": "LOG",
#             "parametername": "Amp3_D2__A_",
#             "specmax": null,
#             "specmin": null,
#             "status": null,
#             "steptype": "Action",
#             "testheaderstepid": 45170063,
#             "units": "NA",
#             "valuemean": 0
#         },
#         "Amp3_D3__A_": {
#             "compoperator": "LOG",
#             "parametername": "Amp3_D3__A_",
#             "specmax": null,
#             "specmin": null,
#             "status": null,
#             "steptype": "Action",
#             "testheaderstepid": 45170063,
#             "units": "NA",
#             "valuemean": 0
#         },
#         "Amp4_D1__A_": {
#             "compoperator": "LOG",
#             "parametername": "Amp4_D1__A_",
#             "specmax": null,
#             "specmin": null,
#             "status": null,
#             "steptype": "Action",
#             "testheaderstepid": 45170063,
#             "units": "NA",
#             "valuemean": 0
#         },
#         "Amp4_D2__A_": {
#             "compoperator": "LOG",
#             "parametername": "Amp4_D2__A_",
#             "specmax": null,
#             "specmin": null,
#             "status": null,
#             "steptype": "Action",
#             "testheaderstepid": 45170063,
#             "units": "NA",
#             "valuemean": 0
#         },
#         "Amp4_D3__A_": {
#             "compoperator": "LOG",
#             "parametername": "Amp4_D3__A_",
#             "specmax": null,
#             "specmin": null,
#             "status": null,
#             "steptype": "Action",
#             "testheaderstepid": 45170063,
#             "units": "NA",
#             "valuemean": 0
#         },
#         "Carrier_Index": {
#             "compoperator": "LOG",
#             "parametername": "Carrier_Index",
#             "specmax": null,
#             "specmin": null,
#             "status": null,
#             "steptype": "Action",
#             "testheaderstepid": 45170063,
#             "units": "NA",
#             "valuemean": 6
#         },
#         "Distance_to_Sensor": {
#             "compoperator": "LOG",
#             "parametername": "Distance_to_Sensor",
#             "specmax": null,
#             "specmin": null,
#             "status": null,
#             "steptype": "Action",
#             "testheaderstepid": 45170063,
#             "units": "NA",
#             "valuemean": 850
#         },
#         "Gain_Code": {
#             "parametername": "Gain_Code",
#             "result": "Done",
#             "status": null,
#             "steptype": "Action",
#             "testheaderstepid": 45170063,
#             "units": "NA",
#             "valuestring": "1"
#         },
#         "Glue_Gap__mm_": {
#             "compoperator": "LOG",
#             "parametername": "Glue_Gap__mm_",
#             "specmax": null,
#             "specmin": null,
#             "status": null,
#             "steptype": "Action",
#             "testheaderstepid": 45170063,
#             "units": "NA",
#             "valuemean": 0.07
#         },
#         "Jig": {
#             "parametername": "Jig",
#             "result": "Done",
#             "status": null,
#             "steptype": "Action",
#             "testheaderstepid": 45170063,
#             "units": "NA",
#             "valuestring": "N"
#         },
#         "Mount_Type": {
#             "parametername": "Mount_Type",
#             "result": "Done",
#             "status": null,
#             "steptype": "Action",
#             "testheaderstepid": 45170063,
#             "units": "NA",
#             "valuestring": "tower"
#         },
#         "Optic Name": {
#             "parametername": "Optic Name",
#             "result": "Done",
#             "status": null,
#             "steptype": "Action",
#             "testheaderstepid": 45170063,
#             "units": "NA",
#             "valuestring": "M514"
#         },
#         "Optic_Type": {
#             "parametername": "Optic_Type",
#             "result": "Done", 
#             "status": null,
#             "steptype": "Action",
#             "testheaderstepid": 45170063,
#             "units": "NA",
#             "valuestring": "mirror"
#         },
#         "Optimization_Type": {
#             "parametername": "Optimization_Type",
#             "result": "Done",
#             "status": null,
#             "steptype": "Action",
#             "testheaderstepid": 45170063,
#             "units": "NA",
#             "valuestring": "jdppx"
#         },
#         "Pick_up_Height_Offset": {
#             "compoperator": "LOG",
#             "parametername": "Pick_up_Height_Offset",
#             "specmax": null,
#             "specmin": null,
#             "status": null,
#             "steptype": "Action",
#             "testheaderstepid": 45170063,
#             "units": "NA",
#             "valuemean": -4
#         },
#         "Pick_up_Orentation": {
#             "parametername": "Pick_up_Orentation",
#             "result": "Done",
#             "status": null,
#             "steptype": "Action",
#             "testheaderstepid": 45170063,
#             "units": "NA",
#             "valuestring": "B"
#         },
#         "PoD_Div_": {
#             "compoperator": "LOG",
#             "parametername": "PoD_Div_",
#             "specmax": null,
#             "specmin": null,
#             "status": null,
#             "steptype": "Action",
#             "testheaderstepid": 45170063,
#             "units": "NA",
#             "valuemean": 0
#         },
#         "PoD_Rel_P____": {
#             "compoperator": "LOG",
#             "parametername": "PoD_Rel_P____",
#             "specmax": null,
#             "specmin": null,
#             "status": null,
#             "steptype": "Action",
#             "testheaderstepid": 45170063,
#             "units": "NA",
#             "valuemean": 0
#         },
#         "RX": {
#             "compoperator": "LOG",
#             "parametername": "RX",
#             "specmax": null,
#             "specmin": null,
#             "status": null,
#             "steptype": "Action",
#             "testheaderstepid": 45170063,
#             "units": "NA",
#             "valuemean": 0.029
#         },
#         "RY": {
#             "compoperator": "LOG",
#             "parametername": "RY",
#             "specmax": null,
#             "specmin": null,
#             "status": null,
#             "steptype": "Action",
#             "testheaderstepid": 45170063,
#             "units": "NA",
#             "valuemean": 0.027
#         },
#         "RZ": {
#             "compoperator": "LOG",
#             "parametername": "RZ",
#             "specmax": null,
#             "specmin": null,
#             "status": null,
#             "steptype": "Action",
#             "testheaderstepid": 45170063,
#             "units": "NA",
#             "valuemean": -46.808
#         },
#         "Rigol__A_": {
#             "compoperator": "LOG",
#             "parametername": "Rigol__A_",
#             "specmax": null,
#             "specmin": null,
#             "status": null,
#             "steptype": "Action",
#             "testheaderstepid": 45170063,
#             "units": "NA",
#             "valuemean": 0
#         },
#         "Seeder_D__A_": {
#             "compoperator": "LOG",
#             "parametername": "Seeder_D__A_",
#             "specmax": null,
#             "specmin": null,
#             "status": null,
#             "steptype": "Action",
#             "testheaderstepid": 45170063,
#             "units": "NA",
#             "valuemean": 0
#         },
#         "Sidemount_Side": {
#             "parametername": "Sidemount_Side",
#             "result": "Done",
#             "status": null,
#             "steptype": "Action",
#             "testheaderstepid": 45170063,
#             "units": "NA",
#             "valuestring": "C"
#         },
#         "X": {
#             "compoperator": "LOG",
#             "parametername": "X",
#             "specmax": null,
#             "specmin": null,
#             "status": null,
#             "steptype": "Action",
#             "testheaderstepid": 45170063,
#             "units": "NA",
#             "valuemean": 412.346
#         },
#         "Y": {
#             "compoperator": "LOG",
#             "parametername": "Y",
#             "specmax": null,
#             "specmin": null,
#             "status": null,
#             "steptype": "Action",
#             "testheaderstepid": 45170063,
#             "units": "NA",
#             "valuemean": 37.233
#         },
#         "Z": {
#             "compoperator": "LOG",
#             "parametername": "Z",
#             "specmax": null,
#             "specmin": null,
#             "status": null,
#             "steptype": "Action",
#             "testheaderstepid": 45170063,
#             "units": "NA",
#             "valuemean": -1.77
#         }
#     },
#     "45170877": {
#         "Amp1_D__A_": {
#             "compoperator": "LOG",
#             "parametername": "Amp1_D__A_",
#             "specmax": null,
#             "specmin": null,
#             "status": null, 
#             "steptype": "Action",
#             "testheaderstepid": 45170877,
#             "units": "NA",
#             "valuemean": 0
#         },
#         "Amp2_D__A_": {
#             "compoperator": "LOG",
#             "parametername": "Amp2_D__A_",
#             "specmax": null,
#             "specmin": null,
#             "status": null,
#             "steptype": "Action",
#             "testheaderstepid": 45170877,
#             "units": "NA",
#             "valuemean": 0
#         },
#         "Amp3_D1__A_": {
#             "compoperator": "LOG",
#             "parametername": "Amp3_D1__A_",
#             "specmax": null,
#             "specmin": null,
#             "status": null,
#             "steptype": "Action",
#             "testheaderstepid": 45170877,
#             "units": "NA",
#             "valuemean": 0
#         },
#         "Amp3_D2__A_": {
#             "compoperator": "LOG",
#             "parametername": "Amp3_D2__A_",
#             "specmax": null,
#             "specmin": null,
#             "status": null,
#             "steptype": "Action",
#             "testheaderstepid": 45170877,
#             "units": "NA",
#             "valuemean": 0
#         },
#         "Amp3_D3__A_": {
#             "compoperator": "LOG",
#             "parametername": "Amp3_D3__A_",
#             "specmax": null,
#             "specmin": null,
#             "status": null,
#             "steptype": "Action",
#             "testheaderstepid": 45170877,
#             "units": "NA",
#             "valuemean": 0
#         },
#         "Amp4_D1__A_": {
#             "compoperator": "LOG",
#             "parametername": "Amp4_D1__A_",
#             "specmax": null,
#             "specmin": null,
#             "status": null,
#             "steptype": "Action",
#             "testheaderstepid": 45170877,
#             "units": "NA",
#             "valuemean": 0
#         },
#         "Amp4_D2__A_": {
#             "compoperator": "LOG",
#             "parametername": "Amp4_D2__A_",
#             "specmax": null,
#             "specmin": null,
#             "status": null,
#             "steptype": "Action",
#             "testheaderstepid": 45170877,
#             "units": "NA",
#             "valuemean": 0
#         },
#         "Amp4_D3__A_": {
#             "compoperator": "LOG",
#             "parametername": "Amp4_D3__A_",
#             "specmax": null,
#             "specmin": null,
#             "status": null,
#             "steptype": "Action",
#             "testheaderstepid": 45170877,
#             "units": "NA",
#             "valuemean": 0
#         },
#         "Carrier_Index": {
#             "compoperator": "LOG",
#             "parametername": "Carrier_Index",
#             "specmax": null,
#             "specmin": null,
#             "status": null,
#             "steptype": "Action",
#             "testheaderstepid": 45170877,
#             "units": "NA",
#             "valuemean": 4
#         },
#         "Distance_to_Sensor": {
#             "compoperator": "LOG",
#             "parametername": "Distance_to_Sensor",
#             "specmax": null,
#             "specmin": null,
#             "status": null,
#             "steptype": "Action",
#             "testheaderstepid": 45170877,
#             "units": "NA",
#             "valuemean": 350
#         },
#         "Gain_Code": {
#             "parametername": "Gain_Code",
#             "result": "Done",
#             "status": null,
#             "steptype": "Action",
#             "testheaderstepid": 45170877,
#             "units": "NA",
#             "valuestring": "1"
#         },
#         "Glue_Gap__mm_": {
#             "compoperator": "LOG",
#             "parametername": "Glue_Gap__mm_",
#             "specmax": null,
#             "specmin": null,
#             "status": null,
#             "steptype": "Action",
#             "testheaderstepid": 45170877,
#             "units": "NA",
#             "valuemean": 0.07
#         },
#         "Jig": {
#             "parametername": "Jig",
#             "result": "Done",
#             "status": null,
#             "steptype": "Action",
#             "testheaderstepid": 45170877,
#             "units": "NA",
#             "valuestring": "N"
#         },
#         "Mount_Type": {
#             "parametername": "Mount_Type",
#             "result": "Done",
#             "status": null,
#             "steptype": "Action",
#             "testheaderstepid": 45170877,
#             "units": "NA",
#             "valuestring": "tower"
#         },
#         "Optic Name": {
#             "parametername": "Optic Name",
#             "result": "Done",
#             "status": null,
#             "steptype": "Action",
#             "testheaderstepid": 45170877,
#             "units": "NA",
#             "valuestring": "M510"
#         },
#         "Optic_Type": {
#             "parametername": "Optic_Type",
#             "result": "Done",
#             "status": null,
#             "steptype": "Action",
#             "testheaderstepid": 45170877,
#             "units": "NA",
#             "valuestring": "mirror"
#         }, 
#         "Optimization_Type": {
#             "parametername": "Optimization_Type",
#             "result": "Done",
#             "status": null,
#             "steptype": "Action",
#             "testheaderstepid": 45170877,
#             "units": "NA",
#             "valuestring": "power"
#         },
#         "Pick_up_Height_Offset": {
#             "compoperator": "LOG",
#             "parametername": "Pick_up_Height_Offset",
#             "specmax": null,
#             "specmin": null,
#             "status": null,
#             "steptype": "Action",
#             "testheaderstepid": 45170877,
#             "units": "NA",
#             "valuemean": -2
#         },
#         "Pick_up_Orentation": {
#             "parametername": "Pick_up_Orentation",
#             "result": "Done",
#             "status": null,
#             "steptype": "Action",
#             "testheaderstepid": 45170877,
#             "units": "NA",
#             "valuestring": "B"
#         },
#         "PoD_Div_": {
#             "compoperator": "LOG",
#             "parametername": "PoD_Div_",
#             "specmax": null,
#             "specmin": null,
#             "status": null,
#             "steptype": "Action",
#             "testheaderstepid": 45170877,
#             "units": "NA",
#             "valuemean": 0
#         },
#         "PoD_Rel_P____": {
#             "compoperator": "LOG",
#             "parametername": "PoD_Rel_P____",
#             "specmax": null,
#             "specmin": null,
#             "status": null,
#             "steptype": "Action", 
#             "testheaderstepid": 45170877,
#             "units": "NA",
#             "valuemean": 0
#         },
#         "RX": {
#             "compoperator": "LOG",
#             "parametername": "RX",
#             "specmax": null,
#             "specmin": null,
#             "status": null,
#             "steptype": "Action",
#             "testheaderstepid": 45170877,
#             "units": "NA",
#             "valuemean": 0
#         },
#         "RY": {
#             "compoperator": "LOG",
#             "parametername": "RY",
#             "specmax": null,
#             "specmin": null,
#             "status": null,
#             "steptype": "Action",
#             "testheaderstepid": 45170877,
#             "units": "NA",
#             "valuemean": 0
#         },
#         "RZ": {
#             "compoperator": "LOG",
#             "parametername": "RZ",
#             "specmax": null,
#             "specmin": null,
#             "status": null,
#             "steptype": "Action",
#             "testheaderstepid": 45170877,
#             "units": "NA",
#             "valuemean": -0.159
#         },
#         "Rigol__A_": {
#             "compoperator": "LOG",
#             "parametername": "Rigol__A_",
#             "specmax": null,
#             "specmin": null,
#             "status": null,
#             "steptype": "Action",
#             "testheaderstepid": 45170877,
#             "units": "NA",
#             "valuemean": 0
#         },
#         "Seeder_D__A_": {
#             "compoperator": "LOG",
#             "parametername": "Seeder_D__A_",
#             "specmax": null,
#             "specmin": null,
#             "status": null,
#             "steptype": "Action",
#             "testheaderstepid": 45170877,
#             "units": "NA",
#             "valuemean": 0
#         },
#         "Sidemount_Side": {
#             "parametername": "Sidemount_Side",
#             "result": "Done",
#             "status": null,
#             "steptype": "Action",
#             "testheaderstepid": 45170877,
#             "units": "NA",
#             "valuestring": "C"
#         },
#         "X": {
#             "compoperator": "LOG",
#             "parametername": "X",
#             "specmax": null,
#             "specmin": null,
#             "status": null,
#             "steptype": "Action",
#             "testheaderstepid": 45170877,
#             "units": "NA",
#             "valuemean": 457
#         },
#         "Y": {
#             "compoperator": "LOG",
#             "parametername": "Y",
#             "specmax": null,
#             "specmin": null,
#             "status": null,
#             "steptype": "Action",
#             "testheaderstepid": 45170877,
#             "units": "NA",
#             "valuemean": 68.975
#         },
#         "Z": {
#             "compoperator": "LOG",
#             "parametername": "Z",
#             "specmax": null,
#             "specmin": null,
#             "status": null,
#             "steptype": "Action",
#             "testheaderstepid": 45170877,
#             "units": "NA",
#             "valuemean": -1.22
#         }
#     }
# }
    count_dic_allL4 = sum('testheaderstepid' in inner_value for value in dic_allL4.values() for inner_value in value.values())
    # print("Total count_dic_allL4:", count_dic_allL4)

    print("Done")


    return render_template('signup_new_09.html',all_header_per_sn_list = all_header_per_sn_list
            , serial_num = ser_num, num_attempts = num_attempts, PartNumber_item = PartNumber_item
            , check_item = check_item
            , result_of_DUT = result_of_DUT
            , CT_Time = section
            ########L3
            , dic_allL2 = dic_allL2, count_dic_allL2 = count_dic_allL2
            ########L3
            , dic_allL3 = dic_allL3, count_dic_allL3 = count_dic_allL3
            , lst_stepName = lst_stepName
            ########L4
            , dic_allL4 = dic_allL4, count_dic_allL4 = count_dic_allL4
            )

@app.route('/show_all_operation_attempts', methods=['POST','GET', 'DELETE'])


def show_all_operation_attempts():
    print ("show_all_operation_attempts")

@app.route('/Chart2', methods=['GET', 'POST'])
def Chart2():
   
    
    if request.method == "POST":
        text = request.form['text3']
    return_it = text
    import shutil
    import os.path
    # removing files if it already exist
    if (os.path.exists('C:\\Inspector\\Static\\pc22.bmp')):
        os.remove('C:\\Inspector\\Static\\pc22.bmp')
    if (os.path.exists('C:\\Inspector\\Static\\pc11.png')):
        os.remove('C:\\Inspector\\Static\\pc11.png')    
    #check if it's bmp or png and copy to static folder
    find_bmp = text.find('bmp')
    if find_bmp != -1:
        shutil.copy(text, 'C:\\Inspector\\Static\\pc22.bmp')
        return_it = 'pc22.bmp'
    find_png = text.find('png')
    if find_png != -1:
        import shutil, os
        shutil.copy(text, 'C:\\Inspector\\Static\\pc11.png')
        return_it = 'pc11.png'

    return render_template('thermal_image2.html' , return_it = return_it)

@app.route('/fetch_file', methods=['GET', 'POST'])
def fetch_file():
   
    
    if request.method == "POST":
        text = request.form['filename']
    return_it = text
    # time_string = str(datetime.now())

    # ip = request.remote_addr
    # hostname = ('host-not-found')
    # try:
    #     #hostname = socket.gethostbyaddr(ip)
    #     print 'hostname search canceled'
    # except:
    #     print 'hostname error'
            
    # file = open('C:\\Inspector\\log\\'+"fetch_file.txt", "a")

    # file.write(time_string+' - '+ip+' - '+hostname[0]+ ' - '+text  +"\n")

    # file.close()
    # #######Added to support Cache######## -Ko 2/19/2022
    # try:
    #    user = session["USERNAME"]
    # except KeyError:
    #     print ('User is not found')
    #     hostname = socket.gethostbyaddr(ip)
    #     user = str(hostname[0])
    #     session["USERNAME"] = user
    # #####################################
    # store_user_action(user,'FETCH_FILE',text)
    try:
        return send_file(text, as_attachment=True)
    except Exception as e:
        return str(e)
    

if __name__ == "__main__":
    app.secret_key = 'super secret key'
    app.run(host="localhost", port=port_flask, threaded=True,debug=True)