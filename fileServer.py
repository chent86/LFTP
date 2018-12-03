# -*- coding: UTF-8 -*-
import json
import os
from socket import *
import struct
import time
import threading
import copy

# 子线程
def get(ip_port, file_cache_len, filename, sk):
    # sk = socket(AF_INET, SOCK_DGRAM)
    # sk.settimeout(10)

    # get_in = False
    # while True:
    #     for port in range(8889, 8899):
    #         try:
    #             sk.bind(('',port))
    #             get_in = True
    #             break
    #         except:
    #             print("address "+str(port)+" already used") 
    #     if get_in:
    #         break
    #     time.sleep(3)
    print(str(ip_port)+' get in')
    buffer = 1024
    recv_base = 0
    file_cache = [0]*file_cache_len
    ACK_status = [0]*file_cache_len
    rwnd = 500
    message = 'ok'
    sk.sendto(message.encode('utf-8'), ip_port)
    print(str(ip_port)+' send OK')
    print("Receiving file from "+str(ip_port))
    while True:
        if recv_base == file_cache_len:
            save_file(file_cache, filename)
            break 
        try:
            message, ip_port = sk.recvfrom(buffer+30)
        except Exception:
            print("time out")
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
    sk.close()

# 从主端口获取用户操作信息, 随后分配到子线程进行对接
def shake_hand():
    sk = socket(AF_INET, SOCK_DGRAM)
    sk.bind(('',8888))
    while True:
        message, new_ip_port = sk.recvfrom(200)
        service_type, file_cache_len, filename_size, filename = struct.unpack("iii100s", message)
        if service_type == 0:
            t = threading.Thread(target = get, args=(new_ip_port, file_cache_len, filename[:filename_size], sk))
            t.start()
    sk.close()

# 保存文件
def save_file(file_cache, filename):
    with open(filename, 'wb') as f:
        for content in file_cache:
            f.write(content)
    print('OK')


shake_hand()
