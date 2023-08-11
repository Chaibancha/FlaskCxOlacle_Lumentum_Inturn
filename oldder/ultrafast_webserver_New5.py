from flask import Flask, send_file, render_template, json, request, redirect, Response,url_for, jsonify, session
import cx_Oracle
import datetime
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

#cache = Cache()
app = Flask(__name__, static_url_path='/static')
#CORS(app)
#Define the path to the upload folder
app.config['UPLOAD_FOLDER'] = 'static/uploads/'
app.config['CACHE_TYPE'] = 'simple'
#cache.init_app(app)
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
        print(list_of_last_week_models)
        print(dict_of_sn_per_model)

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

    print(dict_of_sn_per_model)

    # reset_models dict with 0 to be used as counters     :
    dict_of_models = {}
    dict_of_lists_of_model_data = {}
    for ind_model in list_of_last_week_models:
        dict_of_models[ind_model] = 0
        dict_of_lists_of_model_data[ind_model] = []
    print(dict_of_lists_of_model_data)

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

    print(dict_of_models_in_dict_of_dates)
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
    print(bench_execution_dict)

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

    ser_num = request.form['text']
    completion_percentage = 0

    all_header_per_sn_list = []
    connection = cx_Oracle.connect(username, password, dsn)
    cursor = connection.cursor()

    txt_query_L2 = '''
                SELECT header.testheaderid,header.SERIALNUMBER,header.PARTNUMBER,header.OPERATION,header.OPERATIONID,header.TESTSTATION,header.STARTTIME,header.ENDTIME,header.RESULT,header.OPERATORID 
            FROM testheader_v header WHERE  header.SERIALNUMBER = '{0}' ORDER BY header.STARTTIME
                '''.format(ser_num)

    cursor.execute(txt_query_L2)
    data = cursor.fetchall()
    cursor.close()
    connection.close()

    # Count duplicates and append count as the last index
    count_dict = {}
    for item in data:
        key = item[3]  # Use the operation name as the key for counting duplicates
        #print(key)
        if key in count_dict:
            count_dict[key] += 1
        else:
            count_dict[key] = 1
    # print (count_dict) # MODEL : many of MODEL
    updated_data = [item + (count_dict[item[3]],) for item in data]
    # print(updated_data) # all data
    # Remove duplicated lists
    # print('remove dup')
    # updated_data = list(set(updated_data))

    
    check = ''; result_of_DUT = ''
    def find_check_L2():
        num_of_passed = 0; num_of_failed = 0; num_of_aborted = 0
        for item in data:
            check = item[8]
            if check == 'Passed':
                num_of_passed += 1
            elif check == 'Failed':
                num_of_failed += 1
            else:
                num_of_aborted += 1

        if num_of_passed >= num_of_failed:
            if num_of_passed >= num_of_aborted:
                result_of_DUT = "PASS"
            else: 
                result_of_DUT = "ABORT" 
        elif num_of_failed > num_of_passed:
            if num_of_failed >= num_of_aborted:
                result_of_DUT = "FAIL"
            else: 
                result_of_DUT = "ABORT" 
        else: 
            result_of_DUT = "ABORT" 
        print("pass:{} failed:{} aborted:{} ".format(num_of_passed, num_of_failed, num_of_aborted))
    find_check_L2()

    # print(updated_data)
    deduplicated = {item[3]: item for item in updated_data}

    # Retrieve the de-duplicated list of tuples
    all_header_per_sn_list = list(deduplicated.values())

    #CT_Time
    section = []
    def find_CT_Time():
        for item in deduplicated.values():
            start_time = item[6]
            end_time = item[7]
            minute_time = int((end_time - start_time).total_seconds() / 60)

            section_title = "{} minutes".format(minute_time)
            # print(section_title)
            section.append(section_title)
            # section_item = {
            #     'minutes': minute_time,
            #     'attempts': item[9],
            #     'opertion_id': item[2],
            #     'opertion_name': item[3]
            # }

            # if section_title in section:
            #     section[section_title].append(section_item)
            # else:
            #     section[section_title] = [section_item]
    find_CT_Time()

    # print(all_header_per_sn_list)
    num_item = 5
    for row in all_header_per_sn_list:
        print (row)
        num_item += 1

    #Attempts
    num_attempts = []
    def findAttempts():
        for i in deduplicated.values():
            item_num_attempts = i[10]
            # print(item_num_attempts)
            num_attempts.append(item_num_attempts)
    findAttempts()

    # Oparation_id, name
    Oparation_id = []
    Oparation_name = []
    def findOparation():
        for i in deduplicated.values():
            item_id = i[4]
            item_name = i[3]
            # print(item_id)
            Oparation_id.append(item_id)
            Oparation_name.append(item_name)
    findOparation()

    # check
    check_item = []
    for i in deduplicated.values():
        item_checked = i[8]
        check_item.append(item_checked)

    print("show signup page",ser_num)

    # -----------------------------------------------------------------------------------------------------------


    return render_template('signup_new_06.html',all_header_per_sn_list = all_header_per_sn_list
            , serial_num = ser_num, num_attempts = num_attempts
            , Oparation_id = Oparation_id, Oparation_name = Oparation_name
            , items = num_item, check_item = check_item
            , model_to_print = key
            , result_of_DUT = result_of_DUT
            , CT_Time = section
            ########L3
            )

if __name__ == "__main__":
    app.secret_key = 'super secret key'
    app.run(host="localhost", port=port_flask, threaded=True,debug=True)