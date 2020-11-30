import json 
#import socket
import sys
import _thread
from socket import *
import threading
import random
import pickle
import time


def randomScheduler(wl):
    while 1:
        w = random.randrange(0,len(wl))
        s = wl[w].slots
        bs = wl[w].busy_slots
        if bs < s:
            return wl[w]
    return -1

c = 0
def roundRobin(wl): 
    global c
    while 1:
        n = c%3
        if wl[n].slots > wl[n].busy_slots:
            c += 1
            print('n: ',n)
            return wl[n]
        c += 1
    return c


def leastLoaded(wl):
    maxFreeSlots = 0
    idx = -1
    while idx==-1:
        for i in range(len(wl)):
            freeSlots = wl[i].slots - wl[i].busy_slots
            print(freeSlots)
            if freeSlots > maxFreeSlots:
                maxFreeSlots = freeSlots
                idx = i
            #print(maxFreeSlots, wl[idx].w_id, i, wl[i].slots, wl[i].busy_slots)
        if maxFreeSlots!=0:
            return wl[idx]
        time.sleep(1)
    return wl[idx]


scheduler = sys.argv[2]
reqList = []
lock = threading.Lock()

if scheduler=='RR':
    algo = roundRobin
elif scheduler=='RANDOM':
    algo = randomScheduler
elif scheduler=='LL':
    algo = leastLoaded
else:
    print("Invalid scheduling algorithm")
    exit()


class Worker:
    def __init__(self,w_id,slots,port,busy_slots):
        self.w_id = w_id
        self.slots = slots
        self.port = port
        self.busy_slots = busy_slots
    
    def freeSlot(self):
        self.busy_slots -= 1
    
    def markBusy(self):
        self.busy_slots += 1


class Task:
    def __init__(self,r_id,t_id,duration,status):
        self.r_id = r_id
        self.t_id = t_id
        self.duration = duration
        self.status = status
    
    def markCompleted(self):
        self.status = 1
        print('in completed',self.t_id)

    def isCompletedT(self):
        return self.status


def sendTask(task,worker):
    clientName = "localhost"
    workerPort = worker.port
    clientSocket = socket(AF_INET, SOCK_STREAM)
    #print('connecting to worker')
    clientSocket.connect((clientName,workerPort))
    print('sending task')
    msg = pickle.dumps(task)
    clientSocket.send(msg)
    clientSocket.close()



def listenToWorker(wl):
    serverName = "localhost"
    requestPort = 5001
    masterSocket = socket(AF_INET, SOCK_STREAM)
    masterSocket.bind(("",requestPort))
    masterSocket.listen(1)
    while 1:
        connectionSocket, addr = masterSocket.accept()
        ip = connectionSocket.recv(1024)
        completedTask, updateWorker = pickle.loads(ip)
        #print(completedTask.t_id)
        
        #completedTask.markCompleted()
        wl[updateWorker-1].freeSlot()
        job = int(completedTask.r_id)

        try:
            m = completedTask.t_id.index('M')
            lock.acquire()
            reqList[job].maps[int(completedTask.t_id[m+1:])].markCompleted()
            ready = reqList[job].reducerReady()
            print('ready',ready, 'job',job)
            if ready:
                reqList[job].scheduleReduceTask(wl)
            lock.release()
        except:
            r = completedTask.t_id.index('R')
            lock.acquire()
            reqList[job].reds[int(completedTask.t_id[r+1:])].markCompleted()
            jobDone = reqList[job].isCompletedR()
            if jobDone:
                print("JOB DONE:",job)
            lock.release()
    masterSocket.close()


class Request:
    maps = []
    red = []
    def __init__(self,r_id,map_tasks,reduce_tasks):
        self.maps = []
        self.reds = []
        self.r_id = r_id
        for i in map_tasks:
            self.maps.append(Task(self.r_id,i['task_id'],i['duration'],0))
        for i in reduce_tasks:
            self.reds.append(Task(self.r_id,i['task_id'],i['duration'],0))

    def scheduleMapTask(self, wl):
        for i in self.maps:
            freeWorker = algo(wl) 
            print(freeWorker.w_id, freeWorker.busy_slots)
            sendTask(i,freeWorker)
            freeWorker.markBusy()

    def scheduleReduceTask(self, wl):
        for i in self.reds:
            freeWorker = algo(wl) 
            print(freeWorker.w_id, freeWorker.busy_slots)
            sendTask(i,freeWorker)
            freeWorker.markBusy()  
        
    def reducerReady(self):
        for i in self.maps:
            print('completed:',i.isCompletedT(),'task',i.t_id)
            if i.isCompletedT()==0:
                return 0
        return 1

    def isCompletedR(self):
        for i in self.reds:
            if i.isCompletedT()==0:
                return 0
        return 1

    def printTasks(self):
        print(self.maps)
        print(self.reds) 


def getRequest(workersList):
    serverName = "localhost"
    requestPort = 5000
    masterSocket = socket(AF_INET, SOCK_STREAM)
    masterSocket.bind(("",requestPort))
    masterSocket.listen(1)
    print("The Master is ready to receive")
    while 1:
        connectionSocket, addr = masterSocket.accept()
        ip = connectionSocket.recv(1024)
        req_json = json.loads(ip)
        req = Request(req_json['job_id'],req_json['map_tasks'],req_json['reduce_tasks'])
        lock.acquire()
        reqList.append(req)
        lock.release()
        req.scheduleMapTask(workersList)
    masterSocket.close()


def main():
    workersconfig = json.load(open(sys.argv[1],'r'))
    workersList = []
    for i in workersconfig['workers']:
        #print(i)
        workersList.append(Worker(i['worker_id'],i['slots'],i['port'],0))

    t1 = threading.Thread(target=getRequest, args=(workersList,))
    t2 = threading.Thread(target=listenToWorker, args=(workersList,)) 
    t1.start()
    t2.start()

main()