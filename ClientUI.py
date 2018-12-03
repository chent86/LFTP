import fileClient

while True:
    dirpath = input()
    filename = input()
    fileClient.service(dirpath, filename)