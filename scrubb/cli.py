from __future__ import annotations
import sys
from pathlib import Path
import typer

from .config import load_config, save_config, load_stats, save_stats, CONFIG_PATH, STATS_PATH
from .scrubber import Scrubber
from .file_classifier import FileClassifier
from .folder_organizer import FolderOrganizer, DryRunFormatter
from .tree_visualizer import TreeVisualizer
from .tree_renderer import TreeRenderer, SimpleTreeRenderer, RICH_AVAILABLE
from .verbosity import VerbosityManager, VerbosityLevel
from .prompt_utils import PromptUtils

app = typer.Typer(
    add_completion=False, 
    help="Emoji Scrubber CLI - Remove emojis from text files with persistent statistics tracking",
    no_args_is_help=True
)

def _resolve_target(arg_path: str | None, executor: str | None, default_root: Path) -> Path:
    """
    Resolution rules to satisfy your UX:
    - `scrubb .`                -> default_root
    - `scrubb src .`            -> default_root / 'src'
    - `scrubb /abs/or/rel .`    -> that path (if exists)
    - If executor not given, we still proceed.
    """
    if arg_path is None:
        return default_root
    p = Path(arg_path)
    if p.exists():
        return p.resolve()
    # treat as subpath under default root
    return (default_root / arg_path).resolve()

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
    """
    Scrub emojis from text files and directories.
    
    Removes emojis from text files while preserving structure. Processes files recursively
    and provides detailed statistics about the operation.
    """
    # Set up verbosity manager
    if verbose and quiet:
        from .output_formatter import OutputFormatter
        from rich.console import Console
        
        console = Console(stderr=True)
        formatter = OutputFormatter(console)
        formatter.print_error(
            "Cannot use both --verbose and --quiet flags",
            suggestion="Choose either --verbose for detailed output or --quiet for minimal output"
        )
        raise typer.Exit(code=2)
    
    if verbose:
        verbosity_level = VerbosityLevel.VERBOSE
    elif quiet:
        verbosity_level = VerbosityLevel.QUIET
    else:
        verbosity_level = VerbosityLevel.NORMAL
    
    verbosity_manager = VerbosityManager(verbosity_level)
    VerbosityManager.set_current(verbosity_manager)
    
    cfg = load_config()
    target = _resolve_target(path, executor, Path(cfg["default_root"]).resolve())

    # Initialize scrubber w/ current config
    scrubber = Scrubber(cfg["ignore_patterns"], cfg["text_extensions"])

    # Choose file or directory
    if target.is_file():
        scrubber.scrub_file(target)
    else:
        if not target.exists():
            from .output_formatter import OutputFormatter
            from rich.console import Console
            
            console = Console(stderr=True)
            formatter = OutputFormatter(console)
            formatter.print_error(
                f"Path not found: {target}",
                suggestion="Check that the path is correct and accessible"
            )
            raise typer.Exit(code=2)
        scrubber.scrub_dir(target)

    # ----- Ephemeral per-run output (controlled by verbosity) -----
    rs = scrubber.run
    
    # Summary output (shown in NORMAL and VERBOSE modes)
    if verbosity_manager.should_print_summary():
        typer.secho(
            f"scrubb run: files_processed={rs.files_processed} modified={rs.files_modified} "
            f"skipped={rs.files_skipped} errors={rs.errors} emojis_removed={rs.emojis_removed}",
            bold=True,
        )
    
    # Detailed file information (shown in VERBOSE mode)
    if verbosity_manager.should_print_debug():
        if rs.modified_files:
            typer.secho("\nModified files:", fg="green", bold=True)
            for file_path in rs.modified_files:
                typer.echo(f"  [+] {file_path}")
    
    # Error files (always shown - errors are always displayed)
    if rs.error_files:
        from .output_formatter import OutputFormatter
        from rich.console import Console
        
        console = Console()
        formatter = OutputFormatter(console)
        formatter.print_file_list(rs.error_files, status="error", title="Error files")
    
    # Emoji tokens removed (shown in NORMAL and VERBOSE modes)
    if verbosity_manager.should_print_info() and rs.scoped_scrub:
        from .output_formatter import OutputFormatter
        from rich.console import Console
        
        console = Console()
        formatter = OutputFormatter(console)
        
        typer.secho("\nEmoji tokens removed:", fg="yellow", bold=True)
        # Show top 5 emoji tokens for this run
        items = sorted(rs.scoped_scrub.items(), key=lambda kv: kv[1], reverse=True)[:5]
        for i, (emoji_token, count) in enumerate(items, 1):
            # Use formatter to display emoji with character and codepoint
            display = formatter.format_emoji_display(emoji_token, count)
            typer.echo(f"  #{i}: {display}")
        
        # In verbose mode, show detailed information with file paths
        if verbosity_manager.should_print_debug() and rs.modified_files:
            typer.secho("\nDetailed emoji removal information:", fg="cyan", bold=True)
            # For verbose mode, we'd need to track which emojis came from which files
            # For now, just show the files that were modified
            for file_path in rs.modified_files[:10]:  # Limit to first 10 files
                typer.echo(f"  Modified: {file_path}")

    # ----- Persist into global stats -----
    gs = load_stats()
    gs["runs"] += 1
    gs["files_processed"] += rs.files_processed
    gs["files_modified"]  += rs.files_modified
    gs["files_skipped"]   += rs.files_skipped
    gs["errors"]          += rs.errors
    gs["emojis_removed"]  += rs.emojis_removed

    # merge scoped_scrub
    scoped = gs.get("scoped_scrub", {})
    for tok, cnt in rs.scoped_scrub.items():
        scoped[tok] = scoped.get(tok, 0) + cnt
    gs["scoped_scrub"] = scoped
    save_stats(gs)

@app.command(
    help="View persistent statistics accumulated across all scrubbing runs. Displays comprehensive statistics maintained across all scrubbing operations."
)
def stats(
    top: bool = typer.Option(False, "--top", help="Show top 5 most frequently removed emoji tokens"),
    reset: bool = typer.Option(False, "--reset", help="Reset ALL persistent statistics to zero"),
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation prompts and proceed automatically"),
):
    """
    View persistent statistics accumulated across all scrubbing runs.
    
    Displays comprehensive statistics maintained across all scrubbing operations.
    """
    if reset:
        # Confirmation prompt for destructive operation (unless --yes is provided)
        if not yes:
            try:
                confirm = PromptUtils.prompt_confirmation("Are you sure you want to reset all statistics?", default=False)
                if not confirm:
                    typer.echo("Operation cancelled.")
                    raise typer.Exit(code=130)
            except KeyboardInterrupt:
                typer.echo("\nOperation cancelled.")
                raise typer.Exit(code=130)
        
        from .config import DEFAULT_STATS
        save_stats(DEFAULT_STATS.copy())
        typer.echo("Persistent stats reset.")
        raise typer.Exit()

    gs = load_stats()
    typer.echo(f"runs:            {gs['runs']}")
    typer.echo(f"files_processed: {gs['files_processed']}")
    typer.echo(f"files_modified:  {gs['files_modified']}")
    typer.echo(f"files_skipped:   {gs['files_skipped']}")
    typer.echo(f"errors:          {gs['errors']}")
    typer.echo(f"emojis_removed:  {gs['emojis_removed']}")

    if top and gs.get("scoped_scrub"):
        # Show top 5 tokens by count using rich formatted table
        from .output_formatter import OutputFormatter
        from rich.console import Console
        
        console = Console()
        formatter = OutputFormatter(console)
        
        # Create and display emoji statistics table
        table = formatter.create_emoji_stats_table(gs["scoped_scrub"], top_n=5)
        console.print("\n")
        console.print(table)

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
    """
    Deprecated: Use 'scrubb emoji' instead.
    
    This command is deprecated and will be removed in a future version.
    """
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
    """
    Manage scrubb configuration settings and view current configuration.
    
    View and modify scrubb's configuration settings, including the default root directory.
    """
    cfg = load_config()
    
    # If no arguments provided, show current config (same as --show)
    if not show and not p and not edit:
        show = True
    
    if show:
        typer.echo(f"default_root: {cfg['default_root']}")
        typer.echo(f"config_file:  {CONFIG_PATH}")
        typer.echo(f"stats_file:   {STATS_PATH}")
        typer.echo(f"ignore_patterns: {len(cfg['ignore_patterns'])} patterns")
        typer.echo(f"text_extensions: {len(cfg['text_extensions'])} extensions")

    if p and edit:
        new_root = Path(p).expanduser().resolve()
        cfg["default_root"] = str(new_root)
        save_config(cfg)
        typer.echo(f"default_root updated -> {new_root}")
    elif p and not edit:
        from .output_formatter import OutputFormatter
        from rich.console import Console
        
        console = Console(stderr=True)
        formatter = OutputFormatter(console)
        formatter.print_error(
            "Use --edit flag to update the default root path",
            suggestion="Example: scrubb config -p /path/to/code --edit"
        )
        raise typer.Exit(code=1)
    elif edit and not p:
        from .output_formatter import OutputFormatter
        from rich.console import Console
        
        console = Console(stderr=True)
        formatter = OutputFormatter(console)
        formatter.print_error(
            "Provide a path with -p when using --edit",
            suggestion="Example: scrubb config -p /path/to/code --edit"
        )
        raise typer.Exit(code=1)

# ===== Command Aliases =====
# Hidden aliases for convenience - these invoke the main commands

@app.command(
    name="e",
    hidden=True,
    context_settings={"allow_extra_args": True, "ignore_unknown_options": True},
)
def e_alias(
    ctx: typer.Context,
    path: str = typer.Argument(None, help="Target path (optional) - defaults to configured root directory"),
    executor: str = typer.Argument(None, help="Must be '.' to indicate recursive processing of all files"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Display detailed debug information including file-by-file processing"),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Suppress all non-essential output, only show errors"),
):
    """Alias for 'emoji' command."""
    ctx.invoke(emoji, ctx=ctx, path=path, executor=executor, verbose=verbose, quiet=quiet)

@app.command(
    name="f",
    hidden=True,
)
def f_alias(
    dry: bool = typer.Option(False, "--dry", help="Preview changes without executing them"),
    tree: bool = typer.Option(False, "--tree", help="Display directory tree before and after execution"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Display detailed debug information including file-by-file processing"),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Suppress all non-essential output, only show errors"),
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation prompts and proceed automatically"),
):
    """Alias for 'folder' command."""
    # Directly call the folder function with the same arguments
    folder(dry=dry, tree=tree, verbose=verbose, quiet=quiet, yes=yes)

@app.command(
    name="s",
    hidden=True,
)
def s_alias(
    top: bool = typer.Option(False, "--top", help="Show top 5 most frequently removed emoji tokens"),
    reset: bool = typer.Option(False, "--reset", help="Reset ALL persistent statistics to zero"),
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation prompts and proceed automatically"),
):
    """Alias for 'stats' command."""
    # Directly call the stats function with the same arguments
    stats(top=top, reset=reset, yes=yes)

@app.command(
    name="c",
    hidden=True,
)
def c_alias(
    p: str = typer.Option(None, "-p", help="Path to set as new default root directory"),
    show: bool = typer.Option(False, "--show", help="Show current configuration (default behavior)"),
    edit: bool = typer.Option(False, "--edit", help="Apply the provided path (-p) as new default root"),
):
    """Alias for 'config' command."""
    # Directly call the config function with the same arguments
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
    """
    Organize files into categorized folders and remove empty directories.
    
    Recursively scans the specified directory, categorizes files by type (Images, Video, 
    Documents, Development), and moves them to organized folders within a 'Scrubbed' directory.
    Empty directories are removed after file organization.
    """
    # Set up verbosity manager
    if verbose and quiet:
        from .output_formatter import OutputFormatter
        from rich.console import Console
        
        console = Console(stderr=True)
        formatter = OutputFormatter(console)
        formatter.print_error(
            "Cannot use both --verbose and --quiet flags",
            suggestion="Choose either --verbose for detailed output or --quiet for minimal output"
        )
        raise typer.Exit(code=2)
    
    if verbose:
        verbosity_level = VerbosityLevel.VERBOSE
    elif quiet:
        verbosity_level = VerbosityLevel.QUIET
    else:
        verbosity_level = VerbosityLevel.NORMAL
    
    verbosity_manager = VerbosityManager(verbosity_level)
    VerbosityManager.set_current(verbosity_manager)
    
    # Display dry-run mode header if enabled (shown in NORMAL and VERBOSE modes)
    if dry and verbosity_manager.should_print_info():
        typer.secho("\n DRY RUN MODE - No changes will be made\n", fg=typer.colors.YELLOW, bold=True)
    
    # Prompt for directory path
    path_input = typer.prompt("Enter the directory path to organize")
    
    # Strip quotes from path input (handles both single and double quotes)
    path_input = path_input.strip().strip('"').strip("'")
    
    # Resolve path (handle absolute, relative, and tilde expansion)
    target_path = Path(path_input).expanduser().resolve()
    
    # Validate that path exists and is a directory
    if not target_path.exists():
        from .output_formatter import OutputFormatter
        from rich.console import Console
        
        console = Console(stderr=True)
        formatter = OutputFormatter(console)
        formatter.print_error(
            f"Path does not exist: {target_path}",
            suggestion="Check that the path is correct and accessible"
        )
        raise typer.Exit(code=2)
    
    if not target_path.is_dir():
        from .output_formatter import OutputFormatter
        from rich.console import Console
        
        console = Console(stderr=True)
        formatter = OutputFormatter(console)
        formatter.print_error(
            f"Path is not a directory: {target_path}",
            suggestion="Provide a directory path, not a file path"
        )
        raise typer.Exit(code=2)
    
    # Create classifier and organizer with dry_run parameter
    classifier = FileClassifier()
    organizer = FolderOrganizer(target_path, classifier, dry_run=dry)
    
    # Tree visualization if enabled (Requirements 9.1 - trees display before standard output)
    if tree:
        # Use SimpleTreeRenderer if rich is unavailable
        renderer = TreeRenderer() if RICH_AVAILABLE else SimpleTreeRenderer()
        visualizer = TreeVisualizer(target_path, renderer)
        before_snapshot = visualizer.capture_before_state()
        visualizer.render_before_tree(before_snapshot)
    
    # Log target directory after tree visualization (Requirements 4.1, 9.1)
    if verbosity_manager.should_print_info():
        typer.echo(f"Target directory: {target_path}")
    
    # Confirmation prompt for destructive operation (unless --dry or --yes is provided)
    if not dry and not yes:
        typer.echo(f"\nAbout to organize files in: {target_path}")
        typer.echo("This will move files into categorized folders and remove empty directories.")
        try:
            confirm = PromptUtils.prompt_confirmation("Do you want to proceed?", default=False)
            if not confirm:
                typer.echo("Operation cancelled.")
                raise typer.Exit(code=130)
        except KeyboardInterrupt:
            typer.echo("\nOperation cancelled.")
            raise typer.Exit(code=130)
    
    # Execute organization
    stats = organizer.organize()
    
    # Tree visualization after execution
    if tree:
        if dry:
            # Dry-run mode - simulate after state
            after_snapshot = visualizer.simulate_after_state(stats)
            visualizer.render_after_tree(after_snapshot, is_simulated=True)
        else:
            # Actual mode - capture after state
            after_snapshot = visualizer.capture_after_state()
            visualizer.render_after_tree(after_snapshot, is_simulated=False)
        
        # Display comparison
        visualizer.display_comparison(before_snapshot, after_snapshot)
    
    # Display statistics based on mode
    if dry:
        # Dry-run mode - use DryRunFormatter for detailed output (shown in NORMAL and VERBOSE modes)
        if verbosity_manager.should_print_summary():
            formatted_output = DryRunFormatter.format_output(stats, target_path)
            typer.echo(formatted_output)
    else:
        # Actual mode - show completion information (shown in NORMAL and VERBOSE modes)
        if verbosity_manager.should_print_summary():
            typer.echo("\n" + "="*50)
            typer.secho("Folder cleanup complete!", fg="green", bold=True)
            typer.echo("="*50)
            
            typer.secho(f"\nFiles moved: {stats.files_moved}", fg="cyan", bold=True)
            
            if stats.files_by_category:
                typer.secho("\nFiles moved by category:", fg="cyan")
                for category, count in sorted(stats.files_by_category.items()):
                    typer.echo(f"  {category}: {count}")
            
            typer.secho(f"\nEmpty folders removed: {stats.empty_folders_removed}", fg="cyan", bold=True)
        
        # Errors are always shown
        if stats.errors > 0:
            from .output_formatter import OutputFormatter
            from rich.console import Console
            
            console = Console()
            formatter = OutputFormatter(console)
            
            typer.secho(f"\nErrors encountered: {stats.errors}", fg="red", bold=True)
            if stats.error_files:
                formatter.print_file_list(stats.error_files, status="error", title="Error files")