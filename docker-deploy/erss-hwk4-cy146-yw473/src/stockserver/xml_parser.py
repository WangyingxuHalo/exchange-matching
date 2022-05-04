import xml.etree.ElementTree as ET
from database_funcs import *
from xml.etree.ElementTree import tostring
import psycopg2


def checkBalance(balance, res):
    if float(balance) < 0:
        info = ET.SubElement(res, 'error',{'id': str(id),})
        info.text = "Balance could not small than 0"
        return False
    else:
        return True

def parseXml(xmlstring, trans_id, conn):
    root=ET.fromstring(xmlstring)
    res = ET.Element('results')
    print(root)
    if root.tag == "create":
        for child in root:
            if child.tag == "account":
                accID = child.attrib['id']
                balance = child.attrib['balance']
                print("create")
                if checkBalance(balance, res):
                    createAccount(accID, balance, res, conn)
            elif child.tag == "symbol":
                sym = child.attrib['sym']
                print("create symbol ", sym)
                for grandchild in child.findall('account'):
                    accID = grandchild.attrib['id']
                    amount = grandchild.text
                    print("create symbol {} with {} ".format(sym, amount))
                    print(amount)
                    createPostion(accID, amount, sym, res, conn)
                    ET.SubElement(res, 'created', {'sym':sym, 'id':str(accID)})
            else:
                info = ET.SubElement(res, 'error')
                info.text="Unknow create tag error"

    elif root.tag == "transactions":
        accID = root.attrib["id"]
        sig = checkAccount(accID, conn)
        print("sig == {}".format(sig))
        for child in root:
            if child.tag == "order":
                if sig:
                    if float(child.attrib["amount"]) > 0:
                        if checkEnoughBalance(accID, child.attrib["amount"], child.attrib["limit"], conn):
                            # deductBalance(accID, child.attrib["amount"], child.attrib["limit"], res, conn)      
                            createBuyOrder(accID, child.attrib["amount"], child.attrib["sym"], child.attrib["limit"], trans_id.get_value(), res, conn)
                            trans_id.add_value()
                        else:
                            info = ET.SubElement(res, 'status', {"id": accID})
                            info.text = "NOT enough balance"
                    else:
                        if checkEnoughShare(accID, child.attrib["amount"], child.attrib["sym"], conn):
                            # deductShare(accID, child.attrib["amount"], child.attrib["sym"], conn)
                            createSellOrder(accID, child.attrib["amount"], child.attrib["sym"], child.attrib["limit"], trans_id.get_value(), res, conn)
                            trans_id.add_value()
                        else:
                            info = ET.SubElement(res, 'status', {"id": accID})
                            info.text = "NOT enough Share"
                else:
                    info = ET.SubElement(res, 'error', {'sym': child.attrib["sym"],'amount': child.attrib["amount"], 'limit': child.attrib["limit"],})
                    info.text="Account not exist"
            elif child.tag == "query":
                print("query")
                transaction_id = child.attrib["id"]
                if sig:
                    info = query_trans(res, child, conn, False)
                else:
                    info = ET.SubElement(res, 'error', {'id': transaction_id})
                    info.text="Account not exist"
            elif child.tag == "cancel":
                print("cancel")
                transaction_id = child.attrib["id"]
                if sig:
                    print("sig")
                    cur_orders = find_order(child, conn)
                    if len(cur_orders) == 0:
                        print("No open order to cancel")
                        info = ET.SubElement(res, 'error', {'id': transaction_id})
                        info.text="No open order to cancel"
                    else:
                        print("there are open orders")
                        cancel_trans(res, child, conn, cur_orders)
                else:
                    info = ET.SubElement(res, 'error', {'id': transaction_id})
                    info.text="Account not exist"
            else:
                info = ET.SubElement(res, 'error', {'id': accID})
                info.text="Tag Not Correct"
    return res

if __name__ == "__main__":

    conn = psycopg2.connect(database="exchangematching", user="postgres", password="passw0rd", host="localhost", port="5432")
    print("database connect succsss")
    
    data = open("sample.xml").read() 
    parseXml(data, conn)
    


    