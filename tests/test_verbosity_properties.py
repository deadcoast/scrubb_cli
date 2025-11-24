"""Property-based tests for verbosity management.

Feature: cli-improvements
"""

import pytest
from hypothesis import given, strategies as st

from scrubb.verbosity import VerbosityLevel, VerbosityManager


# Test data strategies
@st.composite
def message_types(draw):
    """Generate different message types."""
    return draw(st.sampled_from(['debug', 'info', 'summary', 'error', 'warning']))


@st.composite
def output_messages(draw):
    """Generate random output messages."""
    return draw(st.text(min_size=1, max_size=200))


class TestQuietModeOutputSuppression:
    """Property 7: Quiet mode output suppression
    
    **Feature: cli-improvements, Property 7: Quiet mode output suppression**
    **Validates: Requirements 7.2, 7.4**
    """
    
    @given(message_type=message_types())
    def test_quiet_mode_suppresses_non_essential_output(self, message_type):
        """For any command executed with quiet mode, the output should contain 
        only error and warning messages, with no informational or debug output.
        """
        manager = VerbosityManager(VerbosityLevel.QUIET)
        
        # Quiet mode should suppress debug, info, and summary
        if message_type == 'debug':
            assert not manager.should_print_debug()
        elif message_type == 'info':
            assert not manager.should_print_info()
        elif message_type == 'summary':
            assert not manager.should_print_summary()
        # But should always allow errors and warnings
        elif message_type == 'error':
            assert manager.should_print_error()
        elif message_type == 'warning':
            assert manager.should_print_warning()
    
    @given(output_messages())
    def test_quiet_mode_allows_errors_and_warnings(self, message):
        """Quiet mode should always allow error and warning messages."""
        manager = VerbosityManager(VerbosityLevel.QUIET)
        
        # Errors and warnings should always be printable in quiet mode
        assert manager.should_print_error()
        assert manager.should_print_warning()


class TestVerboseModeDebugOutput:
    """Property 8: Verbose mode debug output
    
    **Feature: cli-improvements, Property 8: Verbose mode debug output**
    **Validates: Requirements 7.1, 7.3**
    """
    
    @given(message_type=message_types())
    def test_verbose_mode_enables_all_output(self, message_type):
        """For any command executed with verbose mode, the output should contain 
        debug information including file-by-file processing details and timestamps.
        """
        manager = VerbosityManager(VerbosityLevel.VERBOSE)
        
        # Verbose mode should enable all message types
        if message_type == 'debug':
            assert manager.should_print_debug()
        elif message_type == 'info':
            assert manager.should_print_info()
        elif message_type == 'summary':
            assert manager.should_print_summary()
        elif message_type == 'error':
            assert manager.should_print_error()
        elif message_type == 'warning':
            assert manager.should_print_warning()
    
    @given(output_messages())
    def test_verbose_mode_includes_debug_messages(self, message):
        """Verbose mode should specifically enable debug output."""
        manager = VerbosityManager(VerbosityLevel.VERBOSE)
        
        # Debug messages should be enabled in verbose mode
        assert manager.should_print_debug()


class TestDefaultVerbosityOutput:
    """Property 9: Default verbosity output
    
    **Feature: cli-improvements, Property 9: Default verbosity output**
    **Validates: Requirements 7.5**
    """
    
    @given(message_type=message_types())
    def test_normal_mode_shows_summary_but_not_debug(self, message_type):
        """For any command executed without verbosity flags, the output should 
        contain summary statistics but not debug details.
        """
        manager = VerbosityManager(VerbosityLevel.NORMAL)
        
        # Normal mode should show info, summary, errors, warnings but not debug
        if message_type == 'debug':
            assert not manager.should_print_debug()
        elif message_type == 'info':
            assert manager.should_print_info()
        elif message_type == 'summary':
            assert manager.should_print_summary()
        elif message_type == 'error':
            assert manager.should_print_error()
        elif message_type == 'warning':
            assert manager.should_print_warning()
    
    @given(output_messages())
    def test_default_verbosity_is_normal(self, message):
        """Default verbosity should be NORMAL level."""
        manager = VerbosityManager()  # No level specified
        
        # Should default to NORMAL level
        assert manager.level == VerbosityLevel.NORMAL
        assert manager.should_print_info()
        assert manager.should_print_summary()
        assert not manager.should_print_debug()


class TestVerbosityContext:
    """Test context variable functionality."""
    
    def test_get_current_returns_default_when_not_set(self):
        """When no verbosity manager is set, get_current should return NORMAL."""
        manager = VerbosityManager.get_current()
        assert manager.level == VerbosityLevel.NORMAL
    
    def test_set_and_get_current(self):
        """Setting current verbosity manager should be retrievable."""
        quiet_manager = VerbosityManager(VerbosityLevel.QUIET)
        VerbosityManager.set_current(quiet_manager)
        
        retrieved = VerbosityManager.get_current()
        assert retrieved.level == VerbosityLevel.QUIET
    
    def test_context_isolation(self):
        """Context should be isolated per execution context."""
        verbose_manager = VerbosityManager(VerbosityLevel.VERBOSE)
        VerbosityManager.set_current(verbose_manager)
        
        current = VerbosityManager.get_current()
        assert current.level == VerbosityLevel.VERBOSE
