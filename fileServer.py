# -*- coding: UTF-8 -*-
import json
import os
from socket import *
import struct

sk = socket(AF_INET, SOCK_DGRAM)
sk.bind(('',12345))

buffer = 2048
recv_base = 0
file_cache_len = 21475
file_cache = [0]*file_cache_len
ACK_status = [0]*file_cache_len
rwnd = 500
seq_max = 100 # 未用到

def get():
    global recv_base
    while recv_base != file_cache_len:
        message, ip_port = sk.recvfrom(buffer+20)
        if recv_base == file_cache_len-1:
            seq, content, size = struct.unpack("i2039si", message)
        else:
            seq, content, size = struct.unpack("i2048si", message)
        file_cache[seq] = content
        if seq >= recv_base and seq < recv_base+rwnd:
            ACK_status[seq] = 1
            sk.sendto(str(seq), ip_port)
            while ACK_status[recv_base] == 1:
                recv_base = recv_base+1
                if recv_base==file_cache_len:
                    break
        elif seq >= recv_base-rwnd and seq < recv_base:
            sk.sendto(str(seq), ip_port)

print("Receiving file ...")
get()

with open('server.pdf', 'wb') as f:
    for content in file_cache:
        f.write(content)

print("OK")
sk.close()
