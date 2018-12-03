from socket import *
import struct
serverPort = 8888
serverSocket = socket(AF_INET, SOCK_DGRAM)
serverSocket.bind(('',serverPort))
print("The server is ready to receive")
message, clientAddress = serverSocket.recvfrom(3000)
print(message)
sk = socket(AF_INET, SOCK_DGRAM)
sk.sendto(message, clientAddress)

    # modifiedMessage = message.upper()
    # serverSocket.sendto(modifiedMessage, clientAddress)