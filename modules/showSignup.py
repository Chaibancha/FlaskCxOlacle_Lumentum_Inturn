from flask import Flask, send_file, render_template, json, request, redirect, Response,url_for, jsonify, session, Blueprint
from flask_caching import Cache
import cx_Oracle
import datetime

module1_app = Blueprint('showSignUp', __name__)
#import configparer
#import shutil
port_flask = 5009
username = "readonly"
password = "re6d0n1y"
dsn = cx_Oracle.makedsn("patdbtdsprd05.li.lumentuminc.net", 1522, "TDSPRD05")

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


    from collections import Counter

    count_dict = Counter(item[3] for item in data)
    print("count_dict")
    print(count_dict.most_common())  # MODEL: many of MODEL
    print("--------------------------------")


    updated_data = [item + (count_dict[item[3]],) for item in data]
    # print(updated_data) # all data
    # Remove duplicated lists
    # print('remove dup')
    updated_data = list(set(updated_data))

    for k in updated_data:
        print(k)


    deduplicated = {item[4]: item for item in updated_data}
    print(deduplicated)
    
    # Retrieve the de-duplicated list of tuples
    all_header_per_sn_list = list(deduplicated.values())

    num_item = 5 + len(all_header_per_sn_list)
    print("DUT = {}".format(ser_num))
    PartNumber_item = next(iter(deduplicated.values()))[2]
    print("Model = {}".format(PartNumber_item))
    num = len(data)  
    ("Attempts = {} Attempts".format(num))



    num_of_passed = sum(item[8] == 'Passed' for item in data)
    num_of_failed = sum(item[8] == 'Failed' for item in data)
    num_of_aborted = sum(item[8] not in ['Passed', 'Failed'] for item in data)

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
        for item in deduplicated.values():
            start_time = item[6]
            end_time = item[7]
            minute_time = int((end_time - start_time).total_seconds() / 60)

            section_title = "{} minutes".format(minute_time)
            section.append(section_title)
            
    find_CT_Time()

    num_attempts = []

    def findAttempts():
        deduplicated_values = deduplicated.values()  
        append_to_num_attempts = num_attempts.append  

        for i in deduplicated_values:
            item_num_attempts = i[10]
            append_to_num_attempts(item_num_attempts)

    findAttempts()


    Oparation_id = []
    Oparation_name = []

    def findOparation():
        deduplicated_values = deduplicated.values()  
        append_to_Oparation_id = Oparation_id.append  
        append_to_Oparation_name = Oparation_name.append  

        for i in deduplicated_values:
            item_id = i[4]
            item_name = i[3]
            append_to_Oparation_id(item_id)
            append_to_Oparation_name(item_name)

    findOparation()

    # check
    check_item = [i[8] for i in deduplicated.values()]  



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



    from collections import defaultdict
    
    dic_all = defaultdict(dict)

    connection = cx_Oracle.connect(username, password, dsn)
    cursor = connection.cursor()

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
            dic_all[L4][row[1]] = {
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
            dic_all[L4][row[1]] = {
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
            dic_all[L4][row[2]] = {
                "testheaderstepid": row[0],
                "imageid": row[1],
                "imagename": row[2],
                "filenamelong": row[3],
                "operationstepname": row[4],
                "status": row[5]
            }

    cursor.close()
    connection.close()

    empty_keys = [key for key, value in dic_all.items() if not value]
    for key in empty_keys:
        del dic_all[key]



    # print(dic_all)


    # for i in lst_serItem:
    #     print(i)
    # for i in last_serItem:
    #     print(i)

    return render_template('signup_new_08 new.html',all_header_per_sn_list = all_header_per_sn_list
            , serial_num = ser_num, num_attempts = num_attempts, PartNumber_item = PartNumber_item
            , Oparation_id = Oparation_id, Oparation_name = Oparation_name
            , items = num_item, check_item = check_item
            , model_to_print = key
            , result_of_DUT = result_of_DUT
            , CT_Time = section
            ########L3
            , lst_sernum_L3 = lst_sernum_L3, lst_opID = lst_opID
            , lst_serItem = lst_serItem, ST_Time = section_st
            , last_serItem = last_serItem, last_serItemData = last_serItemData
            , lst_stepName = lst_stepName, num_lst_stepName = num_lst_stepName
            ########L4
            , dic_all = dic_all
            )

