# scrubb Command Reference

## Quick Command Table

| Command | Description | Function |
|---------|-------------|----------|
| `scrubb main [PATH] .` | Scrub emojis from files/directories | Remove emojis from text files with detailed output |
| `scrubb stats` | Show persistent statistics | Display accumulated statistics across all runs |
| `scrubb stats --top` | Show top 5 emoji tokens | Display most frequently removed emoji tokens |
| `scrubb stats --reset` | Reset all statistics | Clear all persistent statistics |
| `scrubb config` | Show configuration | Display current configuration and file locations |
| `scrubb config --show` | Show configuration | Same as `scrubb config` (explicit) |
| `scrubb config -p PATH --edit` | Set default root | Update the default root directory path |
| `scrubb --help` | Show help | Display general help information |
| `scrubb COMMAND --help` | Show command help | Display detailed help for specific command |

---

## Full Command Reference

### Main Command: `scrubb main`

**Purpose**: Remove emojis from text files and directories with comprehensive tracking.

**Syntax**:
```bash
scrubb main [PATH] [EXECUTOR]
```

**Parameters**:
- `PATH` (optional): Target path or subpath
  - If omitted: Uses configured default root
  - If relative path: Resolved relative to default root
  - If absolute path: Used directly
  - Examples: `src`, `./docs`, `/home/user/projects`
- `EXECUTOR` (required): Must be `.` to indicate recursive processing

**Examples**:
```bash
# Scrub from configured default root
scrubb main .

# Scrub a subdirectory under default root
scrubb main src .

# Scrub an absolute or relative path
scrubb main ./docs .
scrubb main /home/user/projects .
```

**Output**: Displays comprehensive run statistics including:
- Files processed, modified, skipped, and errors
- Number of emojis removed
- List of modified files (with `[+]` indicators)
- List of error files (with `[X]` indicators)
- Top 5 emoji tokens removed (with codepoint counts)

**Exit Codes**:
- `0`: Success
- `1`: General error
- `2`: Path not found

---

### Statistics Command: `scrubb stats`

**Purpose**: View persistent statistics accumulated across all scrubbing runs.

**Syntax**:
```bash
scrubb stats [OPTIONS]
```

**Options**:
- `--top`: Show top 5 most frequently removed emoji tokens
- `--reset`: Reset all persistent statistics to zero
- `--help`: Show detailed help for this command

**Examples**:
```bash
# View basic statistics
scrubb stats

# Show top emoji tokens
scrubb stats --top

# Reset all statistics
scrubb stats --reset
```

**Output**: Displays persistent statistics including:
- Total runs executed
- Total files processed, modified, skipped
- Total errors encountered
- Total emojis removed
- (with `--top`) Top 5 emoji tokens with removal counts

**Statistics Location**:
- **macOS/Linux**: `~/.local/state/scrubb/stats.json`
- **Windows**: `%LOCALAPPDATA%\scrubb\stats.json`

---

### Configuration Command: `scrubb config`

**Purpose**: Manage scrubb configuration settings and view current configuration.

**Syntax**:
```bash
scrubb config [OPTIONS]
```

**Options**:
- `-p PATH`: Specify a path for configuration operations
- `--show`: Show current configuration (default behavior)
- `--edit`: Apply changes (requires `-p` flag)
- `--help`: Show detailed help for this command

**Examples**:
```bash
# Show current configuration (default)
scrubb config

# Show current configuration (explicit)
scrubb config --show

# Set new default root directory
scrubb config -p /path/to/code --edit

# Set new default root with tilde expansion
scrubb config -p ~/projects --edit
```

**Configuration Display**: Shows:
- Current default root directory
- Configuration file location
- Statistics file location
- Number of ignore patterns configured
- Number of text extensions configured

**Configuration Location**:
- **macOS/Linux**: `~/.config/scrubb/config.json`
- **Windows**: `%APPDATA%\scrubb\config.json`

**Error Handling**:
- Requires `--edit` flag when using `-p` to update configuration
- Requires `-p` path when using `--edit` flag
- Provides helpful error messages with usage examples

---

### Help Commands

#### General Help: `scrubb --help`
**Purpose**: Display general help information and available commands.

**Syntax**:
```bash
scrubb --help
```

**Output**: Shows:
- General usage information
- Available options
- List of available commands with brief descriptions

#### Command-Specific Help: `scrubb COMMAND --help`
**Purpose**: Display detailed help for specific commands.

**Syntax**:
```bash
scrubb main --help
scrubb stats --help
scrubb config --help
```

**Output**: Shows:
- Detailed command syntax
- Parameter descriptions
- Option explanations
- Usage examples

---

## Configuration Details

### Default Settings

**Ignore Patterns** (30 patterns):
- Build directories: `.venv`, `__pycache__`, `.git`, `node_modules`
- System files: `.DS_Store`, `.vscode`, `.idea`
- Binary files: `*.pyc`, `*.exe`, `*.dll`, `*.so`
- Archives: `*.zip`, `*.tar.gz`, `*.rar`
- Logs and cache: `*.log`, `*.tmp`, `*.cache`

**Text Extensions** (57 extensions):
- Documentation: `.txt`, `.md`, `.rst`, `.html`
- Configuration: `.json`, `.yaml`, `.toml`, `.ini`
- Source code: `.py`, `.js`, `.ts`, `.java`, `.c`, `.cpp`
- Styles: `.css`, `.scss`, `.sass`
- Shell scripts: `.sh`, `.bash`, `.ps1`

### Unicode Coverage

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

---

## Usage Patterns

### Common Workflows

**Initial Setup**:
```bash
# Install the tool
pip install .

# Configure default root directory
scrubb config -p /path/to/your/projects --edit

# Verify configuration
scrubb config
```

**Regular Usage**:
```bash
# Scrub current project
scrubb main .

# Scrub specific directory
scrubb main src .

# Check statistics
scrubb stats

# View top emojis removed
scrubb stats --top
```

**Maintenance**:
```bash
# Reset statistics if needed
scrubb stats --reset

# Update default root
scrubb config -p /new/path --edit
```

### Output Interpretation

**Per-Run Output**:
```
scrubb run: files_processed=42 modified=3 skipped=39 errors=0 emojis_removed=15

Modified files:
  [+] /path/to/file1.md
  [+] /path/to/file2.txt

Emoji tokens removed:
  #1: 8 codepoints
  #2: 4 codepoints
  #3: 3 codepoints
```

**Statistics Output**:
```
runs:            5
files_processed: 127
files_modified:  8
files_skipped:   119
errors:          0
emojis_removed:  45
```

---

## Requirements

- **Python**: 3.10 or higher
- **Dependencies**: typer >= 0.12.3
- **Platform**: Windows, macOS, Linux (with proper XDG compliance)

## Installation

```bash
# From project directory
pip install .

# Or using pipx for isolated installation
pipx install .
```

---

*This command reference covers all available commands and options for scrubb v0.1.0*
