# **scrubb**

> Emoji Scrubber CLI
  Persistent cross-run stats **and** ephemeral per-run stats, packaged as a native CLI you can install and call directly as `scrubb`.

---

## Usage

```bash
scrubb .                 # scrub from configured default root
scrubb src .             # scrub configured-root/src
scrubb /path/to/dir .    # scrub an absolute/relative path
scrubb stats             # show global/persistent stats
scrubb stats --top       # show top 5 scrubbed emoji (persistent)
scrubb config -p --show  # show configured default root
scrubb config -p /code   # set default root to /code
```

---

## Project Layout

```text
scrubb/
  __init__.py
  cli.py            # Typer CLI (entrypoint)
  config.py         # config & state locations (XDG/Windows-safe), load/save helpers
  ignore.py         # default ignore patterns + matcher
  scrubber.py       # core scrub logic, per-run (ephemeral) stats
pyproject.toml      # install + console_script = scrubb
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

## How stats work

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

## Install & Use

```bash
# from the folder containing pyproject.toml
pip install .
# or: pipx install .
# then:
scrubb .                # scrub configured root
scrubb src .            # scrub configured-root/src
scrubb /path/to/dir .   # scrub explicit path
scrubb stats            # persistent stats
scrubb stats --top
scrubb config -p --show
scrubb config -p ~/code --edit
```

---
