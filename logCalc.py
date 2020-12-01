import sys
from statistics import mean
from statistics import median

#File with time taken for each of the jobs executed
jobFile = open('joblogs.csv','r')
#File with time taken for each of the tasks executed
taskFile = open('tasklogs.csv','r')

jobList = []
taskList = []

jobList.extend([ float(jobTime.strip().split(',')[2]) for jobTime in jobFile])
# print (jobList)
taskList.extend([ float(taskTime.strip().split(',')[2]) for taskTime in taskFile])
# print (taskList)

jobFile.close()
taskFile.close()

meanJobs = mean(jobList)
medianJobs = median(jobList)
meanTasks = mean(taskList)
medianTasks = median(taskList)

print('mean time for jobs: ', meanJobs, '\nmedian time for jobs: ', medianJobs)
print('mean time for tasks: ', meanTasks, '\nmedian time for tasks: ', medianTasks)

