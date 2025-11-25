"""Integration tests for end-to-end folder command execution."""

import tempfile
from pathlib import Path
from typer.testing import CliRunner
from unittest.mock import patch

from scrubb.cli import app


runner = CliRunner()


def test_folder_command_with_unknown_extensions():
    """
    Integration test for folder command with unknown file extensions.
    Requirements: 3.1, 3.2, 3.3, 3.4
    
    Verifies:
    - Folder command executes successfully
    - Files with unknown extensions are organized into "Other" category
    - All files are moved (none skipped)
    - Statistics are displayed correctly
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        
        # Create files with mixed types including unknown extensions
        (root / "image.jpg").write_text("fake image")
        (root / "video.mp4").write_text("fake video")
        (root / "document.pdf").write_text("fake doc")
        (root / "code.py").write_text("print('hello')")
        (root / "unknown1.xyz").write_text("unknown file 1")
        (root / "unknown2.abc").write_text("unknown file 2")
        (root / "no_extension").write_text("file without extension")
        
        # Mock the prompt to return our test directory
        with patch('typer.prompt', return_value=str(root)):
            result = runner.invoke(app, ['folder', '--yes'])
            
            # Check command succeeded
            assert result.exit_code == 0, f"Command failed with output:\n{result.stdout}"
            
            # Verify success message is displayed
            assert "Folder cleanup complete!" in result.stdout
            
            # Verify statistics are displayed
            assert "Files moved:" in result.stdout
            
            # Verify Scrubbed folder was created
            scrubbed_path = root / "Scrubbed"
            assert scrubbed_path.exists(), "Scrubbed folder was not created"
            
            # Verify "Other" category folder was created
            other_folder = scrubbed_path / "Other"
            assert other_folder.exists(), "Other category folder was not created"
            
            # Verify unknown extension files were moved to Other folder
            files_in_other = list(other_folder.glob("*"))
            assert len(files_in_other) == 3, f"Expected 3 files in Other folder, found {len(files_in_other)}"
            
            # Verify the specific unknown files are in Other folder
            other_file_names = {f.name for f in files_in_other}
            assert "unknown1.xyz" in other_file_names
            assert "unknown2.abc" in other_file_names
            assert "no_extension" in other_file_names
            
            # Verify all files were moved (original locations should be empty)
            assert not (root / "image.jpg").exists()
            assert not (root / "video.mp4").exists()
            assert not (root / "document.pdf").exists()
            assert not (root / "code.py").exists()
            assert not (root / "unknown1.xyz").exists()
            assert not (root / "unknown2.abc").exists()
            assert not (root / "no_extension").exists()
            
            # Verify total files moved is correct (7 files)
            assert "Files moved: 7" in result.stdout


def test_folder_command_dry_run_with_unknown_extensions():
    """
    Integration test for folder command in dry-run mode with unknown extensions.
    Requirements: 3.1, 3.2, 3.3, 3.4
    
    Verifies:
    - Dry-run mode executes successfully
    - Unknown extension files are included in preview
    - "Other" category appears in statistics
    - No files are actually moved
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        
        # Create files with mixed types including unknown extensions
        (root / "image.jpg").write_text("fake image")
        (root / "unknown.xyz").write_text("unknown file")
        (root / "no_ext").write_text("no extension")
        
        # Store original file paths for verification
        original_files = {
            root / "image.jpg",
            root / "unknown.xyz",
            root / "no_ext"
        }
        
        # Mock the prompt to return our test directory
        with patch('typer.prompt', return_value=str(root)):
            result = runner.invoke(app, ['folder', '--dry'])
            
            # Check command succeeded
            assert result.exit_code == 0, f"Command failed with output:\n{result.stdout}"
            
            # Verify dry-run mode header is displayed
            assert "DRY RUN MODE" in result.stdout
            
            # Verify dry-run preview is displayed
            assert "DRY RUN PREVIEW" in result.stdout
            
            # Verify "Other" category appears in files by category
            assert "Other" in result.stdout
            
            # Verify files to move count includes unknown extensions
            assert "Files to move: 3" in result.stdout
            
            # Verify NO files were moved (all original files should still exist)
            for file_path in original_files:
                assert file_path.exists(), f"File {file_path} was moved in dry-run mode!"
            
            # Verify Scrubbed folder was NOT created
            scrubbed_path = root / "Scrubbed"
            assert not scrubbed_path.exists(), "Scrubbed folder was created in dry-run mode!"


def test_folder_command_with_nested_unknown_files():
    """
    Integration test for folder command with unknown files in nested directories.
    Requirements: 3.1, 3.2, 3.3, 3.4
    
    Verifies:
    - Files in nested directories are discovered
    - Unknown extension files from nested directories are organized
    - Empty nested directories are removed
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        
        # Create nested directory structure with unknown files
        level1 = root / "level1"
        level1.mkdir()
        (level1 / "unknown1.xyz").write_text("unknown in level1")
        
        level2 = level1 / "level2"
        level2.mkdir()
        (level2 / "unknown2.abc").write_text("unknown in level2")
        (level2 / "image.jpg").write_text("image in level2")
        
        # Mock the prompt to return our test directory
        with patch('typer.prompt', return_value=str(root)):
            result = runner.invoke(app, ['folder', '--yes'])
            
            # Check command succeeded
            assert result.exit_code == 0, f"Command failed with output:\n{result.stdout}"
            
            # Verify all files were moved
            assert "Files moved: 3" in result.stdout
            
            # Verify "Other" category folder was created
            scrubbed_path = root / "Scrubbed"
            other_folder = scrubbed_path / "Other"
            assert other_folder.exists()
            
            # Verify unknown files were moved to Other folder
            files_in_other = list(other_folder.glob("*"))
            assert len(files_in_other) == 2
            
            other_file_names = {f.name for f in files_in_other}
            assert "unknown1.xyz" in other_file_names
            assert "unknown2.abc" in other_file_names
            
            # Verify nested directories were removed (they should be empty)
            assert not level1.exists() or len(list(level1.rglob("*"))) == 0


def test_folder_command_statistics_include_other_category():
    """
    Integration test verifying statistics include "Other" category.
    Requirements: 3.1, 3.2, 3.3, 3.4
    
    Verifies:
    - Statistics display includes "Other" category
    - Count of files in "Other" category is correct
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        
        # Create multiple unknown extension files
        for i in range(5):
            (root / f"unknown{i}.xyz").write_text(f"unknown file {i}")
        
        # Create one known file
        (root / "image.jpg").write_text("known file")
        
        # Mock the prompt to return our test directory
        with patch('typer.prompt', return_value=str(root)):
            result = runner.invoke(app, ['folder', '--yes'])
            
            # Check command succeeded
            assert result.exit_code == 0, f"Command failed with output:\n{result.stdout}"
            
            # Verify total files moved
            assert "Files moved: 6" in result.stdout
            
            # Verify "Other" category appears in statistics
            assert "Other:" in result.stdout or "Other: 5" in result.stdout
            
            # Verify the count is correct
            # The output should show "Other: 5" somewhere
            output_lines = result.stdout.split('\n')
            other_line = [line for line in output_lines if "Other:" in line]
            assert len(other_line) > 0, "Other category not found in statistics"
            assert "5" in other_line[0], f"Expected 5 files in Other category, got: {other_line[0]}"


def test_folder_command_with_only_unknown_files():
    """
    Integration test with directory containing only unknown extension files.
    Requirements: 3.1, 3.2, 3.3, 3.4
    
    Verifies:
    - Command handles directory with only unknown files
    - All files are organized into "Other" category
    - No files are skipped
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        
        # Create only unknown extension files
        (root / "file1.xyz").write_text("unknown 1")
        (root / "file2.abc").write_text("unknown 2")
        (root / "file3.def").write_text("unknown 3")
        (root / "no_ext").write_text("no extension")
        
        # Mock the prompt to return our test directory
        with patch('typer.prompt', return_value=str(root)):
            result = runner.invoke(app, ['folder', '--yes'])
            
            # Check command succeeded
            assert result.exit_code == 0, f"Command failed with output:\n{result.stdout}"
            
            # Verify all files were moved
            assert "Files moved: 4" in result.stdout
            
            # Verify only "Other" category folder was created
            scrubbed_path = root / "Scrubbed"
            category_folders = [item for item in scrubbed_path.iterdir() if item.is_dir()]
            assert len(category_folders) == 1
            assert category_folders[0].name == "Other"
            
            # Verify all files are in Other folder
            files_in_other = list((scrubbed_path / "Other").glob("*"))
            assert len(files_in_other) == 4


def test_folder_command_empty_directory():
    """
    Integration test with empty directory.
    Requirements: 3.1, 3.2, 3.3, 3.4
    
    Verifies:
    - Command handles empty directory gracefully
    - Appropriate message is displayed
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        
        # Directory is empty - no files created
        
        # Mock the prompt to return our test directory
        with patch('typer.prompt', return_value=str(root)):
            result = runner.invoke(app, ['folder', '--yes'])
            
            # Check command succeeded
            assert result.exit_code == 0, f"Command failed with output:\n{result.stdout}"
            
            # Verify no files were moved
            assert "Files moved: 0" in result.stdout
            
            # Verify Scrubbed folder was created but is empty
            scrubbed_path = root / "Scrubbed"
            assert scrubbed_path.exists()
            
            # No category folders should be created
            category_folders = list(scrubbed_path.iterdir())
            assert len(category_folders) == 0


def test_folder_command_with_verbose_flag():
    """
    Integration test with verbose flag enabled.
    Requirements: 3.1, 3.2, 3.3, 3.4
    
    Verifies:
    - Verbose output includes detailed information
    - File discovery count is displayed
    - Category assignments are logged
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        
        # Create files
        (root / "image.jpg").write_text("image")
        (root / "unknown.xyz").write_text("unknown")
        
        # Mock the prompt to return our test directory
        with patch('typer.prompt', return_value=str(root)):
            result = runner.invoke(app, ['folder', '--verbose', '--yes'])
            
            # Check command succeeded
            assert result.exit_code == 0, f"Command failed with output:\n{result.stdout}"
            
            # Verify verbose output includes file discovery count
            assert "Files discovered:" in result.stdout
            
            # Verify target directory is displayed
            assert "Target directory:" in result.stdout
            
            # Verify operation complete message
            assert "Operation complete:" in result.stdout


def test_folder_command_with_quiet_flag():
    """
    Integration test with quiet flag enabled.
    Requirements: 3.1, 3.2, 3.3, 3.4
    
    Verifies:
    - Quiet mode suppresses non-essential output
    - Command still executes successfully
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        
        # Create files
        (root / "image.jpg").write_text("image")
        (root / "unknown.xyz").write_text("unknown")
        
        # Mock the prompt to return our test directory
        with patch('typer.prompt', return_value=str(root)):
            result = runner.invoke(app, ['folder', '--quiet', '--yes'])
            
            # Check command succeeded
            assert result.exit_code == 0, f"Command failed with output:\n{result.stdout}"
            
            # Verify minimal output (quiet mode should suppress most messages)
            # The output should be significantly shorter than normal mode
            assert len(result.stdout) < 500, "Quiet mode output is too verbose"


def test_folder_command_with_name_conflicts():
    """
    Integration test with name conflicts including unknown extensions.
    Requirements: 3.1, 3.2, 3.3, 3.4
    
    Verifies:
    - Name conflicts are resolved correctly
    - Unknown extension files with conflicts are handled
    - All files are preserved
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        
        # Create subdirectories with files that will have name conflicts
        dir1 = root / "dir1"
        dir1.mkdir()
        (dir1 / "unknown.xyz").write_text("unknown from dir1")
        
        dir2 = root / "dir2"
        dir2.mkdir()
        (dir2 / "unknown.xyz").write_text("unknown from dir2")
        
        dir3 = root / "dir3"
        dir3.mkdir()
        (dir3 / "unknown.xyz").write_text("unknown from dir3")
        
        # Mock the prompt to return our test directory
        with patch('typer.prompt', return_value=str(root)):
            result = runner.invoke(app, ['folder', '--yes'])
            
            # Check command succeeded
            assert result.exit_code == 0, f"Command failed with output:\n{result.stdout}"
            
            # Verify all files were moved
            assert "Files moved: 3" in result.stdout
            
            # Verify "Other" category folder was created
            scrubbed_path = root / "Scrubbed"
            other_folder = scrubbed_path / "Other"
            assert other_folder.exists()
            
            # Verify all 3 files are in Other folder with resolved names
            files_in_other = list(other_folder.glob("*"))
            assert len(files_in_other) == 3
            
            # Verify naming pattern (unknown.xyz, unknown_1.xyz, unknown_2.xyz)
            file_names = sorted([f.name for f in files_in_other])
            assert "unknown.xyz" in file_names
            assert "unknown_1.xyz" in file_names
            assert "unknown_2.xyz" in file_names
