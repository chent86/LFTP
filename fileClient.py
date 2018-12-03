# -*- coding: UTF-8 -*-
from socket import *
import struct
import time
import threading
import json
import os

buffer = 1024
hostName = '119.29.204.118'
# hostName = '127.0.0.1'
ip_port = (hostName, 8888)

sk = socket(AF_INET, SOCK_DGRAM)
file_cache_len = 0

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

def clean():
    global send_base, nextseqnum, cwnd, ssthresh, is_connect, file_cache, ACK_status
    send_base = 0
    nextseqnum = 0
    cwnd = 1
    ssthresh = 1000
    is_connect = True
    ACK_status = []
    file_cache = []

def get():
    global send_base, nextseqnum, cwnd, is_connect, file_cache, file_cache_len
    t = True
    start_time = time.time()
    while t and is_connect:
        process(send_base, file_cache_len, start_time)
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
                process(send_base, file_cache_len, start_time)
                if send_base == len(file_cache):
                    t = False
                    break
        lock.release()

def send(ip_port):
    global send_base, nextseqnum
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
        timer(send_base, ip_port)

def timer(old_base, ip_port):
    global send_base, cwnd, ssthresh, is_connect
    if is_connect:
        # time.sleep(0.001) 
        time.sleep(0.0001)
        lock.acquire()
        if old_base == send_base and send_base != len(file_cache):
            message = struct.pack("i1024si", send_base, file_cache[send_base], len(file_cache[send_base]))
            try:
                sk.sendto(message, ip_port)
                # print('resend '+str(send_base))
                ssthresh = cwnd/2
                cwnd = 1
            except Exception:
                print("socket disconnect")
                lock.release()
                is_connect = False 
                return
        lock.release()

def load_file(file_path):
    global file_cache
    global file_cache_len
    global ACK_status
    filesize = os.path.getsize(file_path)
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
    file_cache_len = len(file_cache)

shake_finish = False
def shake_hand(filename):
    global ip_port, file_cache_len, shake_finish
    service_type = 0 # 上传文件
    message = struct.pack("iii100s", service_type, file_cache_len, len(filename), filename.encode('utf-8'))
    sk.sendto(message, ip_port)

    # print('send syn')
    shake_finish = False
    helper = threading.Thread(target = shake_helper, args=(filename,))
    helper.start()
    print('start to recv')
    new_port = sk.recv(1024)
    new_port = int(new_port)
    print('new port is '+str(new_port))
    shake_finish = True
    print('recv OK')
    threads = [threading.Thread(target = get), threading.Thread(target = send, args=((hostName,new_port),))]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    print('OK')
    clean()  # 清空数据，避免对下次调用造成影响

def shake_helper(filename):
    global shake_finish
    while True:
        time.sleep(1)
        if shake_finish == True:
            break
        service_type = 0
        message = struct.pack("iii100s", service_type, file_cache_len, len(filename), filename.encode('utf-8'))
        sk.sendto(message, ip_port)
        # print('resend syn')

# 输出当前进度
def process(send_base, file_cache_len, start_time):
    percent = send_base*100/file_cache_len
    if send_base != file_cache_len:
        print('complete percent:%10.8s%s   spent time:%s%s'%(str(percent),'%', str(int(time.time()-start_time)),'s'),end='\r')
    else:
        print('complete percent:%10.8s%s   spent time:%s%s'%(str(percent),'%', str(int(time.time()-start_time)),'s'))

def service(dirpath, filename):
    path = os.path.join(dirpath, filename)
    print("Loading "+filename+" ...")
    load_file(path)
    print('OK')
    print("Sending "+filename+" ...")
    shake_hand(filename)
