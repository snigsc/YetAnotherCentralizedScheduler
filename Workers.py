import json 
#import socket
import sys
import _thread
from socket import *
import threading
import random
import pickle
import time

port = int(sys.argv[1])
workerId = int(sys.argv[2])

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
        print(self.t_id, self.duration, self.status)
        

execPool = []

lock = threading.Lock()

def sendUpdate(task):
    clientName = "localhost"
    workerPort = 5001
    clientSocket = socket(AF_INET, SOCK_STREAM)
    clientSocket.connect((clientName,workerPort))
    print('sending update',task.t_id,workerId)
    msg = pickle.dumps((task,workerId))
    clientSocket.send(msg)
    clientSocket.close()


def getTask():
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
        print('received')
        task.printTask()
        lock.acquire()
        execPool.append(task) 
        lock.release() 
    masterSocket.close()

def executeTasks():
    print('inside exec')
    #remaining = {}
    global execPool
    while 1: 
        #print(execPool)
        lock.acquire()
        for i in execPool:
            #if i.duration>0:
            i.duration -= 1
            print(i.t_id,i.duration)
            if i.duration==0:
                sendUpdate(i)
        execPool = [i for i in execPool if i.duration!=0]       
        lock.release()


def main():
    t1 = threading.Thread(target=getTask, args=())
    t1.start()
    print('t1 started')
    t2 = threading.Thread(target=executeTasks, args=())
    t2.start()
    print('t2 started')

main()