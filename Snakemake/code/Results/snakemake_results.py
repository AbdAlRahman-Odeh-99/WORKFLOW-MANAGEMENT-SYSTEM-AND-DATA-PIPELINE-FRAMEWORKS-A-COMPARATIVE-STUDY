import snakemake
from snakemake.utils import format

# set the path to the Snakefile and the name of the workflow
snakefile = "/home/abd/Desktop/Work/Final_Version/Snakemake/dags/BSM-Search/Snakefile"
workflow = "BSM-Search"

# create a Snakemake object for the workflow
sm = snakemake.snakemake(snakefile, workflow, dryrun=True)


# get the status of the latest run
status = sm.summary().get("status")
'''
# check if the latest run was successful
if status == "success":
    # get the latest successful run
    success = sm.get_status("success")[-1]

    # get the start and end times of the run
    start = format("{start:%Y-%m-%d %H:%M:%S}", **success)
    end = format("{end:%Y-%m-%d %H:%M:%S}", **success)

    # get the number of tasks and retries of the run
    num_tasks = success.get("stats").get("num_jobs")
    num_retries = success.get("stats").get("num_jobs_retried")

    # print the results
    print(f"Start time: {start}")
    print(f"End time: {end}")
    print(f"Number of tasks: {num_tasks}")
    print(f"Number of retries: {num_retries}")
else:
    print("No successful runs found")
'''
