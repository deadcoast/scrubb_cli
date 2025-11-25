"""Property-based tests for folder organizer functionality."""

import tempfile
import shutil
from pathlib import Path
from hypothesis import given, strategies as st, settings
import pytest

from scrubb.file_classifier import FileClassifier, FileCategory
from scrubb.folder_organizer import FolderOrganizer


# Helper function to create nested directory structures
def create_nested_structure(base_path: Path, structure: dict):
    """
    Create a nested directory structure from a dictionary.
    
    Args:
        base_path: Base directory to create structure in
        structure: Dict where keys are paths and values are either None (file) or dict (directory)
    """
    for name, content in structure.items():
        path = base_path / name
        if content is None:
            # It's a file
            path.parent.mkdir(parents=True, exist_ok=True)
            path.touch()
        else:
            # It's a directory
            path.mkdir(parents=True, exist_ok=True)
            if content:
                create_nested_structure(path, content)


@settings(max_examples=100)
@given(
    depth=st.integers(min_value=1, max_value=5),
    files_per_level=st.integers(min_value=1, max_value=3)
)
def test_recursive_file_discovery(depth, files_per_level):
    """
    **Feature: folder-cleanup, Property 8: Recursive file discovery**
    **Validates: Requirements 7.1, 7.2**
    
    For any directory tree structure, the system should discover and process
    files at all depth levels, regardless of nesting.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        classifier = FileClassifier()
        organizer = FolderOrganizer(root, classifier)
        
        # Create nested directory structure with files at various depths
        expected_files = []
        
        for level in range(depth):
            level_dir = root
            for d in range(level + 1):
                level_dir = level_dir / f"level_{d}"
            level_dir.mkdir(parents=True, exist_ok=True)
            
            # Create files at this level
            for i in range(files_per_level):
                file_path = level_dir / f"file_{level}_{i}.txt"
                file_path.touch()
                expected_files.append(file_path)
        
        # Scan files
        found_files = organizer._scan_files()
        
        # Verify all files were discovered
        assert len(found_files) == len(expected_files)
        
        # Verify each expected file was found
        found_paths = set(found_files)
        for expected_file in expected_files:
            assert expected_file in found_paths



@settings(max_examples=100)
@given(
    file_count=st.integers(min_value=1, max_value=10),
    extensions=st.lists(
        st.sampled_from([
            ".jpg", ".png", ".gif",  # Images
            ".mp4", ".avi", ".mov",  # Video
            ".md", ".markdown",  # Markdown
            ".pdf", ".txt", ".docx",  # Documents
            ".py", ".js", ".html"  # Development
        ]),
        min_size=1,
        max_size=10
    )
)
def test_file_categorization_correctness(file_count, extensions):
    """
    **Feature: folder-cleanup, Property 1: File categorization correctness**
    **Validates: Requirements 3.1, 3.2, 3.3, 3.4, 3.5**
    
    For any file with a recognized extension, the system should move that file
    to the correct category folder based on its extension type.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        classifier = FileClassifier()
        organizer = FolderOrganizer(root, classifier)
        
        # Create files with various extensions
        created_files = []
        for i in range(file_count):
            ext = extensions[i % len(extensions)]
            file_path = root / f"file_{i}{ext}"
            file_path.touch()
            created_files.append((file_path, ext))
        
        # Organize files
        organizer.organize()
        
        # Verify each file ended up in the correct category folder
        for original_path, ext in created_files:
            # Determine expected category
            expected_category = classifier.classify(Path(f"test{ext}"))
            
            if expected_category == FileCategory.UNKNOWN:
                continue
            
            # Check if file exists in the correct category folder
            category_dir = organizer.scrubbed_path / expected_category.value
            
            # File should be in this category directory
            files_in_category = list(category_dir.glob("*"))
            
            # At least one file should have the same extension
            found = any(f.suffix.lower() == ext.lower() for f in files_in_category)
            assert found, f"File with extension {ext} not found in {expected_category.value}"



@settings(max_examples=100)
@given(
    categories=st.lists(
        st.sampled_from([
            FileCategory.IMAGE,
            FileCategory.VIDEO,
            FileCategory.MARKDOWN,
            FileCategory.DOCUMENT,
            FileCategory.DEVELOPMENT
        ]),
        min_size=1,
        max_size=5,
        unique=True
    )
)
def test_category_directory_creation(categories):
    """
    **Feature: folder-cleanup, Property 3: Category directory creation**
    **Validates: Requirements 3.7**
    
    For any file category that has files to move, the system should create
    the corresponding category subdirectory if it does not exist.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        classifier = FileClassifier()
        organizer = FolderOrganizer(root, classifier)
        
        # Map categories to extensions
        category_to_ext = {
            FileCategory.IMAGE: ".jpg",
            FileCategory.VIDEO: ".mp4",
            FileCategory.MARKDOWN: ".md",
            FileCategory.DOCUMENT: ".pdf",
            FileCategory.DEVELOPMENT: ".py"
        }
        
        # Create files for each category
        for category in categories:
            ext = category_to_ext[category]
            file_path = root / f"file_{category.name}{ext}"
            file_path.touch()
        
        # Organize files
        organizer.organize()
        
        # Verify all necessary category directories were created
        for category in categories:
            category_dir = organizer.scrubbed_path / category.value
            assert category_dir.exists(), f"Category directory {category.value} was not created"
            assert category_dir.is_dir(), f"{category.value} exists but is not a directory"



@settings(max_examples=100)
@given(
    depth=st.integers(min_value=2, max_value=5),
    files_per_level=st.integers(min_value=1, max_value=3)
)
def test_directory_structure_flattening(depth, files_per_level):
    """
    **Feature: folder-cleanup, Property 9: Directory structure flattening**
    **Validates: Requirements 7.3**
    
    For any file in a nested source directory structure, the system should move
    it to a flat category folder without preserving the original directory hierarchy.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        classifier = FileClassifier()
        organizer = FolderOrganizer(root, classifier)
        
        # Create nested directory structure with files at various depths
        for level in range(depth):
            level_dir = root
            for d in range(level + 1):
                level_dir = level_dir / f"nested_{d}"
            level_dir.mkdir(parents=True, exist_ok=True)
            
            # Create files at this level
            for i in range(files_per_level):
                file_path = level_dir / f"file_{level}_{i}.txt"
                file_path.touch()
        
        # Organize files
        organizer.organize()
        
        # Verify destination has flat structure organized by category only
        # All .txt files should be in Docs/Other Docs
        docs_dir = organizer.scrubbed_path / "Docs" / "Other Docs"
        assert docs_dir.exists()
        
        # Check that files are directly in the category folder (flat structure)
        files_in_docs = list(docs_dir.glob("*"))
        
        # All items should be files, not directories (except for conflict resolution numbers)
        for item in files_in_docs:
            assert item.is_file(), f"Found non-file item in category folder: {item}"
        
        # Verify no nested directories were created in the destination
        subdirs_in_docs = [item for item in docs_dir.iterdir() if item.is_dir()]
        assert len(subdirs_in_docs) == 0, "Found nested directories in category folder"



@settings(max_examples=100)
@given(
    total_files=st.integers(min_value=3, max_value=10),
    error_indices=st.lists(st.integers(min_value=0, max_value=9), min_size=1, max_size=3, unique=True)
)
def test_error_handling_continuation(total_files, error_indices):
    """
    **Feature: folder-cleanup, Property 10: Error handling continuation**
    **Validates: Requirements 9.1, 9.2**
    
    For any file that cannot be moved or accessed, the system should log the error,
    increment the error counter, and continue processing remaining files.
    """
    from unittest.mock import patch, MagicMock
    
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        classifier = FileClassifier()
        organizer = FolderOrganizer(root, classifier)
        
        # Create files
        created_files = []
        for i in range(total_files):
            file_path = root / f"file_{i}.txt"
            file_path.touch()
            created_files.append(file_path)
        
        # Filter error indices to only valid ones
        valid_error_indices = [idx for idx in error_indices if idx < total_files]
        
        if not valid_error_indices:
            # Skip test if no valid error indices
            return
        
        # Mock shutil.move to raise errors for specific files
        original_move = shutil.move
        
        def mock_move(src, dst):
            src_path = Path(src)
            if any(f"file_{idx}.txt" in str(src_path) for idx in valid_error_indices):
                raise PermissionError(f"Permission denied: {src}")
            return original_move(src, dst)
        
        with patch('shutil.move', side_effect=mock_move):
            # Organize files
            stats = organizer.organize()
            
            # Verify errors were tracked
            assert stats.errors == len(valid_error_indices), \
                f"Expected {len(valid_error_indices)} errors, got {stats.errors}"
            
            # Verify error files were logged
            assert len(stats.error_files) == len(valid_error_indices), \
                f"Expected {len(valid_error_indices)} error files logged"
            
            # Verify successful files were still moved
            expected_successful = total_files - len(valid_error_indices)
            assert stats.files_moved == expected_successful, \
                f"Expected {expected_successful} files moved, got {stats.files_moved}"



@settings(max_examples=100)
@given(
    base_name=st.text(min_size=1, max_size=10, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'))),
    extension=st.sampled_from([".txt", ".jpg", ".py", ".pdf"]),
    conflict_count=st.integers(min_value=2, max_value=5)
)
def test_name_conflict_resolution_preserves_files(base_name, extension, conflict_count):
    """
    **Feature: folder-cleanup, Property 4: Name conflict resolution preserves files**
    **Validates: Requirements 4.1, 4.3**
    
    For any file name conflict in a destination folder, the system should rename
    the incoming file with a numeric suffix while preserving the file extension,
    ensuring no files are overwritten.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        classifier = FileClassifier()
        organizer = FolderOrganizer(root, classifier)
        
        # Create multiple files with the same name
        for i in range(conflict_count):
            file_path = root / f"{base_name}{extension}"
            # Create in subdirectories to avoid conflicts before organization
            subdir = root / f"dir_{i}"
            subdir.mkdir()
            file_path = subdir / f"{base_name}{extension}"
            file_path.touch()
        
        # Organize files
        organizer.organize()
        
        # Determine which category the files should be in
        category = classifier.classify(Path(f"test{extension}"))
        if category == FileCategory.UNKNOWN:
            return
        
        category_dir = organizer.scrubbed_path / category.value
        
        # Verify all files exist in the category folder
        files_in_category = list(category_dir.glob("*"))
        assert len(files_in_category) == conflict_count, \
            f"Expected {conflict_count} files, found {len(files_in_category)}"
        
        # Verify all files have the correct extension
        for file in files_in_category:
            assert file.suffix == extension, \
                f"File {file.name} has wrong extension {file.suffix}, expected {extension}"



@settings(max_examples=100)
@given(
    base_name=st.text(min_size=1, max_size=10, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'))),
    extension=st.sampled_from([".txt", ".jpg", ".py"]),
    duplicate_count=st.integers(min_value=2, max_value=6)
)
def test_incremental_conflict_numbering(base_name, extension, duplicate_count):
    """
    **Feature: folder-cleanup, Property 5: Incremental conflict numbering**
    **Validates: Requirements 4.2**
    
    For any sequence of files with the same name, the system should append
    incrementing numbers (1, 2, 3, ...) to preserve all files uniquely.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        classifier = FileClassifier()
        organizer = FolderOrganizer(root, classifier)
        
        # Create multiple files with identical names in different subdirectories
        for i in range(duplicate_count):
            subdir = root / f"source_{i}"
            subdir.mkdir()
            file_path = subdir / f"{base_name}{extension}"
            file_path.touch()
        
        # Organize files
        organizer.organize()
        
        # Determine category
        category = classifier.classify(Path(f"test{extension}"))
        if category == FileCategory.UNKNOWN:
            return
        
        category_dir = organizer.scrubbed_path / category.value
        
        # Get all files in category
        files = sorted(category_dir.glob("*"), key=lambda p: p.name)
        
        # Verify we have the right number of files
        assert len(files) == duplicate_count
        
        # Verify naming pattern: first file has original name, rest have _1, _2, etc.
        expected_names = [f"{base_name}{extension}"]
        for i in range(1, duplicate_count):
            expected_names.append(f"{base_name}_{i}{extension}")
        
        actual_names = sorted([f.name for f in files])
        expected_names_sorted = sorted(expected_names)
        
        assert actual_names == expected_names_sorted, \
            f"Expected {expected_names_sorted}, got {actual_names}"



@settings(max_examples=100)
@given(
    empty_dir_count=st.integers(min_value=1, max_value=5),
    file_count=st.integers(min_value=1, max_value=5)
)
def test_empty_directory_removal(empty_dir_count, file_count):
    """
    **Feature: folder-cleanup, Property 6: Empty directory removal**
    **Validates: Requirements 5.1**
    
    For any directory that becomes empty after file moves (and is not the root
    or Scrubbed folder), the system should remove that directory.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        classifier = FileClassifier()
        organizer = FolderOrganizer(root, classifier)
        
        # Create directories that will become empty
        empty_dirs = []
        for i in range(empty_dir_count):
            empty_dir = root / f"will_be_empty_{i}"
            empty_dir.mkdir()
            empty_dirs.append(empty_dir)
            
            # Put files in these directories that will be moved
            for j in range(file_count):
                file_path = empty_dir / f"file_{j}.txt"
                file_path.touch()
        
        # Organize files
        organizer.organize()
        
        # Verify empty directories were removed
        for empty_dir in empty_dirs:
            assert not empty_dir.exists(), f"Empty directory {empty_dir} was not removed"
        
        # Verify root directory still exists
        assert root.exists()
        
        # Verify Scrubbed folder still exists
        assert organizer.scrubbed_path.exists()



@settings(max_examples=100)
@given(
    depth=st.integers(min_value=2, max_value=5),
    branches=st.integers(min_value=1, max_value=3)
)
def test_recursive_empty_directory_removal(depth, branches):
    """
    **Feature: folder-cleanup, Property 7: Recursive empty directory removal**
    **Validates: Requirements 5.2**
    
    For any directory containing only empty subdirectories (and is not the root
    or Scrubbed folder), the system should recursively remove all empty subdirectories.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        classifier = FileClassifier()
        organizer = FolderOrganizer(root, classifier)
        
        # Create nested empty directory structure
        created_dirs = []
        
        def create_nested_empty_dirs(parent, current_depth):
            if current_depth >= depth:
                return
            
            for i in range(branches):
                new_dir = parent / f"empty_level_{current_depth}_branch_{i}"
                new_dir.mkdir()
                created_dirs.append(new_dir)
                create_nested_empty_dirs(new_dir, current_depth + 1)
        
        # Create the nested structure
        base_empty = root / "empty_tree"
        base_empty.mkdir()
        created_dirs.append(base_empty)
        create_nested_empty_dirs(base_empty, 1)
        
        # Create a file somewhere to trigger organization
        test_file = root / "test.txt"
        test_file.touch()
        
        # Organize files
        organizer.organize()
        
        # Verify all empty directories were removed
        for empty_dir in created_dirs:
            assert not empty_dir.exists(), \
                f"Empty directory {empty_dir} was not removed"
        
        # Verify root still exists
        assert root.exists()
        
        # Verify Scrubbed folder still exists
        assert organizer.scrubbed_path.exists()


@settings(max_examples=100)
@given(
    file_count=st.integers(min_value=1, max_value=20),
    extensions=st.lists(
        st.sampled_from([
            ".jpg", ".png", ".gif",  # Images
            ".mp4", ".avi", ".mov",  # Video
            ".md", ".markdown",  # Markdown
            ".pdf", ".txt", ".docx",  # Documents
            ".py", ".js", ".html",  # Development
            ".xyz", ".abc", ".unknown"  # Unknown extensions
        ]),
        min_size=1,
        max_size=20
    )
)
def test_complete_file_coverage(file_count, extensions):
    """
    **Feature: unknown-file-handling, Property 1: Complete file coverage**
    **Validates: Requirements 1.1, 1.4, 3.3**
    
    For any directory containing files, after organization completes, the number
    of files in categorized folders plus files that failed to move SHALL equal
    the total number of files discovered during scanning.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        classifier = FileClassifier()
        organizer = FolderOrganizer(root, classifier, dry_run=False)
        
        # Create files with various extensions
        created_files = []
        for i in range(file_count):
            ext = extensions[i % len(extensions)]
            file_path = root / f"file_{i}{ext}"
            file_path.write_text(f"content {i}")
            created_files.append(file_path)
        
        # Record the number of files discovered
        files_discovered = organizer._scan_files()
        total_files_discovered = len(files_discovered)
        
        # Organize files
        stats = organizer.organize()
        
        # Verify: files_moved + errors == total_files_discovered
        total_accounted = stats.files_moved + stats.errors
        
        assert total_accounted == total_files_discovered, \
            f"File coverage mismatch: {stats.files_moved} moved + {stats.errors} errors = {total_accounted}, but {total_files_discovered} files were discovered"
        
        # Additional verification: count actual files in Scrubbed folder (recursively)
        files_in_scrubbed = []
        if organizer.scrubbed_path.exists():
            for item in organizer.scrubbed_path.rglob("*"):
                if item.is_file():
                    files_in_scrubbed.append(item)
        
        # The number of files in Scrubbed should equal files_moved
        assert len(files_in_scrubbed) == stats.files_moved, \
            f"Files in Scrubbed folder ({len(files_in_scrubbed)}) doesn't match files_moved ({stats.files_moved})"



@settings(max_examples=100)
@given(
    # Generate a random subset of categories (at least 1, at most all 6)
    categories_with_files=st.lists(
        st.sampled_from([
            FileCategory.IMAGE,
            FileCategory.VIDEO,
            FileCategory.MARKDOWN,
            FileCategory.DOCUMENT,
            FileCategory.DEVELOPMENT,
            FileCategory.OTHER
        ]),
        min_size=1,
        max_size=6,
        unique=True
    ),
    files_per_category=st.integers(min_value=1, max_value=5)
)
def test_category_folder_creation_property(categories_with_files, files_per_category):
    """
    **Feature: unknown-file-handling, Property 6: Category folder creation**
    **Validates: Requirements 1.2, 3.4**
    
    For any file category with at least one file to move, the system SHALL create
    the corresponding category folder in the Scrubbed directory.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        classifier = FileClassifier()
        organizer = FolderOrganizer(root, classifier, dry_run=False)
        
        # Map categories to extensions
        category_to_ext = {
            FileCategory.IMAGE: ".jpg",
            FileCategory.VIDEO: ".mp4",
            FileCategory.MARKDOWN: ".md",
            FileCategory.DOCUMENT: ".pdf",
            FileCategory.DEVELOPMENT: ".py",
            FileCategory.OTHER: ".xyz"  # Unknown extension
        }
        
        # Create files for each selected category
        created_categories = set()
        for category in categories_with_files:
            ext = category_to_ext[category]
            for i in range(files_per_category):
                file_path = root / f"file_{category.name}_{i}{ext}"
                file_path.write_text(f"content for {category.name}")
            created_categories.add(category)
        
        # Organize files
        stats = organizer.organize()
        
        # Verify: For each category with files, the corresponding folder was created
        for category in created_categories:
            category_dir = organizer.scrubbed_path / category.value
            
            assert category_dir.exists(), \
                f"Category folder '{category.value}' should exist for category {category.name}"
            
            assert category_dir.is_dir(), \
                f"'{category.value}' should be a directory, not a file"
            
            # Verify files were actually moved to this category folder
            files_in_category = list(category_dir.glob("*"))
            assert len(files_in_category) >= files_per_category, \
                f"Category folder '{category.value}' should contain at least {files_per_category} files, found {len(files_in_category)}"
        
        # Additional verification: No extra category folders should be created
        # (only folders for categories that have files)
        all_category_folders = [item for item in organizer.scrubbed_path.iterdir() if item.is_dir()]
        
        # Extract just the folder names
        created_folder_names = {folder.name for folder in all_category_folders}
        expected_folder_names = {category.value for category in created_categories}
        
        # Handle nested paths (e.g., "Docs/Markdown" creates "Docs" folder)
        # Extract top-level folder names from expected categories
        expected_top_level = set()
        for cat_value in expected_folder_names:
            top_level = cat_value.split('/')[0]
            expected_top_level.add(top_level)
        
        # Verify all created folders correspond to categories with files
        for folder_name in created_folder_names:
            assert folder_name in expected_top_level, \
                f"Unexpected folder '{folder_name}' created in Scrubbed directory"
