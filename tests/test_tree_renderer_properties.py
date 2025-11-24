"""Property-based tests for TreeRenderer functionality."""

import pytest
from pathlib import Path
import tempfile
from io import StringIO
import sys
from hypothesis import given, strategies as st, settings

from scrubb.tree_renderer import TreeRenderer, SimpleTreeRenderer
from scrubb.tree_models import DirectorySnapshot, DirectoryNode, DirectoryStatistics
from scrubb.directory_scanner import DirectoryScanner
from scrubb.file_classifier import FileClassifier
from datetime import datetime


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


def capture_output(func, *args, **kwargs):
    """Capture stdout from a function call."""
    old_stdout = sys.stdout
    sys.stdout = StringIO()
    try:
        func(*args, **kwargs)
        output = sys.stdout.getvalue()
    finally:
        sys.stdout = old_stdout
    return output


class TestTreeRenderingIdempotence:
    """Property tests for tree rendering idempotence."""
    
    @settings(max_examples=100)
    @given(structure=directory_structure())
    def test_tree_rendering_idempotence(self, structure):
        """
        **Feature: tree-visualization, Property 5: Tree rendering idempotence**
        **Validates: Requirements 3.2, 3.3, 9.3**
        
        For any directory snapshot, rendering it multiple times should produce
        identical output.
        """
        # Create temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            root_path = Path(temp_dir)
            
            # Create test structure
            create_test_structure(root_path, structure)
            
            # Create scanner and capture snapshot
            classifier = FileClassifier()
            scanner = DirectoryScanner(classifier)
            snapshot = scanner.scan(root_path)
            
            # Use SimpleTreeRenderer for consistent output (no rich formatting)
            renderer = SimpleTreeRenderer()
            
            # Render the tree multiple times
            output1 = capture_output(renderer.render, snapshot, "Test Tree")
            output2 = capture_output(renderer.render, snapshot, "Test Tree")
            output3 = capture_output(renderer.render, snapshot, "Test Tree")
            
            # Verify all outputs are identical
            assert output1 == output2, \
                "First and second render outputs differ"
            assert output2 == output3, \
                "Second and third render outputs differ"
            assert output1 == output3, \
                "First and third render outputs differ"
    
    @settings(max_examples=100)
    @given(structure=directory_structure())
    def test_tree_rendering_no_emojis(self, structure):
        """
        **Feature: tree-visualization, Property 5: Tree rendering idempotence**
        **Validates: Requirements 3.2, 3.3, 9.3**
        
        For any directory snapshot, the rendered output should not contain
        any emoji characters.
        """
        # Create temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            root_path = Path(temp_dir)
            
            # Create test structure
            create_test_structure(root_path, structure)
            
            # Create scanner and capture snapshot
            classifier = FileClassifier()
            scanner = DirectoryScanner(classifier)
            snapshot = scanner.scan(root_path)
            
            # Use SimpleTreeRenderer for consistent output
            renderer = SimpleTreeRenderer()
            
            # Render the tree
            output = capture_output(renderer.render, snapshot, "Test Tree")
            
            # Check for common emoji characters
            # Unicode ranges for emojis (simplified check)
            emoji_ranges = [
                (0x1F600, 0x1F64F),  # Emoticons
                (0x1F300, 0x1F5FF),  # Misc Symbols and Pictographs
                (0x1F680, 0x1F6FF),  # Transport and Map
                (0x2600, 0x26FF),    # Misc symbols
                (0x2700, 0x27BF),    # Dingbats
                (0xFE00, 0xFE0F),    # Variation Selectors
                (0x1F900, 0x1F9FF),  # Supplemental Symbols and Pictographs
            ]
            
            for char in output:
                code_point = ord(char)
                for start, end in emoji_ranges:
                    assert not (start <= code_point <= end), \
                        f"Found emoji character '{char}' (U+{code_point:04X}) in output"
