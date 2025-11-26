"""Unit tests for directory operations.

This module tests the RealDirectoryOperations implementation to ensure
it correctly handles directory operations and returns proper Result types.
"""

import pytest
import tempfile
import shutil
from pathlib import Path

from scrubb.io.directory_operations import RealDirectoryOperations
from scrubb.core.result import Success, Failure
from scrubb.core.errors import DirectoryOperationError


class TestRealDirectoryOperations:
    """Unit tests for RealDirectoryOperations."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing."""
        temp_path = Path(tempfile.mkdtemp())
        yield temp_path
        # Cleanup
        if temp_path.exists():
            shutil.rmtree(temp_path)
    
    @pytest.fixture
    def dir_ops(self):
        """Create a RealDirectoryOperations instance."""
        return RealDirectoryOperations()
    
    def test_create_directory_success(self, dir_ops, temp_dir):
        """Test creating a directory successfully."""
        new_dir = temp_dir / "test_dir"
        
        result = dir_ops.create_directory(new_dir)
        
        assert result.is_success()
        assert new_dir.exists()
        assert new_dir.is_dir()
    
    def test_create_directory_with_parents(self, dir_ops, temp_dir):
        """Test creating a directory with parent directories."""
        new_dir = temp_dir / "parent" / "child" / "grandchild"
        
        result = dir_ops.create_directory(new_dir)
        
        assert result.is_success()
        assert new_dir.exists()
        assert new_dir.is_dir()
    
    def test_create_directory_already_exists(self, dir_ops, temp_dir):
        """Test creating a directory that already exists."""
        new_dir = temp_dir / "test_dir"
        new_dir.mkdir()
        
        result = dir_ops.create_directory(new_dir)
        
        # Should succeed (exist_ok=True)
        assert result.is_success()
        assert new_dir.exists()
    
    def test_remove_directory_success(self, dir_ops, temp_dir):
        """Test removing an empty directory successfully."""
        test_dir = temp_dir / "test_dir"
        test_dir.mkdir()
        
        result = dir_ops.remove_directory(test_dir)
        
        assert result.is_success()
        assert not test_dir.exists()
    
    def test_remove_directory_not_empty(self, dir_ops, temp_dir):
        """Test removing a non-empty directory fails."""
        test_dir = temp_dir / "test_dir"
        test_dir.mkdir()
        # Create a file in the directory
        (test_dir / "file.txt").write_text("content")
        
        result = dir_ops.remove_directory(test_dir)
        
        assert result.is_failure()
        assert isinstance(result.error, DirectoryOperationError)
        assert test_dir.exists()
    
    def test_remove_directory_not_found(self, dir_ops, temp_dir):
        """Test removing a non-existent directory fails."""
        non_existent = temp_dir / "does_not_exist"
        
        result = dir_ops.remove_directory(non_existent)
        
        assert result.is_failure()
        assert isinstance(result.error, DirectoryOperationError)
        assert "not found" in result.error.message.lower()
    
    def test_list_directory_success(self, dir_ops, temp_dir):
        """Test listing directory contents successfully."""
        # Create some files and directories
        (temp_dir / "file1.txt").write_text("content1")
        (temp_dir / "file2.txt").write_text("content2")
        (temp_dir / "subdir").mkdir()
        
        result = dir_ops.list_directory(temp_dir)
        
        assert result.is_success()
        items = result.unwrap()
        assert len(items) == 3
        assert temp_dir / "file1.txt" in items
        assert temp_dir / "file2.txt" in items
        assert temp_dir / "subdir" in items
    
    def test_list_directory_empty(self, dir_ops, temp_dir):
        """Test listing an empty directory."""
        result = dir_ops.list_directory(temp_dir)
        
        assert result.is_success()
        items = result.unwrap()
        assert len(items) == 0
    
    def test_list_directory_not_found(self, dir_ops, temp_dir):
        """Test listing a non-existent directory fails."""
        non_existent = temp_dir / "does_not_exist"
        
        result = dir_ops.list_directory(non_existent)
        
        assert result.is_failure()
        assert isinstance(result.error, DirectoryOperationError)
        assert "not found" in result.error.message.lower()
    
    def test_is_empty_true(self, dir_ops, temp_dir):
        """Test checking if an empty directory is empty."""
        result = dir_ops.is_empty(temp_dir)
        
        assert result.is_success()
        assert result.unwrap() is True
    
    def test_is_empty_false(self, dir_ops, temp_dir):
        """Test checking if a non-empty directory is empty."""
        # Create a file
        (temp_dir / "file.txt").write_text("content")
        
        result = dir_ops.is_empty(temp_dir)
        
        assert result.is_success()
        assert result.unwrap() is False
    
    def test_is_empty_not_found(self, dir_ops, temp_dir):
        """Test checking if a non-existent directory is empty fails."""
        non_existent = temp_dir / "does_not_exist"
        
        result = dir_ops.is_empty(non_existent)
        
        assert result.is_failure()
        assert isinstance(result.error, DirectoryOperationError)
        assert "not found" in result.error.message.lower()
    
    def test_directory_exists_true(self, dir_ops, temp_dir):
        """Test checking if a directory exists."""
        assert dir_ops.directory_exists(temp_dir) is True
    
    def test_directory_exists_false(self, dir_ops, temp_dir):
        """Test checking if a non-existent directory exists."""
        non_existent = temp_dir / "does_not_exist"
        assert dir_ops.directory_exists(non_existent) is False
    
    def test_directory_exists_file_not_directory(self, dir_ops, temp_dir):
        """Test checking if a file (not directory) exists."""
        file_path = temp_dir / "file.txt"
        file_path.write_text("content")
        
        # Should return False because it's a file, not a directory
        assert dir_ops.directory_exists(file_path) is False
    
    def test_error_context_includes_path(self, dir_ops, temp_dir):
        """Test that errors include the path in context."""
        non_existent = temp_dir / "does_not_exist"
        
        result = dir_ops.remove_directory(non_existent)
        
        assert result.is_failure()
        error = result.error
        assert "path" in error.context
        assert str(non_existent) in str(error.context["path"])
