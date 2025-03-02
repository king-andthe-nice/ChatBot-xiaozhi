# 使用GitHub Actions构建XiaoZhi语音助手

本项目使用GitHub Actions自动构建Windows可执行文件，使用户无需在本地安装Python和依赖即可运行应用。

## 自动构建触发方式

GitHub Actions工作流支持两种触发方式：

### 1. 自动触发

当满足以下条件时，构建将自动触发：
- 推送代码到`main`分支
- 创建新的版本标签（格式为`v*`，例如`v1.0.0`）

当创建版本标签时，构建完成后将自动创建GitHub Release，并上传构建好的可执行文件。

### 2. 手动触发

您可以通过以下步骤手动触发构建：

1. 打开项目GitHub仓库
2. 点击"Actions"标签页
3. 从左侧列表选择"Build and Release XiaoZhi Voice Assistant"工作流
4. 点击"Run workflow"按钮
5. 可选择输入版本标识（默认为`dev-build`）
6. 点击"Run workflow"开始构建

## 获取构建结果

### 发布版本（使用标签触发）

1. 当使用版本标签触发构建时，完成后将自动创建Release
2. 访问项目GitHub仓库的"Releases"页面
3. 下载对应版本的可执行文件

### 开发版本（手动触发或推送到main）

1. 构建完成后，在Actions工作流详情页面找到"Artifacts"部分
2. 下载构建产物（包含可执行文件和README）

## 使用方法

1. 下载构建好的`.exe`文件
2. 双击运行程序
3. 按照README中的说明使用应用

## 技术细节

工作流使用最新的GitHub Actions组件：

- `actions/checkout@v4` - 检出代码库
- `actions/setup-python@v4` - 设置Python环境
- `softprops/action-gh-release@v1` - 创建GitHub Releases
- `actions/upload-artifact@v4` - 上传构建产物

## 注意事项

- 构建过程在Windows环境中进行，确保最佳兼容性
- 包含所有依赖，无需额外安装
- 自动包含opus.dll和所有必要配置文件
- 使用PowerShell而非Bash执行Windows命令 