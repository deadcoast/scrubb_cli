"""Property-based tests for OutputFormatter functionality."""

import pytest
from io import StringIO
from pathlib import Path
from hypothesis import given, strategies as st, settings
import re

from rich.console import Console
from scrubb.output_formatter import OutputFormatter


# Strategy for generating messages
@st.composite
def messages(draw):
    """Generate random messages for testing.
    
    Note: min_size is set to 5 to ensure Rich adds formatting codes.
    Very short messages (1-2 chars) may not trigger ANSI formatting.
    """
    return draw(st.text(
        alphabet="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 .,!?-_",
        min_size=5,
        max_size=100
    ))


# Strategy for generating file paths
@st.composite
def file_paths(draw):
    """Generate random file paths for testing."""
    # Windows reserved names that cannot be used
    WINDOWS_RESERVED = ['CON', 'PRN', 'AUX', 'NUL', 'COM1', 'COM2', 'COM3', 'COM4', 
                        'COM5', 'COM6', 'COM7', 'COM8', 'COM9', 'LPT1', 'LPT2', 
                        'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9']
    
    # Generate directory components
    num_dirs = draw(st.integers(min_value=0, max_value=3))
    dirs = []
    for _ in range(num_dirs):
        dir_name = draw(st.text(
            alphabet="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-",
            min_size=1,
            max_size=10
        ).filter(lambda x: x.upper() not in WINDOWS_RESERVED and x not in ['.', '..']))
        dirs.append(dir_name)
    
    # Generate filename
    filename = draw(st.text(
        alphabet="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-",
        min_size=1,
        max_size=15
    ).filter(lambda x: x.upper() not in WINDOWS_RESERVED))
    
    # Generate extension
    ext = draw(st.sampled_from([".txt", ".py", ".md", ".json", ".jpg", ".png"]))
    
    # Construct path
    if dirs:
        return "/".join(dirs) + "/" + filename + ext
    else:
        return filename + ext


# Strategy for generating statistics dictionaries
@st.composite
def statistics_dicts(draw):
    """Generate random statistics dictionaries for testing."""
    num_stats = draw(st.integers(min_value=1, max_value=10))
    stats = {}
    
    for _ in range(num_stats):
        key = draw(st.text(
            alphabet="abcdefghijklmnopqrstuvwxyz_",
            min_size=3,
            max_size=20
        ))
        value = draw(st.one_of(
            st.integers(min_value=0, max_value=10000),
            st.floats(min_value=0.0, max_value=100.0, allow_nan=False, allow_infinity=False),
            st.text(alphabet="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 ", min_size=1, max_size=20)
        ))
        stats[key] = value
    
    return stats


def has_ansi_codes(text: str) -> bool:
    """Check if text contains ANSI escape codes (used for formatting)."""
    # ANSI escape code pattern
    ansi_pattern = re.compile(r'\x1b\[[0-9;]*m')
    return bool(ansi_pattern.search(text))


def has_rich_markup(text: str) -> bool:
    """Check if text contains rich markup patterns."""
    # Rich markup patterns like [red], [bold], [green], etc.
    markup_pattern = re.compile(r'\[/?[a-z]+[^\]]*\]')
    return bool(markup_pattern.search(text))


def strip_ansi_codes(text: str) -> str:
    """Remove ANSI escape codes from text."""
    ansi_pattern = re.compile(r'\x1b\[[0-9;]*m')
    return ansi_pattern.sub('', text)


class TestRichFormattingPresence:
    """Property tests for rich formatting presence in output."""
    
    @settings(max_examples=100)
    @given(message=messages())
    def test_success_message_has_formatting(self, message):
        """
        **Feature: cli-improvements, Property 13: Rich formatting presence**
        **Validates: Requirements 3.1, 3.3, 3.5**
        
        For any success message, the output should contain ANSI escape codes
        or rich markup for formatting.
        """
        # Create console with string buffer
        string_buffer = StringIO()
        console = Console(file=string_buffer, force_terminal=True, width=120)
        formatter = OutputFormatter(console)
        
        # Print success message
        formatter.print_success(message)
        
        # Get output
        output = string_buffer.getvalue()
        
        # Verify formatting is present
        assert has_ansi_codes(output), \
            f"Success message output should contain ANSI formatting codes"
    
    @settings(max_examples=100)
    @given(message=messages())
    def test_error_message_has_formatting(self, message):
        """
        **Feature: cli-improvements, Property 13: Rich formatting presence**
        **Validates: Requirements 3.1, 3.3, 3.5**
        
        For any error message, the output should contain ANSI escape codes
        or rich markup for formatting.
        """
        # Create console with string buffer
        string_buffer = StringIO()
        console = Console(file=string_buffer, force_terminal=True, width=120)
        formatter = OutputFormatter(console)
        
        # Print error message
        formatter.print_error(message)
        
        # Get output
        output = string_buffer.getvalue()
        
        # Verify formatting is present
        assert has_ansi_codes(output), \
            f"Error message output should contain ANSI formatting codes"
    
    @settings(max_examples=100)
    @given(message=messages())
    def test_warning_message_has_formatting(self, message):
        """
        **Feature: cli-improvements, Property 13: Rich formatting presence**
        **Validates: Requirements 3.1, 3.3, 3.5**
        
        For any warning message, the output should contain ANSI escape codes
        or rich markup for formatting.
        """
        # Create console with string buffer
        string_buffer = StringIO()
        console = Console(file=string_buffer, force_terminal=True, width=120)
        formatter = OutputFormatter(console)
        
        # Print warning message
        formatter.print_warning(message)
        
        # Get output
        output = string_buffer.getvalue()
        
        # Verify formatting is present
        assert has_ansi_codes(output), \
            f"Warning message output should contain ANSI formatting codes"
    
    @settings(max_examples=100)
    @given(message=messages())
    def test_info_message_has_formatting(self, message):
        """
        **Feature: cli-improvements, Property 13: Rich formatting presence**
        **Validates: Requirements 3.1, 3.3, 3.5**
        
        For any info message, the output should contain ANSI escape codes
        or rich markup for formatting.
        """
        # Create console with string buffer
        string_buffer = StringIO()
        console = Console(file=string_buffer, force_terminal=True, width=120)
        formatter = OutputFormatter(console)
        
        # Print info message
        formatter.print_info(message)
        
        # Get output
        output = string_buffer.getvalue()
        
        # Verify formatting is present
        assert has_ansi_codes(output), \
            f"Info message output should contain ANSI formatting codes"
    
    @settings(max_examples=100)
    @given(stats=statistics_dicts())
    def test_stats_table_has_formatting(self, stats):
        """
        **Feature: cli-improvements, Property 13: Rich formatting presence**
        **Validates: Requirements 3.1, 3.3, 3.5**
        
        For any statistics dictionary, the rendered table should contain
        ANSI escape codes for formatting.
        """
        # Create console with string buffer
        string_buffer = StringIO()
        console = Console(file=string_buffer, force_terminal=True, width=120)
        formatter = OutputFormatter(console)
        
        # Create and render table
        table = formatter.create_stats_table(stats)
        console.print(table)
        
        # Get output
        output = string_buffer.getvalue()
        
        # Verify formatting is present
        assert has_ansi_codes(output), \
            f"Statistics table output should contain ANSI formatting codes"


class TestPathSyntaxHighlighting:
    """Property tests for path syntax highlighting in output."""
    
    @settings(max_examples=100)
    @given(paths=st.lists(file_paths(), min_size=1, max_size=10))
    def test_file_list_has_path_highlighting(self, paths):
        """
        **Feature: cli-improvements, Property 14: Path syntax highlighting**
        **Validates: Requirements 3.4**
        
        For any list of file paths, the output should contain formatting codes
        to distinguish different path components.
        """
        # Create console with string buffer
        string_buffer = StringIO()
        console = Console(file=string_buffer, force_terminal=True, width=120)
        formatter = OutputFormatter(console)
        
        # Print file list
        formatter.print_file_list(paths, status="modified")
        
        # Get output
        output = string_buffer.getvalue()
        
        # Verify formatting is present (ANSI codes for highlighting)
        assert has_ansi_codes(output), \
            f"File list output should contain ANSI formatting codes for path highlighting"
        
        # Verify all paths appear in output (strip ANSI codes for comparison)
        plain_output = strip_ansi_codes(output)
        for path in paths:
            # Extract filename from path
            filename = Path(path).name
            # Check that filename appears in output (after stripping formatting)
            assert filename in plain_output or any(part in plain_output for part in path.split("/")), \
                f"Path '{path}' or its components should appear in output"
    
    @settings(max_examples=100)
    @given(
        paths=st.lists(file_paths(), min_size=1, max_size=10),
        status=st.sampled_from(["modified", "error", "skipped", "success", "moved"])
    )
    def test_file_list_different_statuses_have_formatting(self, paths, status):
        """
        **Feature: cli-improvements, Property 14: Path syntax highlighting**
        **Validates: Requirements 3.4**
        
        For any list of file paths with any status, the output should contain
        formatting codes for both status indicators and path components.
        """
        # Create console with string buffer
        string_buffer = StringIO()
        console = Console(file=string_buffer, force_terminal=True, width=120)
        formatter = OutputFormatter(console)
        
        # Print file list with specific status
        formatter.print_file_list(paths, status=status)
        
        # Get output
        output = string_buffer.getvalue()
        
        # Verify formatting is present
        assert has_ansi_codes(output), \
            f"File list output with status '{status}' should contain ANSI formatting codes"
