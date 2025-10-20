# scrubb

> **Emoji Scrubber CLI** - Remove emojis from text files with persistent statistics

A command-line tool that removes emojis from text files across your codebase, with comprehensive statistics tracking and configurable ignore patterns.

## Features

- **Smart Emoji Detection**: Removes emojis from a wide range of Unicode ranges including emoticons, symbols, flags, and more
- **Persistent Statistics**: Tracks global statistics across all runs with detailed per-emoji breakdowns
- **Configurable Ignore Patterns**: Skip common directories like `node_modules`, `.git`, `__pycache__`, etc.
- **Cross-Platform**: Works on Windows, macOS, and Linux with proper XDG compliance
- **Flexible Path Resolution**: Supports relative paths, absolute paths, and subdirectory targeting
- **Safe File Processing**: Only processes text files with recognized extensions

## Installation

From the project directory:

```bash
pip install .
# or using pipx for isolated installation
pipx install .
```

## Quick Start

```bash
# Scrub emojis from current directory
scrubb .

# Scrub a specific subdirectory
scrubb src .

# Scrub a specific path
scrubb /path/to/directory .

# View persistent statistics
scrubb stats

# Show top 5 most removed emojis
scrubb stats --top

# Configure default root directory
scrubb config -p /path/to/code --edit
```

## Usage

### Basic Commands

```bash
scrubb [PATH] [EXECUTOR]
```

- `PATH`: Optional path or subpath (defaults to configured root)
- `EXECUTOR`: Use `.` to indicate recursive processing (required)

### Examples

```bash
# Scrub from configured default root
scrubb .

# Scrub a subdirectory under default root
scrubb src .

# Scrub an absolute or relative path
scrubb ./docs .
scrubb /home/user/projects .

# Show current configuration
scrubb config -p --show

# Set new default root
scrubb config -p /path/to/code --edit
```

### Statistics Commands

```bash
# View global statistics
scrubb stats

# Show top 5 most removed emoji tokens
scrubb stats --top

# Reset all persistent statistics
scrubb stats --reset
```

### Configuration Commands

```bash
# Show current configuration and file locations
scrubb config -p --show

# Set new default root directory
scrubb config -p /path/to/code --edit
```

## Statistics

scrubb tracks two types of statistics:

### Per-Run Statistics (Ephemeral)
Always displayed after each run:
```
scrubb run: files_processed=42 modified=3 skipped=39 errors=0 emojis_removed=15
```

### Persistent Statistics (Global)
Accumulated across all runs and stored in:
- **macOS/Linux**: `~/.local/state/scrubb/stats.json`
- **Windows**: `%LOCALAPPDATA%\scrubb\stats.json`

Persistent stats include:
- Total runs
- Files processed, modified, skipped
- Total emojis removed
- Per-emoji token counts (top 5 with `--top`)

## Configuration

### File Locations

- **Config**: `~/.config/scrubb/config.json` (XDG-compliant)
- **Stats**: `~/.local/state/scrubb/stats.json` (XDG-compliant)
- **Windows**: Uses `%APPDATA%` and `%LOCALAPPDATA%` respectively

### Default Settings

**Ignore Patterns:**
- Common build directories: `.venv`, `__pycache__`, `.git`, `node_modules`
- System files: `.DS_Store`, `.vscode`, `.idea`
- Binary files: `*.pyc`, `*.exe`, `*.dll`, `*.so`
- Archives: `*.zip`, `*.tar.gz`, `*.rar`
- Logs and cache: `*.log`, `*.tmp`, `*.cache`

**Text Extensions:**
- Documentation: `.txt`, `.md`, `.rst`, `.html`
- Configuration: `.json`, `.yaml`, `.toml`, `.ini`
- Source code: `.py`, `.js`, `.ts`, `.java`, `.c`, `.cpp`
- Styles: `.css`, `.scss`, `.sass`
- Shell scripts: `.sh`, `.bash`, `.ps1`

## Project Structure

```
scrubb/
 __init__.py          # Package initialization
 cli.py              # Typer CLI entrypoint and commands
 config.py           # Configuration management and XDG paths
 ignore.py           # File ignore pattern matching
 scrubber.py         # Core emoji removal logic and statistics
```

## Requirements

- Python 3.10+
- typer >= 0.12.3

## How It Works

1. **Path Resolution**: Resolves target paths relative to configured default root
2. **File Filtering**: Applies ignore patterns and checks file extensions
3. **Emoji Detection**: Uses comprehensive Unicode regex patterns to find emojis
4. **Text Processing**: Removes emoji sequences while preserving text structure
5. **Statistics Tracking**: Updates both per-run and persistent statistics
6. **Safe Writing**: Only modifies files that actually contain emojis

## Unicode Coverage

The tool detects and removes emojis from these Unicode ranges:
- Emoticons (U+1F600-U+1F64F)
- Symbols & Pictographs (U+1F300-U+1F5FF)
- Transport & Map Symbols (U+1F680-U+1F6FF)
- Flags (U+1F1E0-U+1F1FF)
- Dingbats (U+2702-U+27B0)
- Enclosed Characters (U+24C2-U+1F251)
- Supplemental Symbols (U+1F900-U+1F9FF)
- Miscellaneous Symbols (U+2600-U+26FF)
- Skin Tones & Modifiers (U+1F3FB-U+1F3FF)

## License

This project is available under the MIT License.
