import struct
import os
import time
# 从客户端接收文件
def service(target_ip_port, file_cache_len, filename, sk):
    buffer = 1024
    recv_base = 0
    file_cache = [0]*file_cache_len
    ACK_status = [0]*file_cache_len
    rwnd = 500
    print("Receiving file from "+str(target_ip_port))
    start_time = time.time()
    while True:
        process(recv_base, file_cache_len, start_time)
        # print(str(recv_base)+' '+str(file_cache_len))
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
                recv_base = recv_base+1
                process(recv_base, file_cache_len, start_time)
                # print(str(recv_base)+' '+str(file_cache_len))
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
    except Exception:
        percent = 100
    if recv_base != file_cache_len:
        print('complete percent:%10.8s%s   spent time:%s%s'%(str(percent),'%', str(int(time.time()-start_time)),'s'),end='\r')
    else:
        print('complete percent:%10.8s%s   spent time:%s%s'%(str(percent),'%', str(int(time.time()-start_time)),'s'))