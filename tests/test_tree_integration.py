"""Integration tests for tree visualization feature."""

import tempfile
import shutil
from pathlib import Path
from typer.testing import CliRunner
from unittest.mock import patch

from scrubb.cli import app


runner = CliRunner()


def test_tree_flag_with_actual_execution():
    """
    Test --tree flag with actual execution.
    Requirements: 1.1
    
    Verifies:
    - Before tree is displayed
    - After tree is displayed
    - Comparison is displayed
    - Files are actually moved
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        
        # Create sample files of different types
        (root / "image1.jpg").write_text("fake image")
        (root / "image2.png").write_text("fake image")
        (root / "video.mp4").write_text("fake video")
        (root / "document.pdf").write_text("fake doc")
        (root / "code.py").write_text("print('hello')")
        
        # Create a subdirectory with a file
        subdir = root / "subdir"
        subdir.mkdir()
        (subdir / "nested.txt").write_text("nested file")
        
        # Mock the prompt to return our test directory
        with patch('typer.prompt', return_value=str(root)):
            result = runner.invoke(app, ['folder', '--tree', '--yes'])
            
            # Check command succeeded
            assert result.exit_code == 0, f"Command failed with output:\n{result.stdout}"
            
            # Verify before tree is displayed
            assert "BEFORE" in result.stdout, "Before tree header not found"
            
            # Verify after tree is displayed
            assert "AFTER" in result.stdout, "After tree header not found"
            
            # Verify comparison is displayed
            assert "COMPARISON" in result.stdout or "Files:" in result.stdout, "Comparison not found"
            
            # Verify files were actually moved
            scrubbed_path = root / "Scrubbed"
            assert scrubbed_path.exists(), "Scrubbed folder was not created"
            
            # Check that at least some category folders were created
            category_folders = list(scrubbed_path.iterdir())
            assert len(category_folders) > 0, "No category folders created"
            
            # Verify files were moved (original locations should be empty or removed)
            # The subdir should be removed as it becomes empty
            assert not (root / "image1.jpg").exists(), "image1.jpg was not moved"
            assert not (root / "video.mp4").exists(), "video.mp4 was not moved"
            
            # Verify standard output is still present
            assert "Folder cleanup complete!" in result.stdout
            assert "Files moved:" in result.stdout


def test_tree_and_dry_flags_together():
    """
    Test --tree --dry flags together.
    Requirements: 1.2, 7.5
    
    Verifies:
    - Before tree is displayed
    - Simulated after tree is displayed
    - Simulation indicator is present
    - No files are moved
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        
        # Create sample files
        (root / "image.jpg").write_text("fake image")
        (root / "video.mp4").write_text("fake video")
        (root / "document.pdf").write_text("fake doc")
        
        # Store original file paths for verification
        original_files = {
            root / "image.jpg",
            root / "video.mp4",
            root / "document.pdf"
        }
        
        # Mock the prompt to return our test directory
        with patch('typer.prompt', return_value=str(root)):
            result = runner.invoke(app, ['folder', '--tree', '--dry'])
            
            # Check command succeeded
            assert result.exit_code == 0, f"Command failed with output:\n{result.stdout}"
            
            # Verify dry-run mode header is displayed
            assert "DRY RUN MODE" in result.stdout, "Dry-run mode header not found"
            
            # Verify before tree is displayed
            assert "BEFORE" in result.stdout, "Before tree header not found"
            
            # Verify simulated after tree is displayed
            assert "AFTER" in result.stdout, "After tree header not found"
            
            # Verify simulation indicator is present
            assert "Simulated" in result.stdout or "SIMULATED" in result.stdout or "DRY RUN" in result.stdout, \
                "Simulation indicator not found"
            
            # Verify comparison is displayed
            assert "COMPARISON" in result.stdout or "Files:" in result.stdout, "Comparison not found"
            
            # Verify NO files were moved (all original files should still exist)
            for file_path in original_files:
                assert file_path.exists(), f"File {file_path} was moved in dry-run mode!"
            
            # Verify Scrubbed folder was NOT created
            scrubbed_path = root / "Scrubbed"
            assert not scrubbed_path.exists(), "Scrubbed folder was created in dry-run mode!"
            
            # Verify standard dry-run output is present
            assert "DRY RUN PREVIEW" in result.stdout


def test_tree_visualization_with_empty_directory():
    """
    Test tree visualization with empty directory.
    Requirements: 4.2, 4.3, 5.2
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        
        # Directory is empty - no files created
        
        # Mock the prompt to return our test directory
        with patch('typer.prompt', return_value=str(root)):
            result = runner.invoke(app, ['folder', '--tree', '--yes'])
            
            # Check command succeeded
            assert result.exit_code == 0, f"Command failed with output:\n{result.stdout}"
            
            # Verify before tree is displayed
            assert "BEFORE" in result.stdout
            
            # Verify after tree is displayed
            assert "AFTER" in result.stdout
            
            # Verify comparison is displayed
            assert "COMPARISON" in result.stdout or "Files:" in result.stdout
            
            # Verify no files were moved (should be 0)
            assert "Files moved: 0" in result.stdout


def test_tree_visualization_with_single_file():
    """
    Test tree visualization with single file.
    Requirements: 4.2, 4.3, 5.2
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        
        # Create a single file
        (root / "single.txt").write_text("single file")
        
        # Mock the prompt to return our test directory
        with patch('typer.prompt', return_value=str(root)):
            result = runner.invoke(app, ['folder', '--tree', '--yes'])
            
            # Check command succeeded
            assert result.exit_code == 0, f"Command failed with output:\n{result.stdout}"
            
            # Verify before tree is displayed
            assert "BEFORE" in result.stdout
            
            # Verify after tree is displayed
            assert "AFTER" in result.stdout
            
            # Verify file was moved
            scrubbed_path = root / "Scrubbed"
            assert scrubbed_path.exists()
            
            # Verify exactly 1 file was moved
            assert "Files moved: 1" in result.stdout


def test_tree_visualization_with_nested_directories():
    """
    Test tree visualization with nested directories.
    Requirements: 4.2, 4.3, 5.2
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        
        # Create nested directory structure
        level1 = root / "level1"
        level1.mkdir()
        (level1 / "file1.txt").write_text("level 1 file")
        
        level2 = level1 / "level2"
        level2.mkdir()
        (level2 / "file2.jpg").write_text("level 2 file")
        
        level3 = level2 / "level3"
        level3.mkdir()
        (level3 / "file3.pdf").write_text("level 3 file")
        
        # Mock the prompt to return our test directory
        with patch('typer.prompt', return_value=str(root)):
            result = runner.invoke(app, ['folder', '--tree', '--yes'])
            
            # Check command succeeded
            assert result.exit_code == 0, f"Command failed with output:\n{result.stdout}"
            
            # Verify before tree is displayed
            assert "BEFORE" in result.stdout
            
            # Verify after tree is displayed
            assert "AFTER" in result.stdout
            
            # Verify files were moved
            scrubbed_path = root / "Scrubbed"
            assert scrubbed_path.exists()
            
            # Verify all 3 files were moved
            assert "Files moved: 3" in result.stdout
            
            # Verify nested directories were removed (they should be empty)
            assert not level1.exists() or len(list(level1.rglob("*"))) == 0


def test_tree_visualization_with_large_directory():
    """
    Test tree visualization with large directory (100+ files).
    Requirements: 4.2, 4.3, 5.2
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        
        # Create 100+ files of various types
        for i in range(30):
            (root / f"image{i}.jpg").write_text(f"image {i}")
        for i in range(30):
            (root / f"video{i}.mp4").write_text(f"video {i}")
        for i in range(30):
            (root / f"doc{i}.pdf").write_text(f"doc {i}")
        for i in range(20):
            (root / f"code{i}.py").write_text(f"code {i}")
        
        # Mock the prompt to return our test directory
        with patch('typer.prompt', return_value=str(root)):
            result = runner.invoke(app, ['folder', '--tree', '--yes'])
            
            # Check command succeeded
            assert result.exit_code == 0, f"Command failed with output:\n{result.stdout}"
            
            # Verify before tree is displayed
            assert "BEFORE" in result.stdout
            
            # Verify after tree is displayed
            assert "AFTER" in result.stdout
            
            # Verify comparison is displayed
            assert "COMPARISON" in result.stdout or "Files:" in result.stdout
            
            # Verify all 110 files were moved
            assert "Files moved: 110" in result.stdout
            
            # Verify Scrubbed folder was created
            scrubbed_path = root / "Scrubbed"
            assert scrubbed_path.exists()


def test_output_ordering():
    """
    Test output ordering.
    Requirements: 9.1, 9.2
    
    Verifies:
    - Trees display before standard output
    - Statistics display after trees
    - Comparison displays between trees and standard output
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        
        # Create sample files
        (root / "image.jpg").write_text("fake image")
        (root / "video.mp4").write_text("fake video")
        
        # Mock the prompt to return our test directory
        with patch('typer.prompt', return_value=str(root)):
            result = runner.invoke(app, ['folder', '--tree', '--yes'])
            
            # Check command succeeded
            assert result.exit_code == 0, f"Command failed with output:\n{result.stdout}"
            
            output = result.stdout
            
            # Find positions of key sections
            before_pos = output.find("BEFORE")
            after_pos = output.find("AFTER")
            comparison_pos = output.find("COMPARISON") if "COMPARISON" in output else output.find("Files:")
            target_dir_pos = output.find("Target directory:")
            cleanup_pos = output.find("Folder cleanup complete!")
            
            # Verify all sections are present
            assert before_pos != -1, "BEFORE section not found"
            assert after_pos != -1, "AFTER section not found"
            assert comparison_pos != -1, "Comparison section not found"
            assert target_dir_pos != -1, f"Target directory message not found. Output:\n{output}"
            assert cleanup_pos != -1, "Cleanup complete message not found"
            
            # Verify ordering: BEFORE < AFTER < COMPARISON < standard output
            assert before_pos < after_pos, "BEFORE should come before AFTER"
            assert after_pos < comparison_pos, "AFTER should come before COMPARISON"
            assert comparison_pos < cleanup_pos, "COMPARISON should come before cleanup message"
            
            # Verify target directory message comes after BEFORE (trees display first)
            assert before_pos < target_dir_pos, "Trees should display before target directory message"


def test_output_ordering_dry_run():
    """
    Test output ordering in dry-run mode.
    Requirements: 9.1, 9.2
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        
        # Create sample files
        (root / "image.jpg").write_text("fake image")
        (root / "video.mp4").write_text("fake video")
        
        # Mock the prompt to return our test directory
        with patch('typer.prompt', return_value=str(root)):
            result = runner.invoke(app, ['folder', '--tree', '--dry'])
            
            # Check command succeeded
            assert result.exit_code == 0, f"Command failed with output:\n{result.stdout}"
            
            output = result.stdout
            
            # Find positions of key sections
            dry_run_header_pos = output.find("DRY RUN MODE")
            before_pos = output.find("BEFORE")
            after_pos = output.find("AFTER")
            comparison_pos = output.find("COMPARISON") if "COMPARISON" in output else output.find("Files:")
            dry_run_preview_pos = output.find("DRY RUN PREVIEW")
            
            # Verify all sections are present
            assert dry_run_header_pos != -1, "DRY RUN MODE header not found"
            assert before_pos != -1, "BEFORE section not found"
            assert after_pos != -1, "AFTER section not found"
            assert comparison_pos != -1, "Comparison section not found"
            assert dry_run_preview_pos != -1, "DRY RUN PREVIEW not found"
            
            # Verify ordering
            assert dry_run_header_pos < before_pos, "DRY RUN MODE header should come first"
            assert before_pos < after_pos, "BEFORE should come before AFTER"
            assert after_pos < comparison_pos, "AFTER should come before COMPARISON"
            assert comparison_pos < dry_run_preview_pos, "COMPARISON should come before DRY RUN PREVIEW"
