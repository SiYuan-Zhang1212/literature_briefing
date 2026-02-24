# Literature Briefing / 文献简报生成器

> [中文](#中文) | [English](#english)

---

## 中文

每周自动帮你追踪 PubMed 和 arXiv 上的最新文献，翻译成中文，生成一份 Markdown 简报。

### 功能一览

- 自动检索 PubMed 核心期刊 + 关键词扩展搜索，以及 arXiv 预印本
- 通过 AI 将英文标题和摘要翻译为中文
- AI 自动挑选「本期亮点」论文
- 可视化设置界面，所有配置都可以通过点击完成
- 支持 Windows 开机自动运行

### 前置条件

- **Python 3.10+**：如果你的电脑还没有安装 Python，请前往 [python.org](https://www.python.org/downloads/) 下载安装，安装时务必勾选 **"Add Python to PATH"**

### 快速开始

**第一步：下载**

[![下载 ZIP](https://img.shields.io/badge/下载-ZIP%20压缩包-blue?style=for-the-badge)](https://github.com/SiYuan-Zhang1212/literature_briefing/archive/refs/heads/master.zip)

下载后解压到任意位置（如桌面或文档文件夹）。

**第二步：安装依赖**

双击解压后文件夹中的 `setup.bat`，它会自动安装所需的 Python 库并创建配置文件。

**第三步：打开设置**

双击 `打开设置.pyw`，你会看到一个设置窗口，有 5 个标签页。下面逐一说明需要设置什么：

#### 「通用」标签页

| 设置项 | 说明 |
|--------|------|
| 输出路径 | 简报文件保存在哪里。点击「浏览」选择一个文件夹，比如你的 Obsidian 笔记库路径或桌面 |
| 子文件夹名 | 简报会保存在输出路径下的这个子文件夹中，默认是「文献简报」 |
| 回溯天数 | 首次运行时往回检索多少天的文献，默认 7 天 |
| 最大结果数 | 每次检索最多返回多少篇，默认 200 |

#### 「文献源」标签页

这里配置你要追踪哪些期刊和关键词。分为 PubMed 和 arXiv 两个子标签。

**PubMed：**
- **PubMed API Key**：去 [NCBI](https://www.ncbi.nlm.nih.gov/account/) 注册一个免费账号，在 Settings → API Key 中生成。没有也能用，但有了检索更快更稳定
- **核心期刊**：你最关注的期刊，程序会检索这些期刊的所有新文献。在输入框中输入期刊缩写（如 `Neuron`），按回车添加
- **扩展期刊**：范围更广的期刊列表，程序只检索其中匹配关键词的文献
- **关键词**：你的研究方向关键词（如 `neuromodulation`、`brain stimulation`）
- **物种过滤**：只保留涉及特定物种的文献（如 `humans[MeSH]`）

**arXiv：**
- 默认关闭。如果你也关注预印本，勾选「启用 arXiv」
- 填入分类代码（如 `q-bio.NC` 表示计算神经科学）和关键词

#### 「AI 设置」标签页

程序需要调用 AI 来翻译文献和生成亮点。你需要选择一个 AI 提供商并填入 API Key。

| 设置项 | 说明 |
|--------|------|
| 提供商 | 推荐选 `openrouter`（聚合平台，可用多种模型）。也支持 `openai`、`gemini`、`claude` |
| API Key | 在对应平台注册后获取。OpenRouter 注册地址：[openrouter.ai](https://openrouter.ai/) |
| 模型 | 默认 `google/gemini-2.0-flash-001`，性价比高，翻译质量好 |
| 温度 | 控制 AI 输出的随机性，翻译场景建议保持默认 0.1 |
| 启用翻译 / 启用亮点 | 可以单独关闭翻译或亮点功能 |

点击「测试连接」可以验证 API Key 是否正确。

#### 「定时任务」标签页

配置 Windows 开机后自动运行简报生成：
- **延迟分钟数**：开机后等多久再运行（默认 20 分钟，等网络稳定）
- **弹窗确认**：运行前是否弹窗让你确认（推荐开启，这样你可以选择取消）
- 点击「安装定时任务」即可生效

**第四步：运行**

设置完成后，双击 `运行简报.pyw` 即可立即生成一份简报。之后每次开机会自动运行。

---

## English

Automatically tracks the latest papers from PubMed and arXiv, translates them via AI, and generates Markdown briefings.

### Features

- PubMed core journal + keyword search, and arXiv preprints
- AI-powered translation (English → Chinese) of titles and abstracts
- AI-generated "papers to watch" highlights
- Visual settings GUI — no config files to edit manually
- Windows scheduled task for automatic daily runs

### Prerequisites

- **Python 3.10+**: Download from [python.org](https://www.python.org/downloads/). Make sure to check **"Add Python to PATH"** during installation.

### Quick Start

**Step 1: Download**

[![Download ZIP](https://img.shields.io/badge/Download-ZIP-blue?style=for-the-badge)](https://github.com/SiYuan-Zhang1212/literature_briefing/archive/refs/heads/master.zip)

Extract to any location.

**Step 2: Install dependencies**

Double-click `setup.bat`. It installs the required Python packages and creates a config file.

**Step 3: Configure**

Double-click `打开设置.pyw` to open the settings GUI. Key things to set up:

- **General tab**: Set the output folder where briefings will be saved
- **Sources tab**: Add your target journals and keywords for PubMed; optionally enable arXiv
- **AI tab**: Choose an LLM provider (recommended: `openrouter`), paste your API key, and click "Test Connection"
- **Schedule tab**: Optionally install a Windows scheduled task for automatic runs

**Step 4: Run**

Double-click `运行简报.pyw` to generate your first briefing.

**Command line (advanced):**
```bash
python -m literature_briefing.main            # Run briefing
python -m literature_briefing.main --no-notify # Run without popup
python -m gui.app                              # Open settings GUI
```

### Project Structure

```
literature_briefing/      # Python package
  main.py                 # Entry point & orchestration
  config.py               # Config load/save/migrate
  llm/                    # LLM providers (openrouter, openai, gemini, claude)
  sources/                # Literature sources (pubmed, arxiv)
  translator.py           # Translation logic
  highlights.py           # Highlights generation
  output.py               # Markdown generation
  notify.py               # Popup notifications
gui/                      # Settings GUI (tkinter)
```

---

## License / 许可证

MIT
