#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 26 07:19:15 2017

@author: christoph
"""

# translation from homecontrol addresses to tifo addresses
inputs = {'72057594093060096':'V00KUE1DEK1LI01','144115188130988032':'V00KUE1DEK1LI02'}

switches = {'V00KUE1DEK1LI01':['node','72057594093060096'],
            'V00KUE1DEK1LI02':['node','144115188130988032']}

outputs = switches.keys()