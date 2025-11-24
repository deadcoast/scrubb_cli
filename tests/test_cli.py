"""Tests for CLI folder command functionality."""

import tempfile
import os
from pathlib import Path
from hypothesis import given, strategies as st, settings
from typer.testing import CliRunner
from unittest.mock import patch, MagicMock

from scrubb.cli import app
from scrubb.file_classifier import FileClassifier
from scrubb.folder_organizer import FolderOrganizer


runner = CliRunner()


@settings(max_examples=100)
@given(
    path_type=st.sampled_from(['absolute', 'relative', 'tilde']),
    subdir_name=st.text(min_size=1, max_size=10, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'))).filter(
        lambda x: x.upper() not in ['CON', 'PRN', 'AUX', 'NUL', 'COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9', 'LPT1', 'LPT2', 'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9']
    )
)
def test_path_resolution_consistency(path_type, subdir_name):
    """
    **Feature: folder-cleanup, Property 2: Path resolution consistency**
    **Validates: Requirements 2.1, 2.3**
    
    For any valid directory path (absolute or relative), the system should
    correctly resolve and use that path as the root directory for all operations.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        
        # Create a subdirectory to test with
        test_dir = root / subdir_name
        test_dir.mkdir()
        
        # Create a test file in the directory
        test_file = test_dir / "test.txt"
        test_file.touch()
        
        # Generate path based on type
        if path_type == 'absolute':
            path_input = str(test_dir.resolve())
        elif path_type == 'relative':
            # Change to parent directory and use relative path
            original_cwd = os.getcwd()
            os.chdir(root)
            path_input = subdir_name
        else:  # tilde
            # For tilde expansion, we'll use a path under home
            home = Path.home()
            tilde_test_dir = home / f"test_scrubb_{subdir_name}"
            tilde_test_dir.mkdir(exist_ok=True)
            tilde_test_file = tilde_test_dir / "test.txt"
            tilde_test_file.touch()
            path_input = f"~/{tilde_test_dir.relative_to(home)}"
            test_dir = tilde_test_dir
        
        try:
            # Create classifier and organizer
            classifier = FileClassifier()
            organizer = FolderOrganizer(test_dir, classifier)
            
            # Execute organization
            stats = organizer.organize()
            
            # Verify operations occurred within the correctly resolved path
            # The Scrubbed folder should be created in the resolved path
            scrubbed_path = test_dir / "Scrubbed"
            assert scrubbed_path.exists(), f"Scrubbed folder not created in resolved path: {test_dir}"
            
            # Verify file was moved (it should be in Docs/Other Docs)
            docs_dir = scrubbed_path / "Docs" / "Other Docs"
            assert docs_dir.exists(), "Category directory not created in resolved path"
            
            # Verify at least one file was moved
            assert stats.files_moved >= 1, "File was not moved in resolved path"
            
        finally:
            # Restore original working directory if changed
            if path_type == 'relative':
                os.chdir(original_cwd)
            # Clean up tilde test directory
            if path_type == 'tilde':
                import shutil
                if tilde_test_dir.exists():
                    shutil.rmtree(tilde_test_dir)


def test_folder_command_with_valid_path():
    """Test folder command with a valid directory path."""
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        
        # Create test files
        (root / "test1.txt").touch()
        (root / "test2.jpg").touch()
        
        # Mock the prompt to return our test directory
        with patch('typer.prompt', return_value=str(root)):
            result = runner.invoke(app, ['folder'])
            
            # Check command succeeded
            assert result.exit_code == 0
            
            # Check output contains expected messages
            assert "Organizing files in:" in result.stdout
            assert "Folder cleanup complete!" in result.stdout
            assert "Files moved:" in result.stdout


def test_folder_command_with_nonexistent_path():
    """Test folder command with a non-existent directory path."""
    nonexistent_path = "/this/path/does/not/exist/at/all"
    
    # Mock the prompt to return a non-existent path
    with patch('typer.prompt', return_value=nonexistent_path):
        result = runner.invoke(app, ['folder'])
        
        # Check command failed with appropriate exit code
        assert result.exit_code == 1
        
        # Check error message is displayed (could be in stdout or stderr)
        output = result.stdout + result.stderr
        assert "Error: Path does not exist:" in output


def test_folder_command_with_file_path():
    """Test folder command with a file path instead of directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        
        # Create a file (not a directory)
        test_file = root / "test.txt"
        test_file.touch()
        
        # Mock the prompt to return the file path
        with patch('typer.prompt', return_value=str(test_file)):
            result = runner.invoke(app, ['folder'])
            
            # Check command failed
            assert result.exit_code == 1
            
            # Check error message (could be in stdout or stderr)
            output = result.stdout + result.stderr
            assert "Error: Path is not a directory:" in output


def test_folder_command_statistics_display():
    """Test that statistics are properly displayed after organization."""
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        
        # Create files of different types
        (root / "image.jpg").touch()
        (root / "video.mp4").touch()
        (root / "doc.pdf").touch()
        (root / "code.py").touch()
        
        # Mock the prompt
        with patch('typer.prompt', return_value=str(root)):
            result = runner.invoke(app, ['folder'])
            
            # Check statistics are displayed
            assert "Files moved:" in result.stdout
            assert "Files moved by category:" in result.stdout
            assert "Empty folders removed:" in result.stdout
            
            # Check that categories are mentioned
            assert "Images:" in result.stdout or "Video:" in result.stdout


def test_folder_command_error_display():
    """Test that errors are properly displayed when they occur."""
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        
        # Create a test file
        test_file = root / "test.txt"
        test_file.touch()
        
        # Mock shutil.move to raise an error
        with patch('typer.prompt', return_value=str(root)):
            with patch('shutil.move', side_effect=PermissionError("Permission denied")):
                result = runner.invoke(app, ['folder'])
                
                # Check that errors are reported
                assert "Errors encountered:" in result.stdout
                assert "Error files:" in result.stdout


def test_folder_mode_exclusivity():
    """Test that folder mode doesn't trigger emoji scrubbing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        
        # Create a file without emojis (to avoid encoding issues on Windows)
        test_file = root / "test.txt"
        test_file.write_text("Hello World")
        
        # Run folder command
        with patch('typer.prompt', return_value=str(root)):
            result = runner.invoke(app, ['folder'])
            
            # Check that emoji scrubbing output is NOT present
            assert "emojis_removed" not in result.stdout
            
            # Check that folder cleanup output IS present
            assert "Folder cleanup complete!" in result.stdout


def test_folder_command_dry_flag_recognized():
    """
    Test that --dry flag is recognized and activates dry-run mode.
    Requirements: 1.1, 7.1
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        
        # Create test files
        (root / "test1.txt").touch()
        (root / "test2.jpg").touch()
        
        # Mock the prompt to return our test directory
        with patch('typer.prompt', return_value=str(root)):
            result = runner.invoke(app, ['folder', '--dry'])
            
            # Check command succeeded
            assert result.exit_code == 0
            
            # Check that dry-run mode header is displayed
            assert "DRY RUN MODE" in result.stdout or "dry run" in result.stdout.lower()


def test_folder_command_dry_flag_displays_header():
    """
    Test that dry-run header is displayed when --dry flag is used.
    Requirements: 1.1, 7.1
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        
        # Create a test file
        (root / "test.txt").touch()
        
        # Mock the prompt to return our test directory
        with patch('typer.prompt', return_value=str(root)):
            result = runner.invoke(app, ['folder', '--dry'])
            
            # Check that prominent dry-run mode header is displayed
            assert "DRY RUN MODE" in result.stdout
            assert "No changes will be made" in result.stdout


def test_dry_run_output_displayed_correctly():
    """
    Test that dry-run output is displayed correctly using DryRunFormatter.
    Requirements: 7.1, 7.2
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        
        # Create test files of different types
        (root / "image.jpg").touch()
        (root / "video.mp4").touch()
        (root / "doc.pdf").touch()
        (root / "unknown.xyz").touch()
        
        # Mock the prompt to return our test directory
        with patch('typer.prompt', return_value=str(root)):
            result = runner.invoke(app, ['folder', '--dry'])
            
            # Check command succeeded
            assert result.exit_code == 0
            
            # Check that formatted output sections are present
            assert "DRY RUN PREVIEW" in result.stdout
            assert "SUMMARY" in result.stdout
            assert "FILES BY CATEGORY" in result.stdout
            assert "DIRECTORIES TO CREATE" in result.stdout
            assert "FILE OPERATIONS" in result.stdout
            
            # Check that files are listed
            assert "Files to move:" in result.stdout
            
            # Check that skipped files section appears (for unknown.xyz)
            assert "SKIPPED FILES" in result.stdout
            
            # Check footer reminder
            assert "This was a DRY RUN" in result.stdout
            assert "No files were moved or modified" in result.stdout


def test_dry_run_completion_message_shown():
    """
    Test that completion message is shown after dry-run.
    Requirements: 7.1, 7.2
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        
        # Create a test file
        (root / "test.txt").touch()
        
        # Mock the prompt to return our test directory
        with patch('typer.prompt', return_value=str(root)):
            result = runner.invoke(app, ['folder', '--dry'])
            
            # Check that completion message reminds user no changes were made
            assert "No files were moved or modified" in result.stdout
            assert "Run without --dry flag to execute these changes" in result.stdout


def test_regular_mode_not_affected_by_dry_run():
    """
    Test that regular mode output is not affected by dry-run changes.
    Requirements: 7.1, 7.2
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        
        # Create test files
        (root / "test1.txt").touch()
        (root / "test2.jpg").touch()
        
        # Run in regular mode (without --dry)
        with patch('typer.prompt', return_value=str(root)):
            result = runner.invoke(app, ['folder'])
            
            # Check command succeeded
            assert result.exit_code == 0
            
            # Check that regular mode output is present
            assert "Folder cleanup complete!" in result.stdout
            assert "Files moved:" in result.stdout
            
            # Check that dry-run specific output is NOT present
            assert "DRY RUN PREVIEW" not in result.stdout
            assert "This was a DRY RUN" not in result.stdout
            assert "No files were moved or modified" not in result.stdout


def test_dry_run_shows_all_sections():
    """
    Test that dry-run output includes all required sections.
    Requirements: 7.2, 7.3
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        
        # Create files that will trigger various sections
        (root / "image1.jpg").touch()
        (root / "image2.jpg").touch()  # Will create conflict if same name
        (root / "video.mp4").touch()
        (root / "unknown.xyz").touch()  # Will be skipped
        
        # Create a subdirectory with a file (will become empty)
        subdir = root / "subdir"
        subdir.mkdir()
        (subdir / "doc.pdf").touch()
        
        # Mock the prompt to return our test directory
        with patch('typer.prompt', return_value=str(root)):
            result = runner.invoke(app, ['folder', '--dry'])
            
            # Check all major sections are present
            assert "SUMMARY" in result.stdout
            assert "FILES BY CATEGORY" in result.stdout
            assert "DIRECTORIES TO CREATE" in result.stdout
            assert "FILE OPERATIONS" in result.stdout
            assert "SKIPPED FILES" in result.stdout
            assert "EMPTY DIRECTORIES TO REMOVE" in result.stdout
            
            # Check that potential errors section is present (even if no errors)
            assert "POTENTIAL ERRORS" in result.stdout or "No potential errors detected" in result.stdout


def test_folder_command_tree_flag_recognized():
    """
    Test that --tree flag is recognized and doesn't cause errors.
    Requirements: 1.1, 1.5
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        
        # Create test files
        (root / "test1.txt").touch()
        (root / "test2.jpg").touch()
        
        # Mock the prompt to return our test directory
        with patch('typer.prompt', return_value=str(root)):
            result = runner.invoke(app, ['folder', '--tree'])
            
            # Check command succeeded
            assert result.exit_code == 0
            
            # Check that tree visualization sections are present
            assert "BEFORE" in result.stdout or "AFTER" in result.stdout
            
            # Check that standard output is still present
            assert "Organizing files in:" in result.stdout
            assert "Folder cleanup complete!" in result.stdout


def test_folder_command_tree_and_dry_flags_together():
    """
    Test that --tree and --dry flags work together.
    Requirements: 1.2, 7.1, 7.5
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        
        # Create test files
        (root / "test1.txt").touch()
        (root / "test2.jpg").touch()
        
        # Mock the prompt to return our test directory
        with patch('typer.prompt', return_value=str(root)):
            result = runner.invoke(app, ['folder', '--tree', '--dry'])
            
            # Check command succeeded
            assert result.exit_code == 0
            
            # Check that dry-run mode header is displayed
            assert "DRY RUN MODE" in result.stdout
            
            # Check that tree visualization is present
            assert "BEFORE" in result.stdout or "AFTER" in result.stdout
            
            # Check that simulation indicator is present
            assert "Simulated" in result.stdout or "SIMULATED" in result.stdout or "DRY RUN" in result.stdout
            
            # Check that standard dry-run output is still present
            assert "DRY RUN PREVIEW" in result.stdout
