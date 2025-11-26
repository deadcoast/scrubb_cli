"""CLI output formatting with dependency injection.

This module provides output formatting for CLI commands with consistent
styling and proper separation of concerns.
"""

from __future__ import annotations
from pathlib import Path
from typing import Any

from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from ..core.result import OperationResult
from ..core.errors import ScrubbError


class OutputFormatter:
    """Handles CLI output formatting with dependency injection.
    
    This class provides consistent formatting for all CLI output,
    including operation results, errors, warnings, and statistics.
    """
    
    def __init__(self, console: Console):
        """Initialize the output formatter.
        
        Args:
            console: Rich Console instance for output
        """
        self.console = console
    
    def format_operation_result(self, result: OperationResult, dry_run: bool = False) -> None:
        """Format and display operation result.
        
        Args:
            result: The operation result to format
            dry_run: Whether this was a dry-run operation
        """
        # Header
        mode = "DRY RUN" if dry_run else "COMPLETE"
        status = "Preview" if dry_run else "Success" if result.success else "Completed with errors"
        color = "yellow" if dry_run else "green" if result.success else "red"
        
        self.console.print()
        self.console.print("=" * 50)
        self.console.print(f"[bold {color}]{mode}: {status}[/bold {color}]")
        self.console.print("=" * 50)
        self.console.print()
        
        # Statistics
        self.console.print(f"Files moved: {result.files_moved}")
        
        if result.files_by_category:
            self.console.print("\nFiles moved by category:")
            for category, count in sorted(result.files_by_category.items()):
                self.console.print(f"  {category}: {count}")
        
        self.console.print(f"\nEmpty folders removed: {result.empty_folders_removed}")
        
        # Warnings
        if result.warnings:
            self.console.print(f"\n[yellow]Warnings: {len(result.warnings)}[/yellow]")
            for warning in result.warnings[:5]:
                self.format_warning(str(warning))
            if len(result.warnings) > 5:
                self.console.print(f"  [dim]... and {len(result.warnings) - 5} more warnings[/dim]")
        
        # Critical errors
        if result.critical_errors:
            self.console.print(f"\n[red]Critical errors: {len(result.critical_errors)}[/red]")
            for error in result.critical_errors[:5]:
                self.format_error(str(error))
            if len(result.critical_errors) > 5:
                self.console.print(f"  [dim]... and {len(result.critical_errors) - 5} more errors[/dim]")
    
    def format_error(self, message: str, suggestion: str | None = None) -> None:
        """Format and display error message.
        
        Args:
            message: The error message to display
            suggestion: Optional suggestion for resolving the error
        """
        content = f"[red]Error:[/red] {message}"
        if suggestion:
            content += f"\n\n[yellow]Suggestion:[/yellow] {suggestion}"
        
        panel = Panel(
            content,
            title="❌ Error",
            border_style="red"
        )
        self.console.print(panel)
    
    def format_warning(self, message: str) -> None:
        """Format and display warning message.
        
        Args:
            message: The warning message to display
        """
        self.console.print(f"[yellow]⚠[/yellow]  {message}")
    
    def format_statistics(self, stats: dict[str, Any], title: str = "Statistics") -> None:
        """Format and display statistics table.
        
        Args:
            stats: Dictionary containing statistics data
            title: Title for the statistics table
        """
        table = Table(title=title, show_header=True, header_style="bold cyan")
        table.add_column("Metric", style="cyan", no_wrap=True)
        table.add_column("Value", style="magenta")
        
        for key, value in stats.items():
            # Format the key to be more readable
            formatted_key = key.replace("_", " ").title()
            table.add_row(formatted_key, str(value))
        
        self.console.print(table)
    
    def format_file_list(
        self,
        files: list[str | Path],
        status: str = "modified",
        title: str | None = None
    ) -> None:
        """Format and display a list of files with status indicators.
        
        Args:
            files: List of file paths to display
            status: Status type - 'modified', 'error', 'skipped', 'success', 'moved'
            title: Optional title for the file list
        """
        # Define status indicators and colors
        status_config = {
            "modified": {"icon": "[+]", "color": "green"},
            "error": {"icon": "[X]", "color": "red"},
            "skipped": {"icon": "[-]", "color": "yellow"},
            "success": {"icon": "[✓]", "color": "green"},
            "moved": {"icon": "[>]", "color": "cyan"},
        }
        
        config = status_config.get(status, {"icon": "[*]", "color": "white"})
        
        # Print title if provided
        if title:
            self.console.print(f"\n[bold {config['color']}]{title}[/bold {config['color']}]")
        
        # Print each file with status indicator and path highlighting
        for file_path in files:
            path_obj = Path(file_path)
            
            # Highlight different parts of the path
            parent = str(path_obj.parent) if path_obj.parent != Path(".") else ""
            name = path_obj.name
            
            if parent:
                formatted_path = f"[dim]{parent}/[/dim][bold]{name}[/bold]"
            else:
                formatted_path = f"[bold]{name}[/bold]"
            
            self.console.print(
                f"  [{config['color']}]{config['icon']}[/{config['color']}] {formatted_path}"
            )
    
    def format_success(self, message: str) -> None:
        """Format and display success message.
        
        Args:
            message: The success message to display
        """
        self.console.print(f"[green]✓[/green] {message}")
    
    def format_info(self, message: str) -> None:
        """Format and display info message.
        
        Args:
            message: The info message to display
        """
        self.console.print(f"[blue]ℹ[/blue] {message}")
