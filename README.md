# YetAnotherCentralizedScheduler
Big Data Project - December 2020

### Instructions for execution:
**Files required:**  
Analysis.py  
Config.json  
Master.py  
Requests.py  
Workers.py  

1. Five terminals are needed to execute this project. We will refer to them as T1, T2, T3, T4 ad T5.

2. Open 3 terminals, one for each worker node and run the following:  
T1: `python3 Workers.py 4000 1`  
T2: `python3 Workers.py 4001 2`  
T3: `python3 Workers.py 4002 3`  

3. Run the following command on T4 to start the master node:  
`python3 Master.py Config.json <scheduling_algorithm>`  
Here, scheduling algorithm can take the following values - LL (least loaded), RANDOM (random) or RR (round robin).

4. Run the following command on T5 to send specified number of job requests to the master:  
`python3 Requests.py <number_of_requests>`  

5. Repeat steps 2 to 4 for each scheduling algorithm and run the following command on T5 to analyse the results obtained:  
`python3 Analysis.py <mode>`  
- Enter mode 'RANDOM' or 'RR' or 'LL' to analyse individual logs of the scheduling algorithm mentioned - prints mean and median times of already run scheduling algorithms on the terminal and creates a heat map depicting number of tasks running on each machine at regular time intervals.  
- Enter mode 'ALL' for visual analysis - generates a bar plot comparing the three algorithms and a heat map for each algorithm depicting number of tasks running on each machine at regular time intervals.  
**Note:** Mode 'ALL' (visual analysis) will only generate plots if all the three algorithms have been tested prior to running analysis.  
  
  
    
### Collaborators:
- Ananya V [PES101800204]
- Sakshi Shetty [PES1201800190]
- Snigdha S Chenjeri [PES1201800045]
- Swanuja Maslekar [PES1201800369]


