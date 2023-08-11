#
# import cx_Oracle
#
#     # Set up the connection details
# username = "readonly"
# password = "re6d0n1y"
# dsn = cx_Oracle.makedsn("patdbtdsprd05.li.lumentuminc.net", 1522, "TDSPRD05")
# ser_num = '1214170400002'
#
# all_header_per_sn_list = []
# connection = cx_Oracle.connect(username, password, dsn)
# cursor = connection.cursor()
#
# # --------------------------------------------------------------------------------------------------
# txt_query = '''
#                 SELECT header.testheaderid, header.SERIALNUMBER,header.PARTNUMBER,header.OPERATION,header.OPERATIONID,header.TESTSTATION,header.OPERATORID,header.STARTTIME,header.ENDTIME,header.RESULT
#                 FROM testheader_v    header where header.SERIALNUMBER = '{0}'ORDER BY header.STARTTIME
#                 '''.format(ser_num)
# cursor.execute(txt_query)
# data = cursor.fetchall()
#
#     # Count duplicates and append count as the last index
# count_dict = {}
# for item in data:
#     key = item[3]  # Use the operation name as the key for counting duplicates
#     # print(key)
#     if key in count_dict:
#         count_dict[key] += 1
#     else:
#         count_dict[key] = 1
# # print (count_dict)
# updated_data = [item + (count_dict[item[3]],) for item in data]
# # print(updated_data)
#
# # Remove duplicated lists
# # print('remove dup')
#
# # SLOW
# updated_data = list(set(updated_data))
# # print(updated_data)
# num = 0
# for row in updated_data:
#     print (row)
#     num += 1
# print("num = {}".format(num))
#
# # FAST
# deduplicated = {item[3]: item for item in updated_data}
# # Retrieve the de-duplicated list of tuples
# # for i in deduplicated.values():
# #     print(i)
#
#
# all_header_per_sn_list = list(deduplicated.values())
# # print(all_header_per_sn_list)
# # for row in all_header_per_sn_list:
# #     print (row)
#
# #------------------------------------------------------------------------------------
#
# print("show signup page",ser_num)

import cx_Oracle
username = "readonly"
password = "re6d0n1y"
dsn = cx_Oracle.makedsn("patdbtdsprd05.li.lumentuminc.net", 1522, "TDSPRD05")
ser_num = '1214170400002'

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
num = 0
for i in data:
    print(i)
    num += 1
print("num = {}".format(num))