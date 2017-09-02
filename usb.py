import pyudev
import re
import subprocess
from socket import socket, AF_INET, SOCK_DGRAM
import csv

import udp_send
import constants


server = socket( AF_INET, SOCK_DGRAM )


device_re = re.compile("Bus\s+(?P<bus>\d+)\s+Device\s+(?P<device>\d+).+ID\s(?P<id>\w+:\w+)\s(?P<tag>.+)$", re.I)

usb_devs = []

context = pyudev.Context()

def db_out(*args):
    if constants.debug:
        print(args)

def check_att_sticks():
#    global usb_devs
    for device in context.list_devices(MAJOR='8'):#subsystem='block', DEVTYPE='partition'):
        db_out('iterating', device.get('ID_SERIAL_SHORT'))
        if device.device_type != None:#'scsi_device':
            usb_devs.append(device.get('ID_SERIAL_SHORT'))
            db_out('found', device.get('ID_SERIAL_SHORT'))
    
    return list(set(usb_devs))

def write_upd_list(liste):
    with open('usb_devs.csv', 'wb') as myfile:
        wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
        wr.writerow(liste)  

def send_to_server(devce, value):
    dicti = {'Name': 'USB.'+str(devce), 'Value': value}
    server.sendto(str(dicti) ,(constants.server1,constants.broadPort))  

usb_devs = check_att_sticks()
db_out(usb_devs)

try:
    with open('usb_devs.csv', 'rb') as f:
        reader = csv.reader(f)
        saved_devs = list(reader)
        saved_devs = saved_devs[0]
        new_devs = list(set(usb_devs) - set(saved_devs))
        removed_devs = list(set(saved_devs) - set(usb_devs))
        for devce in new_devs:
            send_to_server(devce, 1)
        for devce in removed_devs:
            send_to_server(devce, 0)
        db_out('new ', new_devs)
        db_out('removed ', removed_devs)
except:
    pass

monitor = pyudev.Monitor.from_netlink(context)
monitor.start()
monitor.filter_by('usb', 'usb_device')

write_upd_list(usb_devs)
db_out(usb_devs)

def main():
    keys = usb_key()
    keys.monitor()
    
class usb_key:

    def __init__(self):
        self.data = []

    def monitor(self):
        for device in iter(monitor.poll, None):
            devce = device.get('ID_SERIAL_SHORT')
            db_out('change',devce)
            if device.action =="remove":
                send_to_server(devce, 0)
                usb_devs = check_att_sticks()
                write_upd_list(usb_devs)
                db_out('removed',usb_devs)
                
            if device.action =="add": # and serial <> "":                
                send_to_server(devce, 1)
                usb_devs = check_att_sticks()
                write_upd_list(usb_devs)
                db_out('add',usb_devs)                

if __name__ == '__main__':
    main()        