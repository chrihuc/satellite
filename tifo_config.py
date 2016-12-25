# -*- coding: utf-8 -*-
"""
Created on Sat Apr  2 08:11:53 2016

@author: christoph
"""
#TV 6De9SU
#Sideboard 62efV1
#spare 63mHZj

# translation from homecontrol addresses to tifo addresses
inputs = {'6De9SU':'TV','62efV1':'Sideboard','63mHZj':'spare',
          '6De9SU.m4d':'V00WOH1RUM1HE01','6De9SU.xsR':'V00WOH1RUM1CO01',
          '6De9SU.sFC':'V00WOH1RUM1MD01',
          '63mHZj.voh':'V00WOH1RUM1SI01','63mHZj.woZ':'V00WOH1RUM1TE11'}
outputs = {'V01ZIM1RUM1DO01':'IO16o','V01ZIM1RUM1DO02':'IO16o','V01ZIM1RUM1DO03':'IO16o',
           'V00WOH1SRA1LI01':'LEDs','V00WOH1SRA1LI02':'LEDs','V00WOH1SRA1LI03':'LEDs','V00WOH1SRA1LI04':'LEDs',
           'V00WOH1SRA1LI11':'DualRelay'}

# generel setup of IO16           
# tifoadress:(inputa,inputb,outputa,outputb,monoflopa,monoflopb,floptime[ms],normally open a, b)
IO16 = {'62efV1.gox':(0b00111111,0b00000000,0b00000000,0b00000000,0b00000000,0b00000000,500,0b00000000,0b00000000), 
        '63mHZj.vYN':(0b00000000,0b00000000,0b00000000,0b00001111,0b00000000,0b00000011,500,0b00000000,0b00000000)}
# assingment of homecontrol addresses to tifo addreses        
IO16i = {'62efV1.gox':{'a0b1':'V00WOH1SRA1DI01','a0b10':'V00WOH1SRA1DI02','a0b100':'V00WOH1SRA1DI03',
                       'a0b1000':'V00WOH1SRA1DI04','a0b10000':'V00WOH1SRA1DI05','a0b100000':'V00WOH1SRA1DI06'}}
IO16o = {'V01ZIM1RUM1DO01':({'Value':0,'Commands':({'UID':'63mHZj.vYN','Pin':0b00000001,'Port':'B','Value':1},
                                                   {'UID':'63mHZj.vYN','Pin':0b00000010,'Port':'B','Value':0})},
                            {'Value':1,'Commands':({'UID':'63mHZj.vYN','Pin':0b00000001,'Port':'B','Value':0},
                                                   {'UID':'63mHZj.vYN','Pin':0b00000010,'Port':'B','Value':1})}),
         'V01ZIM1RUM1DO02':({'Value':0,'Commands':({'UID':'63mHZj.vYN','Pin':0b00000100,'Port':'B','Value':0})},
                            {'Value':1,'Commands':({'UID':'63mHZj.vYN','Pin':0b00000100,'Port':'B','Value':1})}),
         'V01ZIM1RUM1DO03':({'Value':0,'Commands':({'UID':'63mHZj.vYN','Pin':0b00001000,'Port':'B','Value':0})},
                            {'Value':1,'Commands':({'UID':'63mHZj.vYN','Pin':0b00001000,'Port':'B','Value':1})})                             
         }

LEDs = {'62efV1.oUX':(2812,50)}
LEDsOut = {'V00WOH1SRA1LI01':{'UID':'62efV1.oUX','Start':0,'Ende':15},
           'V00WOH1SRA1LI02':{'UID':'62efV1.oUX','Start':15,'Ende':30},
           'V00WOH1SRA1LI03':{'UID':'62efV1.oUX','Start':30,'Ende':45},
           'V00WOH1SRA1LI04':{'UID':'62efV1.oUX','Start':0,'Ende':45}}
           
DualRelay = {'V00WOH1SRA1LI11':({'Value':0,'UID':'62efV1.wBh','relay':1,'state':False},
                                {'Value':1,'UID':'62efV1.wBh','relay':1,'state':True})}          


SoundInt = {'63mHZj.voh':[1000,'>',200,0]}#debounce, option, min, max