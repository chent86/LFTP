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
cwnd = 1
ssthresh = 1000
seq_max = 100 # 未用到
ACK_status = []
file_cache = []
lock = threading.Lock()

is_connect = True
EstimatedRTT = 0.009
DevRTT = 0

def get():
    global send_base
    global nextseqnum
    global cwnd
    global is_connect
    t = True
    while t and is_connect:
        lock.acquire()
        if send_base == len(file_cache):
            lock.release()
            break
        lock.release()
        try:
            ACK_seq = sk.recv(30)
        except Exception:
            print("socket disconnect")
            is_connect = False
            lock.release()
            break
        ACK_seq = int(ACK_seq)

        lock.acquire()
        if ACK_seq >= send_base and ACK_seq < nextseqnum:
            if ACK_status[ACK_seq] == 0:
                if cwnd < ssthresh:
                    cwnd = cwnd+1
                else:
                    cwnd = cwnd+1/cwnd
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
    while is_connect:
        lock.acquire()
        if send_base == len(file_cache):
            lock.release()
            break
        # 加上and nextseqnum-send_base < cwnd条件增加拥塞控制
        if nextseqnum-send_base < rwnd and nextseqnum < len(file_cache):
            message = struct.pack("i1024si", nextseqnum, file_cache[nextseqnum], len(file_cache[nextseqnum]))
            sk.sendto(message, ip_port)
            nextseqnum = nextseqnum+1   
        lock.release()
        timer(send_base)

def timer(old_base):
    global send_base
    global cwnd
    global ssthresh
    global is_connect
    if is_connect:
        # time.sleep(0.001) 
        time.sleep(0.0001)
        lock.acquire()
        if old_base == send_base and send_base != len(file_cache):
            message = struct.pack("i1024si", send_base, file_cache[send_base], len(file_cache[send_base]))
            try:
                sk.sendto(message, ip_port)
                print('resend '+str(send_base))
                ssthresh = cwnd/2
                cwnd = 1
            except Exception:
                print("socket disconnect")
                lock.release()
                is_connect = False 
                return
        lock.release()

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
