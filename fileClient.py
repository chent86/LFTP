# -*- coding: UTF-8 -*-
from socket import *
import struct
import time
import threading
import json
import os

buffer = 1024
# ip_port = ('119.29.204.118', 8888)
ip_port = ('127.0.0.1', 8888)

sk = socket(AF_INET, SOCK_DGRAM)
sk.connect(ip_port)
filepath = '..'
filename = '1.pdf'
file_path = os.path.join(filepath, filename)
filesize = os.path.getsize(file_path)


send_base = 0
nextseqnum = 0
rwnd = 500
seq_max = 100 # 未用到
ACK_status = []
file_cache = []
lock = threading.Lock()

def get():
    global send_base
    global nextseqnum
    t = True
    while t:
        lock.acquire()
        if send_base == len(file_cache):
            break
        lock.release()
        try:
            ACK_seq = sk.recv(30)
        except Exception:
            print("socket disconnect")
            break
        ACK_seq = int(ACK_seq)

        lock.acquire()
        if ACK_seq >= send_base and ACK_seq < nextseqnum:
            ACK_status[ACK_seq] = 1
            while ACK_status[send_base] == 1:
                send_base = send_base+1
                if send_base == len(file_cache):
                    t = False
                    break
        lock.release()

def send():
    global send_base
    global nextseqnum
    while True:
        lock.acquire()
        if send_base == len(file_cache):
            break
        if nextseqnum-send_base < rwnd and nextseqnum < len(file_cache):
            message = struct.pack("i1024si", nextseqnum, file_cache[nextseqnum], len(file_cache[nextseqnum]))
            sk.sendto(message, ip_port)
            nextseqnum = nextseqnum+1   
        lock.release()
        if timer(send_base)==False:
            break

def timer(old_base):
    time.sleep(0.0009)
    # time.sleep(0.0001)
    lock.acquire()
    if old_base == send_base and send_base != len(file_cache):
        message = struct.pack("i1024si", send_base, file_cache[send_base], len(file_cache[send_base]))
        try:
            sk.sendto(message, ip_port)
        except Exception:
            print("socket disconnect")
            lock.release()
            return False 
    lock.release()
    return True

print("Loading "+filename+" ...")
with open(file_path, 'rb') as f:
    while filesize:
        if filesize >= buffer:
            content = f.read(buffer)
            file_cache.append(content)
            ACK_status.append(0)
            filesize -= buffer
        else:
            content = f.read(filesize)
            file_cache.append(content)
            ACK_status.append(0)
            break
print('OK')

print("Sending "+filename+" ...")

threads = [threading.Thread(target = get), threading.Thread(target = send)]
for t in threads:
    t.start()
for t in threads:
    t.join()

print('OK')
