# -*- coding: utf-8 -*-
"""
Created on Fri Dec 08 18:18:47 2017

@author: chuckle
"""

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
from tinkerforge.bricklet_temperature import BrickletTemperature
from tinkerforge.brick_master import BrickMaster
from threading import Timer
import time
from math import log
import datetime

import constants
from tools import toolbox

# on server:
#from tifo import settings

# on satellite:
import tifo_config as settings
import udp_send

def broadcast_input_value(Name, Value):
    payload = {'Name':Name,'Value':Value}
#    on server:
#    toolbox.log(Name, Value)
#    toolbox.communication.send_message(payload, typ='InputValue')
    
#    on satellite:
    udp_send.send_to_server(Name, Value)


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

class TiFo:

    r = [0]*16
    g = [0]*16
    b = [0]*16
    
    ipcon = None

    led = None
    io = []
    io16list = io16Dict()
    LEDs = []
    LEDList = LEDStrips()
    al = []
    drb = []
    master = []
    md = []
    si = []
    ptc = []
    temp = []
    co2 = []
    moist = None
    unknown = []
    threadliste = []

    def __init__(self):
        pass
#        self.led = None
#        self.io = []
#        self.io16list = io16Dict()
#        self.LEDs = []
#        self.LEDList = LEDStrips()
#        self.al = []
#        self.drb = []
#        self.master = []
#        self.md = []
#        self.si = []
#        self.ptc = []
#        self.co2 = []
#        self.moist = None
#        self.unknown = []
#        self.threadliste = []
        #self.ipcon.enumerate()

    @classmethod
    def main(cls):
        # Create IP Connection
        cls.ipcon = IPConnection()
        # Register IP Connection callbacks
        cls.ipcon.register_callback(IPConnection.CALLBACK_ENUMERATE,
                                     cls.cb_enumerate)
        cls.ipcon.register_callback(IPConnection.CALLBACK_CONNECTED,
                                     cls.cb_connected)
        # Connect to brickd, will trigger cb_connected
        cls.ipcon.connect('localhost', PORT)
#        on server:
#        while constants.run:
#            time.sleep(10)

    @classmethod
    def thread_RSerror(cls):
        while constants.run:
            for mastr in cls.master:
                print mastr.get_rs485_error_log()
            time.sleep(60)

    @staticmethod
    def cb_ambLight(illuminance,device):
        thresUp = illuminance * 4/3
        thresDown = illuminance * 4 / 5
        if thresDown == 0:
            thresDown = 0
            thresUp = 3
        if thresUp > 9000:
            thresUp = 9000
        device.set_illuminance_callback_threshold('o', thresDown, thresUp)
        name = str(device.get_identity()[1]) +"."+ str(device.get_identity()[0])
        broadcast_input_value('TiFo.' + name, str(illuminance))

    @classmethod
    def thread_ambLight(cls, device):
        while constants.run:
            illuminance = device.get_illuminance()
            name = str(device.get_identity()[1]) +"."+ str(device.get_identity()[0])
            broadcast_input_value('TiFo.' + name, str(illuminance))
            time.sleep(60)

    @classmethod
    def thread_CO2(cls, device):
        value = device.get_co2_concentration()
        name = str(device.get_identity()[1]) +"."+ str(device.get_identity()[0])
        broadcast_input_value('TiFo.' + name, str(value))
        thread_co2_ = Timer(60, cls.thread_CO2, [device])
        thread_co2_.start()

    @classmethod
    def thread_pt(cls, device):
        value = device.get_temperature()
        name = str(device.get_identity()[1]) +"."+ str(device.get_identity()[0])
        broadcast_input_value('TiFo.' + name, str(float(value)/100))
        thread_pt_ = Timer(60, cls.thread_pt, [device])
        thread_pt_.start()

    @classmethod
    def cb_interrupt(cls, port, interrupt_mask, value_mask, device, uid):
        #print('Interrupt on port: ' + port + str(bin(interrupt_mask)))
        #print('Value: ' + str(bin(value_mask)))
        namelist = []
        temp_uid = uid #str(device.get_identity()[1]) +"."+ str(device.get_identity()[0])
        bit_list = [(1 << bit) for bit in range(7, -1, -1)]
        for wert in bit_list:
            if interrupt_mask & wert > 0:
                name = settings.IO16i.get(temp_uid).get(port + str(bin(wert)))
                name = temp_uid + "." + port + str(bin(wert))
                if name <> None:
                    namelist.append(name)
        if port == 'a':
            nc_mask = settings.IO16.get(temp_uid)[7]
        else:
            nc_mask = settings.IO16.get(temp_uid)[8]
        value = (value_mask&interrupt_mask)/interrupt_mask
        nc_pos = (nc_mask&interrupt_mask)/interrupt_mask
        dicti = {}
#        dicti['Name'] = name
#        dicti['temp_uid'] = temp_uid
#        dicti['name'] = port + str(bin(interrupt_mask))
        #print name, value
        cls.io16list.setValues(device,value_mask,port)
        #print self.io16list.getTimeDiff(device,interrupt_mask, port)
        if value == nc_pos:
            Value = cls.io16list.getTimeDiff(device,interrupt_mask, port)
        else:
            Value = 0
            cls.io16list.setTime(device,interrupt_mask, port)
        #print dicti
        for name in namelist:
            broadcast_input_value('TiFo.' + name, Value)
#            dicti['Name'] = 'TiFo.' + name
#            mySocket.sendto(str(dicti) ,(constants.server1,constants.broadPort))

    @staticmethod
    def cb_md(device, uid):
#        dicti = {'Name':settings.inputs.get(uid),'Value':1}
        broadcast_input_value('TiFo.' + str(device.get_identity()[1]) +"."+ str(device.get_identity()[0]), 1)
#        dicti = {'Name':'TiFo.' + str(device.get_identity()[1]) +"."+ str(device.get_identity()[0]),'Value':1}
#        mySocket.sendto(str(dicti) ,(constants.server1,constants.broadPort))

    @staticmethod
    def cb_md_end(device, uid):
#        dicti = {'Name':settings.inputs.get(uid),'Value':0}
        broadcast_input_value('TiFo.' + str(device.get_identity()[1]) +"."+ str(device.get_identity()[0]), 0)
#        dicti = {'Name':'TiFo.' + str(device.get_identity()[1]) +"."+ str(device.get_identity()[0]),'Value':0}
#        mySocket.sendto(str(dicti) ,(constants.server1,constants.broadPort))

    @staticmethod
    def cb_si(value, device, uid):
#        dicti = {'Name':settings.inputs.get(uid),'Value':value}
        broadcast_input_value('TiFo.' + str(device.get_identity()[1]) +"."+ str(device.get_identity()[0]), value)
#        dicti = {'Name':'TiFo.' + str(device.get_identity()[1]) +"."+ str(device.get_identity()[0]),'Value':value}
#        mySocket.sendto(str(dicti) ,(constants.server1,constants.broadPort))

    @classmethod
    def set_io16_sub(cls,cmd,io,value):
        port = cmd.get('Port')
        toolbox.log(cmd,io,value,port)
        if port  == 'A':
            flopmask = settings.IO16.get(io.get('addr'))[4]
            if flopmask & cmd.get('Pin') > 0:
                if value == 1:
                    normpos = settings.IO16.get(io.get('addr'))[7]
                    io.get('IO').set_port_monoflop('a', cmd.get('Pin'),((~normpos)&0b11111111),settings.IO16.get(io.get('addr'))[6])
            else:
                if value == 1:
                    mask = io.get('valueA') | cmd.get('Pin')
                else:
                    mask = io.get('valueA') & (0b11111111 & ~ cmd.get('Pin'))
                cls.io16list.setValues(io.get('IO'),mask,'a')
                io.get('IO').set_port('a',mask)
        else:
            flopmask = settings.IO16.get(io.get('addr'))[5]
            if flopmask & cmd.get('Pin') > 0:
                if value == 1:
                    #working but gets overwritten but other commands
                    normpos = settings.IO16.get(io.get('addr'))[8]
                    io.get('IO').set_port_monoflop('b', cmd.get('Pin'),((~normpos)&0b11111111),settings.IO16.get(io.get('addr'))[6])
                    toolbox.log('b', cmd.get('Pin'),((~normpos)&0b11111111),settings.IO16.get(io.get('addr'))[6])
#                    mask = io.get('IO').get_port('b') | cmd.get('Pin')
#                    io.get('IO').set_port('b',mask)
#                    time.sleep(float(settings.IO16.get(io.get('addr'))[6])/1000)
#                    mask = io.get('IO').get_port('b') & (0b11111111 & ~ cmd.get('Pin'))
#                    io.get('IO').set_port('b',mask)
            else:
                if value == 1:
                    mask = io.get('IO').get_port('b') | cmd.get('Pin')
                else:
                    mask = io.get('IO').get_port('b') & (0b11111111 & ~ cmd.get('Pin'))
                cls.io16list.setValues(io.get('IO'),mask,'b')
                io.get('IO').set_port('b',mask)

    @classmethod
    def set_io16(cls,device,value):
        #koennte noch auch .set_selected_values(port, selection_mask, value_mask) umgeschrieben werden
        #monoflop tut nicht
        toolbox.log(device,value)
        cmd_lsts = settings.IO16o.get(device)
        success = False
        for cmd in cmd_lsts:
            if str(cmd.get('Value')) == str(value):
                cmds = cmd.get('Commands')
                #print cmds
                if type(cmds) in (list,tuple):
                    for cmd in cmds:
                        #print cmd
                        if str(cmd.get('Value')) == '0': #erst alle auf Null setzen
                            addr = cmd.get('UID')
                            for io in cls.io16list.liste:
                                if io.get('addr') == addr:
                                    cls.set_io16_sub(cmd,io,cmd.get('Value'))
                                    success = True
                    for cmd in cmds:
                        if str(cmd.get('Value')) == '1': #erst alle auf Null setzen
                            addr = cmd.get('UID')
                            for io in cls.io16list.liste:
                                if io.get('addr') == addr:
                                    cls.set_io16_sub(cmd,io,cmd.get('Value'))
                                    success = True
                else:
                    cmd = cmds
                    addr = cmd.get('UID')
                    for io in cls.io16list.liste:
                        if io.get('addr') == addr:
                            cls.set_io16_sub(cmd,io,cmd.get('Value'))
                            success = True
        return success

    @staticmethod
    def _set_LED_zusammen(LED,start,ende,red,green,blue,transitiontime):
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

    @classmethod
    def set_LED(cls, **kwargs):
#        device, rot, gruen, blau, transitiontime, transition=ANSTEIGEND
        device = kwargs.get('Device')
#        range check kwargs
        try:
            for varia in ['red','green','blue']:
                if int(kwargs.get(varia)) > 255:
                    kwargs[varia] = 255
                if int(kwargs.get(varia)) < 0:
                    kwargs[varia] = 0
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
        except:
            print(kwargs)
            return False
#        gradient
#        lauflicht
        LEDDict = settings.LEDsOut.get(device)
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

        for LED in cls.LEDList.liste:
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
                        cls._set_LED_zusammen(LED,start,ende,red,green,blue,transitiontime)
                else:
                    for birne in range(start,(start+laenge)):
                        LED.get('LED').set_rgb_values(birne, 1, [int(red)]*16, [int(green)]*16, [int(blue)]*16)
                        red += delta_pr
                        green += delta_pg
                        blue += delta_pb
                    for birne in range((start+laenge),ende):
                        LED.get('LED').set_rgb_values(birne, 1, [int(red_2)]*16, [int(green_2)]*16, [int(blue_2)]*16)
#        TODO Transition, 4 types
#        von links nach rechts (ansteigend), von rechts nach links (absteigend)
#        alle zusammen, beides

        return True

    @classmethod
    def set_drb(cls, device, value):
        uid_cmds = settings.DualRelay.get(device)
        uid = ''
        for cmd in uid_cmds:
            if (cmd.get('Value')) == float(value):
                uid = cmd.get('UID')
                state = cmd.get('state')
                relaynr = cmd.get('relay')
        for relay in cls.drb:
            temp_uid = str(relay.get_identity()[1]) +"."+ str(relay.get_identity()[0])
            if temp_uid == uid:
                relay.set_selected_state(relaynr, state)
                return True
        return False

    @classmethod
    def receive_communication(cls, payload, *args, **kwargs):
        if toolbox.kw_unpack(kwargs,'typ') == 'output' and toolbox.kw_unpack(kwargs,'receiver') == 'TiFo':
            result = cls.set_device(payload)
            toolbox.communication.send_message(payload, typ='return', value=result)

    @classmethod
    def set_device(cls, data_ev):
#       TODO do threaded with stop criteria
        toolbox.log(data_ev)
        if settings.outputs.get(data_ev.get('Device')) == 'IO16o':
            return cls.set_io16(data_ev.get('Device'),data_ev.get('Value'))
        elif settings.outputs.get(data_ev.get('Device')) == 'IO16o':
            return cls.set_io16(data_ev.get('Device'),data_ev.get('Value'))
        elif settings.outputs.get(data_ev.get('Device')) == 'LEDs':
            return cls.set_LED(**data_ev) #data_ev.get('Device'),data_ev.get('red'),data_ev.get('green'),data_ev.get('blue'),data_ev.get('transitiontime'))
        elif settings.outputs.get(data_ev.get('Device')) == 'DualRelay':
            return cls.set_drb(data_ev.get('Device'),data_ev.get('Value'))
        else:
            return False

    @classmethod
    def cb_enumerate(cls, uid, connected_uid, position, hardware_version,
                     firmware_version, device_identifier, enumeration_type):
        #global self.led
        found = False
        if enumeration_type == IPConnection.ENUMERATION_TYPE_CONNECTED or \
           enumeration_type == IPConnection.ENUMERATION_TYPE_AVAILABLE:
            # Enumeration for LED
            if device_identifier == LEDStrip.DEVICE_IDENTIFIER:
                cls.LEDs.append(LEDStrip(uid, cls.ipcon))
                temp_uid = str(cls.LEDs[-1].get_identity()[1]) +"."+ str(cls.LEDs[-1].get_identity()[0])
                cls.LEDList.addLED(cls.LEDs[-1],temp_uid)
                cls.LEDs[-1].set_frame_duration(200)
                if settings.LEDs.get(temp_uid) <> None:
                    cls.LEDs[-1].set_chip_type(settings.LEDs.get(temp_uid)[0])
                    cls.LEDs[-1].set_frame_duration(settings.LEDs.get(temp_uid)[1])
                    found  = True
                #self.led.register_callback(self.led.CALLBACK_FRAME_RENDERED,
                #                lambda x: __cb_frame_rendered__(self.led, x))
                #self.led.set_rgb_values(0, self.NUM_LEDS, self.r, self.g, self.b)
                #self.led.set_rgb_values(15, self.NUM_LEDS, self.r, self.g, self.b)
                #self.led.set_rgb_values(30, self.NUM_LEDS, self.r, self.g, self.b)

            if device_identifier == IO16.DEVICE_IDENTIFIER:
                cls.io.append(IO16(uid, cls.ipcon))
                temp_uid = str(cls.io[-1].get_identity()[1]) +"."+ str(cls.io[-1].get_identity()[0])
                cls.io16list.addIO(cls.io[-1],temp_uid,16)
                cls.io[-1].set_debounce_period(100)
                if settings.IO16.get(temp_uid) <> None:
                    cls.io[-1].set_port_interrupt('a', settings.IO16.get(temp_uid)[0])
                    cls.io[-1].set_port_interrupt('b', settings.IO16.get(temp_uid)[1])
                    cls.io[-1].set_port_configuration('a', settings.IO16.get(temp_uid)[0],'i',True)
                    cls.io[-1].set_port_configuration('b', settings.IO16.get(temp_uid)[1],'i',True)
                    cls.io[-1].set_port_configuration('a', settings.IO16.get(temp_uid)[2],'o',False)
                    cls.io[-1].set_port_configuration('b', settings.IO16.get(temp_uid)[3],'o',False)
                    #self.io[-1].set_port_monoflop('a', tifo_config.IO16.get(temp_uid)[4],0,tifo_config.IO16.get(temp_uid)[6])
                    #self.io[-1].set_port_monoflop('b', tifo_config.IO16.get(temp_uid)[5],0,tifo_config.IO16.get(temp_uid)[6])
                    cls.io[-1].register_callback(cls.io[-1].CALLBACK_INTERRUPT, partial( cls.cb_interrupt, device = cls.io[-1], uid = temp_uid ))
                    found  = True

            if device_identifier == AmbientLight.DEVICE_IDENTIFIER:
                cls.al.append(AmbientLight(uid, cls.ipcon))
                cls.al[-1].set_illuminance_callback_threshold('o', 0, 0)
                cls.al[-1].set_debounce_period(10)
                #self.al.set_illuminance_callback_threshold('<', 30, 30)
                #self.al.set_analog_value_callback_period(10000)
                #self.al.set_illuminance_callback_period(10000)
                #self.al.register_callback(self.al.CALLBACK_ILLUMINANCE, self.cb_ambLight)
                #self.al.register_callback(self.al.CALLBACK_ILLUMINANCE_REACHED, self.cb_ambLight)
                args = cls.al[-1]
                #self.al[-1].register_callback(self.al[-1].CALLBACK_ILLUMINANCE_REACHED, lambda event1, event2, event3, args=args: self.cb_ambLight(event1, event2, event3, args))

                cls.al[-1].register_callback(cls.al[-1].CALLBACK_ILLUMINANCE_REACHED, partial( cls.cb_ambLight,  device=args))
                temp_uid = str(cls.al[-1].get_identity()[1]) +"."+ str(cls.al[-1].get_identity()[0])

                thread_cb_amb = Timer(60, cls.thread_ambLight, [cls.al[-1]])
                thread_cb_amb.start()

            if device_identifier == BrickletCO2.DEVICE_IDENTIFIER:
                cls.co2.append(BrickletCO2(uid, cls.ipcon))
                temp_uid = str(cls.co2[-1].get_identity()[1]) +"."+ str(cls.co2[-1].get_identity()[0])
                thread_co2_ = Timer(5, cls.thread_CO2, [cls.co2[-1]])
                thread_co2_.start()
                cls.threadliste.append(thread_co2_)


            if device_identifier == BrickletDualRelay.DEVICE_IDENTIFIER:
                cls.drb.append(BrickletDualRelay(uid, cls.ipcon))
#
#            if device_identifier == Moisture.DEVICE_IDENTIFIER:
#                self.moist = Moisture(uid, self.ipcon)
#                self.moist.set_moisture_callback_period(10000)
#                self.moist.register_callback(self.moist.CALLBACK_MOISTURE, self.cb_moisture)

            if device_identifier == BrickletMotionDetector.DEVICE_IDENTIFIER:
                cls.md.append(BrickletMotionDetector(uid, cls.ipcon))
                temp_uid = str(cls.md[-1].get_identity()[1]) +"."+ str(cls.md[-1].get_identity()[0])
                cls.md[-1].register_callback(cls.md[-1].CALLBACK_MOTION_DETECTED, partial( cls.cb_md, device = cls.md[-1], uid = temp_uid ))
                cls.md[-1].register_callback(cls.md[-1].CALLBACK_DETECTION_CYCLE_ENDED, partial( cls.cb_md_end, device = cls.md[-1], uid = temp_uid ))

            if device_identifier == BrickletSoundIntensity.DEVICE_IDENTIFIER:
                cls.si.append(BrickletSoundIntensity(uid, cls.ipcon))
                temp_uid = str(cls.si[-1].get_identity()[1]) +"."+ str(cls.si[-1].get_identity()[0])

                cls.si[-1].set_debounce_period(1000)
                cls.si[-1].register_callback(cls.si[-1].CALLBACK_INTENSITY_REACHED, partial( cls.cb_si, device = cls.si[-1], uid = temp_uid ))
                cls.si[-1].set_intensity_callback_threshold('>',200,0)

            if device_identifier == BrickletPTC.DEVICE_IDENTIFIER:
                cls.ptc.append(BrickletPTC(uid, cls.ipcon))
                temp_uid = str(cls.ptc[-1].get_identity()[1]) +"."+ str(cls.ptc[-1].get_identity()[0])
                thread_pt_ = Timer(5, cls.thread_pt, [cls.ptc[-1]])
                thread_pt_.start()
                cls.threadliste.append(thread_pt_)

            if device_identifier == BrickletTemperature.DEVICE_IDENTIFIER:
                cls.temp.append(BrickletTemperature(uid, cls.ipcon))
                temp_uid = str(cls.temp[-1].get_identity()[1]) +"."+ str(cls.temp[-1].get_identity()[0])
                thread_pt_ = Timer(5, cls.thread_pt, [cls.temp[-1]])
                thread_pt_.start()
                cls.threadliste.append(thread_pt_)

            if device_identifier == BrickMaster.DEVICE_IDENTIFIER:
                cls.master.append(BrickMaster(uid, cls.ipcon))
                thread_rs_error = Timer(60, cls.thread_RSerror, [])
                #thread_rs_error.start()
                if settings.inputs.get(uid) <> None:
                    found  = True

            if not found:
                toolbox.log(connected_uid, uid, device_identifier)
                print connected_uid, uid, device_identifier

    @classmethod
    def cb_connected(cls, connected_reason):
        # Enumerate devices again. If we reconnected, the Bricks/Bricklets
        # may have been offline and the configuration may be lost.
        # In this case we don't care for the reason of the connection
        cls.ipcon.enumerate()

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

toolbox.communication.register_callback(TiFo.receive_communication)

if __name__ == "__main__":
    #sb = dist_us()
    data_ev = {}
    tf = TiFo()
    tf.main()
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