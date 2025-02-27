"""
Created on 2025-02-27
@author: 罗辑
@description: mqtt读取模块
@last_modified: 2025-02-27 by Trae
"""
import requests
import json
import logging
from deepseek.config.get_yaml_config import config

def get_mqtt_info():
    """获取配置信息和MQTT连接参数"""
    header = {
        'Device-Id': config['DEVICE_ADDR'],  # 设备标识符，使用MAC地址作为唯一标识
        'Content-Type': 'application/json'  # 指定请求体的数据格式为JSON
    }

    post_data = {
        "application": {  # 应用程序信息
            "name": "xiaozhi",  # 应用程序名称，这里是"小智"
            "version": "0.9.9"  # 应用程序版本号
        },
        "board": {  # 设备信息
            "type": "pc-client",  # 设备类型，这里表示是PC客户端
            "mac": config['DEVICE_ADDR']  # 设备的MAC地址，用于唯一标识设备
        }
    }
    # 发送POST请求获取配置
    response = requests.post(config['CONFIG_URL'], headers=header, data=json.dumps(post_data))
    # 从响应中提取MQTT配置信息
    mqtt_info = response.json()['mqtt']
    '''
    这个过程的作用是：
    设备注册：向服务器注册设备信息
    获取配置：获取MQTT连接所需的所有参数
    身份验证：通过MAC地址验证设备身份
    版本控制：上报当前版本，服务器可以决定是否需要更新
    这是整个系统的初始化步骤，为后续的MQTT连接和音频传输做准备。
    '''
    return mqtt_info
mqtt_info = get_mqtt_info()
