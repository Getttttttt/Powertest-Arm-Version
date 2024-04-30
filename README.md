# Powertest

## 2024.04.29 Update for mapping type of CPU or GPU

This repo is appliable for x86, if you are searching for the arm test version, you could click link here[] to access Arm version.

The previous version is here[https://github.com/Zhou1993napolun/Powertest].

## What is Powertest for？

We need to detect the utilization rate of CPU, GPU and RAM, and then calculate the energy consumption of the device according to the relevant formula, which can be used for the detection of the model.
However, because different tools detect different information, such as Prometheus can read the CPU and RAM information, but not directly read the GPU, while PyJoules can configure the relevant nodes to monitor the GPU, we designed a tool that combines the above metrics to monitor various data in real time. The energy consumption was calculated and visualized using Grafana.

## Introduction to Prometheus and Grafana

### Prometheus

[Prometheus](https://prometheus.io/) is an open-source monitoring and alerting toolkit that focuses on reliability and scalability. Originally built by SoundCloud in 2012, Prometheus has since become a project under the Cloud Native Computing Foundation (CNCF). Key features include:

- **Multi-dimensional Data Model:** Uses key-value pairs for data representation, enabling flexible and accurate querying.
- **PromQL:** A powerful query language that allows users to aggregate and select time series data in real time.
- **Distributed and Decentralized:** Each instance operates independently, but can also be part of a larger setup.
- **Pull-based Model:** Scrapes metrics from instrumented jobs, either directly or via an intermediary push gateway.

### Grafana

[Grafana](https://grafana.com/) is an open-source platform known for its robust visualization capabilities. It's designed to provide a comprehensive set of tools to visualize, alert on, and understand metrics stored in a variety of data sources. Key features include:

- **Rich Visualizations:** Offers a wide range of visualization options from charts to geospatial information and logs.
- **Extensibility:** Supports a broad array of plugins, both for data sources and panels.
- **Integrated Alerting:** Built-in alerting suite that allows for attaching conditions to dashboard panels.

### Relationship between Prometheus and Grafana

Prometheus and Grafana complement each other in a monitoring stack:

- **Data Collection & Storage:** Prometheus is responsible for collecting and storing metrics.
- **Visualization & Alerting:** Grafana taps into Prometheus as a data source, enabling detailed visualizations, dashboards, and alerts.

Together, they provide a comprehensive solution for monitoring and observing application performance, system health, and more.

## Before we start(In our project)

We have four main devices, NUC1, NUC2, Xavier and AI Server. NUC1, NUC2, and AI Server are amd64, and Xavier is arm64. In terms of Gpus NUC1 and NUC2 are Intel and Xavier and AI Server are Nvidia, the information of these devices can be read and displayed through our tools.
In addition, we have a folder named mzy in each device, and there may be some installation packages in the Downloads folder as well. The first thing to do after turning on the device is to switch the environment. We created an environment called powertest on each device and downloaded and installed some of the relevant libraries needed for this project so as not to interfere with other projects. 

The way to change the environment is 
```bash
conda activate powertest
```

## Installing Prometheus on Linux

1. **Download Prometheus**:

    ```bash
    wget https://github.com/prometheus/prometheus/releases/download/v<VERSION>/prometheus-<VERSION>.linux-amd64.tar.gz
    tar xvfz prometheus-*.tar.gz
    cd prometheus-<VERSION>.linux-amd64
    ```

2. **Configure Prometheus**:

    Prometheus uses `prometheus.yml` for its configurations. Ensure you adjust this file to your needs.

    ![image](https://github.com/Zhou1993napolun/Powertest/assets/33430986/35f27e8b-f6fc-4d87-aa88-e7f99548d3d6)

3. **Run Prometheus**:

    Start Prometheus with:

    ```bash
    ./prometheus --config.file=prometheus.yml
    ```

4. **(Optional) Running as a System Service**:

    Consider running Prometheus as a system service using tools like `systemd` for longevity and stability.

## Installing Grafana on Linux

### 1. **Download and Install Grafana**:

You can install Grafana using the official APT repositories.

```bash
sudo add-apt-repository "deb https://packages.grafana.com/oss/deb stable main"
sudo wget -q -O - https://packages.grafana.com/gpg.key | sudo apt-key add -
sudo apt-get update
sudo apt-get install grafana
```

### 2. Enable and Start Grafana Service:

After installing, start the Grafana server with the following commands:

```bash
sudo systemctl enable grafana-server
sudo systemctl start grafana-server
```

Check its status with:

```bash
sudo systemctl status grafana-server
```

### 3. Access Grafana:

Open your browser and navigate to:

```bash
http://your_server_ip:3000/
```

Default login credentials are:

Username: admin

Password: admin

### 4. Connect Prometheus to Grafana:

- **Once logged in, click on the gear icon on the left side to open the Configuration menu.**

- **Click Data Sources and then Add data source.**

- **Choose Prometheus as the data source type.**

- **Enter your Prometheus server information and then click Save & Test.**

### 5. (Optional) Configure Grafana to Start on Boot:

To have Grafana start automatically on system boot:

```bash
sudo systemctl enable grafana-server
```

## Nvidia Node Exporter: Installation & Configuration

### Prerequisites
Ensure you have NVIDIA drivers and nvidia-smi properly installed on your machine.

### Installation
#### 1. Downloading the Release

Navigate to the official GitHub repository of 'nvidia_node_exporter' and find the desired release. Alternatively, use 'wget' to directly download the release:
```bash
wget nvidia_gpu_exporter_1.1.0_linux_arm64.tar
```
or
```bash
wget nvidia_gpu_exporter_1.1.0_linux_amd64.tar
```

#### 2. Extracting the Tarball

Once downloaded, extract the contents of the tarball:
```bash
tar -xvf nvidia_gpu_exporter_1.1.0_linux_arm64.tar
```
or
```bash
tar -xvf nvidia_gpu_exporter_1.1.0_linux_amd64.tar
```

#### 3. Configuration
By default, the nvidia_node_exporter should work out of the box for most setups. However, if there are any specific configurations or flags you'd like to set, refer to the official documentation.

Starting the Nvidia Node Exporter

#### 4. Verification:
To ensure that the nvidia_node_exporter is running correctly, you can check its metrics endpoint:

```bash
curl http://localhost:9100/metrics
```

This should display a variety of metrics related to your NVIDIA GPU. e.g.: https://github.com/utkuozdemir/nvidia_gpu_exporter/blob/master/METRICS.md

## Introduction to PyJoules

PyJoules is a library for evaluating the energy efficiency of Python code. It allows developers to measure energy consumption directly in Python code without the need for hardware-level means or other external tools. The goal is to simplify the energy analysis process and provide Python developers with an easy-to-use tool to evaluate and optimize the energy efficiency of their code.

The details of PyJoules can be found on https://github.com/powerapi-ng/pyJoules.

In short, if we want to use PyJoules, the method is as follows：
```bash
from pyJoules.energy_meter import measure_energy
import time

@measure_energy
def foo():
   for i in range(10):
       print(i)
       time.sleep(2)
   # Instructions to be evaluated.

foo()
```


```bash
from pyJoules.energy_meter import measure_energy
```
This line imports the measure_energy decorator in the PyJoules library. A decorator is a Python feature that can modify or enhance the behavior of a function without changing the code of the function.

The **@measure_energy decorator**: This decorator is imported from the PyJoules library and is applied to the foo function. The role of the decorator is to measure and report the energy consumption of the function. When the decorator @measure_energy is applied to a function, the execution of the function is intercepted by the PyJoules library in order to measure its energy consumption.

**foo function**:
This is a simple function that loops 10 times, printing a number (from 0 to 9) for each loop and pausing for 2 seconds between each iteration. It uses time.sleep(2) to implement this pause.
The purpose of this function may be to simulate a sustained energy consumption behavior for measurement with PyJoules.

**foo()**: This line of code calls the foo function. Since the foo function is decorated by the @measure_energy decorator, PyJoules measures and reports its energy consumption when the function executes.


The results are generally shown as follows:
![image](https://github.com/Zhou1993napolun/Powertest/assets/33430986/8e5717a7-7fdb-4bd8-a79d-237b1a74dc60)

From the figure above we can see that it has a number of outputs, the meanings of these outputs are:

**begin timestamp**: indicates the timestamp at which the measurement interval begins

**duration**: indicates the measurement duration

**package**: CPU 0 Energy consumed during the measurement interval (uJ)

**dram**: Dynamic Memory Unit Energy Loss (uJ)

**nvidia_gpu**: Energy consumed by GPU 0 during the measurement interval (uJ)

These results can provide reference for our follow-up measurement comparison. Our tools also need to integrate the functionality of pyJoules.

## Write the code

With the groundwork above, we can write code. The purpose of our code is to take the data read by Prometheus, integrate the CPU, GPU, and RAM, and then calculate the power consumption by power and time, compare the results with pyJoules, and save the data to a csv file for Grafana to visualize.

The specific code can be found at powertest.py.

Here is some explanation of the code.

```bash
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
```
We need to lay out the nodes on Prometheus and make sure that the nodes are in the right state so that Prometheus can properly monitor the device information and pass the data to our code. This function obtains the corresponding node state and outputs it by providing the URL.

To do this we need to change prometheus.yml first. To add a node, the general method is as follows:
```bash
job_name: 'prometheus'
static_configs:
 - targets: ['IP_address:9090']
```

When you are done, you need to restart prometheus and open the prometheus web page.

Open your browser: http://localhost:9090/

Select **Status**->**target**

Then you can view the corresponding status of the node.

The normal situation is shown as follows:

![image](https://github.com/Zhou1993napolun/Powertest/assets/33430986/5a017f79-b587-4987-9157-b2bc5e80535a)


```bash
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
```
This function retrieves the device details and writes them to the csv file.


```bash
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
```
This function is used to query the CPU usage, and we can use it to get the CPU data separately.

```bash
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
```
Similarly, the two functions are RAM and GPU.

```bash
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
       
       print("\n")
       ans = (120*usage_cpu + 250*usage_gpu) / 100 * (end_time-start_time) / 3600
       print(f"Estimated power consumption by CPU+GPU：{ans}Wh")
       print(f"After conversion：{ans*3600000}uJ")
       print(f"Estimated power consumption by CPU：{1200*usage_cpu*(end_time-start_time)}uJ")
       print(f"Estimated power consumption by GPU：{2500*usage_gpu*(end_time-start_time)}uJ")
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
```
This function makes a summary of it, and after executing this function, the relevant data will be written to usage_data.csv.

```bash
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
```

Here, the query_total_energy function is rewritten as a decorator to match pyJoules.

In fact, the purpose is the same, but the use is different. 

```bash
get_system_info()

# 设置Prometheus服务器的IP地址
prometheus_server_address = 'http://localhost:9090'

# 调用函数检测目标状态
getTargetsStatus(prometheus_server_address)
```

These are the preparations.

- **If you want to use query_total_energy function:**
```bash
# 获取最近5分钟的时间范围
# end_time = datetime.now().isoformat()
# start_time = (datetime.now() - timedelta(minutes=5)).isoformat()

end_time = int(time.time())
start_time = end_time - 300

# query_CPU_Average_Usage(prometheus_server_address, start_time, end_time)
# query_RAM_Average_Usage(prometheus_server_address, start_time, end_time)
# query_GPU_Average_Usage(prometheus_server_address, start_time, end_time)
query_total_energy(prometheus_server_address, start_time, end_time)
```

Here you need to set start_time and end_time, which are adjustable. But in a practical application, you could write:
```bash
start_time = int(time.time())
# Your other code, for example, some deep learning models, that is, the fragments you want to measure.
end_time = int(time.time())
query_total_energy(prometheus_server_address, start_time, end_time)
```
In this way, the energy consumption of the desired part can be measured. See UserManual.md for more details.

- **If you want to use the decorator**
```bash
@measure_total_energy
def foo():
    start_time = int(time.time())
    # Your other code, for example, some deep learning models, that is, the fragments you want to measure.
    end_time = int(time.time())
    query_total_energy(prometheus_server_address, start_time, end_time)

foo()
```

## Grafana

At the end of the day you can build a visual panel using Grafana.

Once in Grafana, your first step is to add a data source.

Since Grafana's data sources are typically databases such as MySQL, you need to install a plugin to read the csv data source.

The plugin can be download from https://grafana.com/grafana/plugins/marcusolsson-csv-datasource/?tab=installation%E3%80%82.

![image](https://github.com/Zhou1993napolun/Powertest/assets/33430986/3f51e50f-d3b0-45a6-bdc1-a50352c1cdc2)

By selecting prometheus as the data source, you can directly display many of prometheus's data, including CPU and RAM.

![image](https://github.com/Zhou1993napolun/Powertest/assets/33430986/c2141810-d59f-4d78-b0d5-ea3e2d3a88fa)

If you have the plugin installed, you can select CSV from others at the bottom.

![image](https://github.com/Zhou1993napolun/Powertest/assets/33430986/7e9fd3db-e56e-4d20-a988-d561949810fc)

You can choose local or HTTP here. HTTP is recommended.

The method is to directly use Python's native functions in the corresponding folder directory.
```bash
python3 -m http.server
```

We can then access the csv data via the Intranet at http://localhost:8000.

Then you can use Grafana's tools to build your dashboard and panels yourself!

This is our dashboard.

![image](https://github.com/Zhou1993napolun/Powertest/assets/33430986/62b61ed7-ae44-40f3-bba1-da7597ee2e79)

## Conclusion

So far, the project is almost complete. But there are a few more things to look into.

- **Grafana's Dashboard could be even more polished.**

Grafana has many powerful features that allow you to deploy more powerful databases or use more aesthetically pleasing presentation methods.

- **Query_expression**

Prometheus requires query statements to retrieve data, but these queries may have different methods for calculating average data over a period of time. Different query statements correspond to different query principles, although they may all be calculated usage. Therefore, it is possible to compare different methods.

- **For Intel device**

The current tool can only be used on Nvidia devices, Intel's GPU has a different query method, but the current configuration and the way is not perfect.
