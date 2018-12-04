import struct
import os
import time
import threading
# 从客户端接收文件

recv_base = 0
has_finish = False

def download(target_ip_port, file_cache_len, filename, sk):
    global recv_base, has_finish
    buffer = 1024
    file_cache = [0]*file_cache_len
    ACK_status = [0]*file_cache_len
    rwnd = 500
    print("Receiving file from "+str(target_ip_port))
    start_time = time.time()
    while True:
        process(recv_base, file_cache_len, start_time)
        if recv_base == file_cache_len:
            save_file(file_cache, filename)
            break 
        try:
            message, ip_port = sk.recvfrom(buffer+30)
            if ip_port[0] != target_ip_port[0]:  # 限制其他ip恶意连接
                continue
        except Exception:
            print("time out")
            break
        seq, content, size = struct.unpack("i1024si", message)
        if seq >= recv_base and seq < recv_base+rwnd:
            ACK_status[seq] = 1
            message = struct.pack("ii", seq, recv_base)
            sk.sendto(message, ip_port)
            while ACK_status[recv_base] == 1:
                process(recv_base, file_cache_len, start_time)
                recv_base = recv_base+1
                if recv_base==file_cache_len:
                    break
        elif seq >= recv_base-rwnd and seq < recv_base:
            message = struct.pack("ii", seq, recv_base)
            sk.sendto(message, ip_port)
        else:
            continue
        if seq == file_cache_len-1:
            file_cache[seq] = content[:size]
        else:
            file_cache[seq] = content
    sk.close()
    has_finish = True
    recv_base = 0

# 保存文件
def save_file(file_cache, filename):
    with open(filename, 'wb') as f:
        for content in file_cache:
            f.write(content)
    print('OK')

# 输出当前进度
def process(recv_base, file_cache_len, start_time):
    try:
        percent = recv_base*100/file_cache_len
        speed = int(recv_base/int(time.time()-start_time))
    except Exception:
        percent = 100
        speed = 0
    if recv_base != file_cache_len:
        print('complete percent:%10.8s%s   spent time:%s%s  speed: %s kb/s '%(str(percent),'%', str(int(time.time()-start_time)),'s', str(speed)),end='\r')
    else:
        print('complete percent:%10.8s%s   spent time:%s%s  speed: %s kb/s '%(str(percent),'%', str(int(time.time()-start_time)),'s', str(speed)))

def shake_hand(ip_port, sk):
    global recv_base
    while True:
        message = struct.pack("ii", -1, -1)
        try:
            sk.sendto(message, ip_port)
        except Exception:
            break
        if recv_base != 0 or has_finish:
            break
        time.sleep(1)
    
def service(ip_port, file_cache_len, filename, sk):
    global has_finish
    has_finish = False
    t = threading.Thread(target = download, args=(ip_port, file_cache_len, filename, sk))
    t.start()
    shake_hand(ip_port, sk)
    t.join()
