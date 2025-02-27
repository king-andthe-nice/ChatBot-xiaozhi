#!/usr/bin/python
# -*- coding: UTF-8 -*-
"""
Created on 2025-02-27
@author: 罗辑
@description: YAML配置文件读取模块
@last_modified: 2025-02-27 by Trae
"""
import yaml
import os

def get_yaml_config(file_name):
    """读取yaml配置文件"""
    config_path = os.path.join(os.path.dirname(__file__), file_name)
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    return config

config = get_yaml_config('device.yaml')
# print(config)
