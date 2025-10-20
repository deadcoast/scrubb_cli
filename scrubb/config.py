from __future__ import annotations
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict

APP_NAME = "scrubb"

def _platform_dirs() -> dict[str, Path]:
    home = Path.home()
    if sys.platform == "win32":
        base_config = Path(os.getenv("APPDATA", home / "AppData/Roaming"))
        base_state  = Path(os.getenv("LOCALAPPDATA", home / "AppData/Local"))
        base_data   = base_state
    else:
        base_config = Path(os.getenv("XDG_CONFIG_HOME", home / ".config"))
        base_state  = Path(os.getenv("XDG_STATE_HOME",  home / ".local/state"))
        base_data   = Path(os.getenv("XDG_DATA_HOME",   home / ".local/share"))
    return {
        "config_dir": base_config / APP_NAME,
        "state_dir":  base_state  / APP_NAME,
        "data_dir":   base_data   / APP_NAME,
    }

DIRS = _platform_dirs()
CONFIG_PATH = DIRS["config_dir"] / "config.json"
STATS_PATH  = DIRS["state_dir"]  / "stats.json"

DEFAULT_CONFIG: Dict[str, Any] = {
    "default_root": str(Path.cwd()),
    "ignore_patterns": [
        ".venv", "__pycache__", ".git", "node_modules", ".DS_Store",
        ".vscode", ".idea", "*.pyc", "*.pyo", "*.pyd", "*.so", "*.dll",
        "*.exe", "*.app", "*.dmg", "*.pkg", "*.zip", "*.tar.gz", "*.rar", "*.7z",
        "*.log", "*.tmp", "*.temp", "*.cache", "*.min.js", "*.min.css", "*.map",
        "package-lock.json", "yarn.lock", "poetry.lock",
    ],
    "text_extensions": [
        ".txt",".md",".rst",".adoc",".tex",".html",".htm",".xml",".json",".yaml",".yml",".toml",".ini",".cfg",".conf",
        ".py",".js",".ts",".jsx",".tsx",".vue",".php",".rb",".java",".c",".cpp",".h",".hpp",".cs",".go",".rs",".swift",".kt",".scala",
        ".clj",".hs",".ml",".fs",".sql",".sh",".bash",".zsh",".fish",".ps1",".bat",".css",".scss",".sass",".less",".styl",
        ".dockerfile",".gitignore",".gitattributes","readme","license","changelog","contributing",
    ],
}

DEFAULT_STATS: Dict[str, Any] = {
    "runs": 0,
    "files_processed": 0,
    "files_modified": 0,
    "files_skipped": 0,
    "errors": 0,
    "emojis_removed": 0,
    "scoped_scrub": {},      # emoji -> total count
}

def ensure_dirs() -> None:
    for p in DIRS.values():
        p.mkdir(parents=True, exist_ok=True)

def load_config() -> Dict[str, Any]:
    ensure_dirs()
    if CONFIG_PATH.exists():
        try:
            return {**DEFAULT_CONFIG, **json.loads(CONFIG_PATH.read_text(encoding="utf-8"))}
        except Exception:
            return DEFAULT_CONFIG.copy()
    return DEFAULT_CONFIG.copy()

def save_config(cfg: Dict[str, Any]) -> None:
    ensure_dirs()
    CONFIG_PATH.write_text(json.dumps(cfg, indent=2, ensure_ascii=False), encoding="utf-8")

def load_stats() -> Dict[str, Any]:
    ensure_dirs()
    if STATS_PATH.exists():
        try:
            data = json.loads(STATS_PATH.read_text(encoding="utf-8"))
            # backfill missing keys
            merged = DEFAULT_STATS.copy()
            merged.update(data)
            merged["scoped_scrub"] = merged.get("scoped_scrub", {})
            return merged
        except Exception:
            return DEFAULT_STATS.copy()
    return DEFAULT_STATS.copy()

def save_stats(stats: Dict[str, Any]) -> None:
    ensure_dirs()
    STATS_PATH.write_text(json.dumps(stats, indent=2, ensure_ascii=False), encoding="utf-8")