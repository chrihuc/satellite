#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
@author: christoph
"""

from display import epd2in13
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

import udp_send
import time

epd = epd2in13.EPD()
epd.init(epd.lut_full_update)

image = Image.new('1', (epd2in13.EPD_WIDTH, epd2in13.EPD_HEIGHT), 255)  # 255: clear the frame
draw = ImageDraw.Draw(image)
image_width, image_height  = image.size
draw.rectangle((0, 0, image_width, image_height), fill = 255)
#draw.rectangle((0, 10, 128, 30), fill = 0)
fontTime = ImageFont.truetype('./display/FreeMonoBold.ttf', 16)
fontStatus = ImageFont.truetype('./display/FreeMonoBold.ttf', 18)

epd.clear_frame_memory(0xFF)
epd.set_frame_memory(image.transpose(Image.ROTATE_90), 0, 0)
epd.display_frame()
epd.set_frame_memory(image.transpose(Image.ROTATE_90), 0, 0)
epd.display_frame()
epd.delay_ms(2000)
epd.set_frame_memory(image.transpose(Image.ROTATE_90), 0, 0)

epd.display_frame()
        
def main():
    while 1:
        #draw = ImageDraw.Draw(image)
        inp_dict = udp_send.bidirekt_new('Inputs')
        set_dict = udp_send.bidirekt_new('Settings')
        draw.rectangle((0, 0, image_width, image_height), fill = 255)
        draw.text((0, 0), time.strftime('%H:%M'), font = fontTime, fill = 0)
        
        draw.text((0, 26), 'Aussen: ' + inp_dict['A00TER1GEN1TE01'] + " °C", font = fontTime, fill = 0)
        draw.text((0, 42), 'Innen : ' + inp_dict['V00KUE1RUM1TE02'] + " °C " + inp_dict['V00WOH1RUM1TE01'] + " °C", font = fontTime, fill = 0)
        #draw.text((10, 58), 'Aussen: ' + inp_dict['A00TER1GEN1TE01'] + " degC ", font = fontTime, fill = 0)
        draw.text((0, 74), 'Status: ' + set_dict['Status'], font = fontStatus, fill = 0)
        #draw.text((10, 90), 'Status: ' + set_dict['Status'], font = fontTime, fill = 0)
        epd.set_frame_memory(image.transpose(Image.ROTATE_90), 0, 80)
        epd.display_frame()
        
        time.sleep(60)        