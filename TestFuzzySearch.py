import csv
import re

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

if __name__ == '__main__':
    cpu_model = 'Core 3 100U'
    gpu_model = 'GeForce RTX 4090'
    cpu_power = fuzzy_search_power('cpu',cpu_model)
    gpu_power = fuzzy_search_power('gpu',gpu_model)
    print(cpu_power)
    print(gpu_power)