#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
@author: christoph
"""

import constants
import paho.mqtt.client as mqtt
import json
import datetime
import time
from time import localtime,strftime

import urllib



zeit =  time.time()
uhr = str(strftime("%Y-%m-%d %H:%M:%S",localtime(zeit)))
client = mqtt.Client(constants.name +'_pub_' + uhr)
client.username_pw_set(username=constants.mqtt_.user,password=constants.mqtt_.password)
client.connect(constants.mqtt_.server)
client.loop_start()

def handler(obj):
    if hasattr(obj, 'isoformat'):
        return obj.isoformat()
    elif isinstance(obj, datetime.timedelta):
        return obj.seconds
    else:
        return 'non Json'

 
def send_pic():
    urllib.urlretrieve("http://192.168.192.36/html/cam.jpg", "tuerspi.jpg")
    f=open("tuerspi.jpg", "rb") #3.7kiB in same folder
    fileContent = f.read() #String
    byteArr = (bytearray(fileContent)) # working
#    byteArr = (bytes(fileContent)) # working
    client.publish('Image/Satellite/' + constants.name + '/Channel1' ,byteArr,1,retain=True)
#    client.publish('Image/' + constants.name,'test',1,retain=True)
    print('pic send')

def mqtt_pub(channel, data, retain=True):
    zeit =  time.time()
    uhr = str(strftime("%Y-%m-%d %H:%M:%S",localtime(zeit)))    
    if isinstance(data, dict):
        data['ts'] = uhr
        data = json.dumps(data, default=handler, allow_nan=False)
        client.publish(channel, data, qos=1, retain=retain)
    else:
        raise TypeError, 'Data is not a dictionary'
        
if __name__ == '__main__':
    send_pic()