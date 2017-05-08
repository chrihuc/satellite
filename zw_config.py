#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 26 07:19:15 2017

@author: christoph
"""

# translation from homecontrol addresses to tifo addresses
# if not configured as input no manual interaction will be registered
inputs = {4009416294:{72057594093060096L:'V00KUE1DEK1LI01',144115188130988032L:'V00KUE1DEK1LI02',
                      72057594109853697L:'V00WOH1DEK1LI01',72057594176962561L:'V01FLU1DEK1LI01',
                      72057594193723392L:'Vm1ZIM1DEK1LI01'}}

switches = {'V00KUE1DEK1LI01':[3, 72057594093060096L],
            'V00KUE1DEK1LI02':[3, 144115188130988032L],
            'Vm1FLU1DEK1LI01':[5, 72057594126614528L],
            'V00FLU1DEK1LI01':[6, 72057594143391744L],
            'Vm1ZIM1DEK1LI01':[9, 72057594193723392L]}

dimmer = {'V00ESS1DEK1LI01':[4, 72057594109853697L],
          'V01FLU1DEK1LI01':[8, 72057594176962561L]}

outputs = switches.keys() + dimmer.keys()
