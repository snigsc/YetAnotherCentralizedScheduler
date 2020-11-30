import sys
from statistics import mean
from statistics import median

jobFile = open('joblogs.txt','r')
taskFile = open('tasklogs.txt','r')

jobList = []
taskList = []

jobList.extend([ float(jobTime.strip()) for jobTime in jobFile])
# print (jobList)
taskList.extend([ float(taskTime.strip()) for taskTime in taskFile])
# print (taskList)

jobFile.close()
taskFile.close()

meanJobs = mean(jobList)
medianJobs = median(jobList)
meanTasks = mean(taskList)
medianTasks = median(taskList)
print('mean time for jobs: ', meanJobs, '\nmedian time for jobs: ', medianJobs)
print('mean time for tasks: ', meanTasks, '\nmedian time for tasks: ', medianTasks)
    
# for jobTime in jobFile:
#     jobTime = jobTime.strip()
#     jobList.append(float(jobTime))

# for taskTime in taskFile:
#     taskTime = taskTime.strip()
#     taskList.append(float(taskTime))


