# scrubb

> **Emoji Scrubber & Folder Organizer CLI** - Remove emojis from text files and organize cluttered directories

A command-line tool that removes emojis from text files across your codebase and organizes files into categorized folders, with comprehensive statistics tracking and configurable ignore patterns.

## Features

### Emoji Scrubbing
- **Smart Emoji Detection**: Removes emojis from a wide range of Unicode ranges including emoticons, symbols, flags, and more
- **Persistent Statistics**: Tracks global statistics across all runs with detailed per-emoji breakdowns
- **Configurable Ignore Patterns**: Skip common directories like `node_modules`, `.git`, `__pycache__`, etc.
- **Safe File Processing**: Only processes text files with recognized extensions

### Folder Cleanup
- **Automatic File Categorization**: Organizes files by type (Images, Video, Documents, Development)
- **Dry-Run Mode**: Preview all changes before executing with `--dry` flag
- **Smart Conflict Resolution**: Handles duplicate file names with incremental numbering
- **Empty Folder Removal**: Automatically cleans up empty directories after organization
- **Recursive Processing**: Scans and organizes files at all directory depths
- **Detailed Statistics**: Reports files moved, categories used, and folders removed

### General
- **Cross-Platform**: Works on Windows, macOS, and Linux with proper XDG compliance
- **Flexible Path Resolution**: Supports relative paths, absolute paths, and subdirectory targeting

## Installation

From the project directory:

```bash
pip install .
# or using pipx for isolated installation
pipx install .
```

## Quick Start

### Emoji Scrubbing
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

### Folder Cleanup
```bash
# Preview changes without executing (dry-run mode)
scrubb --folder --dry
# (You'll be prompted to enter the directory path)

# Organize files in a directory (actual execution)
scrubb --folder
# (You'll be prompted to enter the directory path)

# Files will be organized into:
# - Scrubbed/Images/
# - Scrubbed/Video/
# - Scrubbed/Docs/Markdown/
# - Scrubbed/Docs/Other Docs/
# - Scrubbed/Development/
```

## Usage

### Emoji Scrubbing Commands

```bash
scrubb [PATH] [EXECUTOR]
```

- `PATH`: Optional path or subpath (defaults to configured root)
- `EXECUTOR`: Use `.` to indicate recursive processing (required)

#### Examples

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

### Folder Cleanup Command

```bash
# Preview mode (recommended first)
scrubb --folder --dry

# Actual execution
scrubb --folder
```

#### Dry-Run Mode (Preview)

Before making any changes, use dry-run mode to preview what will happen:

```bash
scrubb --folder --dry
```

**Dry-run mode provides:**
- Complete list of files that would be moved with source and destination paths
- Detection of name conflicts and how they would be resolved
- List of directories that would be created
- List of empty directories that would be removed
- Files that would be skipped (unknown extensions)
- Potential errors (permission issues, inaccessible files)
- Detailed statistics for all operations

**Important**: Dry-run mode makes NO changes to your file system. It's a safe way to verify the cleanup behavior before committing to changes.

#### Regular Mode (Execution)

When you run the command without `--dry`:
1. You'll be prompted to enter a directory path
2. The system validates the path exists
3. All files are recursively scanned and categorized by type
4. Files are moved to organized subdirectories within a "Scrubbed" folder
5. Empty directories are automatically removed
6. Statistics are displayed showing the results

#### Folder Cleanup Workflow

```
Your Directory/
├── photo.jpg          →  Scrubbed/Images/photo.jpg
├── video.mp4          →  Scrubbed/Video/video.mp4
├── notes.md           →  Scrubbed/Docs/Markdown/notes.md
├── report.pdf         →  Scrubbed/Docs/Other Docs/report.pdf
├── script.py          →  Scrubbed/Development/script.py
└── nested/
    └── file.txt       →  Scrubbed/Docs/Other Docs/file.txt
```

After cleanup, empty directories (like `nested/`) are automatically removed.

#### File Type Categories

The folder cleanup feature organizes files into these categories:

**Images** (`Scrubbed/Images/`)
- Extensions: `.jpg`, `.jpeg`, `.png`, `.gif`, `.bmp`, `.svg`, `.webp`, `.ico`, `.tiff`, `.tif`

**Video** (`Scrubbed/Video/`)
- Extensions: `.mp4`, `.avi`, `.mov`, `.mkv`, `.flv`, `.wmv`, `.webm`, `.m4v`, `.mpeg`, `.mpg`

**Markdown Documents** (`Scrubbed/Docs/Markdown/`)
- Extensions: `.md`, `.markdown`

**Other Documents** (`Scrubbed/Docs/Other Docs/`)
- Extensions: `.pdf`, `.doc`, `.docx`, `.txt`, `.rtf`, `.odt`, `.xls`, `.xlsx`, `.ppt`, `.pptx`, `.csv`

**Development Files** (`Scrubbed/Development/`)
- Extensions: `.py`, `.js`, `.ts`, `.jsx`, `.tsx`, `.java`, `.c`, `.cpp`, `.h`, `.hpp`, `.rs`, `.go`, `.rb`, `.php`, `.html`, `.css`, `.scss`, `.json`, `.xml`, `.yaml`, `.yml`, `.toml`, `.sh`, `.bash`, `.sql`, `.r`, `.swift`, `.kt`

**Note**: Files with unrecognized extensions or no extension are skipped and remain in their original location.

#### Comparison: Dry-Run vs Regular Mode

| Feature | Dry-Run Mode (`--dry`) | Regular Mode |
|---------|------------------------|--------------|
| **File System Changes** | None - completely safe | Files moved, directories created/removed |
| **Output Detail** | Comprehensive preview with all planned operations | Concise summary of completed operations |
| **Conflict Information** | Shows all conflicts and how they'd be resolved | Resolves conflicts automatically |
| **Directory Listing** | Lists all directories to create/remove | Creates/removes without listing |
| **Skipped Files** | Lists all skipped files with reasons | Skips silently |
| **Potential Errors** | Detects and reports permission issues | Encounters errors during execution |
| **Use Case** | Verify behavior before committing | Execute the actual cleanup |

**Recommended Workflow:**
1. Run `scrubb --folder --dry` first to preview changes
2. Review the detailed output to ensure everything looks correct
3. Run `scrubb --folder` to execute the actual cleanup

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
 file_classifier.py  # File type classification for folder cleanup
 folder_organizer.py # Folder organization and cleanup logic
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
