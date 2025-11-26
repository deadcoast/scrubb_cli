"""CLI application for scrubb.

This module provides the Typer CLI application with command routing
and minimal business logic. All business logic is delegated to command
handlers in the cli_handlers package.
"""

from __future__ import annotations
from pathlib import Path
import typer

from .config import load_config
from .cli_handlers.shared import (
    setup_verbosity,
    resolve_path,
    create_formatter,
    load_default_root,
)
from .cli_handlers.commands import EmojiCommand, FolderCommand, StatsCommand, ConfigCommand
from .cli_handlers.input import InputHandler
from .io.path_validator import PathValidator

app = typer.Typer(
    add_completion=False,
    help="Emoji Scrubber CLI - Remove emojis from text files with persistent statistics tracking",
    no_args_is_help=True
)

@app.command(
    name="emoji",
    context_settings={"allow_extra_args": True, "ignore_unknown_options": True},
    help="Scrub emojis from text files and directories. Removes emojis from text files while preserving structure. Processes files recursively and provides detailed statistics about the operation."
)
def emoji(
    ctx: typer.Context,
    path: str = typer.Argument(None, help="Target path (optional) - defaults to configured root directory"),
    executor: str = typer.Argument(None, help="Must be '.' to indicate recursive processing of all files"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Display detailed debug information including file-by-file processing"),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Suppress all non-essential output, only show errors"),
):
    """Scrub emojis from text files and directories."""
    # Create formatter and setup verbosity
    formatter = create_formatter(stderr=True)
    verbosity_manager = setup_verbosity(verbose, quiet, formatter)
    
    # Load config and resolve target path
    cfg = load_config()
    default_root = load_default_root()
    target = resolve_path(path, executor, default_root)
    
    # Create and execute command
    command = EmojiCommand(formatter, verbosity_manager, cfg)
    exit_code = command.execute(target)
    
    raise typer.Exit(code=exit_code)

@app.command(
    help="View persistent statistics accumulated across all scrubbing runs. Displays comprehensive statistics maintained across all scrubbing operations."
)
def stats(
    top: bool = typer.Option(False, "--top", help="Show top 5 most frequently removed emoji tokens"),
    reset: bool = typer.Option(False, "--reset", help="Reset ALL persistent statistics to zero"),
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation prompts and proceed automatically"),
):
    """View persistent statistics accumulated across all scrubbing runs."""
    # Create formatter and input handler
    formatter = create_formatter()
    path_validator = PathValidator()
    input_handler = InputHandler(path_validator)
    
    # Create and execute command
    command = StatsCommand(formatter, input_handler)
    exit_code = command.execute(show_top=top, reset=reset, skip_confirmation=yes)
    
    raise typer.Exit(code=exit_code)

@app.command(
    name="main",
    hidden=True,
    context_settings={"allow_extra_args": True, "ignore_unknown_options": True},
)
def main(
    ctx: typer.Context,
    path: str = typer.Argument(None, help="Target path (optional) - defaults to configured root directory"),
    executor: str = typer.Argument(None, help="Must be '.' to indicate recursive processing of all files"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Display detailed debug information including file-by-file processing"),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Suppress all non-essential output, only show errors"),
):
    """Deprecated: Use 'scrubb emoji' instead."""
    # Display deprecation warning to stderr
    typer.secho(
        "\n  WARNING: The 'main' command is deprecated and will be removed in a future version.",
        fg=typer.colors.YELLOW,
        bold=True,
        err=True
    )
    typer.secho(
        "   Please use 'scrubb emoji' instead.",
        fg=typer.colors.YELLOW,
        err=True
    )
    typer.secho(
        "   See documentation for migration guide.\n",
        fg=typer.colors.YELLOW,
        err=True
    )
    
    # Redirect to emoji command with the same arguments
    ctx.invoke(emoji, ctx=ctx, path=path, executor=executor, verbose=verbose, quiet=quiet)

@app.command(
    help="Manage scrubb configuration settings and view current configuration. View and modify scrubb's configuration settings, including the default root directory."
)
def config(
    p: str = typer.Option(None, "-p", help="Path to set as new default root directory"),
    show: bool = typer.Option(False, "--show", help="Show current configuration (default behavior)"),
    edit: bool = typer.Option(False, "--edit", help="Apply the provided path (-p) as new default root"),
):
    """Manage scrubb configuration settings and view current configuration."""
    # Create formatter
    formatter = create_formatter()
    
    # Create and execute command
    command = ConfigCommand(formatter)
    exit_code = command.execute(show=show, new_path=p, edit=edit)
    
    raise typer.Exit(code=exit_code)

# ===== Command Aliases =====
# Hidden aliases for convenience - these invoke the main commands

@app.command(name="e", hidden=True, context_settings={"allow_extra_args": True, "ignore_unknown_options": True})
def e_alias(
    ctx: typer.Context,
    path: str = typer.Argument(None, help="Target path (optional) - defaults to configured root directory"),
    executor: str = typer.Argument(None, help="Must be '.' to indicate recursive processing of all files"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Display detailed debug information including file-by-file processing"),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Suppress all non-essential output, only show errors"),
):
    """Alias for 'emoji' command."""
    ctx.invoke(emoji, ctx=ctx, path=path, executor=executor, verbose=verbose, quiet=quiet)


@app.command(name="f", hidden=True)
def f_alias(
    dry: bool = typer.Option(False, "--dry", help="Preview changes without executing them"),
    tree: bool = typer.Option(False, "--tree", help="Display directory tree before and after execution"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Display detailed debug information including file-by-file processing"),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Suppress all non-essential output, only show errors"),
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation prompts and proceed automatically"),
):
    """Alias for 'folder' command."""
    folder(dry=dry, tree=tree, verbose=verbose, quiet=quiet, yes=yes)


@app.command(name="s", hidden=True)
def s_alias(
    top: bool = typer.Option(False, "--top", help="Show top 5 most frequently removed emoji tokens"),
    reset: bool = typer.Option(False, "--reset", help="Reset ALL persistent statistics to zero"),
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation prompts and proceed automatically"),
):
    """Alias for 'stats' command."""
    stats(top=top, reset=reset, yes=yes)


@app.command(name="c", hidden=True)
def c_alias(
    p: str = typer.Option(None, "-p", help="Path to set as new default root directory"),
    show: bool = typer.Option(False, "--show", help="Show current configuration (default behavior)"),
    edit: bool = typer.Option(False, "--edit", help="Apply the provided path (-p) as new default root"),
):
    """Alias for 'config' command."""
    config(p=p, show=show, edit=edit)

@app.command(
    help="Organize files into categorized folders and remove empty directories. Recursively scans the specified directory, categorizes files by type, and moves them to organized folders."
)
def folder(
    dry: bool = typer.Option(False, "--dry", help="Preview changes without executing them"),
    tree: bool = typer.Option(False, "--tree", help="Display directory tree before and after execution"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Display detailed debug information including file-by-file processing"),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Suppress all non-essential output, only show errors"),
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation prompts and proceed automatically"),
):
    """Organize files into categorized folders and remove empty directories."""
    # Create formatter and setup verbosity
    formatter = create_formatter(stderr=True)
    verbosity_manager = setup_verbosity(verbose, quiet, formatter)
    
    # Create input handler
    path_validator = PathValidator()
    input_handler = InputHandler(path_validator)
    
    # Create and execute command
    command = FolderCommand(formatter, input_handler, verbosity_manager)
    exit_code = command.execute(dry_run=dry, show_tree=tree, skip_confirmation=yes)
    
    raise typer.Exit(code=exit_code)