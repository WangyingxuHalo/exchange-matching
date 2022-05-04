import socket
from multiprocessing import Process
import xml.etree.ElementTree as ET
import psycopg2
from xml_parser import parseXml
from xml.etree.ElementTree import tostring
from global_transid import *
#how to handle the request
num_of_processes = 10
processes = []
port = 12345
trans_id = -1
def recvLength(fd):
    rec_msg = ''
    num = ''
    rec_msg = fd.recv(1)
    rec_msg = rec_msg.decode('utf-8')
    while rec_msg != '\n':
        num += str(rec_msg)
        rec_msg = fd.recv(1)
        rec_msg = rec_msg.decode('utf-8')
    return int(num)

def acceptRequest(sk, tmp):
    conn = psycopg2.connect(database="exchangematching", user="postgres", password="passw0rd", host="db", port="5432")
    trans_id = transId(tmp)
    while True:
        (fd, addr) = sk.accept()
        handleRequest(fd, addr, conn, trans_id)

def handleRequest(fd, address, conn, tmp):
    global trans_id
    trans_id = tmp
    size = recvLength(fd)
    if size == 0:
        return
    xml = fd.recv(size)
    # print("recevive:")
    handle_res = parseXml(xml, trans_id, conn)
    # print("after handle:")
    # print(tostring(handle_res).decode("UTF-8"))
    fd.send(tostring(handle_res))
    # rootNode = ET.fromstring(xml)



def main():
    # conn = psycopg2.connect(database="exchangematching", user="postgres", password="passw0rd", host="localhost", port="5432")
    
    #create socket
    sk = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #bind the socket to hostname and port
    sk.bind((socket.gethostname(), port))    
    # Listen for incoming connections            
    sk.listen(1)                    

    
    for i in range(num_of_processes):
        tmp = int((i + 1) * 1e3)
        p = Process(target=acceptRequest, args=(sk,tmp,))
        p.deamon = True
        p.start()
        processes.append(p)
    
    for p in processes:
        p.join()
        

if __name__ == "__main__":
    main()
