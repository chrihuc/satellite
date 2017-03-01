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
import constants
import zw_config

device="/dev/ttyACM0"
log="None"

from socket import socket, AF_INET, SOCK_DGRAM

mySocket = socket( AF_INET, SOCK_DGRAM )

class zwave(object):

    #Define some manager options
    options = ZWaveOption(device, \
      config_path=constants.zwpath, \
      user_path=".", cmd_line="")
    options.set_log_file("OZW_Log.log")
    options.set_append_log_file(False)
    options.set_console_output(False)
    options.set_save_log_level(log)
    options.set_logging(True)
    options.lock()
    
    def louie_network_started(self, network):
        pass
        print("Hello from network : I'm started : homeid {:08x} - {} nodes were found.".format(network.home_id, network.nodes_count))
    
    def louie_network_failed(self, network):
        pass
        print("Hello from network : can't load :(.")
    
    def louie_network_ready(self, network):
#        print("Hello from network : I'm ready : {} nodes were found.".format(network.nodes_count))
#        print("Hello from network : my controller is : {}".format(network.controller))
        dispatcher.connect(self.louie_node_update, ZWaveNetwork.SIGNAL_NODE)
        dispatcher.connect(self.louie_value_update, ZWaveNetwork.SIGNAL_VALUE)
    
    def louie_node_update(self, network, node):
        pass
        print("Hello from node : {}.".format(node))
    
    def louie_value_update(self, network, node, value):
        # TODO: catch exception
        try:
            print zw_config.inputs[node.home_id][value.value_id], int(value.data)
            dicti = {'Value':str(int(value.data))}
            dicti['Name'] = zw_config.inputs[node.home_id][value.value_id]
            #print dicti
            mySocket.sendto(str(dicti) ,(constants.server1,constants.broadPort))            
        except:
            print 'not understood', node.home_id, value.value_id, value.data
#        print("Hello from value : {}.".format( value ))
    #    home_id: [0xeefad666] id: [72057594093060096] parent_id: [3] label: [Switch] data: [False].
    #    home_id: [0xeefad666] id: [72057594093273218] parent_id: [3] label: [Power] data: [0.0].
    #    home_id: [0xeefad666] id: [144115188131201026] parent_id: [3] label: [Energy] data: [0.00999999977648]
    #   value.label = switch

    def __init__(self):
        #Create a network object
        self.network = ZWaveNetwork(self.options, autostart=False)
        
        
        #We connect to the louie dispatcher
        dispatcher.connect(self.louie_network_started, ZWaveNetwork.SIGNAL_NETWORK_STARTED)
        dispatcher.connect(self.louie_network_failed, ZWaveNetwork.SIGNAL_NETWORK_FAILED)
        dispatcher.connect(self.louie_network_ready, ZWaveNetwork.SIGNAL_NETWORK_READY)
        
        self.network.start()

        #We wait for the network.
        # print("Waiting for network to become ready : ")
        for i in range(0,90):
            if self.network.state>=self.network.STATE_READY:
                print "Network is ready"
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
            
            
#            for node in self.network.nodes:
#                for val in self.network.nodes[node].get_switches() :
#                    print("Switch : {}".format(self.network.nodes[node]))
#                    print("Switch1: {}".format(val))
            #        72057594093060096
            #       144115188130988032
            #        network.nodes[node].set_switch(val,True)
                #We only activate the first switch
                #exit
            
            
#            for node in self.network.nodes:
#                for val in self.network.nodes[node].get_dimmers() :
#                   print("Dimmer : {}".format(self.network.nodes[node]))
#                   print("Switch1: {}".format(val))
            #        72057594093076481
            #        144115188131004513
            #        144115188131004417
            #        72057594093076577 
            #        network.nodes[node].set_dimmer(val,80)
                #We only activate the first dimmer
                #exit

    def end_network(self):
        self.network.stop()

    def _set_switch(self,node_id , switch, wert):
        if wert == 'Toggle':
            cur_val = self.network.nodes[node_id].get_switch_state(switch)
            self.network.nodes[node_id].set_switch(switch, not cur_val)
        else:
            if eval(wert) > 0:
                self.network.nodes[node_id].set_switch(switch, True)
            else:
                self.network.nodes[node_id].set_switch(switch, bool(eval(wert)))
        return True
        
    def _set_dimmer(self,node_id , dimmer, wert):
        if wert == 'Toggle':
            cur_val = self.network.nodes[node_id].get_dimmer_level(dimmer)
            if cur_val == 0:
                self.network.nodes[node_id].set_dimmer(dimmer, 50)
            else:
                self.network.nodes[node_id].set_dimmer(dimmer, 0)
        else:
            self.network.nodes[node_id].set_dimmer(dimmer, eval(wert))
        return True       
        
    def set_device(self, data_ev): 
#       TODO do threaded with stop criteria
        if data_ev.get('Device') in zw_config.switches:
            print data_ev
            return self._set_switch(zw_config.switches[data_ev['Device']][0],zw_config.switches[data_ev['Device']][1],data_ev['Value'])
        if data_ev.get('Device') in zw_config.dimmer:
            print data_ev
            return self._set_dimmer(zw_config.dimmer[data_ev['Device']][0],zw_config.dimmer[data_ev['Device']][1],data_ev['Value'])

if __name__ == "__main__":
    zwnw = zwave()
    zwnw.set_device()
    raw_input('Press key to exit\n') 
    zwnw.end_network()
