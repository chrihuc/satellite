#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sun Mar 18 20:15:21 2018

@author: christoph
"""

import time
import spidev as SPI
import EPD_driver
import datetime
import udp_send

EPD2X9 = 0
EPD02X13 = 1
EPD1X54 = 0

bus = 0
device = 0
DELAYTIME = 1.5

disp = EPD_driver.EPD_driver(spi=SPI.SpiDev(bus, device))


disp.Dis_Clear_full()
disp.Dis_Clear_part()

#disp.Dis_String(0, 10, "SHOW TIME : ",16)
#disp.Dis_String(0, 26, "I am an electronic paper display",12)

#time
print '------------show time------------'
while 1 :
    now = datetime.datetime.now()
#	now_sec = now.second%10
#	next_sec = 11  #Guaranteed next greater than 9
#	if now_sec != next_sec:
#		disp.Dis_showtime(now.hour,now.minute,now.second)
#		next_sec = now.second%10
    inp_dict = udp_send.bidirekt_new('Inputs')
    set_dict = udp_send.bidirekt_new('Settings')
    disp.Dis_showtime(now.hour,now.minute,0)
    disp.Dis_String(10, 26, inp_dict['A00TER1GEN1TE01'] + " grad Celsius",16)
    disp.Dis_String(10, 42, set_dict['Status'] + " grad Celsius",16)
    time.sleep(60)
