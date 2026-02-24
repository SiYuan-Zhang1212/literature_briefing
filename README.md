# Literature Briefing / 文献简报生成器

> [中文](#中文) | [English](#english)

---

## 中文

自动从 PubMed 和 arXiv 获取最新文献，通过 LLM 翻译并生成 Markdown 简报。

### 功能

- **多文献源**：PubMed（核心期刊 + 关键词扩展搜索）和 arXiv
- **多 LLM 支持**：OpenRouter、OpenAI、Google Gemini、Anthropic Claude — 纯 HTTP 调用，零 SDK 依赖
- **自动翻译**：标题和摘要翻译为中文
- **本期亮点**：LLM 自动挑选值得关注的论文
- **GUI 设置界面**：基于 tkinter 的可视化配置
- **定时任务**：Windows 任务计划集成

### 快速开始

1. 克隆仓库，运行 `setup.bat`
2. 编辑 `config.json`，填入 API Key 和期刊列表
3. 双击 `运行简报.pyw` 或等待定时任务触发

### 使用方式

**双击启动（推荐）：**
- `打开设置.pyw` — 打开设置界面
- `运行简报.pyw` — 运行文献简报生成

**命令行：**
```bash
python -m literature_briefing.main            # 运行简报
python -m literature_briefing.main --no-notify # 无弹窗模式
python -m gui.app                              # 打开设置界面
```

### 配置

将 `config.template.json` 复制为 `config.json`，填写：
- `output_path`：简报输出路径
- `llm.api_key`：LLM 提供商 API Key
- `sources.pubmed.api_key`：NCBI API Key（可选但推荐）

环境变量回退：`OPENROUTER_API_KEY`、`OPENAI_API_KEY`、`GEMINI_API_KEY`、`ANTHROPIC_API_KEY`、`PUBMED_API_KEY`

### 从旧版迁移

如果你之前使用的是单文件版本（`literature_briefing.py`），只需运行新版本，程序会自动将旧版 `config.json` 迁移为 v2 格式，不会丢失任何配置。

---

## English

Automated literature briefing generator that fetches recent papers from PubMed and arXiv, translates them via LLM, and generates Markdown reports.

### Features

- **Multi-source**: PubMed (core + keyword search) and arXiv
- **Multi-LLM**: OpenRouter, OpenAI, Google Gemini, Anthropic Claude — all via raw HTTP, zero SDK dependencies
- **Auto-translation**: Titles and abstracts translated to Chinese
- **Highlights**: LLM-generated "papers to watch" section
- **GUI settings**: tkinter-based configuration interface
- **Scheduled task**: Windows Task Scheduler integration

### Quick Start

1. Clone the repo and run `setup.bat`
2. Edit `config.json` with your API keys and journal lists
3. Double-click `运行简报.pyw` or wait for the scheduled task

### Usage

**Double-click (recommended):**
- `打开设置.pyw` — Open settings GUI
- `运行简报.pyw` — Run literature briefing

**Command line:**
```bash
python -m literature_briefing.main            # Run briefing
python -m literature_briefing.main --no-notify # Run without popup
python -m gui.app                              # Open settings GUI
```

### Configuration

Copy `config.template.json` to `config.json` and fill in:
- `output_path`: where to save briefing files
- `llm.api_key`: your LLM provider API key
- `sources.pubmed.api_key`: NCBI API key (optional but recommended)

Environment variable fallbacks: `OPENROUTER_API_KEY`, `OPENAI_API_KEY`, `GEMINI_API_KEY`, `ANTHROPIC_API_KEY`, `PUBMED_API_KEY`

### Project Structure

```
literature_briefing/      # Python package
  main.py                 # Entry point
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
