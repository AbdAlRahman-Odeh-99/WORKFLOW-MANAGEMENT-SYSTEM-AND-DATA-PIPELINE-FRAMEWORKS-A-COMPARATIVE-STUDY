import os
from metaflow import FlowSpec, step, card, retry
import subprocess

os.environ.update({"METAFLOW_RUN_MAX_WORKERS": "4"})
base_dir = "/home/abd/Desktop/Work/Final_Version/Metaflow/data/BSM-Search"
code_dir = "/home/abd/Desktop/Work/Final_Version/Metaflow/code/BSM-Search"
thisroot_dir = "/home/abd/root/root/bin"

list_of_tasks = []

#----------------------------------- MC CONFIGURATIONS START -----------------------------------
mc_options =\
    {
        "mc1": { 'data_type': 'mc1', 'mcweight': '0.01875', 'nevents': '40000', 'njobs': 4 },
        "mc2": { 'data_type': 'mc2', 'mcweight': '0.0125', 'nevents': '40000', 'njobs': 4 },
        "sig" : { 'data_type': 'sig', 'mcweight': '0.0025', 'nevents': '40000', 'njobs': 2 },
        "data" : { 'data_type': 'data', 'nevents': '20000', 'njobs': 5 }
    }

select_mc_options = \
    {
        'mc' : [ 
            { 'region': 'signal', 'variation': 'shape_conv_up', 'suffix': 'shape_conv_up' },
            { 'region': 'signal', 'variation': 'shape_conv_dn', 'suffix': 'shape_conv_dn' },
            { 'region': 'signal', 'variation': 'nominal,weight_var1_up,weight_var1_dn', 'suffix': 'nominal' }
        ],
        'sig' : [
            {'region':'signal','variation':'nominal','suffix':'nominal'}
        ],
        'data': [
            { 'region': 'signal', 'variation': 'nominal', 'suffix': 'signal' },
            { 'region': 'control', 'variation': 'nominal', 'suffix': 'control' }
        ]
    }


histogram_options = \
    {
        'shape' : [ 
            { 'variations' : 'nominal' , 'shapevar': 'shape_conv_up' },
            { 'variations' : 'nominal' , 'shapevar': 'shape_conv_dn' }
        ],
        'mc1': {'variations' : 'nominal,weight_var1_up,weight_var1_dn', 'shapevar': 'nominal'},
        'mc2': {'variations' : 'nominal,weight_var1_up,weight_var1_dn', 'shapevar': 'nominal'},
        'sig': {'variations' : 'nominal', 'shapevar': 'nominal'},
        'data' : [
            { 'variations' : 'nominal', 'shapevar': 'nominal', 'parent_data_type':'data', 'sub_data_type': 'signal', 'result':'data', 'weight': 1.0 },
            { 'variations' : 'nominal', 'shapevar': 'nominal', 'parent_data_type':'data', 'sub_data_type': 'control', 'result': 'qcd', 'weight': 0.1875 }
        ]
    }

#----------------------------------- MC CONFIGURATIONS END -----------------------------------


#----------------------------------- DATA CONFIGURATIONS START ----------------------------------- 
hist_weight_data_options = \
    {
        'data': { 'variations' : 'nominal', 'shapevar': 'nominal', 'parent_data_type':'data', 'sub_data_type': 'signal', 'result':'data', 'weight': 1.0 },
        'qcd': { 'variations' : 'nominal', 'shapevar': 'nominal', 'parent_data_type':'data', 'sub_data_type': 'control', 'result': 'qcd', 'weight': 0.1875 }
    }
#----------------------------------- DATA CONFIGURATIONS END ----------------------------------- 


plot_outputs = [
    base_dir + "/nominal_vals.yml",
    base_dir + "/fit_results.yml",
    base_dir + "/prefit.pdf",
    base_dir + "/postfit.pdf"
]

#----------------------------------- Prepare Dir Operation Start -----------------------------------
def generatePrepareCommand():
    return f"""
        rm -rf {base_dir}
        mkdir -p {base_dir}
        """
#----------------------------------- Prepare Dir Operation End -----------------------------------

#----------------------------------- Scatter Operation Start -----------------------------------
def scatter(option):
        import json
        data_type = option['data_type']
        output_file = base_dir+"/"+data_type+".json"
        json_object = { data_type:[i+1 for i in range(option['njobs'])]}
        with open(output_file,'w') as outfile:
            json.dump(json_object,outfile)
#----------------------------------- Scatter Operation End -----------------------------------

#----------------------------------- Generate Operation Start -----------------------------------
def generate_data_generation(option, job_number):
    data_type = option['data_type']
    output_file =  base_dir + "/" + data_type + "_" + str(job_number) + ".root"
    return {
        'option':option,
        'jobnumber':str(job_number), 
        'output_file':output_file
    }

def generate_GenerateCommand(data):
    return f"""
        
        source {thisroot_dir}/thisroot.sh
        pwd
        python {code_dir}/generatetuple.py {data['option']['data_type']} {data['option']['nevents']} {data['output_file']}
    """
#----------------------------------- Generate Operation End -----------------------------------

#----------------------------------- Merge Root Operation Start -----------------------------------
def merge_root_data_generation(option):
    data_type = option['data_type']
    njobs = option['njobs']
    output_file = base_dir + '/' + data_type + '.root'
    input_files = ''
    for i in range (1,njobs+1):
        input_files += ' ' + base_dir + '/' + data_type + '_' + str(i) + '.root'
    return {
        'output_file':output_file, 
        'input_files':input_files
    }

def merge_root_GenerateCommand(data):
    return f"""

        source {thisroot_dir}/thisroot.sh
        hadd -f {data['output_file']} {data['input_files']}
        """
#----------------------------------- Merge Root Operation End -----------------------------------

#----------------------------------- Select Operation Start -----------------------------------
def select_data_genertion(option, select_option):
    data_type = option['data_type']
    suffix = select_option['suffix']
    region =  select_option['region']
    variation = select_option['variation']
    return{
        'input_file': base_dir + '/' + data_type + '.root',
        'output_file': base_dir + '/' + data_type+'_'+suffix+'.root',
        'region': region,
        'variation': variation
    }

def select_GenerateCommand(data):
    return f"""
        
            source {thisroot_dir}/thisroot.sh        
            python {code_dir}/select.py {data['input_file']} {data['output_file']} {data['region']} {data['variation']}
        """
#----------------------------------- Select Operation End -----------------------------------

#----------------------------------- Hist Shape Operation Start -----------------------------------
def hist_shape_data_genertion(option, shapevar, variations):
    data_type = option['data_type']
    return {
        'input_file': base_dir + '/' + data_type + '_' + shapevar + '.root',
        'output_file': base_dir + '/' + data_type+'_'+shapevar+'_hist.root',
        'option':option,
        'shapevar':shapevar,
        'variations':variations,
        "name":data_type+"_"+shapevar
        }

def hist_shape_GenerateCommand(data):
    return f"""
        
        source {thisroot_dir}/thisroot.sh        
        python {code_dir}/histogram.py {data['input_file']} {data['output_file']} {data['option']['data_type']} {data['option']['mcweight']} {data['variations']} {data['name']}
        """
#----------------------------------- Hist Shape Operation End -----------------------------------

#----------------------------------- Hist Weight Operation Start -----------------------------------
def hist_weight_data_genertion(option, shapevar, variations, hist_weight_data_options = None):
    data_type = option['data_type']
    weight = None
    input_file = ''
    output_file = data_type+'_hist.root'
    if('mc' in data_type or 'sig' in data_type):
        input_file = data_type+'_'+shapevar+'.root'
        output_file = data_type+'_'+shapevar+'_hist.root'
        weight = option['mcweight']
    elif ('data' in data_type and hist_weight_data_options != None):
        input_file = data_type+'_'+hist_weight_data_options['sub_data_type']+'.root'
        output_file = hist_weight_data_options['result']+'_hist.root'
        weight = hist_weight_data_options['weight']
        if('control' in hist_weight_data_options['sub_data_type']):
            data_type = hist_weight_data_options['result']
    if('sig' in data_type):
        data_type = data_type+'nal'
    return {
        'input_file': base_dir + '/' + input_file,
        'output_file': base_dir + '/' + output_file,
        'option':option,
        'weight':weight,
        'variations':variations,
        'name':data_type
        }

def hist_weight_GenerateCommand(data):
    return f"""
        source {thisroot_dir}/thisroot.sh        
        python {code_dir}/histogram.py {data['input_file']} {data['output_file']} {data['name']} {data['weight']} {data['variations']}
    """
#----------------------------------- Hist Weight Operation End -----------------------------------

#----------------------------------- Merge Explicit Operation Start -----------------------------------
def merge_explicit_data_genertion(option = None, operation = None):
    if (option == None and operation == None) :
        input_files = base_dir + '/' + 'mc1_merged_hist.root ' + \
                      base_dir + '/' + 'mc2_merged_hist.root ' + \
                      base_dir + '/' + 'sig_merged_hist.root ' + \
                      base_dir + '/' + 'data_merged_hist.root'
        output_file = "all_merged_hist.root"
        option = 'all'
        return{
        'input_files': input_files,
        'output_file': base_dir + "/" + output_file,
        }
    else:
        data_type = option['data_type']
        input_files = ''
        output_file = data_type+'_merged_hist.root'

        if('mc' in data_type):
            if('merge_hist_shape' in operation):
                input_files = base_dir + '/' + data_type + '_shape_conv_up_hist.root ' + \
                            base_dir + '/' + data_type +'_shape_conv_dn_hist.root'
                output_file = data_type+'_shape_hist.root'
            elif('merge_hist_all' in operation):
                input_files = base_dir + '/' + data_type + '_nominal_hist.root ' + \
                            base_dir + '/' + data_type + '_shape_hist.root'
        elif('sig' in data_type):
            input_files = base_dir + '/' + data_type + '_nominal_hist.root'
        elif('data' in data_type):
            input_files = base_dir + '/' + data_type + '_hist.root '+ base_dir+'/qcd_hist.root'
            
        return{
            'input_files': input_files,
            'output_file': base_dir + "/" + output_file,
        }

def merge_explicit_GenerateCommand(data):
    return f"""
        source {thisroot_dir}/thisroot.sh        
        hadd -f {data['output_file']} {data['input_files']}
    """
#----------------------------------- Merge Explicit Operation End -----------------------------------

#----------------------------------- Makews Operation Start -----------------------------------
def makews_data_generation(data_bkg_hists,workspace_prefix,xml_dir):
    return {
        'data_bkg_hists':data_bkg_hists,
        'workspace_prefix':workspace_prefix,
        'xml_dir':xml_dir
    }

def makews_GenerateCommand(data):
    return f"""
        source {thisroot_dir}/thisroot.sh
        python {code_dir}/makews.py {data['data_bkg_hists']} {data['workspace_prefix']} {data['xml_dir']}
    """
#----------------------------------- Makews Operation End -----------------------------------

#----------------------------------- Plot Operation Start -----------------------------------
def plot_data_generation(combined_model, nominal_vals, fit_results, prefit_plot, postfit_plot):
    return {
        'combined_model':combined_model,
        'nominal_vals':nominal_vals,
        'fit_results':fit_results,
        'prefit_plot':prefit_plot,
        'postfit_plot':postfit_plot
        }

def plot_GenerateCommand(data):
    return f"""
        source {thisroot_dir}/thisroot.sh
        hfquickplot write-vardef {data['combined_model']} combined {data['nominal_vals']}
        hfquickplot plot-channel {data['combined_model']} combined channel1 x {data['nominal_vals']} -c qcd,mc2,mc1,signal -o {data['prefit_plot']}
        hfquickplot fit {data['combined_model']} combined {data['fit_results']}
        hfquickplot plot-channel {data['combined_model']} combined channel1 x {data['fit_results']} -c qcd,mc2,mc1,signal -o {data['postfit_plot']}
	"""
#----------------------------------- Plot Operation End -----------------------------------

#----------------------------------- Run Command Start -----------------------------------
def run_bash(bashCommand):
    process = subprocess.Popen(bashCommand, shell=True, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
    output, error = process.communicate()
    print("The command is: \n",bashCommand)
    print("The output is: \n",output.decode())
    print("Return Code:", process.returncode)
    if process.returncode and error:
        print("The error is: \n",error.decode())
#----------------------------------- Run Command End -----------------------------------

class BSM_Search(FlowSpec):
    
    @card
    @retry(times = 4, minutes_between_retries = 0.5)
    @step
    def start(self):
        print("Start Flow")
        self.next(self.prepare_directory)

    @card
    @retry(times = 4, minutes_between_retries = 0.5)
    @step
    def prepare_directory(self):
        bashCommand = generatePrepareCommand()
        run_bash(bashCommand)
        self.options = []
        for key in mc_options.keys():
            self.options.append(key)
        self.next(self.scatter_operation, foreach="options")
    
    @card
    @retry(times = 4, minutes_between_retries = 0.5)
    @step
    def scatter_operation(self):
        self.option = mc_options[self.input]
        scatter(self.option)
        self.jobs = []
        for i in range (1,self.option['njobs']+1):
            self.jobs.append(str(i))
        self.next(self.generate_operation, foreach="jobs")

    @card
    @retry(times = 4, minutes_between_retries = 0.5)
    @step
    def generate_operation(self):
        option = self.option
        jobnumber = self.input
        data = generate_data_generation(option, jobnumber)
        bashCommand = generate_GenerateCommand(data)
        run_bash(bashCommand)
        self.next(self.merge_root_operation)

    @card
    @retry(times = 4, minutes_between_retries = 0.5)
    @step
    def merge_root_operation(self,inputs):        
        self.merge_artifacts(inputs)
        option = self.option
        data = merge_root_data_generation(option)
        bashCommand = merge_root_GenerateCommand(data)
        run_bash(bashCommand)
        self.next(self.merge_and_select_link)

    @card
    @retry(times = 4, minutes_between_retries = 0.5)
    @step
    def merge_and_select_link(self):        
        option = self.option
        if(option['data_type'][2].isdigit()):
            data_type = 'mc'
        else:
            data_type = option['data_type']

        self.select_options = select_mc_options[data_type]
        self.next(self.select_operation, foreach="select_options")

    @card
    @retry(times = 4, minutes_between_retries = 0.5)
    @step
    def select_operation(self):        
        option = self.option
        select_option = self.input
        data_type = option['data_type']
        data = select_data_genertion(option, select_option)
        bashCommand = select_GenerateCommand(data)
        run_bash(bashCommand)
        self.next(self.join_select)
        
    @card
    @retry(times = 4, minutes_between_retries = 0.5)
    @step
    def join_select(self,inputs):
        self.merge_artifacts(inputs)
        self.next(self.select_and_hist_link)

    @card   
    @retry(times = 4, minutes_between_retries = 0.5)
    @step
    def select_and_hist_link(self):        
        option = self.option
        data_type = option['data_type']
        self.hist_options = []        
        if('data' in data_type):
            self.hist_options += histogram_options[data_type]
        else:
            self.hist_options.append(histogram_options[data_type])

        if('mc' in data_type):
            self.hist_options += histogram_options['shape']

        self.next(self.hist_operation, foreach='hist_options')
        
    @card
    @retry(times = 4, minutes_between_retries = 0.5)
    @step
    def hist_operation(self):        
        option = self.option
        data_type = option['data_type']
        hist_option = self.input
        shapevar = hist_option['shapevar']
        variations = hist_option['variations']
        bashCommand = ''
        if(shapevar in ['shape_conv_up', 'shape_conv_dn']):
            data = hist_shape_data_genertion(self.option, shapevar, variations)
            bashCommand = hist_shape_GenerateCommand(data)
        else:
            if('data' in data_type):
                data = hist_weight_data_genertion(self.option, shapevar, variations, hist_option)
            else:
                data = hist_weight_data_genertion(self.option, shapevar, variations)
            
            bashCommand = hist_weight_GenerateCommand(data)

        run_bash(bashCommand)
        self.next(self.join_hists)
    
    @card
    @retry(times = 4, minutes_between_retries = 0.5)
    @step
    def join_hists(self,inputs):
        self.merge_artifacts(inputs)
        option = self.option

        if('mc' in option['data_type']):
            data = merge_explicit_data_genertion(self.option, 'merge_hist_shape')
            bashCommand = merge_explicit_GenerateCommand(data)
            run_bash(bashCommand)
        
        data = merge_explicit_data_genertion(self.option, 'merge_hist_all')
        bashCommand = merge_explicit_GenerateCommand(data)
        run_bash(bashCommand)
        self.next(self.final_join)

    @card
    @retry(times = 4, minutes_between_retries = 0.5)
    @step
    def final_join(self, inputs):
        self.next(self.merge_hists)

    @card
    @retry(times = 4, minutes_between_retries = 0.5)
    @step
    def merge_hists(self):
        data = merge_explicit_data_genertion()
        bashCommand = merge_explicit_GenerateCommand(data)
        run_bash(bashCommand)
        self.next(self.makews)

    @card
    @retry(times = 4, minutes_between_retries = 0.5)
    @step
    def makews(self):
        data_bkg_hists = base_dir + "/all_merged_hist.root"
        workspace_prefix = base_dir + "/results"
        xml_dir = base_dir + "/xmldir"
        data = makews_data_generation(data_bkg_hists, workspace_prefix, xml_dir)
        bashCommand = makews_GenerateCommand(data)
        run_bash(bashCommand)
        self.next(self.plot)

    @card
    @retry(times = 4, minutes_between_retries = 0.5)
    @step
    def plot(self):
        combined_model = base_dir + '/results_combined_meas_model.root'
        nominal_vals = base_dir + "/nominal_vals.yml"
        fit_results = base_dir + "/fit_results.yml"
        prefit_plot = base_dir + "/prefit.pdf"
        postfit_plot = base_dir + "/postfit.pdf"
        data = plot_data_generation(combined_model, nominal_vals, fit_results, prefit_plot, postfit_plot)
        bashCommand = plot_GenerateCommand(data)
        run_bash(bashCommand)
        self.next(self.end)

        
    @card
    @retry(times = 4, minutes_between_retries = 0.5)
    @step
    def end(self):
        print("End Flow")

if __name__ == '__main__':
    BSM_Search()
