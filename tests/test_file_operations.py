"""Unit tests for file operations.

This module tests the RealFileOperations implementation to ensure
it correctly handles file operations and returns proper Result types.
"""

import pytest
import tempfile
import shutil
from pathlib import Path

from scrubb.io.file_operations import RealFileOperations
from scrubb.core.result import Success, Failure
from scrubb.core.errors import FileOperationError


class TestRealFileOperations:
    """Unit tests for RealFileOperations."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing."""
        temp_path = Path(tempfile.mkdtemp())
        yield temp_path
        # Cleanup
        if temp_path.exists():
            shutil.rmtree(temp_path)
    
    @pytest.fixture
    def file_ops(self):
        """Create a RealFileOperations instance."""
        return RealFileOperations()
    
    def test_read_file_success(self, file_ops, temp_dir):
        """Test reading a file successfully."""
        test_file = temp_dir / "test.txt"
        test_content = "Hello, World!"
        test_file.write_text(test_content)
        
        result = file_ops.read_file(test_file)
        
        assert result.is_success()
        assert result.unwrap() == test_content
    
    def test_read_file_not_found(self, file_ops, temp_dir):
        """Test reading a non-existent file fails."""
        non_existent = temp_dir / "does_not_exist.txt"
        
        result = file_ops.read_file(non_existent)
        
        assert result.is_failure()
        assert isinstance(result.error, FileOperationError)
        assert "not found" in result.error.message.lower()
    
    def test_read_file_unicode(self, file_ops, temp_dir):
        """Test reading a file with Unicode content."""
        test_file = temp_dir / "unicode.txt"
        test_content = "Hello 世界 🌍"
        test_file.write_text(test_content, encoding='utf-8')
        
        result = file_ops.read_file(test_file)
        
        assert result.is_success()
        assert result.unwrap() == test_content
    
    def test_write_file_success(self, file_ops, temp_dir):
        """Test writing a file successfully."""
        test_file = temp_dir / "test.txt"
        test_content = "Hello, World!"
        
        result = file_ops.write_file(test_file, test_content)
        
        assert result.is_success()
        assert test_file.exists()
        assert test_file.read_text() == test_content
    
    def test_write_file_creates_parent_directories(self, file_ops, temp_dir):
        """Test writing a file creates parent directories."""
        test_file = temp_dir / "parent" / "child" / "test.txt"
        test_content = "Hello, World!"
        
        result = file_ops.write_file(test_file, test_content)
        
        assert result.is_success()
        assert test_file.exists()
        assert test_file.read_text() == test_content
    
    def test_write_file_overwrites_existing(self, file_ops, temp_dir):
        """Test writing a file overwrites existing content."""
        test_file = temp_dir / "test.txt"
        test_file.write_text("Old content")
        new_content = "New content"
        
        result = file_ops.write_file(test_file, new_content)
        
        assert result.is_success()
        assert test_file.read_text() == new_content
    
    def test_move_file_success(self, file_ops, temp_dir):
        """Test moving a file successfully."""
        source = temp_dir / "source.txt"
        destination = temp_dir / "destination.txt"
        test_content = "Hello, World!"
        source.write_text(test_content)
        
        result = file_ops.move_file(source, destination)
        
        assert result.is_success()
        assert not source.exists()
        assert destination.exists()
        assert destination.read_text() == test_content

    def test_move_file_creates_parent_directories(self, file_ops, temp_dir):
        """Test moving a file creates parent directories."""
        source = temp_dir / "source.txt"
        destination = temp_dir / "parent" / "child" / "destination.txt"
        test_content = "Hello, World!"
        source.write_text(test_content)
        
        result = file_ops.move_file(source, destination)
        
        assert result.is_success()
        assert not source.exists()
        assert destination.exists()
        assert destination.read_text() == test_content
    
    def test_move_file_not_found(self, file_ops, temp_dir):
        """Test moving a non-existent file fails."""
        source = temp_dir / "does_not_exist.txt"
        destination = temp_dir / "destination.txt"
        
        result = file_ops.move_file(source, destination)
        
        assert result.is_failure()
        assert isinstance(result.error, FileOperationError)
        assert "not found" in result.error.message.lower()
    
    def test_delete_file_success(self, file_ops, temp_dir):
        """Test deleting a file successfully."""
        test_file = temp_dir / "test.txt"
        test_file.write_text("Hello, World!")
        
        result = file_ops.delete_file(test_file)
        
        assert result.is_success()
        assert not test_file.exists()
    
    def test_delete_file_not_found(self, file_ops, temp_dir):
        """Test deleting a non-existent file fails."""
        non_existent = temp_dir / "does_not_exist.txt"
        
        result = file_ops.delete_file(non_existent)
        
        assert result.is_failure()
        assert isinstance(result.error, FileOperationError)
        assert "not found" in result.error.message.lower()
    
    def test_delete_file_is_directory(self, file_ops, temp_dir):
        """Test deleting a directory (not a file) fails."""
        test_dir = temp_dir / "test_dir"
        test_dir.mkdir()
        
        result = file_ops.delete_file(test_dir)
        
        assert result.is_failure()
        assert isinstance(result.error, FileOperationError)
        assert "directory" in result.error.message.lower()
    
    def test_file_exists_true(self, file_ops, temp_dir):
        """Test checking if a file exists."""
        test_file = temp_dir / "test.txt"
        test_file.write_text("Hello, World!")
        
        assert file_ops.file_exists(test_file) is True
    
    def test_file_exists_false(self, file_ops, temp_dir):
        """Test checking if a non-existent file exists."""
        non_existent = temp_dir / "does_not_exist.txt"
        
        assert file_ops.file_exists(non_existent) is False
    
    def test_file_exists_directory_not_file(self, file_ops, temp_dir):
        """Test checking if a directory (not file) exists."""
        test_dir = temp_dir / "test_dir"
        test_dir.mkdir()
        
        # Should return False because it's a directory, not a file
        assert file_ops.file_exists(test_dir) is False
    
    def test_get_file_size_success(self, file_ops, temp_dir):
        """Test getting file size successfully."""
        test_file = temp_dir / "test.txt"
        test_content = "Hello, World!"
        test_file.write_text(test_content)
        expected_size = len(test_content.encode('utf-8'))
        
        result = file_ops.get_file_size(test_file)
        
        assert result.is_success()
        assert result.unwrap() == expected_size
    
    def test_get_file_size_empty_file(self, file_ops, temp_dir):
        """Test getting size of an empty file."""
        test_file = temp_dir / "empty.txt"
        test_file.write_text("")
        
        result = file_ops.get_file_size(test_file)
        
        assert result.is_success()
        assert result.unwrap() == 0
    
    def test_get_file_size_not_found(self, file_ops, temp_dir):
        """Test getting size of a non-existent file fails."""
        non_existent = temp_dir / "does_not_exist.txt"
        
        result = file_ops.get_file_size(non_existent)
        
        assert result.is_failure()
        assert isinstance(result.error, FileOperationError)
        assert "not found" in result.error.message.lower()
    
    def test_error_context_includes_path(self, file_ops, temp_dir):
        """Test that errors include the path in context."""
        non_existent = temp_dir / "does_not_exist.txt"
        
        result = file_ops.read_file(non_existent)
        
        assert result.is_failure()
        error = result.error
        assert "path" in error.context
        assert str(non_existent) in str(error.context["path"])
    
    def test_move_file_error_context_includes_both_paths(self, file_ops, temp_dir):
        """Test that move errors include both source and destination in context."""
        source = temp_dir / "does_not_exist.txt"
        destination = temp_dir / "destination.txt"
        
        result = file_ops.move_file(source, destination)
        
        assert result.is_failure()
        error = result.error
        assert "source" in error.context
        assert "destination" in error.context
        assert str(source) in str(error.context["source"])
        assert str(destination) in str(error.context["destination"])
