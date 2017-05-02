from led_class import LEDs 
import RPi.GPIO as GPIO
import time
import pyudev
import re
import subprocess
from socket import socket, AF_INET, SOCK_DGRAM
import MySQLdb as mdb

import udp_send
import constants

led = LEDs()

server = socket( AF_INET, SOCK_DGRAM )
SERVER_IP_1   = constants.server1
SERVER_PORT = 5000


context = pyudev.Context()
monitor = pyudev.Monitor.from_netlink(context)
monitor.start()
monitor.filter_by('usb', 'usb_device')


def main():
    keys = usb_key()
    keys.monitor()
    
class usb_key:

    def __init__(self):
        self.data = []

    def monitor(self):
        for device in iter(monitor.poll, None):
            keys = udp_send.bidirekt('Bewohner')
            keys = keys + udp_send.bidirekt('Besucher')          
            if device.action =="remove":
                device_re = re.compile("Bus\s+(?P<bus>\d+)\s+Device\s+(?P<device>\d+).+ID\s(?P<id>\w+:\w+)\s(?P<tag>.+)$", re.I)
                df = subprocess.check_output("lsusb", shell=True)
                devices = []
                for i in df.split('\n'):
                    if i:
                        info = device_re.match(i)
                        if info:
                            dinfo = info.groupdict()
                            dinfo['device'] = '/dev/bus/usb/%s/%s' % (dinfo.pop('bus'), dinfo.pop('device'))
                            devices.append(dinfo)
                for key in keys:
                    if (not(key.get('prod') in str(devices))) and (key.get('USB_State') == 1):
                        dicti = {}
                        dicti['value'] = 0
                        dicti['Key'] = str(key.get('USB_ID')) 
                        dicti['prod'] = 'leer'
                        server.sendto(str(dicti),(SERVER_IP_1,SERVER_PORT))
                        #keys.remove(key) 
                       
            try:
                atts = device.attributes
                vendor = atts["idVendor"]
                product = atts["idProduct"]
                name = atts["product"]
                serial = atts["serial"]
            except KeyError:
                continue
            if device.action =="add" and serial <> "":                
                key = {}
                key['prod'] = str(vendor) +":"+ str(product)
                key['USB_ID'] = serial
                keys.append(key)
                dicti = {}
                dicti['value'] = 1
                dicti['Key'] = str(serial)  
                dicti['prod'] = str(vendor) +":"+ str(product)
                server.sendto(str(dicti),(SERVER_IP_1,SERVER_PORT))

if __name__ == '__main__':
    main()        