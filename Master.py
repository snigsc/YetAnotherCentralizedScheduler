import json 
import sys
import _thread
from socket import *
import threading
import random
import pickle
import time
from statistics import mean
from statistics import median
import os

# Random Scheduler - Randomly schedules tasks to worker with free slots - returns worker
# wl -> list of the three worker objects
def randomScheduler(wl):
    while 1:
        w = random.randrange(0,len(wl))
        s = wl[w].slots
        bs = wl[w].busy_slots
        if bs < s:
            return wl[w]
    return -1

# Round Robin Scheduler - Assigns worker to tasks in rotation - returns worker
# wl -> list of the three worker objects
c = 0
def roundRobin(wl): 
    global c
    while 1:
        n = c%3
        if wl[n].slots > wl[n].busy_slots:
            c += 1
            return wl[n]
        c += 1
    return c

# Least Loaded Scheduler - Finds worker with max free slots - returns worker
# wl -> list of the three worker objects
def leastLoaded(wl):
    maxFreeSlots = 0
    idx = -1
    while idx==-1:
        for i in range(len(wl)):
            freeSlots = wl[i].slots - wl[i].busy_slots
            #print(freeSlots)
            if freeSlots > maxFreeSlots:
                maxFreeSlots = freeSlots
                idx = i
            #print(maxFreeSlots, wl[idx].w_id, i, wl[i].slots, wl[i].busy_slots)
        if maxFreeSlots!=0:
            return wl[idx]
        time.sleep(1)
    return wl[idx]

# establishing a connection with the worker and sending the task to be executed
def sendTask(task,worker):
    clientName = "localhost"
    workerPort = worker.port
    clientSocket = socket(AF_INET, SOCK_STREAM)
    clientSocket.connect((clientName,workerPort))
    print('Sending task: ', task.t_id, 'to worker: ', worker.w_id)
    msg = pickle.dumps(task)
    clientSocket.send(msg)
    clientSocket.close()

def callScheduleReduceTask(wl,job):
    lock.acquire()
    reqList[job].scheduleReduceTask(wl)
    lock.release()

# listening to the worker for updates -> completed task and worker
def listenToWorker(wl):
    serverName = "localhost"
    requestPort = 5001
    masterSocket = socket(AF_INET, SOCK_STREAM)
    masterSocket.bind(("",requestPort))
    masterSocket.listen(1)
    while 1:
        connectionSocket, addr = masterSocket.accept()
        ip = connectionSocket.recv(1024)
        # completedTask -> The completed task object 
        # updateWorker -> Id of the worker that executed the task
        completedTask, updateWorker = pickle.loads(ip)
        end_time = time.time()
        # index position of worker in workerList = workerId - 1
        wl[updateWorker-1].freeSlot()
        # job -> stores the Job ID of the task that completed execution
        job = int(completedTask.r_id)

        try:
            # completedTask.t_id of the form 0_M0 ; m -> index of 'M'
            m = completedTask.t_id.index('M')
            # start of critical section -> reqList access 
            lock.acquire()
            # completedTask.t_id[m+1:] -> gives the index of the map task in maps[]
            # returns the completed task object using reqList
            ogCompletedTask = reqList[job].maps[int(completedTask.t_id[m+1:])]
            ogCompletedTask.markCompleted()
            ogCompletedTask.end = end_time
            # writing time taken for each map task into file -> tasklogs.csv
            print('Task: ', ogCompletedTask.t_id, 'completed')
            with open(scheduler+'_tasklogs.csv','a') as taskLogs:                
                taskLogs.write("{},{},{},{},{}\n".format(updateWorker, ogCompletedTask.t_id, ogCompletedTask.start, ogCompletedTask.end, ogCompletedTask.end - ogCompletedTask.start))
            taskLogs.close()
            # checks if all map tasks of a job are completed
            # ready = 1 : completed all mappers, else ready = 0
            ready = reqList[job].reducerReady()
            # end of critical section -> reqList access 
            lock.release()
            # reducer tasks scheduled after all mapper tasks execute
            if ready:
                print('Job ', job, 'scheduling reducer tasks')
                try:
                    t3 = threading.Thread(target=callScheduleReduceTask, args=(wl,job))
                    t3.start()
                except: 
                    pass
                #reqList[job].scheduleReduceTask(wl)
            
        except:
            # completedTask.t_id of the form 0_R0 ; r -> index of 'R'
            r = completedTask.t_id.index('R')
            # start of critical section -> reqList access 
            lock.acquire()
            # completedTask.t_id[r+1:] -> gives the index of the map task in reds[]
            # returns the completed task object using reqList
            ogCompletedTask = reqList[job].reds[int(completedTask.t_id[r+1:])]
            ogCompletedTask.markCompleted()
            ogCompletedTask.end = end_time
            # writing time taken for each reduce task into file -> tasklogs.csv
            print('Task: ', ogCompletedTask.t_id, 'completed')
            with open(scheduler+'_tasklogs.csv','a') as taskLogs:                
                taskLogs.write("{},{},{},{},{}\n".format(updateWorker,ogCompletedTask.t_id, ogCompletedTask.start, ogCompletedTask.end, ogCompletedTask.end - ogCompletedTask.start))
            taskLogs.close()           
            # checks if all the tasks (map and reduce) of a job are completed
            # jobDone = 1 : completed all tasks, else jobDone = 0
            jobDone = reqList[job].isCompletedR()
            if jobDone:
                # end time of job = end time of last reduce task
                reqList[job].end = end_time
                print('Job ', job, 'completed')
                # writing time taken for job into file -> joblogs.csv
                with open(scheduler+'_joblogs.csv','a') as jobLogs:                
                    jobLogs.write("{},{},{},{}\n".format(job, reqList[job].start, reqList[job].end, reqList[job].end - reqList[job].start))
                jobLogs.close()
            lock.release()
    masterSocket.close()

# listens for requests from Requests.py at port 5000
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
        start_time = time.time()
        # creates object req of class Request for each job
        req = Request(req_json['job_id'],req_json['map_tasks'],req_json['reduce_tasks'],start_time,-1)
        # critical section -> reqList (global list of Requests)
        lock.acquire()
        reqList.append(req)
        # end of critical section
        lock.release()
        req.scheduleMapTask(workersList)
    masterSocket.close()

# worker class to create the 3 worker objects with id, slots, ports
# busy slots -> created to mark number of slots occupied my tasks in the worker
class Worker:
    def __init__(self,w_id,slots,port,busy_slots):
        self.w_id = w_id
        self.slots = slots
        self.port = port
        self.busy_slots = busy_slots
    
    # called when a task completes and a slot becomes free
    def freeSlot(self):
        self.busy_slots -= 1
    
    # called when a task is assigned to the worker and a slot is occupied
    def markBusy(self):
        self.busy_slots += 1

# task objects created here -> for both mapper and reducer tasks
class Task:
    def __init__(self,r_id,t_id,duration,status,start_time,end_time):
        # stores the job id that the task belongs to
        self.r_id = r_id
        self.t_id = t_id
        self.duration = duration
        # status-> marked as 0 : task incomplete ; 1 : task completed
        self.status = status
        # start and end -> denotes when a task is created and completed
        self.start = start_time
        self.end = end_time
    
    # marks status as 1: Task completed
    def markCompleted(self):
        self.status = 1
        # print('in completed',self.t_id)

    # checks if task is complete
    def isCompletedT(self):
        return self.status

# request class to create the request objects (jobs)
# maps [] -> used to store all map tasks of a job
# reds [] -> used to store all reduce tasks of a job
class Request:

    def __init__(self,r_id,map_tasks,reduce_tasks,start_time,end_time):
        self.maps = []
        self.reds = []
        self.r_id = r_id
        for i in map_tasks:
            # creating task objects for map and reduce tasks
            self.maps.append(Task(self.r_id,i['task_id'],i['duration'],0,-1,-1))
        for i in reduce_tasks:
            self.reds.append(Task(self.r_id,i['task_id'],i['duration'],0,-1,-1))
        # start and end time for each job
        self.start = start_time
        self.end = end_time
 
    def scheduleMapTask(self, wl):
        for i in self.maps:
            # freeWorker -> worker that the task gets assigned to according to the selected algo
            freeWorker = algo(wl) 
            i.start = time.time()
            sendTask(i,freeWorker)
            freeWorker.markBusy()

    def scheduleReduceTask(self, wl):
        for i in self.reds:
            # freeWorker -> worker that the task gets assigned to according to the selected algo
            freeWorker = algo(wl)
            i.start = time.time()
            sendTask(i,freeWorker)
            freeWorker.markBusy()  

    # checks if all map tasks are complete and reducer tasks can begin executing
    def reducerReady(self):
        for i in self.maps:
            if i.isCompletedT()==0:
                return 0
        return 1

    # checks if request (job) is complete
    def isCompletedR(self):
        for i in self.reds:
            if i.isCompletedT()==0:
                return 0
        return 1

    def printTasks(self):
        print(self.maps)
        print(self.reds) 


def delExistingFile(scheduler):
    # joblogs.csv -> File with time taken for each of the jobs to execute
    if os.path.exists(scheduler+'_joblogs.csv'):
        os.remove(scheduler+'_joblogs.csv')
    # tasklogs.csv -> File with time taken for each of the tasks to execute
    if os.path.exists(scheduler+'_tasklogs.csv'):
        os.remove(scheduler+'_tasklogs.csv')
    with open(scheduler+'_joblogs.csv','a') as f:
        f.write('JobID,startTime,endtime,JobCompletionTime\n')
    f.close()
    with open(scheduler+'_tasklogs.csv','a') as f:
        f.write('WorkerID,taskID,startTime,endTime,TaskCompletionTime\n')
    f.close()

if __name__ == '__main__':
    workersconfig = json.load(open(sys.argv[1],'r'))
    # workersList -> list of 3 worker objects
    workersList = []
    for i in workersconfig['workers']:
        workersList.append(Worker(i['worker_id'],i['slots'],i['port'],0))   
    # CLI argument for scheduling algo
    global scheduler
    scheduler = sys.argv[2]
    # list of all request objects sent to Master
    reqList = []
    # creating lock object to take care of critical sections of the code
    lock = threading.Lock()
    if scheduler == 'RR':
        algo = roundRobin
    elif scheduler == 'RANDOM':
        algo = randomScheduler
    elif scheduler == 'LL':
        algo = leastLoaded
    else:
        print("Invalid scheduling algorithm")
        exit()
    delExistingFile(scheduler)
    # thread t1 -> gets and assigns tasks in the requests
    t1 = threading.Thread(target=getRequest, args=(workersList,))
    # thread t2 -> listens to worker for task updates
    t2 = threading.Thread(target=listenToWorker, args=(workersList,)) 
    t1.start()
    t2.start()
