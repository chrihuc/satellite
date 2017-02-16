#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 26 07:19:15 2017

@author: christoph
"""

# translation from homecontrol addresses to tifo addresses
inputs = {4009416294:{72057594093060096L:'V00KUE1DEK1LI01',144115188130988032L:'V00KUE1DEK1LI02',72057594109853697L:'V00WOH1DEK1LI01'}}

switches = {'V00KUE1DEK1LI01':[3, 72057594093060096L],
            'V00KUE1DEK1LI02':[3, 144115188130988032L]}

dimmer = {'V00WOH1DEK1LI01':[4, 72057594109853697L]}

outputs = switches.keys() + dimmer.keys()
