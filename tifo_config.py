# -*- coding: utf-8 -*-
"""
Created on Sat Apr  2 08:11:53 2016

@author: christoph
"""

inputs = {'62efV1.m4d':'V00WOH1RUM1HE01'}
outputs = {'V01ZIM1RUM1DO01':'IO16o','V01ZIM1RUM1DO02':'IO16o','V01ZIM1RUM1DO03':'IO16o',
           'V00WOH1SRA1LI01':'LEDs','V00WOH1SRA1LI02':'LEDs','V00WOH1SRA1LI03':'LEDs'}

IO16 = {'62efV1.gox':(0b00111111,0b00000000,0b00000000,0b00000000,0b00000000,0b00000000,500,0b00000000,0b00000000), #(inputa,inputb,outputa,outputb,monoflopa,monoflopb,floptime[ms],normally open a, b)
        '63mHZj.vYN':(0b00000000,0b00000000,0b00000000,0b00001100,0b00000000,0b00000011,500,0b00000000,0b00000000)}
IO16i = {'62efV1.gox':{'a0b1':'V00WOH1SRA1DI01','a0b10':'V00WOH1SRA1DI02','a0b100':'V00WOH1SRA1DI03','a0b1000':'V00WOH1SRA1DI04','a0b10000':'V00WOH1SRA1DI05','a0b100000':'V00WOH1SRA1DI06'}}
IO16o = {'V01ZIM1RUM1DO01':({'Value':0,'Commands':({'UID':'63mHZj.vYN','Pin':0b00000001,'Port':'B','Value':0},{'UID':'63mHZj.vYN','Pin':0b00000010,'Port':'B','Value':1})},
                            {'Value':1,'Commands':({'UID':'63mHZj.vYN','Pin':0b00000001,'Port':'B','Value':1},{'UID':'63mHZj.vYN','Pin':0b00000010,'Port':'B','Value':0})}),
         'V01ZIM1RUM1DO02':({'Value':0,'Commands':({'UID':'63mHZj.vYN','Pin':0b00000100,'Port':'B','Value':0})},
                            {'Value':1,'Commands':({'UID':'63mHZj.vYN','Pin':0b00000100,'Port':'B','Value':1})}),
         'V01ZIM1RUM1DO03':({'Value':0,'Commands':({'UID':'63mHZj.vYN','Pin':0b00001000,'Port':'B','Value':0})},
                            {'Value':1,'Commands':({'UID':'63mHZj.vYN','Pin':0b00001000,'Port':'B','Value':1})})                             
         }

LEDs = {'62efV1.oUX':(2812,50)}
LEDsOut = {'V00WOH1SRA1LI01':{'UID':'62efV1.oUX','Start':0,'Ende':15},
           'V00WOH1SRA1LI02':{'UID':'62efV1.oUX','Start':15,'Ende':30},
           'V00WOH1SRA1LI03':{'UID':'62efV1.oUX','Start':30,'Ende':45}}