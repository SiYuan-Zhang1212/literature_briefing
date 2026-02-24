# Literature Briefing

Automated literature briefing generator that fetches recent papers from PubMed and arXiv, translates them via LLM, and generates Markdown reports.

## Features

- **Multi-source**: PubMed (core + keyword search) and arXiv
- **Multi-LLM**: OpenRouter, OpenAI, Google Gemini, Anthropic Claude — all via raw HTTP, zero SDK dependencies
- **Auto-translation**: Titles and abstracts translated to Chinese
- **Highlights**: LLM-generated "papers to watch" section
- **GUI settings**: tkinter-based configuration interface
- **Scheduled task**: Windows Task Scheduler integration

## Quick Start

1. Clone the repo and run `setup.bat`
2. Edit `config.json` with your API keys and journal lists
3. Run `run_briefing.bat` or wait for the scheduled task

## Configuration

Copy `config.template.json` to `config.json` and fill in:
- `output_path`: where to save briefing files
- `llm.api_key`: your LLM provider API key
- `sources.pubmed.api_key`: NCBI API key (optional but recommended)

Environment variable fallbacks: `OPENROUTER_API_KEY`, `OPENAI_API_KEY`, `GEMINI_API_KEY`, `ANTHROPIC_API_KEY`, `PUBMED_API_KEY`

## Usage

```bash
# Run briefing
python -m literature_briefing.main

# Run without popup notifications
python -m literature_briefing.main --no-notify

# Open settings GUI
python -m gui.app
```

## Project Structure

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

## License

MIT
