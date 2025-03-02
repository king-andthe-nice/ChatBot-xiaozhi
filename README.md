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
- 自动化构建（GitHub Actions）

## 系统要求

- Windows 10/11
- 麦克风和扬声器
- 网络连接

## 使用方法

### 方法1：直接使用预构建的可执行文件（推荐）

无需安装Python和依赖，直接下载使用：

1. 从GitHub Releases页面下载最新版本的`xiaozhi-voice-assistant-vX.X.X.exe`
2. 双击运行下载的可执行文件
3. 使用按键操作：
   - 按住 空格键 进行语音对话
   - 松开 空格键 结束语音输入
   - 按 ESC 键退出程序

更多详情请参阅 [QUICK_START.md](QUICK_START.md)

### 方法2：从源代码安装

如果您希望从源代码运行，请按照以下步骤操作：

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

3. 配置设备：

修改 `deepseek/config/device.yaml` 文件：

```yaml
CONFIG_URL: 'https://api.tenclass.net/xiaozhi/ota/'
DEVICE_ADDR: '你的设备MAC地址'
```

4. 运行主程序：

```bash
python chat_deepseek.py
登录到控制面板地址：https://xiaozhi.me/login
```

## 自动构建说明

本项目使用GitHub Actions自动构建Windows可执行文件，支持以下功能：

- 自动触发构建（推送到main分支或创建新标签）
- 手动触发构建（通过GitHub Actions界面）
- 自动发布Release（当创建版本标签时）

详细使用说明请参阅 [GITHUB_ACTIONS.md](GITHUB_ACTIONS.md)

## 技术架构

- 使用 MQTT 进行实时通信
- 采用 AES-CTR 模式进行音频加密
- 使用 Opus 编解码器进行音频压缩
- PyAudio 处理音频输入输出
- TLS/SSL 加密保护通信安全
- GitHub Actions 实现CI/CD自动构建

## 注意事项

1. 确保设备有可用的麦克风和扬声器
2. 需要稳定的网络连接
3. 首次运行时会自动向服务器注册设备
4. 自动构建的可执行文件可能会被部分杀毒软件误报（可添加白名单）

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
