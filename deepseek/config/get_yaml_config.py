#!/usr/bin/python
# -*- coding: UTF-8 -*-
"""
Created on 2025-02-27
@author: 罗辑
@description: YAML配置文件读取模块
"""
import yaml
import os
import uuid
import re
import platform
import socket
import subprocess

def get_yaml_config(file_name):
    """读取yaml配置文件"""
    config_path = os.path.join(os.path.dirname(__file__), file_name)
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    return config

# 获取配置文件的路径
dir_path = os.path.dirname(os.path.realpath(__file__))
config_path = os.path.join(dir_path, 'device.yaml')

# 加载配置文件
with open(config_path, 'r', encoding='utf-8') as file:
    config = yaml.safe_load(file)

def get_mac_address():
    """获取实际MAC地址的多平台方法"""
    try:
        # 方法1: 使用uuid模块获取MAC地址
        mac_int = uuid.getnode()
        # 验证地址是否有效 (如果getnode()失败，它会返回一个随机数)
        if (mac_int >> 40) % 2 == 0:  # 判断MAC是否是单播地址
            hex_mac = format(mac_int, '012x')
            formatted_mac = ':'.join(hex_mac[i:i+2] for i in range(0, 12, 2))
            return formatted_mac
            
        # 方法2: 使用系统特定的命令获取MAC地址
        system = platform.system().lower()
        
        if system == 'windows':
            # Windows系统使用ipconfig命令
            output = subprocess.check_output('ipconfig /all', shell=True).decode('gbk')
            for line in output.split('\n'):
                if '物理地址' in line or 'Physical Address' in line:
                    mac = line.split(':')[1].strip()
                    # 确保格式化为标准MAC地址格式
                    if mac and len(mac) >= 12:
                        if '-' in mac:
                            mac = mac.replace('-', ':')
                        return mac
                        
        elif system == 'linux':
            # Linux系统使用ip命令
            output = subprocess.check_output('ip link show', shell=True).decode('utf-8')
            for line in output.split('\n'):
                if 'link/ether' in line:
                    mac = line.split('link/ether')[1].split()[0].strip()
                    return mac
                    
        elif system == 'darwin':  # macOS
            # macOS系统使用ifconfig命令
            output = subprocess.check_output('ifconfig en0', shell=True).decode('utf-8')
            for line in output.split('\n'):
                if 'ether' in line:
                    mac = line.split('ether')[1].strip()
                    return mac
                    
        # 方法3: 尝试使用socket获取主机名，然后解析MAC
        hostname = socket.gethostname()
        ip_addr = socket.gethostbyname(hostname)
        
        # 如果上述方法都失败，生成一个唯一但一致的ID基于主机名
        host_hash = hash(hostname + ip_addr)
        # 确保为正数并限制范围
        host_hash = abs(host_hash) % (2**48)  # MAC地址是48位
        hex_mac = format(host_hash, '012x')
        formatted_mac = ':'.join(hex_mac[i:i+2] for i in range(0, 12, 2))
        return formatted_mac
            
    except Exception as e:
        print(f"获取MAC地址出错: {str(e)}，将生成随机ID")
        # 如果所有方法都失败，返回一个随机但一致的ID
        return get_random_device_id()

def get_random_device_id():
    """生成随机但对于同一用户是一致的设备ID"""
    try:
        # 基于用户名和计算机名创建一个稳定的种子
        username = os.getenv('USERNAME') or os.getenv('USER') or 'user'
        hostname = socket.gethostname()
        # 组合用户名和主机名作为种子
        seed = f"{username}@{hostname}"
        # 使用哈希函数生成一个稳定的数值
        hash_value = hash(seed) % (2**48)  # 确保在MAC地址范围内
        # 转换为十六进制字符串并格式化为MAC地址格式
        hex_id = format(abs(hash_value), '012x')
        formatted_id = ':'.join(hex_id[i:i+2] for i in range(0, 12, 2))
        return formatted_id
    except Exception as e:
        print(f"生成随机设备ID时出错: {str(e)}")
        # 最后的后备选项 - 固定ID
        return "ff:ff:ff:ff:ff:ff"

# 如果用户共享同一个可执行文件，根据配置决定是否使用实际MAC地址
if 'DEVICE_ADDR' in config:
    # 保存原始配置的MAC地址格式
    mac_format = config['DEVICE_ADDR']
    # 检查是否需要生成新的设备ID
    # 如果环境变量中设置了XIAOZHI_FIXED_MAC=1，则使用配置文件中的固定ID
    if os.environ.get('XIAOZHI_FIXED_MAC') != '1':
        # 使用实际的MAC地址作为设备ID
        config['DEVICE_ADDR'] = get_mac_address()
        # 输出提示
        print(f"为本实例使用的设备ID: {config['DEVICE_ADDR']}")

# print(config)
