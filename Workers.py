import sys
from socket import *
import threading
import pickle
import time
from Master2 import Task


def sendUpdate(task):
    clientName = "localhost"
    workerPort = 5001
    clientSocket = socket(AF_INET, SOCK_STREAM)
    clientSocket.connect((clientName,workerPort))
    print('Sending update to Worker: Task Completed',task.t_id)
    msg = pickle.dumps((task,workerId))
    clientSocket.send(msg)
    clientSocket.close()

def getTask():
    serverName = "localhost"
    requestPort = port
    masterSocket = socket(AF_INET, SOCK_STREAM)
    masterSocket.bind(("",requestPort))
    masterSocket.listen(1)
    print('Worker '+str(workerId)+' is ready to receive')
    while 1:
        connectionSocket, addr = masterSocket.accept()
        ip = connectionSocket.recv(1024)
        task = pickle.loads(ip)
        print('Received Task:',task.t_id)
        lock.acquire()
        execPool.append(task) 
        lock.release() 
        # try:
        #     t2 = threading.Thread(target=executeTask, args=())
        #     t2.start()
        #     #print('T2 started')
        # except: 
        #     pass
    masterSocket.close()

def executeTask():
    global execPool
    while 1: 
        time.sleep(1)
        lock.acquire() 
        for i in execPool:
            i.duration -= 1
            if i.duration==0:
                sendUpdate(i)
        execPool = [i for i in execPool if i.duration!=0]     
        lock.release()

if __name__ == '__main__': 
    port = int(sys.argv[1])
    workerId = int(sys.argv[2])
    execPool = []
    lock = threading.Lock()
    t1 = threading.Thread(target=getTask, args=())
    t1.start()
    print('T1 started')
    t2 = threading.Thread(target=executeTask, args=())
    t2.start()
    print('T2 started')
