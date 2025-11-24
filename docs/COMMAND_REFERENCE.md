# scrubb Command Reference

## Quick Command Table

| Command | Aliases | Description | Function |
|---------|---------|-------------|----------|
| `scrubb emoji [PATH] .` | `e` | Scrub emojis from files/directories | Remove emojis from text files with detailed output |
| `scrubb folder` | `f` | Organize files into categories | Move files to categorized folders and remove empty directories |
| `scrubb folder --dry` | `f --dry` | Preview folder organization | Show what would happen without making changes |
| `scrubb folder --tree` | `f --tree` | Organize with tree visualization | Show before/after directory trees with statistics |
| `scrubb folder --tree --dry` | `f --tree --dry` | Preview with tree visualization | Show current and simulated trees without making changes |
| `scrubb stats` | `s` | Show persistent statistics | Display accumulated statistics across all runs |
| `scrubb stats --top` | `s --top` | Show top 5 emoji tokens | Display most frequently removed emoji tokens |
| `scrubb stats --reset` | `s --reset` | Reset all statistics | Clear all persistent statistics (requires confirmation) |
| `scrubb config` | `c` | Show configuration | Display current configuration and file locations |
| `scrubb config --show` | `c --show` | Show configuration | Same as `scrubb config` (explicit) |
| `scrubb config -p PATH --edit` | `c -p PATH --edit` | Set default root | Update the default root directory path |
| `scrubb --help` | | Show help | Display general help information |
| `scrubb COMMAND --help` | | Show command help | Display detailed help for specific command |

### Command Aliases

All commands support short aliases for faster typing:
- `scrubb e` → `scrubb emoji` (emoji scrubbing)
- `scrubb f` → `scrubb folder` (folder organization)
- `scrubb s` → `scrubb stats` (statistics)
- `scrubb c` → `scrubb config` (configuration)

Aliases work with all flags and options. For example:
```bash
scrubb e .              # Same as: scrubb emoji .
scrubb f --dry          # Same as: scrubb folder --dry
scrubb s --top          # Same as: scrubb stats --top
scrubb c --show         # Same as: scrubb config --show
```

### Global Options

All commands support verbosity control:
- `--verbose` or `-v`: Display detailed debug information including file-by-file processing and timestamps
- `--quiet` or `-q`: Suppress all non-essential output, showing only errors and warnings

Examples:
```bash
scrubb emoji . --verbose        # Detailed output with debug info
scrubb folder --dry --quiet     # Minimal output, errors only
scrubb stats --top -v           # Statistics with verbose details
```

---

## Full Command Reference

### Folder Cleanup Command: `scrubb folder`

**Purpose**: Organize files into categorized folders and remove empty directories.

**Syntax**:
```bash
# Preview mode (dry-run)
scrubb folder --dry

# Actual execution (requires confirmation)
scrubb folder

# With tree visualization
scrubb folder --tree

# Preview with tree visualization
scrubb folder --tree --dry

# Skip confirmation prompt
scrubb folder --yes

# Using alias
scrubb f --dry
```

**Options**:
- `--dry`: Enable dry-run mode to preview changes without executing them
- `--tree`: Display directory tree visualization before and after execution with comprehensive statistics
- `--yes` or `-y`: Skip confirmation prompt and proceed automatically (use with caution)
- `--verbose` or `-v`: Display detailed debug information including file-by-file processing
- `--quiet` or `-q`: Suppress all non-essential output, showing only errors

**Interactive Workflow (Regular Mode)**:
1. System prompts: "Enter the directory path to clean up:"
2. User provides a directory path (absolute, relative, or with tilde expansion)
3. System validates the path exists and is a directory
4. System recursively scans all files in the directory tree
5. System displays a summary of planned operations
6. **System prompts for confirmation**: "Proceed with folder cleanup? (yes/no)"
7. User confirms (yes/y/Y/YES or Enter) or cancels (no/n/N/NO)
8. If confirmed: Files are categorized by extension and moved to organized folders
9. Empty directories are automatically removed
10. Statistics are displayed

**Note**: Use `--yes` or `-y` flag to skip the confirmation prompt for automated workflows.

**Interactive Workflow (Dry-Run Mode)**:
1. System displays prominent dry-run mode indicator
2. System prompts: "Enter the directory path to clean up:"
3. User provides a directory path (absolute, relative, or with tilde expansion)
4. System validates the path exists and is a directory
5. System recursively scans all files in the directory tree
6. System simulates all operations without making changes
7. Comprehensive preview is displayed with detailed information
8. System reminds user that no changes were made

**File Categories**:

Files are organized into the following structure within a `Scrubbed/` folder:

- **Images** → `Scrubbed/Images/`
  - `.jpg`, `.jpeg`, `.png`, `.gif`, `.bmp`, `.svg`, `.webp`, `.ico`, `.tiff`, `.tif`

- **Video** → `Scrubbed/Video/`
  - `.mp4`, `.avi`, `.mov`, `.mkv`, `.flv`, `.wmv`, `.webm`, `.m4v`, `.mpeg`, `.mpg`

- **Markdown** → `Scrubbed/Docs/Markdown/`
  - `.md`, `.markdown`

- **Documents** → `Scrubbed/Docs/Other Docs/`
  - `.pdf`, `.doc`, `.docx`, `.txt`, `.rtf`, `.odt`, `.xls`, `.xlsx`, `.ppt`, `.pptx`, `.csv`

- **Development** → `Scrubbed/Development/`
  - `.py`, `.js`, `.ts`, `.jsx`, `.tsx`, `.java`, `.c`, `.cpp`, `.h`, `.hpp`, `.rs`, `.go`, `.rb`, `.php`, `.html`, `.css`, `.scss`, `.json`, `.xml`, `.yaml`, `.yml`, `.toml`, `.sh`, `.bash`, `.sql`, `.r`, `.swift`, `.kt`

**Conflict Resolution**:
- If a file with the same name exists in the destination, the system appends a numeric suffix
- Example: `file.txt` → `file_1.txt`, `file_2.txt`, etc.
- Original file extensions are always preserved

**Empty Folder Removal**:
- After moving files, all empty directories are automatically removed
- The root directory and Scrubbed folder are protected from deletion
- Nested empty directories are removed recursively
- Common hidden/system files (`.DS_Store`, `Thumbs.db`, `.gitkeep`, etc.) are automatically removed before directory cleanup

**Output (Regular Mode)**: Displays organization statistics including:
- Total files moved
- Files moved per category
- Number of empty folders removed
- Error count and list of files that couldn't be processed

**Example Output (Regular Mode)**:
```
Folder cleanup complete:
  Files moved: 42
    Images: 15
    Video: 3
    Docs/Markdown: 8
    Docs/Other Docs: 12
    Development: 4
  Empty folders removed: 7
  Errors: 0
```

**Output (Dry-Run Mode)**: Displays comprehensive preview including:
- Summary statistics (files to move, directories to create/remove, conflicts, skipped files)
- Files by category with counts
- List of directories that would be created
- Detailed file operations grouped by category
- Name conflicts with original and resolved names
- Skipped files with reasons
- Empty directories that would be removed
- Potential errors (permission issues, inaccessible files)
- Reminder that no changes were made

**Example Output (Dry-Run Mode)**:
```
======================================================================
DRY RUN PREVIEW - No changes will be made
======================================================================

 SUMMARY
  Files to move: 42
  Directories to create: 5
  Empty directories to remove: 7
  Files to skip: 3
  Potential conflicts: 2

 FILES BY CATEGORY
  Development: 4 files
  Docs/Markdown: 8 files
  Docs/Other Docs: 12 files
  Images: 15 files
  Video: 3 files

 DIRECTORIES TO CREATE
  /path/to/dir/Scrubbed
  /path/to/dir/Scrubbed/Images
  /path/to/dir/Scrubbed/Video
  /path/to/dir/Scrubbed/Docs/Markdown
  /path/to/dir/Scrubbed/Development

 FILE OPERATIONS
  Images:
    photo.jpg → /path/to/dir/Scrubbed/Images/photo.jpg
    image.png → /path/to/dir/Scrubbed/Images/image.png
    ...

  NAME CONFLICTS
  report.pdf → report_1.pdf
    Category: Docs/Other Docs

⏭  SKIPPED FILES
  /path/to/dir/unknown.xyz - Unknown extension

  EMPTY DIRECTORIES TO REMOVE
  /path/to/dir/nested/empty

 No potential errors detected

======================================================================
This was a DRY RUN - No files were moved or modified
Run without --dry flag to execute these changes
======================================================================
```

**Error Handling**:
- Invalid path: Displays error message and exits
- Permission errors: Logs error, continues processing other files
- File access errors: Increments error counter, continues processing

**Dry-Run Mode Benefits**:
- **Safe Preview**: See exactly what will happen before making changes
- **Conflict Detection**: Identify name conflicts and see how they'll be resolved
- **Error Prevention**: Detect potential permission issues before execution
- **Verification**: Ensure files are categorized correctly
- **Planning**: Understand the scope of changes before committing

**Recommended Workflow**:
1. Run `scrubb folder --dry` to preview changes
2. Review the detailed output
3. Run `scrubb folder` to execute if everything looks correct

**Tree Visualization Mode (`--tree` flag)**:

The `--tree` flag adds visual directory tree representations before and after file organization, making it easy to see structural changes at a glance.

**Usage Examples**:
```bash
# Actual execution with tree visualization
scrubb folder --tree

# Dry-run with tree visualization (recommended for first-time use)
scrubb folder --tree --dry
```

**Tree Output Format**:

The tree visualization uses professional box-drawing characters and color-coded file types for easy readability:

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
  
  Files by Category:
    Images: 1
    Video: 1
    Docs/Markdown: 1
    Docs/Other Docs: 2
    Development: 1


COMPARISON - Changes

  Files: 0 (no change)
  Directories: +6
  Total Size: 0 B (no change)
  Max Depth: +2
```

**Statistics Displayed**:

The tree visualization provides comprehensive statistics for both before and after states:

- **Files**: Total number of files in the directory tree
- **Directories**: Total number of directories (folders)
- **Total Size**: Combined size of all files in human-readable format (B, KB, MB, GB, TB)
- **Max Depth**: Maximum nesting level of the directory structure
- **Files by Category**: Breakdown of files by type (Images, Video, Documents, Development)

**Comparison Section**:

After displaying both trees, a comparison section shows the delta (change) for each statistic:
- Positive changes shown in green with `+` prefix (e.g., `+6` directories created)
- Negative changes shown in red with `-` prefix (e.g., `-3` empty directories removed)
- No change shown in gray (e.g., `0` files - files moved, not created/deleted)
- Percentage changes displayed where applicable

**Tree Visualization with Dry-Run Mode**:

When combining `--tree` and `--dry` flags:
```bash
scrubb folder --tree --dry
```

The after-state tree is **simulated** based on planned operations:
- Shows what the directory structure would look like after execution
- Clearly marked with "SIMULATED" indicator
- No actual file system changes are made
- Provides accurate preview of the final structure

**Benefits of Tree Visualization**:
- **Visual Clarity**: See the exact directory structure before and after
- **Structural Understanding**: Understand how files are reorganized at a glance
- **Verification**: Confirm the organization matches your expectations
- **Debugging**: Quickly identify unexpected behavior or categorization issues
- **Documentation**: Capture before/after states for record-keeping

**Display Constraints**:

The tree renderer respects terminal width and provides options to limit output:
- Long file paths are truncated with ellipsis (`...`) if they exceed terminal width
- Optional depth limiting to prevent overwhelming output for very deep directories
- Optional file count limiting per directory for large directories

**Color Coding**:

Files are color-coded by category for easy identification:
- **Images**: Cyan
- **Video**: Magenta
- **Documents**: Yellow
- **Development**: Green
- **Directories**: Bold white
- **New directories** (in after-state): Bold white with indicator

**Integration with Standard Output**:

Tree visualization integrates seamlessly with existing output:
1. Tree visualization displays first (before and after trees with comparison)
2. Standard operation statistics display after trees
3. In dry-run mode, detailed DryRunFormatter output follows tree visualization

**Error Handling**:

Tree visualization is designed to be non-intrusive:
- If tree rendering fails, the cleanup operation continues normally
- Falls back to simple text-based tree if the `rich` library is unavailable
- Permission errors in tree scanning are marked and don't block the operation
- Partial statistics are displayed if complete calculation fails

**Exit Codes**:
- `0`: Success
- `1`: Invalid directory path or critical error

---

### Emoji Scrubbing Command: `scrubb emoji`

**Purpose**: Remove emojis from text files and directories with comprehensive tracking.

**Syntax**:
```bash
scrubb emoji [PATH] [EXECUTOR]
```

**Parameters**:
- `PATH` (optional): Target path or subpath
  - If omitted: Uses configured default root
  - If relative path: Resolved relative to default root
  - If absolute path: Used directly
  - Examples: `src`, `./docs`, `/home/user/projects`
- `EXECUTOR` (required): Must be `.` to indicate recursive processing

**Options**:
- `--verbose` or `-v`: Display detailed debug information including file-by-file processing and timestamps
- `--quiet` or `-q`: Suppress all non-essential output, showing only errors and warnings

**Examples**:
```bash
# Scrub from configured default root
scrubb emoji .

# Scrub a subdirectory under default root
scrubb emoji src .

# Scrub an absolute or relative path
scrubb emoji ./docs .
scrubb emoji /home/user/projects .

# Using alias
scrubb e .

# With verbose output
scrubb emoji . --verbose

# Quiet mode (errors only)
scrubb emoji . --quiet
```

**Deprecation Notice**: The old `scrubb main` command is deprecated but still works with a warning. It will be removed in a future version. Please update your scripts to use `scrubb emoji` instead.

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
- `--reset`: Reset all persistent statistics to zero (requires confirmation)
- `--yes` or `-y`: Skip confirmation prompt when using `--reset`
- `--verbose` or `-v`: Display detailed statistics information
- `--quiet` or `-q`: Suppress all non-essential output
- `--help`: Show detailed help for this command

**Examples**:
```bash
# View basic statistics
scrubb stats

# Show top emoji tokens
scrubb stats --top

# Reset all statistics (prompts for confirmation)
scrubb stats --reset

# Reset without confirmation prompt
scrubb stats --reset --yes

# Using alias
scrubb s --top
```

**Confirmation Prompts**:
- When using `--reset`, the system will prompt: "Are you sure you want to reset all statistics? (yes/no)"
- Confirm with yes/y/Y/YES or Enter to proceed
- Cancel with no/n/N/NO to abort
- Use `--yes` or `-y` flag to skip the confirmation prompt for automated workflows

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
- `--verbose` or `-v`: Display detailed configuration information
- `--quiet` or `-q`: Suppress all non-essential output
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

# Using alias
scrubb c --show

# Verbose configuration display
scrubb config --verbose
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
scrubb emoji --help
scrubb folder --help
scrubb stats --help
scrubb config --help
```

**Output**: Shows:
- Detailed command syntax
- Parameter descriptions
- Option explanations
- Available aliases
- Usage examples

---

## Safety Features

### Confirmation Prompts

To prevent accidental data loss, scrubb prompts for confirmation before destructive operations:

**Folder Cleanup Confirmation**:
```bash
# When running without --dry flag
scrubb folder

# System displays summary and prompts:
Proceed with folder cleanup? (yes/no):
```

**Statistics Reset Confirmation**:
```bash
# When resetting statistics
scrubb stats --reset

# System prompts:
Are you sure you want to reset all statistics? (yes/no):
```

**Accepting Confirmations**:
- Type `yes`, `y`, `Y`, or `YES` to proceed
- Press Enter to accept (if default is yes)
- Type `no`, `n`, `N`, or `NO` to cancel

**Bypassing Confirmations**:

For automated workflows or when you're certain about the operation, use the `--yes` or `-y` flag:

```bash
# Skip folder cleanup confirmation
scrubb folder --yes

# Skip statistics reset confirmation
scrubb stats --reset --yes

# Using aliases with auto-confirm
scrubb f -y
scrubb s --reset -y
```

**Warning**: Use `--yes` with caution, especially in scripts, as it bypasses all safety prompts.

### Dry-Run Mode

The `--dry` flag for folder operations provides a safe preview:
- Shows exactly what would happen without making changes
- Identifies potential conflicts and errors
- Allows verification before execution
- No confirmation prompt needed (non-destructive)

```bash
# Always safe to run
scrubb folder --dry
scrubb f --dry --tree
```

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
scrubb emoji .

# Scrub specific directory
scrubb emoji src .

# Using aliases for faster typing
scrubb e .              # Same as: scrubb emoji .
scrubb e src .          # Same as: scrubb emoji src .

# Preview folder cleanup (dry-run)
scrubb folder --dry
scrubb f --dry          # Using alias

# Execute folder cleanup (with confirmation)
scrubb folder
scrubb f --yes          # Skip confirmation with alias

# Check statistics
scrubb stats
scrubb s                # Using alias

# View top emojis removed
scrubb stats --top
scrubb s --top          # Using alias

# Verbose mode for detailed output
scrubb emoji . --verbose
scrubb folder --dry -v

# Quiet mode for minimal output
scrubb emoji . --quiet
scrubb stats -q
```

**Maintenance**:
```bash
# Reset statistics (with confirmation)
scrubb stats --reset

# Reset statistics without confirmation
scrubb stats --reset --yes
scrubb s --reset -y     # Using alias

# Update default root
scrubb config -p /new/path --edit
scrubb c -p /new/path --edit  # Using alias
```

### Output Interpretation

**Per-Run Output (Normal Mode)**:
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

**Per-Run Output (Verbose Mode)**:
```
[DEBUG] Processing file: /path/to/file1.md
[DEBUG] Found emoji:  (U+1F600 - GRINNING FACE)
[DEBUG] Removed 3 emojis from /path/to/file1.md
[DEBUG] Processing file: /path/to/file2.txt
...
scrubb run: files_processed=42 modified=3 skipped=39 errors=0 emojis_removed=15
```

**Per-Run Output (Quiet Mode)**:
```
(Only errors and warnings are displayed)
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
