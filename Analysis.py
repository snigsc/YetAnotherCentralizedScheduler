import pandas as pd
import seaborn as sns
import matplotlib as plt
from statistics import *
import sys
import os

mode = sys.argv[1]

def heatMap(f):
    jobs = pd.read_csv(f[0])
    tasks = pd.read_csv(f[1])
    jmeanlst.append(mean(jobs['JobCompletionTime'].tolist()))
    jmedianlst.append(median(jobs['JobCompletionTime'].tolist()))
    tmeanlst.append(mean(tasks['TaskCompletionTime'].tolist()))
    tmedianlst.append(median(tasks['TaskCompletionTime'].tolist()))
    #heatmap
    time0 = min(tasks['startTime'].tolist())
    timeN = max(tasks['endTime'].tolist())+1
    time_X = []
    for i in range(int(time0), int(timeN)):
     time_X.append(i)
    df = pd.DataFrame(columns = ['Worker1','Worker2','Worker3'],index=time_X)
    df = df.fillna(0)
    for i,row in tasks.iterrows():
     w = str(row['WorkerID'])
     for s in range(int(row['startTime']),int(row['endTime'])+1):
      df.loc[s,'Worker'+w]+=1
    sns.set(rc={'figure.figsize':(24,16)})
    plt.pyplot.figure()
    sns.heatmap(df.transpose(),cmap='Blues',cbar=True,annot=False)
    plt.pyplot.title('Time vs number of tasks running on each worker',fontsize=20)
    plt.pyplot.xlabel('Time', fontsize=20)
    plt.pyplot.ylabel('Workers',fontsize=20)
    plt.pyplot.savefig(f[1][:-4]+'.png')
    #print('Please check current working directory for the heatmap.')

def logs(mode):
    jobFile = open(mode+'_joblogs.csv','r')
    taskFile = open(mode+'_tasklogs.csv','r')
    next(jobFile)
    next(taskFile)
    jobList = []
    taskList = []
    jobList.extend([float(jobTime.strip().split(',')[-1]) for jobTime in jobFile])
    # print (jobList)
    taskList.extend([float(taskTime.strip().split(',')[-1]) for taskTime in taskFile])
    # print (taskList)
    jobFile.close()
    taskFile.close()
    meanJobs = mean(jobList)
    medianJobs = median(jobList)
    meanTasks = mean(taskList)
    medianTasks = median(taskList)
    print('Mean time for jobs: ', meanJobs, '\nMedian time for jobs: ', medianJobs)
    print('Mean time for tasks: ', meanTasks, '\nMedian time for tasks: ', medianTasks)

jmeanlst = ['Mean_Jobs']
tmeanlst = ['Mean_Tasks']
jmedianlst = ['Median_Jobs']
tmedianlst = ['Median_Tasks']

if mode=="RANDOM":
    if os.path.isfile('RANDOM_joblogs.csv') and os.path.isfile('RANDOM_tasklogs.csv'):
        logs(mode)
        f=['RANDOM_joblogs.csv','RANDOM_tasklogs.csv']
        heatMap(f)
    else:
        print('Files do not exist.')
    exit()
elif mode=="RR":
    if os.path.isfile('RR_joblogs.csv') and os.path.isfile('RR_tasklogs.csv'):
        logs(mode)
        f=['RR_joblogs.csv','RR_tasklogs.csv']
        heatMap(f)
    else:
        print('Files do not exist.')
    exit()
elif mode=="LL":
    if os.path.isfile('LL_joblogs.csv') and os.path.isfile('LL_tasklogs.csv'):
        logs(mode)
        f=['LL_joblogs.csv','LL_tasklogs.csv']
        heatMap(f)
    exit()
elif mode=="ALL":
    f_RANDOM=['RANDOM_joblogs.csv','RANDOM_tasklogs.csv']
    f_RR=['RR_joblogs.csv','RR_tasklogs.csv']
    f_LL=['LL_joblogs.csv','LL_tasklogs.csv']
    heatMap(f_RANDOM)
    heatMap(f_RR)
    heatMap(f_LL)

    #bar chart
    df = pd.DataFrame([jmeanlst,tmeanlst,jmedianlst,tmedianlst])
    df.columns = ['Metric','RANDOM','RR','LL']
    pos = list(range(len(df['LL'])))
    width = 0.25
    fig, ax = plt.pyplot.subplots(figsize=(10,5))
    plt.pyplot.bar(pos, df['LL'], width, alpha=0.5, color='#EE3224')
    plt.pyplot.bar([p + width for p in pos], df['RR'], width, alpha=0.5, color='#F78F1E')
    plt.pyplot.bar([p + width*2 for p in pos], df['RANDOM'], width, alpha=0.5, color='#FFC222')
    ax.set_ylabel('Time')
    ax.set_title('Comparison')
    ax.set_xticks([p + 1.5 * width for p in pos])
    ax.set_xticklabels(df['Metric'])
    plt.pyplot.xlim(min(pos)-width, max(pos)+width*4)
    plt.pyplot.ylim([0, max(df['LL'] + df['RR'] + df['RANDOM'])] )
    plt.pyplot.legend(['LL', 'RR', 'RANDOM'], loc='upper left')
    plt.pyplot.savefig('barChart.png')
    print('Done. Please check current working directory for files:\n barChart.png\n RANDOM_tasklogs.png\n RR_tasklogs.png\n LL_tasklogs.png')