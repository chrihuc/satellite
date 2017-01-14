from led_class import LEDs 
import RPi.GPIO as GPIO
import time
import pyudev
import re
import subprocess
from socket import socket, AF_INET, SOCK_DGRAM
import MySQLdb as mdb

led = LEDs()

server = socket( AF_INET, SOCK_DGRAM )
SERVER_IP_1   = '192.168.192.10'
SERVER_IP_2   = '192.168.192.33'
OWN_IP   = '192.168.192.32'
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

    def read_mysql(self, table):
        for k in range(4):
            try:        
                con = mdb.connect('192.168.192.10', 'python_user', 'python', 'XS1DB')
                dicti = {}
                liste = []
                with con:
                    cur = con.cursor()
                    sql = 'SELECT * FROM ' + table
                    cur.execute(sql)
                    results = cur.fetchall()
                    field_names = [i[0] for i in cur.description]
                    j = 0
                    for row in results:
                        for i in range (0,len(row)):
                            dicti[field_names[i]] = row[i]
                        liste.append(dicti)
                        dicti = {}
                        j = j + 1
                con.close()
                return liste  
            except:
                pass 
            
    def read_mysql_2(self, table):
        for k in range(4):
            try:        
                con = mdb.connect('192.168.192.33', 'customer', 'user', 'XS1DB')
                dicti = {}
                liste = []
                with con:
                    cur = con.cursor()
                    sql = 'SELECT * FROM ' + table
                    cur.execute(sql)
                    results = cur.fetchall()
                    field_names = [i[0] for i in cur.description]
                    j = 0
                    for row in results:
                        for i in range (0,len(row)):
                            dicti[field_names[i]] = row[i]
                        liste.append(dicti)
                        dicti = {}
                        j = j + 1
                con.close()
                return liste  
            except:
                pass            

    def led_send(self, rot, gelb, gruen, erinnern):
        dicti = {}
        dicti['Rot'] = rot
        dicti['Gelb'] = gelb
        dicti['Gruen'] = gruen  
        dicti['erinnern'] = erinnern
        for k in range(4):
            try:
                server.sendto(str(dicti),(OWN_IP,SERVER_PORT))  
                return
            except:
                pass

    def monitor(self):
        for device in iter(monitor.poll, None):
            keys = self.read_mysql("Bewohner")
            keys = keys + self.read_mysql("Besucher") 
            #keys = keys + self.read_mysql_2("Bewohner")
            #keys = keys + self.read_mysql_2("Besucher")             
            if device.action =="remove":
                self.led_send("Aus","An","Aus",True)
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
                        server.sendto(str(dicti),(SERVER_IP_2,SERVER_PORT))
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
                self.led_send("Aus","An","Aus",True)                
                key = {}
                key['prod'] = str(vendor) +":"+ str(product)
                key['USB_ID'] = serial
                keys.append(key)
                dicti = {}
                dicti['value'] = 1
                dicti['Key'] = str(serial)  
                dicti['prod'] = str(vendor) +":"+ str(product)
                server.sendto(str(dicti),(SERVER_IP_1,SERVER_PORT))
                server.sendto(str(dicti),(SERVER_IP_2,SERVER_PORT))

if __name__ == '__main__':
    main()        