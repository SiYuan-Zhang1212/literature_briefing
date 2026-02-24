"""配置加载、保存、迁移、校验"""

import json
import os
import logging

log = logging.getLogger(__name__)

SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(SCRIPT_DIR, "config.json")

DEFAULT_CONFIG = {
    "config_version": 2,
    "output_path": "",
    "output_folder": "文献简报",
    "default_lookback_days": 7,
    "max_results": 200,
    "llm": {
        "provider": "openrouter",
        "api_key": "",
        "model": "google/gemini-2.0-flash-001",
        "temperature": 0.1,
        "enable_translation": True,
        "enable_highlights": True,
    },
    "sources": {
        "pubmed": {
            "enabled": True,
            "api_key": "",
            "core_journals": [],
            "extended_journals": [],
            "keywords": [],
            "species_filter": [],
        },
        "arxiv": {
            "enabled": False,
            "categories": [],
            "keywords": [],
        },
    },
    "schedule": {
        "delay_minutes": 20,
        "show_popup": True,
        "popup_timeout_sec": 30,
    },
}


def _migrate_v1(old: dict) -> dict:
    """将 v1 配置（无 config_version）迁移为 v2 格式"""
    cfg = json.loads(json.dumps(DEFAULT_CONFIG))  # deep copy
    cfg["output_path"] = old.get("obsidian_vault", "")
    cfg["output_folder"] = old.get("briefing_folder", "文献简报")
    cfg["default_lookback_days"] = old.get("default_lookback_days", 7)
    cfg["max_results"] = old.get("max_results", 200)
    # LLM
    cfg["llm"]["provider"] = "openrouter"
    cfg["llm"]["api_key"] = old.get("openrouter_api_key", "") or os.environ.get("OPENROUTER_API_KEY", "")
    cfg["llm"]["model"] = old.get("openrouter_model", "google/gemini-2.0-flash-001")
    # PubMed
    pm = cfg["sources"]["pubmed"]
    pm["api_key"] = old.get("pubmed_api_key", "")
    pm["core_journals"] = old.get("core_journals", [])
    pm["extended_journals"] = old.get("extended_journals", [])
    pm["keywords"] = old.get("keywords", [])
    pm["species_filter"] = old.get("species_filter", [])
    return cfg


def load_config(path: str = None) -> dict:
    """加载配置，自动迁移旧版本"""
    path = path or CONFIG_PATH
    if not os.path.exists(path):
        log.warning(f"配置文件不存在: {path}，使用默认配置")
        return json.loads(json.dumps(DEFAULT_CONFIG))

    with open(path, "r", encoding="utf-8") as f:
        raw = json.load(f)

    if "config_version" not in raw:
        log.info("检测到 v1 配置，自动迁移为 v2 格式")
        cfg = _migrate_v1(raw)
        save_config(cfg, path)
        return cfg

    # 补全缺失字段
    merged = json.loads(json.dumps(DEFAULT_CONFIG))
    _deep_merge(merged, raw)
    return merged


def _deep_merge(base: dict, override: dict):
    """递归合并，override 覆盖 base"""
    for k, v in override.items():
        if k in base and isinstance(base[k], dict) and isinstance(v, dict):
            _deep_merge(base[k], v)
        else:
            base[k] = v


def save_config(cfg: dict, path: str = None):
    """保存配置到文件"""
    path = path or CONFIG_PATH
    with open(path, "w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)
    log.info(f"配置已保存: {path}")


def get_env_fallback(cfg: dict) -> dict:
    """环境变量回退：如果配置中 API key 为空，尝试从环境变量读取"""
    cfg = json.loads(json.dumps(cfg))  # deep copy
    if not cfg["llm"]["api_key"]:
        provider = cfg["llm"]["provider"]
        env_map = {
            "openrouter": "OPENROUTER_API_KEY",
            "openai": "OPENAI_API_KEY",
            "gemini": "GEMINI_API_KEY",
            "claude": "ANTHROPIC_API_KEY",
        }
        env_key = env_map.get(provider, "")
        if env_key:
            cfg["llm"]["api_key"] = os.environ.get(env_key, "")
    if not cfg["sources"]["pubmed"]["api_key"]:
        cfg["sources"]["pubmed"]["api_key"] = os.environ.get("PUBMED_API_KEY", "")
    return cfg
