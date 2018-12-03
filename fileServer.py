# -*- coding: UTF-8 -*-
import json
import os
from socket import *
import struct
import time
import threading

sk = socket(AF_INET, SOCK_DGRAM)
sk.bind(('',8888))
sk.settimeout(5)

buffer = 1024
recv_base = 0
file_cache_len = 42950
file_cache = [0]*file_cache_len
ACK_status = [0]*file_cache_len
rwnd = 500
seq_max = 100 # 未用到
lock = threading.Lock()


def get():
    global recv_base
    while True:
        if recv_base == file_cache_len:
            break 
        try:
            message, ip_port = sk.recvfrom(buffer+30)
        except Exception:
            print("socket disconnect")
            break
        seq, content, size = struct.unpack("i1024si", message)
        if seq >= recv_base and seq < recv_base+rwnd:
            ACK_status[seq] = 1
            sk.sendto(str(seq).encode('utf-8'), ip_port)
            while ACK_status[recv_base] == 1:
                recv_base = recv_base+1
                if recv_base==file_cache_len:
                    break
        elif seq >= recv_base-rwnd and seq < recv_base:
            sk.sendto(str(seq).encode('utf-8'), ip_port)
        else:
            continue
        if seq == file_cache_len-1:
            file_cache[seq] = content[:size]
        else:
            file_cache[seq] = content

def process():
    global recv_base
    while recv_base==0:
        start_time = time.time()
    while True:
        last_base = recv_base
        time.sleep(0.01)
        percent = recv_base*100/file_cache_len
        if recv_base != file_cache_len:
            print('complete percent:%10.8s%s   spent time:%s%s'%(str(percent),'%', str(int(time.time()-start_time)),'s'),end='\r')
        else:
            print('complete percent:%10.8s%s   spent time:%s%s'%(str(percent),'%', str(int(time.time()-start_time)),'s'))
            break

print("Receiving file ...")
threads = [threading.Thread(target = process), threading.Thread(target = get)]
for t in threads:
    t.start()
for t in threads:
    t.join()
get()

with open('server.pdf', 'wb') as f:
    for content in file_cache:
        f.write(content)
sk.close()
print('OK')

