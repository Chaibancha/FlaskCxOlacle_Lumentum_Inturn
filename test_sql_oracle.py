from flask import Flask, send_file, render_template, json, request, redirect, Response,url_for, jsonify, session
import cx_Oracle
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
    FROM testheader_v header WHERE header.productfamilyname ='PicoBlade3' AND header.starttime >= SYSDATE - INTERVAL '1' DAY
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
            # print(single_row)
            count = count + 1
        length_of_last_tested = count
        #print(length_of_last_tested)

        
    list_of_last_week_dates = []
    if new_last_tested_units_list != []:
        count = 0
        for single_row in new_last_tested_units_list:
            date_time_string = single_row[5].strftime('%Y-%m-%d')
            if date_time_string not in list_of_last_week_dates:
                list_of_last_week_dates.append(date_time_string)

        # list_of_last_week_dates = set(list_of_last_week_dates)
        #print(list_of_last_week_dates)

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

        #list_of_last_week_models = set(list_of_last_week_models)



if __name__ == "__main__":
    main()