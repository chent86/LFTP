from socket import *
import struct
serverPort = 8888
serverSocket = socket(AF_INET, SOCK_DGRAM)
serverSocket.bind(('',serverPort))
print("The server is ready to receive")
while True:
    message, clientAddress = serverSocket.recvfrom(3000)
    print(message)
    seq, content, size = struct.unpack("i4si", message)
    content = content[:size]
    print(content)
    # modifiedMessage = message.upper()
    # serverSocket.sendto(modifiedMessage, clientAddress)