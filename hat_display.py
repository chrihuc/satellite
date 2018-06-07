#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
@author: christoph
"""

from display import epd2in13
import Image
import ImageDraw
import ImageFont

import udp_send
import time

epd = epd2in13.EPD()
epd.init(epd.lut_full_update)

image = Image.new('1', (epd2in13.EPD_WIDTH, epd2in13.EPD_HEIGHT), 255)  # 255: clear the frame
draw = ImageDraw.Draw(image)
fontTime = ImageFont.truetype('/usr/share/fonts/truetype/freefont/FreeMonoBold.ttf', 16)
fontStatus = ImageFont.truetype('/usr/share/fonts/truetype/freefont/FreeMonoBold.ttf', 18)

    

def main():
    while 1:
        draw = ImageDraw.Draw(image)
        inp_dict = udp_send.bidirekt_new('Inputs')
        set_dict = udp_send.bidirekt_new('Settings')

        draw.text((10, 0), time.strftime('%M:%S'), font = fontTime, fill = 0)
        
        draw.text((10, 26), 'Aussen: ' + inp_dict['A00TER1GEN1TE01'] + " °C", font = fontTime, fill = 0)
        draw.text((10, 42), 'Innen : ' + inp_dict['V00KUE1RUM1TE02'] + " °C " + inp_dict['V00WOH1RUM1TE01'] + " °C", font = fontTime, fill = 0)
        #draw.text((10, 58), 'Aussen: ' + inp_dict['A00TER1GEN1TE01'] + " degC ", font = fontTime, fill = 0)
        draw.text((10, 74), 'Status: ' + set_dict['Status'], font = fontStatus, fill = 0)
        #draw.text((10, 90), 'Status: ' + set_dict['Status'], font = fontTime, fill = 0)

        time.sleep(60)        