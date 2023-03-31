#from wsgiref.handlers import BaseCGIHandler
from metaflow import FlowSpec, step, card, retry
import subprocess
import os

os.environ.update({"METAFLOW_RUN_MAX_WORKERS": "4"})
dir_path = "/home/abd/Desktop/Work/Final_Version/Metaflow"
vol_path = dir_path + "/data/CMS-Analysis/vol"
shell_scripts_path = dir_path + "/code/CMS-Analysis"

recids = [24119, 24120, 19980, 19983, 19985, 19949, 19999, 19397, 19407, 19419, 19412, 20548]

#----------------------------------- Pull Images -----------------------------------
def pullCommand():
    return """
        docker pull ubuntu:latest
        docker pull cernopendata/cernopendata-client:0.3.0
        docker pull cmsopendata/cmssw_7_6_7-slc6_amd64_gcc493
        docker pull gitlab-registry.cern.ch/cms-cloud/python-vnc:latest
        """

#----------------------------------- Prepare -----------------------------------
def prepareCommand():
    return f"""
        docker run \
        --name ubuntu \
        --mount type=bind,source={dir_path},target={dir_path} \
        ubuntu:latest \
        bash {shell_scripts_path}/prepare-bash.sh {vol_path} && \
        docker stop ubuntu && \
        docker rm ubuntu
        """

#----------------------------------- Filelist -----------------------------------
def fileListCommand(recid):
    return f"""
        if ! docker stop cernopendata-client-{recid} && ! docker rm cernopendata-client-{recid}; then
            echo "some_command returned an error"
        else
            docker stop cernopendata-client-{recid} && docker rm cernopendata-client-{recid}
        fi && \
        docker run \
        --rm \
        --name cernopendata-client-{recid} \
        --mount type=bind,source={dir_path},target={dir_path} \
        cernopendata/cernopendata-client:0.3.0 \
        get-file-locations --recid {recid} --protocol xrootd > {vol_path}/files_{recid}.txt;
        """

#----------------------------------- Runpoet -----------------------------------
def runpoetCommand(nFiles, recid, nJobs):
    return f"""
        if ! docker stop cmssw-{recid} && ! docker rm cmssw-{recid}; then
            echo "some_command returned an error"
        else
            docker stop cmssw-{recid} && docker rm cmssw-{recid}
        fi && \
        docker run \
        --name cmssw-{recid} \
        --mount type=bind,source={dir_path},target={dir_path} \
        cmsopendata/cmssw_7_6_7-slc6_amd64_gcc493 \
        bash {shell_scripts_path}/runpoet-bash.sh {vol_path} {nFiles} {recid} {nJobs} && \
        docker stop cmssw-{recid} && \
        docker rm cmssw-{recid}
        """
        
#----------------------------------- Flattentrees -----------------------------------
def flattentreesCommand(recid):
    return f"""
        if ! docker stop python-{recid} && ! docker rm python-{recid}; then
            echo "some_command returned an error"
        else
            docker stop python-{recid} && docker rm python-{recid}
        fi && \
        docker run \
        -i \
        -d \
        --name python-{recid} \
        --mount type=bind,source={dir_path},target={dir_path} \
        gitlab-registry.cern.ch/cms-cloud/python-vnc && \
        docker start python-{recid} && \
        docker exec python-{recid} bash {shell_scripts_path}/flattentrees-bash.sh {vol_path} {recid} && \
        docker stop python-{recid} && \
        docker rm python-{recid}
        """

#----------------------------------- Prepare Coffea -----------------------------------
def prepareCoffeaCommand():
    return f"""
        if ! docker stop prepare-coffea && ! docker rm prepare-coffea; then
            echo "some_command returned an error"
        else
            docker stop prepare-coffea && docker rm prepare-coffea
        fi && \
        docker run \
        -i \
        -d \
        --name prepare-coffea \
        --mount type=bind,source={dir_path},target={dir_path} \
        gitlab-registry.cern.ch/cms-cloud/python-vnc && \
        docker start prepare-coffea && \
        docker exec prepare-coffea bash {shell_scripts_path}/preparecoffea-bash.sh {vol_path} && \
        docker stop prepare-coffea && \
        docker rm prepare-coffea
        """
    
#----------------------------------- Run Coffea -----------------------------------
def runCoffeaCommand():
    return f"""
        if ! docker stop run-coffea && ! docker rm run-coffea; then
            echo "some_command returned an error"
        else
            docker stop run-coffea && docker rm run-coffea
        fi && \
        docker run \
        -i \
        -d \
        --name run-coffea \
        --mount type=bind,source={dir_path},target={dir_path} \
        gitlab-registry.cern.ch/cms-cloud/python-vnc && \
        docker start run-coffea && \
        docker exec run-coffea bash {vol_path}/code/commands.sh && \
        docker stop run-coffea && \
        docker rm run-coffea
        """
        

#----------------------------------- Run Bash -----------------------------------
def run_bash(bashCommand):
    process = subprocess.Popen(bashCommand, shell=True, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
    output, error = process.communicate()
    print("The command is: \n",bashCommand)
    print("The output is: \n",output.decode())
    print("Return Code:", process.returncode)
    if process.returncode and error:
        print("The error is: \n",error.decode())


class CMS_Analysis(FlowSpec):
    
    @card
    @retry(times = 4, minutes_between_retries = 0.5)
    @step
    def start(self):
        print("Start Flow")
        self.next(self.pull_images)
    
    @card
    @retry(times = 4, minutes_between_retries = 0.5)
    @step
    def pull_images(self):
        bashCommand = pullCommand()
        run_bash(bashCommand)
        self.next(self.prepare_directory)

    @card
    @retry(times = 4, minutes_between_retries = 0.5)
    @step
    def prepare_directory(self):
        bashCommand = prepareCommand()
        run_bash(bashCommand)
        self.recids = recids
        self.next(self.file_list, foreach="recids")
    
    @card
    @retry(times = 4, minutes_between_retries = 0.5)
    @step
    def file_list(self):
        self.recid = self.input
        bashCommand = fileListCommand(self.recid)
        run_bash(bashCommand)
        self.next(self.file_list_join)

    @card
    @retry(times = 4, minutes_between_retries = 0.5)
    @step
    def file_list_join(self, inputs):        
        self.next(self.file_list_runpoet_link)
    
    @card
    @retry(times = 4, minutes_between_retries = 0.5)
    @step
    def file_list_runpoet_link(self):        
        self.recids = recids
        self.next(self.runpoet, foreach="recids")

    @card
    @retry(times = 4, minutes_between_retries = 0.5)
    @step
    def runpoet(self):
        self.recid = self.input
        bashCommand = runpoetCommand(2, self.recid, 1)
        run_bash(bashCommand)
        self.next(self.runpoet_join)
    
    @card
    @retry(times = 4, minutes_between_retries = 0.5)
    @step
    def runpoet_join(self, inputs):        
        self.next(self.runpoet_flattentrees_link)
    
    @card
    @retry(times = 4, minutes_between_retries = 0.5)
    @step
    def runpoet_flattentrees_link(self):        
        self.recids = recids
        self.next(self.flattentrees, foreach="recids")

    @card
    @retry(times = 4, minutes_between_retries = 0.5)
    @step
    def flattentrees(self):
        self.recid = self.input
        bashCommand = flattentreesCommand(self.recid)
        run_bash(bashCommand)
        self.next(self.flattentrees_join)
    
    @card
    @retry(times = 4, minutes_between_retries = 0.5)
    @step
    def flattentrees_join(self, inputs):        
        self.recids = recids
        self.next(self.preparecoffea)

    @card
    @retry(times = 4, minutes_between_retries = 0.5)
    @step
    def preparecoffea(self):
        bashCommand = prepareCoffeaCommand()
        run_bash(bashCommand)
        self.next(self.runcoffea)
    
    @card
    @retry(times = 4, minutes_between_retries = 0.5)
    @step
    def runcoffea(self):
        bashCommand = runCoffeaCommand()
        run_bash(bashCommand)
        self.next(self.end)

    @card
    @retry(times = 4, minutes_between_retries = 0.5)
    @step
    def end(self):
        print("End Flow")

if __name__ == '__main__':
    CMS_Analysis()
