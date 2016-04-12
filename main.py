#!/usr/bin/env python

import threading
import socket
import time
#import urllib2, os
#import tf_class
import constants


SERVER_IP_1   = '192.168.192.10'
SERVER_IP_2   = '192.168.192.33'
OUTPUTS_PORT = 5000

PORT_NUMBER = 5005
mySocket = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
hbtsocket = socket.socket( socket.AF_INET, socket.SOCK_DGRAM )
mySocket.bind( ('', PORT_NUMBER) )
mySocket.listen(1)
SIZE = 1024

def send_heartbeat():
    while True:
        dicti = {}
        dicti['value'] = str(1)
        dicti['name'] = 'Hrtbt_' + constants.name
        hbtsocket.sendto(str(dicti),(SERVER_IP_1,OUTPUTS_PORT)) 
        #mySocket.sendto(str(dicti),(SERVER_IP_2,OUTPUTS_PORT))  
        time.sleep(60)

hb = threading.Thread(target=send_heartbeat, args = [])
hb.start()

#vc = tf_class.TiFo()

#tuer = tuer_switch()
#t = threading.Thread(target=tuer.monitor, args = [])
#t.start()



while True:
    conn, addr = mySocket.accept()
    data = conn.recv(1024)
    if not data:
        break
    isdict = False
    try:
        data_ev = eval(data)
        if type(data_ev) is dict:
            isdict = True
    except Exception as serr:
        isdict = False 
    #print data
    conn.send("True")
    conn.close()           