from socket import *
import struct
# serverName = '127.0.0.1'
serverName = '119.29.204.118'
serverPort = 8888
clientSocket = socket(AF_INET, SOCK_DGRAM)
a = "123"
# message = raw_input('Input lowercase sentence:')
clientSocket.sendto(a.encode('utf-8'), (serverName, serverPort))
message = clientSocket.recv(100)
print(message)

# modifiedMessage, serverAddress = clientSocket.recvfrom(2048)
# print modifiedMessage
# clientSocket.close()