import Upload
import Download
import os
import struct
from socket import *
import threading
import time


# hostName = '119.29.204.118'
hostName = '127.0.0.1'
ip_port = (hostName, 8888)

sk = socket(AF_INET, SOCK_DGRAM)

# 建立连接
shake_finish = False
def shake_hand(filename, file_cache_len, service_type):
    global ip_port, shake_finish
    message = struct.pack("iii100s", service_type, file_cache_len, len(filename), filename.encode('utf-8'))
    sk.sendto(message, ip_port)

    # print('send syn')
    shake_finish = False
    helper = threading.Thread(target = shake_helper, args=(filename,))
    helper.start()
    print('start to recv')
    message = sk.recv(1024)
    new_port, file_cache_len = struct.unpack("ii", message)
    print('new port is '+str(new_port))
    shake_finish = True
    print('recv OK')
    return new_port, file_cache_len

# SYN 信息重发
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

while True:
    # dirpath = input()
    filename = input()

    # path = os.path.join(dirpath, filename)
    # filesize = os.path.getsize(path)
    # new_port, file_cache_len = shake_hand(filename, int(filesize/Upload.buffer)+1, 0)
    # Upload.service(dirpath, filename, (hostName,new_port), sk)
    new_port, file_cache_len = shake_hand(filename, 0, 1)
    Download.service((hostName,new_port), file_cache_len, filename, sk)
