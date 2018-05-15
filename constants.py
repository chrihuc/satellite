# -*- coding: utf-8 -*-
"""
Created on Sat Apr  2 08:27:20 2016

@author: christoph
"""
import ConfigParser
import socket

own_ip = socket.gethostbyname(socket.gethostname())

cfg_main={'Name':'Satellite1','Server1':'192.168.192.10','broadPort':5000,'biPort':5050,
          'ownIP':own_ip,
          'tifo':False,
          'OS':False,       # Operator Station
          'PiLEDs':False,
          'PiInputs':False,
          'USBkeys':False,
          'wifi':False,
          'Z-wave':False,
          'Enocean':False,
          'Z-wave Path':'/home/pi/python-openzwave/openzwave/config',
          'RasPiCam':False,
          'ePaperHat':False}
cfg_mqtt = {'Username': '', 'Password': '', 'Server': '192.168.192.10'}

config = ConfigParser.RawConfigParser()

def init_cfg():
    if not config.has_section('Main'):
        config.add_section('Main')
    for cfg in cfg_main:
        if not config.has_option('Main', cfg):
            if cfg_main.get(cfg) == '':
                value = raw_input(cfg+': ')
            else:
                value = cfg_main.get(cfg)
            config.set('Main', cfg, value)
    if not config.has_section('MQTT'):
        config.add_section('MQTT')
    for cfg in cfg_mqtt:
        if not config.has_option('MQTT', cfg):
            config.set('MQTT', cfg, cfg_mqtt.get(cfg))
    with open('satellite.cfg', 'wb') as configfile:
        config.write(configfile)

for i in range(0,2):
    try:
        config.readfp(open('satellite.cfg'))
        name = config.get('Main', 'Name')
        server1 = config.get('Main', 'Server1')
        broadPort = config.getint('Main', 'broadPort')
        biPort = config.getint('Main', 'biPort')
        ownIP = config.get('Main', 'ownIP')
        tifo = config.getboolean('Main', 'tifo')
        operatingstation = config.getboolean('Main', 'OS')
        PiLEDs = config.getboolean('Main', 'PiLEDs')
        PiInputs = config.getboolean('Main', 'PiInputs')
        USBkeys = config.getboolean('Main', 'USBkeys')
        wifi = config.getboolean('Main', 'wifi')
        zwave = config.getboolean('Main', 'Z-wave')
        enoc = config.getboolean('Main', 'Enocean')
        zwpath = config.get('Main', 'Z-wave Path')
        raspicam = config.getboolean('Main', 'RasPiCam')
        ePaperHat = config.getboolean('Main', 'ePaperHat')
        class mqtt_:
            user = config.get('MQTT', 'Username')
            password = config.get('MQTT', 'Password')
            server = config.get('MQTT', 'Server')
    except:
        init_cfg()

debug = False
debug_level = 10
debug_text = ''
run = True
LEDoutputs = {'KellerSPi':'Vm1ZIM1SAT1LI01'}
GPIO_IN = {'TuerSPIon':('V00FLU1TUE1DI01', 2)}

if __name__ == '__main__':
    print name, ownIP