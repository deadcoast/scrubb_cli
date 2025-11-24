"""Property-based tests for TreeVisualizer functionality."""

import pytest
from pathlib import Path
import tempfile
from hypothesis import given, strategies as st, settings

from scrubb.tree_visualizer import TreeVisualizer
from scrubb.tree_renderer import TreeRenderer
from scrubb.file_classifier import FileClassifier
from scrubb.folder_organizer import FolderOrganizer


# Strategy for generating file extensions
@st.composite
def file_extensions(draw):
    """Generate valid file extensions for testing."""
    known_extensions = [
        ".jpg", ".png", ".gif", ".mp4", ".avi", ".md", ".txt", ".pdf",
        ".py", ".js", ".html", ".css", ".json"
    ]
    
    return draw(st.sampled_from(known_extensions))


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


class TestDryRunSimulationAccuracy:
    """Property tests for dry-run simulation accuracy."""
    
    @settings(max_examples=100)
    @given(structure=directory_structure())
    def test_dry_run_simulation_file_count(self, structure):
        """
        **Feature: tree-visualization, Property 4: Dry-run simulation accuracy**
        **Validates: Requirements 7.2, 7.3**
        
        For any dry-run operation, the simulated after-state file count should
        equal the before-state file count (files are moved, not created or deleted).
        """
        # Create temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            root_path = Path(temp_dir)
            
            # Create test structure
            create_test_structure(root_path, structure)
            
            # Create visualizer
            renderer = TreeRenderer()
            visualizer = TreeVisualizer(root_path, renderer)
            
            # Capture before state
            before_snapshot = visualizer.capture_before_state()
            
            # Run dry-run organization
            classifier = FileClassifier()
            organizer = FolderOrganizer(root_path, classifier, dry_run=True)
            dry_run_stats = organizer.organize()
            
            # Simulate after state
            after_snapshot = visualizer.simulate_after_state(dry_run_stats)
            
            # Verify file count is conserved
            assert before_snapshot.statistics.total_files == after_snapshot.statistics.total_files, \
                f"File count not conserved: before={before_snapshot.statistics.total_files}, " \
                f"after={after_snapshot.statistics.total_files}"


class TestBeforeAfterFileConservation:
    """Property tests for file conservation in actual execution."""
    
    @settings(max_examples=100)
    @given(structure=directory_structure())
    def test_before_after_file_conservation(self, structure):
        """
        **Feature: tree-visualization, Property 10: Before-after file conservation**
        **Validates: Requirements 1.3, 1.4, 5.3**
        
        For any actual execution (non-dry-run), the number of files in the before
        state should equal the number of files in the after state (files are moved,
        not created or deleted).
        """
        # Create temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            root_path = Path(temp_dir)
            
            # Create test structure
            create_test_structure(root_path, structure)
            
            # Create visualizer
            renderer = TreeRenderer()
            visualizer = TreeVisualizer(root_path, renderer)
            
            # Capture before state
            before_snapshot = visualizer.capture_before_state()
            
            # Run actual organization
            classifier = FileClassifier()
            organizer = FolderOrganizer(root_path, classifier, dry_run=False)
            organizer.organize()
            
            # Capture after state
            after_snapshot = visualizer.capture_after_state()
            
            # Verify file count is conserved
            assert before_snapshot.statistics.total_files == after_snapshot.statistics.total_files, \
                f"File count not conserved: before={before_snapshot.statistics.total_files}, " \
                f"after={after_snapshot.statistics.total_files}"
