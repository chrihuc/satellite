#!/usr/bin/env python

import threading
import socket
import time
#import urllib2, os
from tf_class import tiFo
import constants
import sys


PORT_NUMBER = 5005
mySocket = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
hbtsocket = socket.socket( socket.AF_INET, socket.SOCK_DGRAM )
mySocket.bind( ('', PORT_NUMBER) )
mySocket.listen(1)
SIZE = 1024

threadliste = []

def send_heartbeat():
    while True:
        for t in threadliste:
            if not t in threading.enumerate():
                #print t.name
                sys.exit()        
        dicti = {}
        dicti['value'] = str(1)
        dicti['name'] = 'Hrtbt_' + constants.name
        hbtsocket.sendto(str(dicti),(constants.server1,constants.broadPort))  
        time.sleep(60)

hb = threading.Thread(name="TiFo", target=send_heartbeat, args = [])
threadliste.append(hb)
hb.start()

tf = tiFo()

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
    result = False
    if isdict:
        if 'Device' in data_ev:
           result = tf.set_device(data_ev)  
    conn.send(result)
    conn.close()           