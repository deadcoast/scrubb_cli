# **scrubb**

> Emoji Scrubber & Folder Organizer CLI
  Persistent cross-run stats **and** ephemeral per-run stats, packaged as a native CLI you can install and call directly as `scrubb`.

---

## Usage

### Emoji Scrubbing
```bash
scrubb .                 # scrub from configured default root
scrubb src .             # scrub configured-root/src
scrubb /path/to/dir .    # scrub an absolute/relative path
scrubb stats             # show global/persistent stats
scrubb stats --top       # show top 5 scrubbed emoji (persistent)
scrubb config -p --show  # show configured default root
scrubb config -p /code   # set default root to /code
```

### Folder Cleanup
```bash
scrubb --folder --dry    # preview changes without executing (dry-run mode)
scrubb --folder          # organize files into categorized folders
                         # (prompts for directory path)
```

---

## Project Layout

```text
scrubb/
  __init__.py
  cli.py              # Typer CLI (entrypoint)
  config.py           # config & state locations (XDG/Windows-safe), load/save helpers
  ignore.py           # default ignore patterns + matcher
  scrubber.py         # core scrub logic, per-run (ephemeral) stats
  file_classifier.py  # file type classification for folder cleanup
  folder_organizer.py # folder organization and cleanup logic
pyproject.toml        # install + console_script = scrubb
```

---

### `pyproject.toml`

```toml
[project]
name = "scrubb"
version = "0.1.0"
description = "Emoji Scrubber CLI"
readme = "README.md"
requires-python = ">=3.10"
dependencies = ["typer>=0.12.3"]

[project.scripts]
scrubb = "scrubb.cli:app"  # Typer app is callable directly

[build-system]
requires = ["setuptools>=68", "wheel"]
build-backend = "setuptools.build_meta"
```

---

## How it works

### Emoji Scrubbing Stats

* **Ephemeral (per-run)**: Always printed after each `scrubb` execution:

  ```bash
  scrubb run: files_processed=… modified=… skipped=… errors=… emojis_removed=…
  ```

* **Persistent (global)**: Accumulated in a JSON file:

  * macOS/Linux: `~/.local/state/scrubb/stats.json` (XDG-compliant)
  * Windows: `%LOCALAPPDATA%\scrubb\stats.json`
  * View with `scrubb stats` (and `--top`), reset with `scrubb stats --reset`.

Top entries measure how many **codepoints removed** for each emoji token (consecutive emoji sequences are tracked as tokens). It’s fast and robust without extra deps.

---

### Folder Cleanup

* **Dry-Run Mode**: Preview all changes with `--dry` flag before executing (no file system modifications)
* **File Classification**: Files are categorized by extension into Images, Video, Documents, Markdown, and Development
* **Organization**: Files are moved to `Scrubbed/` subdirectories based on their category
* **Conflict Resolution**: Duplicate file names get numeric suffixes (`file_1.txt`, `file_2.txt`, etc.)
* **Cleanup**: Empty directories are automatically removed after file moves
* **Statistics**: Displays files moved per category, empty folders removed, and any errors encountered

---

## Install & Use

```bash
# from the folder containing pyproject.toml
pip install .
# or: pipx install .
# then:
scrubb .                # scrub configured root
scrubb src .            # scrub configured-root/src
scrubb /path/to/dir .   # scrub explicit path
scrubb --folder --dry   # preview folder cleanup (dry-run)
scrubb --folder         # organize files into categories
scrubb stats            # persistent stats
scrubb stats --top
scrubb config -p --show
scrubb config -p ~/code --edit
```

---
