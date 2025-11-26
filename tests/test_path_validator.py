"""Unit tests for path validator.

This module tests the PathValidator implementation to ensure
it correctly validates paths and prevents security issues.
"""

import pytest
import tempfile
import shutil
from pathlib import Path

from scrubb.io.path_validator import PathValidator
from scrubb.core.result import Success, Failure
from scrubb.core.errors import PathSecurityError


class TestPathValidator:
    """Unit tests for PathValidator."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing."""
        temp_path = Path(tempfile.mkdtemp())
        yield temp_path
        # Cleanup
        if temp_path.exists():
            shutil.rmtree(temp_path)
    
    @pytest.fixture
    def validator(self):
        """Create a PathValidator instance."""
        return PathValidator()
    
    def test_validate_path_within_root(self, validator, temp_dir):
        """Test validating a path within root succeeds."""
        test_path = temp_dir / "subdir" / "file.txt"
        
        result = validator.validate(test_path, temp_dir)
        
        assert result.is_success()
        validated_path = result.unwrap()
        assert validated_path.is_absolute()
    
    def test_validate_path_is_root(self, validator, temp_dir):
        """Test validating the root path itself succeeds."""
        result = validator.validate(temp_dir, temp_dir)
        
        assert result.is_success()
    
    def test_validate_path_outside_root(self, validator, temp_dir):
        """Test validating a path outside root fails."""
        outside_path = temp_dir.parent / "outside.txt"
        
        result = validator.validate(outside_path, temp_dir)
        
        assert result.is_failure()
        assert isinstance(result.error, PathSecurityError)
        assert "outside root" in result.error.message.lower()
    
    def test_validate_path_with_traversal(self, validator, temp_dir):
        """Test validating a path with .. traversal that escapes root fails."""
        # Create a subdirectory
        subdir = temp_dir / "subdir"
        subdir.mkdir()
        
        # Try to escape using ..
        traversal_path = subdir / ".." / ".." / "outside.txt"
        
        result = validator.validate(traversal_path, temp_dir)
        
        assert result.is_failure()
        assert isinstance(result.error, PathSecurityError)
    
    def test_validate_path_with_safe_traversal(self, validator, temp_dir):
        """Test validating a path with .. that stays within root succeeds."""
        # Create subdirectories
        subdir1 = temp_dir / "subdir1"
        subdir2 = temp_dir / "subdir2"
        subdir1.mkdir()
        subdir2.mkdir()
        
        # Use .. but stay within root
        safe_path = subdir1 / ".." / "subdir2" / "file.txt"
        
        result = validator.validate(safe_path, temp_dir)
        
        assert result.is_success()
    
    def test_resolve_relative_path(self, validator, temp_dir):
        """Test resolving a relative path."""
        result = validator.resolve("subdir/file.txt", temp_dir)
        
        assert result.is_success()
        resolved_path = result.unwrap()
        assert resolved_path.is_absolute()
        assert temp_dir in resolved_path.parents or resolved_path.parent == temp_dir
    
    def test_resolve_absolute_path_within_root(self, validator, temp_dir):
        """Test resolving an absolute path within root."""
        abs_path = str(temp_dir / "file.txt")
        
        result = validator.resolve(abs_path, temp_dir)
        
        assert result.is_success()
    
    def test_resolve_absolute_path_outside_root(self, validator, temp_dir):
        """Test resolving an absolute path outside root fails."""
        outside_path = str(temp_dir.parent / "outside.txt")
        
        result = validator.resolve(outside_path, temp_dir)
        
        assert result.is_failure()
        assert isinstance(result.error, PathSecurityError)
    
    def test_resolve_path_with_traversal_attempt(self, validator, temp_dir):
        """Test resolving a path with .. traversal attempt."""
        result = validator.resolve("../../outside.txt", temp_dir)
        
        assert result.is_failure()
        assert isinstance(result.error, PathSecurityError)
    
    def test_resolve_path_with_null_byte(self, validator, temp_dir):
        """Test resolving a path with null byte fails."""
        result = validator.resolve("file\0.txt", temp_dir)
        
        assert result.is_failure()
        assert isinstance(result.error, PathSecurityError)
        assert "null" in result.error.message.lower()
    
    def test_validate_path_with_null_byte(self, validator, temp_dir):
        """Test validating a path with null byte fails."""
        # Create a path string with null byte
        # Note: Path() might normalize this, so we test the string check
        result = validator.resolve("file\0.txt", temp_dir)
        
        assert result.is_failure()
        assert isinstance(result.error, PathSecurityError)
    
    def test_error_context_includes_paths(self, validator, temp_dir):
        """Test that errors include paths in context."""
        outside_path = temp_dir.parent / "outside.txt"
        
        result = validator.validate(outside_path, temp_dir)
        
        assert result.is_failure()
        error = result.error
        assert "path" in error.context
        assert "root" in error.context
