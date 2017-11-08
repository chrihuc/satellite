# -*- coding: utf-8 -*-
"""
Created on Wed Mar 30 15:35:24 2016

@author: chuckle
"""

import socket
import constants
from socket import AF_INET, SOCK_DGRAM

server = socket.socket( AF_INET, SOCK_DGRAM )

def bidirekt(request):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    data_ev = {'Request':request}
    s.connect((constants.server1,constants.biPort))
    s.send(str(data_ev))
    reply = s.recv(1024)
    print reply
    s.close() 
    isddict, dicti = check_dict(reply)
    if isddict:
        return dicti
    else:
        return None
        
def send_to_server(devce, value):
    dicti = {'Name': str(devce), 'Value': value}
    server.sendto(str(dicti) ,(constants.server1,constants.broadPort))  
       
def check_dict(incoming):
    try:
        eval_in = eval(incoming)
        if isinstance(eval_in, dict):
            return True, eval_in
        elif isinstance(eval_in, basestring):
            return False, incoming
        else:
            return False, eval_in
    except Exception as serr:
        return False, incoming

if __name__ == '__main__':
    antwort = bidirekt('Bewohner')
    print antwort
    