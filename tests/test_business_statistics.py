"""Unit tests for the new business layer StatisticsCalculator."""

import pytest
from pathlib import Path

from scrubb.business.statistics import StatisticsCalculator
from scrubb.tree_models import DirectoryNode, DirectoryStatistics
from scrubb.file_classifier import FileCategory
from scrubb.core.errors import ValidationError


class TestStatisticsCalculatorValidation:
    """Test that StatisticsCalculator validates inputs and fails fast."""
    
    def test_calculate_with_none_raises_validation_error(self):
        """Verify that passing None to calculate raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            StatisticsCalculator.calculate(None)
        
        assert "root_node cannot be None" in str(exc_info.value)
    
    def test_calculate_with_invalid_type_raises_validation_error(self):
        """Verify that passing wrong type to calculate raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            StatisticsCalculator.calculate("not a node")
        
        assert "must be DirectoryNode" in str(exc_info.value)
    
    def test_calculate_delta_with_none_before_raises_validation_error(self):
        """Verify that passing None as before raises ValidationError."""
        stats = DirectoryStatistics()
        
        with pytest.raises(ValidationError) as exc_info:
            StatisticsCalculator.calculate_delta(None, stats)
        
        assert "before cannot be None" in str(exc_info.value)
    
    def test_calculate_delta_with_none_after_raises_validation_error(self):
        """Verify that passing None as after raises ValidationError."""
        stats = DirectoryStatistics()
        
        with pytest.raises(ValidationError) as exc_info:
            StatisticsCalculator.calculate_delta(stats, None)
        
        assert "after cannot be None" in str(exc_info.value)
    
    def test_format_size_with_negative_raises_validation_error(self):
        """Verify that passing negative size raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            StatisticsCalculator.format_size(-100)
        
        assert "must be non-negative" in str(exc_info.value)
    
    def test_calculate_with_valid_tree(self):
        """Verify that calculate works with valid tree."""
        # Create a simple valid tree
        root = DirectoryNode(
            path=Path("/test"),
            name="test",
            is_directory=True,
            size=0,
            children=[
                DirectoryNode(
                    path=Path("/test/file1.txt"),
                    name="file1.txt",
                    is_directory=False,
                    size=100,
                    category=FileCategory.DOCUMENT,
                    depth=1
                ),
                DirectoryNode(
                    path=Path("/test/file2.py"),
                    name="file2.py",
                    is_directory=False,
                    size=200,
                    category=FileCategory.DEVELOPMENT,
                    depth=1
                )
            ],
            depth=0
        )
        
        stats = StatisticsCalculator.calculate(root)
        
        assert stats.total_files == 2
        assert stats.total_directories == 1
        assert stats.total_size == 300
        assert stats.max_depth == 1
        assert stats.files_by_category["Docs/Other Docs"] == 1
        assert stats.files_by_category["Development"] == 1
    
    def test_format_size_with_valid_values(self):
        """Verify that format_size works with valid values."""
        assert StatisticsCalculator.format_size(0) == "0 B"
        assert StatisticsCalculator.format_size(500) == "500 B"
        assert StatisticsCalculator.format_size(1024) == "1.00 KB"
        assert StatisticsCalculator.format_size(1024 * 1024) == "1.00 MB"
        assert StatisticsCalculator.format_size(1024 * 1024 * 1024) == "1.00 GB"
