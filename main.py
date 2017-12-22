#!/usr/bin/env python

import threading
import socket
import time

import tifo_config
# TODO: LED Class
# TODO: USB key
import zw_config
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

if sys.argv:
    if 'debug' in sys.argv:
        print('debug on')
        constants.debug = True

if constants.tifo:
    os.system("sudo service brickd stop")
    os.system("sudo service brickd start")
    time.sleep(2)

def db_out(text):
    if constants.debug:
        print(text)

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
        dicti = {}
        dicti['Value'] = str(1)
        dicti['Name'] = 'Hrtbt.' + constants.name
        hbtsocket.sendto(str(dicti),(constants.server1,constants.broadPort))
        for i in range(0,60):
            if not run:
                break
            time.sleep(1)

def supervise_threads(tliste):
#    print tliste
    while run:
        for t in tliste:
            if not t in threading.enumerate():
                print t.name
                sys.exit()
                exit()
        for i in range(0,60):
            if not run:
                break
            time.sleep(1)                

def upd_incoming():
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
            if data_ev.get('Szene')=='Update':
                conn.send('True')
                conn.close()             
                git_update()       
            elif 'Device' in data_ev:
    #           TODO threaded commands and stop if new comes in
                if constants.tifo and data_ev.get('Device') in tifo_config.outputs:
                    result = tf.set_device(data_ev) 
                elif constants.name in constants.LEDoutputs:
                    if data_ev.get('Device') in constants.LEDoutputs[constants.name]:
                        result = leds.set_device(**data_ev)
                elif constants.zwave and data_ev['Device'] in zw_config.outputs:
                    result = zwa.set_device(data_ev)
                elif constants.raspicam and data_ev['Name'] == 'Take_Pic':
                    take_pic()
                elif constants.raspicam and data_ev['Name'] == 'Record_Video':
                    take_vid()                
        conn.send(str(result))
        conn.close()  

def take_pic():
    os.system("echo 'im' >/var/www/html/FIFO")           
    
def take_vid():
    os.system("echo 'ca 1 10' >/var/www/html/FIFO") 
            
#if constants.tifo:
#    from tf_class import tiFo
#    tf = tiFo()

if constants.tifo:
    from tf_connection import TiFo
    tf = TiFo()
    tf.main()


if constants.PiLEDs:
    from led_class import LEDs
    leds = LEDs()  

if constants.PiInputs:
    from switch import gpio_input_monitoring
    eingang = gpio_input_monitoring()
    t = threading.Thread(name='inp_monitor',target=eingang.monitor, args = [])
    threadliste.append(t)
    t.start()    

if constants.USBkeys:
    from usb import usb_key
    db_out('USB active')
    keys = usb_key()
    t = threading.Thread(name='usb',target=keys.monitor, args = [])
    threadliste.append(t)
    t.start() 
    
if constants.wifi:
    import net_sup
    wifi_sup = threading.Thread(name='wifi', target=net_sup.main, args=[])
    threadliste.append(wifi_sup)
    wifi_sup.start()

if constants.zwave:
    from zw_class import zwave
    zwa = zwave()
    zw_sup = threading.Thread(name='ZWave', target=zwa.start, args=[])
    threadliste.append(zw_sup)
    zw_sup.start()

if constants.enoc:
    from enocean_class import Encocean_Sat
    enc = Encocean_Sat()
    enc_sup = threading.Thread(name='Enocean', target=enc.monitor, args=[])
    threadliste.append(enc_sup)
    enc_sup.start()

hb = threading.Thread(name="Heartbeat", target=send_heartbeat, args = [])
threadliste.append(hb)
hb.start()

ud = threading.Thread(name="UDP Input", target=upd_incoming, args = [])
threadliste.append(ud)
ud.start()

sth = threading.Thread(name="sup_thread", target=supervise_threads, args = [threadliste])
threadliste.append(sth)
sth.start()   