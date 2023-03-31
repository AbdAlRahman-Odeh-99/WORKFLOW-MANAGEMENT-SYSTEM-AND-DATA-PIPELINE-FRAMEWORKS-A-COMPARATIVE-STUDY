from metaflow import Metaflow, Flow

# initialize the Metaflow client
metaflow = Metaflow()
print(metaflow.flows)

# get the latest successful run of the workflow
flow_name = 'CMS_Analysis'
flow = Flow(flow_name)
latest_run = flow.latest_successful_run

# get the start and end time of the latest successful run
start_time = latest_run.start_time
end_time = latest_run.end_time

print(f"Latest successful run of {flow_name} started at {start_time} and ended at {end_time}.")