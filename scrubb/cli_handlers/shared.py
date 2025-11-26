"""Shared CLI utilities to eliminate code duplication.

This module provides shared functions for common CLI operations,
eliminating duplication across command implementations.
"""

from __future__ import annotations
from pathlib import Path

from rich.console import Console

from ..verbosity import VerbosityManager, VerbosityLevel
from ..config import load_config
from .output import OutputFormatter


def setup_verbosity(verbose: bool, quiet: bool, formatter: OutputFormatter) -> VerbosityManager:
    """Set up verbosity manager based on flags.
    
    Args:
        verbose: Whether verbose mode is enabled
        quiet: Whether quiet mode is enabled
        formatter: Output formatter for error messages
        
    Returns:
        VerbosityManager: Configured verbosity manager
        
    Raises:
        SystemExit: If both verbose and quiet flags are provided
    """
    # Validate flags
    if verbose and quiet:
        formatter.format_error(
            "Cannot use both --verbose and --quiet flags",
            suggestion="Choose either --verbose for detailed output or --quiet for minimal output"
        )
        raise SystemExit(2)
    
    # Determine verbosity level
    if verbose:
        verbosity_level = VerbosityLevel.VERBOSE
    elif quiet:
        verbosity_level = VerbosityLevel.QUIET
    else:
        verbosity_level = VerbosityLevel.NORMAL
    
    # Create and set verbosity manager
    verbosity_manager = VerbosityManager(verbosity_level)
    VerbosityManager.set_current(verbosity_manager)
    
    return verbosity_manager


def handle_error(error: Exception, formatter: OutputFormatter, exit_code: int = 1) -> None:
    """Handle error with consistent formatting.
    
    Args:
        error: The error to handle
        formatter: Output formatter for error messages
        exit_code: Exit code to use
        
    Raises:
        SystemExit: Always exits with the specified code
    """
    formatter.format_error(str(error))
    raise SystemExit(exit_code)


def resolve_path(arg_path: str | None, executor: str | None, default_root: Path) -> Path:
    """Resolve target path based on arguments.
    
    Resolution rules:
    - `scrubb .`                -> default_root
    - `scrubb src .`            -> default_root / 'src'
    - `scrubb /abs/or/rel .`    -> that path (if exists)
    - If executor not given, we still proceed.
    
    Args:
        arg_path: User-provided path argument
        executor: Executor argument (typically '.')
        default_root: Default root path from config
        
    Returns:
        Path: Resolved path
    """
    if arg_path is None:
        return default_root
    
    p = Path(arg_path)
    if p.exists():
        return p.resolve()
    
    # Treat as subpath under default root
    return (default_root / arg_path).resolve()


def confirm_operation(
    message: str,
    formatter: OutputFormatter,
    default: bool = False,
    skip_confirmation: bool = False,
) -> bool:
    """Prompt for confirmation with consistent handling.
    
    Args:
        message: Confirmation message to display
        formatter: Output formatter for messages
        default: Default value if user presses Enter
        skip_confirmation: Whether to skip confirmation
        
    Returns:
        bool: True if confirmed, False otherwise
        
    Raises:
        SystemExit: If user cancels with Ctrl+C
    """
    if skip_confirmation:
        return True
    
    try:
        from rich.prompt import Confirm
        return Confirm.ask(message, default=default)
    except KeyboardInterrupt:
        formatter.format_info("Operation cancelled")
        raise SystemExit(130)


def create_console(stderr: bool = False) -> Console:
    """Create a Rich Console instance.
    
    Args:
        stderr: Whether to output to stderr instead of stdout
        
    Returns:
        Console: Configured Rich Console instance
    """
    return Console(stderr=stderr)


def create_formatter(stderr: bool = False) -> OutputFormatter:
    """Create an OutputFormatter instance.
    
    Args:
        stderr: Whether to output to stderr instead of stdout
        
    Returns:
        OutputFormatter: Configured output formatter
    """
    console = create_console(stderr=stderr)
    return OutputFormatter(console)


def load_default_root() -> Path:
    """Load default root path from configuration.
    
    Returns:
        Path: Default root path
    """
    cfg = load_config()
    return Path(cfg["default_root"]).resolve()
