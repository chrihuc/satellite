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
import json

import constants

epd = epd2in13.EPD()
epd.init(epd.lut_full_update)
#epd.init(epd.lut_partial_update)
fontTime = ImageFont.truetype('./display/FreeMonoBold.ttf', 16)
fontStatus = ImageFont.truetype('./display/FreeMonoBold.ttf', 18)
#epd.delay_ms(2000)

image = Image.new('1', (epd2in13.EPD_HEIGHT, epd2in13.EPD_WIDTH), 255)  # 255: clear the frame
draw = ImageDraw.Draw(image)
image_width, image_height  = image.size
draw.rectangle((0, 0, image_width, image_height), fill = 0)

#epd.clear_frame_memory(255)
#epd.set_frame_memory(image.transpose(Image.ROTATE_90), 0, 0)
#epd.display_frame()
#
#draw.rectangle((0, 0, image_width, image_height), fill = 255)
#epd.clear_frame_memory(255)
#epd.set_frame_memory(image.transpose(Image.ROTATE_90), 0, 0)
#epd.display_frame()
#epd.set_frame_memory(image.transpose(Image.ROTATE_90), 0, 0)
#epd.display_frame()

## neu leeren
#emptimage = Image.new('1', (epd2in13.EPD_WIDTH, 32), 255)
#emptdraw = ImageDraw.Draw(emptimage)
#emptimage_width, emptimage_height  = emptimage.size
#for k in range(0, 3):
#    emptdraw.rectangle((0, 0, emptimage_width, emptimage_height), fill = 255)
#    epd.set_frame_memory(emptimage.transpose(Image.ROTATE_270), 0, k * 32)
#    epd.display_frame()

epd.clear_frame_memory(0xFF)
epd.display_frame()
epd.clear_frame_memory(0xFF)
epd.display_frame()

if True:
    pix_size = 32 # 32 ging 64 nicht
    pixel = Image.new('1', (pix_size,pix_size), 0)
    for x in range(0,epd2in13.EPD_WIDTH,pix_size):
        for y in range(0,epd2in13.EPD_HEIGHT,pix_size):
            for fc in range(2):
                epd.set_frame_memory(pixel, x, y)
                epd.display_frame()
            print(x,y)

print('Cleared')
#image.save('./1.png', "PNG")

mqtt.Client.connected_flag=False
client = None
topics = ["Settings/Status", "Inputs/A00TER1GEN1TE01", "Inputs/V00WOH1RUM1TE01", "Inputs/V00WOH1RUM1TE02"]
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
            print('subscrived',topic)
    elif client.connected_flag:
        pass
    else:
        print("Bad connection Returned code=",rc)

def on_message(client, userdata, msg):
#    print(msg.topic + " " + str(msg.payload))
#    retained = msg.retain
    try:
        m_in=(json.loads(msg.payload)) #decode json data
#        draw.rectangle((0, 0, image_width, image_height), fill = 255)
#        print(m_in)
        if 'Status' in m_in.values():
#            print('Status: ' + m_in['Value'])
            draw.text((0, 74), 'Status: ' + m_in['Value'], font = fontStatus, fill = 0)
        elif 'A00TER1GEN1TE01' in m_in.values():
#            print('Aussen: ' + m_in['Value'])
            draw.text((0, 26), 'Aussen: ' + m_in['Value'] + u" °C", font = fontTime, fill = 0)
        elif 'V00KUE1RUM1TE02' in m_in.values():
            draw.text((0, 42), 'Innen: ' + m_in['Value'] + u" °C", font = fontTime, fill = 0)
#            print('Innen: ' + m_in['Value'])
        elif 'V00WOH1RUM1TE01' in m_in.values():
#            print('Innen: ' + m_in['Value'])
            draw.text((40, 42), 'Innen: ' + m_in['Value'] + u" °C", font = fontTime, fill = 0)
        epd.set_frame_memory(image.transpose(Image.ROTATE_90), 0, 0)
        epd.display_frame()
        image.save('./1.png', "PNG")
    except Exception as e:
        print('Error on', e)

def main():
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