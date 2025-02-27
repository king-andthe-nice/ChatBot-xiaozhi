# python电脑版小智语音助手(直连虾哥服务器-感谢虾哥)

虾哥开源小智项目地址：https://github.com/78/xiaozhi-esp32

开发参考项目：https://github.com/zhh827/py-xiaozhi （感谢作者）

小智语音助手是一个基于Python开发的智能语音交互系统，支持实时语音对话功能。

## 功能特点

- 实时语音对话
- 加密音频传输
- MQTT通信
- 自动设备注册
- TLS安全连接

## 系统要求

- Python 3.7+
- Windows 10/11
- 麦克风和扬声器

## 安装说明

1. 克隆项目到本地：

```bash
git clone [项目地址]
cd ChatBot
windwos平台将opus.dll 拷贝到C:\Windows\System32
```

2. 安装依赖：

```bash
pip install -r requirements.txt
```

注意：在Windows系统上，某些依赖可能需要额外的步骤：

- PyAudio可能需要先安装Visual C++ Build Tools
- opuslib可能需要手动安装opus编解码器

## 配置说明

1. 修改 `deepseek/config/device.yaml` 文件：

```yaml
CONFIG_URL: 'https://api.tenclass.net/xiaozhi/ota/'
DEVICE_ADDR: '你的设备MAC地址'
```

## 使用方法

1. 运行主程序：

```bash
python chat_deepseek.py
登录到控制面板地址：https://xiaozhi.me/login
```

2. 操作说明：

- 按住 F23 键进行语音对话（根据自己情况修改）
- 松开 F23 键结束语音输入
- 按 ESC 键退出程序

## 技术架构

- 使用 MQTT 进行实时通信
- 采用 AES-CTR 模式进行音频加密
- 使用 Opus 编解码器进行音频压缩
- PyAudio 处理音频输入输出
- TLS/SSL 加密保护通信安全

## 注意事项

1. 确保设备有可用的麦克风和扬声器
2. 需要稳定的网络连接
3. 首次运行时会自动向服务器注册设备

## 许可证

MIT License

本项目遵循原作者虾哥的开源项目 [xiaozhi-esp32](https://github.com/78/xiaozhi-esp32) 的 MIT 许可证，同时参考了 [py-xiaozhi](https://github.com/zhh827/py-xiaozhi) 项目的实现。

根据 MIT 许可证，您可以自由地使用、修改和分发本软件，但需要在所有副本中包含原始许可证和版权声明。

特别感谢：
- 虾哥的 [xiaozhi-esp32](https://github.com/78/xiaozhi-esp32) 项目
- zhh827 的 [py-xiaozhi](https://github.com/zhh827/py-xiaozhi) 项目

详细许可证内容请参见原项目：https://github.com/78/xiaozhi-esp32
## 作者
- 罗辑 - 初始开发
- Trae - 最新维护
