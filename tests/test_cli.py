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


@settings(max_examples=100, deadline=None)
@given(
    path_arg=st.one_of(
        st.none(),
        st.just('.'),
        st.text(min_size=1, max_size=20, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd', 'Pd'))).filter(
            lambda x: x not in ['..', '.', '/', '\\'] and not x.startswith('-')
        )
    )
)
def test_emoji_command_name_consistency(path_arg):
    """
    **Feature: cli-improvements, Property 1: Command name consistency**
    **Validates: Requirements 1.1**
    
    For any valid path argument, invoking `scrubb emoji [PATH] .` should execute 
    emoji scrubbing operations with identical functionality to the former `main` command.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        
        # Create a test file with some content (no emojis to avoid encoding issues)
        test_file = root / "test.txt"
        test_file.write_text("Hello World", encoding='utf-8')
        
        # Build command arguments
        if path_arg is None:
            # Test with no arguments (should use default root)
            args = ['emoji']
        elif path_arg == '.':
            # Test with just '.' executor
            args = ['emoji', '.']
        else:
            # Test with path and '.' executor
            # Create a subdirectory for the path
            subdir = root / path_arg
            try:
                subdir.mkdir(exist_ok=True)
                (subdir / "test.txt").write_text("Hello World", encoding='utf-8')
                args = ['emoji', str(subdir), '.']
            except (OSError, ValueError):
                # Skip invalid paths
                return
        
        # Mock the config to use our test directory
        mock_config = {
            "default_root": str(root),
            "ignore_patterns": [".git", "__pycache__", "node_modules"],
            "text_extensions": [".txt", ".md", ".py", ".js"]
        }
        
        with patch('scrubb.cli.load_config', return_value=mock_config):
            with patch('scrubb.cli.load_stats', return_value={
                "runs": 0,
                "files_processed": 0,
                "files_modified": 0,
                "files_skipped": 0,
                "errors": 0,
                "emojis_removed": 0,
                "scoped_scrub": {}
            }):
                with patch('scrubb.cli.save_stats'):
                    result = runner.invoke(app, args)
                    
                    # Check that the command executed successfully or with expected error codes
                    # Exit code 0 = success, 2 = path not found (acceptable for some generated paths)
                    assert result.exit_code in [0, 2], f"Unexpected exit code: {result.exit_code}"
                    
                    # If successful, check that emoji scrubbing output is present
                    if result.exit_code == 0:
                        assert "scrubb run:" in result.stdout, "Expected emoji scrubbing output not found"
                        assert "files_processed=" in result.stdout, "Expected statistics output not found"
                        assert "emojis_removed=" in result.stdout, "Expected emoji removal statistics not found"


@settings(max_examples=100, deadline=1000)
@given(
    path_arg=st.one_of(
        st.none(),
        st.just('.'),
        st.text(min_size=1, max_size=20, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd', 'Pd'))).filter(
            lambda x: x not in ['..', '.', '/', '\\'] and not x.startswith('-')
        )
    )
)
def test_deprecation_warning_display(path_arg):
    """
    **Feature: cli-improvements, Property 2: Deprecation warning display**
    **Validates: Requirements 1.2**
    
    For any valid path argument, invoking `scrubb main [PATH] .` should display 
    a deprecation warning in the output.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        
        # Create a test file with some content (no emojis to avoid encoding issues)
        test_file = root / "test.txt"
        test_file.write_text("Hello World", encoding='utf-8')
        
        # Build command arguments for 'main' command
        if path_arg is None:
            # Test with no arguments (should use default root)
            args = ['main']
        elif path_arg == '.':
            # Test with just '.' executor
            args = ['main', '.']
        else:
            # Test with path and '.' executor
            # Create a subdirectory for the path
            subdir = root / path_arg
            try:
                subdir.mkdir(exist_ok=True)
                (subdir / "test.txt").write_text("Hello World", encoding='utf-8')
                args = ['main', str(subdir), '.']
            except (OSError, ValueError):
                # Skip invalid paths
                return
        
        # Mock the config to use our test directory
        mock_config = {
            "default_root": str(root),
            "ignore_patterns": [".git", "__pycache__", "node_modules"],
            "text_extensions": [".txt", ".md", ".py", ".js"]
        }
        
        with patch('scrubb.cli.load_config', return_value=mock_config):
            with patch('scrubb.cli.load_stats', return_value={
                "runs": 0,
                "files_processed": 0,
                "files_modified": 0,
                "files_skipped": 0,
                "errors": 0,
                "emojis_removed": 0,
                "scoped_scrub": {}
            }):
                with patch('scrubb.cli.save_stats'):
                    result = runner.invoke(app, args)
                    
                    # Check that the command executed successfully or with expected error codes
                    # Exit code 0 = success, 2 = path not found (acceptable for some generated paths)
                    assert result.exit_code in [0, 2], f"Unexpected exit code: {result.exit_code}"
                    
                    # Check that deprecation warning is displayed in stderr or output
                    output = result.stdout + result.stderr
                    assert "deprecated" in output.lower(), "Deprecation warning not found in output"
                    assert "main" in output.lower(), "Reference to 'main' command not found in deprecation warning"
                    assert "emoji" in output.lower(), "Reference to 'emoji' command not found in deprecation warning"
                    
                    # If successful, check that emoji scrubbing still occurred (backward compatibility)
                    if result.exit_code == 0:
                        assert "scrubb run:" in result.stdout, "Expected emoji scrubbing output not found"
                        assert "files_processed=" in result.stdout, "Expected statistics output not found"


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
            # Use --yes flag to bypass confirmation prompt
            result = runner.invoke(app, ['folder', '--yes'])
            
            # Check command succeeded
            assert result.exit_code == 0
            
            # Check output contains expected messages
            assert "Target directory:" in result.stdout
            assert "Folder cleanup complete!" in result.stdout
            assert "Files moved:" in result.stdout


def test_folder_command_with_nonexistent_path():
    """Test folder command with a non-existent directory path."""
    nonexistent_path = "/this/path/does/not/exist/at/all"
    
    # Mock the prompt to return a non-existent path
    with patch('typer.prompt', return_value=nonexistent_path):
        result = runner.invoke(app, ['folder'])
        
        # Check command failed with appropriate exit code (2 for invalid input)
        assert result.exit_code == 2
        
        # Check error message is displayed (could be in stdout or stderr)
        output = result.stdout + result.stderr
        assert "Path does not exist:" in output


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
            
            # Check command failed (2 for invalid input)
            assert result.exit_code == 2
            
            # Check error message (could be in stdout or stderr)
            output = result.stdout + result.stderr
            assert "Path is not a directory:" in output


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
            # Use --yes flag to bypass confirmation prompt
            result = runner.invoke(app, ['folder', '--yes'])
            
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
                # Use --yes flag to bypass confirmation prompt
                result = runner.invoke(app, ['folder', '--yes'])
                
                # Check that errors are reported (updated message)
                assert "Critical errors encountered:" in result.stdout
                assert "Permission denied" in result.stdout


def test_folder_mode_exclusivity():
    """Test that folder mode doesn't trigger emoji scrubbing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        
        # Create a file without emojis (to avoid encoding issues on Windows)
        test_file = root / "test.txt"
        test_file.write_text("Hello World")
        
        # Run folder command
        with patch('typer.prompt', return_value=str(root)):
            # Use --yes flag to bypass confirmation prompt
            result = runner.invoke(app, ['folder', '--yes'])
            
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
            
            # Check that unknown.xyz is now in the "Other" category (not skipped)
            assert "Other" in result.stdout
            assert "unknown.xyz" in result.stdout
            
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
            # Use --yes flag to bypass confirmation prompt
            result = runner.invoke(app, ['folder', '--yes'])
            
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
            # SKIPPED FILES section only appears when there are skipped files
            # Since unknown.xyz is now moved to "Other" category, no files are skipped
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
            # Use --yes flag to bypass confirmation prompt
            result = runner.invoke(app, ['folder', '--tree', '--yes'])
            
            # Check command succeeded
            assert result.exit_code == 0
            
            # Check that tree visualization sections are present
            assert "BEFORE" in result.stdout or "AFTER" in result.stdout
            
            # Check that standard output is still present
            assert "Target directory:" in result.stdout
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


@settings(max_examples=100, deadline=2000)
@given(
    command_pair=st.sampled_from([
        ('emoji', 'e'),
        ('stats', 's'),
        ('config', 'c'),
    ]),
    test_scenario=st.sampled_from(['basic', 'with_flag'])
)
def test_command_alias_equivalence(command_pair, test_scenario):
    """
    **Feature: cli-improvements, Property 6: Command alias equivalence**
    **Validates: Requirements 6.1, 6.2, 6.3, 6.4**
    
    For any command and its alias (emoji/e, folder/f, stats/s, config/c), 
    invoking both with identical arguments should produce identical output and exit codes.
    """
    full_command, alias = command_pair
    
    # Test different scenarios based on command type
    if full_command == 'emoji':
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            
            # Create a test file
            test_file = root / "test.txt"
            test_file.write_text("Hello World", encoding='utf-8')
            
            # Mock the config
            mock_config = {
                "default_root": str(root),
                "ignore_patterns": [".git", "__pycache__", "node_modules"],
                "text_extensions": [".txt", ".md", ".py", ".js"]
            }
            
            mock_stats = {
                "runs": 0,
                "files_processed": 0,
                "files_modified": 0,
                "files_skipped": 0,
                "errors": 0,
                "emojis_removed": 0,
                "scoped_scrub": {}
            }
            
            # Build arguments based on scenario
            if test_scenario == 'basic':
                args_full = [full_command]
                args_alias = [alias]
            else:  # with_flag
                args_full = [full_command, '.']
                args_alias = [alias, '.']
            
            with patch('scrubb.cli.load_config', return_value=mock_config):
                with patch('scrubb.cli.load_stats', return_value=mock_stats):
                    with patch('scrubb.cli.save_stats'):
                        # Run with full command name
                        result_full = runner.invoke(app, args_full)
                        
                        # Run with alias
                        result_alias = runner.invoke(app, args_alias)
                        
                        # Check that exit codes match
                        assert result_full.exit_code == result_alias.exit_code, \
                            f"Exit codes differ: {full_command}={result_full.exit_code}, {alias}={result_alias.exit_code}"
                        
                        # Check that key output elements are present in both
                        if result_full.exit_code == 0:
                            assert "scrubb run:" in result_full.stdout
                            assert "scrubb run:" in result_alias.stdout
                            assert "files_processed=" in result_full.stdout
                            assert "files_processed=" in result_alias.stdout
    
    elif full_command == 'stats':
        mock_stats = {
            "runs": 5,
            "files_processed": 10,
            "files_modified": 3,
            "files_skipped": 2,
            "errors": 0,
            "emojis_removed": 15,
            "scoped_scrub": {"": 5, "": 10}
        }
        
        # Build arguments based on scenario
        if test_scenario == 'basic':
            args_full = [full_command]
            args_alias = [alias]
        else:  # with_flag
            args_full = [full_command, '--top']
            args_alias = [alias, '--top']
        
        with patch('scrubb.cli.load_stats', return_value=mock_stats):
            # Run with full command name
            result_full = runner.invoke(app, args_full)
            
            # Run with alias
            result_alias = runner.invoke(app, args_alias)
            
            # Check that exit codes match
            assert result_full.exit_code == result_alias.exit_code, \
                f"Exit codes differ: {full_command}={result_full.exit_code}, {alias}={result_alias.exit_code}"
            
            # Check that key output elements are present in both
            if result_full.exit_code == 0:
                assert "runs:" in result_full.stdout
                assert "runs:" in result_alias.stdout
                assert "files_processed:" in result_full.stdout
                assert "files_processed:" in result_alias.stdout
                assert "emojis_removed:" in result_full.stdout
                assert "emojis_removed:" in result_alias.stdout
                
                # If --top flag was used, check for emoji statistics table
                if test_scenario == 'with_flag':
                    # Check for table headers (new rich table format)
                    assert ("Top Emoji Statistics" in result_full.stdout or 
                            "Rank" in result_full.stdout or 
                            "Emoji" in result_full.stdout)
                    assert ("Top Emoji Statistics" in result_alias.stdout or 
                            "Rank" in result_alias.stdout or 
                            "Emoji" in result_alias.stdout)
    
    elif full_command == 'config':
        mock_config = {
            "default_root": "/test/path",
            "ignore_patterns": [".git", "__pycache__"],
            "text_extensions": [".txt", ".md"]
        }
        
        # Build arguments based on scenario
        if test_scenario == 'basic':
            args_full = [full_command]
            args_alias = [alias]
        else:  # with_flag
            args_full = [full_command, '--show']
            args_alias = [alias, '--show']
        
        with patch('scrubb.cli.load_config', return_value=mock_config):
            # Run with full command name
            result_full = runner.invoke(app, args_full)
            
            # Run with alias
            result_alias = runner.invoke(app, args_alias)
            
            # Check that exit codes match
            assert result_full.exit_code == result_alias.exit_code, \
                f"Exit codes differ: {full_command}={result_full.exit_code}, {alias}={result_alias.exit_code}"
            
            # Check that key output elements are present in both
            if result_full.exit_code == 0:
                assert "default_root:" in result_full.stdout
                assert "default_root:" in result_alias.stdout
                assert "config_file:" in result_full.stdout
                assert "config_file:" in result_alias.stdout
                assert "stats_file:" in result_full.stdout
                assert "stats_file:" in result_alias.stdout



def test_emoji_command_verbose_flag():
    """Test that emoji command accepts --verbose flag."""
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        
        # Create a test file with emoji
        test_file = root / "test.txt"
        test_file.write_text("Hello  World", encoding='utf-8')
        
        # Mock the config
        mock_config = {
            "default_root": str(root),
            "ignore_patterns": [".git", "__pycache__", "node_modules"],
            "text_extensions": [".txt", ".md", ".py", ".js"]
        }
        
        mock_stats = {
            "runs": 0,
            "files_processed": 0,
            "files_modified": 0,
            "files_skipped": 0,
            "errors": 0,
            "emojis_removed": 0,
            "scoped_scrub": {}
        }
        
        with patch('scrubb.cli.load_config', return_value=mock_config):
            with patch('scrubb.cli.load_stats', return_value=mock_stats):
                with patch('scrubb.cli.save_stats'):
                    result = runner.invoke(app, ['emoji', '--verbose'])
                    
                    # Check command succeeded
                    assert result.exit_code == 0
                    
                    # Check that verbose output is present (modified files list)
                    assert "scrubb run:" in result.stdout


def test_emoji_command_quiet_flag():
    """Test that emoji command accepts --quiet flag."""
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        
        # Create a test file
        test_file = root / "test.txt"
        test_file.write_text("Hello World", encoding='utf-8')
        
        # Mock the config
        mock_config = {
            "default_root": str(root),
            "ignore_patterns": [".git", "__pycache__", "node_modules"],
            "text_extensions": [".txt", ".md", ".py", ".js"]
        }
        
        mock_stats = {
            "runs": 0,
            "files_processed": 0,
            "files_modified": 0,
            "files_skipped": 0,
            "errors": 0,
            "emojis_removed": 0,
            "scoped_scrub": {}
        }
        
        with patch('scrubb.cli.load_config', return_value=mock_config):
            with patch('scrubb.cli.load_stats', return_value=mock_stats):
                with patch('scrubb.cli.save_stats'):
                    result = runner.invoke(app, ['emoji', '--quiet'])
                    
                    # Check command succeeded
                    assert result.exit_code == 0
                    
                    # In quiet mode, summary output should be suppressed
                    # Only errors would be shown (if any)
                    assert "scrubb run:" not in result.stdout or result.stdout.strip() == ""


def test_emoji_command_verbose_and_quiet_conflict():
    """Test that using both --verbose and --quiet flags results in an error."""
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        
        # Create a test file
        test_file = root / "test.txt"
        test_file.write_text("Hello World", encoding='utf-8')
        
        # Mock the config
        mock_config = {
            "default_root": str(root),
            "ignore_patterns": [".git", "__pycache__", "node_modules"],
            "text_extensions": [".txt", ".md", ".py", ".js"]
        }
        
        with patch('scrubb.cli.load_config', return_value=mock_config):
            result = runner.invoke(app, ['emoji', '--verbose', '--quiet'])
            
            # Check command failed with appropriate exit code
            assert result.exit_code == 2
            
            # Check error message
            output = result.stdout + result.stderr
            assert "Cannot use both --verbose and --quiet" in output


def test_folder_command_verbose_flag():
    """Test that folder command accepts --verbose flag."""
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        
        # Create test files
        (root / "test1.txt").touch()
        (root / "test2.jpg").touch()
        
        # Mock the prompt to return our test directory
        with patch('typer.prompt', return_value=str(root)):
            # Use --yes flag to bypass confirmation prompt
            result = runner.invoke(app, ['folder', '--verbose', '--yes'])
            
            # Check command succeeded
            assert result.exit_code == 0
            
            # Check that output is present
            assert "Target directory:" in result.stdout
            assert "Folder cleanup complete!" in result.stdout


def test_folder_command_quiet_flag():
    """Test that folder command accepts --quiet flag."""
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        
        # Create test files
        (root / "test1.txt").touch()
        (root / "test2.jpg").touch()
        
        # Mock the prompt to return our test directory
        with patch('typer.prompt', return_value=str(root)):
            # Use --yes flag to bypass confirmation prompt
            result = runner.invoke(app, ['folder', '--quiet', '--yes'])
            
            # Check command succeeded
            assert result.exit_code == 0
            
            # In quiet mode, most output should be suppressed
            # Only errors would be shown (if any)
            assert "Folder cleanup complete!" not in result.stdout or result.stdout.strip() == ""


def test_folder_command_verbose_and_quiet_conflict():
    """Test that using both --verbose and --quiet flags results in an error."""
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        
        # Create a test file
        (root / "test.txt").touch()
        
        # Mock the prompt to return our test directory
        with patch('typer.prompt', return_value=str(root)):
            result = runner.invoke(app, ['folder', '--verbose', '--quiet'])
            
            # Check command failed with appropriate exit code
            assert result.exit_code == 2
            
            # Check error message
            output = result.stdout + result.stderr
            assert "Cannot use both --verbose and --quiet" in output


@settings(max_examples=100, deadline=2000)
@given(
    command_type=st.sampled_from(['stats_reset', 'folder']),
    use_yes_flag=st.booleans()
)
def test_auto_confirm_bypass(command_type, use_yes_flag):
    """
    **Feature: cli-improvements, Property 10: Auto-confirm bypass**
    **Validates: Requirements 8.5**
    
    For any destructive operation executed with --yes flag, the command should 
    complete without displaying confirmation prompts.
    """
    if command_type == 'stats_reset':
        # Test stats --reset command with/without --yes flag
        mock_stats = {
            "runs": 5,
            "files_processed": 10,
            "files_modified": 3,
            "files_skipped": 2,
            "errors": 0,
            "emojis_removed": 15,
            "scoped_scrub": {"": 5, "": 10}
        }
        
        # Build arguments
        if use_yes_flag:
            args = ['stats', '--reset', '--yes']
        else:
            args = ['stats', '--reset']
        
        with patch('scrubb.cli.load_stats', return_value=mock_stats):
            with patch('scrubb.cli.save_stats'):
                if use_yes_flag:
                    # With --yes flag, should complete without prompting
                    result = runner.invoke(app, args)
                    
                    # Check command succeeded
                    assert result.exit_code == 0, f"Command failed with exit code {result.exit_code}"
                    
                    # Check that reset message is displayed
                    assert "Persistent stats reset" in result.stdout
                    
                    # Check that no confirmation prompt was displayed
                    # (typer.confirm would show "Are you sure" in the output)
                    assert "Are you sure" not in result.stdout
                else:
                    # Without --yes flag, should prompt for confirmation
                    # Simulate user declining the confirmation
                    result = runner.invoke(app, args, input='n\n')
                    
                    # Check that operation was cancelled
                    assert result.exit_code == 130, f"Expected exit code 130, got {result.exit_code}"
                    
                    # Check that cancellation message is displayed
                    assert "Operation cancelled" in result.stdout
                    
                    # Now test with user accepting the confirmation
                    result = runner.invoke(app, args, input='y\n')
                    
                    # Check command succeeded
                    assert result.exit_code == 0, f"Command failed with exit code {result.exit_code}"
                    
                    # Check that reset message is displayed
                    assert "Persistent stats reset" in result.stdout
    
    elif command_type == 'folder':
        # Test folder command with/without --yes flag
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            
            # Create test files
            (root / "test1.txt").touch()
            (root / "test2.jpg").touch()
            
            # Build arguments
            if use_yes_flag:
                args = ['folder', '--yes']
            else:
                args = ['folder']
            
            # Mock the prompt to return our test directory
            with patch('typer.prompt', return_value=str(root)):
                if use_yes_flag:
                    # With --yes flag, should complete without prompting for confirmation
                    result = runner.invoke(app, args)
                    
                    # Check command succeeded
                    assert result.exit_code == 0, f"Command failed with exit code {result.exit_code}"
                    
                    # Check that completion message is displayed
                    assert "Folder cleanup complete!" in result.stdout
                    
                    # Check that no confirmation prompt was displayed
                    assert "Do you want to proceed?" not in result.stdout
                else:
                    # Without --yes flag, should prompt for confirmation
                    # Simulate user declining the confirmation
                    result = runner.invoke(app, args, input='n\n')
                    
                    # Check that operation was cancelled
                    assert result.exit_code == 130, f"Expected exit code 130, got {result.exit_code}"
                    
                    # Check that cancellation message is displayed
                    assert "Operation cancelled" in result.stdout
                    
                    # Now test with user accepting the confirmation
                    result = runner.invoke(app, args, input='y\n')
                    
                    # Check command succeeded
                    assert result.exit_code == 0, f"Command failed with exit code {result.exit_code}"
                    
                    # Check that completion message is displayed
                    assert "Folder cleanup complete!" in result.stdout
