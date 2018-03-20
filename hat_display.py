#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sun Mar 18 20:15:21 2018

@author: christoph
"""

import spidev as SPI
import EPD_driver
import datetime

EPD2X9 = 0
EPD02X13 = 1
EPD1X54 = 0

bus = 0 
device = 0
 	

disp = EPD_driver.EPD_driver(spi=SPI.SpiDev(bus, device))

#init and Clear full screen
print '------------init and Clear full screen------------'
disp.Dis_Clear_full()

#String
#print '------------Show string------------'
disp.Dis_String(0, 10, "SHOW TIME : ",16)
disp.Dis_String(0, 26, "I am an electronic paper display",12)


#time
print '------------show time------------'
while 1 :
	now = datetime.datetime.now()
	now_sec = now.second%10
	next_sec = 11  #Guaranteed next greater than 9
	if now_sec != next_sec:
		disp.Dis_showtime(now.hour,now.minute,now.second)
		next_sec = now.second%10
		
		