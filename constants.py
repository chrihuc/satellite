# -*- coding: utf-8 -*-
"""
Created on Sat Apr  2 08:27:20 2016

@author: christoph
"""
import ConfigParser

cfg_main={'Name':'Satellite1','Server1':'192.168.192.10','broadPort':5000,'biPort':5005,
          'ownIP':'127.0.0.1','tifo':False,'OS':False}

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
    except:
        init_cfg()