# Design Document

## Overview

This design addresses two primary objectives:
1. **Command Renaming**: Migrate the `main` command to `emoji` for better clarity and consistency
2. **CLI Enhancements**: Leverage the existing `rich` library and modern typer features to improve user experience

The design maintains backward compatibility through deprecation warnings while introducing modern CLI patterns including command aliases, verbose/quiet modes, confirmation prompts, and enhanced visual feedback.

## Architecture

### High-Level Architecture

The CLI architecture follows a layered approach:

```

         CLI Layer (cli.py)              
  - Command definitions                  
  - Argument parsing                     
  - Output formatting                    

                  ↓

      Business Logic Layer               
  - Scrubber (emoji removal)             
  - FolderOrganizer (file organization)  
  - TreeVisualizer (tree rendering)      

                  ↓

      Configuration Layer                
  - Config management (config.py)        
  - Statistics tracking                  
  - XDG-compliant paths                  

```

### Command Structure

The new command structure will be:

```
scrubb
 emoji (formerly main)
    Aliases: e
    Options: --verbose, --quiet, --yes
 folder
    Aliases: f
    Options: --dry, --tree, --verbose, --quiet, --yes
 stats
    Aliases: s
    Options: --top, --reset
 config
     Aliases: c
     Options: -p, --show, --edit
```

## Components and Interfaces

### 1. Command Registration Module

**Purpose**: Register commands with typer and handle aliases

**Interface**:
```python
def register_emoji_command(app: typer.Typer) -> None:
    """Register the emoji command with aliases."""
    
def register_folder_command(app: typer.Typer) -> None:
    """Register the folder command with aliases."""
    
def register_stats_command(app: typer.Typer) -> None:
    """Register the stats command with aliases."""
    
def register_config_command(app: typer.Typer) -> None:
    """Register the config command with aliases."""
```

**Implementation Notes**:
- Use typer's `@app.command()` decorator with `name` parameter
- Implement command aliases by registering the same function multiple times with different names
- Set `hidden=True` for alias commands to avoid cluttering help output

### 2. Output Formatting Module

**Purpose**: Provide rich formatting utilities for CLI output

**Interface**:
```python
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress

class OutputFormatter:
    """Handles rich formatting for CLI output."""
    
    def __init__(self, console: Console):
        self.console = console
    
    def print_success(self, message: str) -> None:
        """Print success message with green formatting."""
    
    def print_error(self, message: str, suggestion: str = None) -> None:
        """Print error message with red formatting and optional suggestion."""
    
    def print_warning(self, message: str) -> None:
        """Print warning message with yellow formatting."""
    
    def print_info(self, message: str) -> None:
        """Print info message with blue formatting."""
    
    def create_stats_table(self, stats: dict) -> Table:
        """Create a formatted table for statistics."""
    
    def create_panel(self, content: str, title: str) -> Panel:
        """Create a formatted panel with title."""
    
    def print_file_list(self, files: list[str], status: str) -> None:
        """Print a list of files with status indicators."""
```

**Implementation Notes**:
- Use `rich.console.Console` for all output
- Leverage `rich.table.Table` for tabular data
- Use `rich.panel.Panel` for grouped information
- Implement `rich.progress.Progress` for long operations

### 3. Prompt Utilities Module

**Purpose**: Provide interactive prompts with validation

**Interface**:
```python
from rich.prompt import Prompt, Confirm

class PromptUtils:
    """Utilities for interactive prompts."""
    
    @staticmethod
    def prompt_directory(message: str, default: str = None) -> Path:
        """Prompt for directory path with validation."""
    
    @staticmethod
    def prompt_confirmation(message: str, default: bool = False) -> bool:
        """Prompt for yes/no confirmation."""
    
    @staticmethod
    def prompt_choice(message: str, choices: list[str]) -> str:
        """Prompt for selection from choices."""
```

**Implementation Notes**:
- Use `rich.prompt.Prompt` for text input
- Use `rich.prompt.Confirm` for yes/no questions
- Validate directory paths before returning
- Handle keyboard interrupts gracefully

### 4. Verbosity Manager

**Purpose**: Control output verbosity based on flags

**Interface**:
```python
from enum import Enum

class VerbosityLevel(Enum):
    QUIET = 0
    NORMAL = 1
    VERBOSE = 2

class VerbosityManager:
    """Manages output verbosity levels."""
    
    def __init__(self, level: VerbosityLevel):
        self.level = level
    
    def should_print_debug(self) -> bool:
        """Check if debug messages should be printed."""
    
    def should_print_info(self) -> bool:
        """Check if info messages should be printed."""
    
    def should_print_summary(self) -> bool:
        """Check if summary should be printed."""
```

**Implementation Notes**:
- Store verbosity level in a context variable
- Check verbosity before printing non-essential output
- Always print errors regardless of verbosity

### 5. Deprecation Handler

**Purpose**: Handle deprecated command names with warnings

**Interface**:
```python
def handle_deprecated_main() -> None:
    """Display deprecation warning for 'main' command and redirect to 'emoji'."""
```

**Implementation Notes**:
- Register `main` as a hidden command that calls `emoji`
- Display a prominent warning using rich formatting
- Log deprecation to stderr
- Continue execution with emoji command

## Data Models

### Enhanced Statistics Model

```python
from dataclasses import dataclass
from typing import Dict

@dataclass
class EmojiStatistics:
    """Enhanced emoji statistics with visual representation."""
    emoji: str
    codepoint: str
    count: int
    percentage: float
    unicode_name: str
    
    def to_table_row(self) -> list[str]:
        """Convert to table row for display."""
        return [
            self.emoji,
            self.unicode_name,
            str(self.count),
            f"{self.percentage:.1f}%"
        ]
```

### Command Context Model

```python
from dataclasses import dataclass

@dataclass
class CommandContext:
    """Shared context for all commands."""
    verbosity: VerbosityLevel
    auto_confirm: bool  # --yes flag
    console: Console
    formatter: OutputFormatter
```

**Implementation Notes**:
- Pass context to all command functions
- Use typer's callback mechanism to initialize context
- Store context in a global variable or use dependency injection

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Command name consistency

*For any* valid path argument, invoking `scrubb emoji [PATH] .` should execute emoji scrubbing operations with identical functionality to the former `main` command
**Validates: Requirements 1.1**

### Property 2: Deprecation warning display

*For any* valid path argument, invoking `scrubb main [PATH] .` should display a deprecation warning in the output
**Validates: Requirements 1.2**

### Property 3: Documentation string consistency

*For any* documentation file (README.md, COMMAND_REFERENCE.md), scanning for "scrubb main" should return zero matches (except in migration/deprecation sections)
**Validates: Requirements 1.3, 2.2, 2.3**

### Property 4: Help text command name

*For any* invocation of `scrubb --help`, the output should contain "emoji" as a command name and should not list "main" as a primary command
**Validates: Requirements 1.4**

### Property 5: Test file command references

*For any* test file in the tests directory, scanning for command invocations should use "emoji" instead of "main"
**Validates: Requirements 1.5, 2.4**

### Property 6: Command alias equivalence

*For any* command and its alias (emoji/e, folder/f, stats/s, config/c), invoking both with identical arguments should produce identical output and exit codes
**Validates: Requirements 6.1, 6.2, 6.3, 6.4**

### Property 7: Quiet mode output suppression

*For any* command executed with `--quiet` flag, the output should contain only error and warning messages, with no informational or debug output
**Validates: Requirements 7.2, 7.4**

### Property 8: Verbose mode debug output

*For any* command executed with `--verbose` flag, the output should contain debug information including file-by-file processing details and timestamps
**Validates: Requirements 7.1, 7.3**

### Property 9: Default verbosity output

*For any* command executed without verbosity flags, the output should contain summary statistics but not debug details
**Validates: Requirements 7.5**

### Property 10: Auto-confirm bypass

*For any* destructive operation executed with `--yes` flag, the command should complete without displaying confirmation prompts
**Validates: Requirements 8.5**

### Property 11: Confirmation prompt acceptance

*For any* confirmation prompt, providing any of ('yes', 'y', 'Y', 'YES', or Enter) should proceed with the operation
**Validates: Requirements 5.3, 8.3**

### Property 12: Confirmation prompt rejection

*For any* confirmation prompt, providing a negative response ('no', 'n', 'N', 'NO') should cancel the operation and exit gracefully
**Validates: Requirements 8.4**

### Property 13: Rich formatting presence

*For any* command output in a terminal supporting rich formatting, the output should contain ANSI escape codes or rich markup for formatting
**Validates: Requirements 3.1, 3.3, 3.5**

### Property 14: Path syntax highlighting

*For any* file path displayed in output, the path should contain formatting codes to distinguish path components
**Validates: Requirements 3.4**

### Property 15: Error message structure

*For any* error condition, the error message should contain both a description of what failed and a suggestion for resolution
**Validates: Requirements 4.1, 4.2, 4.5**

### Property 16: File operation error details

*For any* file operation failure, the error message should include the specific file path that caused the failure
**Validates: Requirements 4.3**

### Property 17: Path validation in prompts

*For any* directory path provided to a prompt, if the path doesn't exist or isn't a directory, the system should reject it and re-prompt
**Validates: Requirements 5.1**

### Property 18: Emoji display format

*For any* emoji removal operation, the output should display both the emoji character and its codepoint count
**Validates: Requirements 9.1**

### Property 19: Emoji statistics table format

*For any* invocation of `scrubb stats --top`, the output should contain a formatted table with columns for rank, emoji, count, and percentage
**Validates: Requirements 9.3**

### Property 20: Verbose emoji details

*For any* emoji removal in verbose mode, the output should include the emoji character, Unicode name, and source file path
**Validates: Requirements 9.4**

### Property 21: Error exit codes

*For any* error condition, the system should exit with an appropriate non-zero exit code (1 for general errors, 2 for invalid input, 3 for permissions, 130 for user cancellation)
**Validates: Requirements 10.3**

### Property 22: Help text formatting

*For any* invocation of `--help`, the output should use rich formatting with proper sections and styling
**Validates: Requirements 10.4**

### Property 23: Input validation errors

*For any* invalid command argument, the system should display a validation error before attempting to execute the command
**Validates: Requirements 10.5**

## Error Handling

### Error Categories

1. **User Input Errors**
   - Invalid paths
   - Invalid command arguments
   - Invalid configuration values
   - **Handling**: Display formatted error with suggestion, re-prompt if interactive

2. **File System Errors**
   - Permission denied
   - File not found
   - Disk full
   - **Handling**: Display specific error with file path, continue processing other files

3. **Configuration Errors**
   - Corrupted config file
   - Invalid JSON
   - Missing required fields
   - **Handling**: Fall back to defaults, warn user, offer to reset config

4. **Terminal Capability Errors**
   - Unicode not supported
   - Rich formatting not available
   - Terminal too narrow
   - **Handling**: Gracefully degrade to simpler output

### Error Display Format

Using rich formatting:

```python
from rich.panel import Panel

def display_error(error: Exception, suggestion: str = None):
    """Display formatted error message."""
    content = f"[red]Error:[/red] {str(error)}"
    if suggestion:
        content += f"\n\n[yellow]Suggestion:[/yellow] {suggestion}"
    
    console.print(Panel(
        content,
        title=" Error",
        border_style="red"
    ))
```

### Exit Codes

- `0`: Success
- `1`: General error
- `2`: Invalid input or path not found
- `3`: Permission denied
- `4`: Configuration error
- `130`: User cancelled (Ctrl+C)

## Testing Strategy

### Unit Testing

Unit tests will cover:
- Command registration and alias resolution
- Output formatting functions
- Prompt validation logic
- Verbosity level filtering
- Error message formatting
- Deprecation warning display

### Property-Based Testing

Property-based tests will use the `hypothesis` library (already in use based on `.hypothesis` directory) to verify:

1. **Command Alias Equivalence**: Generate random valid arguments and verify that `emoji` and `e` produce identical results
2. **Verbosity Filtering**: Generate random output messages and verify that quiet mode suppresses non-essential output
3. **Path Validation**: Generate random path strings and verify that validation correctly identifies valid/invalid paths
4. **Rich Formatting Fallback**: Test with various terminal capabilities and verify graceful degradation

### Integration Testing

Integration tests will verify:
- End-to-end command execution with new names
- Backward compatibility with deprecated `main` command
- Rich formatting in actual terminal environments
- Confirmation prompts in interactive mode

### Testing Framework

- **Unit Tests**: pytest
- **Property-Based Tests**: hypothesis (already configured)
- **CLI Testing**: typer's testing utilities with `CliRunner`
- **Rich Testing**: rich's `Console` with `record=True` for output capture

### Test Configuration

Configure hypothesis for CLI testing:
```python
from hypothesis import settings

settings.register_profile("cli", max_examples=100, deadline=1000)
```

## Implementation Notes

### Third-Party Libraries

The design leverages these libraries (all compatible with existing dependencies):

1. **rich** (already installed)
   - Version: >=13.0.0
   - Purpose: Terminal formatting, tables, panels, progress bars
   - Benefits: Professional output, better UX, wide terminal support

2. **typer** (already installed)
   - Version: >=0.12.3
   - Purpose: CLI framework
   - Benefits: Type hints, automatic help, rich integration

### Migration Strategy

1. **Phase 1**: Add `emoji` command alongside `main`
2. **Phase 2**: Add deprecation warning to `main`
3. **Phase 3**: Update all documentation
4. **Phase 4**: Update all tests
5. **Phase 5**: (Future) Remove `main` command in next major version

### Backward Compatibility

- Keep `main` command functional with deprecation warning
- Ensure all existing scripts continue to work
- Document migration path in CHANGELOG
- Provide migration guide in documentation

### Performance Considerations

- Rich formatting adds minimal overhead (<10ms per command)
- Progress bars only shown for operations >100 files
- Lazy loading of rich components to reduce startup time
- Cache console instance to avoid repeated initialization

### Accessibility

- Ensure output works with screen readers
- Provide plain text fallback for all rich formatting
- Use semantic colors (red=error, green=success, yellow=warning)
- Support NO_COLOR environment variable

## Dependencies

### New Dependencies

None - all required libraries are already installed:
- `typer>=0.12.3` 
- `rich>=13.0.0` 

### Dependency Justification

**rich**: Already a project dependency, provides:
- Professional terminal output
- Cross-platform compatibility
- Extensive formatting options
- Active maintenance and wide adoption

**typer**: Already a project dependency, provides:
- Modern CLI patterns
- Type safety
- Automatic help generation
- Rich integration built-in

## Configuration Changes

### New Configuration Options

Add to `config.json`:

```json
{
  "output": {
    "use_rich": true,
    "use_color": true,
    "verbosity": "normal"
  },
  "prompts": {
    "confirm_destructive": true,
    "confirm_folder_cleanup": true
  }
}
```

### Configuration Migration

- Existing configs remain valid
- New options have sensible defaults
- Config validation on load with helpful error messages

## Documentation Updates

### Files to Update

1. **README.md**
   - Replace all `scrubb main` with `scrubb emoji`
   - Add section on command aliases
   - Add section on verbosity modes
   - Update quick start examples

2. **docs/COMMAND_REFERENCE.md**
   - Update command table
   - Replace all `scrubb main` references
   - Add alias documentation
   - Add verbosity flag documentation
   - Add confirmation prompt documentation

3. **CHANGELOG.md**
   - Document command rename
   - Document new features
   - Document deprecation

4. **docs/ARCHITECTURE.md**
   - Update CLI architecture section
   - Document new modules

### Migration Guide

Create `docs/MIGRATION.md`:
- Explain command rename
- Provide find/replace patterns for scripts
- Document deprecation timeline
- Show before/after examples
