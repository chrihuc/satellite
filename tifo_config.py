# -*- coding: utf-8 -*-
"""
Created on Sat Apr  2 08:11:53 2016

@author: christoph
"""

inputs = {'63mHZj.m4d':'V01ZIM1RUM1HE01'}
outputs = {'Vm1.....':'IO16o','V00...':'LEDs'}

IO16 = {'63mHZj.vYN':(0b10000001,0b00000000,0b00000000,0b00000000,0b00000000,0b00000000,500,0b10000000,0b00000000), #(inputa,inputb,outputa,outputb,monoflopa,monoflopb,floptime[ms],normally open a, b)
        '63mHZj.xxx':(0b00000000,0b00000000,0b00000000,0b00000000,0b00000000,0b00000000,500,0b00000000,0b00000000)}
IO16i = {'63mHZj.vYN':{'a0b1':'V00WOH1SRA1DI01','a0b10000000':'V00WOH1SRA1DI02'}}
IO16o = {'Vm1.......':{'Value':({'UID':'UID1','Pin':1<<13,'Value':0})}}

LEDs = {'V00...':{'UID':'UID','Start':0,'Ende':90}}