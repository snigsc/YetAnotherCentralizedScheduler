import sys
from socket import *
import threading
import pickle
import time
from Master import Task

# sends updates to master on task completion -> sends completed task and workerId
def sendUpdate(task):
    clientName = "localhost"
    workerPort = 5001
    clientSocket = socket(AF_INET, SOCK_STREAM)
    clientSocket.connect((clientName,workerPort))
    print('Sending update to Worker: Task Completed',task.t_id)
    msg = pickle.dumps((task,workerId))
    clientSocket.send(msg)
    clientSocket.close()

# listens for tasks from Master 
def getTask(workerId):
    global execPool
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
        # acquire lock -> critical section -> execPool[]
        lock.acquire()
        #print('getTask')
        execPool.append([task,time.time()]) 
        # release lock -> exiting critical section -> execPool[]
        lock.release() 
        try:
            t2 = threading.Thread(target=executeTask, args=())
            t2.start()
            #print('T2 started')
        except: 
            pass
    masterSocket.close()

# fn to execute tasks and decrement duration for tasks per clock cycle, until task is complete
def executeTask():
    global execPool
    while 1: 
        #time.sleep(1)
        # acquire lock -> accessing critical section -> execPool[]
        lock.acquire() 
        #print('executeTask')
        for i in execPool:
            if (time.time() - i[1]) >= i[0].duration:
                i[0].duration -= 1
            # send update to Master on completion of task -> remaining duration = 0
            if i[0].duration==0:
                sendUpdate(i[0])
            #print(i.t_id, i.duration)
        # execPool repopulated with only those tasks that still need to run (removes all those with duration = 0)
        execPool = [i for i in execPool if i[0].duration!=0]  
        # release lock -> exiting critical section -> execPool[]   
        lock.release()

if __name__ == '__main__': 
    port = int(sys.argv[1])
    workerId = int(sys.argv[2])
    # execPool -> execution pool with all the tasks currently being processed
    execPool = []
    lock = threading.Lock()
    # thread 1 -> listens for tasks from the Master
    t1 = threading.Thread(target=getTask, args=(workerId,))
    t1.start()
    # print('T1 started')
    # thread 2 -> executes tasks and sends updates to Master
    # t2 = threading.Thread(target=executeTask, args=())
    # t2.start()
    # # print('T2 started')
