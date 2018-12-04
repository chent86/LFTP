import struct
import os
import time
import threading
# 从客户端接收文件

recv_base = 0

def download(target_ip_port, file_cache_len, filename, sk):
    global recv_base
    buffer = 1024
    file_cache = [0]*file_cache_len
    ACK_status = [0]*file_cache_len
    rwnd = 500
    print("Receiving file from "+str(target_ip_port))
    while True:
        if recv_base == file_cache_len:
            save_file(file_cache, filename)
            break 
        try:
            message, ip_port = sk.recvfrom(buffer+30)
            if ip_port != target_ip_port:  # 限制其他ip恶意连接
                continue
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
    recv_base = 0

# 保存文件
def save_file(file_cache, filename):
    with open(filename, 'wb') as f:
        for content in file_cache:
            f.write(content)
    print('OK')

def shake_hand(ip_port, sk):
    global recv_base
    while True:
        sk.sendto(b'-1', ip_port)
        if recv_base != 0:
            break
        time.sleep(1)
    
def service(ip_port, file_cache_len, filename, sk):
    t = threading.Thread(target = download, args=(ip_port, file_cache_len, filename, sk))
    t.start()
    shake_hand(ip_port, sk)
