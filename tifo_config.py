# -*- coding: utf-8 -*-
"""
Created on Sat Apr  2 08:11:53 2016

@author: christoph
"""

inputs = {'63mHZj.m4d':'V01ZIM1RUM1HE01'}
outputs = {'V01ZIM1RUM1DO01':'IO16o','V01ZIM1RUM1DO02':'IO16o','V01ZIM1RUM1DO03':'IO16o','V00...':'LEDs'}

IO16 = {'63mHZj.vYN':(0b10000001,0b00000000,0b00000000,0b00000111,0b00000000,0b00001000,500,0b10000001,0b00000000), #(inputa,inputb,outputa,outputb,monoflopa,monoflopb,floptime[ms],normally open a, b)
        '63mHZj.xxx':(0b00000000,0b00000000,0b00000000,0b00000000,0b00000000,0b00000000,500,0b00000000,0b00000000)}
IO16i = {'63mHZj.vYN':{'a0b1':'V00WOH1SRA1DI01','a0b10000000':'V00WOH1SRA1DI02'}}
IO16o = {'V01ZIM1RUM1DO01':({'Value':0,'Commands':({'UID':'63mHZj.vYN','Pin':0b00000001,'Port':'B','Value':0},{'UID':'63mHZj.vYN','Pin':0b00000010,'Port':'B','Value':1})},
                            {'Value':1,'Commands':({'UID':'63mHZj.vYN','Pin':0b00000001,'Port':'B','Value':1},{'UID':'63mHZj.vYN','Pin':0b00000010,'Port':'B','Value':0})}),
         'V01ZIM1RUM1DO02':({'Value':0,'Commands':({'UID':'63mHZj.vYN','Pin':0b00000100,'Port':'B','Value':0})},
                            {'Value':1,'Commands':({'UID':'63mHZj.vYN','Pin':0b00000100,'Port':'B','Value':1})}),
         'V01ZIM1RUM1DO03':({'Value':0,'Commands':({'UID':'63mHZj.vYN','Pin':0b00001000,'Port':'B','Value':0})},
                            {'Value':1,'Commands':({'UID':'63mHZj.vYN','Pin':0b00001000,'Port':'B','Value':1})})                             
         }

LEDs = {'63mHZj.xxx':(2812,50)}
LEDsOut = {'V00...':{'UID':'UID','Start':0,'Ende':90}}