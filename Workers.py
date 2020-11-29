import json 
#import socket
import sys
import _thread
from socket import *
import threading
import random
import pickle

workerId = int(sys.argv[2])
port = int(sys.argv[1])


class Task:
    def __init__(self,t_id,duration,status):
        self.t_id = t_id
        self.duration = duration
        self.status = status
    
    def markCompleted(self):
        self.status = 1

    def isCompletedT(self):
        return self.status

    def printTask(self):
        print(self.t_id)
        #print(self.duration)
        #print(self.status)


serverName = "localhost"
requestPort = port
masterSocket = socket(AF_INET, SOCK_STREAM)
masterSocket.bind(("",requestPort))
masterSocket.listen(1)
print("The Worker is ready to receive")
while 1:
    connectionSocket, addr = masterSocket.accept()
    ip = connectionSocket.recv(1024)
    task = pickle.loads(ip)
    task.printTask()
  
masterSocket.close()