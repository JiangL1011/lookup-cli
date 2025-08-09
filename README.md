# 🔍 Lu (Lookup CLI) - AI驱动的智能翻译工具

一个强大、智能的AI命令行翻译工具，支持多种AI供应商，提供流式翻译、智能语言检测和个性化配置。

## ✨ 核心特性

- 🤖 **多AI供应商支持**: OpenAI (GPT系列)、DashScope (通义千问)、自定义OpenAI兼容API
- 🧠 **智能语言检测**: 自动识别输入语言，智能选择翻译目标
- 🌐 **多语言UI**: 支持中英文界面，根据用户主语言自动切换
- ⚡ **流式输出**: 实时显示翻译过程，响应迅速
- � **分层翻译**: 根据输入类型（单词/短语/句子）提供不同深度的翻译内容
- 🎨 **美观界面**: Rich终端UI，表情符号和颜色提升体验
- ⚙️ **智能配置**: 交互式配置向导，支持配置覆盖保护

## 🚀 安装与升级

无需克隆仓库，直接下载安装脚本即可获取已构建好的二进制文件。

### macOS / Linux 一键安装（最新版本）
```bash
curl -LsSf https://raw.githubusercontent.com/JiangL1011/lookup-cli/main/scripts/install.sh | sh
```

### Windows PowerShell 一键安装（最新版本）
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://raw.githubusercontent.com/JiangL1011/lookup-cli/main/scripts/install.ps1 | iex"
```

### 指定版本安装（示例 v0.1.0）
macOS / Linux：
```bash
curl -LsSf https://raw.githubusercontent.com/JiangL1011/lookup-cli/main/scripts/install.sh | LU_VERSION=v0.1.0 sh
```
Windows：
```powershell
powershell -ExecutionPolicy ByPass -c "$env:LU_VERSION='v0.1.0'; irm https://raw.githubusercontent.com/JiangL1011/lookup-cli/main/scripts/install.ps1 | iex"
```

### 升级
直接重复执行安装命令即可（脚本会自动检测并覆盖原有版本）。

### 卸载
macOS / Linux：
```bash
curl -LsSf https://raw.githubusercontent.com/JiangL1011/lookup-cli/main/scripts/uninstall.sh | sh
```
静默卸载（跳过确认）：
```bash
curl -LsSf https://raw.githubusercontent.com/JiangL1011/lookup-cli/main/scripts/uninstall.sh | FORCE=1 sh
```
Windows：
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://raw.githubusercontent.com/JiangL1011/lookup-cli/main/scripts/uninstall.ps1 | iex"
```

### 验证安装
```bash
lu --help
lu trans hello world
```

### 自定义安装目录
```bash
PREFIX=$HOME/.local curl -LsSf https://raw.githubusercontent.com/JiangL1011/lookup-cli/main/scripts/install.sh | sh
```
确保将 $HOME/.local/bin 加入 PATH。

### 手动（开发者）安装
```bash
git clone https://github.com/JiangL1011/lookup-cli.git
cd lookup-cli
uv sync  # 或 pip install -e .
python main.py --help
```

---

## 🏁 初始化配置
首次运行建议执行：
```bash
lu init
```
交互式配置向导将帮您设置：
* 主语言
* AI 供应商 (openai / dashscope / custom)
* 模型名称
* API Key / Base URL

配置文件位置： `~/.lu/config.yaml`

---

## 🔰 使用快速示例

```bash
# 自动检测语言
lu hello
lu "good morning"

# 指定目标语言
lu -t ja "Hello world"
lu --target zh-cn "Beautiful day"
```

## 🎯 使用方法

### 基本翻译
```bash
# 翻译单词
lu apple
lu programming

# 翻译短语
lu "good morning"
lu "artificial intelligence"

# 翻译句子
lu "How are you doing today?"
lu "The weather is beautiful."
```

### 使用trans命令（无需引号）
```bash
# 推荐使用trans命令，无需引号
lu trans hello world
lu trans How are you
lu trans The weather is nice today

# 指定目标语言
lu trans -t ja Good morning
lu -t zh-cn trans Hello world
```

### 语言和帮助
```bash
# 查看支持的语言
lu -s
lu --support

# 查看帮助
lu -h
lu --help

# 子命令帮助
lu init --help
lu trans --help
```

## 🌍 支持的语言

| 代码 | 语言 | 代码 | 语言 |
|------|------|------|------|
| `zh-cn` | 简体中文 | `en` | English |
| `zh-tw` | 繁体中文（台湾） | `de` | Deutsch |
| `zh-hk` | 繁体中文（香港） | `fr` | Français |
| `ja` | 日本語 | `es` | Español |
| `ko` | 한국어 | `nl` | Nederlands |
| `pl` | Polski | `ru` | Русский |
| `pt` | Português | `ar` | العربية |

## 🧠 智能特性

### 🎯 智能语言切换
- **非主语言 → 主语言**: 自动翻译为您配置的主语言
- **主语言输入**: 提供交互式目标语言选择菜单
- **手动指定**: 使用 `-t/--target` 参数强制指定目标语言

### 🌽 内容分层处理
- **单词翻译**: 提供音标、词性、例句
- **短语翻译**: 提供语境解释、使用示例
- **句子翻译**: 提供语法分析、相似表达

### 🔡 多语言界面
- 根据配置的主语言自动切换界面语言
- 所有提示、错误信息、帮助文本均支持双语
- AI说明内容使用用户的主语言

## ⚙️ 配置管理

### 配置文件位置
```
~/.lu/config.yaml
```

### 配置结构示例
```yaml
provider: dashscope
primary_language: zh-cn
models:
  dashscope:
    api_key: "sk-your-api-key"
    model: "qwen-plus"
  openai:
    api_key: "your-openai-key"
    model: "gpt-4"
    base_url: "https://api.openai.com/v1"
  custom:
    api_key: "custom-key"
    model: "custom-model"
    base_url: "http://localhost:8000/v1"
```

### 重新配置
```bash
# 重新运行init会显示当前配置并询问是否覆盖
lu init
```

## 🛠️ 开发信息

### 项目结构
```
lookup-cli/
├── main.py              # 程序入口
├── lu                   # 便捷执行脚本  
├── app/
│   ├── cli.py           # 命令行界面和路由
│   ├── translator.py    # 翻译服务核心
│   ├── config.py        # 配置管理
│   ├── i18n.py          # 国际化支持
│   └── __init__.py      # 包初始化
├── pyproject.toml       # 项目配置
└── README.md           # 项目文档
```

### 核心命令
```bash
# 查看所有命令
lu --help

# 主要子命令
lu init                # 初始化配置
lu trans [text...]     # 翻译文本（推荐）

# 选项参数  
-t, --target TEXT        # 指定目标语言
-s, --support           # 显示支持的语言
-h, --help              # 显示帮助信息
```

## 🎨 输出示例

### 单词翻译
```
🔍 正在翻译：: programming
🎯 目标语言：: zh-cn

╭────────── 🌐 翻译结果 ──────────╮
│ 编程                           │
│ (biān chéng)                  │
│ 例句：学习编程需要耐心和练习。    │
╰────────────────────────────────╯
```

### 智能语言选择
```
🎯 请选择目标语言：
1. zh-tw - 繁体中文（台湾）
2. zh-hk - 繁体中文（香港）  
3. en - English
4. de - Deutsch
... 
选择目标语言编号 [1/2/3/...]: 
```

## 🤝 贡献

欢迎提交Issue和Pull Request来改进这个项目！

## 📄 许可证

本项目采用 [MIT License](LICENSE) 开源许可证。