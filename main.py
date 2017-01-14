#!/usr/bin/env python

import threading
import socket
import time

from tf_class import tiFo
import tifo_config
# TODO: LED Class
# TODO: network supervision
# TODO: Tuer switch
# TODO: USB key
# TODO: z-wave class
import constants
import sys, os
import git

# mySocket for receiving TCP commands
# hbtsocked for sending the heartbeats to the server
mySocket = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
hbtsocket = socket.socket( socket.AF_INET, socket.SOCK_DGRAM )
mySocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
mySocket.bind( ('', constants.biPort) )
mySocket.listen(128)
SIZE = 1024

threadliste = []

run = True

if constants.tifo:
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

hb = threading.Thread(name="Heartbeat", target=send_heartbeat, args = [])
threadliste.append(hb)
hb.start()

if constants.tifo:
    tf = tiFo()

if constants.PiLEDs:
    from led_class import LEDs
    inp = LEDs()  

if constants.PiInputs:
    from switch import tuer_switch

if constants.USBkeys:
    from usb import usb_key
    
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
#           TODO threaded commands and stop if new comes in
            if data_ev.get('Device') in tifo_config.outputs:
                result = tf.set_device(data_ev) 
            elif constants.name in constants.LEDoutputs:
                if data_ev.get('Device') in constants.LEDoutputs[constants.name]:
                    result = inp.set_device(data_ev)                
    conn.send(str(result))
    conn.close()           