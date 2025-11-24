"""Property-based tests for prompt utilities."""

from __future__ import annotations
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from hypothesis import given, strategies as st, settings
from scrubb.prompt_utils import PromptUtils


# Property 17: Path validation in prompts
# **Feature: cli-improvements, Property 17: Path validation in prompts**
@given(
    invalid_path=st.one_of(
        # Non-existent paths - use paths that are very unlikely to exist
        st.text(min_size=10, alphabet=st.characters(blacklist_categories=('Cs',))).map(
            lambda x: f"/nonexistent_{x.replace('/', '_').replace('\\', '_')}_path"
        ).filter(lambda x: not Path(x).exists()),
        # Generate random file paths that don't exist
        st.text(min_size=5, max_size=20, alphabet='abcdefghijklmnopqrstuvwxyz0123456789').map(
            lambda x: f"/tmp/nonexistent_file_{x}.txt"
        ).filter(lambda x: not Path(x).exists())
    )
)
@settings(max_examples=100, deadline=1000)
def test_path_validation_rejects_invalid_paths(invalid_path):
    """
    Property 17: Path validation in prompts
    
    For any directory path provided to a prompt, if the path doesn't exist 
    or isn't a directory, the system should reject it and re-prompt.
    
    Validates: Requirements 5.1
    """
    import tempfile
    
    # Create a valid directory for the second attempt
    with tempfile.TemporaryDirectory() as tmpdir:
        valid_dir = Path(tmpdir)
        
        # Mock Prompt.ask to return invalid path first, then valid path
        with patch('scrubb.prompt_utils.Prompt.ask') as mock_ask:
            # First call returns invalid path
            # Second call (error acknowledgment) returns empty string
            # Third call returns valid path
            mock_ask.side_effect = [invalid_path, "", str(valid_dir)]
            
            result = PromptUtils.prompt_directory("Enter path")
            
            # Should have been called at least twice (invalid attempt + retry)
            assert mock_ask.call_count >= 2
            # Should return the valid directory
            assert result == valid_dir


# Property 11: Confirmation prompt acceptance
# **Feature: cli-improvements, Property 11: Confirmation prompt acceptance**
@given(
    affirmative=st.sampled_from(['yes', 'y', 'Y', 'YES', 'Yes'])
)
@settings(max_examples=100, deadline=1000)
def test_confirmation_prompt_accepts_affirmative_responses(affirmative):
    """
    Property 11: Confirmation prompt acceptance
    
    For any confirmation prompt, providing any of ('yes', 'y', 'Y', 'YES', or Enter) 
    should proceed with the operation.
    
    Validates: Requirements 5.3, 8.3
    """
    # Mock Confirm.ask to simulate user input
    with patch('scrubb.prompt_utils.Confirm.ask') as mock_confirm:
        # Confirm.ask returns True for affirmative responses
        mock_confirm.return_value = True
        
        result = PromptUtils.prompt_confirmation("Proceed?")
        
        # Should return True for affirmative response
        assert result is True
        # Should have been called once
        assert mock_confirm.call_count == 1


# Property 12: Confirmation prompt rejection
# **Feature: cli-improvements, Property 12: Confirmation prompt rejection**
@given(
    negative=st.sampled_from(['no', 'n', 'N', 'NO', 'No'])
)
@settings(max_examples=100, deadline=1000)
def test_confirmation_prompt_rejects_negative_responses(negative):
    """
    Property 12: Confirmation prompt rejection
    
    For any confirmation prompt, providing a negative response ('no', 'n', 'N', 'NO') 
    should cancel the operation and exit gracefully.
    
    Validates: Requirements 8.4
    """
    # Mock Confirm.ask to simulate user input
    with patch('scrubb.prompt_utils.Confirm.ask') as mock_confirm:
        # Confirm.ask returns False for negative responses
        mock_confirm.return_value = False
        
        result = PromptUtils.prompt_confirmation("Proceed?")
        
        # Should return False for negative response
        assert result is False
        # Should have been called once
        assert mock_confirm.call_count == 1


# Additional test for keyboard interrupt handling
def test_prompt_directory_handles_keyboard_interrupt():
    """Test that keyboard interrupts are properly propagated."""
    with patch('scrubb.prompt_utils.Prompt.ask') as mock_ask:
        mock_ask.side_effect = KeyboardInterrupt()
        
        with pytest.raises(KeyboardInterrupt):
            PromptUtils.prompt_directory("Enter path")


def test_prompt_confirmation_handles_keyboard_interrupt():
    """Test that keyboard interrupts are properly propagated."""
    with patch('scrubb.prompt_utils.Confirm.ask') as mock_confirm:
        mock_confirm.side_effect = KeyboardInterrupt()
        
        with pytest.raises(KeyboardInterrupt):
            PromptUtils.prompt_confirmation("Proceed?")


def test_prompt_choice_handles_keyboard_interrupt():
    """Test that keyboard interrupts are properly propagated."""
    with patch('scrubb.prompt_utils.Prompt.ask') as mock_ask:
        mock_ask.side_effect = KeyboardInterrupt()
        
        with pytest.raises(KeyboardInterrupt):
            PromptUtils.prompt_choice("Select option", ["Option 1", "Option 2"])


def test_prompt_choice_validates_empty_choices():
    """Test that empty choices list raises ValueError."""
    with pytest.raises(ValueError, match="Choices list cannot be empty"):
        PromptUtils.prompt_choice("Select option", [])
