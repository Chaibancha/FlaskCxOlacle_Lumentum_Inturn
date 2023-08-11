from main import main_bp
from . import main_bp
from flask import render_template
from flask import Flask, send_file, render_template, json, request, redirect, Response,url_for, jsonify, session
from flask_caching import Cache
import cx_Oracle
import datetime
import json
from collections import defaultdict
from collections import Counter
import csv
from datetime import datetime, timedelta

show_signup_bp = Blueprint('show_signup', __name__, template_folder='templates')

with open('part_number_config.json') as f:
    namePart_numbers = json.load(f)

from collections import defaultdict
dic_all = defaultdict(dict)
@app.route('/showSignUp', methods=['POST','GET', 'DELETE'])
def showSignUp():

    
    ser_num = request.form['text']
    username = "readonly"
    password = "re6d0n1y"
    dsn = cx_Oracle.makedsn("patdbtdsprd05.li.lumentuminc.net", 1522, "TDSPRD05")

    completion_percentage = 0
    all_header_per_sn_list = []
    connection = cx_Oracle.connect(username, password, dsn)
    cursor = connection.cursor()


    txt_query_L2 = '''
                SELECT header.testheaderid, header.SERIALNUMBER,header.PARTNUMBER,header.OPERATION,header.OPERATIONID,header.TESTSTATION,header.STARTTIME,header.ENDTIME,header.RESULT,header.OPERATORID
                FROM testheader_v       header where header.SERIALNUMBER = '{0}'ORDER BY header.STARTTIME
                '''.format(ser_num)

    cursor.execute(txt_query_L2)
    data = cursor.fetchall()
    cursor.close()
    connection.close()


    

    count_dict = Counter(item[3] for item in data)
    print("count_dict")
    print(count_dict.most_common())  # MODEL: many of MODEL
    print("--------------------------------")


    updated_data = [item + (count_dict[item[3]],) for item in data]
    # print('updated_data1', updated_data)
    # print(updated_data) # all data
    # Remove duplicated lists
    # print('remove dup')
    # updated_data = list(set(updated_data))

    # for k in updated_data:
    #     print(k)


    deduplicated = {item[4]: item for item in updated_data}
    PARTNUMBER_item = None
    for k, item in deduplicated.items():
        if PARTNUMBER_item is None:
            PARTNUMBER_item = item[2]
    op_order = namePart_numbers[PARTNUMBER_item]["op_order"]
    print(op_order)


    # dic_compL2 = {"op_order" : [], "unknow" : []}
    # for k, v in deduplicated.items():
    #     dic_forloop = {k: v}
    #     if k in op_order:
    #         dic_compL2["op_order"].append(dic_forloop)
    #     else:
    #         dic_compL2["unknow"].append(dic_forloop)
    # print("dic_compL2", dic_compL2)

    # print("dic get ==", dic_compL2["op_order"])

    # print("i forLoop")
    # for i in dic_compL2["op_order"]:
    #     if 55 in i:
    #         print("i==", i.get(55)[3])

    print("deduplicated")
    for k ,v in deduplicated.items():
        print(k, v)
    
    # sorted_dict_by_key = {}
    # for key in op_order:
    #     sorted_dict_by_key[key] = deduplicated[key]
    # # for key in deduplicated:
    # #     if key not in op_order:
    # #         sorted_dict_by_key[key] = deduplicated[key]
    # sorted_dict_by_key.update((key, deduplicated[key]) for key in deduplicated if key not in op_order)

    # print("sorted_dict_by_key")
    # for key, value in sorted_dict_by_key.items():
    #     print(key, value)
    # # print(sorted_dict_by_key)

    
    
    

    
    # Retrieve the de-duplicated list of tuples
    all_header_per_sn_list = list(deduplicated.values())

    num_item = 5 + len(all_header_per_sn_list)
    print("DUT = {}".format(ser_num))
    PartNumber_item = next(iter(deduplicated.values()))[2]
    print("Model = {}".format(PartNumber_item))
    num = len(deduplicated.items())  
    print("Attempts = {} Attempts".format(num))
    

    

    num_of_passed = sum(item[8] == 'Passed' for k, item in deduplicated.items())
    num_of_failed = sum(item[8] == 'Failed' for k, item in deduplicated.items())
    num_of_aborted = sum(item[8] not in ['Passed', 'Failed'] for k, item in deduplicated.items())

    if num_of_passed >= num_of_failed and num_of_passed >= num_of_aborted and num_of_failed == 0 and num_of_aborted == 0:
        result_of_DUT = "PASS"
    else:
        result_of_DUT = "FAIL"
    print("All Result = pass:{} failed:{} aborted:{}".format(num_of_passed, num_of_failed, num_of_aborted))

    # percentage
    percentageInOr_der = (sum(1 for k, item in deduplicated.items() if k in op_order and item[8] == 'Passed') / float(num)) * 100
    percentageInOr_der_rounded = round(percentageInOr_der, 2)
    print("Percentage of Passed: {}%".format(percentageInOr_der_rounded))
    
    #CT_Time
    section = []
    def find_CT_Time():
        for j in op_order:
            for item in deduplicated.values():
                if item[4] == j:
                    start_time = item[6]
                    end_time = item[7]
                    minute_time = int((end_time - start_time).total_seconds() / 60)
                    section_title = "{} minutes".format(minute_time)
                    section.append(section_title)
        for item in deduplicated.values():
            if item[4] not in op_order:
                start_time = item[6]
                end_time = item[7]
                minute_time = int((end_time - start_time).total_seconds() / 60)

                section_title = "{} minutes".format(minute_time)
                section.append(section_title)
        # for item in deduplicated.values():
        #     start_time = item[6]
        #     end_time = item[7]
        #     minute_time = int((end_time - start_time).total_seconds() / 60)

        #     section_title = "{} minutes".format(minute_time)
        #     section.append(section_title)
            # print(item, section_title)
        # for i in section:
        #     print(i)
            
    find_CT_Time()

    num_attempts = []

    def findAttempts():
        deduplicated_values = deduplicated.values()  
        append_to_num_attempts = num_attempts.append  
        # for i in deduplicated_values:
        #     item_num_attempts = i[10]
        #     append_to_num_attempts(item_num_attempts)
        for j in op_order:
            for i in deduplicated.values():
                if i[4] == j:
                    item_num_attempts = i[10]
                    append_to_num_attempts(item_num_attempts)
        for i in deduplicated.values():
            if i[4] not in op_order:
                item_num_attempts = i[10]
                append_to_num_attempts(item_num_attempts)


    findAttempts()


    Oparation_id = []
    Oparation_name = []
    Operation_headerid = []
    def findOparation2():
        deduplicated_values = deduplicated.values()  
        append_to_Oparation_id = Oparation_id.append  
        append_to_Oparation_name = Oparation_name.append
        append_to_Operation_headerid = Operation_headerid.append  

        # for i in deduplicated_values:
        #     item_id = i[4]
        #     item_name = i[3]
        #     item_testheaderid = i[0]
        #     append_to_Oparation_id(item_id)
        #     append_to_Oparation_name(item_name)
        #     append_to_Operation_headerid(item_testheaderid)
        for j in op_order:
            for i in deduplicated.values():
                if i[4] == j:
                    item_id = i[4]
                    item_name = i[3]
                    item_testheaderid = i[0]
                    append_to_Oparation_id(item_id)
                    append_to_Oparation_name(item_name)
                    append_to_Operation_headerid(item_testheaderid)
        for i in deduplicated.values():
            if i[4] not in op_order:
                item_id = i[4]
                item_name = i[3]
                item_testheaderid = i[0]
                append_to_Oparation_id(item_id)
                append_to_Oparation_name(item_name)
                append_to_Operation_headerid(item_testheaderid)

    findOparation2()
    print("Oparation_id", Oparation_id)
    print("Oparation_name", Oparation_name)
    print("Operation_headerid", Operation_headerid)

    # print("op_order")
    # for i in op_order:
    #     for j in deduplicated.values():
    #         if j[4] == i:
    #             print(i)
    # print("op_orderv2")
    # for i in deduplicated.values():
    #     if i[4] not in op_order:
    #         print(i[4]) 


    dic_allL2 = {}
    # print("dic_allL2")
    def findOparation():
        deduplicated_values = deduplicated.values()
        
        for i in deduplicated_values:
            testheaderid = i[0]
            SERIALNUMBER = i[1]
            PARTNUMBER = i[2]
            OPERATION = i[3]
            OPERATIONID = i[4]
            TESTSTATION = i[5]
            STARTTIME = i[6]
            ENDTIME = i[7]
            RESULT = i[8]
            OPERATORID = i[9]
            MINUTE_TIME = (ENDTIME - STARTTIME).total_seconds() / 60
            ATTEMPTS = i[10]

            dic_allL2[testheaderid] = {
                "testheaderid": testheaderid
                , "SERIALNUMBER": SERIALNUMBER
                , "PARTNUMBER": PARTNUMBER
                , "OPERATION": OPERATION
                , "OPERATIONID": OPERATIONID
                , "TESTSTATION": TESTSTATION
                , "STARTTIME": STARTTIME
                , "ENDTIME": ENDTIME
                , "RESULT": RESULT
                , "OPERATORID": OPERATORID
                , "MINUTE_TIME": MINUTE_TIME
                , "ATTEMPTS": ATTEMPTS
            }

    findOparation()
    
    # for k, v in dic_allL2.items():
    #     print("{} {}".format(k, v))

    # check
    check_item = []
    # check_item = [i[8] for i in deduplicated.values()]  
    for j in op_order:
            for i in deduplicated.values():
                if i[4] == j:
                    check = i[8]
                    check_item.append(check)
    for i in deduplicated.values():
        if i[4] not in op_order:
            check = i[8]
            check_item.append(check)


    # for i in deduplicated.values():
    #     print(i)

    print("show signup page ",ser_num)

    # -----------------------------------------------------------------------------------------------------------
    # L3 after click green botton

    from future_builtins import map
    from itertools import repeat
    from operator import itemgetter

    key_sql_L3 = {item[4]: item for item in updated_data}
    lst_key_sql_L3 = list(map(itemgetter(4), key_sql_L3.values()))

    lst_sernum_L3 = []
    lst_opID = []
    lst_serItem = []

    connectionL3 = cx_Oracle.connect(username, password, dsn)
    cursorL3 = connectionL3.cursor()

    for opID in lst_key_sql_L3:
        cursorL3.execute(txt_query_L2)
        data = cursorL3.fetchall()

        # Count duplicates and append count as the last index
        count_dictL3 = {}
        for item in data:
            key = item[4]  # Use the operation name as the key for counting duplicates
            count_dictL3[key] = count_dictL3.get(key, 0) + 1

        updated_dataL3 = []
        for item in data:
            if item[4] == opID:
                updated_item = item + (count_dictL3[item[4]],)
                updated_dataL3.append(updated_item)

        for item in updated_dataL3:
            ser_num_L3 = item[0]
            lst_serItem.append(item)
            lst_sernum_L3.append(ser_num_L3)

        lst_opID.append(opID)

    cursorL3.close()
    connectionL3.close()


    # -----------------------------------------------------------------------------------------------------------
    # L3 after click green botton
    last_serItemData = []
    for find_last_item in lst_serItem:
        is_duplicate = False
        for i in range(len(last_serItemData)):
            if find_last_item[4] == last_serItemData[i][4]:
                last_serItemData[i] = find_last_item
                is_duplicate = True
                break
        if not is_duplicate:
            last_serItemData.append(find_last_item)

    last_serItem = [item[0] for item in last_serItemData]
    print("last_serItem", last_serItem)



    lst_stepName = []
    section_st = []

    for IDL4 in last_serItem:
        connectionL4 = cx_Oracle.connect(username, password, dsn)
        cursorL4 = connectionL4.cursor()
        keyL3 = '''
                select step.testheaderid, step.testheaderstepid, step.serialnumber,step.operationname,step.steptype,step.operationstepname,step.result, step.starttime, step.endtime from testheaderstep_v   step
                where step.testheaderid = :IDL4
                '''
        cursorL4.execute(keyL3, IDL4=IDL4)
        dataL4 = cursorL4.fetchall()
        cursorL4.close()
        connectionL4.close()

        num_data = 0
        for item in dataL4:
            lst_stepName.append(item)
            num_data += 1

        count_dictL4 = {}
        for item in dataL4:
            key = item[4]  # Use the operation name as the key for counting duplicates
            if key in count_dict:
                count_dictL4[key] += 1
            else:
                count_dictL4[key] = 1

        updated_dataL4 = [item + (count_dictL4[item[4]],) for item in dataL4]

    num_lst_stepName = len(lst_stepName)
    lst_stepID = [item[1] for item in lst_stepName]

    

    # -----------------------------------------------------------------------------------------------------------
    # L4 after click Step name

    connection = cx_Oracle.connect(username, password, dsn)
    cursor = connection.cursor()

    for L4 in lst_stepID:
        # Numeric
        numeric_query = '''
            select param.testheaderstepid, param.parametername, param.steptype, param.valuemean, param.units, param.specmin
            , param.specmax, param.status, param.compoperator, param.testheaderid, param.operationname, param.starttime
            , param.endtime, param.operatorid, param.teststation
            from measurementparameter_v param
            where param.testheaderstepid = :L4
        '''
        cursor.execute(numeric_query, L4=L4)
        rows = cursor.fetchall()
        for row in rows:
            dic_all[L4][row[1]] = {
                "testheaderstepid": row[0],
                "parametername": row[1],
                "steptype": row[2],
                "valuemean": row[3],
                "units": row[4],
                "specmin": row[5],
                "specmax": row[6],
                "status": row[7],
                "compoperator": row[8],
                "testheaderid": row[9],
                "operationname": row[10],
                "starttime": row[11],
                "endtime": row[12],
                "operatorid": row[13],
                "teststation": row[14]
                
            }

        # String
        string_query = '''
            select str_param.testheaderstepid, str_param.parametername, str_param.steptype, str_param.valuestring, str_param.result
            , str_param.units, str_param.status, str_param.testheaderid, str_param.operationname, str_param.starttime
            , str_param.endtime, str_param.operatorid, str_param.teststation
            from stringmeasurement_v str_param
            where str_param.testheaderstepid = :L4
        '''
        cursor.execute(string_query, L4=L4)
        rows = cursor.fetchall()
        for row in rows:
            dic_all[L4][row[1]] = {
                "testheaderstepid": row[0],
                "parametername": row[1],
                "steptype": row[2],
                "valuestring": row[3],
                "result": row[4],
                "units": row[5],
                "status": row[6],
                "testheaderid": row[7],
                "operationname": row[8],
                "starttime": row[9],
                "endtime": row[10],
                "operatorid": row[11],
                "teststation": row[12]
            }

        # Image
        image_query = '''
            select image_param.testheaderstepid, image_param.imageid, image_param.imagename, image_param.filenamelong
            , image_param.operationstepname, image_param.status, image_param.testheaderid, image_param.operationname
            , image_param.starttime, image_param.endtime, image_param.operatorid, image_param.teststation
            from imagedata_v image_param
            where image_param.testheaderstepid = :L4
        '''
        cursor.execute(image_query, L4=L4)
        rows = cursor.fetchall()
        for row in rows:
            dic_all[L4][row[2]] = {
                "testheaderstepid": row[0],
                "imageid": row[1],
                "imagename": row[2],
                "filenamelong": row[3],
                "operationstepname": row[4],
                "status": row[5],
                "testheaderid": row[6],
                "operationname": row[7],
                "starttime": row[8],
                "endtime": row[9],
                "operatorid": row[10],
                "teststation": row[11]
            }

    cursor.close()
    connection.close()

    empty_keys = [key for key, value in dic_all.items() if not value]
    for key in empty_keys:
        del dic_all[key]


    # return render_template('signup_new_11.html',all_header_per_sn_list = all_header_per_sn_list
    #         , serial_num = ser_num, num_attempts = num_attempts, percentageInOr_der_rounded = percentageInOr_der_rounded
    #         , PartNumber_item = PartNumber_item, namePart_numbers = namePart_numbers
    #         , Oparation_id = Oparation_id, Oparation_name = Oparation_name, Operation_headerid = Operation_headerid
    #         , dic_allL2 = dic_allL2
    #         , Loopitems = num_item, check_item = check_item
    #         , model_to_print = key
    #         , result_of_DUT = result_of_DUT
    #         , CT_Time = section
    #         ########L3
    #         , lst_sernum_L3 = lst_sernum_L3, lst_opID = lst_opID
    #         , lst_serItem = lst_serItem, ST_Time = section_st
    #         , last_serItem = last_serItem, last_serItemData = last_serItemData
    #         , lst_stepName = lst_stepName, num_lst_stepName = num_lst_stepName
    #         ########L4
    #         , dic_all = dic_all
    #         )


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
    
@app.route('/get_csv/<serial_num>/<serialText>/<Operation_value>', methods=['GET'])
def get_csv(serial_num, serialText, Operation_value):
    print("Start downloading")
    csv_data = [['TestHeaderID', 'Operation Name', 'StepID', 'Parameter Name', 'Value', 'Units', 'Min Limit', 'Max Limit']]

    for key, inner_dict in dic_all.items():
        step_id = key
        for param_name, param_value in inner_dict.items():
            value = units = min_limit = max_limit = None

            testheaderid = param_value['testheaderid']
            operationname = param_value['operationname']

            if param_value is None:
                value = "Data not available"
            else:
                if 'imagename' in param_value and param_value['imagename'] == 'ReportText':
                    value = param_value.get('filenamelong', '')
                elif 'valuemean' in param_value:
                    value = param_value['valuemean']
                elif 'valuestring' in param_value:
                    value = param_value['valuestring']
                else:
                    value = "None"

                if 'units' in param_value and param_value['units'] != 'NA':
                    units = param_value['units']
                else:
                    units = "None"

                if 'specmin' in param_value and param_value['specmin'] is not None:
                    min_limit = param_value['specmin']
                elif 'specmax' in param_value and param_value['specmax'] is not None:
                    min_limit = -999
                else:
                    min_limit = "None"

                if 'specmax' in param_value and param_value['specmax'] is not None:
                    max_limit = param_value['specmax']
                elif 'specmin' in param_value and param_value['specmin'] is not None: 
                    max_limit = 999
                else:
                    max_limit = "None"

            testheaderid_index = csv_data[0].index('TestHeaderID')
            testheaderid_values = [row[testheaderid_index] for row in csv_data]
            start_time = "START TIME"; start_time_value = "{}".format(param_value['starttime'])
            end_time = "END TIME"; end_time_value = "{}".format(param_value['endtime'])
            operator_id = "OPERATOR"; operator_id_value = "{}".format(param_value['operatorid'])
            station = "STATION"; station_value = "{}".format(param_value['teststation'])
            if param_value['testheaderid'] not in testheaderid_values:
                csv_data.append([testheaderid, operationname, 'None', start_time, start_time_value, '', '', ''])
                csv_data.append([testheaderid, operationname, 'None', end_time, end_time_value, '', '', ''])
                csv_data.append([testheaderid, operationname, 'None', operator_id, operator_id_value, '', '', ''])
                csv_data.append([testheaderid, operationname, 'None', station, station_value, '', '', ''])    
                
            # Append the row data to the CSV data
            # print("testheaderid: ", testheaderid)
            csv_data.append([testheaderid, operationname, step_id, param_name, value, units, min_limit, max_limit])

    csv_file = '{} {}{}.csv'.format(serial_num, serialText, Operation_value)

    with open(csv_file, mode='wb') as file:
        writer = csv.writer(file)
        writer.writerows(csv_data)

    # Prepare the response to send the file for download
    response = Response()
    response.headers['Content-Type'] = 'text/csv'
    response.headers['Content-Disposition'] = 'attachment; filename="{}"'.format(csv_file)

    with open(csv_file, mode='rb') as file:
        response.data = file.read()

    return response