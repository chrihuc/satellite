#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
@author: christoph
"""

from display import epd2in13
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

from time import localtime,strftime
import paho.mqtt.client as mqtt
import time
import threading
import json

import constants
from tools import toolbox

epd = epd2in13.EPD()
epd.init(epd.lut_full_update)
#epd.init(epd.lut_partial_update)
fontTime = ImageFont.truetype('./display/FreeMonoBold.ttf', 16)
fontStatus = ImageFont.truetype('./display/FreeMonoBold.ttf', 18)
#epd.delay_ms(2000)

image = Image.new('1', (epd2in13.EPD_HEIGHT, epd2in13.EPD_WIDTH), 255)  # 255: clear the frame
draw = ImageDraw.Draw(image)
image_width, image_height  = image.size
#draw.rectangle((0, 0, image_width, image_height), fill = 255)


epd.clear_frame_memory(0xFF)
epd.display_frame()
epd.clear_frame_memory(0xFF)
epd.display_frame()

epd.init(epd.lut_partial_update)

if True:
    pix_size = 64 # 32 ging 64 nicht, mit anderem USB Ladegerät ging dann auch 64
    pixel = Image.new('1', (pix_size,pix_size), 255)
    for x in range(0,epd2in13.EPD_WIDTH,pix_size):
        for y in range(0,epd2in13.EPD_HEIGHT,pix_size):
            for fc in range(2):
                epd.set_frame_memory(pixel, x, y)
                epd.display_frame()
            print(x,y)

mqtt.Client.connected_flag=False
client = None
topics = ["Settings/Status", "Settings/Alarmanlage" , "Settings/Alarmstatus", "Inputs/A00TER1GEN1TE01", "Inputs/V00KUE1RUM1TE02",
          "Inputs/V00WOH1RUM1TE01", "Inputs/V00WOH1RUM1TE02", 'Inputs/AlleFensterZu', 'Inputs/TuerenVerriegelt', 'Time', "Wetter/Jetzt", "Inputs/A00EIN1GEN1TE01", "Message/DispPi"]

ipaddress = constants.mqtt_.server
port = 1883

def connect(ipaddress, port):
    global client
    zeit =  time.time()
    uhr = str(strftime("%Y-%m-%d %H:%M:%S",localtime(zeit)))
    client = mqtt.Client(constants.name +'_disp_' + uhr, clean_session=False)
    assign_handlers(on_connect, dis_con, on_message)
    client.username_pw_set(username=constants.mqtt_.user,password=constants.mqtt_.password)
    client.connect(ipaddress, port, 60)
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
            print('subscribed',topic)
    elif client.connected_flag:
        pass
    else:
        print("Bad connection Returned code=",rc)

values = {'Time': '',
          'A00TER1GEN1TE01': '',
          'V00KUE1RUM1TE02': 0,
          'V00WOH1RUM1TE01': 0,
          'Status':'',
          'Alarmanlage':'',
          'Alarmstatus':'aus',
          'FensterZu' : 0,
          'TuerenVerriegelt' :0,
          'Wetter': {'Value':0, 'Min':0, 'Max':0, 'Status':''}}
innenTemp = (values['V00WOH1RUM1TE01'] + values['V00KUE1RUM1TE02']) / 2

marginTop = 16
marginLeft = 5
hintBlock = False

def drawAll(hint=None):
    global hintBlock
    if hintBlock and not hint:
        return
    draw.rectangle((0, 0, image_width, image_height), fill = 255)
    if hint:
        hintBlock = True
        draw.text((marginLeft, 32 + marginTop), hint, font = fontTime, fill = 0)
    else:
        if values['Alarmanlage'] == 'True':
            draw.text((marginLeft, 0 + marginTop), values['Time'] + " Alarmanlage ein", font = fontTime, fill = 0)
        else:
            draw.text((93, 0 + marginTop), values['Time'], font = fontTime, fill = 0)
        draw.text((marginLeft, 16 + marginTop), 'Aussen: ' + values['A00TER1GEN1TE01'] + u", " + str(values['Wetter']['Value']), font = fontTime, fill = 0)
    
        innenTemp = (values['V00WOH1RUM1TE01'] + values['V00KUE1RUM1TE02']) / 2
        draw.text((marginLeft, 32 + marginTop), 'Innen : ' + str(innenTemp) +  u"    ", font = fontTime, fill = 0)
    
        draw.text((marginLeft, 48 + marginTop), values['Wetter']['Status'], font = fontTime, fill = 0)
        draw.text((marginLeft, 64 + marginTop), str(values['Wetter']['Min']) + u"/" + str(values['Wetter']['Max']), font = fontTime, fill = 0)
    
        draw.text((marginLeft, 80 + marginTop), 'Status: ' + values['Status'], font = fontTime, fill = 0)
        
        if float(values['FensterZu']) == 1:
            draw.text((210, 75 + marginTop), 'x', font = fontTime, fill = 0)
        else:
            draw.text((210, 75 + marginTop), 'o', font = fontTime, fill = 0)
            
        if float(values['TuerenVerriegelt']) == 1:
            draw.text((220, 80 + marginTop), 'X', font = fontTime, fill = 0)
        else:
            draw.text((220, 80 + marginTop), 'O', font = fontTime, fill = 0)
    
    epd.set_frame_memory(image.transpose(Image.ROTATE_90), 0, 0)
    epd.display_frame()
#    image.save('./1.png', "PNG")
    if hint:
        time.sleep(0.5)
        hintBlock = False
        drawAll()

def clear_A00TER1GEN1TE01():
    values['A00TER1GEN1TE01'] = '-.-'
    drawAll()

A00TER1GEN1TE01_timer = threading.Timer(10 * 60, clear_A00TER1GEN1TE01)

# ab hier nur partial update
epd.init(epd.lut_partial_update)

def on_message(client, userdata, msg):
#    print(msg.topic + " " + str(msg.payload))
#    retained = msg.retain
    global A00TER1GEN1TE01_timer
    message = str(msg.payload.decode("utf-8"))
    try:
        m_in=(json.loads(message)) #decode json data

        redraw = False
        hint = None
        if 'Value' in m_in:
            m_in['Value'] = str(m_in['Value'])
        if 'Status' in m_in.values():
            values['Status'] = m_in['Value']
            redraw = True
        elif 'Alarmanlage' in m_in.values():
            values['Alarmanlage'] = m_in['Value']
            redraw = True            
        elif 'A00TER1GEN1TE01' in m_in.values():
            A00TER1GEN1TE01_timer.cancel()
            values['A00TER1GEN1TE01'] = m_in['Value']
            A00TER1GEN1TE01_timer = threading.Timer(10 * 60, clear_A00TER1GEN1TE01)
            A00TER1GEN1TE01_timer.start()
            redraw = True
        elif 'A00EIN1GEN1TE01' in m_in.values():
            A00TER1GEN1TE01_timer.cancel()
            values['A00TER1GEN1TE01'] = m_in['Value']
            A00TER1GEN1TE01_timer = threading.Timer(10 * 60, clear_A00TER1GEN1TE01)
            A00TER1GEN1TE01_timer.start()
            redraw = True            
        elif 'V00KUE1RUM1TE02' in m_in.values():
            values['V00KUE1RUM1TE02'] = float(m_in['Value'])
            redraw = True
        elif 'V00WOH1RUM1TE01' in m_in.values():
            values['V00WOH1RUM1TE01'] = float(m_in['Value'])
            redraw = True
        elif 'Time' in msg.topic:
            values['Time'] = m_in['Value']
            redraw = True
        elif 'Wetter' in msg.topic:
            values['Wetter']['Value'] = m_in['Value']
            values['Wetter']['Min'] = m_in['Min']
            values['Wetter']['Max'] = m_in['Max']
            values['Wetter']['Status'] = m_in['Status']
            redraw = True
        elif 'Message' in msg.topic:
            hint = m_in['message']
            redraw = True     
        elif 'FensterZu' in msg.topic:
            values['FensterZu'] = m_in['Value']
        elif 'TuerenVerriegelt' in msg.topic:
            values['TuerenVerriegelt'] = m_in['Value']             
        if redraw:
            drawAll(hint)
    except Exception as e:
        print('Error on', e)

def main():
    toolbox.communication.register_callback(drawAll)
    connect(ipaddress, port)
#    while constants.run:
        #draw = ImageDraw.Draw(image)
#        inp_dict = udp_send.bidirekt_new('Inputs')
#        set_dict = udp_send.bidirekt_new('Settings')
#        draw.rectangle((0, 0, image_width, image_height), fill = 255)
#        draw.text((0, 0), time.strftime('%H:%M'), font = fontTime, fill = 0)

#        draw.text((0, 26), 'Aussen: ' + inp_dict['A00TER1GEN1TE01'] + " °C", font = fontTime, fill = 0)
#        draw.text((0, 42), 'Innen : ' + inp_dict['V00KUE1RUM1TE02'] + " °C " + inp_dict['V00WOH1RUM1TE01'] + " °C", font = fontTime, fill = 0)
        #draw.text((10, 58), 'Aussen: ' + inp_dict['A00TER1GEN1TE01'] + " degC ", font = fontTime, fill = 0)
#        draw.text((0, 74), 'Status: ' + set_dict['Status'], font = fontStatus, fill = 0)
        #draw.text((10, 90), 'Status: ' + set_dict['Status'], font = fontTime, fill = 0)
#        epd.set_frame_memory(image.transpose(Image.ROTATE_90), 0, 0)
#        epd.display_frame()

#        time.sleep(60)

if __name__ == '__main__':
    main()
