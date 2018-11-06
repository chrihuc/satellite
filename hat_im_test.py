#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 11 11:29:13 2018

@author: christoph
"""

from PIL import Image, ImageDraw
from PIL import ImageFont
import time

from display import epd2in13

#image = Image.new('1', (250, 128), 255) 
#
#
#fontTime = ImageFont.truetype('./display/FreeMonoBold.ttf', 16)
#fontStatus = ImageFont.truetype('./display/FreeMonoBold.ttf', 18)
#
#draw = ImageDraw.Draw(image)
##draw.line((0, 0) + image.size, fill=128)
##draw.line((0, image.size[1], image.size[0], 0), fill=0)
##del draw
#draw.text((0, 0), time.strftime('%H:%M'), font = fontTime, fill = 0)
#
#image = image.transpose(Image.ROTATE_90)
## write to stdout
#image.save('./test.png', "PNG")

epd = epd2in13.EPD()
epd.init(epd.lut_full_update)
epd.clear_frame_memory(0xFF)
epd.display_frame()
epd.clear_frame_memory(0xFF)
epd.display_frame()

time.sleep(60)

pixel = Image.new('1', (8,8), 0)
for x in range(0,epd2in13.EPD_WIDTH,8):
    for y in range(0,epd2in13.EPD_HEIGHT,8):
        for fc in range(2):
            epd.set_frame_memory(pixel, x, y)
            epd.display_frame()
#        print(x,y)

time.sleep(30)

pixel = Image.new('1', (8,8), 0)
for x in range(0,epd2in13.EPD_WIDTH,8):
    for y in range(0,epd2in13.EPD_HEIGHT,8):
            epd.set_frame_memory(pixel, x, y)
            epd.display_frame()
#            print(x,y)
            
time.sleep(30)  

pixel = Image.new('1', (8,8), 255)
for x in range(0,epd2in13.EPD_WIDTH,8):
    for y in range(0,epd2in13.EPD_HEIGHT,8):
        for fc in range(2):
            epd.set_frame_memory(pixel, x, y)
            epd.display_frame()
#        print(x,y)     