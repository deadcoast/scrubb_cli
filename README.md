# scrubb

> **Multi Function Scrubber CLI** - `scrubb`
- Remove emojis from document / code files
- Organize cluttered directories and clean them up

`scrubb` Is a command-line tool that removes emojis from text files across your codebase and organizes files into categorized folders, with comprehensive statistics tracking and configurable ignore patterns.

## Features

### Emoji Scrubbing
- **Smart Emoji Detection**: Removes emojis from a wide range of Unicode ranges including emoticons, symbols, flags, and more
- **Persistent Statistics**: Tracks global statistics across all runs with detailed per-emoji breakdowns
- **Configurable Ignore Patterns**: Skip common directories like `node_modules`, `.git`, `__pycache__`, etc.
- **Safe File Processing**: Only processes text files with recognized extensions

### Folder Cleanup
- **Automatic File Categorization**: Organizes files by type (Images, Video, Documents, Development)
- **Tree Visualization**: Visual before/after directory trees with comprehensive statistics using `--tree` flag
- **Dry-Run Mode**: Preview all changes before executing with `--dry` flag
- **Smart Conflict Resolution**: Handles duplicate file names with incremental numbering
- **Empty Folder Removal**: Automatically cleans up empty directories after organization (including removal of hidden system files like `.DS_Store`, `Thumbs.db`)
- **Recursive Processing**: Scans and organizes files at all directory depths
- **Detailed Statistics**: Reports files moved, categories used, and folders removed

### General
- **Cross-Platform**: Works on Windows, macOS, and Linux with proper XDG compliance
- **Flexible Path Resolution**: Supports relative paths, absolute paths, and subdirectory targeting

## Installation

This project uses the [UV](https://docs.astral.sh/uv/) ecosystem for fast, reliable Python package management.

### Installing UV

If you don't have UV installed yet:

**macOS/Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows:**
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**Alternative (using pip):**
```bash
pip install uv
```

For more installation options, see the [UV installation guide](https://docs.astral.sh/uv/getting-started/installation/).

### Installing scrubb

From the project directory:

```bash
# Install in development mode (recommended for development)
uv pip install -e .

# Or install normally
uv pip install .

# Or use uvx to run without installing (requires UV 0.4.0+)
uvx --from . scrubb --help
```

**Note**: UV automatically manages virtual environments and dependencies, making installation faster and more reliable than traditional pip.

## Quick Start

### Emoji Scrubbing
```bash
# Scrub emojis from current directory
scrubb emoji .
# Or use the shorthand alias
scrubb e .

# Scrub a specific subdirectory
scrubb emoji src .

# Scrub a specific path
scrubb emoji /path/to/directory .

# View persistent statistics
scrubb stats
# Or use the shorthand alias
scrubb s

# Show top 5 most removed emojis
scrubb stats --top

# Configure default root directory
scrubb config -p /path/to/code --edit
# Or use the shorthand alias
scrubb c -p /path/to/code --edit
```

**Tip**: All commands support shorthand aliases for faster typing. See [Command Aliases](#command-aliases) for the complete list.

### Folder Cleanup
```bash
# Preview changes without executing (dry-run mode)
scrubb folder --dry
# Or use the shorthand alias
scrubb f --dry
# (You'll be prompted to enter the directory path)

# Organize files in a directory (actual execution)
scrubb folder
# (You'll be prompted to confirm before making changes)

# Organize with visual tree display (recommended)
scrubb folder --tree
# Shows before/after directory trees with statistics

# Preview with tree visualization (best for first-time use)
scrubb folder --tree --dry
# Shows current and simulated trees without making changes

# Skip confirmation prompt with auto-confirm flag
scrubb folder --yes
# Proceeds without asking for confirmation

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
scrubb emoji [PATH] [EXECUTOR]
# Or use the alias
scrubb e [PATH] [EXECUTOR]
```

- `PATH`: Optional path or subpath (defaults to configured root)
- `EXECUTOR`: Use `.` to indicate recursive processing (required)

#### Examples

```bash
# Scrub from configured default root
scrubb emoji .
scrubb e .  # Using alias

# Scrub a subdirectory under default root
scrubb emoji src .

# Scrub an absolute or relative path
scrubb emoji ./docs .
scrubb emoji /home/user/projects .

# With verbosity control
scrubb emoji . --verbose  # Show detailed debug information
scrubb emoji . --quiet    # Suppress non-essential output

# Show current configuration
scrubb config -p --show
scrubb c -p --show  # Using alias

# Set new default root
scrubb config -p /path/to/code --edit
```

### Folder Cleanup Command

```bash
# Preview mode (recommended first)
scrubb folder --dry
scrubb f --dry  # Using alias

# Actual execution (will prompt for confirmation)
scrubb folder

# With tree visualization (recommended)
scrubb folder --tree

# Preview with tree visualization
scrubb folder --tree --dry

# Skip confirmation prompt
scrubb folder --yes

# With verbosity control
scrubb folder --verbose  # Show detailed debug information
scrubb folder --quiet    # Suppress non-essential output
```

#### Dry-Run Mode (Preview)

Before making any changes, use dry-run mode to preview what will happen:

```bash
scrubb folder --dry
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
 photo.jpg          →  Scrubbed/Images/photo.jpg
 video.mp4          →  Scrubbed/Video/video.mp4
 notes.md           →  Scrubbed/Docs/Markdown/notes.md
 report.pdf         →  Scrubbed/Docs/Other Docs/report.pdf
 script.py          →  Scrubbed/Development/script.py
 nested/
     file.txt       →  Scrubbed/Docs/Other Docs/file.txt
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
1. Run `scrubb folder --tree --dry` first to preview changes with visual trees
2. Review the detailed output and tree visualization to ensure everything looks correct
3. Run `scrubb folder --tree` to execute the actual cleanup with visual confirmation

#### Confirmation Prompts

For safety, scrubb prompts for confirmation before performing destructive operations:

**Operations that require confirmation:**
- `scrubb folder` (when not in dry-run mode) - Before moving files
- `scrubb stats --reset` - Before clearing all statistics

**Example confirmation prompt:**
```bash
$ scrubb folder
Enter directory path: /path/to/messy/folder
[Scanning and analyzing files...]

About to move 42 files into organized folders.
Do you want to proceed? [y/N]: y
[Proceeding with file organization...]
```

**Responding to prompts:**
- Type `yes`, `y`, `Y`, or `YES` to proceed
- Type `no`, `n`, `N`, `NO`, or press Ctrl+C to cancel
- Press Enter to use the default (usually "no" for safety)

**Skip prompts with auto-confirm:**
```bash
# Use --yes flag to skip confirmation
scrubb folder --yes
scrubb stats --reset --yes
```

#### Tree Visualization

The `--tree` flag adds professional directory tree visualization to the folder cleanup command, making it easy to see structural changes before and after file organization.

**Example Output:**

```

BEFORE - Directory Structure

/path/to/directory
 photo.jpg
 video.mp4
 notes.md
 report.pdf
 script.py
 nested/
     file.txt

 Statistics:
  Files: 6
  Directories: 2
  Total Size: 2.4 MB
  Max Depth: 2
  
  Files by Category:
    Images: 1
    Video: 1
    Docs/Markdown: 1
    Docs/Other Docs: 2
    Development: 1


AFTER - Directory Structure

/path/to/directory
 Scrubbed/
     Images/
        photo.jpg
     Video/
        video.mp4
     Docs/
        Markdown/
           notes.md
        Other Docs/
            report.pdf
            file.txt
     Development/
         script.py

 Statistics:
  Files: 6
  Directories: 8
  Total Size: 2.4 MB
  Max Depth: 4


COMPARISON - Changes

  Files: 0 (no change)
  Directories: +6
  Total Size: 0 B (no change)
  Max Depth: +2
```

**Features:**
- **Visual Clarity**: See exact directory structure before and after organization
- **Comprehensive Statistics**: File counts, directory counts, total size, max depth, and category breakdowns
- **Change Tracking**: Clear comparison showing what changed (files moved, directories created/removed)
- **Color Coding**: Files color-coded by type for easy identification
- **Professional Formatting**: Uses box-drawing characters for clean, readable trees
- **Dry-Run Support**: Simulates after-state when used with `--dry` flag

**Usage:**
```bash
# Actual execution with tree visualization
scrubb folder --tree

# Preview with tree visualization (no changes made)
scrubb folder --tree --dry
```

**Benefits:**
- Verify file organization before committing changes
- Understand structural impact at a glance
- Debug categorization issues visually
- Document before/after states for record-keeping
- Confidence in cleanup operations

### Statistics Commands

```bash
# View global statistics
scrubb stats
scrubb s  # Using alias

# Show top 5 most removed emoji tokens
scrubb stats --top

# Reset all persistent statistics (will prompt for confirmation)
scrubb stats --reset

# Skip confirmation prompt when resetting
scrubb stats --reset --yes
```

### Configuration Commands

```bash
# Show current configuration and file locations
scrubb config -p --show
scrubb c -p --show  # Using alias

# Set new default root directory
scrubb config -p /path/to/code --edit
```

## Command Aliases

All scrubb commands support shorthand aliases for faster typing and improved workflow efficiency:

| Command | Alias | Description |
|---------|-------|-------------|
| `scrubb emoji` | `scrubb e` | Emoji scrubbing operations |
| `scrubb folder` | `scrubb f` | Folder cleanup and organization |
| `scrubb stats` | `scrubb s` | Statistics viewing and management |
| `scrubb config` | `scrubb c` | Configuration management |

**Examples:**
```bash
# These commands are equivalent
scrubb emoji .
scrubb e .

# These commands are equivalent
scrubb folder --tree --dry
scrubb f --tree --dry

# These commands are equivalent
scrubb stats --top
scrubb s --top

# These commands are equivalent
scrubb config -p --show
scrubb c -p --show
```

**Benefits:**
- Faster command entry for frequent operations
- Reduced typing for repetitive tasks
- Improved terminal workflow efficiency
- All aliases support the same options and flags as their full command names

## Verbosity Modes

Control the amount of output scrubb displays with verbosity flags. All commands support these flags:

### Verbose Mode (`--verbose` or `-v`)

Shows detailed debug information including file-by-file processing, timestamps, and internal operations.

**Use cases:**
- Debugging issues
- Understanding what scrubb is doing
- Monitoring progress on large operations
- Troubleshooting file processing

**Examples:**
```bash
# Verbose emoji scrubbing
scrubb emoji . --verbose
scrubb e . -v  # Short form

# Verbose folder cleanup
scrubb folder --verbose
scrubb f -v --tree  # Combine with other flags

# Verbose statistics
scrubb stats --verbose
```

**Verbose output includes:**
- File-by-file processing details
- Timestamps for each operation
- Debug information about decisions made
- Detailed error context
- Internal state information

### Quiet Mode (`--quiet` or `-q`)

Suppresses all non-essential output, showing only errors and critical warnings.

**Use cases:**
- Running in scripts or automation
- Reducing terminal clutter
- Focusing only on errors
- Batch processing

**Examples:**
```bash
# Quiet emoji scrubbing
scrubb emoji . --quiet
scrubb e . -q  # Short form

# Quiet folder cleanup
scrubb folder --quiet
scrubb f -q --yes  # Combine with auto-confirm for fully automated operation

# Quiet statistics
scrubb stats --quiet
```

**Quiet output includes:**
- Critical errors only
- Important warnings
- Final exit status

### Default Mode (No Flag)

Shows standard output with summary statistics and important information.

**Default output includes:**
- Summary statistics
- Files processed counts
- Important warnings
- Success/failure messages
- Progress indicators for long operations

**Comparison:**

| Output Type | Default | Verbose | Quiet |
|-------------|---------|---------|-------|
| Summary statistics |  |  |  |
| File-by-file details |  |  |  |
| Debug information |  |  |  |
| Timestamps |  |  |  |
| Errors |  |  |  |
| Warnings |  |  |  |

## Auto-Confirm Flag

The `--yes` (or `-y`) flag allows you to skip confirmation prompts for destructive operations, enabling fully automated workflows.

**Supported commands:**
- `scrubb folder --yes` - Skip confirmation before moving files
- `scrubb stats --reset --yes` - Skip confirmation before clearing statistics

**Examples:**
```bash
# Folder cleanup without confirmation
scrubb folder --yes
scrubb f -y  # Using alias and short form

# Reset statistics without confirmation
scrubb stats --reset --yes
scrubb s --reset -y  # Using alias and short form

# Combine with other flags
scrubb folder --tree --yes  # Tree visualization + auto-confirm
scrubb folder --quiet --yes  # Quiet mode + auto-confirm
scrubb f -q -y --tree  # All flags combined with alias
```

**Use cases:**
- Automated scripts and CI/CD pipelines
- Batch processing multiple directories
- Scheduled cleanup tasks
- When you're confident about the operation

**Safety considerations:**
- Always test with `--dry` flag first before using `--yes`
- Review the operation manually at least once
- Use with caution on important directories
- Consider using verbose mode initially: `scrubb folder --verbose --yes`

**Example automated workflow:**
```bash
# Safe automated workflow
# 1. Preview first
scrubb folder --dry --tree

# 2. Review the output, then execute with auto-confirm
scrubb folder --yes

# Or combine into a script
scrubb folder --dry && read -p "Proceed? " && scrubb folder --yes
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
 .archive/                    # Historical design documents
 .kiro/                       # Kiro specs and planning documents
    specs/                   # Feature specifications
 docs/                        # User documentation
    ARCHITECTURE.md          # System design and architecture
    COMMAND_REFERENCE.md     # Complete command-line reference
    dev/                     # Developer documentation
        CONTRIBUTING.md      # Contribution guidelines
        DOCUMENTATION_VALIDATION_PLAN.md
        EMPTY_FOLDER_FIX.md
        FIXES_SUMMARY.md
 examples/                    # Example scripts and demos
    demo_empty_folder_fix.py
 scripts/                     # Utility scripts
    update_links.py
    validate_docs.py
    verify_links.py
 scrubb/                      # Main package
    __init__.py              # Package initialization
    cli.py                   # Typer CLI entrypoint and commands
    config.py                # Configuration management and XDG paths
    directory_scanner.py    # Directory scanning functionality
    file_classifier.py      # File type classification for folder cleanup
    folder_organizer.py     # Folder organization and cleanup logic
    ignore.py                # File ignore pattern matching
    scrubber.py              # Core emoji removal logic and statistics
    statistics_calculator.py # Statistics calculation
    tree_comparator.py      # Tree comparison functionality
    tree_models.py           # Tree data models
    tree_renderer.py        # Tree rendering
    tree_visualizer.py      # Tree visualization
 tests/                       # Test suite
 CHANGELOG.md                 # Version history and changes
 pyproject.toml               # Project configuration and dependencies
 README.md                    # This file
```

## Requirements

- Python 3.10+
- UV (for package management)
- typer >= 0.12.3

## Development

### Setting Up Development Environment

```bash
# Clone the repository
git clone <repository-url>
cd scrubb

# Install in development mode with UV
uv pip install -e .

# Run tests
uv run pytest

# Run tests with coverage
uv run pytest --cov=scrubb --cov-report=html
```

### Running Tests

The project includes comprehensive test coverage with both unit tests and property-based tests:

```bash
# Run all tests
uv run pytest

# Run with verbose output
uv run pytest -v

# Run specific test file
uv run pytest tests/test_cli.py

# Run tests matching a pattern
uv run pytest -k "dry_run"
```

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


## Documentation

Comprehensive documentation is available to help you use and contribute to scrubb:

### User Documentation
- **[Command Reference](docs/COMMAND_REFERENCE.md)** - Complete command-line reference with all available commands and options
- **[Architecture](docs/ARCHITECTURE.md)** - System design, component overview, and architectural decisions

### Developer Documentation
- **[Contributing Guidelines](docs/dev/CONTRIBUTING.md)** - How to contribute to the project, coding standards, and development workflow
- **[Documentation Validation Plan](docs/dev/DOCUMENTATION_VALIDATION_PLAN.md)** - Documentation testing and validation procedures
- **[Empty Folder Fix](docs/dev/EMPTY_FOLDER_FIX.md)** - Technical details on empty folder handling
- **[Fixes Summary](docs/dev/FIXES_SUMMARY.md)** - Summary of bug fixes and improvements

### Project Information
- **[Changelog](CHANGELOG.md)** - Version history and release notes

## License

This project is available under the MIT License.
