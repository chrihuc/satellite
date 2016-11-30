#!/usr/bin/env python

import threading
import socket
import time

from tf_class import tiFo
import constants
import sys, os
import git

PORT_NUMBER = 5005
mySocket = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
hbtsocket = socket.socket( socket.AF_INET, socket.SOCK_DGRAM )
mySocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
mySocket.bind( ('', PORT_NUMBER) )
mySocket.listen(128)
SIZE = 1024

threadliste = []

run = True

os.system("sudo service brickd stop")
os.system("sudo service brickd start")
time.sleep(2)

def git_update():
    global run
    g = git.cmd.Git()
    g.reset('--hard')
    g.pull()
    print "Update done, exiting"
    run = False
    sys.exit() 

def send_heartbeat():
    while run:
        for t in threadliste:
            if not t in threading.enumerate():
                #print t.name
                sys.exit()        
        dicti = {}
        dicti['Value'] = str(1)
        dicti['Name'] = 'Hrtbt_' + constants.name
        hbtsocket.sendto(str(dicti),(constants.server1,constants.broadPort))
        for i in range(0,60):
            if not run:
                break
            time.sleep(1)

hb = threading.Thread(name="TiFo", target=send_heartbeat, args = [])
threadliste.append(hb)
hb.start()

tf = tiFo()

#tuer = tuer_switch()
#t = threading.Thread(target=tuer.monitor, args = [])
#t.start()


while run:
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
        if data_ev.get('Command')=='Update':
            conn.send('True')
            conn.close()             
            git_update()       
        elif 'Device' in data_ev:
           result = tf.set_device(data_ev)             
    conn.send(str(result))
    conn.close()           