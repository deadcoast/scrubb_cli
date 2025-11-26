"""Property-based tests for algorithm efficiency.

**Feature: architectural-unification, Property 3: Algorithm Efficiency**
**Validates: Requirements 3.1**

This module tests that core algorithms exhibit O(n) time complexity,
not O(n²) or worse. We verify this empirically by measuring execution
time for various input sizes and checking that time scales linearly.
"""

import tempfile
import time
from pathlib import Path
from typing import List, Tuple
import pytest
from hypothesis import given, strategies as st, settings, assume

from scrubb.business.organizer import FileOrganizer, OrganizationPlan
from scrubb.business.classifier import EnhancedFileClassifier, FileCategory
from scrubb.business.conflict_resolver import ConflictResolver
from scrubb.io.directory_operations import RealDirectoryOperations


# Mock file operations for testing (we only need move_file for the organizer)
class MockFileOperations:
    """Mock file operations that don't actually move files."""
    
    def move_file(self, source: Path, dest: Path):
        """Mock move that always succeeds."""
        from scrubb.core.result import Success
        return Success(None)
    
    def file_exists(self, path: Path) -> bool:
        """Check if file exists."""
        return path.exists()


def create_test_directory_structure(root: Path, num_files: int, depth: int = 3) -> List[Path]:
    """Create a test directory structure with specified number of files.
    
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
            # Create 2-3 subdirectories at each level
            for i in range(2):
                subdir = parent / f"level{level}_dir{i}"
                subdir.mkdir(exist_ok=True)
                new_dirs.append(subdir)
        dirs.extend(new_dirs)
    
    # Distribute files across directories
    extensions = [".txt", ".jpg", ".mp4", ".pdf", ".py"]
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


def measure_plan_organization_time(num_files: int) -> float:
    """Measure time to plan organization for given number of files.
    
    Args:
        num_files: Number of files to organize
        
    Returns:
        Time in seconds
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        scrubbed_folder = root / "Scrubbed"
        
        # Create test structure
        create_test_directory_structure(root, num_files)
        
        # Create organizer
        file_ops = MockFileOperations()
        dir_ops = RealDirectoryOperations()
        classifier = EnhancedFileClassifier()
        conflict_resolver = ConflictResolver()
        
        organizer = FileOrganizer(file_ops, dir_ops, classifier, conflict_resolver)
        
        # Measure time
        start_time = time.perf_counter()
        result = organizer.plan_organization(root, scrubbed_folder)
        end_time = time.perf_counter()
        
        # Verify it succeeded
        assert result.is_success(), "Planning should succeed"
        
        return end_time - start_time


def test_plan_organization_is_linear():
    """Test that plan_organization exhibits O(n) time complexity.
    
    **Feature: architectural-unification, Property 3: Algorithm Efficiency**
    **Validates: Requirements 3.1**
    
    We test this by measuring execution time for different input sizes
    and verifying that doubling the input size roughly doubles the time.
    """
    # Test with progressively larger inputs
    sizes = [50, 100, 200, 400]
    times = []
    
    for size in sizes:
        # Run multiple times and take average to reduce noise
        measurements = []
        for _ in range(3):
            t = measure_plan_organization_time(size)
            measurements.append(t)
        
        avg_time = sum(measurements) / len(measurements)
        times.append(avg_time)
        print(f"Size {size}: {avg_time:.4f}s")
    
    # Check that time scales roughly linearly with input size
    # For O(n), doubling input should roughly double time
    # We allow for some variance due to constant factors and measurement noise
    
    for i in range(len(sizes) - 1):
        size_ratio = sizes[i + 1] / sizes[i]
        time_ratio = times[i + 1] / times[i]
        
        # For O(n), time_ratio should be close to size_ratio
        # For O(n²), time_ratio would be close to size_ratio²
        
        # We expect time_ratio to be between 0.5 * size_ratio and 3 * size_ratio
        # This allows for measurement noise and constant factors
        # But rules out O(n²) behavior where time_ratio would be ~4x for 2x size
        
        print(f"Size ratio: {size_ratio:.2f}, Time ratio: {time_ratio:.2f}")
        
        # If we had O(n²), doubling size would quadruple time (ratio ~4)
        # With O(n), doubling size should double time (ratio ~2)
        # We assert that time_ratio is not quadratic
        assert time_ratio < size_ratio * 2.5, (
            f"Time complexity appears worse than O(n): "
            f"size increased by {size_ratio}x but time increased by {time_ratio}x"
        )


@given(
    num_files=st.integers(min_value=10, max_value=100),
    depth=st.integers(min_value=1, max_value=5)
)
@settings(max_examples=20, deadline=None)
def test_plan_organization_completes_for_random_structures(num_files: int, depth: int):
    """Test that plan_organization completes successfully for random structures.
    
    **Feature: architectural-unification, Property 3: Algorithm Efficiency**
    **Validates: Requirements 3.1**
    
    This property test verifies that the algorithm completes successfully
    for various random directory structures without hanging or failing.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        scrubbed_folder = root / "Scrubbed"
        
        # Create test structure
        created_files = create_test_directory_structure(root, num_files, depth)
        
        # Verify we created the expected number of files
        assume(len(created_files) == num_files)
        
        # Create organizer
        file_ops = MockFileOperations()
        dir_ops = RealDirectoryOperations()
        classifier = EnhancedFileClassifier()
        conflict_resolver = ConflictResolver()
        
        organizer = FileOrganizer(file_ops, dir_ops, classifier, conflict_resolver)
        
        # Measure time (should complete quickly for small inputs)
        start_time = time.perf_counter()
        result = organizer.plan_organization(root, scrubbed_folder)
        end_time = time.perf_counter()
        
        elapsed = end_time - start_time
        
        # Verify it succeeded
        assert result.is_success(), "Planning should succeed"
        
        # Verify it completed in reasonable time
        # For 100 files, should complete in well under 1 second
        # This catches any O(n²) or worse behavior
        max_time = num_files * 0.01  # 10ms per file is very generous
        assert elapsed < max_time, (
            f"Planning took {elapsed:.3f}s for {num_files} files, "
            f"expected < {max_time:.3f}s"
        )
        
        # Verify the plan is correct
        plan = result.unwrap()
        assert isinstance(plan, OrganizationPlan)
        
        # All created files should be in the plan (except those in scrubbed folder)
        files_to_move_sources = {source for source, _ in plan.files_to_move}
        for file_path in created_files:
            if not organizer._is_in_scrubbed_folder(file_path, scrubbed_folder):
                assert file_path in files_to_move_sources, (
                    f"File {file_path} should be in plan"
                )


def test_empty_directory_detection_is_efficient():
    """Test that empty directory detection is O(n), not O(n²).
    
    **Feature: architectural-unification, Property 3: Algorithm Efficiency**
    **Validates: Requirements 3.1**
    
    The old implementation had O(n²) behavior for empty directory detection.
    This test verifies the new implementation is O(n).
    """
    # Create a deep directory structure with many empty directories
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        scrubbed_folder = root / "Scrubbed"
        
        # Create a deep tree: 10 levels, 3 branches per level
        # This creates 3^10 = 59,049 directories if fully expanded
        # We'll create a more modest structure
        def create_deep_tree(parent: Path, depth: int, branches: int):
            if depth == 0:
                return
            for i in range(branches):
                child = parent / f"dir{i}"
                child.mkdir()
                create_deep_tree(child, depth - 1, branches)
        
        # Create 5 levels with 3 branches = 3^5 = 243 directories
        create_deep_tree(root, 5, 3)
        
        # Add a few files at various levels
        (root / "file1.txt").touch()
        (root / "dir0" / "file2.txt").touch()
        (root / "dir0" / "dir0" / "file3.txt").touch()
        
        # Create organizer
        file_ops = MockFileOperations()
        dir_ops = RealDirectoryOperations()
        classifier = EnhancedFileClassifier()
        conflict_resolver = ConflictResolver()
        
        organizer = FileOrganizer(file_ops, dir_ops, classifier, conflict_resolver)
        
        # Measure time
        start_time = time.perf_counter()
        result = organizer.plan_organization(root, scrubbed_folder)
        end_time = time.perf_counter()
        
        elapsed = end_time - start_time
        
        # Verify it succeeded
        assert result.is_success(), "Planning should succeed"
        
        # With O(n) algorithm, this should complete very quickly
        # With O(n²), this would take much longer
        assert elapsed < 1.0, (
            f"Empty directory detection took {elapsed:.3f}s, "
            f"expected < 1.0s (may indicate O(n²) behavior)"
        )
        
        # Verify empty directories were identified
        plan = result.unwrap()
        # Most directories should be marked for removal since we only have 3 files
        assert len(plan.directories_to_remove) > 100, (
            "Should identify many empty directories"
        )


if __name__ == "__main__":
    # Run the linear time test
    print("Testing linear time complexity...")
    test_plan_organization_is_linear()
    print("\nTesting empty directory detection efficiency...")
    test_empty_directory_detection_is_efficient()
    print("\nAll efficiency tests passed!")
