"""Compare before and after directory states and display differences."""

try:
    from rich.console import Console
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

from scrubb.tree_models import DirectorySnapshot
from scrubb.statistics_calculator import StatisticsCalculator


class TreeComparator:
    """Compare before and after states and display differences."""
    
    @staticmethod
    def display_comparison(before: DirectorySnapshot, after: DirectorySnapshot) -> None:
        """Display formatted comparison of before/after statistics.
        
        Args:
            before: DirectorySnapshot from before state
            after: DirectorySnapshot from after state
        """
        # Calculate delta using StatisticsCalculator
        delta = StatisticsCalculator.calculate_delta(before.statistics, after.statistics)
        
        # Initialize console for rich output if available
        if RICH_AVAILABLE:
            console = Console()
        
        # Display comparison header
        header = "\n" + "=" * 60
        comparison_title = "COMPARISON: Before → After"
        footer = "=" * 60
        
        if RICH_AVAILABLE:
            console.print(header, style="bold cyan")
            console.print(comparison_title.center(60), style="bold cyan")
            console.print(footer, style="bold cyan")
        else:
            print(header)
            print(comparison_title.center(60))
            print(footer)
        
        # Display file count delta
        files_delta_str = TreeComparator._format_delta(
            delta.files_delta,
            show_percentage=True,
            base_value=before.statistics.total_files
        )
        if RICH_AVAILABLE:
            console.print(f"\nFiles: {before.statistics.total_files} → {after.statistics.total_files} ({files_delta_str})")
        else:
            # Strip rich markup for plain text
            files_delta_plain = TreeComparator._strip_markup(files_delta_str)
            print(f"\nFiles: {before.statistics.total_files} → {after.statistics.total_files} ({files_delta_plain})")
        
        # Display directory count delta
        dirs_delta_str = TreeComparator._format_delta(
            delta.directories_delta,
            show_percentage=True,
            base_value=before.statistics.total_directories
        )
        if RICH_AVAILABLE:
            console.print(f"Directories: {before.statistics.total_directories} → {after.statistics.total_directories} ({dirs_delta_str})")
        else:
            dirs_delta_plain = TreeComparator._strip_markup(dirs_delta_str)
            print(f"Directories: {before.statistics.total_directories} → {after.statistics.total_directories} ({dirs_delta_plain})")
        
        # Display size delta
        before_size = StatisticsCalculator.format_size(before.statistics.total_size)
        after_size = StatisticsCalculator.format_size(after.statistics.total_size)
        size_delta_str = TreeComparator._format_delta(
            delta.size_delta,
            show_percentage=True,
            base_value=before.statistics.total_size
        )
        if RICH_AVAILABLE:
            console.print(f"Total Size: {before_size} → {after_size} ({size_delta_str})")
        else:
            size_delta_plain = TreeComparator._strip_markup(size_delta_str)
            print(f"Total Size: {before_size} → {after_size} ({size_delta_plain})")
        
        # Display depth delta
        depth_delta_str = TreeComparator._format_delta(
            delta.depth_delta,
            show_percentage=False
        )
        if RICH_AVAILABLE:
            console.print(f"Max Depth: {before.statistics.max_depth} → {after.statistics.max_depth} ({depth_delta_str})")
        else:
            depth_delta_plain = TreeComparator._strip_markup(depth_delta_str)
            print(f"Max Depth: {before.statistics.max_depth} → {after.statistics.max_depth} ({depth_delta_plain})")
        
        # Display category deltas if there are any changes
        if delta.category_deltas:
            if RICH_AVAILABLE:
                console.print("\nCategory Changes:", style="bold")
            else:
                print("\nCategory Changes:")
            
            for category, cat_delta in sorted(delta.category_deltas.items()):
                if cat_delta != 0:  # Only show categories with changes
                    before_count = before.statistics.files_by_category.get(category, 0)
                    after_count = after.statistics.files_by_category.get(category, 0)
                    cat_delta_str = TreeComparator._format_delta(
                        cat_delta,
                        show_percentage=True,
                        base_value=before_count
                    )
                    if RICH_AVAILABLE:
                        console.print(f"  {category}: {before_count} → {after_count} ({cat_delta_str})")
                    else:
                        cat_delta_plain = TreeComparator._strip_markup(cat_delta_str)
                        print(f"  {category}: {before_count} → {after_count} ({cat_delta_plain})")
        
        # Display footer
        if RICH_AVAILABLE:
            console.print("\n" + "=" * 60, style="bold cyan")
        else:
            print("\n" + "=" * 60)
    
    @staticmethod
    def _format_delta(value: int, show_percentage: bool = False, base_value: int = None) -> str:
        """Format delta with +/- indicators and optional percentage.
        
        Args:
            value: The delta value to format
            show_percentage: Whether to calculate and show percentage change
            base_value: The base value for percentage calculation (required if show_percentage is True)
            
        Returns:
            Formatted string with rich markup for color
        """
        # Determine sign and color
        if value > 0:
            sign = "+"
            color = "green"
        elif value < 0:
            sign = ""  # Negative sign is already included in the number
            color = "red"
        else:
            sign = ""
            color = "dim"
        
        # Format the basic delta
        delta_str = f"[{color}]{sign}{value}[/{color}]"
        
        # Add percentage if requested
        if show_percentage and base_value is not None and base_value != 0:
            percentage = (value / base_value) * 100
            if percentage > 0:
                percentage_str = f"[{color}], +{percentage:.1f}%[/{color}]"
            elif percentage < 0:
                percentage_str = f"[{color}], {percentage:.1f}%[/{color}]"
            else:
                percentage_str = f"[{color}], 0.0%[/{color}]"
            delta_str += percentage_str
        elif show_percentage and base_value == 0 and value != 0:
            # Special case: going from 0 to something
            delta_str += f"[{color}], ∞%[/{color}]"
        
        return delta_str
    
    @staticmethod
    def _strip_markup(text: str) -> str:
        """Strip rich markup from text for plain output.
        
        Args:
            text: Text with rich markup
            
        Returns:
            Plain text without markup
        """
        import re
        # Remove [color]...[/color] patterns
        return re.sub(r'\[/?[^\]]+\]', '', text)
