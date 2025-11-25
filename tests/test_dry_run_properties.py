"""Property-based tests for dry-run mode functionality."""

import pytest
from pathlib import Path
import tempfile
import shutil
from hypothesis import given, strategies as st, settings

from scrubb.file_classifier import FileClassifier, FileCategory
from scrubb.folder_organizer import FolderOrganizer


# Strategy for generating file extensions
@st.composite
def file_extensions(draw):
    """Generate valid file extensions for testing."""
    known_extensions = [
        ".jpg", ".png", ".gif", ".mp4", ".avi", ".md", ".txt", ".pdf",
        ".py", ".js", ".html", ".css", ".json"
    ]
    unknown_extensions = [".xyz", ".abc", ".unknown", ".test"]
    
    extension_type = draw(st.sampled_from(["known", "unknown"]))
    if extension_type == "known":
        return draw(st.sampled_from(known_extensions))
    else:
        return draw(st.sampled_from(unknown_extensions))


@st.composite
def directory_structure(draw):
    """Generate a random directory structure with files."""
    # Windows reserved names that cannot be used as directory names
    WINDOWS_RESERVED = ['CON', 'PRN', 'AUX', 'NUL', 'COM1', 'COM2', 'COM3', 'COM4', 
                        'COM5', 'COM6', 'COM7', 'COM8', 'COM9', 'LPT1', 'LPT2', 
                        'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9']
    
    # Generate number of files (1-20)
    num_files = draw(st.integers(min_value=1, max_value=20))
    
    # Generate file names with extensions (ASCII only for Windows compatibility)
    files = []
    for _ in range(num_files):
        # Generate filename with ASCII characters only
        name = draw(st.text(
            alphabet="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789",
            min_size=1,
            max_size=10
        ).filter(lambda x: x.upper() not in WINDOWS_RESERVED))
        ext = draw(file_extensions())
        files.append(f"{name}{ext}")
    
    # Generate subdirectory structure (0-3 levels deep)
    num_subdirs = draw(st.integers(min_value=0, max_value=3))
    subdirs = []
    for _ in range(num_subdirs):
        subdir_name = draw(st.text(
            alphabet="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789",
            min_size=1,
            max_size=8
        ).filter(lambda x: x.upper() not in WINDOWS_RESERVED))
        subdirs.append(subdir_name)
    
    return {"files": files, "subdirs": subdirs}


def create_test_structure(root_path: Path, structure: dict):
    """Create a test directory structure on disk."""
    # Create subdirectories
    for subdir in structure["subdirs"]:
        subdir_path = root_path / subdir
        subdir_path.mkdir(exist_ok=True)
    
    # Create files in root and subdirectories
    for i, filename in enumerate(structure["files"]):
        # Distribute files across root and subdirectories
        if structure["subdirs"] and i % 2 == 0:
            # Place in a subdirectory
            subdir = structure["subdirs"][i % len(structure["subdirs"])]
            file_path = root_path / subdir / filename
        else:
            # Place in root
            file_path = root_path / filename
        
        # Create the file
        file_path.write_text(f"Test content for {filename}")


def capture_filesystem_state(root_path: Path) -> dict:
    """Capture the current state of the filesystem."""
    state = {
        "files": set(),
        "directories": set()
    }
    
    for item in root_path.rglob("*"):
        if item.is_file():
            state["files"].add(item.relative_to(root_path))
        elif item.is_dir():
            state["directories"].add(item.relative_to(root_path))
    
    return state


class TestDryRunNoModifications:
    """Property tests for ensuring dry-run makes no file system modifications."""
    
    @settings(max_examples=100)
    @given(structure=directory_structure())
    def test_no_file_system_modifications(self, structure):
        """
        **Feature: dry-run-mode, Property 1: No file system modifications in dry-run mode**
        **Validates: Requirements 1.2, 1.3, 1.4**
        
        For any dry-run execution, the system should not create directories,
        move files, or delete directories.
        """
        # Create temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            root_path = Path(temp_dir)
            
            # Create test structure
            create_test_structure(root_path, structure)
            
            # Capture initial state
            initial_state = capture_filesystem_state(root_path)
            
            # Run dry-run mode
            classifier = FileClassifier()
            organizer = FolderOrganizer(root_path, classifier, dry_run=True)
            stats = organizer.organize()
            
            # Capture final state
            final_state = capture_filesystem_state(root_path)
            
            # Verify no changes were made
            assert initial_state["files"] == final_state["files"], \
                "Files were modified during dry-run"
            assert initial_state["directories"] == final_state["directories"], \
                "Directories were modified during dry-run"
            
            # Verify Scrubbed folder was not created
            scrubbed_path = root_path / "Scrubbed"
            assert not scrubbed_path.exists(), \
                "Scrubbed folder was created during dry-run"


class TestClassificationConsistency:
    """Property tests for classification consistency between dry-run and actual mode."""
    
    @settings(max_examples=100)
    @given(
        filenames=st.lists(
            st.tuples(
                st.text(
                    alphabet="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789",
                    min_size=1,
                    max_size=10
                ),
                file_extensions()
            ),
            min_size=1,
            max_size=15,
            unique_by=lambda x: f"{x[0]}{x[1]}".lower()  # Ensure case-insensitive uniqueness for Windows
        )
    )
    def test_classification_consistency(self, filenames):
        """
        **Feature: dry-run-mode, Property 9: Classification consistency**
        **Validates: Requirements 10.1**
        
        For any file, the dry-run mode should use the same classification logic
        as actual execution, producing identical categorization results.
        """
        # Create temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            root_path = Path(temp_dir)
            
            # Create test files
            created_files = []
            for name, ext in filenames:
                filename = f"{name}{ext}"
                file_path = root_path / filename
                file_path.write_text(f"Test content")
                created_files.append(file_path)
            
            # Classify files using classifier directly
            classifier = FileClassifier()
            direct_classifications = {}
            for file_path in created_files:
                category = classifier.classify(file_path)
                direct_classifications[file_path.name] = category
            
            # Run dry-run mode and get classifications from operations
            organizer = FolderOrganizer(root_path, classifier, dry_run=True)
            stats = organizer.organize()
            
            dry_run_classifications = {}
            for op in stats.file_operations:
                dry_run_classifications[op.source.name] = op.category
            
            # Also check skipped files
            for skipped in stats.skipped_files:
                dry_run_classifications[skipped.path.name] = FileCategory.UNKNOWN
            
            # Verify classifications match
            for filename, direct_category in direct_classifications.items():
                if direct_category == FileCategory.UNKNOWN:
                    # Should be in skipped files
                    assert filename in dry_run_classifications, \
                        f"File {filename} not found in dry-run results"
                    assert dry_run_classifications[filename] == FileCategory.UNKNOWN, \
                        f"File {filename} classification mismatch"
                else:
                    # Should be in file operations
                    assert filename in dry_run_classifications, \
                        f"File {filename} not found in dry-run operations"
                    assert dry_run_classifications[filename] == direct_category, \
                        f"File {filename} classification mismatch: " \
                        f"expected {direct_category}, got {dry_run_classifications[filename]}"


class TestConflictResolutionConsistency:
    """Property tests for conflict resolution consistency."""
    
    @settings(max_examples=100)
    @given(
        base_name=st.text(
            alphabet="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789",
            min_size=1,
            max_size=10
        ),
        num_duplicates=st.integers(min_value=2, max_value=5)
    )
    def test_conflict_resolution_consistency(self, base_name, num_duplicates):
        """
        **Feature: dry-run-mode, Property 10: Conflict resolution consistency**
        **Validates: Requirements 10.2**
        
        For any name conflict scenario, the dry-run mode should use the same
        conflict resolution logic as actual execution, producing identical
        resolved filenames.
        """
        # Create temporary directories for both modes
        with tempfile.TemporaryDirectory() as temp_dir1, \
             tempfile.TemporaryDirectory() as temp_dir2:
            
            dry_run_root = Path(temp_dir1)
            actual_root = Path(temp_dir2)
            
            # Create duplicate files in both directories
            filename = f"{base_name}.txt"
            for i in range(num_duplicates):
                dry_file = dry_run_root / f"subdir{i}" / filename
                actual_file = actual_root / f"subdir{i}" / filename
                
                dry_file.parent.mkdir(exist_ok=True)
                actual_file.parent.mkdir(exist_ok=True)
                
                dry_file.write_text(f"Content {i}")
                actual_file.write_text(f"Content {i}")
            
            # Run dry-run mode
            classifier = FileClassifier()
            dry_organizer = FolderOrganizer(dry_run_root, classifier, dry_run=True)
            dry_stats = dry_organizer.organize()
            
            # Run actual mode
            actual_organizer = FolderOrganizer(actual_root, classifier, dry_run=False)
            actual_stats = actual_organizer.organize()
            
            # Extract resolved names from dry-run
            dry_run_destinations = set()
            for op in dry_stats.file_operations:
                if op.source.name == filename:
                    dry_run_destinations.add(op.destination.name)
            
            # Extract resolved names from actual execution
            actual_destinations = set()
            scrubbed_path = actual_root / "Scrubbed"
            if scrubbed_path.exists():
                for file_path in scrubbed_path.rglob("*"):
                    if file_path.is_file() and base_name in file_path.name:
                        actual_destinations.add(file_path.name)
            
            # Verify same number of files
            assert len(dry_run_destinations) == len(actual_destinations), \
                f"Different number of files: dry-run={len(dry_run_destinations)}, " \
                f"actual={len(actual_destinations)}"
            
            # Verify conflict resolution patterns match
            # Both should have one original and (n-1) with _1, _2, etc.
            assert dry_run_destinations == actual_destinations, \
                f"Conflict resolution mismatch: dry-run={dry_run_destinations}, " \
                f"actual={actual_destinations}"


class TestEmptyDirectoryDetectionConsistency:
    """Property tests for empty directory detection consistency."""
    
    @settings(max_examples=100)
    @given(
        num_subdirs=st.integers(min_value=1, max_value=5),
        files_per_dir=st.integers(min_value=1, max_value=3)
    )
    def test_empty_directory_detection_consistency(self, num_subdirs, files_per_dir):
        """
        **Feature: dry-run-mode, Property 11: Empty directory detection consistency**
        **Validates: Requirements 10.3**
        
        For any directory structure, the dry-run mode should identify the same
        empty directories that would be removed in actual execution.
        """
        # Create temporary directories for both modes
        with tempfile.TemporaryDirectory() as temp_dir1, \
             tempfile.TemporaryDirectory() as temp_dir2:
            
            dry_run_root = Path(temp_dir1)
            actual_root = Path(temp_dir2)
            
            # Create identical directory structures
            for i in range(num_subdirs):
                subdir_name = f"subdir_{i}"
                dry_subdir = dry_run_root / subdir_name
                actual_subdir = actual_root / subdir_name
                
                dry_subdir.mkdir()
                actual_subdir.mkdir()
                
                # Create files in each subdirectory
                for j in range(files_per_dir):
                    filename = f"file_{j}.txt"
                    (dry_subdir / filename).write_text(f"Content {j}")
                    (actual_subdir / filename).write_text(f"Content {j}")
            
            # Run dry-run mode
            classifier = FileClassifier()
            dry_organizer = FolderOrganizer(dry_run_root, classifier, dry_run=True)
            dry_stats = dry_organizer.organize()
            
            # Get directories that would be removed
            dry_run_empty_dirs = set(
                str(d.relative_to(dry_run_root)) for d in dry_stats.directories_to_remove
            )
            
            # Run actual mode
            actual_organizer = FolderOrganizer(actual_root, classifier, dry_run=False)
            actual_stats = actual_organizer.organize()
            
            # Find which directories were actually removed
            actual_empty_dirs = set()
            for i in range(num_subdirs):
                subdir_name = f"subdir_{i}"
                subdir_path = actual_root / subdir_name
                if not subdir_path.exists():
                    actual_empty_dirs.add(subdir_name)
            
            # Verify same directories identified
            assert dry_run_empty_dirs == actual_empty_dirs, \
                f"Empty directory detection mismatch: " \
                f"dry-run={dry_run_empty_dirs}, actual={actual_empty_dirs}"


class TestCompleteFileOperationReporting:
    """Property tests for complete file operation reporting in output."""
    
    @settings(max_examples=100)
    @given(structure=directory_structure())
    def test_complete_file_operation_reporting(self, structure):
        """
        **Feature: dry-run-mode, Property 2: Complete file operation reporting**
        **Validates: Requirements 2.1, 2.2, 2.3**
        
        For any set of files in the target directory, the dry-run output should
        list all files that would be moved with their source paths and destination
        categories.
        """
        from scrubb.folder_organizer import DryRunFormatter
        
        # Create temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            root_path = Path(temp_dir)
            
            # Create test structure
            create_test_structure(root_path, structure)
            
            # Run dry-run mode
            classifier = FileClassifier()
            organizer = FolderOrganizer(root_path, classifier, dry_run=True)
            stats = organizer.organize()
            
            # Format output
            output = DryRunFormatter.format_output(stats, root_path)
            
            # Verify all moveable files are listed in output
            for op in stats.file_operations:
                # Check source filename is in output
                assert op.source.name in output, \
                    f"Source file {op.source.name} not found in output"
                
                # Check destination path or category is in output
                # (destination path should be present)
                assert str(op.destination) in output or op.destination.name in output, \
                    f"Destination for {op.source.name} not found in output"
            
            # Verify file operations section exists if there are operations
            if stats.file_operations:
                assert " FILE OPERATIONS" in output, \
                    "FILE OPERATIONS section missing from output"
            
            # Verify all files are accounted for (either moved or skipped)
            all_files = []
            for item in root_path.rglob("*"):
                if item.is_file():
                    all_files.append(item)
            
            files_in_output = len(stats.file_operations) + len(stats.skipped_files)
            assert files_in_output == len(all_files), \
                f"Not all files accounted for: {files_in_output} in output, " \
                f"{len(all_files)} total files"


class TestAccurateStatisticsReporting:
    """Property tests for accurate statistics reporting in output."""
    
    @settings(max_examples=100)
    @given(structure=directory_structure())
    def test_accurate_statistics_reporting(self, structure):
        """
        **Feature: dry-run-mode, Property 3: Accurate statistics reporting**
        **Validates: Requirements 3.1, 3.2, 3.3, 3.5**
        
        For any dry-run execution, the displayed statistics (total files,
        per-category counts, empty directories) should accurately reflect
        what would happen in actual execution.
        """
        from scrubb.folder_organizer import DryRunFormatter
        
        # Create temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            root_path = Path(temp_dir)
            
            # Create test structure
            create_test_structure(root_path, structure)
            
            # Run dry-run mode
            classifier = FileClassifier()
            organizer = FolderOrganizer(root_path, classifier, dry_run=True)
            stats = organizer.organize()
            
            # Format output
            output = DryRunFormatter.format_output(stats, root_path)
            
            # Verify total files to move is in output
            assert f"Files to move: {stats.files_to_move}" in output, \
                "Total files to move not correctly displayed"
            
            # Verify per-category counts are in output
            for category, count in stats.files_by_category.items():
                assert f"{category}: {count} files" in output, \
                    f"Category {category} count not correctly displayed"
            
            # Verify empty directories count is in output
            assert f"Empty directories to remove: {stats.empty_folders_to_remove}" in output, \
                "Empty directories count not correctly displayed"
            
            # Verify skipped files count is in output
            assert f"Files to skip: {len(stats.skipped_files)}" in output, \
                "Skipped files count not correctly displayed"
            
            # Verify statistics are consistent
            total_from_categories = sum(stats.files_by_category.values())
            assert stats.files_to_move == total_from_categories, \
                f"Inconsistent statistics: files_to_move={stats.files_to_move}, " \
                f"sum of categories={total_from_categories}"


class TestConflictDetectionAndReporting:
    """Property tests for conflict detection and reporting in output."""
    
    @settings(max_examples=100)
    @given(
        base_name=st.text(
            alphabet="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789",
            min_size=1,
            max_size=10
        ),
        num_duplicates=st.integers(min_value=2, max_value=5)
    )
    def test_conflict_detection_and_reporting(self, base_name, num_duplicates):
        """
        **Feature: dry-run-mode, Property 4: Conflict detection and reporting**
        **Validates: Requirements 4.1, 4.2, 4.3, 4.4**
        
        For any files that would have name conflicts, the dry-run should identify
        them, show original and resolved names, and group them by category.
        """
        from scrubb.folder_organizer import DryRunFormatter
        
        # Create temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            root_path = Path(temp_dir)
            
            # Create duplicate files with same name in different subdirectories
            filename = f"{base_name}.txt"
            for i in range(num_duplicates):
                subdir = root_path / f"subdir_{i}"
                subdir.mkdir()
                file_path = subdir / filename
                file_path.write_text(f"Content {i}")
            
            # Run dry-run mode
            classifier = FileClassifier()
            organizer = FolderOrganizer(root_path, classifier, dry_run=True)
            stats = organizer.organize()
            
            # Format output
            output = DryRunFormatter.format_output(stats, root_path)
            
            # Verify conflicts are detected
            if len(stats.conflicts) > 0:
                assert "  NAME CONFLICTS" in output, \
                    "NAME CONFLICTS section missing when conflicts exist"
                
                # Verify each conflict is reported
                for conflict in stats.conflicts:
                    # Check original name is in output
                    assert conflict.original_name in output, \
                        f"Original name {conflict.original_name} not in output"
                    
                    # Check resolved name is in output
                    assert conflict.resolved_name in output, \
                        f"Resolved name {conflict.resolved_name} not in output"
                    
                    # Check category is in output
                    assert f"Category: {conflict.category}" in output, \
                        f"Category {conflict.category} not in conflict output"
            
            # Verify conflict count in summary
            assert f"Potential conflicts: {len(stats.conflicts)}" in output, \
                "Conflict count not in summary"


class TestDirectoryCreationReporting:
    """Property tests for directory creation reporting in output."""
    
    @settings(max_examples=100)
    @given(structure=directory_structure())
    def test_directory_creation_reporting(self, structure):
        """
        **Feature: dry-run-mode, Property 5: Directory creation reporting**
        **Validates: Requirements 5.1, 5.2, 5.4**
        
        For any categories that would receive files, the dry-run should list
        all directories that would be created including the Scrubbed folder
        and category subdirectories.
        """
        from scrubb.folder_organizer import DryRunFormatter
        
        # Create temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            root_path = Path(temp_dir)
            
            # Create test structure
            create_test_structure(root_path, structure)
            
            # Run dry-run mode
            classifier = FileClassifier()
            organizer = FolderOrganizer(root_path, classifier, dry_run=True)
            stats = organizer.organize()
            
            # Format output
            output = DryRunFormatter.format_output(stats, root_path)
            
            # Verify directories to create section exists if there are directories
            if stats.directories_to_create:
                assert " DIRECTORIES TO CREATE" in output, \
                    "DIRECTORIES TO CREATE section missing"
                
                # Verify each directory is listed
                for dir_path in stats.directories_to_create:
                    # Directory path should be in output
                    assert str(dir_path) in output or dir_path.name in output, \
                        f"Directory {dir_path} not found in output"
            
            # Verify directory count in summary
            assert f"Directories to create: {len(stats.directories_to_create)}" in output, \
                "Directory creation count not in summary"


class TestSkippedFileReporting:
    """Property tests for skipped file reporting in output."""
    
    @settings(max_examples=100)
    @given(
        num_unknown=st.integers(min_value=1, max_value=10)
    )
    def test_skipped_file_reporting(self, num_unknown):
        """
        **Feature: dry-run-mode, Property 6: Skipped file reporting**
        **Validates: Requirements 6.1, 6.2, 6.3**
        
        For any files with unknown extensions, the dry-run should list them
        with their paths and reasons for skipping.
        """
        from scrubb.folder_organizer import DryRunFormatter
        
        # Create temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            root_path = Path(temp_dir)
            
            # Create files with unknown extensions
            unknown_files = []
            for i in range(num_unknown):
                filename = f"unknown_{i}.xyz"
                file_path = root_path / filename
                file_path.write_text(f"Content {i}")
                unknown_files.append(filename)
            
            # Run dry-run mode
            classifier = FileClassifier()
            organizer = FolderOrganizer(root_path, classifier, dry_run=True)
            stats = organizer.organize()
            
            # Format output
            output = DryRunFormatter.format_output(stats, root_path)
            
            # Verify skipped files section exists
            if stats.skipped_files:
                assert "⏭  SKIPPED FILES" in output, \
                    "SKIPPED FILES section missing"
                
                # Verify each skipped file is listed
                for skipped in stats.skipped_files:
                    # Filename should be in output
                    assert skipped.path.name in output, \
                        f"Skipped file {skipped.path.name} not in output"
                    
                    # Reason should be in output
                    assert skipped.reason in output, \
                        f"Skip reason '{skipped.reason}' not in output"
            
            # Verify skipped files count in summary
            assert f"Files to skip: {len(stats.skipped_files)}" in output, \
                "Skipped files count not in summary"


class TestPotentialErrorDetection:
    """Property tests for potential error detection in output."""
    
    @settings(max_examples=100)
    @given(
        num_files=st.integers(min_value=1, max_value=10)
    )
    def test_potential_error_detection(self, num_files):
        """
        **Feature: dry-run-mode, Property 7: Potential error detection**
        **Validates: Requirements 8.1, 8.3**
        
        For any files that might be inaccessible, the dry-run should identify
        and list potential permission issues with an accurate error count.
        """
        from scrubb.folder_organizer import DryRunFormatter
        
        # Create temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            root_path = Path(temp_dir)
            
            # Create normal files (we can't easily simulate permission errors
            # in a cross-platform way, so we test the reporting mechanism)
            for i in range(num_files):
                filename = f"file_{i}.txt"
                file_path = root_path / filename
                file_path.write_text(f"Content {i}")
            
            # Run dry-run mode
            classifier = FileClassifier()
            organizer = FolderOrganizer(root_path, classifier, dry_run=True)
            stats = organizer.organize()
            
            # Format output
            output = DryRunFormatter.format_output(stats, root_path)
            
            # Verify potential errors section or no errors message
            if stats.potential_errors:
                assert " POTENTIAL ERRORS" in output, \
                    "POTENTIAL ERRORS section missing when errors exist"
                
                # Verify each error is listed
                for error in stats.potential_errors:
                    assert error in output, \
                        f"Error '{error}' not in output"
            else:
                assert " No potential errors detected" in output, \
                    "No errors message missing when no errors detected"


class TestOutputOrganization:
    """Property tests for output organization and formatting."""
    
    @settings(max_examples=100)
    @given(structure=directory_structure())
    def test_output_organization(self, structure):
        """
        **Feature: dry-run-mode, Property 8: Output organization**
        **Validates: Requirements 9.1, 9.4**
        
        For any dry-run execution, the output should be organized into clear
        sections with consistent formatting throughout.
        """
        from scrubb.folder_organizer import DryRunFormatter
        
        # Create temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            root_path = Path(temp_dir)
            
            # Create test structure
            create_test_structure(root_path, structure)
            
            # Run dry-run mode
            classifier = FileClassifier()
            organizer = FolderOrganizer(root_path, classifier, dry_run=True)
            stats = organizer.organize()
            
            # Format output
            output = DryRunFormatter.format_output(stats, root_path)
            
            # Verify required sections are present
            required_sections = [
                "DRY RUN PREVIEW",
                " SUMMARY",
                "This was a DRY RUN"
            ]
            
            for section in required_sections:
                assert section in output, \
                    f"Required section '{section}' missing from output"
            
            # Verify header and footer formatting
            lines = output.split("\n")
            
            # Check for separator lines (70 equals signs)
            separator = "=" * 70
            assert separator in output, \
                "Separator lines missing from output"
            
            # Verify consistent formatting
            # All section headers should use emoji or clear markers
            section_markers = ["", "", "", "", "", "⏭", "", "", ""]
            found_markers = [marker for marker in section_markers if marker in output]
            
            # At least some section markers should be present
            assert len(found_markers) > 0, \
                "No section markers found in output"


class TestDryRunPredictionAccuracy:
    """Property tests for dry-run prediction accuracy (round-trip property)."""
    
    @settings(max_examples=100)
    @given(structure=directory_structure())
    def test_dry_run_prediction_accuracy(self, structure):
        """
        **Feature: dry-run-mode, Property 12: Dry-run prediction accuracy**
        **Validates: Requirements 10.4**
        
        For any directory structure, if we run dry-run mode followed by actual
        execution, the actual results should match the dry-run predictions for
        all operations.
        """
        # Create two temporary directories - one for dry-run, one for actual
        with tempfile.TemporaryDirectory() as temp_dir1, \
             tempfile.TemporaryDirectory() as temp_dir2:
            
            dry_run_root = Path(temp_dir1)
            actual_root = Path(temp_dir2)
            
            # Create identical test structures in both directories
            create_test_structure(dry_run_root, structure)
            create_test_structure(actual_root, structure)
            
            # Run dry-run mode to capture predictions
            classifier = FileClassifier()
            dry_organizer = FolderOrganizer(dry_run_root, classifier, dry_run=True)
            dry_stats = dry_organizer.organize()
            
            # Run actual mode on the copy
            actual_organizer = FolderOrganizer(actual_root, classifier, dry_run=False)
            actual_stats = actual_organizer.organize()
            
            # Verify file destinations match predictions
            # Build a map of source filename to destination for dry-run
            dry_run_destinations = {}
            for op in dry_stats.file_operations:
                # Use relative path from root for comparison
                source_name = op.source.name
                dest_relative = op.destination.relative_to(dry_run_root / "Scrubbed")
                dry_run_destinations[source_name] = str(dest_relative)
            
            # Build a map of actual destinations
            actual_destinations = {}
            scrubbed_path = actual_root / "Scrubbed"
            if scrubbed_path.exists():
                for file_path in scrubbed_path.rglob("*"):
                    if file_path.is_file():
                        # Get the relative path from Scrubbed folder
                        dest_relative = file_path.relative_to(scrubbed_path)
                        # Find the original filename (without _N suffix if conflict)
                        filename = file_path.name
                        actual_destinations[filename] = str(dest_relative)
            
            # Verify number of files moved matches prediction
            assert dry_stats.files_to_move == actual_stats.files_moved, \
                f"File count mismatch: predicted {dry_stats.files_to_move}, " \
                f"actual {actual_stats.files_moved}"
            
            # Verify files by category matches prediction
            for category, predicted_count in dry_stats.files_by_category.items():
                actual_count = actual_stats.files_by_category.get(category, 0)
                assert predicted_count == actual_count, \
                    f"Category {category} count mismatch: " \
                    f"predicted {predicted_count}, actual {actual_count}"
            
            # Verify conflict resolutions match predictions
            # For each conflict in dry-run, verify the resolved name exists in actual
            for conflict in dry_stats.conflicts:
                resolved_name = conflict.resolved_name
                # Check that this resolved name exists in actual destinations
                assert resolved_name in actual_destinations, \
                    f"Predicted conflict resolution {resolved_name} not found in actual results"
            
            # Verify empty directories removed match predictions
            assert dry_stats.empty_folders_to_remove == actual_stats.empty_folders_removed, \
                f"Empty directory count mismatch: " \
                f"predicted {dry_stats.empty_folders_to_remove}, " \
                f"actual {actual_stats.empty_folders_removed}"
            
            # Verify that all predicted directories were created
            for predicted_dir in dry_stats.directories_to_create:
                # Convert to relative path from root
                relative_dir = predicted_dir.relative_to(dry_run_root)
                actual_dir = actual_root / relative_dir
                assert actual_dir.exists(), \
                    f"Predicted directory {relative_dir} was not created in actual execution"
            
            # Verify that predicted empty directories were actually removed
            for predicted_empty_dir in dry_stats.directories_to_remove:
                # Convert to relative path from root
                relative_dir = predicted_empty_dir.relative_to(dry_run_root)
                actual_dir = actual_root / relative_dir
                assert not actual_dir.exists(), \
                    f"Predicted empty directory {relative_dir} was not removed in actual execution"



class TestNoFilesSkippedForUnknownExtensions:
    """Property tests for ensuring unknown extension files are not skipped."""
    
    @settings(max_examples=100)
    @given(
        num_unknown=st.integers(min_value=1, max_value=10),
        num_known=st.integers(min_value=0, max_value=10)
    )
    def test_no_files_skipped_for_unknown_extensions(self, num_unknown, num_known):
        """
        **Feature: unknown-file-handling, Property 3: No files skipped for unknown extensions**
        **Validates: Requirements 1.3, 1.4**
        
        For any file classified as FileCategory.OTHER, the FolderOrganizer SHALL
        include it in file operations and SHALL NOT add it to the skipped files list.
        """
        # Create temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            root_path = Path(temp_dir)
            
            # Create files with unknown extensions
            unknown_files = []
            for i in range(num_unknown):
                filename = f"unknown_{i}.xyz"
                file_path = root_path / filename
                file_path.write_text(f"Content {i}")
                unknown_files.append(filename)
            
            # Create files with known extensions
            known_extensions = [".txt", ".jpg", ".py", ".md", ".pdf"]
            known_files = []
            for i in range(num_known):
                ext = known_extensions[i % len(known_extensions)]
                filename = f"known_{i}{ext}"
                file_path = root_path / filename
                file_path.write_text(f"Content {i}")
                known_files.append(filename)
            
            # Run dry-run mode
            classifier = FileClassifier()
            organizer = FolderOrganizer(root_path, classifier, dry_run=True)
            stats = organizer.organize()
            
            # Verify no files with unknown extensions are in skipped_files
            skipped_filenames = [skipped.path.name for skipped in stats.skipped_files]
            for unknown_file in unknown_files:
                assert unknown_file not in skipped_filenames, \
                    f"File with unknown extension {unknown_file} should not be skipped"
            
            # Verify all unknown extension files are in file_operations
            operation_filenames = [op.source.name for op in stats.file_operations]
            for unknown_file in unknown_files:
                assert unknown_file in operation_filenames, \
                    f"File with unknown extension {unknown_file} should be in file operations"
            
            # Verify unknown extension files are categorized as OTHER
            for op in stats.file_operations:
                if op.source.name in unknown_files:
                    assert op.category == FileCategory.OTHER, \
                        f"File {op.source.name} should be categorized as OTHER, got {op.category}"
            
            # Verify "Other" category appears in statistics if unknown files exist
            if num_unknown > 0:
                assert "Other" in stats.files_by_category, \
                    "Other category should appear in statistics when unknown files exist"
                assert stats.files_by_category["Other"] == num_unknown, \
                    f"Other category count should be {num_unknown}, got {stats.files_by_category.get('Other', 0)}"
            
            # Verify total files to move includes unknown extension files
            total_files = num_unknown + num_known
            assert stats.files_to_move == total_files, \
                f"Total files to move should be {total_files}, got {stats.files_to_move}"


class TestDryRunConsistency:
    """Property tests for dry-run consistency with actual mode."""
    
    @settings(max_examples=100)
    @given(structure=directory_structure())
    def test_dry_run_consistency(self, structure):
        """
        **Feature: unknown-file-handling, Property 5: Dry-run consistency**
        **Validates: Requirements 1.3, 2.1**
        
        For any directory, running in dry-run mode SHALL produce statistics that
        match what would happen in actual mode, including OTHER category files.
        """
        # Create two temporary directories - one for dry-run, one for actual
        with tempfile.TemporaryDirectory() as temp_dir1, \
             tempfile.TemporaryDirectory() as temp_dir2:
            
            dry_run_root = Path(temp_dir1)
            actual_root = Path(temp_dir2)
            
            # Create identical test structures in both directories
            create_test_structure(dry_run_root, structure)
            create_test_structure(actual_root, structure)
            
            # Run dry-run mode to capture predictions
            classifier = FileClassifier()
            dry_organizer = FolderOrganizer(dry_run_root, classifier, dry_run=True)
            dry_stats = dry_organizer.organize()
            
            # Run actual mode on the copy
            actual_organizer = FolderOrganizer(actual_root, classifier, dry_run=False)
            actual_stats = actual_organizer.organize()
            
            # Verify files_to_move matches files_moved (accounting for errors)
            # In ideal case with no errors, they should match exactly
            if actual_stats.errors == 0:
                assert dry_stats.files_to_move == actual_stats.files_moved, \
                    f"File count mismatch: dry-run predicted {dry_stats.files_to_move}, " \
                    f"actual moved {actual_stats.files_moved}"
            else:
                # With errors, files_moved should be less than or equal to predicted
                assert actual_stats.files_moved <= dry_stats.files_to_move, \
                    f"Actual files moved ({actual_stats.files_moved}) should not exceed " \
                    f"dry-run prediction ({dry_stats.files_to_move})"
            
            # Verify category counts match (including OTHER category)
            for category, predicted_count in dry_stats.files_by_category.items():
                actual_count = actual_stats.files_by_category.get(category, 0)
                
                # Account for potential errors in actual execution
                if actual_stats.errors == 0:
                    assert predicted_count == actual_count, \
                        f"Category '{category}' count mismatch: " \
                        f"dry-run predicted {predicted_count}, actual {actual_count}"
                else:
                    # With errors, actual count should be less than or equal to predicted
                    assert actual_count <= predicted_count, \
                        f"Category '{category}' actual count ({actual_count}) should not exceed " \
                        f"dry-run prediction ({predicted_count})"
            
            # Verify all categories in actual mode were predicted in dry-run
            for category in actual_stats.files_by_category.keys():
                assert category in dry_stats.files_by_category, \
                    f"Category '{category}' appeared in actual mode but was not predicted in dry-run"
            
            # Verify empty directories count matches
            if actual_stats.errors == 0:
                assert dry_stats.empty_folders_to_remove == actual_stats.empty_folders_removed, \
                    f"Empty directory count mismatch: " \
                    f"dry-run predicted {dry_stats.empty_folders_to_remove}, " \
                    f"actual removed {actual_stats.empty_folders_removed}"
            
            # Verify that if OTHER category was predicted, it exists in actual results
            if "Other" in dry_stats.files_by_category:
                assert "Other" in actual_stats.files_by_category, \
                    "OTHER category was predicted in dry-run but not found in actual results"
                
                # Verify OTHER folder was created
                other_folder = actual_root / "Scrubbed" / "Other"
                assert other_folder.exists(), \
                    "OTHER folder should be created when OTHER category files are present"


class TestStatisticsCompleteness:
    """Property tests for statistics completeness with OTHER category."""
    
    @settings(max_examples=100)
    @given(
        num_unknown=st.integers(min_value=1, max_value=10),
        num_known=st.integers(min_value=0, max_value=10)
    )
    def test_statistics_completeness_dry_run(self, num_unknown, num_known):
        """
        **Feature: unknown-file-handling, Property 4: Statistics completeness**
        **Validates: Requirements 1.5, 2.2**
        
        For any organization operation (dry-run or actual), the statistics SHALL
        include a count for the "Other" category if any files with unknown
        extensions were processed.
        """
        # Create temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            root_path = Path(temp_dir)
            
            # Create files with unknown extensions
            unknown_files = []
            for i in range(num_unknown):
                filename = f"unknown_{i}.xyz"
                file_path = root_path / filename
                file_path.write_text(f"Content {i}")
                unknown_files.append(filename)
            
            # Create files with known extensions
            known_extensions = [".txt", ".jpg", ".py", ".md", ".pdf"]
            known_files = []
            for i in range(num_known):
                ext = known_extensions[i % len(known_extensions)]
                filename = f"known_{i}{ext}"
                file_path = root_path / filename
                file_path.write_text(f"Content {i}")
                known_files.append(filename)
            
            # Run dry-run mode
            classifier = FileClassifier()
            organizer = FolderOrganizer(root_path, classifier, dry_run=True)
            stats = organizer.organize()
            
            # Verify "Other" category appears in statistics
            assert "Other" in stats.files_by_category, \
                "Other category should appear in files_by_category when unknown files exist"
            
            # Verify count is correct
            assert stats.files_by_category["Other"] == num_unknown, \
                f"Other category count should be {num_unknown}, got {stats.files_by_category.get('Other', 0)}"
            
            # Verify total count is consistent
            total_from_categories = sum(stats.files_by_category.values())
            assert stats.files_to_move == total_from_categories, \
                f"Total files to move ({stats.files_to_move}) should equal sum of categories ({total_from_categories})"
    
    @settings(max_examples=100)
    @given(
        num_unknown=st.integers(min_value=1, max_value=10),
        num_known=st.integers(min_value=0, max_value=10)
    )
    def test_statistics_completeness_actual_mode(self, num_unknown, num_known):
        """
        **Feature: unknown-file-handling, Property 4: Statistics completeness**
        **Validates: Requirements 1.5, 2.2**
        
        For any organization operation (dry-run or actual), the statistics SHALL
        include a count for the "Other" category if any files with unknown
        extensions were processed.
        """
        # Create temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            root_path = Path(temp_dir)
            
            # Create files with unknown extensions
            unknown_files = []
            for i in range(num_unknown):
                filename = f"unknown_{i}.xyz"
                file_path = root_path / filename
                file_path.write_text(f"Content {i}")
                unknown_files.append(filename)
            
            # Create files with known extensions
            known_extensions = [".txt", ".jpg", ".py", ".md", ".pdf"]
            known_files = []
            for i in range(num_known):
                ext = known_extensions[i % len(known_extensions)]
                filename = f"known_{i}{ext}"
                file_path = root_path / filename
                file_path.write_text(f"Content {i}")
                known_files.append(filename)
            
            # Run actual mode
            classifier = FileClassifier()
            organizer = FolderOrganizer(root_path, classifier, dry_run=False)
            stats = organizer.organize()
            
            # Verify "Other" category appears in statistics
            assert "Other" in stats.files_by_category, \
                "Other category should appear in files_by_category when unknown files exist"
            
            # Verify count is correct
            assert stats.files_by_category["Other"] == num_unknown, \
                f"Other category count should be {num_unknown}, got {stats.files_by_category.get('Other', 0)}"
            
            # Verify total count is consistent
            total_from_categories = sum(stats.files_by_category.values())
            assert stats.files_moved == total_from_categories, \
                f"Total files moved ({stats.files_moved}) should equal sum of categories ({total_from_categories})"
            
            # Verify "Other" folder was created
            other_folder = root_path / "Scrubbed" / "Other"
            assert other_folder.exists(), \
                "Other folder should be created in Scrubbed directory"
            
            # Verify files were actually moved to Other folder
            other_files = list(other_folder.glob("*"))
            assert len(other_files) == num_unknown, \
                f"Other folder should contain {num_unknown} files, found {len(other_files)}"
