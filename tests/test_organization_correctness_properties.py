"""Property-based tests for organization correctness.

**Feature: architectural-unification, Property 6: Simulation Accuracy**
**Validates: Requirements 6.1**

This module tests that file organization planning is correct:
- All files are accounted for in the plan
- No files are lost during planning
- The plan accurately represents what will happen
"""

import tempfile
from pathlib import Path
from typing import List, Set
import pytest
from hypothesis import given, strategies as st, settings, assume

from scrubb.business.organizer import FileOrganizer, OrganizationPlan
from scrubb.business.classifier import EnhancedFileClassifier, FileCategory
from scrubb.business.conflict_resolver import ConflictResolver
from scrubb.io.directory_operations import RealDirectoryOperations


# Mock file operations for testing
class MockFileOperations:
    """Mock file operations that don't actually move files."""
    
    def move_file(self, source: Path, dest: Path):
        """Mock move that always succeeds."""
        from scrubb.core.result import Success
        return Success(None)
    
    def file_exists(self, path: Path) -> bool:
        """Check if file exists."""
        return path.exists()


# Strategies for generating test data

@st.composite
def file_extensions(draw):
    """Generate file extensions."""
    extensions = [
        ".txt", ".md", ".pdf", ".doc", ".docx",  # Documents
        ".jpg", ".png", ".gif", ".svg", ".bmp",  # Images
        ".mp4", ".avi", ".mov", ".mkv",          # Videos
        ".py", ".js", ".ts", ".java", ".cpp",    # Development
        ".zip", ".tar", ".gz", ".rar",           # Archives
    ]
    return draw(st.sampled_from(extensions))


@st.composite
def file_names(draw):
    """Generate file names."""
    name = draw(st.text(
        alphabet="abcdefghijklmnopqrstuvwxyz0123456789_-",
        min_size=1,
        max_size=20
    ))
    ext = draw(file_extensions())
    return name + ext


@st.composite
def directory_structures(draw):
    """Generate random directory structures with files.
    
    Returns:
        Tuple of (num_files, depth, files_per_dir)
    """
    num_files = draw(st.integers(min_value=5, max_value=50))
    depth = draw(st.integers(min_value=1, max_value=4))
    files_per_dir = draw(st.integers(min_value=1, max_value=10))
    
    return (num_files, depth, files_per_dir)


def create_test_files(root: Path, num_files: int, depth: int = 3) -> List[Path]:
    """Create test files in a directory structure.
    
    Args:
        root: Root directory
        num_files: Number of files to create
        depth: Maximum depth of directory tree
        
    Returns:
        List of created file paths
    """
    created_files = []
    
    # Create nested directory structure
    dirs = [root]
    for level in range(depth):
        new_dirs = []
        for parent in dirs:
            # Create 2 subdirectories at each level
            for i in range(2):
                subdir = parent / f"level{level}_dir{i}"
                subdir.mkdir(exist_ok=True)
                new_dirs.append(subdir)
        dirs.extend(new_dirs)
    
    # Distribute files across directories
    extensions = [".txt", ".jpg", ".mp4", ".pdf", ".py", ".md", ".png", ".doc"]
    files_per_dir = max(1, num_files // len(dirs))
    
    file_count = 0
    for dir_path in dirs:
        if file_count >= num_files:
            break
        
        for i in range(files_per_dir):
            if file_count >= num_files:
                break
            
            ext = extensions[file_count % len(extensions)]
            file_path = dir_path / f"file{file_count}{ext}"
            file_path.touch()
            created_files.append(file_path)
            file_count += 1
    
    # Create any remaining files in root
    while file_count < num_files:
        ext = extensions[file_count % len(extensions)]
        file_path = root / f"file{file_count}{ext}"
        file_path.touch()
        created_files.append(file_path)
        file_count += 1
    
    return created_files


class TestOrganizationCorrectness:
    """Property tests for organization correctness.
    
    **Feature: architectural-unification, Property 6: Simulation Accuracy**
    **Validates: Requirements 6.1**
    """
    
    @settings(max_examples=50, deadline=None)
    @given(structure=directory_structures())
    def test_all_files_accounted_for_in_plan(self, structure):
        """
        **Feature: architectural-unification, Property 6: Simulation Accuracy**
        **Validates: Requirements 6.1**
        
        For any random file set, when planning organization, all files should
        be accounted for in the plan (either moved or already in scrubbed folder).
        """
        num_files, depth, _ = structure
        
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            scrubbed_folder = root / "Scrubbed"
            
            # Create test files
            created_files = create_test_files(root, num_files, depth)
            
            # Verify we created the expected number of files
            assume(len(created_files) == num_files)
            
            # Create organizer
            file_ops = MockFileOperations()
            dir_ops = RealDirectoryOperations()
            classifier = EnhancedFileClassifier()
            conflict_resolver = ConflictResolver()
            
            organizer = FileOrganizer(file_ops, dir_ops, classifier, conflict_resolver)
            
            # Plan organization
            result = organizer.plan_organization(root, scrubbed_folder)
            
            # Verify planning succeeded
            assert result.is_success(), "Planning should succeed"
            
            plan = result.unwrap()
            
            # Collect all source files from the plan
            planned_sources = {source for source, _ in plan.files_to_move}
            
            # Verify all created files are in the plan
            for file_path in created_files:
                # Files not in scrubbed folder should be in the plan
                if not organizer._is_in_scrubbed_folder(file_path, scrubbed_folder):
                    assert file_path in planned_sources, (
                        f"File {file_path} should be in organization plan"
                    )
            
            # Verify no extra files in the plan
            for source in planned_sources:
                assert source in created_files, (
                    f"Planned source {source} should be one of the created files"
                )
    
    @settings(max_examples=50, deadline=None)
    @given(structure=directory_structures())
    def test_no_files_lost_in_plan(self, structure):
        """
        **Feature: architectural-unification, Property 6: Simulation Accuracy**
        **Validates: Requirements 6.1**
        
        For any random file set, when planning organization, no files should
        be lost - every file should have exactly one destination.
        """
        num_files, depth, _ = structure
        
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            scrubbed_folder = root / "Scrubbed"
            
            # Create test files
            created_files = create_test_files(root, num_files, depth)
            
            # Verify we created the expected number of files
            assume(len(created_files) == num_files)
            
            # Create organizer
            file_ops = MockFileOperations()
            dir_ops = RealDirectoryOperations()
            classifier = EnhancedFileClassifier()
            conflict_resolver = ConflictResolver()
            
            organizer = FileOrganizer(file_ops, dir_ops, classifier, conflict_resolver)
            
            # Plan organization
            result = organizer.plan_organization(root, scrubbed_folder)
            
            # Verify planning succeeded
            assert result.is_success(), "Planning should succeed"
            
            plan = result.unwrap()
            
            # Count files in plan
            files_in_plan = len(plan.files_to_move)
            
            # Count files not in scrubbed folder
            files_to_organize = sum(
                1 for f in created_files
                if not organizer._is_in_scrubbed_folder(f, scrubbed_folder)
            )
            
            # Verify counts match
            assert files_in_plan == files_to_organize, (
                f"Plan should include all {files_to_organize} files to organize, "
                f"but only includes {files_in_plan}"
            )
    
    @settings(max_examples=50, deadline=None)
    @given(structure=directory_structures())
    def test_each_file_has_unique_destination(self, structure):
        """
        **Feature: architectural-unification, Property 6: Simulation Accuracy**
        **Validates: Requirements 6.1**
        
        For any random file set, when planning organization, each file should
        have a unique destination (conflicts should be resolved).
        """
        num_files, depth, _ = structure
        
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            scrubbed_folder = root / "Scrubbed"
            
            # Create test files
            created_files = create_test_files(root, num_files, depth)
            
            # Verify we created the expected number of files
            assume(len(created_files) == num_files)
            
            # Create organizer
            file_ops = MockFileOperations()
            dir_ops = RealDirectoryOperations()
            classifier = EnhancedFileClassifier()
            conflict_resolver = ConflictResolver()
            
            organizer = FileOrganizer(file_ops, dir_ops, classifier, conflict_resolver)
            
            # Plan organization
            result = organizer.plan_organization(root, scrubbed_folder)
            
            # Verify planning succeeded
            assert result.is_success(), "Planning should succeed"
            
            plan = result.unwrap()
            
            # Collect all destinations
            destinations = [dest for _, dest in plan.files_to_move]
            
            # Verify all destinations are unique
            unique_destinations = set(destinations)
            assert len(destinations) == len(unique_destinations), (
                f"All destinations should be unique, but found {len(destinations)} "
                f"destinations with only {len(unique_destinations)} unique values"
            )
    
    @settings(max_examples=50, deadline=None)
    @given(structure=directory_structures())
    def test_all_destinations_in_scrubbed_folder(self, structure):
        """
        **Feature: architectural-unification, Property 6: Simulation Accuracy**
        **Validates: Requirements 6.1**
        
        For any random file set, when planning organization, all destination
        paths should be within the scrubbed folder.
        """
        num_files, depth, _ = structure
        
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            scrubbed_folder = root / "Scrubbed"
            
            # Create test files
            created_files = create_test_files(root, num_files, depth)
            
            # Verify we created the expected number of files
            assume(len(created_files) == num_files)
            
            # Create organizer
            file_ops = MockFileOperations()
            dir_ops = RealDirectoryOperations()
            classifier = EnhancedFileClassifier()
            conflict_resolver = ConflictResolver()
            
            organizer = FileOrganizer(file_ops, dir_ops, classifier, conflict_resolver)
            
            # Plan organization
            result = organizer.plan_organization(root, scrubbed_folder)
            
            # Verify planning succeeded
            assert result.is_success(), "Planning should succeed"
            
            plan = result.unwrap()
            
            # Verify all destinations are in scrubbed folder
            for source, dest in plan.files_to_move:
                try:
                    dest.relative_to(scrubbed_folder)
                except ValueError:
                    pytest.fail(
                        f"Destination {dest} is not within scrubbed folder {scrubbed_folder}"
                    )
    
    @settings(max_examples=50, deadline=None)
    @given(structure=directory_structures())
    def test_directories_created_for_all_categories(self, structure):
        """
        **Feature: architectural-unification, Property 6: Simulation Accuracy**
        **Validates: Requirements 6.1**
        
        For any random file set, when planning organization, the plan should
        include directory creation for all categories that have files.
        """
        num_files, depth, _ = structure
        
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            scrubbed_folder = root / "Scrubbed"
            
            # Create test files
            created_files = create_test_files(root, num_files, depth)
            
            # Verify we created the expected number of files
            assume(len(created_files) == num_files)
            
            # Create organizer
            file_ops = MockFileOperations()
            dir_ops = RealDirectoryOperations()
            classifier = EnhancedFileClassifier()
            conflict_resolver = ConflictResolver()
            
            organizer = FileOrganizer(file_ops, dir_ops, classifier, conflict_resolver)
            
            # Plan organization
            result = organizer.plan_organization(root, scrubbed_folder)
            
            # Verify planning succeeded
            assert result.is_success(), "Planning should succeed"
            
            plan = result.unwrap()
            
            # Collect categories from files
            categories_needed = set()
            for file_path in created_files:
                if not organizer._is_in_scrubbed_folder(file_path, scrubbed_folder):
                    category = classifier.classify(file_path)
                    categories_needed.add(category.value)
            
            # Verify directories are created for all categories
            for category_name in categories_needed:
                expected_dir = scrubbed_folder / category_name
                assert expected_dir in plan.directories_to_create, (
                    f"Directory {expected_dir} should be in creation plan for category {category_name}"
                )
    
    @settings(max_examples=50, deadline=None)
    @given(structure=directory_structures())
    def test_source_and_destination_counts_match(self, structure):
        """
        **Feature: architectural-unification, Property 6: Simulation Accuracy**
        **Validates: Requirements 6.1**
        
        For any random file set, when planning organization, the number of
        source files should equal the number of destination files.
        """
        num_files, depth, _ = structure
        
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            scrubbed_folder = root / "Scrubbed"
            
            # Create test files
            created_files = create_test_files(root, num_files, depth)
            
            # Verify we created the expected number of files
            assume(len(created_files) == num_files)
            
            # Create organizer
            file_ops = MockFileOperations()
            dir_ops = RealDirectoryOperations()
            classifier = EnhancedFileClassifier()
            conflict_resolver = ConflictResolver()
            
            organizer = FileOrganizer(file_ops, dir_ops, classifier, conflict_resolver)
            
            # Plan organization
            result = organizer.plan_organization(root, scrubbed_folder)
            
            # Verify planning succeeded
            assert result.is_success(), "Planning should succeed"
            
            plan = result.unwrap()
            
            # Count sources and destinations
            num_sources = len({source for source, _ in plan.files_to_move})
            num_destinations = len({dest for _, dest in plan.files_to_move})
            
            # They should match (after conflict resolution)
            assert num_sources == num_destinations, (
                f"Number of sources ({num_sources}) should equal number of "
                f"destinations ({num_destinations})"
            )
    
    @settings(max_examples=30, deadline=None)
    @given(structure=directory_structures())
    def test_plan_is_deterministic(self, structure):
        """
        **Feature: architectural-unification, Property 6: Simulation Accuracy**
        **Validates: Requirements 6.1**
        
        For any random file set, when planning organization multiple times,
        the plan should be deterministic (same input produces same output).
        """
        num_files, depth, _ = structure
        
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            scrubbed_folder = root / "Scrubbed"
            
            # Create test files
            created_files = create_test_files(root, num_files, depth)
            
            # Verify we created the expected number of files
            assume(len(created_files) == num_files)
            
            # Create organizer
            file_ops = MockFileOperations()
            dir_ops = RealDirectoryOperations()
            classifier = EnhancedFileClassifier()
            conflict_resolver = ConflictResolver()
            
            organizer = FileOrganizer(file_ops, dir_ops, classifier, conflict_resolver)
            
            # Plan organization twice
            result1 = organizer.plan_organization(root, scrubbed_folder)
            result2 = organizer.plan_organization(root, scrubbed_folder)
            
            # Verify both succeeded
            assert result1.is_success(), "First planning should succeed"
            assert result2.is_success(), "Second planning should succeed"
            
            plan1 = result1.unwrap()
            plan2 = result2.unwrap()
            
            # Verify plans are identical
            assert len(plan1.files_to_move) == len(plan2.files_to_move), (
                "Plans should have same number of file moves"
            )
            
            # Convert to sets for comparison (order doesn't matter)
            moves1 = set(plan1.files_to_move)
            moves2 = set(plan2.files_to_move)
            
            assert moves1 == moves2, (
                "Plans should have identical file moves"
            )
            
            assert plan1.directories_to_create == plan2.directories_to_create, (
                "Plans should have identical directory creation"
            )


class TestOrganizationWithConflicts:
    """Property tests for organization with naming conflicts.
    
    **Feature: architectural-unification, Property 6: Simulation Accuracy**
    **Validates: Requirements 6.1**
    """
    
    @settings(max_examples=30, deadline=None)
    @given(num_duplicates=st.integers(min_value=2, max_value=10))
    def test_duplicate_filenames_resolved(self, num_duplicates):
        """
        **Feature: architectural-unification, Property 6: Simulation Accuracy**
        **Validates: Requirements 6.1**
        
        For any set of files with duplicate names, when planning organization,
        all conflicts should be resolved with unique destinations.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            scrubbed_folder = root / "Scrubbed"
            
            # Create files with duplicate names in different directories
            created_files = []
            for i in range(num_duplicates):
                subdir = root / f"dir{i}"
                subdir.mkdir()
                file_path = subdir / "duplicate.txt"
                file_path.touch()
                created_files.append(file_path)
            
            # Create organizer
            file_ops = MockFileOperations()
            dir_ops = RealDirectoryOperations()
            classifier = EnhancedFileClassifier()
            conflict_resolver = ConflictResolver()
            
            organizer = FileOrganizer(file_ops, dir_ops, classifier, conflict_resolver)
            
            # Plan organization
            result = organizer.plan_organization(root, scrubbed_folder)
            
            # Verify planning succeeded
            assert result.is_success(), "Planning should succeed"
            
            plan = result.unwrap()
            
            # Verify all files are in the plan
            assert len(plan.files_to_move) == num_duplicates, (
                f"Plan should include all {num_duplicates} files"
            )
            
            # Verify all destinations are unique
            destinations = [dest for _, dest in plan.files_to_move]
            unique_destinations = set(destinations)
            
            assert len(destinations) == len(unique_destinations), (
                f"All {num_duplicates} destinations should be unique"
            )
            
            # Verify that if there were duplicates, some conflicts were resolved
            # The conflicts dict maps original destination to resolved destination
            # Note: Not all duplicate files will be in conflicts dict, only those
            # that actually conflicted with an existing destination
            if num_duplicates > 1:
                # At least one conflict should have been detected and resolved
                # (when the second file tried to use the same destination as the first)
                assert len(plan.conflicts) >= 1, (
                    f"Should have at least 1 conflict recorded for {num_duplicates} duplicate files"
                )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
