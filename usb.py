import pyudev
import re
import subprocess
from socket import socket, AF_INET, SOCK_DGRAM
import csv
import paho.mqtt.client as mqtt

import udp_send
import constants

client = mqtt.Client(constants.name)
if constants.mqtt_.user != '':
    client.username_pw_set(username=constants.mqtt_.user,password=constants.mqtt_.password)
    client.connect(constants.mqtt_.server)
    client.loop_start()

server = socket( AF_INET, SOCK_DGRAM )
device_re = re.compile("Bus\s+(?P<bus>\d+)\s+Device\s+(?P<device>\d+).+ID\s(?P<id>\w+:\w+)\s(?P<tag>.+)$", re.I)


def db_out(*args):
    if constants.debug:
        print(args)


def main():
    keys = usb_key()
    keys.monitor()

class usb_key:

    usb_devs = []


    def __init__(self):
        self.data = []
        self.usb_devs = self.check_att_sticks()
        db_out(self.usb_devs)
        try:
            with open('usb_devs.csv', 'rb') as f:
                reader = csv.reader(f)
                saved_devs = list(reader)
                saved_devs = saved_devs[0]
                new_devs = list(set(self.usb_devs) - set(saved_devs))
                removed_devs = list(set(saved_devs) - set(self.usb_devs))
                for devce in new_devs:
                    self.send_to_server(devce, 1)
                for devce in removed_devs:
                    self.send_to_server(devce, 0)
                db_out('new ', new_devs)
                db_out('removed ', removed_devs)
        except:
            pass
        context = pyudev.Context()
        self.usb_monitor = pyudev.Monitor.from_netlink(context)
        self.usb_monitor.start()
        self.usb_monitor.filter_by('usb', 'usb_device')

        self.write_upd_list(self.usb_devs)
        db_out(self.usb_devs)


    def check_att_sticks(self):
        reload(pyudev)
        context = pyudev.Context()
        for device in context.list_devices(MAJOR='8'):#subsystem='block', DEVTYPE='partition'):
            if device.device_type != None:#'scsi_device':
                self.usb_devs.append(device.get('ID_SERIAL_SHORT'))
                db_out('found', device.get('ID_SERIAL_SHORT'))

        return list(set(self.usb_devs))

    @staticmethod
    def write_upd_list(liste):
        with open('usb_devs.csv', 'wb') as myfile:
            wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
            wr.writerow(liste)

    @staticmethod
    def send_to_server(devce, value):
        dicti = {'Name': 'USB.'+str(devce), 'Value': value}
        server.sendto(str(dicti) ,(constants.server1,constants.broadPort))

    def monitor(self):
        for device in iter(self.usb_monitor.poll, None):
            devce = device.get('ID_SERIAL_SHORT')
            db_out('change',devce, device.action)
            client.publish("debug/dispi/usb", devce, qos=0)
            if device.action =="remove":
                self.send_to_server(devce, 0)
                usb_devs = self.check_att_sticks()
                self.write_upd_list(usb_devs)
                db_out('removed',usb_devs)

            if device.action =="add": # and serial <> "":
                self.send_to_server(devce, 1)
                usb_devs = self.check_att_sticks()
                self.write_upd_list(usb_devs)
                db_out('add',usb_devs)

if __name__ == '__main__':
    constants.debug = True
    main()