import json 
#import socket
import sys
import _thread
from socket import *
import threading
import random

workers = {}
workersconfig = json.load(open(sys.argv[1],'r'))

count=1
for i in workersconfig['workers']:
    if count not in workers.keys():
        workers[count] = []
    workers[count].extend([i['worker_id'],i['slots'],i['port'],0])
    count+=1

print(workers)  #{1: [1, 5, 4000, 0], 2: [2, 7, 4001, 0], 3: [3, 3, 4002, 0]}
#worker: id,slots,port,num_tasks

#scheduler = sys.argv[2]

def randomScheduler(req):
    flag = 0
    while 1:
        w = random.randrange(1,4)
        ports = workers[w][2]
        tasks = workers[w][3]
        if ports > tasks:
            flag = w
            break
    if flag!=0:
        return flag

def manageRequest(num):
    '''Job request : {'job_id': '0', 'map_tasks': [{'task_id': '0_M0', 'duration': 2}, {'task_id': '0_M1', 'duration': 4}], 'reduce_tasks': [{'task_id': '0_R0', 'duration': 2}]}
    interval:  0.09692741268979561 
    Job request : {'job_id': '1', 'map_tasks': [{'task_id': '1_M0', 'duration': 3}, {'task_id': '1_M1', 'duration': 1}, {'task_id': '1_M2', 'duration': 1}], 'reduce_tasks': [{'task_id': '1_R0', 'duration': 4}, {'task_id': '1_R1', 'duration': 2}]}'''

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

        #print(req)
        w = randomScheduler(req)
        print(w)

    masterSocket.close()







def listenToWorker():


    serverName = "localhost"
    workerPort = 5001
    workerSocket = socket(AF_INET, SOCK_STREAM)
    workerSocket.bind(("localhost",workerPort))




try:
    t1 = threading.Thread(target=manageRequest, args=(1,))
    #t2 = threading.Thread(target=listenToWorker, args=(1,))) 
    t1.start()
    
    print("Hi")
    #_thread.start_new_thread(listenToRequest,(,))
    #_thread.start_new_thread(manageWorker,(,))
except:
    print("Did not start thread bye")
