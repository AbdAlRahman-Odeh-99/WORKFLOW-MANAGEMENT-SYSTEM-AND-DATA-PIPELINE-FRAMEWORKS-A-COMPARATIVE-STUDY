import luigi
from luigi.task_history import TaskHistory

# Set the name of the DAG that you want to get the metrics for
dag_name = "MyDag"

# Create a TaskHistory object for the DAG
task_history = TaskHistory(config=luigi.configuration.get_config(), dag_id=dag_name)

# Get the latest run of the DAG
latest_run_id = task_history.get_latest_run_id()

if latest_run_id is None:
    print(f"No successful runs of DAG {dag_name} found.")
    exit()

# Get the run result for the latest run of the DAG
run_result = task_history.get_summary(latest_run_id)

# Print the metrics
print(f"Start time: {run_result.start_time}")
print(f"End time: {run_result.end_time}")
print(f"Number of tasks: {run_result.task_count}")
print(f"Number of errors: {run_result.failed_task_count}")
print(f"Number of retries: {run_result.retry_count}")
