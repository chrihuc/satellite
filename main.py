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

from time import localtime,strftime
import paho.mqtt.client as mqtt
import json

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

mqtt.Client.connected_flag=False
client = None
topics = ["Command/" + constants.name + "/#"]
ipaddress = constants.mqtt_.server
port = 1883

def connect(ipaddress, port):
    global client
    zeit =  time.time()
    uhr = str(strftime("%Y-%m-%d %H:%M:%S",localtime(zeit)))
    client = mqtt.Client(constants.name +'_sub_' + uhr, clean_session=False)
    assign_handlers(on_connect, dis_con, on_message)
    client.username_pw_set(username=constants.mqtt_.user,password=constants.mqtt_.password)
    client.connect(ipaddress, port, 60)
#    client.loop_start()
    client.loop_forever()

def assign_handlers(connect, disconnect, message):
    """
    :param mqtt.Client client:
    :param connect:
    :param message:
    :return:
    """

    global client
    client.on_connect = connect
    client.on_disconnect = disconnect
    client.on_message = message

def dis_con (*args, **kargs):
    print("disconnected")

def on_connect(client_data, userdata, flags, rc):
    global client, topics
    if rc==0 and not client.connected_flag:
        client.connected_flag=True #set flag
        print("connected OK")
        for topic in topics:
            client.subscribe(topic)
    elif client.connected_flag:
        pass
    else:
        print("Bad connection Returned code=",rc)

def on_message(client, userdata, msg):
    print(msg.topic + " " + str(msg.payload))
    try:
        m_in=(json.loads(msg.payload)) #decode json data
        print(m_in)
        if m_in.get('Szene')=='Update':
            git_update()        
        if m_in['Name'] == "STOP":
            os.system("sudo killall python")
            #pass
        elif 'Device' in m_in:
#           TODO threaded commands and stop if new comes in
            if constants.tifo and m_in.get('Device') in tifo_config.outputs:
                result = tf.set_device(m_in)
            elif constants.name in constants.LEDoutputs:
                if m_in.get('Device') in constants.LEDoutputs[constants.name]:
                    result = leds.set_device(**m_in)
            elif constants.zwave and m_in['Device'] in zw_config.outputs:
                result = zwa.set_device(m_in)
            elif constants.raspicam and m_in['Name'] == 'Take_Pic':
                take_pic()
            elif constants.raspicam and m_in['Name'] == 'Record_Video':
                take_vid()
    except:
        pass

#def upd_incoming():
#    while run:      
#        connect(ipaddress, port)
#        conn, addr = mySocket.accept()
#        data = conn.recv(1024)
#        if not data:
#            break
#        isdict = False
#        try:
#            data_ev = eval(data)
#            if type(data_ev) is dict:
#                isdict = True
#        except Exception as serr:
#            isdict = False
#        result = False
#        if isdict:
#            if data_ev.get('Szene')=='Update':
#                conn.send('True')
#                conn.close()
#                git_update()
#            elif 'Device' in data_ev:
#    #           TODO threaded commands and stop if new comes in
#                if constants.tifo and data_ev.get('Device') in tifo_config.outputs:
#                    result = tf.set_device(data_ev)
#                elif constants.name in constants.LEDoutputs:
#                    if data_ev.get('Device') in constants.LEDoutputs[constants.name]:
#                        result = leds.set_device(**data_ev)
#                elif constants.zwave and data_ev['Device'] in zw_config.outputs:
#                    result = zwa.set_device(data_ev)
#                elif constants.raspicam and data_ev['Name'] == 'Take_Pic':
#                    take_pic()
#                elif constants.raspicam and data_ev['Name'] == 'Record_Video':
#                    take_vid()
#        conn.send(str(result))
#        conn.close()
                
                
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

if constants.ePaperHat:
    import hat_display
    paphat = threading.Thread(name='PaperHat', target=hat_display.main, args=[])
    threadliste.append(paphat)
    paphat.start()

hb = threading.Thread(name="Heartbeat", target=send_heartbeat, args = [])
threadliste.append(hb)
hb.start()

#ud = threading.Thread(name="UDP Input", target=upd_incoming, args = [])
#threadliste.append(ud)
#ud.start()

sth = threading.Thread(name="sup_thread", target=supervise_threads, args = [threadliste])
threadliste.append(sth)
sth.start()

connect(ipaddress, port)