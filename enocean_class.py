#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Nov  8 14:32:21 2017

@author: christoph
"""

from enocean.communicators.serialcommunicator import SerialCommunicator
from enocean.protocol.packet import RadioPacket
from enocean.protocol.constants import PACKET, RORG
import sys
import traceback
import constants

import mqtt_publish

#sudo pip install git+https://github.com/chrihuc/enocean.git

try:
    import queue
except ImportError:
    import Queue as queue


class Encocean_Sat(object):
    
    def __init__(self):
        self.communicator = SerialCommunicator(port='/dev/ttyUSB0')
        self.communicator.start()
     
    def assemble_radio_packet(transmitter_id):
        return RadioPacket.create(rorg=RORG.BS4, rorg_func=0x20, rorg_type=0x01,
                                  sender=transmitter_id,
                                  CV=50,
                                  TMP=21.5,
                                  ES='true')
    
    def monitor(self):
        while self.communicator.is_alive():
            try:
                # Loop to empty the queue...
                packet = self.communicator.receive.get(block=True, timeout=1)
                            
                if packet.packet_type == PACKET.RADIO and packet.rorg == RORG.BS4:
                    # parse packet with given FUNC and TYPE
                    for k in packet.parse_eep(0x02, 0x05):
                        print('A %s: %s' % (k, packet.parsed[k]))
                if packet.packet_type == PACKET.RADIO and packet.rorg == RORG.BS1:
                    # alternatively you can select FUNC and TYPE explicitely
                    packet.select_eep(0x00, 0x01)
                    # parse it
                    packet.parse_eep()
                    for k in packet.parsed:
                        print('B %s: %s' % (k, packet.parsed[k]))
                if packet.packet_type == PACKET.RADIO and packet.rorg == RORG.RPS:
                    received = packet.parse_eep(0x02, 0x02)
                    print(packet.sender_hex, packet.parsed['EB']['raw_value'])
#                    udp_send.send_to_server('Enocean.' + packet.sender_hex, packet.parsed['EB']['raw_value'])
                    dicti = {'Name': 'Enocean.'+str(packet.sender_hex), 'Value': str(packet.parsed['EB']['raw_value'])}
                    mqtt_publish.mqtt_pub('Inputs/Satellite/' + constants.name + '/Enocean/'+str(packet.sender_hex),dicti)
            except queue.Empty:
                continue
            except KeyboardInterrupt:
                break
            except Exception:
                traceback.print_exc(file=sys.stdout)
                break
        if self.communicator.is_alive():
            self.communicator.stop()
