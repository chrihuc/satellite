#!/usr/bin/python

#c:/python27/python.exe leds.py

from socket import socket, AF_INET, SOCK_DGRAM
import time
import threading
from threading import Timer
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

Rot = 2
Gelb = 3
Gruen = 4

#GPIO.setup(Tuer, GPIO.IN, pull_up_down=GPIO.PUD_UP)
# TODO: a lot change constants...
GPIO.setup(Rot, GPIO.OUT)
GPIO.setup(Gelb, GPIO.OUT)
GPIO.setup(Gruen, GPIO.OUT)

def main():
    inp = LEDs()
    inp.schalte("F1","F2","F3")  
    t = threading.Thread(target=inp.start, args = [0.25])    
    t.start()
#    time.sleep(10)
#    inp.schalte("Aus","An","F2",erinn = True) 
   
'''
    modes for the leds:
        An, Aus, F1, F2, F3, F4,
        Speed defines basic frequency, default 0.25s
        F1 = 2Hz, F2 = 1Hz, F3 = 0.5Hz, F4 = 0.25Hz
'''
    
class LEDs:
    

    def __init__(self):
        self.rot = False
        self.gelb = False
        self.gruen = False
        self.erinnere = False
        self.er_rot = False
        self.er_gelb = False
        self.er_gruen = False        
        self.aus = "Aus"
        self.an = "An"
        self.f2 = "F2"
        self.f1 = "F1" 
        self.f3 = "F3" 
        self.f4 = "F4"
        self.tim = Timer(5, self.schalte, [self.er_rot,self.er_gelb,self.er_gruen])
        t = threading.Thread(target=self.start, args = [0.25])    
        t.start()        
        
    def schalte(self, ro = "Aus", ge = "Aus", gr = "Aus", erinn = False):
        #wenn erinn gesetzt dann springt auf letzte zurueck
        #wenn nicht gesetzt dann bleibt es dauerhaft
        self.tim.cancel()
        if not erinn:
            self.er_rot = ro
            self.er_gelb = ge
            self.er_gruen = gr
        self.rot = ro
        self.gelb = ge
        self.gruen = gr
        self.setze_leds(cycle = self.an, value = True)
        if erinn:
            self.tim = Timer(3, self.schalte, [self.er_rot,self.er_gelb,self.er_gruen])
            self.tim.start()

    def schalte_rot(self, ro = "Aus"):
        self.rot = ro
        self.setze_leds(cycle = self.an, value = True)

    def schalte_gelb(self, ge = "Aus"):
        self.gelb = ge
        self.setze_leds(cycle = self.an, value = True)
        
    def schalte_gruen(self, gr = "Aus"):
        global gruen    
        self.gruen = gr
        self.setze_leds(cycle = self.an, value = True)
       
    def setze_leds(self, cycle, value):
        if value == "False2":
            value = False
        if self.rot == cycle:
            GPIO.output(Rot,value)
        if self.gelb == cycle:
            GPIO.output(Gelb,value)    
        if self.gruen == cycle:
            GPIO.output(Gruen,value)
        if self.rot == self.aus:
            GPIO.output(Rot,False)   
        if self.gelb == self.aus:
            GPIO.output(Gelb,False) 
        if self.gruen == self.aus:
            GPIO.output(Gruen,False)                
        
    def start(self, speed=0.25):
        while True:
            self.setze_leds(cycle = self.an, value = True)
            for l in (True, False, "False2"):
                self.setze_leds(cycle = self.f4, value = l)
                for k in (True, False):
                    self.setze_leds(cycle = self.f3, value = k)                
                    for i in (True, False):
                        self.setze_leds(cycle = self.f2, value = i)
                        for j in (True, False):
                            self.setze_leds(cycle = self.f1, value = j)
                            time.sleep(speed)
                            
    def set_device(self, **kwargs):
        device = kwargs.get('Device')
        rot = kwargs.get('red',self.aus)
        gelb = kwargs.get('yellow',self.aus)
        gruen = kwargs.get('green',self.aus)      
        go_back = kwargs.get('go_back',False) 
        self.schalte(ro = rot, ge = gelb, gr = gruen)
    
            
if  __name__ =='__main__':main()                    