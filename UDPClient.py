from socket import *

serverName = '127.0.0.1'
serverPort = 12345
clientSocket = socket(AF_INET, SOCK_DGRAM)
# message = raw_input('Input lowercase sentence:')
clientSocket.sendto('1', (serverName, serverPort))
clientSocket.sendto('2', (serverName, serverPort))
clientSocket.sendto('3', (serverName, serverPort))
clientSocket.sendto('4', (serverName, serverPort))
clientSocket.sendto('5', (serverName, serverPort))
clientSocket.sendto('6', (serverName, serverPort))
clientSocket.sendto('7', (serverName, serverPort))
clientSocket.sendto('8', (serverName, serverPort))
# modifiedMessage, serverAddress = clientSocket.recvfrom(2048)
# print modifiedMessage
# clientSocket.close()