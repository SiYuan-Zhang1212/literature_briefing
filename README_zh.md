# 文献简报生成器

自动从 PubMed 和 arXiv 获取最新文献，通过 LLM 翻译并生成 Markdown 简报。

## 功能

- **多文献源**：PubMed（核心期刊 + 关键词扩展搜索）和 arXiv
- **多 LLM 支持**：OpenRouter、OpenAI、Google Gemini、Anthropic Claude — 纯 HTTP 调用，零 SDK 依赖
- **自动翻译**：标题和摘要翻译为中文
- **本期亮点**：LLM 自动挑选值得关注的论文
- **GUI 设置界面**：基于 tkinter 的可视化配置
- **定时任务**：Windows 任务计划集成

## 快速开始

1. 克隆仓库，运行 `setup.bat`
2. 编辑 `config.json`，填入 API Key 和期刊列表
3. 运行 `run_briefing.bat` 或等待定时任务触发

## 配置

将 `config.template.json` 复制为 `config.json`，填写：
- `output_path`：简报输出路径
- `llm.api_key`：LLM 提供商 API Key
- `sources.pubmed.api_key`：NCBI API Key（可选但推荐）

环境变量回退：`OPENROUTER_API_KEY`、`OPENAI_API_KEY`、`GEMINI_API_KEY`、`ANTHROPIC_API_KEY`、`PUBMED_API_KEY`

## 使用

```bash
# 运行简报
python -m literature_briefing.main

# 无弹窗模式
python -m literature_briefing.main --no-notify

# 打开设置界面
python -m gui.app
```

## 从旧版迁移

如果你之前使用的是单文件版本（`literature_briefing.py`），只需运行新版本，程序会自动将旧版 `config.json` 迁移为 v2 格式，不会丢失任何配置。

## 许可证

MIT
