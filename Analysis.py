import pandas as pd
import seaborn as sns
import matplotlib as plt
from statistics import *
import sys
import os.path

mode = sys.argv[1]

if mode=='1':
    files = []
    if os.path.isfile('RANDOM_joblogs.csv') and os.path.isfile('RANDOM_tasklogs.csv'):
        files.append([open('RANDOM_joblogs.csv','r'),open('RANDOM_tasklogs.csv','r')])
    if os.path.isfile('RR_joblogs.csv') and os.path.isfile('RR_tasklogs.csv'):
        files.append([open('RR_joblogs.csv','r'),open('RR_tasklogs.csv','r')])
    if os.path.isfile('LL_joblogs.csv') and os.path.isfile('LL_tasklogs.csv'):
        files.append([open('LL_joblogs.csv','r'),open('LL_tasklogs.csv','r')])
    # print(files)
    for f in files:
        next(f[0])
        next(f[1])
        jobList = []
        taskList = []
        jobList.extend([float(jobTime.strip().split(',')[-1]) for jobTime in f[0]])
        # print (jobList)
        taskList.extend([float(taskTime.strip().split(',')[-1]) for taskTime in f[1]])
        # print (taskList)
        f[0].close()
        f[1].close()
        try:
            meanJobs = mean(jobList)
            medianJobs = median(jobList)
            meanTasks = mean(taskList)
            medianTasks = median(taskList)
            i = f[0].name.index('_')
            print('\nAlgorithm: '+f[0].name[:i])
            print('Mean time for jobs: ', meanJobs, 's \nMedian time for jobs: ', medianJobs, 's')
            print('Mean time for tasks: ', meanTasks, 's \nMedian time for tasks: ', medianTasks,'s \n')
        except:
            pass
    exit()   
elif mode=='2':
    pass 
else:
    print('Invalid input')
    exit()


files = [['RANDOM_joblogs.csv','RANDOM_tasklogs.csv'],['RR_joblogs.csv','RR_tasklogs.csv'],['LL_joblogs.csv','LL_tasklogs.csv']]

for f in files:
    if not os.path.isfile(f[0]) or not os.path.isfile(f[1]):
        print('Some required files are missing for visualization.\nPlease run all three algorithms before entering mode 2 or enter mode 1 for individual analysis.')
        exit()

jmeanlst = ['Mean_Jobs']
tmeanlst = ['Mean_Tasks']
jmedianlst = ['Median_Jobs']
tmedianlst = ['Median_Tasks']

for f in files:
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
    sns.set(rc={'figure.figsize':(24,12)})
    sns.heatmap(df.transpose(),cmap='Blues')
    plt.pyplot.savefig(f[1][:-4]+'.png')

# bar plot
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

