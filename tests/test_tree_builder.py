"""Tests for TreeBuilder class."""

import pytest
from pathlib import Path
from datetime import datetime
from scrubb.business.tree_builder import TreeBuilder
from scrubb.business.classifier import EnhancedFileClassifier, FileCategory
from scrubb.business.organizer import OrganizationPlan
from scrubb.tree_models import DirectoryNode, DirectorySnapshot


class TestTreeBuilder:
    """Test TreeBuilder functionality."""
    
    @pytest.fixture
    def classifier(self):
        """Create a classifier for testing."""
        return EnhancedFileClassifier()
    
    @pytest.fixture
    def tree_builder(self, classifier):
        """Create a TreeBuilder instance."""
        return TreeBuilder(classifier)
    
    @pytest.fixture
    def temp_structure(self, tmp_path):
        """Create a temporary directory structure for testing."""
        # Create some files and directories
        (tmp_path / "file1.txt").write_text("content1")
        (tmp_path / "file2.jpg").write_text("image")
        (tmp_path / "subdir").mkdir()
        (tmp_path / "subdir" / "file3.py").write_text("code")
        (tmp_path / "subdir" / "file4.md").write_text("docs")
        
        return tmp_path
    
    def test_build_tree_creates_snapshot(self, tree_builder, temp_structure):
        """Test that build_tree creates a valid DirectorySnapshot."""
        snapshot = tree_builder.build_tree(temp_structure)
        
        assert isinstance(snapshot, DirectorySnapshot)
        assert snapshot.root_path == temp_structure
        assert isinstance(snapshot.root_node, DirectoryNode)
        assert snapshot.root_node.is_directory
        assert not snapshot.is_simulated
        assert len(snapshot.root_node.children) > 0
    
    def test_build_tree_respects_max_depth(self, tree_builder, temp_structure):
        """Test that build_tree respects max_depth parameter."""
        snapshot = tree_builder.build_tree(temp_structure, max_depth=0)
        
        # At depth 0, we should only have the root node with no children
        assert snapshot.root_node.depth == 0
        # Children should be empty or not traversed
        assert len(snapshot.root_node.children) == 0
    
    def test_simulate_after_state_without_filesystem_access(self, tree_builder, temp_structure, classifier):
        """Test that simulate_after_state works without filesystem access."""
        # Build initial snapshot
        before_snapshot = tree_builder.build_tree(temp_structure)
        
        # Create a simple organization plan
        scrubbed_folder = temp_structure / "Scrubbed"
        plan = OrganizationPlan()
        
        # Add some file moves
        file1 = temp_structure / "file1.txt"
        file2 = temp_structure / "file2.jpg"
        plan.files_to_move = [
            (file1, scrubbed_folder / "Docs/Other Docs" / "file1.txt"),
            (file2, scrubbed_folder / "Images" / "file2.jpg"),
        ]
        plan.directories_to_create = {
            scrubbed_folder / "Docs/Other Docs",
            scrubbed_folder / "Images",
        }
        
        # Simulate after state
        after_snapshot = tree_builder.simulate_after_state(
            before_snapshot, plan, scrubbed_folder
        )
        
        assert after_snapshot.is_simulated
        assert after_snapshot.root_path == temp_structure
        
        # Verify scrubbed folder was added
        scrubbed_node = None
        for child in after_snapshot.root_node.children:
            if child.name == "Scrubbed":
                scrubbed_node = child
                break
        
        assert scrubbed_node is not None
        assert scrubbed_node.is_new
        assert scrubbed_node.is_directory
    
    def test_remove_moved_files(self, tree_builder, temp_structure):
        """Test that _remove_moved_files correctly removes files from tree."""
        before_snapshot = tree_builder.build_tree(temp_structure)
        
        # Get a file to remove
        file_to_remove = temp_structure / "file1.txt"
        files_to_remove = {file_to_remove}
        
        # Deep copy and remove
        simulated_root = tree_builder._deep_copy_node(before_snapshot.root_node)
        original_child_count = len(simulated_root.children)
        
        tree_builder._remove_moved_files(simulated_root, files_to_remove)
        
        # Verify file was removed
        assert len(simulated_root.children) < original_child_count
        
        # Verify the specific file is not in children
        for child in simulated_root.children:
            assert child.path != file_to_remove
    
    def test_add_scrubbed_folder(self, tree_builder, temp_structure, classifier):
        """Test that _add_scrubbed_folder correctly adds organized files."""
        before_snapshot = tree_builder.build_tree(temp_structure)
        simulated_root = tree_builder._deep_copy_node(before_snapshot.root_node)
        
        scrubbed_folder = temp_structure / "Scrubbed"
        plan = OrganizationPlan()
        
        file1 = temp_structure / "file1.txt"
        plan.files_to_move = [
            (file1, scrubbed_folder / "Docs/Other Docs" / "file1.txt"),
        ]
        
        tree_builder._add_scrubbed_folder(
            simulated_root, plan, scrubbed_folder, temp_structure
        )
        
        # Verify scrubbed folder exists
        scrubbed_node = None
        for child in simulated_root.children:
            if child.path == scrubbed_folder:
                scrubbed_node = child
                break
        
        assert scrubbed_node is not None
        assert scrubbed_node.is_new
        assert len(scrubbed_node.children) > 0
    
    def test_remove_empty_dirs(self, tree_builder, temp_structure):
        """Test that _remove_empty_dirs correctly removes directories."""
        before_snapshot = tree_builder.build_tree(temp_structure)
        simulated_root = tree_builder._deep_copy_node(before_snapshot.root_node)
        
        # Mark subdir for removal
        subdir = temp_structure / "subdir"
        dirs_to_remove = {subdir}
        
        tree_builder._remove_empty_dirs(simulated_root, dirs_to_remove)
        
        # Verify directory was removed
        for child in simulated_root.children:
            assert child.path != subdir
    
    def test_deep_copy_node(self, tree_builder, temp_structure):
        """Test that _deep_copy_node creates independent copy."""
        before_snapshot = tree_builder.build_tree(temp_structure)
        original = before_snapshot.root_node
        
        copied = tree_builder._deep_copy_node(original)
        
        # Verify it's a different object
        assert copied is not original
        assert copied.path == original.path
        assert copied.name == original.name
        assert len(copied.children) == len(original.children)
        
        # Verify children are also copied
        if len(original.children) > 0:
            assert copied.children[0] is not original.children[0]
    
    def test_calculate_statistics(self, tree_builder, temp_structure):
        """Test that statistics are calculated correctly."""
        snapshot = tree_builder.build_tree(temp_structure)
        
        stats = snapshot.statistics
        assert stats.total_files > 0
        assert stats.total_directories > 0
        assert stats.total_size >= 0
        assert stats.max_depth >= 0
