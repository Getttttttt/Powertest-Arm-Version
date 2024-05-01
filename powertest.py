import requests
import urllib.request
import json
import subprocess
import re
import time
import platform
import pyJoules
import csv
from datetime import datetime, timedelta
from pyJoules.energy_meter import measure_energy
# from prometheus_api_client import PrometheusConnect

def getTargetsStatus(address):
    print("\n\n")
    url = address + '/api/v1/targets'
    response = requests.request('GET', url)
    if response.status_code == 200:
        targets = response.json()['data']['activeTargets']
        aliveNum, totalNum = 0, 0
        downList = []
        for target in targets:
            totalNum += 1
            if target['health'] == 'up':
                aliveNum += 1
            else:
                downList.append(target['labels']['instance'])
        print('-----------------------TargetsStatus--------------------------')
        print(str(aliveNum) + ' in ' + str(totalNum) + ' Targets are alive !!!')
        print('--------------------------------------------------------------')
        for down in downList:
            print('\033[31m\033[1m' + down + '\033[0m' + ' down !!!')
        print('-----------------------TargetsStatus--------------------------')
    else:
        print('\033[31m\033[1m' + 'Get targets status failed!' + '\033[0m')
    print()


def get_system_info():
    # 获取操作系统名称和版本号
    os_name = platform.system()
    os_version = platform.release()

    # 获取计算机的网络名称
    node_name = platform.node()

    # 获取计算机的处理器信息
    processor = platform.processor()

    # 获取计算机的架构信息
    machine = platform.machine()

    # 获取计算机的平台信息
    platform_name = platform.platform()

    # 获取计算机的完整信息
    system_info = platform.uname()
    
    print("\n\n")
    '''print("Operating System Name:", os_name)
    print("Operating System Version:", os_version)
    print("Computer Network Name: rann-ai-server:", node_name)
    print("Processor Information: x86_64:", processor)
    print("Architecture Information:", machine)
    print("Platform Information:", platform_name)
    print("Complete System Information:", system_info)'''
    print("Operating System Name:".ljust(30), os_name)
    print("Operating System Version:".ljust(30), os_version)
    print("Computer Network Name:".ljust(30), node_name)
    print("Processor Information:".ljust(30), processor)
    print("Architecture Information:".ljust(30), machine)
    print("Platform Information:".ljust(30), platform_name)
    print("Complete System Information:".ljust(30), system_info)
    print("\n")
    cpu_info = subprocess.check_output("cat /proc/cpuinfo | grep 'model name' | head -n 1", shell=True)
    cpu_model = cpu_info.decode().strip().split(":")[1].strip()
    gpu_info = subprocess.check_output("lspci | grep 'VGA compatible controller'", shell=True)
    gpu_model = gpu_info.decode().strip().split(":")[2].strip()
    print("CPU Model:", cpu_model)
    print("GPU Model:", gpu_model)
    
    with open('usage_data.csv', 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
    # Writing system and hardware info
        writer.writerow(["Operating System Name", os_name])
        writer.writerow(["Operating System Version", os_version])
        writer.writerow(["Computer Network Name", node_name])
        writer.writerow(["Processor Information", processor])
        writer.writerow(["Architecture Information", machine])
        writer.writerow(["Platform Information", platform_name])
        writer.writerow(["Complete System Information", str(system_info)])
        writer.writerow(["CPU Model", cpu_model])
        writer.writerow(["GPU Model", gpu_model])


def queryUsage(address, expr, start_time, end_time):
    url = address + '/api/v1/query?query=' + expr
    params = {
        'query': expr,
        'start': start_time,
        'end': end_time,
        'step': '1m'  # 时间间隔，可以根据需要进行调整
    }
    try:
        # return json.loads(requests.get(url=url).content.decode('utf8', 'ignore'))
        response = requests.get(url=url, params=params)
        data = json.loads(response.content.decode('utf8', 'ignore'))
        return data
    except Exception as e:
        print(e)
        return {}


def query_CPU_Average_Usage(address, start_time, end_time):
    # query_expression = '100 - (avg by (instance) (irate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)'
    query_expression = '100 - (avg by (instance) (irate(node_cpu_seconds_total{{mode="idle"}}[{}s]))) * 100'.format(end_time - start_time)
    
    result = queryUsage(prometheus_server_address, query_expression, start_time, end_time)
    # 处理结果
    if result:
       cpu_usages = []
       for result_data in result['data']['result']:
           metric = result_data['metric']
           values = result_data['value']
           instance = metric['instance']
           # print(result_data.keys())
           average_usage = float(values[1])
           cpu_usages.append((instance, average_usage))

       print("查询结果：")
       for instance, usage in cpu_usages:
           print(f"实例: {instance}, 平均CPU使用率: {usage}%")
           
       '''with open('cpu_usage.csv', 'w', newline='') as csvfile:
           writer = csv.writer(csvfile)
           # 写入表头
           writer.writerow(["Instance", "Average CPU Usage"])
           # 写入数据
           for instance, usage in cpu_usages:
               writer.writerow([instance, usage])'''
       
    else:
        print("查询失败或返回为空字典。")
    print()
        

def query_RAM_Average_Usage(address, start_time, end_time):
    query_expression = '(avg by (instance) (irate(node_memory_MemAvailable_bytes[{}s]))) / (avg by (instance) (node_memory_MemTotal_bytes)) * 100'.format(end_time - start_time)
    result = queryUsage(prometheus_server_address, query_expression, start_time, end_time)
    # 处理结果
    if result:
       cpu_usages = []
       for result_data in result['data']['result']:
           metric = result_data['metric']
           values = result_data['value']
           instance = metric['instance']
           # print(result_data.keys())
           average_usage = float(values[1])
           cpu_usages.append((instance, average_usage))
       # print(result)
       print("查询结果：")
       for instance, usage in cpu_usages:
           print(f"实例: {instance}, 平均RAM使用率: {usage}%")
    else:
        print("查询失败或返回为空字典。")
    print()


def query_GPU_Average_Usage(address, start_time, end_time):
    # query_expression = 'avg_over_time(nvidia_gpu_utilization{{job="nvidia_gpu_exporter"}}[{}s])'.format(end_time - start_time)
    query_expression = 'avg_over_time(nvidia_smi_utilization_gpu_ratio{{job="nvidia_gpu_exporter"}}[{}s])'.format(end_time - start_time)
    result = queryUsage(prometheus_server_address, query_expression, start_time, end_time)
    # 处理结果
    if result:
       cpu_usages = []
       for result_data in result['data']['result']:
           metric = result_data['metric']
           values = result_data['value']
           instance = metric['instance']
           # print(result_data.keys())
           average_usage = float(values[1])
           cpu_usages.append((instance, average_usage))
       # print(result)
       print("查询结果：")
       for instance, usage in cpu_usages:
           print(f"实例: {instance}, 平均GPU使用率: {usage}%")
    else:
        print("查询失败或返回为空字典。")
    print()

def fuzzy_search_power(model_type ,model_name ):
    if model_type == 'cpu':
        file_path = './CPUPowerDict.csv'
    else:file_path = './GPUPowerDict.csv'
    matched_powers = []  # 存储匹配到的功率值
    # 将输入的cpu_model字符串转换为一个用于模糊匹配的正则表达式模式
    # 为了提高匹配的灵活性，词之间添加.*匹配任意字符
    pattern = '.*'.join(map(re.escape, model_name.split()))

    with open(file_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            # 使用正则表达式模糊匹配Name列
            if re.search(pattern, row['Name'], re.IGNORECASE):
                # 如果找到匹配，将功率值添加到列表中
                matched_powers.append(row['power(W)'])
    if len(matched_powers) == 0:
        if model_type == 'cpu': matched_power = 120  
        else:  matched_power = 250
    else: 
        matched_power = matched_powers[0]
        if model_type == 'cpu':
            matched_power = matched_power.split(' ')[0]
    return matched_power
    
def query_total_energy(prometheus_server_address, start_time, end_time):
    query_expression1 = '100 - (avg by (instance) (irate(node_cpu_seconds_total{{mode="idle"}}[{}s]))) * 100'.format(end_time - start_time)
    # query_expression1 = '(1 - sum(rate(node_cpu_seconds_total{job="node_exporter",mode="idle"}[{}s])) by (instance) / sum(rate(node_cpu_seconds_total{job="node_exporter"}[{}s])) by (instance))'.format(end_time - start_time)
    result1 = queryUsage(prometheus_server_address, query_expression1, start_time, end_time)
    
    query_expression2 = '(avg by (instance) (irate(node_memory_MemAvailable_bytes[{}s]))) / (avg by (instance) (node_memory_MemTotal_bytes)) * 100'.format(end_time - start_time)
    # query_expression2 = avg_over_time(1 - (node_memory_Buffers_bytes{job="node_exporter"} + node_memory_Cached_bytes{job="node_exporter"} + node_memory_MemFree_bytes{job="node_exporter"}) / node_memory_MemTotal_bytes{job="node_exporter"} [end_time - start_time])

    result2 = queryUsage(prometheus_server_address, query_expression2, start_time, end_time)
    
    query_expression3 = 'avg_over_time(nvidia_smi_utilization_gpu_ratio{{job="nvidia_gpu_exporter"}}[{}s])'.format(end_time - start_time)
    result3 = queryUsage(prometheus_server_address, query_expression3, start_time, end_time)
    
    if result1 and result2 and result3:
       cpu_usages = []
       for result_data1 in result1['data']['result']:
           metric1 = result_data1['metric']
           values1 = result_data1['value']
           instance1 = metric1['instance']
           # print(result_data.keys())
           average_usage1 = float(values1[1])
           cpu_usages.append((instance1, average_usage1))

       print("Query Result：")
       usage_cpu = 0
       i = 0
       for instance, usage in cpu_usages:
           print(f"Instance: {instance}, Average CPU Usage: {usage}%")
           usage_cpu += usage
           i += 1
       usage_cpu /= i
       
       ram_usages = []
       for result_data2 in result2['data']['result']:
           metric2 = result_data2['metric']
           values2 = result_data2['value']
           instance2 = metric2['instance']
           # print(result_data.keys())
           average_usage2 = float(values2[1])
           ram_usages.append((instance2, average_usage2))
       # print(result)
       print("Query Result：")
       usage_ram = 0
       i = 0
       for instance, usage in ram_usages:
           print(f"Instance: {instance}, Average RAM Usage: {usage}%")
           usage_ram += usage
           i += 1
       usage_ram /= i
           
       gpu_usages = []
       for result_data3 in result3['data']['result']:
           metric3 = result_data3['metric']
           values3 = result_data3['value']
           instance3 = metric3['instance']
           # print(result_data.keys())
           average_usage3 = float(values3[1])
           gpu_usages.append((instance3, average_usage3))
       # print(result)
       print("Query Result：")
       usage_gpu = 0
       for instance, usage in gpu_usages:
           print(f"Instance: {instance}, Average GPU Usage: {usage*100}%")
           usage_gpu += usage*100
       
       cpu_info = subprocess.check_output("cat /proc/cpuinfo | grep 'model name' | head -n 1", shell=True)
       cpu_model = cpu_info.decode().strip().split(":")[1].strip()
       gpu_info = subprocess.check_output("lspci | grep 'VGA compatible controller'", shell=True)
       gpu_model = gpu_info.decode().strip().split(":")[2].strip()
       
       cpu_power = fuzzy_search_power('cpu',cpu_model)
       gpu_power = fuzzy_search_power('gpu',gpu_model)
       
       print("\n")
       ans = (cpu_power*usage_cpu + gpu_power*usage_gpu) / 100 * (end_time-start_time) / 3600
       print(f"Estimated power consumption by CPU+GPU：{ans}Wh")
       print(f"After conversion：{ans*3600000}uJ")
       print(f"Estimated power consumption by CPU：{cpu_power*10*usage_cpu*(end_time-start_time)}uJ")
       print(f"Estimated power consumption by GPU：{gpu_power*10*usage_gpu*(end_time-start_time)}uJ")
       print("\n\n")
    else:
        print("The query failed or an empty dictionary was returned.")
    
    # Now, let's write this combined data to a CSV file
    with open('usage_data.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
    
    # Write headers and CPU usages
        writer.writerow(["Instance", "Resource Type", "Average Usage (%)"])
        for instance, usage in cpu_usages:
            writer.writerow([instance, "CPU", usage])
    
    # Append RAM usages
        for instance, usage in ram_usages:
            writer.writerow([instance, "RAM", usage])
    
    # Append GPU usages
        for instance, usage in gpu_usages:
            writer.writerow([instance, "GPU", usage * 100])


def measure_total_energy(func):
    def wrapper(*args, **kwargs):
        
        prometheus_server_address = 'http://localhost:9090'
        
        start_time = int(time.time())
        func(*args, **kwargs)
        end_time = int(time.time())
        
        query_expression1 = '100 - (avg by (instance) (irate(node_cpu_seconds_total{{mode="idle"}}[{}s]))) * 100'.format(end_time - start_time)
        result1 = queryUsage(prometheus_server_address, query_expression1, start_time, end_time)
    
        query_expression2 = '(avg by (instance) (irate(node_memory_MemAvailable_bytes[{}s]))) / (avg by (instance) (node_memory_MemTotal_bytes)) * 100'.format(end_time - start_time)
        result2 = queryUsage(prometheus_server_address, query_expression2, start_time, end_time)
    
        query_expression3 = 'avg_over_time(nvidia_smi_utilization_gpu_ratio{{job="nvidia_gpu_exporter"}}[{}s])'.format(end_time - start_time)
        result3 = queryUsage(prometheus_server_address, query_expression3, start_time, end_time)
    
        if result1 and result2 and result3:
           cpu_usages = []
           for result_data1 in result1['data']['result']:
               metric1 = result_data1['metric']
               values1 = result_data1['value']
               instance1 = metric1['instance']
               # print(result_data.keys())
               average_usage1 = float(values1[1])
               cpu_usages.append((instance1, average_usage1))
           print("Query Result：")
           usage_cpu = 0
           i = 0
           for instance, usage in cpu_usages:
               print(f"Instance: {instance}, Average CPU Usage: {usage}%")
               usage_cpu += usage
               i += 1
           usage_cpu /= i
       
           ram_usages = []
           for result_data2 in result2['data']['result']:
               metric2 = result_data2['metric']
               values2 = result_data2['value']
               instance2 = metric2['instance']
               # print(result_data.keys())
               average_usage2 = float(values2[1])
               ram_usages.append((instance2, average_usage2))
           # print(result)
           print("Query Result：")
           usage_ram = 0
           i = 0
           for instance, usage in ram_usages:
               print(f"Instance: {instance}, Average RAM Usage: {usage}%")
               usage_ram += usage
               i += 1
           usage_ram /= i
           
           gpu_usages = []
           for result_data3 in result3['data']['result']:
               metric3 = result_data3['metric']
               values3 = result_data3['value']
               instance3 = metric3['instance']
               # print(result_data.keys())
               average_usage3 = float(values3[1])
               gpu_usages.append((instance3, average_usage3))
           # print(result)
           print("Query Result：")
           usage_gpu = 0
           for instance, usage in gpu_usages:
               print(f"Instance: {instance}, Average GPU Usage: {usage*100}%")
               usage_gpu += usage*100
       
           print("\n")
           ans = (120*usage_cpu + 250*usage_gpu) / 100 * (end_time-start_time) / 3600
           print(f"Estimated power consumption by CPU+GPU：{ans}Wh")
           print(f"After conversion：{ans*3600000}uJ")
           print(f"Estimated power consumption by CPU：{1200*usage_cpu*(end_time-start_time)}uJ")
           print(f"Estimated power consumption by GPU：{2500*usage_gpu*(end_time-start_time)}uJ")
           print("\n\n")
        else:
            print("The query failed or an empty dictionary was returned.")

    return wrapper


get_system_info()

# 设置Prometheus服务器的IP地址
prometheus_server_address = 'http://localhost:9090'

# 调用函数检测目标状态
getTargetsStatus(prometheus_server_address)

# 获取最近5分钟的时间范围
# end_time = datetime.now().isoformat()
# start_time = (datetime.now() - timedelta(minutes=5)).isoformat()

end_time = int(time.time())
start_time = end_time - 300

# query_CPU_Average_Usage(prometheus_server_address, start_time, end_time)
# query_RAM_Average_Usage(prometheus_server_address, start_time, end_time)
# query_GPU_Average_Usage(prometheus_server_address, start_time, end_time)
query_total_energy(prometheus_server_address, start_time, end_time)

'''@measure_energy
def foo():
    # start_time = int(time.time())
    # func
    # end_time = int(time.time())
    query_total_energy(prometheus_server_address, start_time, end_time)

foo()'''
