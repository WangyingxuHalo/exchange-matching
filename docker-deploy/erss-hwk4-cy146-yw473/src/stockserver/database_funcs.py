from math import fabs
from datetime import datetime
from venv import create
import xml.etree.ElementTree as ET

def checkAccount(id, conn):
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM ACCOUNT where ACCOUNT_ID =" + str(id))
    row = cur.fetchall()
    print(len(row))
    return len(row) != 0

def createAccount(id, balance, res, conn):
    if not checkAccount(id, conn):
        cur = conn.cursor()
        cur.execute("INSERT INTO ACCOUNT (ACCOUNT_ID, Balance) VALUES (%s, %s)", (id, balance)) 
        conn.commit()
        ET.SubElement(res, 'created', {'id': str(id), })
        print("Successfully create account")
    else:
        info = ET.SubElement(res, 'error', {'id': str(id),})
        print("account exist error")
        info.text="Account already exists"
        
def checkAmount(amount, sym, res):
    if float(amount) < 0:
        info = ET.SubElement(res, 'error', {'sym': str(sym), 'id': str(id),})
        info.text="Amount should not be negative"
        return False
    return True

def createPostion(id, amount, sym, res, conn):
    # if checkAccount(id, conn) and checkAmount(amount, sym, res):
    #     cur = conn.cursor()
    #     cur.execute("SELECT COUNT(*) FROM POSITION WHERE SYMBOL = %s AND ACCOUNT_ID = %s", (sym, id)) 
    #     row = cur.fetchall()
    #     if len(row) == 1:
    #         cur.execute("UPDATE POSITION SET AMOUNT = AMOUNT + %s WHERE SYMBOL = %s AND ACCOUNT_ID = %s", (amount, sym, id))
    #     else:
    #         cur.execute("INSERT INTO POSITION (AMOUNT, SYMBOL, ACCOUNT_ID) VALUES(%s, %s, %s)", (amount, sym, id))
    #     conn.commit()
    #     ET.SubElement(res, 'created', {'sym': sym, 'id': str(id)},)
    #     print("Successfully create Positions")
    cur = conn.cursor()
    cur.execute("INSERT INTO POSITION (account_id, symbol, amount) values (%s, %s, %s) ON conflict (account_id, symbol) DO update set amount = position.amount + %s ;", (id, sym, amount, amount))
    # cur.execute("update position set amount=( (select amount from position where account_id=%s and symbol=%s)+%s) where account_id=%s and symbol=%s; insert into position (symbol, amount, account_id) select %s, %s, %s where not exists (select 1 from position where account_id=%s and symbol=%s);", (str(id), str(sym), str(amount), str(id), str(sym),str(sym), str(amount), str(id),  str(id), str(sym)))
    conn.commit()
    # ET.SubElement(res, 'created', {'sym': sym, 'id': str(id)},)
    print("Successfully create Positions")

def updatePosition(id, amount, sym, cur):
    cur.execute("INSERT INTO POSITION (account_id, symbol, amount) values (%s, %s, %s) ON conflict (account_id, symbol) DO update set amount = position.amount + (%s) ;", (id, sym, amount, amount))

def checkEnoughBalance(id, amount, limit, conn):
    cur = conn.cursor()
    cur.execute("SELECT BALANCE FROM ACCOUNT WHERE ACCOUNT_ID =" + str(id))
    row = cur.fetchall()
    if len(row) == 0:
        return 0
    return float(row[0][0]) >= float(limit) * float(amount)

def checkEnoughShare(id, amount, sym, conn):
    cur = conn.cursor()
    cur.execute("SELECT AMOUNT FROM POSITION WHERE ACCOUNT_ID = %s AND SYMBOL = %s", (id, sym) )
    row = cur.fetchall()
    if len(row) == 0:
        return 0
    return float(row[0][0]) >= float(amount)

def deductBalance(id, amount, limit, cur):
    cur.execute("UPDATE ACCOUNT SET BALANCE = (SELECT BALANCE FROM ACCOUNT WHERE ACCOUNT_ID = %s) - (%s) WHERE ACCOUNT_ID = %s",(id, float(amount) * float(limit), id))

def deductShare(id, amount, sym, cur):
    cur.execute("UPDATE POSITION SET AMOUNT = (SELECT AMOUNT FROM POSITION WHERE ACCOUNT_ID = %s AND SYMBOL = %s) - (%s) WHERE ACCOUNT_ID = %s AND SYMBOL = %s", (id, sym, amount, id , sym))

def executeOrder(id, cur):
    cur.execute("UPDATE ORDERS SET STATUS='executed' where ORDER_ID = %s", (id,))

def updateAccount(id, money, cur):
    cur.execute("UPDATE ACCOUNT SET BALANCE = (SELECT BALANCE FROM ACCOUNT WHERE ACCOUNT_ID = %s)+ ( %s ) where ACCOUNT_ID = %s",(id, money, id))

def createOrder(trans_id, sym, amount, limit, id, now, status, cur):
    cur.execute("INSERT INTO ORDERS ( TRANS_ID, SYMBOL, AMOUNT, LIMIT_PRICE, ACCOUNT_ID, TIME, STATUS) VALUES ( %s, %s, %s, %s, %s, %s, %s);", ( trans_id, sym, amount, limit, id, now, status))

def updateOrderAmount(id, amount, cur):
    cur.execute("update orders set amount=%s where ORDER_ID = %s",(amount, id))

def refund(id, money, cur):
    cur.execute("UPDATE ACCOUNT SET BALANCE = (SELECT BALANCE FROM ACCOUNT WHERE ACCOUNT_ID = %s) + (%s) WHERE ACCOUNT_ID = %s",(id, money, id))

def createBuyOrder(id, amount, sym, limit, trans_id, result, conn ):
    cur = conn.cursor()
    deductBalance(id, amount, limit, cur)
    now = datetime.now()
    cur.execute("SELECT * FROM ORDERS WHERE SYMBOL = %s AND AMOUNT < 0 AND STATUS = 'open' AND LIMIT_PRICE <= %s AND ACCOUNT_ID != %s ORDER BY LIMIT_PRICE ASC, time ASC", (sym, limit, id))
    #cur.execute("SELECT * FROM ORDERS WHERE SYMBOL = %s AND AMOUNT > 0 AND STATUS = 'open' ORDER BY LIMIT_PRICE ASC, time ASC", (sym, ))
    remain_amt = float(amount)
    row = cur.fetchall()
    print(row)
    if len(row) == 0:
        createOrder(trans_id, sym, amount, limit, id, now, "open", cur)
        conn.commit()
    else:
        money_spent = 0
        for item in row:
            if remain_amt == 0:
                #if remaining is 0 just break
                break
            sell_amt = -float(item[3])
            sell_lmt = float(item[4])
            sell_id = item[0]
            sell_accid = item[5]
            sell_transid =item[1]
            if sell_amt > remain_amt:
                tmp = remain_amt * sell_lmt
                money_spent += tmp
                #update remaining open sell order
                updateOrderAmount(sell_id, -(sell_amt - remain_amt), cur)
                #create executed buy order
                createOrder(trans_id, sym, remain_amt, sell_lmt, id, now, "executed", cur)
                #create executed sell order
                createOrder(sell_transid, sym, -remain_amt, sell_lmt, sell_accid, now, "executed", cur)
                # updateAccount(sell_accid, tmp, cur)
                refund(id, (float(limit) - sell_lmt) * remain_amt, cur)
                refund(sell_accid, tmp, cur)
                updatePosition(id, remain_amt, sym, cur)
                conn.commit()
                remain_amt = 0
            else:
                remain_amt -= sell_amt
                tmp = sell_lmt*sell_amt
                money_spent += tmp
                #execute sell order
                executeOrder(sell_id, cur)
                createOrder(trans_id, sym, sell_amt, sell_lmt, id, now, "executed", cur)
                # createOrder(sell_transid, sym, -sell_amt, sell_lmt, sell_accid, now, "executed", cur)
                refund(id, (float(limit) - sell_lmt) * sell_amt, cur)
                refund(sell_accid, tmp, cur)
                updatePosition(id, sell_amt, sym, cur)
                # updateAccount(sell_accid, tmp, cur)
                conn.commit()
        # if money_spent != 0:
        #     # updateAccount(id, -money_spent, cur)
        #     if remain_amt != 0:
        #         createOrder(trans_id, sym, remain_amt, limit, id, now, "open", cur)
        #     conn.commit()
        # else:
        #     createOrder(trans_id, sym, amount, limit, id, now, "open", cur)
        #     conn.commit()
        if remain_amt != 0:
            createOrder(trans_id, sym, remain_amt, limit, id, now, "open", cur)
            conn.commit()
        # else:
        #     createOrder(trans_id, sym, amount, limit, id, now, "open", cur)
        #     conn.commit()
    ET.SubElement(result, 'opened', {'sym': sym,'amount': str(amount), 'limit': str(limit), 'id': str(trans_id)})



def createSellOrder(id, amount, sym, limit, trans_id, result, conn ):
    cur = conn.cursor()
    deductShare(id, -float(amount), sym, cur)
    now = datetime.now()
    cur.execute("SELECT * FROM ORDERS WHERE SYMBOL = %s AND AMOUNT > 0 AND STATUS = 'open' AND LIMIT_PRICE >= %s AND ACCOUNT_ID != %s ORDER BY LIMIT_PRICE DESC, time ASC", (sym, limit, id))
    remain_amt = -float(amount)
    row = cur.fetchall()
    if len(row) == 0:
        createOrder(trans_id, sym, amount, limit, id, now, "open", cur)
        conn.commit()
    else:
        money_earn = 0
        for item in row:
            if remain_amt == 0:
                #if remaining is 0 just break
                break
            buy_amt = float(item[3])
            buy_lmt = float(item[4])
            buy_id = item[0]
            buy_accid = item[5]
            buy_transid =item[1]
            if buy_amt > remain_amt:
                tmp = remain_amt * buy_lmt
                money_earn += tmp
                #update remaining open buy order
                updateOrderAmount(buy_id, buy_amt - remain_amt, cur)
                #create executed buy order
                createOrder(buy_transid, sym, remain_amt, buy_lmt, buy_accid, now,  "executed", cur)
                #create executed sell order
                createOrder(trans_id, sym, -remain_amt, buy_lmt, id, now, "executed", cur)
                #make money for seller
                refund(id, tmp, cur)
                #upadate buyer position
                updatePosition(buy_accid, remain_amt, sym, cur)
                conn.commit()
                remain_amt = 0
            else:
                remain_amt -= buy_amt
                tmp = buy_lmt * buy_amt
                money_earn += tmp
                #execute buy Order 
                executeOrder(buy_id, cur)
                createOrder(trans_id, sym, -buy_amt, buy_lmt, id, now, "executed", cur)
                # createOrder(buy_transid, sym, buy_amt, buy_lmt, buy_accid, now, "executed", cur)
                refund(id, tmp, cur)
                # print("update position for {} with {}".format(buy_accid, buy_amt))
                updatePosition(buy_accid, buy_amt, sym, cur)
                conn.commit()
        if remain_amt != 0:
            print(remain_amt)
            createOrder(trans_id, sym, -remain_amt, limit, id, now, "open", cur)
            conn.commit()
        # else:
        #     print('amount',amount)
        #     createOrder(trans_id, sym, amount, limit, id, now, "open", cur)
        #     conn.commit()
    ET.SubElement(result, 'opened', {'sym': sym,'amount': str(amount), 'limit': str(limit), 'id': str(trans_id)})
                
def query_trans(my_info, child, conn, is_cancel):
    queryid = child.attrib["id"]
    cur = conn.cursor()
    cur.execute("SELECT * FROM ORDERS WHERE TRANS_ID=%s", (queryid,))
    query_res = cur.fetchall()
    if is_cancel:
        for result in query_res:
            if str(result[7])=="open":
                ET.SubElement(my_info, 'open', {'shares': str(result[3])})
            elif str(result[7])=="canceled":
                ET.SubElement(my_info, 'canceled', {'shares': str(result[3]), 'time': str(result[6])})
            elif str(result[7])=="executed":
                ET.SubElement(my_info, 'executed', {'shares': str(result[3]), 'price': str(result[4]), 'time': str(result[6])})
            else:
                errors = ET.SubElement(my_info, 'error', {'id': queryid})
                errors.text = ("Status not correct")
    else:
        if len(query_res) == 0:
            info = ET.SubElement(my_info, 'error', {'id': queryid})
            info.text = ("Empty query")
        else:
            info = ET.SubElement(my_info, 'status', {'id': child.attrib["id"]})
            for result in query_res:
                if str(result[7])=="open":
                    ET.SubElement(info, 'open', {'shares': str(result[3])})
                elif str(result[7])=="canceled":
                    ET.SubElement(info, 'canceled', {'shares': str(result[3]), 'time': str(result[6])})
                elif str(result[7])=="executed":
                    ET.SubElement(info, 'executed', {'shares': str(result[3]), 'price': str(result[4]), 'time': str(result[6])})
                else:
                    errors = ET.SubElement(my_info, 'error', {'id': queryid})
                    errors.text = ("Status not correct")

def find_order(child, conn):
    cancelid = child.attrib["id"]
    cur = conn.cursor()
    cur.execute("SELECT ACCOUNT_ID, AMOUNT, LIMIT_PRICE, status, SYMBOL FROM ORDERS WHERE TRANS_ID=%s AND status='open'", (cancelid,))
    my_order = cur.fetchall()
    return my_order

def cancel_trans(res, child, conn, cur_orders):
    cancelid = child.attrib["id"]
    info = ET.SubElement(res, 'canceled', {'id': cancelid})
    for cur_order in cur_orders:
        acc_id = cur_order[0]
        cancel_money = cur_order[1] * cur_order[2]
        cur = conn.cursor()
        cur.execute("UPDATE ORDERS SET STATUS='canceled' WHERE TRANS_ID=%s AND status='open'", (cancelid,))
        conn.commit()
        if cancel_money > 0:
            cur.execute("UPDATE ACCOUNT SET BALANCE = (BALANCE + %s) WHERE ACCOUNT_ID = %s",(cancel_money, acc_id))
        else:
            cur_symbol = cur_order[4]
            updatePosition(acc_id, -cur_order[1], cur_symbol, cur)
        conn.commit()
    query_trans(info, child, conn, True)





