#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sat Jan 14 08:12:25 2017

@author: christoph
"""
import sys
import time
import openzwave
from openzwave.option import ZWaveOption
from openzwave.network import ZWaveNetwork
from louie import dispatcher

device="/dev/ttyACM0"
log="None"
sniff=300.0

#Define some manager options
options = ZWaveOption(device, \
  config_path="/home/christoph/spyder/python-openzwave/openzwave/config", \
  user_path=".", cmd_line="")
options.set_log_file("OZW_Log.log")
options.set_append_log_file(False)
options.set_console_output(False)
options.set_save_log_level(log)
options.set_logging(True)
options.lock()

def louie_network_started(network):
    print("Hello from network : I'm started : homeid {:08x} - {} nodes were found.".format(network.home_id, network.nodes_count))

def louie_network_failed(network):
    print("Hello from network : can't load :(.")

def louie_network_ready(network):
    print("Hello from network : I'm ready : {} nodes were found.".format(network.nodes_count))
    print("Hello from network : my controller is : {}".format(network.controller))
    dispatcher.connect(louie_node_update, ZWaveNetwork.SIGNAL_NODE)
    dispatcher.connect(louie_value_update, ZWaveNetwork.SIGNAL_VALUE)

def louie_node_update(network, node):
    print("Hello from node : {}.".format(node))

def louie_value_update(network, node, value):
    print("Hello from value : {}.".format( value ))

#Create a network object
network = ZWaveNetwork(options, autostart=False)


#We connect to the louie dispatcher
dispatcher.connect(louie_network_started, ZWaveNetwork.SIGNAL_NETWORK_STARTED)
dispatcher.connect(louie_network_failed, ZWaveNetwork.SIGNAL_NETWORK_FAILED)
dispatcher.connect(louie_network_ready, ZWaveNetwork.SIGNAL_NETWORK_READY)

network.start()

#We wait for the network.
print("***** Waiting for network to become ready : ")
for i in range(0,90):
    if network.state>=network.STATE_READY:
        print("***** Network is ready")
        break
    else:
        sys.stdout.write(".")
        sys.stdout.flush()
        time.sleep(1.0)

#time.sleep(5.0)

#We update the name of the controller
#print("Update controller name")
#network.controller.node.name = "Hello name"

#time.sleep(5.0)

#We update the location of the controller
#print("Update controller location")
#network.controller.node.location = "Hello location"


for node in network.nodes:
    for val in network.nodes[node].get_switches() :
        print("Switch : {}".format(network.nodes[node]))
        print("Switch1: {}".format(val))
#        72057594093060096
#       144115188130988032
#        network.nodes[node].set_switch(val,True)
    #We only activate the first switch
    #exit


for node in network.nodes:
    for val in network.nodes[node].get_dimmers() :
       print("Dimmer : {}".format(network.nodes[node]))
       print("Switch1: {}".format(val))
#        72057594093076481
#        144115188131004513
#        144115188131004417
#        72057594093076577
#        network.nodes[node].set_dimmer(val,80)
    #We only activate the first dimmer
    #exit

raw_input('Press key to exit\n') 

network.stop()