import pandas
import time
from datetime import datetime
import psutil
    
def get_usage():
    # Get CPU usage statistics
    core_numbers = psutil.cpu_count()
    core_usages = psutil.cpu_percent(percpu = True)
    cpu_percent = sum(core_usages)/core_numbers
    cpu_usage = {"core_numbers":core_numbers, "core_usages":core_usages, "cpu_percent":cpu_percent}
    
    # Get memory usage statistics
    mem_stats = psutil.virtual_memory()
    mem_total = mem_stats.total
    mem_used = mem_stats.used
    mem_percent = mem_stats.percent
    mem_usage = {"mem_total":mem_total, "mem_used":mem_used, "mem_percent":mem_percent}
    
    # Get disk usage statistics for the root partition
    disk_stats = psutil.disk_usage('/')
    disk_total = disk_stats.total
    disk_used = disk_stats.used
    disk_percent = disk_stats.percent
    disk_usage = {"disk_total":disk_total, "disk_used":disk_used, "disk_percent":disk_percent}
    
    # Get network usage statistics
    net_io_counters = psutil.net_io_counters()
    bytes_sent = net_io_counters.bytes_sent
    bytes_recv = net_io_counters.bytes_recv
    network_usage = {"bytes_sent":bytes_sent, "bytes_recv":bytes_recv}
    
    # Prepare resources usage
    resources_usage = {"cpu_usage":cpu_usage, "mem_usage":mem_usage, "disk_usage":disk_usage, "network_usage":network_usage}
    
    # Return resources usage
    return resources_usage

def log_usage(resources_usage):
    now = datetime.now()
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
    with open('/home/abd/Desktop/Work/Final_Version/Metaflow/data/Resources/Metaflow-CMS-Analysis-Resources.txt','a') as f:
        f.write(f"{dt_string},{resources_usage['cpu_usage']['core_numbers']},{resources_usage['cpu_usage']['core_usages'][0]},{resources_usage['cpu_usage']['core_usages'][1]},{resources_usage['cpu_usage']['core_usages'][2]},{resources_usage['cpu_usage']['core_usages'][3]},{resources_usage['cpu_usage']['cpu_percent']},{resources_usage['mem_usage']['mem_total']},{resources_usage['mem_usage']['mem_used']},{resources_usage['mem_usage']['mem_percent']},{resources_usage['disk_usage']['disk_total']},{resources_usage['disk_usage']['disk_used']},{resources_usage['disk_usage']['disk_percent']},{resources_usage['network_usage']['bytes_sent']},{resources_usage['network_usage']['bytes_recv']}\n")

def display_usage(cpu_usage,mem_usage,bars=50):
    cpu_percent = (cpu_usage/100.0)
    mem_percent = (mem_usage/100.0)
    cpu_bar = '▉' * int(cpu_percent*bars) + '-' * (bars - int(cpu_percent*bars))
    mem_bar = '▉' * int(mem_percent*bars) + '-' * (bars - int(mem_percent*bars))
    print(f"\r CPU Usage: | |{cpu_bar}| {cpu_usage:.2f}%", end ="")
    print(f" Mem Usage: | |{mem_bar}| {mem_usage:.2f}%", end="\r")

while True:
    resources_usage = get_usage()
    log_usage(resources_usage)
    display_usage(resources_usage['cpu_usage']['cpu_percent'],resources_usage['mem_usage']['mem_percent'],40)
    time.sleep(1)
