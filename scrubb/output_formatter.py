"""Output formatting module with rich integration for CLI output."""

from __future__ import annotations
from pathlib import Path
from typing import Any
import unicodedata

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text


class OutputFormatter:
    """Handles rich formatting for CLI output."""
    
    def __init__(self, console: Console | None = None):
        """Initialize the output formatter.
        
        Args:
            console: Rich Console instance. If None, creates a new one.
        """
        self.console = console or Console()
    
    def print_success(self, message: str) -> None:
        """Print success message with green formatting.
        
        Args:
            message: The success message to display
        """
        # Wrap the entire message in green to ensure ANSI codes are generated
        self.console.print(f"[green] {message}[/green]")
    
    def print_error(self, message: str, suggestion: str | None = None) -> None:
        """Print error message with red formatting and optional suggestion.
        
        Args:
            message: The error message to display
            suggestion: Optional suggestion for resolving the error
        """
        content = f"[red]Error:[/red] {message}"
        if suggestion:
            content += f"\n\n[yellow]Suggestion:[/yellow] {suggestion}"
        
        panel = Panel(
            content,
            title=" Error",
            border_style="red"
        )
        self.console.print(panel)
    
    def print_warning(self, message: str) -> None:
        """Print warning message with yellow formatting.
        
        Args:
            message: The warning message to display
        """
        self.console.print(f"[yellow]![/yellow] {message}")
    
    def print_info(self, message: str) -> None:
        """Print info message with blue formatting.
        
        Args:
            message: The info message to display
        """
        self.console.print(f"[blue]i[/blue] {message}")
    
    def create_stats_table(self, stats: dict[str, Any]) -> Table:
        """Create a formatted table for statistics.
        
        Args:
            stats: Dictionary containing statistics data
            
        Returns:
            A formatted Rich Table object
        """
        table = Table(title="Statistics", show_header=True, header_style="bold cyan")
        table.add_column("Metric", style="cyan", no_wrap=True)
        table.add_column("Value", style="magenta")
        
        for key, value in stats.items():
            # Format the key to be more readable
            formatted_key = key.replace("_", " ").title()
            table.add_row(formatted_key, str(value))
        
        return table
    
    def create_panel(self, content: str, title: str, border_style: str = "blue") -> Panel:
        """Create a formatted panel with title.
        
        Args:
            content: The content to display in the panel
            title: The title of the panel
            border_style: The color/style of the panel border
            
        Returns:
            A formatted Rich Panel object
        """
        return Panel(
            content,
            title=title,
            border_style=border_style
        )
    
    def print_file_list(
        self, 
        files: list[str | Path], 
        status: str = "modified",
        title: str | None = None
    ) -> None:
        """Print a list of files with status indicators.
        
        Args:
            files: List of file paths to display
            status: Status type - 'modified', 'error', 'skipped', 'success'
            title: Optional title for the file list
        """
        # Define status indicators and colors
        status_config = {
            "modified": {"icon": "[+]", "color": "green"},
            "error": {"icon": "[X]", "color": "red"},
            "skipped": {"icon": "[-]", "color": "yellow"},
            "success": {"icon": "[]", "color": "green"},
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
    
    def format_emoji_display(self, emoji: str, count: int) -> str:
        """Format emoji for display with character and codepoint count.
        
        Args:
            emoji: The emoji character(s) to display
            count: The number of codepoints removed
            
        Returns:
            Formatted string with emoji and count
        """
        # Get codepoint notation for fallback
        codepoint = f"U+{ord(emoji[0]):04X}" if emoji else "U+0000"
        
        # Try to display emoji with fallback to codepoint notation
        try:
            # Check if emoji can be displayed (has a Unicode name)
            unicodedata.name(emoji[0])
            return f"{emoji} ({codepoint}) -> {count} codepoints"
        except (ValueError, TypeError):
            # Fallback to codepoint notation only
            return f"{codepoint} -> {count} codepoints"
    
    def create_emoji_stats_table(
        self, 
        emoji_stats: dict[str, int], 
        top_n: int = 5
    ) -> Table:
        """Create a formatted table for emoji statistics.
        
        Args:
            emoji_stats: Dictionary mapping emoji to count
            top_n: Number of top emojis to display
            
        Returns:
            A formatted Rich Table with rank, emoji, count, and percentage
        """
        table = Table(
            title="Top Emoji Statistics", 
            show_header=True, 
            header_style="bold cyan"
        )
        table.add_column("Rank", style="cyan", no_wrap=True, justify="right")
        table.add_column("Emoji", style="yellow", no_wrap=True)
        table.add_column("Count", style="magenta", justify="right")
        table.add_column("Percentage", style="green", justify="right")
        
        # Calculate total for percentages
        total_count = sum(emoji_stats.values())
        
        # Sort by count and add top N rows
        sorted_emojis = sorted(emoji_stats.items(), key=lambda x: x[1], reverse=True)
        for rank, (emoji, count) in enumerate(sorted_emojis[:top_n], 1):
            percentage = (count / total_count * 100) if total_count > 0 else 0
            
            # Get codepoint for fallback
            try:
                codepoint = f"U+{ord(emoji[0]):04X}"
                emoji_display = f"{emoji} ({codepoint})"
            except (ValueError, TypeError, IndexError):
                emoji_display = emoji
            
            table.add_row(
                str(rank),
                emoji_display,
                str(count),
                f"{percentage:.1f}%"
            )
        
        return table
    
    def print_verbose_emoji_details(
        self, 
        emoji: str, 
        count: int, 
        file_path: str | Path
    ) -> None:
        """Print detailed emoji information in verbose mode.
        
        Args:
            emoji: The emoji character(s)
            count: Number of occurrences
            file_path: Source file where emoji was found
        """
        # Get Unicode name and codepoint
        try:
            unicode_name = unicodedata.name(emoji[0])
            codepoint = f"U+{ord(emoji[0]):04X}"
        except (ValueError, TypeError, IndexError):
            unicode_name = "Unknown"
            codepoint = "U+0000"
        
        # Format the verbose output
        details = f"{emoji} ({unicode_name}, {codepoint}) - {count} occurrences in [cyan]{file_path}[/cyan]"
        self.console.print(f"  [yellow]*[/yellow] {details}")

    
    def print_error_group(
        self, 
        errors: list[tuple[str, str | Path]], 
        title: str = "Errors"
    ) -> None:
        """Print a group of errors with file paths.
        
        Args:
            errors: List of (error_message, file_path) tuples
            title: Title for the error group
        """
        if not errors:
            return
        
        # Group errors by error message
        error_groups: dict[str, list[str | Path]] = {}
        for error_msg, file_path in errors:
            if error_msg not in error_groups:
                error_groups[error_msg] = []
            error_groups[error_msg].append(file_path)
        
        # Display grouped errors
        self.console.print(f"\n[bold red]{title}[/bold red]")
        
        for error_msg, file_paths in error_groups.items():
            self.console.print(f"\n[red]Error:[/red] {error_msg}")
            self.console.print(f"[dim]Affected files ({len(file_paths)}):[/dim]")
            
            # Show first 5 files, then summarize if more
            for file_path in file_paths[:5]:
                path_obj = Path(file_path)
                parent = str(path_obj.parent) if path_obj.parent != Path(".") else ""
                name = path_obj.name
                
                if parent:
                    formatted_path = f"[dim]{parent}/[/dim][bold]{name}[/bold]"
                else:
                    formatted_path = f"[bold]{name}[/bold]"
                
                self.console.print(f"  [red][/red] {formatted_path}")
            
            if len(file_paths) > 5:
                self.console.print(f"  [dim]... and {len(file_paths) - 5} more files[/dim]")
