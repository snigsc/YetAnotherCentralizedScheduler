import json 
#import socket
import sys
import _thread
from socket import *
import threading



#workers = {}
workersconfig = json.load(open(sys.argv[1],'r'))
print(workersconfig)

def listenToRequest(num):
    serverName = "localhost"
    requestPort = 5000
    masterSocket = socket(AF_INET, SOCK_STREAM)
    masterSocket.bind(("localhost",requestPort))
    masterSocket.listen(1)
    print("The Master is ready to receive")
    while 1:
        connectionSocket, addr = masterSocket.accept()
        ip = connectionSocket.recv(1024)
        req = json.loads(ip)
        print(type(req))
    masterSocket.close()

def manageWorker():
    serverName = "localhost"
    workerPort = 5001
    workerSocket = socket(AF_INET, SOCK_STREAM)
    workerSocket.bind(("localhost",workerPort))

try:
    t1 = threading.Thread(target=listenToRequest, args=(1,))
    #t2 = threading.Thread(target=manageWorker, args=(1,))) 
    t1.start()
    
    print("Hi")
    #_thread.start_new_thread(listenToRequest,(,))
    #_thread.start_new_thread(manageWorker,(,))
except:
    print("Did not start thread bye")
