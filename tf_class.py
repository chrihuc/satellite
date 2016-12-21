#!/usr/bin/env python
# -*- coding: utf-8 -*-  

PORT = 4223

from functools import partial

from tinkerforge.ip_connection import IPConnection
from tinkerforge.bricklet_io16 import IO16
from tinkerforge.bricklet_led_strip import LEDStrip
from tinkerforge.bricklet_ambient_light import AmbientLight
from tinkerforge.bricklet_moisture import Moisture
from tinkerforge.bricklet_voltage_current import BrickletVoltageCurrent
from tinkerforge.bricklet_distance_us import BrickletDistanceUS
from tinkerforge.bricklet_dual_relay import BrickletDualRelay
from tinkerforge.bricklet_co2 import BrickletCO2
from tinkerforge.bricklet_motion_detector import BrickletMotionDetector
from tinkerforge.bricklet_sound_intensity import BrickletSoundIntensity
from tinkerforge.bricklet_ptc import BrickletPTC
from tinkerforge.brick_master import BrickMaster
from threading import Timer
import time
from math import log
import datetime

import tifo_config
import constants

from socket import socket, AF_INET, SOCK_DGRAM

mySocket = socket( AF_INET, SOCK_DGRAM )

# tranisiton modes
ANSTEIGEND = 0
ABSTEIGEND = 1
ZUSAMMEN = 2
GEMISCHT = 3

class io16Dict:
    def __init__(self):
        self.liste = []

    def addIO(self, IO,addr, length):
        global liste
        dicti = {}
        dicti["IO"] = IO
        dicti['addr'] = addr
        dicti["value"] = 0
        dicti["valueA"] = 0
        dicti["valueB"] = 0
        times = []
        for cnt in range(0,length):
            times.append(datetime.datetime.now())
        dicti["times"] = times
        self.liste.append(dicti)

    def setValues(self, IO,  values, port = 'a'):
        for ios in self.liste:
            if ios.get('IO') == IO:
                if port == 'a':
                    ios["valueA"] = values
                else:
                    ios["valueB"] = values
                
    def setTime(self, IO,  addr, port = 'a'):
        for ios in self.liste:
            if ios.get('IO') == IO:        
                index = int(log(addr,2))
                times = ios.get("times")
                times[index] = datetime.datetime.now()
                ios["times"] = times
                
    def getTimeDiff(self, IO,  addr, port = 'a'):
        for ios in self.liste:
            if ios.get('IO') == IO:        
                index = int(log(addr,2))
                times = ios.get("times")
                timedelta = datetime.datetime.now() - times[index]
                #times[index] = 0
                ios["times"] = times     
                return timedelta.total_seconds()

class LEDStrips:
    def __init__(self):
        self.liste = []
        
    def addLED(self, LED,addr):
        global liste
        dicti = {}
        dicti["LED"] = LED
        dicti['addr'] = addr  
        self.liste.append(dicti)        
        
class tiFo:
    
    r = [0]*16
    g = [0]*16
    b = [0]*16
    
    def __init__(self):
        self.led = None
        self.io = []
        self.io16list = io16Dict()
        self.LEDs = []
        self.LEDList = LEDStrips()
        self.al = []
        self.drb = []
        self.master = []
        self.md = []
        self.si = []
        self.ptc = []
        self.co2 = []
        self.moist = None
        # Create IP Connection
        self.ipcon = IPConnection() 
        # Register IP Connection callbacks
        self.ipcon.register_callback(IPConnection.CALLBACK_ENUMERATE, 
                                     self.cb_enumerate)
        self.ipcon.register_callback(IPConnection.CALLBACK_CONNECTED, 
                                     self.cb_connected)
        # Connect to brickd, will trigger cb_connected
        self.ipcon.connect(constants.ownIP, PORT) 
        self.unknown = []
        self.threadliste = []
        #self.ipcon.enumerate()        

    def thread_RSerror(self):
        for mastr in self.master:    
            print mastr.get_rs485_error_log()
        thread_rs_error = Timer(60, self.thread_RSerror, [])
        thread_rs_error.start()         

    def cb_ambLight(self, illuminance,device):
        thresUp = illuminance * 4/3
        thresDown = illuminance * 4 / 5
        if thresDown == 0:
            thresDown = 0
            thresUp = 3
        if thresUp > 9000:
            thresUp = 9000            
        #print illuminance, thresDown, thresUp
        device.set_illuminance_callback_threshold('o', thresDown, thresUp)
        dicti = {}
        name = tifo_config.inputs.get(str(device.get_identity()[1]) +"."+ str(device.get_identity()[0]))
        dicti['Value'] = str(illuminance)
        dicti['Name'] = name
        #print dicti
        mySocket.sendto(str(dicti) ,(constants.server1,constants.broadPort))
        
    def thread_ambLight(self, device):
        illuminance = device.get_analog_value()
        dicti = {}
        name = tifo_config.inputs.get(str(device.get_identity()[1]) +"."+ str(device.get_identity()[0]))
        dicti['Value'] = str(illuminance)
        dicti['Name'] = name
        #print dicti
        mySocket.sendto(str(dicti) ,(constants.server1,constants.broadPort))
        thread_cb_amb = Timer(60, self.thread_ambLight, [device])
        thread_cb_amb.start()        

    def thread_CO2(self, device):
        value = device.get_co2_concentration()
        dicti = {}
        name = tifo_config.inputs.get(str(device.get_identity()[1]) +"."+ str(device.get_identity()[0]))
        dicti['Value'] = str(value)
        dicti['Name'] = name
        mySocket.sendto(str(dicti) ,(constants.server1,constants.broadPort))
        thread_co2_ = Timer(60, self.thread_CO2, [device])
        thread_co2_.start()

    def thread_pt(self, device):
        value = device.get_temperature()
        dicti = {}
        name = tifo_config.inputs.get(str(device.get_identity()[1]) +"."+ str(device.get_identity()[0]))
        dicti['Value'] = str(float(value)/100)
        dicti['Name'] = name
        mySocket.sendto(str(dicti) ,(constants.server1,constants.broadPort))
        thread_pt_ = Timer(60, self.thread_pt, [device])
        thread_pt_.start()

    def cb_interrupt(self, port, interrupt_mask, value_mask, device, uid):
        #print('Interrupt on port: ' + port + str(bin(interrupt_mask)))
        #print('Value: ' + str(bin(value_mask)))
        namelist = []
        temp_uid = uid #str(device.get_identity()[1]) +"."+ str(device.get_identity()[0])
        bit_list = [(1 << bit) for bit in range(7, -1, -1)]
        for wert in bit_list:
            if interrupt_mask & wert > 0:
                name = tifo_config.IO16i.get(temp_uid).get(port + str(bin(wert)))
                if name <> None:
                    namelist.append(name)
        if port == 'a':
            nc_mask = tifo_config.IO16.get(temp_uid)[7]
        else:
            nc_mask = tifo_config.IO16.get(temp_uid)[8]
        value = (value_mask&interrupt_mask)/interrupt_mask
        nc_pos = (nc_mask&interrupt_mask)/interrupt_mask
        dicti = {}
#        dicti['Name'] = name
#        dicti['temp_uid'] = temp_uid
#        dicti['name'] = port + str(bin(interrupt_mask))
        #print name, value
        self.io16list.setValues(device,value_mask,port)
        #print self.io16list.getTimeDiff(device,interrupt_mask, port)
        if value == nc_pos:        
            dicti['Value'] = self.io16list.getTimeDiff(device,interrupt_mask, port)
        else:
            dicti['Value'] = 0
            self.io16list.setTime(device,interrupt_mask, port)
        #print dicti
        for name in namelist:
            dicti['Name'] = name
            mySocket.sendto(str(dicti) ,(constants.server1,constants.broadPort))       

    def cb_md(self, device, uid):
        dicti = {'Name':tifo_config.inputs.get(uid),'Value':1}
        mySocket.sendto(str(dicti) ,(constants.server1,constants.broadPort))
        
    def cb_md_end(self, device, uid):
        dicti = {'Name':tifo_config.inputs.get(uid),'Value':0}
        mySocket.sendto(str(dicti) ,(constants.server1,constants.broadPort))      

    def cb_si(self,value, device, uid):
        dicti = {'Name':tifo_config.inputs.get(uid),'Value':value}
        mySocket.sendto(str(dicti) ,(constants.server1,constants.broadPort)) 

    def set_io16_sub(self,cmd,io,value):
        port = cmd.get('Port') 
        if port  == 'A':
            flopmask = tifo_config.IO16.get(io.get('addr'))[4]
            if flopmask & cmd.get('Pin') > 0:
                if value == 1:
                    normpos = tifo_config.IO16.get(io.get('addr'))[7]
                    io.get('IO').set_port_monoflop('a', cmd.get('Pin'),((~normpos)&0b11111111),tifo_config.IO16.get(io.get('addr'))[6])
            else:
                if value == 1:
                    mask = io.get('valueA') | cmd.get('Pin')
                else:
                    mask = io.get('valueA') & (0b11111111 & ~ cmd.get('Pin'))
                self.io16list.setValues(io.get('IO'),mask,'a')
                io.get('IO').set_port('a',mask)
        else:
            flopmask = tifo_config.IO16.get(io.get('addr'))[5]
            if flopmask & cmd.get('Pin') > 0:
                if value == 1:
                    #working but gets overwritten but other commands
#                    normpos = tifo_config.IO16.get(io.get('addr'))[8]
#                    io.get('IO').set_port_monoflop('b', cmd.get('Pin'),((~normpos)&0b11111111),tifo_config.IO16.get(io.get('addr'))[6]) 
                    mask = io.get('IO').get_port('b') | cmd.get('Pin')
                    io.get('IO').set_port('b',mask)
                    time.sleep(float(tifo_config.IO16.get(io.get('addr'))[6])/1000)
                    mask = io.get('IO').get_port('b') & (0b11111111 & ~ cmd.get('Pin'))
                    io.get('IO').set_port('b',mask)   
            else:
                if value == 1:
                    mask = io.get('IO').get_port('b') | cmd.get('Pin')
                else:
                    mask = io.get('IO').get_port('b') & (0b11111111 & ~ cmd.get('Pin'))
                self.io16list.setValues(io.get('IO'),mask,'b')
                io.get('IO').set_port('b',mask)       

    def set_io16(self,device,value):
        #koennte noch auch .set_selected_values(port, selection_mask, value_mask) umgeschrieben werden
        #monoflop tut nicht
        cmd_lsts = tifo_config.IO16o.get(device)
        for cmd in cmd_lsts:
            if cmd.get('Value') == value:
                cmds = cmd.get('Commands')
                #print cmds
                if type(cmds) in (list,tuple):
                    for cmd in cmds:
                        #print cmd
                        if cmd.get('Value') == 0: #erst alle auf Null setzen
                            addr = cmd.get('UID') 
                            for io in self.io16list.liste:
                                if io.get('addr') == addr:
                                    self.set_io16_sub(cmd,io,cmd.get('Value'))
                    for cmd in cmds:                            
                        if cmd.get('Value') == 1: #erst alle auf Null setzen
                            addr = cmd.get('UID') 
                            for io in self.io16list.liste:
                                if io.get('addr') == addr:
                                    self.set_io16_sub(cmd,io,cmd.get('Value'))    
                else:
                    cmd = cmds
                    addr = cmd.get('UID') 
                    for io in self.io16list.liste:
                        if io.get('addr') == addr:
                            self.set_io16_sub(cmd,io,cmd.get('Value'))
        return True                           

    def _set_LED_zusammen(self,LED,start,ende,red,green,blue,transitiontime):
        laenge = (ende-start)                        
        o_r, o_g, o_b = LED.get('LED').get_rgb_values(start, 1)
        steps = abs(red-o_r) + abs(green-o_g) + abs(blue-o_b)
        wartezeit = float(transitiontime) / steps 
        while o_r <> red or o_g <> green or o_b <> blue:
            while (laenge) > 16:
                laenge = 16
                if (red-o_r) > 0:
                    o_r = o_r + 1
                    LED.get('LED').set_rgb_values(start, laenge, o_r, o_g, o_b)
                    time.sleep(wartezeit)
                elif (red-o_r) < 0:
                    o_r = o_r - 1
                    LED.get('LED').set_rgb_values(start, laenge, o_r, o_g, o_b)
                    time.sleep(wartezeit)
                if (green-o_g) > 0:
                    o_g = o_g + 1
                    LED.get('LED').set_rgb_values(start, laenge, o_r, o_g, o_b)
                    time.sleep(wartezeit)
                elif (green-o_g) < 0:
                    o_g = o_g - 1
                    LED.get('LED').set_rgb_values(start, laenge, o_r, o_g, o_b)
                    time.sleep(wartezeit) 
                if (blue-o_b) > 0:
                    o_b = o_b + 1
                    LED.get('LED').set_rgb_values(start, laenge, o_r, o_g, o_b)
                    time.sleep(wartezeit)
                elif (blue-o_b) < 0:
                    o_b = o_b - 1
                    LED.get('LED').set_rgb_values(start, laenge, o_r, o_g, o_b)
                    time.sleep(wartezeit)                                     
                start += laenge
                laenge = (ende-start)
            else:
                if (red-o_r) > 0:
                    o_r = o_r + 1
                    LED.get('LED').set_rgb_values(start, laenge, o_r, o_g, o_b)
                    time.sleep(wartezeit)
                elif (red-o_r) < 0:
                    o_r = o_r - 1
                    LED.get('LED').set_rgb_values(start, laenge, o_r, o_g, o_b)
                    time.sleep(wartezeit)
                if (green-o_g) > 0:
                    o_g = o_g + 1
                    LED.get('LED').set_rgb_values(start, laenge, o_r, o_g, o_b)
                    time.sleep(wartezeit)
                elif (green-o_g) < 0:
                    o_g = o_g - 1
                    LED.get('LED').set_rgb_values(start, laenge, o_r, o_g, o_b)
                    time.sleep(wartezeit) 
                if (blue-o_b) > 0:
                    o_b = o_b + 1
                    LED.get('LED').set_rgb_values(start, laenge, o_r, o_g, o_b)
                    time.sleep(wartezeit)
                elif (blue-o_b) < 0:
                    o_b = o_b - 1
                    LED.get('LED').set_rgb_values(start, laenge, o_r, o_g, o_b)
                    time.sleep(wartezeit)       
        
    def set_LED(self, **kwargs):
#        device, rot, gruen, blau, transitiontime, transition=ANSTEIGEND
        device = kwargs.get('Device')
        green = int(kwargs.get('red',0))
        blue = int(kwargs.get('green',0))
        red = int(kwargs.get('blue',0))
        transitiontime = kwargs.get('transitiontime')
        transition = kwargs.get('transition',ANSTEIGEND)
        proc = kwargs.get('percentage',None)

        red_1 = kwargs.get('blue_1','None')
        green_1 = kwargs.get('red_1','None')
        blue_1 = kwargs.get('green_1','None')

        red_2 = int(kwargs.get('blue_2',0))
        green_2 = int(kwargs.get('red_2',0))
        blue_2 = int(kwargs.get('green_2',0))        

#        gradient
#        lauflicht          
        LEDDict = tifo_config.LEDsOut.get(device)
        uid = LEDDict.get('UID')
        start = LEDDict.get('Start')
        ende = LEDDict.get('Ende')
#        TODO vectorize
        delta_r = 0
        delta_g = 0
        delta_b = 0        
        if str(red_1) == 'None' and str(green_1) == 'None' and str(blue_1) == 'None':
            red = [int(red)]*16
            green = [int(green)]*16
            blue = [int(blue)]*16 
            gradient = False
        else:
            laenge = (ende-start)
            if not str(red_1) == 'None':
                delta_r = int(red_1) - int(red)
                delta_pr = float(delta_r) / laenge
            else:
                delta_pr = 0
            if not str(green_1) == 'None':
                delta_g = (int(green_1) -int(green))
                delta_pg = float(delta_g) / laenge
            else:
                delta_pg = 0                
            if not str(blue_1) == 'None':
                delta_b = (int(blue_1) - int(blue))    
                delta_pb = float(delta_b) / laenge 
            else:
                delta_pb = 0 
            gradient = True

        for LED in self.LEDList.liste:
            if LED.get('addr') == uid:
                laenge = (ende-start)
                if proc <> None and 0 <= proc <= 100:
                    laenge = int(float(proc)/100 * laenge)                  
                elif proc <> None and proc < 0:
                    laenge = 0  
                if (transitiontime == None or transitiontime <= 0) and not gradient:                  
                    while (laenge) > 16:
                        laenge = 16
#                         TODO check that command is executed
#                        while not (red, green, blue) == LED.get('LED').get_rgb_values(start, laenge):
                        LED.get('LED').set_rgb_values(start, laenge, red, green, blue)
                        start += laenge
                        laenge = (ende-start)
                    else:
                        LED.get('LED').set_rgb_values(start, laenge, red, green, blue)
                elif not (transitiontime == None or transitiontime <= 0):
#                    Ansteigend
                    if transition == ANSTEIGEND:
                        wartezeit = float(transitiontime) / (ende-start)
                        for birne in range(start,ende):
                            LED.get('LED').set_rgb_values(birne, 1, red, green, blue)  
                            time.sleep(wartezeit)
                    elif transition == ABSTEIGEND:
                        wartezeit = float(transitiontime) / (ende-start)
                        for birne in list(reversed(range(start,ende))):
                            LED.get('LED').set_rgb_values(birne, 1, red, green, blue)  
                            time.sleep(wartezeit)        
                    elif transition == ZUSAMMEN:
                        self._set_LED_zusammen(LED,start,ende,red,green,blue,transitiontime)  
                else:
                    for birne in range(start,laenge):
                        LED.get('LED').set_rgb_values(birne, 1, [int(red)]*16, [int(green)]*16, [int(blue)]*16)  
                        red += delta_pr
                        green += delta_pg
                        blue += delta_pb  
                    for birne in range(laenge,ende):
                        LED.get('LED').set_rgb_values(birne, 1, [int(red_2)]*16, [int(green_2)]*16, [int(blue_2)]*16)                          
#        TODO Transition, 4 types
#        von links nach rechts (ansteigend), von rechts nach links (absteigend)
#        alle zusammen, beides                

        return True
         
    def set_drb(self, device, value):
        uid_cmds = tifo_config.DualRelay.get(device) 
        uid = ''
        for cmd in uid_cmds:
            if (cmd.get('Value')) == float(value):
                uid = cmd.get('UID')
                state = cmd.get('state')
                relaynr = cmd.get('relay')
        for relay in self.drb:
            temp_uid = str(relay.get_identity()[1]) +"."+ str(relay.get_identity()[0])
            if temp_uid == uid:
                relay.set_selected_state(relaynr, state)
                return True
        return False
         
         
    def set_device(self, data_ev): 
#       TODO do threaded with stop criteria
        if tifo_config.outputs.get(data_ev.get('Device')) == 'IO16o':
            return self.set_io16(data_ev.get('Device'),data_ev.get('Value'))
        elif tifo_config.outputs.get(data_ev.get('Device')) == 'IO16o':
            return self.set_io16(data_ev.get('Device'),data_ev.get('Value'))
        elif tifo_config.outputs.get(data_ev.get('Device')) == 'LEDs':
            return self.set_LED(**data_ev) #data_ev.get('Device'),data_ev.get('red'),data_ev.get('green'),data_ev.get('blue'),data_ev.get('transitiontime'))      
        elif tifo_config.outputs.get(data_ev.get('Device')) == 'DualRelay':
            return self.set_drb(data_ev.get('Device'),data_ev.get('Value'))            
        else:
            return False

    def cb_enumerate(self, uid, connected_uid, position, hardware_version, 
                     firmware_version, device_identifier, enumeration_type):
        #global self.led
        found = False
        if enumeration_type == IPConnection.ENUMERATION_TYPE_CONNECTED or \
           enumeration_type == IPConnection.ENUMERATION_TYPE_AVAILABLE:
            # Enumeration for LED
            if device_identifier == LEDStrip.DEVICE_IDENTIFIER:
                self.LEDs.append(LEDStrip(uid, self.ipcon))
                temp_uid = str(self.LEDs[-1].get_identity()[1]) +"."+ str(self.LEDs[-1].get_identity()[0])
                self.LEDList.addLED(self.LEDs[-1],temp_uid)
                self.LEDs[-1].set_frame_duration(200)
                if tifo_config.LEDs.get(temp_uid) <> None:
                    self.LEDs[-1].set_chip_type(tifo_config.LEDs.get(temp_uid)[0])
                    self.LEDs[-1].set_frame_duration(tifo_config.LEDs.get(temp_uid)[1])
                    found  = True
                #self.led.register_callback(self.led.CALLBACK_FRAME_RENDERED, 
                #                lambda x: __cb_frame_rendered__(self.led, x))
                #self.led.set_rgb_values(0, self.NUM_LEDS, self.r, self.g, self.b)
                #self.led.set_rgb_values(15, self.NUM_LEDS, self.r, self.g, self.b)
                #self.led.set_rgb_values(30, self.NUM_LEDS, self.r, self.g, self.b)

            if device_identifier == IO16.DEVICE_IDENTIFIER:
                self.io.append(IO16(uid, self.ipcon))
                temp_uid = str(self.io[-1].get_identity()[1]) +"."+ str(self.io[-1].get_identity()[0])
                self.io16list.addIO(self.io[-1],temp_uid,16)
                self.io[-1].set_debounce_period(100)
                if tifo_config.IO16.get(temp_uid) <> None:
                    self.io[-1].set_port_interrupt('a', tifo_config.IO16.get(temp_uid)[0])
                    self.io[-1].set_port_interrupt('b', tifo_config.IO16.get(temp_uid)[1])
                    self.io[-1].set_port_configuration('a', tifo_config.IO16.get(temp_uid)[0],'i',True)
                    self.io[-1].set_port_configuration('b', tifo_config.IO16.get(temp_uid)[1],'i',True)                    
                    self.io[-1].set_port_configuration('a', tifo_config.IO16.get(temp_uid)[2],'o',False)
                    self.io[-1].set_port_configuration('b', tifo_config.IO16.get(temp_uid)[3],'o',False)
                    #self.io[-1].set_port_monoflop('a', tifo_config.IO16.get(temp_uid)[4],0,tifo_config.IO16.get(temp_uid)[6])
                    #self.io[-1].set_port_monoflop('b', tifo_config.IO16.get(temp_uid)[5],0,tifo_config.IO16.get(temp_uid)[6])
                    self.io[-1].register_callback(self.io[-1].CALLBACK_INTERRUPT, partial( self.cb_interrupt, device = self.io[-1], uid = temp_uid ))
                    found  = True
             
            if device_identifier == AmbientLight.DEVICE_IDENTIFIER:
                self.al.append(AmbientLight(uid, self.ipcon))
                self.al[-1].set_illuminance_callback_threshold('o', 0, 0)
                self.al[-1].set_debounce_period(10)
                #self.al.set_illuminance_callback_threshold('<', 30, 30)
                #self.al.set_analog_value_callback_period(10000)
                #self.al.set_illuminance_callback_period(10000)
                #self.al.register_callback(self.al.CALLBACK_ILLUMINANCE, self.cb_ambLight)
                #self.al.register_callback(self.al.CALLBACK_ILLUMINANCE_REACHED, self.cb_ambLight)
                args = self.al[-1]
                #self.al[-1].register_callback(self.al[-1].CALLBACK_ILLUMINANCE_REACHED, lambda event1, event2, event3, args=args: self.cb_ambLight(event1, event2, event3, args))
                self.al[-1].register_callback(self.al[-1].CALLBACK_ILLUMINANCE_REACHED, partial( self.cb_ambLight,  device=args))
                temp_uid = str(self.al[-1].get_identity()[1]) +"."+ str(self.al[-1].get_identity()[0])
                
                #thread_cb_amb.start()                 
                if tifo_config.inputs.get(temp_uid) <> None:
                    found  = True
                    thread_cb_amb = Timer(60, self.thread_ambLight, [self.al[-1]])

            if device_identifier == BrickletCO2.DEVICE_IDENTIFIER:
                self.co2.append(BrickletCO2(uid, self.ipcon))
                temp_uid = str(self.co2[-1].get_identity()[1]) +"."+ str(self.co2[-1].get_identity()[0])
                if tifo_config.inputs.get(temp_uid) <> None:
                    found  = True  
                    thread_co2_ = Timer(5, self.thread_CO2, [self.co2[-1]])
                    thread_co2_.start()    
                    self.threadliste.append(thread_co2_)

            if device_identifier == BrickletDualRelay.DEVICE_IDENTIFIER:
                self.drb.append(BrickletDualRelay(uid, self.ipcon))
#                
#            if device_identifier == Moisture.DEVICE_IDENTIFIER:
#                self.moist = Moisture(uid, self.ipcon)
#                self.moist.set_moisture_callback_period(10000)
#                self.moist.register_callback(self.moist.CALLBACK_MOISTURE, self.cb_moisture)
            
            if device_identifier == BrickletMotionDetector.DEVICE_IDENTIFIER:   
                self.md.append(BrickletMotionDetector(uid, self.ipcon))
                temp_uid = str(self.md[-1].get_identity()[1]) +"."+ str(self.md[-1].get_identity()[0])
                self.md[-1].register_callback(self.md[-1].CALLBACK_MOTION_DETECTED, partial( self.cb_md, device = self.md[-1], uid = temp_uid ))  
                self.md[-1].register_callback(self.md[-1].CALLBACK_DETECTION_CYCLE_ENDED, partial( self.cb_md_end, device = self.md[-1], uid = temp_uid ))
                if tifo_config.inputs.get(temp_uid) <> None:
                    found  = True                
            
            if device_identifier == BrickletSoundIntensity.DEVICE_IDENTIFIER:   
                self.si.append(BrickletSoundIntensity(uid, self.ipcon))
                temp_uid = str(self.si[-1].get_identity()[1]) +"."+ str(self.si[-1].get_identity()[0])
                if tifo_config.inputs.get(temp_uid) <> None:
                    found  = True             
                    self.si[-1].set_debounce_period(tifo_config.SoundInt.get(temp_uid)[0])                
                    self.si[-1].register_callback(self.si[-1].CALLBACK_INTENSITY_REACHED, partial( self.cb_si, device = self.si[-1], uid = temp_uid ))  
                    self.si[-1].set_intensity_callback_threshold(tifo_config.SoundInt.get(temp_uid)[1], tifo_config.SoundInt.get(temp_uid)[2], tifo_config.SoundInt.get(temp_uid)[3])                    
            
            if device_identifier == BrickletPTC.DEVICE_IDENTIFIER:
                self.ptc.append(BrickletPTC(uid, self.ipcon))
                temp_uid = str(self.ptc[-1].get_identity()[1]) +"."+ str(self.ptc[-1].get_identity()[0])
                if tifo_config.inputs.get(temp_uid) <> None:
                    found  = True  
                    thread_pt_ = Timer(5, self.thread_pt, [self.ptc[-1]])
                    thread_pt_.start()   
                    self.threadliste.append(thread_pt_)
            
            if device_identifier == BrickMaster.DEVICE_IDENTIFIER:   
                self.master.append(BrickMaster(uid, self.ipcon))
                thread_rs_error = Timer(60, self.thread_RSerror, [])
                #thread_rs_error.start()       
                if tifo_config.inputs.get(uid) <> None:
                    found  = True                 
            
            if not found:
                print connected_uid, uid, device_identifier

        
    def cb_connected(self, connected_reason):
        # Enumerate devices again. If we reconnected, the Bricks/Bricklets
        # may have been offline and the configuration may be lost.
        # In this case we don't care for the reason of the connection
        self.ipcon.enumerate()     

class volt_cur:
    def __init__(self):
        self.vc = None

        # Create IP Connection
        self.ipcon = IPConnection() 

        # Register IP Connection callbacks
        self.ipcon.register_callback(IPConnection.CALLBACK_ENUMERATE, 
                                     self.cb_enumerate)
        self.ipcon.register_callback(IPConnection.CALLBACK_CONNECTED, 
                                     self.cb_connected)

        # Connect to brickd, will trigger cb_connected
        self.ipcon.connect(constants.ownIP, PORT) 
        #self.ipcon.enumerate()                 
       
    
    def cb_reached_vc(self):        
        voltage = self.vc.get_voltage()
        dicti = {}
        dicti['value'] = str(voltage)
        dicti['name'] = 'Voltage'
        mySocket.sendto(str(dicti),(constants.server1,constants.broadPort)) 
        mySocket.sendto(str(dicti),(constants.server1,constants.broadPort)) 
        current = self.vc.get_current()
        dicti = {}
        dicti['value'] = str(current)
        dicti['name'] = 'Current'
        mySocket.sendto(str(dicti),(constants.server1,constants.broadPort)) 
        mySocket.sendto(str(dicti),(constants.server1,constants.broadPort))         
        thread_cb_reached = Timer(60, self.cb_reached_vc, [])
        thread_cb_reached.start()        
       
    
    # Callback handles device connections and configures possibly lost 
    # configuration of lcd and temperature callbacks, backlight etc.
    def cb_enumerate(self, uid, connected_uid, position, hardware_version, 
                     firmware_version, device_identifier, enumeration_type):

        if enumeration_type == IPConnection.ENUMERATION_TYPE_CONNECTED or \
           enumeration_type == IPConnection.ENUMERATION_TYPE_AVAILABLE:
            
            # Enumeration for V/C
            if device_identifier == BrickletVoltageCurrent.DEVICE_IDENTIFIER:
                self.vc = BrickletVoltageCurrent(uid, self.ipcon)
                self.cb_reached_vc()
        
    def cb_connected(self, connected_reason):
        # Enumerate devices again. If we reconnected, the Bricks/Bricklets
        # may have been offline and the configuration may be lost.
        # In this case we don't care for the reason of the connection
        self.ipcon.enumerate()    
        
class dist_us:
    def __init__(self):
        self.dus = None

        # Create IP Connection
        self.ipcon = IPConnection() 

        # Register IP Connection callbacks
        self.ipcon.register_callback(IPConnection.CALLBACK_ENUMERATE, 
                                     self.cb_enumerate)
        self.ipcon.register_callback(IPConnection.CALLBACK_CONNECTED, 
                                     self.cb_connected)

        # Connect to brickd, will trigger cb_connected
        self.ipcon.connect(constants.ownIP, PORT) 
        #self.ipcon.enumerate()                 
       
    
    def cb_distance(self, distance):        
        dicti = {}
        dicti['value'] = str(distance)
        dicti['name'] = str(self.dus.get_identity()[0]) + "_" + str(self.dus.get_identity()[5])
        mySocket.sendto(str(dicti),(constants.server1,constants.broadPort)) 
        mySocket.sendto(str(dicti),(constants.server1,constants.broadPort)) 
       
    
    # Callback handles device connections and configures possibly lost 
    # configuration of lcd and temperature callbacks, backlight etc.
    def cb_enumerate(self, uid, connected_uid, position, hardware_version, 
                     firmware_version, device_identifier, enumeration_type):

        if enumeration_type == IPConnection.ENUMERATION_TYPE_CONNECTED or \
           enumeration_type == IPConnection.ENUMERATION_TYPE_AVAILABLE:
            
            # Enumeration for Distance US
            if device_identifier == BrickletDistanceUS.DEVICE_IDENTIFIER:
                self.dus = BrickletDistanceUS(uid, self.ipcon)
                self.dus.register_callback(self.dus.CALLBACK_DISTANCE, self.cb_distance)
                self.dus.set_distance_callback_period(10000)

        
    def cb_connected(self, connected_reason):
        # Enumerate devices again. If we reconnected, the Bricks/Bricklets
        # may have been offline and the configuration may be lost.
        # In this case we don't care for the reason of the connection
        self.ipcon.enumerate()          
        
    
if __name__ == "__main__":
    #sb = dist_us()
    data_ev = {}
    tf = tiFo()
#    time.sleep(2)
#    data_ev['Device'] = 'V00WOH1SRA1LI11'
#    data_ev['Value'] = 1   
#    tf.set_device(data_ev)    
#    time.sleep(2)
#    data_ev['Device'] = 'V00WOH1SRA1LI11'
#    data_ev['Value'] = 0   
#    tf.set_device(data_ev)     
#    data_ev['Device'] = 'V00WOH1SRA1LI01'
#    data_ev['red'] = 255
#    data_ev['green'] = 0
#    data_ev['blue'] = 0    
#    tf.set_device(data_ev) 
#        
#    time.sleep(2)
#    data_ev['Device'] = 'V00WOH1SRA1LI02'
#    data_ev['red'] = 0
#    data_ev['green'] = 255
#    data_ev['blue'] = 0    
#    tf.set_device(data_ev)
#
#    time.sleep(2)
#    data_ev['Device'] = 'V00WOH1SRA1LI03'
#    data_ev['red'] = 0
#    data_ev['green'] = 0
#    data_ev['blue'] = 255    
#    tf.set_device(data_ev)    
#        
#    time.sleep(2)
#    data_ev['Device'] = 'V01ZIM1RUM1DO01'
#    data_ev['Value'] = 0
#    tf.set_device(data_ev) 
#    data_ev['Device'] = 'V01ZIM1RUM1DO02'
#    data_ev['Value'] = 1
#    tf.set_device(data_ev)    
#        
#    time.sleep(2)        
#    data_ev['Device'] = 'V01ZIM1RUM1DO01'
#    data_ev['Value'] = 1
#    tf.set_device(data_ev)   
#    data_ev['Device'] = 'V01ZIM1RUM1DO02'
#    data_ev['Value'] = 0
#    tf.set_device(data_ev) 
#    data_ev['Device'] = 'V01ZIM1RUM1DO03'
#    data_ev['Value'] = 1
#    tf.set_device(data_ev) 
#
#    time.sleep(2)        
#    data_ev['Device'] = 'V01ZIM1RUM1DO01'
#    data_ev['Value'] = 1
#    tf.set_device(data_ev) 
#    
#    time.sleep(2)        
#    data_ev['Device'] = 'V01ZIM1RUM1DO01'
#    data_ev['Value'] = 0
#    tf.set_device(data_ev) 
#    data_ev['Device'] = 'V01ZIM1RUM1DO02'
#    data_ev['Value'] = 1
#    tf.set_device(data_ev) 
#    data_ev['Device'] = 'V01ZIM1RUM1DO03'
#    data_ev['Value'] = 0    
#    tf.set_device(data_ev) 
#    raw_input('Press key to exit\n') # Use input() in Python 3   
#    #sb.set_one_color(rot = 255)
    raw_input('Press key to exit\n')   
    #time.sleep(15)
    #sb.flash(start = 0, new = True, n_blau = 255) 
    #sb.flash(start = 15, new = True, n_blau = 255)
    #sb.flash(start = 30, new = True, n_blau = 255)
    #sb.flash(start = 30, new = True, reverse = True, n_gruen = 255)
    #sb.flash(start = 15, new = True, reverse = True, n_gruen = 255)
    #sb.flash(start = 0, new = True, reverse = True, n_gruen = 255)    
    #raw_input('Press key to exit\n') 
    #ipcon.disconnect()
