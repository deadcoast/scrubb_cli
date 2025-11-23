"""Unit tests for FolderOrganizer refactoring to support dry-run mode."""

import tempfile
from pathlib import Path
import pytest

from scrubb.file_classifier import FileClassifier
from scrubb.folder_organizer import FolderOrganizer, OrganizationStats, DryRunStats


def test_dry_run_false_uses_actual_execution_path():
    """
    Test that dry_run=False uses the actual execution path.
    
    Validates: Requirements 1.2, 1.3, 1.4
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        classifier = FileClassifier()
        
        # Create organizer with dry_run=False
        organizer = FolderOrganizer(root, classifier, dry_run=False)
        
        # Create a test file
        test_file = root / "test.txt"
        test_file.touch()
        
        # Run organize
        result = organizer.organize()
        
        # Verify it returns OrganizationStats (not DryRunStats)
        assert isinstance(result, OrganizationStats)
        assert not isinstance(result, DryRunStats)
        
        # Verify actual file system changes occurred
        # The file should have been moved to Scrubbed/Docs/Other Docs
        scrubbed_path = root / "Scrubbed"
        assert scrubbed_path.exists(), "Scrubbed folder should be created"
        
        docs_path = scrubbed_path / "Docs" / "Other Docs"
        assert docs_path.exists(), "Category folder should be created"
        
        # Verify file was actually moved
        moved_files = list(docs_path.glob("*.txt"))
        assert len(moved_files) == 1, "File should be moved to category folder"
        
        # Verify original file no longer exists
        assert not test_file.exists(), "Original file should be moved (not copied)"


def test_dry_run_true_uses_dry_run_execution_path():
    """
    Test that dry_run=True uses the dry-run execution path.
    
    Validates: Requirements 1.2, 1.3, 1.4
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        classifier = FileClassifier()
        
        # Create organizer with dry_run=True
        organizer = FolderOrganizer(root, classifier, dry_run=True)
        
        # Create a test file
        test_file = root / "test.txt"
        test_file.touch()
        
        # Run organize
        result = organizer.organize()
        
        # Verify it returns DryRunStats (not OrganizationStats)
        assert isinstance(result, DryRunStats)
        
        # Verify NO file system changes occurred
        # The Scrubbed folder should NOT be created
        scrubbed_path = root / "Scrubbed"
        assert not scrubbed_path.exists(), "Scrubbed folder should NOT be created in dry-run"
        
        # Verify original file still exists
        assert test_file.exists(), "Original file should remain in place during dry-run"


def test_existing_functionality_not_broken_with_default_dry_run():
    """
    Test that existing functionality is not broken when dry_run defaults to False.
    
    Validates: Requirements 1.2, 1.3, 1.4
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        classifier = FileClassifier()
        
        # Create organizer without specifying dry_run (should default to False)
        organizer = FolderOrganizer(root, classifier)
        
        # Create test files with different extensions
        test_files = {
            "image.jpg": "Images",
            "video.mp4": "Video",
            "doc.pdf": "Docs/Other Docs",
            "code.py": "Development"
        }
        
        for filename in test_files.keys():
            (root / filename).touch()
        
        # Run organize
        result = organizer.organize()
        
        # Verify it returns OrganizationStats
        assert isinstance(result, OrganizationStats)
        
        # Verify files were moved correctly
        assert result.files_moved == len(test_files)
        
        # Verify Scrubbed folder was created
        scrubbed_path = root / "Scrubbed"
        assert scrubbed_path.exists()
        
        # Verify category folders were created and files were moved
        for filename, category_path in test_files.items():
            full_category_path = scrubbed_path / category_path
            assert full_category_path.exists(), f"Category folder {category_path} should exist"
            
            # Check that a file with the correct extension exists in the category
            extension = Path(filename).suffix
            files_in_category = list(full_category_path.glob(f"*{extension}"))
            assert len(files_in_category) >= 1, f"File with extension {extension} should be in {category_path}"


def test_dry_run_false_explicit_matches_actual_behavior():
    """
    Test that explicitly setting dry_run=False produces the same behavior as default.
    
    Validates: Requirements 1.2, 1.3, 1.4
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        classifier = FileClassifier()
        
        # Create organizer with explicit dry_run=False
        organizer = FolderOrganizer(root, classifier, dry_run=False)
        
        # Create test files
        (root / "test1.txt").touch()
        (root / "test2.jpg").touch()
        
        # Run organize
        result = organizer.organize()
        
        # Verify actual execution behavior
        assert isinstance(result, OrganizationStats)
        assert result.files_moved == 2
        
        # Verify files were actually moved
        scrubbed_path = root / "Scrubbed"
        assert scrubbed_path.exists()
        
        # Verify original files don't exist
        assert not (root / "test1.txt").exists()
        assert not (root / "test2.jpg").exists()


def test_organize_method_branches_correctly():
    """
    Test that the organize() method correctly branches based on dry_run flag.
    
    Validates: Requirements 1.2, 1.3, 1.4
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        classifier = FileClassifier()
        
        # Test with dry_run=False
        organizer_actual = FolderOrganizer(root, classifier, dry_run=False)
        (root / "test.txt").touch()
        result_actual = organizer_actual.organize()
        assert isinstance(result_actual, OrganizationStats)
        assert not isinstance(result_actual, DryRunStats)
        
    # Create a new temp directory for dry-run test
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        classifier = FileClassifier()
        
        # Test with dry_run=True
        organizer_dry = FolderOrganizer(root, classifier, dry_run=True)
        (root / "test.txt").touch()
        result_dry = organizer_dry.organize()
        assert isinstance(result_dry, DryRunStats)
