# -*- coding: utf-8 -*-
"""
Created on Wed Mar 30 15:35:24 2016

@author: chuckle
"""

import socket
import struct
import constants
from socket import AF_INET, SOCK_DGRAM

server = socket.socket( AF_INET, SOCK_DGRAM )

def send_msg(sock, msg):
    # Prefix each message with a 4-byte length (network byte order)
    msg = struct.pack('>I', len(msg)) + msg
    sock.sendall(msg)

def recv_msg(sock):
    # Read message length and unpack it into an integer
    raw_msglen = recvall(sock, 4)
    if not raw_msglen:
        return None
    msglen = struct.unpack('>I', raw_msglen)[0]
    # Read the message data
    return recvall(sock, msglen)

def recvall(sock, n):
    # Helper function to recv n bytes or return None if EOF is hit
    data = b''
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            return None
        data += packet
    return data

def bidirekt(request, key=''):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    data_ev = {'Request':request, 'Key':key}
    s.connect((constants.server1,constants.biPort))
    s.send(str(data_ev))
    reply = recv_msg(s)#s.recv(4096)
    print reply
    s.close()
    isddict, dicti = check_dict(reply)
    if isddict:
        return dicti
    else:
        return None

def bidirekt_new(request, key=''):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    data_ev = {'Request':request, 'Key':key}
    s.connect((constants.server1,5050))
    send_msg(s, str(data_ev))
    reply = recv_msg(s)#s.recv(4096)
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
    antwort = bidirekt_new('Inputs')
#    print antwort
#    _, antwort = check_dict(bidirekt('Inputs'))
    print antwort['A00TER1GEN1TE01']
