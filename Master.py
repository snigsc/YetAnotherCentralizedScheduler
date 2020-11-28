import json 
import socket
import sys
import threading

from socket import *
serverName = "localhost"
serverPort = 5000
masterSocket = socket(AF_INET, SOCK_STREAM)

masterSocket.bind(("localhost",serverPort))
masterSocket.listen(1)
print("The Master is ready to receive")
while 1:
    connectionSocket, addr = masterSocket.accept()
    ip = connectionSocket.recv(1024)
    print(ip)
 
masterSocket.close()