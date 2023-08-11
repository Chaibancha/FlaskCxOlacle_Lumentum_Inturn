import cx_Oracle

port_flask = 5009
username = "readonly"
password = "re6d0n1y"
dsn = cx_Oracle.makedsn("patdbtdsprd05.li.lumentuminc.net", 1522, "TDSPRD05")

try:
    #create connection
    conn = cx_Oracle.connect(username, password, dsn)
except Exception as err:
    print('Error while creating the connection', err)
else:
    print (conn.version)
    try:
        cur = conn.cursor()
        sql_insert = """
            SELECT header.SERIALNUMBER,header.PARTNUMBER,header.OPERATION,header.OPERATIONID,header.TESTSTATION,header.STARTTIME,header.RESULT,header.OPERATORID,SYSTIMESTAMP - header.STARTTIME
            FROM testheader_v header WHERE header.productfamilyname ='PicoBlade3' AND header.starttime >= SYSDATE - INTERVAL '14' DAY
            """
        cur.execute(sql_insert)
    except Exception as err:
        print('Error while inserting the data', err)
    else:
        print ('Data inserted successfully')
        conn.commit()

finally:
    cur.close()
    conn.close()


print ("Table Created.")