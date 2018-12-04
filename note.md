1. struct.pack()传输数据时，个别的字节长度可能会在传输的过程中被丢弃，总之无法被接收(在互联网中的情况)

demo:
发送方
```python
from socket import *
import struct
serverName = '119.29.204.118'
serverPort = 8888
clientSocket = socket(AF_INET, SOCK_DGRAM)
a = "123"
message = struct.pack("i1024si", 65, a.encode('utf-8'), 3)
clientSocket.sendto(message, (serverName, serverPort))
```
接收方
```python
from socket import *
import struct
serverPort = 8888
serverSocket = socket(AF_INET, SOCK_DGRAM)
serverSocket.bind(('',serverPort))
print("The server is ready to receive")
while True:
    message, clientAddress = serverSocket.recvfrom(3000)
    print(message)
    seq, content, size = struct.unpack("i1024si", message)
    content = content[:size]
    print(content)
```
如果代码中的字符长度为2048,会出现无法收到包的情况

2. 接收message的socket才有权利回复信息,如果使用另外的socket去主动访问客户端的端口，会无法连通

demo
```python
message, new_ip_port = sk.recvfrom(200)
sk.sendto(byte, new_ip_port) #　可以送到
new_sk.sendto(byte, new_ip_port) #　无法送到
```