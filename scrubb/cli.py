from __future__ import annotations
import sys
from pathlib import Path
import typer

from .config import load_config, save_config, load_stats, save_stats, CONFIG_PATH, STATS_PATH
from .scrubber import Scrubber

app = typer.Typer(add_completion=False, help="Emoji Scrubber CLI (scrubb)")

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

@app.command(context_settings={"allow_extra_args": True, "ignore_unknown_options": True})
def main(
    ctx: typer.Context,
    path: str = typer.Argument(None, help="Optional path or subpath; see docs"),
    executor: str = typer.Argument(None, help="Use '.' to indicate 'ALL' (recursive)"),
):
    """
    Scrub emojis from files/directories.

    Examples:
      scrubb .
      scrubb src .
      scrubb ./docs .
    """
    cfg = load_config()
    target = _resolve_target(path, executor, Path(cfg["default_root"]).resolve())

    # Initialize scrubber w/ current config
    scrubber = Scrubber(cfg["ignore_patterns"], cfg["text_extensions"])

    # Choose file or directory
    if target.is_file():
        scrubber.scrub_file(target)
    else:
        if not target.exists():
            typer.echo(f"Path not found: {target}", err=True)
            raise typer.Exit(code=2)
        scrubber.scrub_dir(target)

    # ----- Ephemeral per-run output (ALWAYS printed at end of run) -----
    rs = scrubber.run
    typer.secho(
        f"scrubb run: files_processed={rs.files_processed} modified={rs.files_modified} "
        f"skipped={rs.files_skipped} errors={rs.errors} emojis_removed={rs.emojis_removed}",
        bold=True,
    )
    
    # Show detailed file information
    if rs.modified_files:
        typer.secho("\nModified files:", fg="green", bold=True)
        for file_path in rs.modified_files:
            typer.echo(f"  [+] {file_path}")
    
    if rs.error_files:
        typer.secho("\nError files:", fg="red", bold=True)
        for file_path in rs.error_files:
            typer.echo(f"  [X] {file_path}")
    
    if rs.scoped_scrub:
        typer.secho("\nEmoji tokens removed:", fg="yellow", bold=True)
        # Show top 5 emoji tokens for this run
        items = sorted(rs.scoped_scrub.items(), key=lambda kv: kv[1], reverse=True)[:5]
        for i, (emoji_token, count) in enumerate(items, 1):
            # Show emoji count with index to avoid Unicode display issues on Windows
            typer.echo(f"  #{i}: {count} codepoints")

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

@app.command()
def stats(
    top: bool = typer.Option(False, "--top", help="Show top 5 scrubbed emoji"),
    reset: bool = typer.Option(False, "--reset", help="Reset ALL persistent statistics"),
):
    """
    Print global/persistent statistics (across runs).
    """
    if reset:
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
        # Show top 5 tokens by count (count is measured in removed codepoints length)
        items = sorted(gs["scoped_scrub"].items(), key=lambda kv: kv[1], reverse=True)[:5]
        if items:
            typer.echo("top_scrubs:")
            for emoji_token, count in items:
                typer.echo(f"  {emoji_token}  -> {count}")

@app.command()
def config(
    p: str = typer.Option(None, "-p", help="Default root path"),
    show: bool = typer.Option(False, "--show", help="Show current default root path"),
    edit: bool = typer.Option(False, "--edit", help="Apply provided -p as the new default"),
):
    """
    Manage scrubb configuration.
    
    Examples:
      scrubb config --show              # Show current configuration
      scrubb config -p /path --edit     # Set new default root
      scrubb config                     # Show current configuration (default)
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
        typer.echo("Error: Use --edit flag to update the default root path", err=True)
        typer.echo("Example: scrubb config -p /path/to/code --edit")
        raise typer.Exit(code=1)
    elif edit and not p:
        typer.echo("Error: Provide a path with -p when using --edit", err=True)
        typer.echo("Example: scrubb config -p /path/to/code --edit")
        raise typer.Exit(code=1)