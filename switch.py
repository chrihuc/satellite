 
import RPi.GPIO as GPIO
import time
from socket import socket, AF_INET, SOCK_DGRAM
from camera import usb_cam
import threading

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

server = socket( AF_INET, SOCK_DGRAM )
SERVER_IP_1   = '192.168.192.10'
SERVER_IP_2   = '192.168.192.33'
OWN_IP   = '192.168.192.32'
SERVER_PORT = 5000

cam = usb_cam()

Tuer = 14

GPIO.setup(Tuer, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def main():
    tuer = tuer_switch()
    tuer.monitor()
    
def server_send(dicti):
    try:
        server.sendto(str(dicti),(SERVER_IP_1,SERVER_PORT)) 
    except:
        pass
    try:
        server.sendto(str(dicti),(SERVER_IP_2,SERVER_PORT))
    except:
        pass    
    
class tuer_switch:

    def __init__(self):
        self.data = []
        self.alt = 0

    def monitor(self):
        counter = 0
        offen = GPIO.input(Tuer)
        dicti = {}
        dicti['value'] = offen
        dicti['name'] = 'Haustuer_static'            
        server_send(dicti)
        while True:
            offen = GPIO.input(Tuer)
            try:
                if offen == 1 and self.alt == 0:
                    t = threading.Thread(target=cam.take_p, args = [])
                    t.start()
                    dicti = {}
                    dicti['Rot'] = "Aus"
                    dicti['Gelb'] = "An"
                    dicti['Gruen'] = "Aus"  
                    dicti['erinnern'] = True
                    server.sendto(str(dicti),(OWN_IP,SERVER_PORT))
                    dicti = {}
                    dicti['value'] = 1
                    dicti['name'] = 'Haustuer'            
                    server_send(dicti)
                if offen == 0 and self.alt == 1:
                    dicti = {}
                    dicti['Rot'] = "Aus"
                    dicti['Gelb'] = "Aus"
                    dicti['Gruen'] = "Aus"  
                    dicti['erinnern'] = True
                    server.sendto(str(dicti),(OWN_IP,SERVER_PORT)) 
                    dicti = {}
                    dicti['value'] = 0
                    dicti['name'] = 'Haustuer'            
                    server_send(dicti)
                if counter >= 1800:
                    counter = 0
                    dicti = {}
                    dicti['value'] = offen
                    dicti['name'] = 'Haustuer_static'            
                    server_send(dicti)
            except:
                pass
            self.alt = offen
            counter += 1
            time.sleep(0.1)
            
if  __name__ =='__main__':main()                
