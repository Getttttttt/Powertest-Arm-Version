from jtop import jtop, JtopException
import csv
import requests
import urllib.request
import json
import subprocess
import re
import time
import platform
import pyJoules
from datetime import datetime, timedelta
from pyJoules.energy_meter import measure_energy
import pandas as pd

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

def log_usage_stats(jetson, file_path):
    with open(file_path, 'w', newline='') as csvfile:
        fieldnames = ['time', 'CPU_usage', 'GPU_usage', 'RAM_usage']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        start_time = time.time()  # 记录循环开始的时间
        
        while jetson.ok():
            stats = jetson.stats
            row = {
                'time': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()),
                'CPU_usage': (stats['CPU1']+stats['CPU2']+stats['CPU3']+stats['CPU4']+stats['CPU5']+stats['CPU6']+stats['CPU7']+stats['CPU8'])/8,
                'GPU_usage': stats['GPU'],
                'RAM_usage': stats['RAM'],
            }
            writer.writerow(row)
            print(f"Logged data at {row['time']}")
            
            # 检查是否已经过了7分钟
            if time.time() - start_time >= 1.5 * 60:
                print("Time limit reached. Exiting loop.")
                break
            
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
        if model_type == 'cpu': matched_powers = 120  
        else:  matched_powers = 250
    else: 
        matched_power = matched_powers[0]
        if model_type == 'cpu':
            matched_power = matched_power.split(' ')[0]
    return matched_power

def calculate_energy(start_time,end_time):
    csv_file = './jtop_usage.csv'
    
    df = pd.read_csv(csv_file, parse_dates=['time'])
    
    start_time = datetime.fromtimestamp(start_time).strftime('%Y-%m-%d %H:%M:%S')
    end_time = datetime.fromtimestamp(end_time).strftime('%Y-%m-%d %H:%M:%S')

    
    filtered_df = df[(df['time'] >= start_time) & (df['time'] <= end_time)]
    
    cpu_mean = filtered_df['CPU_usage'].mean()
    gpu_mean = filtered_df['GPU_usage'].mean()
    ram_mean = filtered_df['RAM_usage'].mean()
    
    cpu_info = subprocess.check_output("cat /proc/cpuinfo | grep 'model name' | head -n 1", shell=True)
    cpu_model = cpu_info.decode().strip().split(":")[1].strip()
    gpu_info = subprocess.check_output("lspci | grep 'controller'", shell=True)
    gpu_model = gpu_info.decode().strip().split(":")[2].strip()
    
    cpu_power = fuzzy_search_power('cpu',cpu_model)
    gpu_power = fuzzy_search_power('gpu',gpu_model)
    
    start_time = int(datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S').timestamp())
    end_time = int(datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S').timestamp())
    
    energy = (cpu_mean / 100 * 8 * cpu_power + gpu_mean / 100 * gpu_power) * (start_time - end_time)
    
    print(f'Energy Comsumption: {energy} mu W, CPU_average_usage: {cpu_mean}%, , GPU_average_usage: {gpu_mean}%, RAM_average_usage: {ram_mean}%')
    
    return energy

def main(file_path='./jtop_usage.csv'):
    try:
        with jtop() as jetson:
            log_usage_stats(jetson, file_path)
    except JtopException as e:
        print(f"An error occurred with jtop: {e}")
    except KeyboardInterrupt:
        print("Closed with CTRL-C")
    except IOError:
        print("I/O error")

if __name__ == "__main__":
    main()
    
    end_time = int(time.time())
    start_time = end_time - 60
    
    calculate_energy(start_time, end_time)
