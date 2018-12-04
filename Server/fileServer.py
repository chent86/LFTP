# -*- coding: UTF-8 -*-
import json
import os
from socket import *
import struct
import time
import threading
import multiprocessing
import copy
import Recv
import Send

buffer = 1024

# 从主端口获取用户操作信息, 随后分配到子线程进行对接
def shake_hand():
    sk = socket(AF_INET, SOCK_DGRAM)
    sk.bind(('',8888))
    while True:
        message, new_ip_port = sk.recvfrom(200)
        service_type, file_cache_len, filename_size, filename = struct.unpack("iii100s", message)
        if service_type == 0 or service_type == 1:
            new_sk = socket(AF_INET, SOCK_DGRAM)
            new_port = 0
            get_socket = False
            while True:
                for port in range(8889, 8899):
                    try:
                        new_sk.bind(('',port))
                        new_port = port
                        get_socket = True
                        break
                    except:
                        print("address "+str(port)+" already used") 
                if get_socket:
                    break
                time.sleep(3)
            new_sk.settimeout(5)
            # 用户请求上传文件
            if service_type == 0:
                message = struct.pack("ii", new_port, 0)
                sk.sendto(message, new_ip_port)
                t = threading.Thread(target = Recv.service, args=(new_ip_port, file_cache_len, filename[:filename_size], new_sk))
                t.start()
            # 用户请求下载文件
            elif service_type == 1:
                # todo: 判断是否有这个文件
                filesize = os.path.getsize(filename[:filename_size])
                file_cache_len = int(filesize/buffer)+1
                if int(filesize/buffer)==filesize/buffer:
                    file_cache_len = file_cache_len-1
                message = struct.pack("ii", new_port, file_cache_len)
                sk.sendto(message, new_ip_port)
                t = multiprocessing.Process(target = Send.service, args=(new_ip_port, filename[:filename_size], new_sk))
                t.start()
    sk.close()

shake_hand()
