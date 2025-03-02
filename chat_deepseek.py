#!/usr/bin/python
# -*- coding: UTF-8 -*-
"""
Created on 2025-02-27
@author: 罗辑
@description: chat主文件
@last_modified: 2025-02-27 by Trae
"""
import json
import time
import requests
import paho.mqtt.client as mqtt
import threading
import pyaudio
import opuslib
import socket
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import logging
from pynput import keyboard as pynput_keyboard
from deepseek.config.get_remote_mqtt import mqtt_info
class VoiceBot:
    def __init__(self):
        # MQTT相关
        self.mqtt_info = {}
        self.mqttc = None
        self.aes_opus_info={}
        # 状态相关
        self.local_sequence = 0
        self.listen_state = None
        self.tts_state = None
        self.key_state = None
        self.conn_state = False
        
        # 音频相关
        self.audio = pyaudio.PyAudio()
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.recv_audio_thread = threading.Thread()
        self.send_audio_thread = threading.Thread()

    def aes_ctr_encrypt(self, key, nonce, plaintext):
        # 1. 创建 AES-CTR 模式的加密器
        cipher = Cipher(
            algorithms.AES(key),        # 使用AES算法，传入密钥
            modes.CTR(nonce),          # 使用CTR模式，传入nonce（计数器初始值）
            backend=default_backend()   # 使用默认的加密后端
        )
        
        # 2. 获取加密器实例
        encryptor = cipher.encryptor()
        
        # 3. 加密数据
        return encryptor.update(plaintext) + encryptor.finalize()

    def aes_ctr_decrypt(self, key, nonce, ciphertext):
        # 1. 创建 AES-CTR 模式的解密器
        cipher = Cipher(
            algorithms.AES(key),        # 使用AES算法，传入密钥
            modes.CTR(nonce),          # 使用CTR模式，传入nonce（计数器初始值）
            backend=default_backend()   # 使用默认的加密后端
        )
        
        # 2. 获取解密器实例
        decryptor = cipher.decryptor()
        
        # 3. 解密数据
        plaintext = decryptor.update(ciphertext) + decryptor.finalize()
        
        return plaintext

    def transmit_audio(self):
        # 1. 获取配置参数
        key = self.aes_opus_info['udp']['key']
        nonce = self.aes_opus_info['udp']['nonce']
        server_ip = self.aes_opus_info['udp']['server']
        server_port = self.aes_opus_info['udp']['port']
        
        # 获取音频参数
        sample_rate = self.aes_opus_info['audio_params']['sample_rate']      # 采样率
        frame_duration = self.aes_opus_info['audio_params']['frame_duration'] # 帧时长(ms)
        
        # 计算每帧采样点数
        frame_size = int(sample_rate * frame_duration / 1000)  # 采样率 * 帧时长(秒)
        # frame_size=960
        
        # 2. 初始化音频编码器和麦克风
        encoder = opuslib.Encoder(sample_rate, 1, opuslib.APPLICATION_AUDIO)
        mic = self.audio.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=sample_rate,
            input=True,
            frames_per_buffer=frame_size  # 使用计算出的帧大小
        )
        
        try:
            while True:
                if self.listen_state == "stop":
                    continue
                    time.sleep(0.1)
                
                data = mic.read(frame_size)              # 使用计算出的帧大小
                encoded_data = encoder.encode(data, frame_size)  # 使用计算出的帧大小
                
                # 5. 生成新的nonce并加密
                self.local_sequence += 1
                # 组装新的nonce：前4字节 + 数据长度(4字节) + 中间部分 + 序列号(8字节)
                new_nonce = nonce[0:4] + format(len(encoded_data), '04x') + nonce[8:24] + format(self.local_sequence, '08x')
                
                # 6. 加密音频数据
                encrypt_encoded_data = self.aes_ctr_encrypt(
                    bytes.fromhex(key),
                    bytes.fromhex(new_nonce),
                    bytes(encoded_data)
                )
                
                # 7. 组装并发送数据包
                data = bytes.fromhex(new_nonce) + encrypt_encoded_data  # nonce + 加密数据
                self.udp_socket.sendto(data, (server_ip, server_port))  # 发送到服务器
                
        except Exception as e:
            print(f"发送音频错误: {e}")
        finally:
            # 8. 清理资源
            self.local_sequence = 0
            self.udp_socket = None
            mic.stop_stream()
            mic.close()

    def receive_audio(self):
        # 1. 获取配置参数
        key = self.aes_opus_info['udp']['key']                    # 解密密钥
        nonce = self.aes_opus_info['udp']['nonce']               # 加密用的 nonce
        sample_rate = self.aes_opus_info['audio_params']['sample_rate']      # 采样率
        frame_duration = self.aes_opus_info['audio_params']['frame_duration'] # 帧时长
        frame_num = int(frame_duration / (1000 / sample_rate))    # 计算每帧样本数
        
        # 2. 初始化音频解码器和播放器
        decoder = opuslib.Decoder(sample_rate, 1)                 # Opus 解码器
        spk = self.audio.open(                                    # 打开音频输出流
            format=pyaudio.paInt16,                              # 16位音频格式
            channels=1,                                          # 单声道
            rate=sample_rate,                                    # 采样率
            output=True,                                         # 输出模式
            frames_per_buffer=frame_num                          # 缓冲区大小
        )
        
        try:
            while True:
                # 3. 接收加密的音频数据
                data, server = self.udp_socket.recvfrom(4096)    # 从UDP接收数据，4096（4KB）是一个比较常见的缓冲区大小
                encrypt_encoded_data = data
                
                # 4. 解密过程
                # 分离nonce（前16字节）和加密数据
                split_encrypt_encoded_data_nonce = encrypt_encoded_data[:16]
                split_encrypt_encoded_data = encrypt_encoded_data[16:]
                
                # 5. 解密：将加密的数据还原为原始的 Opus 编码数据
                decrypt_data = self.aes_ctr_decrypt(
                    bytes.fromhex(key),
                    split_encrypt_encoded_data_nonce,
                    split_encrypt_encoded_data
                )
                
                # 6. 解码：将 Opus 编码的音频数据解码为原始的PCM音频数据
                pcm_audio = decoder.decode(decrypt_data, frame_num)
                
                # 7. 播放：将PCM音频数据写入音频设备
                spk.write(pcm_audio)
                
        except Exception as e:
            print(f"接收音频错误: {e}")
        finally:
            # 8. 清理资源
            self.udp_socket = None
            spk.stop_stream()
            spk.close()

    def handle_mqtt_connect(self, client, userdata, flags, rc, properties=None):
        """
        MQTT连接成功的回调函数
        
        Args:
            client: MQTT客户端实例
            userdata: 用户定义的数据
            flags: 包含broker返回的标志的字典
            rc: 连接结果的返回码（0表示连接成功）
            properties: MQTT v5 的连接属性
        """
        print("连接服务器成功，请按住对话键开始聊天吧^_^")

    def handle_mqtt_message(self, client, userdata, message, properties=None):
        """
        处理接收到的MQTT消息的回调函数
        
        Args:
            client: MQTT客户端实例
            userdata: 用户定义的数据
            message: 收到的消息对象，包含主题(topic)和负载(payload)
            properties: MQTT v5 的消息属性
        """
        msg = json.loads(message.payload)  # 解析收到的JSON消息
        # print(msg)
        # 只输出 llm 类型的消息中的 text
        if 'text' in msg and msg.get('type') == 'tts' and msg.get('state')=='sentence_start':
            print(f"小智: {msg['text']}")
        if 'text' in msg and msg.get('type') == 'stt':
            print(f"我: {msg['text']}")
        
        # 1. 处理hello消息：服务器确认连接
        if msg['type'] == 'hello':
            self.aes_opus_info = msg  # # 用服务器返回的配置更新aes_opus_info
            self.udp_socket.connect((msg['udp']['server'], msg['udp']['port']))  # 建立UDP连接
            self.conn_state = True  # 更新连接状态
            
            # 启动接收音频线程（如果未启动）
            if not self.recv_audio_thread.is_alive():
                self.recv_audio_thread = threading.Thread(target=self.receive_audio) # target 参数指定线程要执行的函数，self.receive_audio 是传递函数引用
                self.recv_audio_thread.start() #在创建线程时，我们传递函数引用而不是执行函数，让线程在启动时（调用 start() 方法时）才执行该函数。
            else:
                print("接收音频线程正在运行")
            
            # 启动发送音频线程（如果未启动）
            if not self.send_audio_thread.is_alive():
                self.send_audio_thread = threading.Thread(target=self.transmit_audio) # target 参数指定线程要执行的函数
                self.send_audio_thread.start()
            else:
                print("发送音频线程正在运行")
        
        # 2. 处理TTS状态消息
        if msg['type'] == 'tts':
            self.tts_state = msg['state']  # 更新TTS播放状态
        
        # 3. 处理goodbye消息：结束会话
        if (msg['type'] == 'goodbye' and 
            self.udp_socket and 
            'session_id' in msg and 
            'session_id' in self.aes_opus_info and 
            msg['session_id'] == self.aes_opus_info['session_id']):
            
            print(f"收到结束会话消息")
            self.aes_opus_info['session_id'] = None  # 清除会话ID

    def publish_mqtt_message(self, message):
        """发布MQTT消息到指定主题"""
        # 如果消息中包含text字段，则输出
        if 'text' in message:
            print(f">>> {message['text']}")
        self.mqttc.publish(
            self.mqtt_info['publish_topic'],
            json.dumps(message)
        )

    def handle_voice_input_start(self, event):
        """
        处理开始语音输入的事件（当用户按下触发键时）
        
        Args:
            event: 键盘事件对象
        """
        if self.key_state == "press":
            return
        self.key_state = "press"
        
        # 判断是否需要发送hello消息建立连接
        if self.conn_state is False or not self.aes_opus_info.get('session_id'):
            # 构造并发送hello消息,建立UDP连接
            hello_msg = {
                "type": "hello", 
                "version": 3, 
                "transport": "udp",
                "audio_params": {
                    "format": "opus", 
                    "sample_rate": 16000, 
                    "channels": 1, 
                    "frame_duration": 60
                }
            }
            self.publish_mqtt_message(hello_msg)
            # print(f"发送hello消息: {hello_msg}")
            # 等待服务器的hello响应
            return  # 等待服务器hello响应后再继续
            
        # 如果正在播放TTS,发送abort消息中断播放
        if self.tts_state == "start" or self.tts_state == "sentence_start":
            abort_msg = {"type": "abort"}
            self.publish_mqtt_message(abort_msg)
            print(f"发送中断消息:{abort_msg}")

        # 发送开始监听消息
        msg = {
            "session_id": self.aes_opus_info['session_id'], 
            "type": "listen", 
            "state": "start", 
            "mode": "manual"
        }
        self.publish_mqtt_message(msg)

    def handle_voice_input_end(self, event):
        """
        处理结束语音输入的事件（当用户释放触发键时）
        
        Args:
            event: 键盘事件对象
        """
        self.key_state = "release"
        
        # 检查是否有有效的会话
        if not self.aes_opus_info.get('session_id'):
            return  # 如果没有有效的会话ID，直接返回
            
        # 发送停止监听消息
        msg = {
            "session_id": self.aes_opus_info['session_id'], 
            "type": "listen", 
            "state": "stop"
        }
        # print(f"发送停止监听消息: {msg}")
        self.publish_mqtt_message(msg)

    def on_press(self, key):
        """
        键盘按键按下事件的回调函数
        
        Args:
            key: pynput自动传入的按键对象，可能是以下两种类型：
                1. pynput.keyboard.Key: 特殊键（如空格、ESC等）
                2. pynput.keyboard.KeyCode: 字符键（如字母、数字等）
        """
        #使用空格键作为触发键
        if key == pynput_keyboard.Key.space:
            self.handle_voice_input_start(None)
        # 原F23按键已禁用
        # if key == pynput_keyboard.Key.f23:
        #     self.handle_voice_input_start(None)
        # 如果要使用字符键，可以这样：
        # if hasattr(key, 'char') and key.char == 'a':
        #     self.handle_voice_input_start(None)

    def on_release(self, key):
        """
        键盘按键释放事件的回调函数
        
        Args:
            key: 同上，pynput自动传入的按键对象
        """
        if key == pynput_keyboard.Key.space:
            self.handle_voice_input_end(None)
        # 原F23按键已禁用
        # if key == pynput_keyboard.Key.f23:
        #     self.handle_voice_input_end(None)
        if key == pynput_keyboard.Key.esc:
            return False  # 返回False会停止监听

    def initialize_mqtt_client(self):
        """初始化MQTT客户端配置"""
        # 创建 MQTT v5 客户端
        self.mqttc = mqtt.Client(
            client_id=self.mqtt_info['client_id'],
            protocol=mqtt.MQTTv5,  # 指定使用 MQTT v5 协议
            callback_api_version=mqtt.CallbackAPIVersion.VERSION2  # 明确指定使用 V2 回调 API
        )
        
        # 设置回调函数
        self.mqttc.on_connect = self.handle_mqtt_connect
        self.mqttc.on_message = self.handle_mqtt_message
        
        # 1. 配置 MQTT 客户端的 TLS/SSL 加密连接参数：是客户端对服务器连接的要求和期望
        self.mqttc.tls_set(
            ca_certs=None,      # 使用系统的 CA 证书来验证服务器
            certfile=None,      # 客户端不提供证书
            keyfile=None,       # 客户端不提供密钥
            cert_reqs=mqtt.ssl.CERT_REQUIRED,  # 要求服务器必须提供有效证书
            tls_version=mqtt.ssl.PROTOCOL_TLS, # 要求服务器使用现代 TLS 协议
            ciphers=None        # 接受默认的加密算法
        )
        # 2. 使用用户名密码进行身份验证
        self.mqttc.username_pw_set(
            username=self.mqtt_info['username'],
            password=self.mqtt_info['password']
        )

        # 3. 连接到加密的 MQTT 端口（8883是标准的 MQTT over TLS 端口）
        self.mqttc.connect(host=self.mqtt_info['endpoint'], port=8883, keepalive=120)  # keepalive设为120秒(2分钟)
        self.mqttc.loop_forever()  # 开始消息循环
        '''
        启动一个永久运行的消息循环
        作用：
        保持与服务器的连接                       
        自动处理消息的收发
        处理所有回调函数（on_connect, on_message 等）
        自动重连（如果连接断开）
        这是一个阻塞调用，会一直运行直到程序结束
        '''

    def start(self):
        """启动语音机器人服务"""
        self.mqtt_info=mqtt_info
        # 创建监听器时，指定回调函数
        listener = pynput_keyboard.Listener(
            on_press=self.on_press,     # 不需要手动传参，pynput会自动传入key
            on_release=self.on_release  # 不需要手动传参，pynput会自动传入key
        )
        listener.start()
        
        self.initialize_mqtt_client()


if __name__ == "__main__":
    voicebot = VoiceBot()
    voicebot.start()
