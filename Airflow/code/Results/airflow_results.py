import airflow
import psutil
from airflow.models import DagModel, DagRun, TaskInstance
import datetime
from airflow.utils.session import create_session

# Get the most recent DagRuns
dag_runs = DagRun.get_latest_runs()

for dag_run in dag_runs:
    print(dag_run.dag_id)
    #if(dag_run.state == "success"):   
    if(dag_run.state):   
        # Get the start time of the workflow
        kwtTimeDelta = datetime.timedelta(hours=3)
        kwtTZObject = datetime.timezone(kwtTimeDelta,name="KWT")
        start_time = dag_run.start_date.astimezone(kwtTZObject)
        # Get the end time of the workflow
        end_time = dag_run.end_date.astimezone(kwtTZObject)
        # Calculate the runtime of the workflow
        runtime = (end_time - start_time).total_seconds()
        print(f"Starttime: {start_time} Seconds")
        print(f"Endtime: {end_time} Seconds")
        print(f"Runtime: {runtime} Seconds")
        
        hours, remainder = divmod(runtime, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        print("Runtime: ", int(hours), ":", int(minutes),":", int(seconds), sep="")
    
        # Get the latest task instance of the workflow
        task_instances = dag_run.get_task_instances()
        # Calculate the number of tasks
        num_tasks = len(task_instances)
        print(f"Number of tasks: {num_tasks}")

        # Calculate the throughput
        throughput = num_tasks / runtime
        print(f"Throughput: {throughput} Tasks/Second")

        # Calculate the number of errors
        errors = len([task for task in task_instances if task.state == 'failed'])
        print(f"Number of errors: {errors}")

        # Calculate the number of retries
        task_retries = [task for task in task_instances if task.try_number > 2]
        retries = 0
        for task_retry in task_retries:
            retries += task_retry.try_number - 1 
        print(f"Number of retries: {retries}")
	
        with open(f'/home/abd/Desktop/Work/Final_Version/Airflow/data/Resources/Airflow-{dag_run.dag_id}-Results.txt','a') as f:
            f.write(f"{start_time}, {end_time}, {runtime}, {int(hours)}:{int(minutes)}:{int(seconds)}, {num_tasks}, {throughput}, {errors}, {retries}\n")
            
    elif(dag_run.state == "failed"):
        print(f"The latest run of the {dag_run.dag_id} DAG has failed.")
    elif(dag_run.state == "running"):
        print(f"The latest run of the {dag_run.dag_id} DAG is still running.")
    
    print("-------------------------------------------")
