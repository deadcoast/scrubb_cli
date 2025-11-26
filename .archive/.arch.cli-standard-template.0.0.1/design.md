# CLI Standard Template - Design Document

## Overview

This design document provides a standardized, reusable template for building professional command-line interface (CLI) applications in Python. It captures proven architectural patterns, component designs, and implementation strategies extracted from production CLI tools.

**Purpose**: Use this template when starting any new CLI project to ensure:
- Professional code organization
- Consistent user experience
- Maintainable architecture
- Comprehensive testing
- Cross-platform compatibility

**Not Included**: Specific business logic, domain models, or application-specific functionality. This template focuses on CLI infrastructure and patterns.

## Architecture

### Layered Architecture Pattern

```
┌─────────────────────────────────────────────────────────┐
│                     CLI Layer                           │
│  - Command registration (Typer decorators)              │
│  - Argument/option parsing                              │
│  - Command routing                                      │
│  - Dependency injection setup                           │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│                  CLI Handlers Layer                     │
│  - Command handler classes                              │
│  - Input validation and prompting                       │
│  - Output formatting                                    │
│  - Verbosity management                                 │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│                  Business Logic Layer                   │
│  - Domain operations                                    │
│  - Core algorithms                                      │
│  - Data transformations                                 │
│  - Business rules                                       │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│                 Infrastructure Layer                    │
│  - Configuration management                             │
│  - File system operations                               │
│  - External service integration                         │
│  - Data persistence                                     │
└─────────────────────────────────────────────────────────┘
```

### Module Structure Template

```
your_cli/
├── cli.py                    # Main CLI app with Typer decorators
├── cli_handlers/
│   ├── __init__.py
│   ├── shared.py            # Shared utilities (no duplication)
│   ├── commands.py          # Command handler classes
│   ├── input.py             # Input handling and validation
│   └── output.py            # Output formatting (optional if using separate module)
├── business/
│   ├── __init__.py
│   └── [domain_logic].py    # Your business logic modules
├── config.py                # Configuration management
├── output_formatter.py      # Rich output formatting
├── verbosity.py            # Verbosity level management
├── prompt_utils.py         # Interactive prompt utilities
└── [other_modules].py      # Additional infrastructure
```

## Components and Interfaces

### 1. Main CLI Module (cli.py)

**Purpose**: Define the Typer application and register commands with minimal logic.

**Responsibilities**:
- Create Typer app instance
- Register commands with decorators
- Define command signatures (arguments, options)
- Route to command handlers
- Handle command aliases

**Pattern**:
```python
import typer
from .cli_handlers.shared import setup_verbosity, resolve_path, create_formatter
from .cli_handlers.commands import CommandHandler

app = typer.Typer(
    add_completion=False,
    help="Your CLI description",
    no_args_is_help=True
)

@app.command(
    name="command-name",
    help="Command description"
)
def command_name(
    arg: str = typer.Argument(None, help="Argument description"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Quiet mode"),
):
    """Command implementation."""
    # Setup
    formatter = create_formatter()
    verbosity_manager = setup_verbosity(verbose, quiet, formatter)
    
    # Create handler with dependencies
    handler = CommandHandler(formatter, verbosity_manager)
    
    # Execute
    exit_code = handler.execute(arg)
    
    raise typer.Exit(code=exit_code)

# Command aliases (hidden)
@app.command(name="c", hidden=True)
def c_alias(
    arg: str = typer.Argument(None, help="Argument description"),
    verbose: bool = typer.Option(False, "--verbose", "-v"),
    quiet: bool = typer.Option(False, "--quiet", "-q"),
):
    """Alias for command-name."""
    command_name(arg=arg, verbose=verbose, quiet=quiet)
```

**Key Principles**:
- Keep CLI functions thin - delegate to handlers
- Use dependency injection for all dependencies
- Consistent option naming across commands
- Hidden aliases for convenience


### 2. Shared Utilities Module (cli_handlers/shared.py)

**Purpose**: Eliminate code duplication across CLI commands.

**Responsibilities**:
- Setup verbosity management
- Resolve and validate paths
- Create formatter instances
- Load configuration
- Common error handling

**Pattern**:
```python
from pathlib import Path
from rich.console import Console
from ..output_formatter import OutputFormatter
from ..verbosity import VerbosityManager, VerbosityLevel
from ..config import load_config

def setup_verbosity(
    verbose: bool,
    quiet: bool,
    formatter: OutputFormatter
) -> VerbosityManager:
    """Setup verbosity manager based on flags."""
    if verbose:
        level = VerbosityLevel.VERBOSE
    elif quiet:
        level = VerbosityLevel.QUIET
    else:
        level = VerbosityLevel.NORMAL
    
    return VerbosityManager(level)

def resolve_path(
    path: str | None,
    executor: str | None,
    default_root: Path
) -> Path:
    """Resolve user-provided path with validation."""
    # Your path resolution logic
    pass

def create_formatter(stderr: bool = False) -> OutputFormatter:
    """Create output formatter with console."""
    console = Console(stderr=stderr)
    return OutputFormatter(console)

def load_default_root() -> Path:
    """Load default root from configuration."""
    config = load_config()
    return Path(config.get("default_root", Path.cwd()))
```

**Key Principles**:
- Single source of truth for common operations
- No duplication across commands
- Clear function names describing purpose
- Consistent return types

### 3. Command Handler Classes (cli_handlers/commands.py)

**Purpose**: Implement command logic with dependency injection.

**Responsibilities**:
- Execute command operations
- Coordinate between business logic and I/O
- Handle errors and return exit codes
- Format output using formatter

**Pattern**:
```python
from pathlib import Path
from ..output_formatter import OutputFormatter
from ..verbosity import VerbosityManager
from ..business.your_logic import YourBusinessLogic

class CommandHandler:
    """Handler for a specific command."""
    
    def __init__(
        self,
        formatter: OutputFormatter,
        verbosity_manager: VerbosityManager,
        # Other dependencies...
    ):
        self.formatter = formatter
        self.verbosity = verbosity_manager
    
    def execute(self, arg: str) -> int:
        """Execute the command.
        
        Returns:
            Exit code (0 for success, non-zero for errors)
        """
        try:
            # Validate inputs
            if not arg:
                self.formatter.print_error("Argument required")
                return 2
            
            # Execute business logic
            result = self._perform_operation(arg)
            
            # Format and display output
            if self.verbosity.should_print_summary():
                self._display_results(result)
            
            return 0
            
        except KeyboardInterrupt:
            self.formatter.print_warning("Operation cancelled by user")
            return 130
        except Exception as e:
            self.formatter.print_error(str(e))
            return 1
    
    def _perform_operation(self, arg: str):
        """Perform the actual operation."""
        # Your business logic here
        pass
    
    def _display_results(self, result):
        """Display formatted results."""
        # Your output formatting here
        pass
```

**Key Principles**:
- One handler class per command
- Dependencies injected via constructor
- Return exit codes, don't call sys.exit()
- Separate validation, execution, and output

### 4. Output Formatter Module (output_formatter.py)

**Purpose**: Provide consistent, rich terminal output.

**Responsibilities**:
- Format success/error/warning/info messages
- Create tables and panels
- Display file lists with status indicators
- Handle emoji/Unicode display
- Graceful degradation for limited terminals

**Pattern**:
```python
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from pathlib import Path

class OutputFormatter:
    """Handles rich formatting for CLI output."""
    
    def __init__(self, console: Console | None = None):
        self.console = console or Console()
    
    def print_success(self, message: str) -> None:
        """Print success message with green formatting."""
        self.console.print(f"[green]✓ {message}[/green]")
    
    def print_error(self, message: str, suggestion: str | None = None) -> None:
        """Print error message with red formatting."""
        content = f"[red]Error:[/red] {message}"
        if suggestion:
            content += f"\n\n[yellow]Suggestion:[/yellow] {suggestion}"
        
        panel = Panel(content, title="✗ Error", border_style="red")
        self.console.print(panel)
    
    def print_warning(self, message: str) -> None:
        """Print warning message with yellow formatting."""
        self.console.print(f"[yellow]⚠ {message}[/yellow]")
    
    def print_info(self, message: str) -> None:
        """Print info message with blue formatting."""
        self.console.print(f"[blue]ℹ {message}[/blue]")
    
    def create_stats_table(self, stats: dict) -> Table:
        """Create a formatted table for statistics."""
        table = Table(title="Statistics", show_header=True)
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="magenta")
        
        for key, value in stats.items():
            table.add_row(key.replace("_", " ").title(), str(value))
        
        return table
    
    def print_file_list(
        self,
        files: list[Path],
        status: str = "modified"
    ) -> None:
        """Print a list of files with status indicators."""
        status_icons = {
            "modified": ("[+]", "green"),
            "error": ("[X]", "red"),
            "skipped": ("[-]", "yellow"),
            "moved": ("[>]", "cyan"),
        }
        
        icon, color = status_icons.get(status, ("[*]", "white"))
        
        for file_path in files:
            self.console.print(
                f"  [{color}]{icon}[/{color}] {file_path}"
            )
```

**Key Principles**:
- Consistent formatting across all output
- Use Rich library for professional appearance
- Provide semantic methods (success, error, warning)
- Handle terminal limitations gracefully

### 5. Verbosity Manager Module (verbosity.py)

**Purpose**: Control output verbosity across the application.

**Responsibilities**:
- Define verbosity levels (QUIET, NORMAL, VERBOSE)
- Provide methods to check what should be printed
- Store verbosity state in context variable
- Always show errors/warnings regardless of level

**Pattern**:
```python
from enum import Enum
from contextvars import ContextVar

class VerbosityLevel(Enum):
    """Verbosity levels for output control."""
    QUIET = 0
    NORMAL = 1
    VERBOSE = 2

_verbosity_context: ContextVar['VerbosityManager'] = ContextVar(
    'verbosity_context',
    default=None
)

class VerbosityManager:
    """Manages output verbosity levels."""
    
    def __init__(self, level: VerbosityLevel = VerbosityLevel.NORMAL):
        self.level = level
    
    def should_print_debug(self) -> bool:
        """Check if debug messages should be printed."""
        return self.level == VerbosityLevel.VERBOSE
    
    def should_print_info(self) -> bool:
        """Check if info messages should be printed."""
        return self.level in (VerbosityLevel.NORMAL, VerbosityLevel.VERBOSE)
    
    def should_print_summary(self) -> bool:
        """Check if summary should be printed."""
        return self.level in (VerbosityLevel.NORMAL, VerbosityLevel.VERBOSE)
    
    def should_print_error(self) -> bool:
        """Always print errors."""
        return True
    
    def should_print_warning(self) -> bool:
        """Always print warnings."""
        return True
    
    @classmethod
    def get_current(cls) -> 'VerbosityManager':
        """Get current verbosity manager from context."""
        manager = _verbosity_context.get()
        return manager or cls(VerbosityLevel.NORMAL)
    
    @classmethod
    def set_current(cls, manager: 'VerbosityManager') -> None:
        """Set current verbosity manager in context."""
        _verbosity_context.set(manager)
```

**Key Principles**:
- Three levels: QUIET, NORMAL, VERBOSE
- Always show errors and warnings
- Use context variables for global access
- Provide clear query methods

### 6. Prompt Utilities Module (prompt_utils.py)

**Purpose**: Provide interactive prompts with validation.

**Responsibilities**:
- Prompt for directory paths with validation
- Prompt for yes/no confirmations
- Prompt for choices from a list
- Handle keyboard interrupts gracefully
- Strip quotes from user input

**Pattern**:
```python
from pathlib import Path
from rich.prompt import Prompt, Confirm

class PromptUtils:
    """Utilities for interactive prompts with validation."""
    
    @staticmethod
    def prompt_directory(
        message: str,
        default: str | None = None
    ) -> Path:
        """Prompt for directory path with validation."""
        while True:
            try:
                path_input = Prompt.ask(message, default=default)
                path_input = path_input.strip().strip('"').strip("'")
                
                target_path = Path(path_input).expanduser().resolve()
                
                if not target_path.exists():
                    Prompt.ask(
                        f"[red]Error:[/red] Path does not exist: {target_path}\n"
                        "Press Enter to try again",
                        default=""
                    )
                    continue
                
                if not target_path.is_dir():
                    Prompt.ask(
                        f"[red]Error:[/red] Not a directory: {target_path}\n"
                        "Press Enter to try again",
                        default=""
                    )
                    continue
                
                return target_path
                
            except KeyboardInterrupt:
                raise
    
    @staticmethod
    def prompt_confirmation(
        message: str,
        default: bool = False
    ) -> bool:
        """Prompt for yes/no confirmation."""
        try:
            return Confirm.ask(message, default=default)
        except KeyboardInterrupt:
            raise
    
    @staticmethod
    def prompt_choice(message: str, choices: list[str]) -> str:
        """Prompt for selection from numbered choices."""
        if not choices:
            raise ValueError("Choices list cannot be empty")
        
        try:
            choice_str = "\n".join(
                f"{i+1}. {choice}" for i, choice in enumerate(choices)
            )
            full_message = f"{message}\n{choice_str}\n\nEnter choice number"
            
            while True:
                response = Prompt.ask(full_message)
                
                try:
                    choice_num = int(response)
                    if 1 <= choice_num <= len(choices):
                        return choices[choice_num - 1]
                    else:
                        Prompt.ask(
                            f"[red]Error:[/red] Enter 1-{len(choices)}\n"
                            "Press Enter to try again",
                            default=""
                        )
                except ValueError:
                    Prompt.ask(
                        "[red]Error:[/red] Enter a valid number\n"
                        "Press Enter to try again",
                        default=""
                    )
                    
        except KeyboardInterrupt:
            raise
```

**Key Principles**:
- Validate input before returning
- Re-prompt on invalid input (don't exit)
- Strip quotes from paths
- Handle Ctrl+C gracefully
- Use Rich prompts for consistency

### 7. Configuration Module (config.py)

**Purpose**: Manage application configuration with XDG compliance.

**Responsibilities**:
- Load configuration from JSON files
- Save configuration changes
- Provide XDG-compliant paths (Linux/macOS)
- Provide Windows-compliant paths (%APPDATA%)
- Create directories as needed
- Provide sensible defaults

**Pattern**:
```python
import json
import platform
from pathlib import Path
from typing import Any

def get_config_dir() -> Path:
    """Get XDG-compliant configuration directory."""
    system = platform.system()
    
    if system == "Windows":
        base = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming"))
    else:
        base = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))
    
    config_dir = base / "your_app_name"
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir

def get_state_dir() -> Path:
    """Get XDG-compliant state/data directory."""
    system = platform.system()
    
    if system == "Windows":
        base = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
    else:
        base = Path(os.environ.get("XDG_STATE_HOME", Path.home() / ".local" / "state"))
    
    state_dir = base / "your_app_name"
    state_dir.mkdir(parents=True, exist_ok=True)
    return state_dir

def load_config() -> dict[str, Any]:
    """Load configuration from file."""
    config_file = get_config_dir() / "config.json"
    
    if not config_file.exists():
        return get_default_config()
    
    try:
        with open(config_file, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return get_default_config()

def save_config(config: dict[str, Any]) -> None:
    """Save configuration to file."""
    config_file = get_config_dir() / "config.json"
    
    with open(config_file, "w") as f:
        json.dump(config, f, indent=2)

def get_default_config() -> dict[str, Any]:
    """Get default configuration."""
    return {
        "default_root": str(Path.cwd()),
        # Add your default settings
    }
```

**Key Principles**:
- XDG Base Directory compliance
- Windows compatibility
- Graceful handling of missing/corrupt files
- Sensible defaults
- Create directories automatically

## Data Models

### Standard Exit Codes

```python
# Exit codes
EXIT_SUCCESS = 0
EXIT_ERROR = 1
EXIT_INVALID_INPUT = 2
EXIT_PERMISSION_ERROR = 3
EXIT_USER_CANCELLED = 130
```

### Command Context Pattern

```python
from dataclasses import dataclass

@dataclass
class CommandContext:
    """Shared context for all commands."""
    verbosity: VerbosityManager
    auto_confirm: bool  # --yes flag
    formatter: OutputFormatter
    config: dict
```

## Error Handling

### Error Display Pattern

```python
def handle_command_error(
    error: Exception,
    formatter: OutputFormatter
) -> int:
    """Handle command errors and return exit code."""
    if isinstance(error, KeyboardInterrupt):
        formatter.print_warning("Operation cancelled by user")
        return EXIT_USER_CANCELLED
    
    elif isinstance(error, PermissionError):
        formatter.print_error(
            str(error),
            suggestion="Check file permissions"
        )
        return EXIT_PERMISSION_ERROR
    
    elif isinstance(error, FileNotFoundError):
        formatter.print_error(
            str(error),
            suggestion="Verify the path exists"
        )
        return EXIT_INVALID_INPUT
    
    else:
        formatter.print_error(str(error))
        return EXIT_ERROR
```

### Confirmation Prompt Pattern

```python
def confirm_destructive_operation(
    formatter: OutputFormatter,
    skip_confirmation: bool,
    operation_description: str
) -> bool:
    """Confirm destructive operation with user."""
    if skip_confirmation:
        return True
    
    try:
        return PromptUtils.prompt_confirmation(
            f"{operation_description} Proceed?",
            default=False
        )
    except KeyboardInterrupt:
        formatter.print_warning("Operation cancelled")
        return False
```

## Testing Strategy

### Unit Testing Pattern

```python
from unittest.mock import Mock
import pytest

def test_command_handler_success():
    """Test command handler with successful execution."""
    # Arrange
    formatter = Mock(spec=OutputFormatter)
    verbosity = VerbosityManager(VerbosityLevel.NORMAL)
    handler = CommandHandler(formatter, verbosity)
    
    # Act
    exit_code = handler.execute("test_arg")
    
    # Assert
    assert exit_code == 0
    formatter.print_success.assert_called_once()

def test_command_handler_error():
    """Test command handler with error."""
    formatter = Mock(spec=OutputFormatter)
    verbosity = VerbosityManager(VerbosityLevel.NORMAL)
    handler = CommandHandler(formatter, verbosity)
    
    # Act
    exit_code = handler.execute("")  # Invalid input
    
    # Assert
    assert exit_code == 2
    formatter.print_error.assert_called_once()
```

### CLI Integration Testing Pattern

```python
from typer.testing import CliRunner

def test_command_integration():
    """Test command end-to-end."""
    runner = CliRunner()
    result = runner.invoke(app, ["command-name", "arg"])
    
    assert result.exit_code == 0
    assert "expected output" in result.stdout

def test_command_with_verbose():
    """Test command with verbose flag."""
    runner = CliRunner()
    result = runner.invoke(app, ["command-name", "arg", "--verbose"])
    
    assert result.exit_code == 0
    assert "debug" in result.stdout.lower()
```

## Implementation Checklist

When building a new CLI using this template:

- [ ] Create module structure (cli.py, cli_handlers/, business/, etc.)
- [ ] Implement OutputFormatter with Rich
- [ ] Implement VerbosityManager with three levels
- [ ] Implement PromptUtils for interactive input
- [ ] Implement Configuration with XDG compliance
- [ ] Create shared utilities module (no duplication)
- [ ] Implement command handler classes
- [ ] Register commands in main CLI module
- [ ] Add command aliases (hidden)
- [ ] Implement --verbose, --quiet, --yes flags consistently
- [ ] Add confirmation prompts for destructive operations
- [ ] Implement proper error handling with exit codes
- [ ] Add comprehensive help text
- [ ] Write unit tests for handlers
- [ ] Write integration tests with CliRunner
- [ ] Test cross-platform compatibility
- [ ] Document all public APIs

## Best Practices Summary

1. **Separation of Concerns**: CLI layer only handles I/O, delegates to handlers
2. **Dependency Injection**: All dependencies passed via constructor
3. **No Duplication**: Extract shared code to utilities module
4. **Consistent Options**: Use same flags across all commands (--verbose, --quiet, --yes)
5. **Rich Output**: Use Rich library for professional formatting
6. **Graceful Degradation**: Handle limited terminals
7. **XDG Compliance**: Follow platform standards for config/data
8. **Exit Codes**: Return meaningful exit codes
9. **Error Messages**: Provide context and suggestions
10. **Testing**: Unit tests for handlers, integration tests for CLI

## Conclusion

This template provides a solid foundation for building professional CLI applications. Adapt the patterns to your specific domain while maintaining the core architectural principles of separation of concerns, dependency injection, and consistent user experience.
