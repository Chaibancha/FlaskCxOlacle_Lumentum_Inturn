import cx_Oracle

port_flask = 5009
username = "readonly"
password = "re6d0n1y"
dsn = cx_Oracle.makedsn("patdbtdsprd05.li.lumentuminc.net", 1522, "TDSPRD05")

try:
    conn = cx_Oracle.connect(username, password, dsn)
except Exception as err:
    print("Error occurred while trying to create connection", err)
else:
    try:
        cur = conn.cursor()
        sql = """
            SELECT header.SERIALNUMBER,header.PARTNUMBER,header.OPERATION,header.OPERATIONID,header.TESTSTATION,header.STARTTIME,header.RESULT,header.OPERATORID,SYSTIMESTAMP - header.STARTTIME
            FROM testheader_v header WHERE header.productfamilyname ='PicoBlade3' AND header.starttime >= SYSDATE - INTERVAL '14' DAY
            """
        cur.execute(sql)
        for i in range(5):
            row = cur.fetchone()
            print(row)
        # rows = cur.fetchone()
        # print(rows)
        # rows2 = cur.fetchone()
        # print(rows2)
        # rows3 = cur.fetchone()
        # print(rows3)
        # rows4 = cur.fetchone()
        # print(rows4)
        # rows5 = cur.fetchone()
        # print(rows5)
        
        # for index, record in enumerate(rows):
        #     print("Index is ", index, " : ", record)


    except Exception as err:
        print("Error occurred while fetching the records ", err)
    else:
        print("Success")
    finally:
        cur.close()

finally:
    conn.close()