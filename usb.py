import pyudev
import re
import subprocess
from socket import socket, AF_INET, SOCK_DGRAM
import csv

import udp_send
import constants


server = socket( AF_INET, SOCK_DGRAM )
SERVER_IP_1   = constants.server1
SERVER_PORT = 5000


device_re = re.compile("Bus\s+(?P<bus>\d+)\s+Device\s+(?P<device>\d+).+ID\s(?P<id>\w+:\w+)\s(?P<tag>.+)$", re.I)

usb_devs = []

context = pyudev.Context()

def check_att_sticks():
    for device in context.list_devices(MAJOR='8'):#subsystem='block', DEVTYPE='partition'):
        if device.device_type != None:#'scsi_device':
            usb_devs.append(device.get('ID_SERIAL_SHORT'))
    
    return list(set(usb_devs))

def write_upd_list(liste):
    with open('usb_devs.csv', 'wb') as myfile:
        wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
        wr.writerow(liste)  

def send_to_server(devce, value):
    dicti = {'USB_Stick': devce, 'Value': value}
    print dicti    

usb_devs = check_att_sticks()

try:
    with open('usb_devs.csv', 'rb') as f:
        reader = csv.reader(f)
        saved_devs = list(reader)
        saved_devs = saved_devs[0]
        new_devs = list(set(usb_devs) - set(saved_devs))
        removed_devs = list(set(saved_devs) - set(usb_devs))
        print 'new ', new_devs
        print 'removed ', removed_devs
except:
    pass

monitor = pyudev.Monitor.from_netlink(context)
monitor.start()
monitor.filter_by('usb', 'usb_device')

write_upd_list(usb_devs)

def main():
    keys = usb_key()
    keys.monitor()
    
class usb_key:

    def __init__(self):
        self.data = []

    def monitor(self):
        for device in iter(monitor.poll, None):
            devce = device.get('ID_SERIAL_SHORT')         
            if device.action =="remove":
                send_to_server(devce, 0)
                usb_devs = check_att_sticks()
                write_upd_list(usb_devs)
                
            if device.action =="add": # and serial <> "":                
                send_to_server(devce, 1)
                usb_devs = check_att_sticks()
                write_upd_list(usb_devs)

if __name__ == '__main__':
    main()        