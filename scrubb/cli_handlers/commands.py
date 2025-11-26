"""CLI command handlers with dependency injection.

This module provides command handlers that separate business logic
from Typer decorators, enabling better testing and maintainability.
"""

from __future__ import annotations
from pathlib import Path

from ..config import load_config, save_config, load_stats, save_stats, DEFAULT_STATS
from ..scrubber import Scrubber
from ..file_classifier import FileClassifier
from ..folder_organizer import FolderOrganizer, DryRunFormatter
from ..tree_visualizer import TreeVisualizer
from ..tree_renderer import TreeRenderer, SimpleTreeRenderer, RICH_AVAILABLE
from ..verbosity import VerbosityManager
from .output import OutputFormatter
from .input import InputHandler


class EmojiCommand:
    """Handler for emoji scrubbing command.
    
    This class encapsulates the business logic for the emoji command,
    separating it from the CLI framework.
    """
    
    def __init__(
        self,
        formatter: OutputFormatter,
        verbosity_manager: VerbosityManager,
        config: dict,
    ):
        """Initialize the emoji command handler.
        
        Args:
            formatter: Output formatter for displaying results
            verbosity_manager: Verbosity manager for controlling output
            config: Configuration dictionary
        """
        self.formatter = formatter
        self.verbosity_manager = verbosity_manager
        self.config = config
    
    def execute(self, target: Path) -> int:
        """Execute emoji scrubbing.
        
        Args:
            target: Target path to scrub
            
        Returns:
            int: Exit code (0 for success, non-zero for error)
        """
        # Validate target exists
        if not target.exists():
            self.formatter.format_error(
                f"Path not found: {target}",
                suggestion="Check that the path is correct and accessible"
            )
            return 2
        
        # Initialize scrubber with current config
        scrubber = Scrubber(
            self.config["ignore_patterns"],
            self.config["text_extensions"]
        )
        
        # Choose file or directory
        if target.is_file():
            scrubber.scrub_file(target)
        else:
            scrubber.scrub_dir(target)
        
        # Get run statistics
        rs = scrubber.run
        
        # Display summary (controlled by verbosity)
        if self.verbosity_manager.should_print_summary():
            self.formatter.format_info(
                f"Files processed: {rs.files_processed}, "
                f"Modified: {rs.files_modified}, "
                f"Skipped: {rs.files_skipped}, "
                f"Errors: {rs.errors}, "
                f"Emojis removed: {rs.emojis_removed}"
            )
        
        # Display modified files (verbose mode)
        if self.verbosity_manager.should_print_debug() and rs.modified_files:
            self.formatter.format_file_list(
                rs.modified_files,
                status="modified",
                title="Modified files"
            )
        
        # Display error files (always shown)
        if rs.error_files:
            self.formatter.format_file_list(
                rs.error_files,
                status="error",
                title="Error files"
            )
        
        # Persist statistics
        self._persist_stats(rs)
        
        return 0
    
    def _persist_stats(self, run_stats) -> None:
        """Persist run statistics to global stats.
        
        Args:
            run_stats: Run statistics to persist
        """
        gs = load_stats()
        gs["runs"] += 1
        gs["files_processed"] += run_stats.files_processed
        gs["files_modified"] += run_stats.files_modified
        gs["files_skipped"] += run_stats.files_skipped
        gs["errors"] += run_stats.errors
        gs["emojis_removed"] += run_stats.emojis_removed
        
        # Merge scoped_scrub
        scoped = gs.get("scoped_scrub", {})
        for tok, cnt in run_stats.scoped_scrub.items():
            scoped[tok] = scoped.get(tok, 0) + cnt
        gs["scoped_scrub"] = scoped
        
        save_stats(gs)


class FolderCommand:
    """Handler for folder organization command.
    
    This class encapsulates the business logic for the folder command,
    separating it from the CLI framework.
    """
    
    def __init__(
        self,
        formatter: OutputFormatter,
        input_handler: InputHandler,
        verbosity_manager: VerbosityManager,
    ):
        """Initialize the folder command handler.
        
        Args:
            formatter: Output formatter for displaying results
            input_handler: Input handler for prompts
            verbosity_manager: Verbosity manager for controlling output
        """
        self.formatter = formatter
        self.input_handler = input_handler
        self.verbosity_manager = verbosity_manager
    
    def execute(
        self,
        dry_run: bool = False,
        show_tree: bool = False,
        skip_confirmation: bool = False,
    ) -> int:
        """Execute folder organization.
        
        Args:
            dry_run: Whether to run in dry-run mode
            show_tree: Whether to show tree visualization
            skip_confirmation: Whether to skip confirmation prompt
            
        Returns:
            int: Exit code (0 for success, non-zero for error)
        """
        # Display dry-run mode header if enabled
        if dry_run and self.verbosity_manager.should_print_info():
            self.formatter.format_info("DRY RUN MODE - No changes will be made")
        
        # Prompt for directory path
        try:
            # For now, use a simple root (current directory)
            # In production, this would use the config's default_root
            root = Path.cwd()
            target_path = self.input_handler.prompt_for_path(
                "Enter the directory path to organize",
                root=root,
                must_exist=True
            )
        except KeyboardInterrupt:
            self.formatter.format_info("Operation cancelled")
            return 130
        except Exception as e:
            self.formatter.format_error(str(e))
            return 2
        
        # Validate that path is a directory
        if not target_path.is_dir():
            self.formatter.format_error(
                f"Path is not a directory: {target_path}",
                suggestion="Provide a directory path, not a file path"
            )
            return 2
        
        # Create classifier and organizer
        classifier = FileClassifier()
        organizer = FolderOrganizer(target_path, classifier, dry_run=dry_run)
        
        # Tree visualization (before)
        visualizer = None
        before_snapshot = None
        if show_tree:
            renderer = TreeRenderer() if RICH_AVAILABLE else SimpleTreeRenderer()
            visualizer = TreeVisualizer(target_path, renderer)
            before_snapshot = visualizer.capture_before_state()
            visualizer.render_before_tree(before_snapshot)
        
        # Log target directory
        if self.verbosity_manager.should_print_info():
            self.formatter.format_info(f"Target directory: {target_path}")
        
        # Confirmation prompt (unless dry-run or skip_confirmation)
        if not dry_run and not skip_confirmation:
            try:
                self.formatter.format_info(
                    f"About to organize files in: {target_path}\n"
                    "This will move files into categorized folders and remove empty directories."
                )
                confirm = self.input_handler.prompt_for_confirmation(
                    "Do you want to proceed?",
                    default=False
                )
                if not confirm:
                    self.formatter.format_info("Operation cancelled")
                    return 130
            except KeyboardInterrupt:
                self.formatter.format_info("Operation cancelled")
                return 130
        
        # Execute organization
        stats = organizer.organize()
        
        # Tree visualization (after)
        if show_tree and visualizer:
            if dry_run:
                after_snapshot = visualizer.simulate_after_state(stats)
                visualizer.render_after_tree(after_snapshot, is_simulated=True)
            else:
                after_snapshot = visualizer.capture_after_state()
                visualizer.render_after_tree(after_snapshot, is_simulated=False)
            
            visualizer.display_comparison(before_snapshot, after_snapshot)
        
        # Display statistics
        if self.verbosity_manager.should_print_summary():
            if dry_run:
                # Dry-run mode - use DryRunFormatter
                formatted_output = DryRunFormatter.format_output(stats, target_path)
                print(formatted_output)
            else:
                # Actual mode - show completion information
                self._display_completion_stats(stats)
        
        return 0
    
    def _display_completion_stats(self, stats) -> None:
        """Display completion statistics.
        
        Args:
            stats: Organization statistics
        """
        self.formatter.format_success("Folder cleanup complete!")
        
        self.formatter.format_info(f"Files moved: {stats.files_moved}")
        
        if stats.files_by_category:
            print("\nFiles moved by category:")
            for category, count in sorted(stats.files_by_category.items()):
                print(f"  {category}: {count}")
        
        self.formatter.format_info(f"Empty folders removed: {stats.empty_folders_removed}")
        
        # Directory permission warnings
        if stats.directory_permission_warnings > 0:
            self.formatter.format_warning(
                f"Directory removal warnings: {stats.directory_permission_warnings}\n"
                "Some empty directories could not be removed (OneDrive, cloud storage, or system-protected)\n"
                "This is normal and does not affect file organization."
            )
        
        # Critical errors
        if stats.errors > 0:
            self.formatter.format_error(f"Critical errors encountered: {stats.errors}")
            for error_file in stats.error_files[:10]:
                print(f"  [X] {error_file}")
            if len(stats.error_files) > 10:
                print(f"  ... and {len(stats.error_files) - 10} more errors")


class StatsCommand:
    """Handler for statistics command.
    
    This class encapsulates the business logic for the stats command,
    separating it from the CLI framework.
    """
    
    def __init__(self, formatter: OutputFormatter, input_handler: InputHandler):
        """Initialize the stats command handler.
        
        Args:
            formatter: Output formatter for displaying results
            input_handler: Input handler for prompts
        """
        self.formatter = formatter
        self.input_handler = input_handler
    
    def execute(self, show_top: bool = False, reset: bool = False, skip_confirmation: bool = False) -> int:
        """Execute statistics command.
        
        Args:
            show_top: Whether to show top emoji statistics
            reset: Whether to reset statistics
            skip_confirmation: Whether to skip confirmation prompt
            
        Returns:
            int: Exit code (0 for success, non-zero for error)
        """
        if reset:
            # Confirmation prompt (unless skip_confirmation)
            if not skip_confirmation:
                try:
                    confirm = self.input_handler.prompt_for_confirmation(
                        "Are you sure you want to reset all statistics?",
                        default=False
                    )
                    if not confirm:
                        self.formatter.format_info("Operation cancelled")
                        return 130
                except KeyboardInterrupt:
                    self.formatter.format_info("Operation cancelled")
                    return 130
            
            save_stats(DEFAULT_STATS.copy())
            self.formatter.format_success("Persistent stats reset")
            return 0
        
        # Display statistics
        gs = load_stats()
        stats_dict = {
            "runs": gs["runs"],
            "files_processed": gs["files_processed"],
            "files_modified": gs["files_modified"],
            "files_skipped": gs["files_skipped"],
            "errors": gs["errors"],
            "emojis_removed": gs["emojis_removed"],
        }
        
        self.formatter.format_statistics(stats_dict, title="Persistent Statistics")
        
        # Show top emoji statistics if requested
        if show_top and gs.get("scoped_scrub"):
            from ..output_formatter import OutputFormatter as LegacyFormatter
            from rich.console import Console
            
            console = Console()
            legacy_formatter = LegacyFormatter(console)
            table = legacy_formatter.create_emoji_stats_table(gs["scoped_scrub"], top_n=5)
            console.print("\n")
            console.print(table)
        
        return 0


class ConfigCommand:
    """Handler for configuration command.
    
    This class encapsulates the business logic for the config command,
    separating it from the CLI framework.
    """
    
    def __init__(self, formatter: OutputFormatter):
        """Initialize the config command handler.
        
        Args:
            formatter: Output formatter for displaying results
        """
        self.formatter = formatter
    
    def execute(
        self,
        show: bool = False,
        new_path: str | None = None,
        edit: bool = False,
    ) -> int:
        """Execute configuration command.
        
        Args:
            show: Whether to show current configuration
            new_path: New path to set as default root
            edit: Whether to apply the new path
            
        Returns:
            int: Exit code (0 for success, non-zero for error)
        """
        from ..config import CONFIG_PATH, STATS_PATH
        
        cfg = load_config()
        
        # If no arguments provided, show current config
        if not show and not new_path and not edit:
            show = True
        
        if show:
            print(f"default_root: {cfg['default_root']}")
            print(f"config_file:  {CONFIG_PATH}")
            print(f"stats_file:   {STATS_PATH}")
            print(f"ignore_patterns: {len(cfg['ignore_patterns'])} patterns")
            print(f"text_extensions: {len(cfg['text_extensions'])} extensions")
        
        if new_path and edit:
            new_root = Path(new_path).expanduser().resolve()
            cfg["default_root"] = str(new_root)
            save_config(cfg)
            self.formatter.format_success(f"default_root updated -> {new_root}")
        elif new_path and not edit:
            self.formatter.format_error(
                "Use --edit flag to update the default root path",
                suggestion="Example: scrubb config -p /path/to/code --edit"
            )
            return 1
        elif edit and not new_path:
            self.formatter.format_error(
                "Provide a path with -p when using --edit",
                suggestion="Example: scrubb config -p /path/to/code --edit"
            )
            return 1
        
        return 0
