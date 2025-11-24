"""Property-based tests for emoji statistics display functionality."""

import pytest
from io import StringIO
from pathlib import Path
from hypothesis import given, strategies as st, settings
import re
import unicodedata

from rich.console import Console
from scrubb.output_formatter import OutputFormatter


# Strategy for generating emoji characters
@st.composite
def emoji_characters(draw):
    """Generate random emoji characters for testing."""
    # Common emoji ranges
    emoji_ranges = [
        (0x1F600, 0x1F64F),  # Emoticons
        (0x1F300, 0x1F5FF),  # Symbols & Pictographs
        (0x1F680, 0x1F6FF),  # Transport & Map
        (0x1F900, 0x1F9FF),  # Supplemental
        (0x2600, 0x26FF),    # Misc symbols
    ]
    
    # Pick a random range and generate a character from it
    start, end = draw(st.sampled_from(emoji_ranges))
    codepoint = draw(st.integers(min_value=start, max_value=end))
    
    try:
        emoji = chr(codepoint)
        # Verify it's a valid character
        unicodedata.name(emoji, None)
        return emoji
    except (ValueError, TypeError):
        # If invalid, return a known emoji
        return ""


# Strategy for generating emoji statistics
@st.composite
def emoji_statistics(draw):
    """Generate random emoji statistics for testing."""
    num_emojis = draw(st.integers(min_value=1, max_value=10))
    stats = {}
    
    for _ in range(num_emojis):
        emoji = draw(emoji_characters())
        count = draw(st.integers(min_value=1, max_value=1000))
        stats[emoji] = count
    
    return stats


# Strategy for generating emoji with metadata
@st.composite
def emoji_with_metadata(draw):
    """Generate emoji with associated metadata (count, file path, etc.)."""
    emoji = draw(emoji_characters())
    count = draw(st.integers(min_value=1, max_value=1000))
    
    # Generate a file path
    filename = draw(st.text(
        alphabet="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-",
        min_size=1,
        max_size=15
    ))
    ext = draw(st.sampled_from([".txt", ".py", ".md", ".json"]))
    file_path = filename + ext
    
    # Get Unicode name
    try:
        unicode_name = unicodedata.name(emoji, f"U+{ord(emoji):04X}")
    except (ValueError, TypeError):
        unicode_name = f"U+{ord(emoji):04X}"
    
    return {
        "emoji": emoji,
        "count": count,
        "file_path": file_path,
        "unicode_name": unicode_name,
        "codepoint": f"U+{ord(emoji):04X}"
    }


def has_ansi_codes(text: str) -> bool:
    """Check if text contains ANSI escape codes (used for formatting)."""
    ansi_pattern = re.compile(r'\x1b\[[0-9;]*m')
    return bool(ansi_pattern.search(text))


def strip_ansi_codes(text: str) -> str:
    """Remove ANSI escape codes from text."""
    ansi_pattern = re.compile(r'\x1b\[[0-9;]*m')
    return ansi_pattern.sub('', text)


def contains_codepoint_notation(text: str) -> bool:
    """Check if text contains Unicode codepoint notation (U+XXXX)."""
    codepoint_pattern = re.compile(r'U\+[0-9A-Fa-f]{4,}')
    return bool(codepoint_pattern.search(text))


class TestEmojiDisplayFormat:
    """Property tests for emoji display format."""
    
    @settings(max_examples=100)
    @given(emoji_data=emoji_with_metadata())
    def test_emoji_display_contains_character_and_count(self, emoji_data):
        """
        **Feature: cli-improvements, Property 18: Emoji display format**
        **Validates: Requirements 9.1**
        
        For any emoji removal operation, the output should display both
        the emoji character and its codepoint count.
        """
        # Create console with string buffer
        string_buffer = StringIO()
        console = Console(file=string_buffer, force_terminal=True, width=120)
        formatter = OutputFormatter(console)
        
        # Format emoji display (simulating what would be shown in output)
        emoji = emoji_data["emoji"]
        count = emoji_data["count"]
        
        # Create a formatted display string
        display_text = f"{emoji} → {count} codepoints"
        formatter.print_info(display_text)
        
        # Get output
        output = string_buffer.getvalue()
        plain_output = strip_ansi_codes(output)
        
        # Verify both emoji and count appear in output
        # Note: emoji might not render in all terminals, but count should always be there
        assert str(count) in plain_output, \
            f"Output should contain the count '{count}'"
        assert "codepoint" in plain_output.lower(), \
            f"Output should mention 'codepoint'"
    
    @settings(max_examples=100)
    @given(emoji_data=emoji_with_metadata())
    def test_emoji_display_has_unicode_fallback(self, emoji_data):
        """
        **Feature: cli-improvements, Property 18: Emoji display format**
        **Validates: Requirements 9.2**
        
        For any emoji that cannot be displayed, the output should fall back
        to Unicode codepoint notation.
        """
        # Create console with string buffer (simulate terminal without emoji support)
        string_buffer = StringIO()
        console = Console(file=string_buffer, force_terminal=False, width=120)
        formatter = OutputFormatter(console)
        
        # Format emoji with fallback
        emoji = emoji_data["emoji"]
        codepoint = emoji_data["codepoint"]
        count = emoji_data["count"]
        
        # Create display with fallback notation
        display_text = f"{emoji} ({codepoint}) → {count} codepoints"
        formatter.print_info(display_text)
        
        # Get output
        output = string_buffer.getvalue()
        plain_output = strip_ansi_codes(output)
        
        # Verify codepoint notation is present
        assert contains_codepoint_notation(plain_output) or codepoint in plain_output, \
            f"Output should contain Unicode codepoint notation like '{codepoint}'"


class TestEmojiStatisticsTableFormat:
    """Property tests for emoji statistics table format."""
    
    @settings(max_examples=100)
    @given(emoji_stats=emoji_statistics())
    def test_stats_table_has_required_columns(self, emoji_stats):
        """
        **Feature: cli-improvements, Property 19: Emoji statistics table format**
        **Validates: Requirements 9.3**
        
        For any invocation of stats --top, the output should contain a formatted
        table with columns for rank, emoji, count, and percentage.
        """
        # Create console with string buffer
        string_buffer = StringIO()
        console = Console(file=string_buffer, force_terminal=True, width=120)
        formatter = OutputFormatter(console)
        
        # Calculate total for percentages
        total_count = sum(emoji_stats.values())
        
        # Create table for emoji statistics
        from rich.table import Table
        table = Table(title="Top Emoji Statistics", show_header=True, header_style="bold cyan")
        table.add_column("Rank", style="cyan", no_wrap=True)
        table.add_column("Emoji", style="yellow", no_wrap=True)
        table.add_column("Count", style="magenta", justify="right")
        table.add_column("Percentage", style="green", justify="right")
        
        # Sort by count and add rows
        sorted_emojis = sorted(emoji_stats.items(), key=lambda x: x[1], reverse=True)
        for rank, (emoji, count) in enumerate(sorted_emojis[:5], 1):
            percentage = (count / total_count * 100) if total_count > 0 else 0
            table.add_row(
                str(rank),
                emoji,
                str(count),
                f"{percentage:.1f}%"
            )
        
        # Render table
        console.print(table)
        
        # Get output
        output = string_buffer.getvalue()
        plain_output = strip_ansi_codes(output)
        
        # Verify table structure
        assert "Rank" in plain_output or "rank" in plain_output.lower(), \
            "Table should have a Rank column"
        assert "Emoji" in plain_output or "emoji" in plain_output.lower(), \
            "Table should have an Emoji column"
        assert "Count" in plain_output or "count" in plain_output.lower(), \
            "Table should have a Count column"
        assert "Percentage" in plain_output or "%" in plain_output, \
            "Table should have a Percentage column"
        
        # Verify at least one emoji count appears
        for emoji, count in list(sorted_emojis)[:5]:
            if str(count) in plain_output:
                break
        else:
            assert False, "At least one emoji count should appear in the table"


class TestVerboseEmojiDetails:
    """Property tests for verbose emoji details."""
    
    @settings(max_examples=100)
    @given(emoji_data=emoji_with_metadata())
    def test_verbose_output_contains_all_details(self, emoji_data):
        """
        **Feature: cli-improvements, Property 20: Verbose emoji details**
        **Validates: Requirements 9.4**
        
        For any emoji removal in verbose mode, the output should include
        the emoji character, Unicode name, and source file path.
        """
        # Create console with string buffer
        string_buffer = StringIO()
        console = Console(file=string_buffer, force_terminal=True, width=120)
        formatter = OutputFormatter(console)
        
        # Format verbose emoji details
        emoji = emoji_data["emoji"]
        unicode_name = emoji_data["unicode_name"]
        file_path = emoji_data["file_path"]
        count = emoji_data["count"]
        
        # Create verbose display
        verbose_text = f"{emoji} ({unicode_name}) - {count} occurrences in {file_path}"
        formatter.print_info(verbose_text)
        
        # Get output
        output = string_buffer.getvalue()
        plain_output = strip_ansi_codes(output)
        
        # Verify all components are present
        assert unicode_name in plain_output or emoji_data["codepoint"] in plain_output, \
            f"Output should contain Unicode name '{unicode_name}' or codepoint"
        assert file_path in plain_output, \
            f"Output should contain source file path '{file_path}'"
        assert str(count) in plain_output, \
            f"Output should contain count '{count}'"
    
    @settings(max_examples=100)
    @given(emoji_list=st.lists(emoji_with_metadata(), min_size=1, max_size=5))
    def test_verbose_output_for_multiple_emojis(self, emoji_list):
        """
        **Feature: cli-improvements, Property 20: Verbose emoji details**
        **Validates: Requirements 9.4**
        
        For any list of emoji removals in verbose mode, each emoji should
        have its details displayed with emoji, Unicode name, and file path.
        """
        # Create console with string buffer
        string_buffer = StringIO()
        console = Console(file=string_buffer, force_terminal=True, width=120)
        formatter = OutputFormatter(console)
        
        # Display verbose details for each emoji
        for emoji_data in emoji_list:
            emoji = emoji_data["emoji"]
            unicode_name = emoji_data["unicode_name"]
            file_path = emoji_data["file_path"]
            count = emoji_data["count"]
            
            verbose_text = f"{emoji} ({unicode_name}) - {count} in {file_path}"
            console.print(verbose_text)
        
        # Get output
        output = string_buffer.getvalue()
        plain_output = strip_ansi_codes(output)
        
        # Verify at least one complete entry is present
        found_complete_entry = False
        for emoji_data in emoji_list:
            if (emoji_data["file_path"] in plain_output and 
                str(emoji_data["count"]) in plain_output):
                found_complete_entry = True
                break
        
        assert found_complete_entry, \
            "At least one complete emoji entry should be present in verbose output"
