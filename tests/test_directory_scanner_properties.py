"""Property-based tests for DirectoryScanner functionality."""

import pytest
from pathlib import Path
import tempfile
from hypothesis import given, strategies as st, settings

from scrubb.directory_scanner import DirectoryScanner
from scrubb.file_classifier import FileClassifier


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
        
        # Create the file with some content
        file_path.write_text(f"Test content for {filename}")


class TestTreeCaptureConsistency:
    """Property tests for tree capture consistency."""
    
    @settings(max_examples=100)
    @given(structure=directory_structure())
    def test_tree_capture_consistency(self, structure):
        """
        **Feature: tree-visualization, Property 1: Tree capture consistency**
        **Validates: Requirements 1.3, 1.4**
        
        For any directory state, capturing a snapshot and immediately capturing
        another snapshot without intervening operations should produce equivalent
        statistics.
        """
        # Create temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            root_path = Path(temp_dir)
            
            # Create test structure
            create_test_structure(root_path, structure)
            
            # Create scanner
            classifier = FileClassifier()
            scanner = DirectoryScanner(classifier)
            
            # Capture first snapshot
            snapshot1 = scanner.scan(root_path)
            
            # Capture second snapshot immediately
            snapshot2 = scanner.scan(root_path)
            
            # Verify statistics are equivalent
            assert snapshot1.statistics.total_files == snapshot2.statistics.total_files, \
                "Total files differ between consecutive scans"
            assert snapshot1.statistics.total_directories == snapshot2.statistics.total_directories, \
                "Total directories differ between consecutive scans"
            assert snapshot1.statistics.total_size == snapshot2.statistics.total_size, \
                "Total size differs between consecutive scans"
            assert snapshot1.statistics.max_depth == snapshot2.statistics.max_depth, \
                "Max depth differs between consecutive scans"
            assert snapshot1.statistics.files_by_category == snapshot2.statistics.files_by_category, \
                "Files by category differ between consecutive scans"
            assert snapshot1.statistics.size_by_category == snapshot2.statistics.size_by_category, \
                "Size by category differs between consecutive scans"


class TestDirectoryCountAccuracy:
    """Property tests for directory count accuracy."""
    
    @settings(max_examples=100)
    @given(structure=directory_structure())
    def test_directory_count_accuracy(self, structure):
        """
        **Feature: tree-visualization, Property 7: Directory count accuracy**
        **Validates: Requirements 2.2**
        
        For any directory tree, the total directory count should equal the
        number of nodes where is_directory is True.
        """
        # Create temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            root_path = Path(temp_dir)
            
            # Create test structure
            create_test_structure(root_path, structure)
            
            # Create scanner and scan
            classifier = FileClassifier()
            scanner = DirectoryScanner(classifier)
            snapshot = scanner.scan(root_path)
            
            # Count directories by traversing the tree
            def count_directories(node):
                """Recursively count directory nodes."""
                count = 1 if node.is_directory else 0
                for child in node.children:
                    count += count_directories(child)
                return count
            
            actual_dir_count = count_directories(snapshot.root_node)
            
            # Verify statistics match actual count
            assert snapshot.statistics.total_directories == actual_dir_count, \
                f"Directory count mismatch: statistics={snapshot.statistics.total_directories}, " \
                f"actual={actual_dir_count}"


class TestDepthCalculation:
    """Property tests for depth calculation correctness."""
    
    @settings(max_examples=100)
    @given(structure=directory_structure())
    def test_depth_calculation_correctness(self, structure):
        """
        **Feature: tree-visualization, Property 8: Depth calculation correctness**
        **Validates: Requirements 2.3**
        
        For any directory tree, the maximum depth should be greater than or
        equal to the depth of any individual node in the tree.
        """
        # Create temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            root_path = Path(temp_dir)
            
            # Create test structure
            create_test_structure(root_path, structure)
            
            # Create scanner and scan
            classifier = FileClassifier()
            scanner = DirectoryScanner(classifier)
            snapshot = scanner.scan(root_path)
            
            # Find maximum depth by traversing the tree
            def find_max_depth(node):
                """Recursively find maximum depth in tree."""
                max_depth = node.depth
                for child in node.children:
                    child_max = find_max_depth(child)
                    max_depth = max(max_depth, child_max)
                return max_depth
            
            actual_max_depth = find_max_depth(snapshot.root_node)
            
            # Verify statistics max_depth is correct
            assert snapshot.statistics.max_depth == actual_max_depth, \
                f"Max depth mismatch: statistics={snapshot.statistics.max_depth}, " \
                f"actual={actual_max_depth}"
            
            # Verify max_depth is >= all node depths
            def verify_all_depths(node):
                """Verify all node depths are <= max_depth."""
                assert node.depth <= snapshot.statistics.max_depth, \
                    f"Node depth {node.depth} exceeds max_depth {snapshot.statistics.max_depth}"
                for child in node.children:
                    verify_all_depths(child)
            
            verify_all_depths(snapshot.root_node)


class TestSizeCalculation:
    """Property tests for size calculation consistency."""
    
    @settings(max_examples=100)
    @given(structure=directory_structure())
    def test_size_calculation_consistency(self, structure):
        """
        **Feature: tree-visualization, Property 9: Size calculation consistency**
        **Validates: Requirements 2.4**
        
        For any directory tree, the total size should equal the sum of all
        file sizes in the tree.
        """
        # Create temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            root_path = Path(temp_dir)
            
            # Create test structure
            create_test_structure(root_path, structure)
            
            # Create scanner and scan
            classifier = FileClassifier()
            scanner = DirectoryScanner(classifier)
            snapshot = scanner.scan(root_path)
            
            # Calculate total size by traversing the tree
            def calculate_total_size(node):
                """Recursively calculate total size of all files."""
                total = 0
                if not node.is_directory:
                    total += node.size
                for child in node.children:
                    total += calculate_total_size(child)
                return total
            
            actual_total_size = calculate_total_size(snapshot.root_node)
            
            # Verify statistics match actual size
            assert snapshot.statistics.total_size == actual_total_size, \
                f"Total size mismatch: statistics={snapshot.statistics.total_size}, " \
                f"actual={actual_total_size}"
