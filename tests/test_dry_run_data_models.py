"""Unit tests for dry-run data models."""

import pytest
from pathlib import Path

from scrubb.file_classifier import FileCategory
from scrubb.folder_organizer import (
    DryRunStats,
    FileOperation,
    ConflictInfo,
    SkippedFile
)


class TestDryRunStats:
    """Tests for DryRunStats dataclass."""
    
    def test_initialization_with_defaults(self):
        """Test DryRunStats initialization and field defaults."""
        stats = DryRunStats()
        
        assert stats.files_to_move == 0
        assert stats.files_by_category == {}
        assert stats.empty_folders_to_remove == 0
        assert stats.file_operations == []
        assert stats.directories_to_create == []
        assert stats.directories_to_remove == []
        assert stats.conflicts == []
        assert stats.skipped_files == []
        assert stats.potential_errors == []
    
    def test_initialization_with_values(self):
        """Test DryRunStats initialization with custom values."""
        file_op = FileOperation(
            source=Path("/src/file.txt"),
            destination=Path("/dst/file.txt"),
            category=FileCategory.DOCUMENT
        )
        
        stats = DryRunStats(
            files_to_move=5,
            files_by_category={"Docs": 3, "Images": 2},
            empty_folders_to_remove=2,
            file_operations=[file_op],
            directories_to_create=[Path("/dst")],
            directories_to_remove=[Path("/empty")],
            conflicts=[],
            skipped_files=[],
            potential_errors=[]
        )
        
        assert stats.files_to_move == 5
        assert stats.files_by_category == {"Docs": 3, "Images": 2}
        assert stats.empty_folders_to_remove == 2
        assert len(stats.file_operations) == 1
        assert len(stats.directories_to_create) == 1
        assert len(stats.directories_to_remove) == 1
    
    def test_mutable_defaults_are_independent(self):
        """Test that default factory creates independent instances."""
        stats1 = DryRunStats()
        stats2 = DryRunStats()
        
        stats1.file_operations.append(FileOperation(
            source=Path("/test.txt"),
            destination=Path("/dst/test.txt"),
            category=FileCategory.DOCUMENT
        ))
        
        assert len(stats1.file_operations) == 1
        assert len(stats2.file_operations) == 0


class TestFileOperation:
    """Tests for FileOperation dataclass."""
    
    def test_creation_without_conflict(self):
        """Test FileOperation creation without conflicts."""
        op = FileOperation(
            source=Path("/src/file.txt"),
            destination=Path("/dst/file.txt"),
            category=FileCategory.DOCUMENT
        )
        
        assert op.source == Path("/src/file.txt")
        assert op.destination == Path("/dst/file.txt")
        assert op.category == FileCategory.DOCUMENT
        assert op.is_conflict is False
        assert op.resolved_name is None
    
    def test_creation_with_conflict(self):
        """Test FileOperation creation with conflict information."""
        op = FileOperation(
            source=Path("/src/file.txt"),
            destination=Path("/dst/file_1.txt"),
            category=FileCategory.DOCUMENT,
            is_conflict=True,
            resolved_name="file_1.txt"
        )
        
        assert op.source == Path("/src/file.txt")
        assert op.destination == Path("/dst/file_1.txt")
        assert op.category == FileCategory.DOCUMENT
        assert op.is_conflict is True
        assert op.resolved_name == "file_1.txt"
    
    def test_different_categories(self):
        """Test FileOperation with different file categories."""
        categories = [
            FileCategory.IMAGE,
            FileCategory.VIDEO,
            FileCategory.MARKDOWN,
            FileCategory.DOCUMENT,
            FileCategory.DEVELOPMENT
        ]
        
        for category in categories:
            op = FileOperation(
                source=Path("/src/file"),
                destination=Path("/dst/file"),
                category=category
            )
            assert op.category == category


class TestConflictInfo:
    """Tests for ConflictInfo dataclass."""
    
    def test_creation(self):
        """Test ConflictInfo creation."""
        conflict = ConflictInfo(
            original_name="file.txt",
            resolved_name="file_1.txt",
            category="Docs",
            destination_path=Path("/dst/Docs/file_1.txt")
        )
        
        assert conflict.original_name == "file.txt"
        assert conflict.resolved_name == "file_1.txt"
        assert conflict.category == "Docs"
        assert conflict.destination_path == Path("/dst/Docs/file_1.txt")
    
    def test_multiple_conflicts(self):
        """Test creating multiple ConflictInfo instances."""
        conflicts = [
            ConflictInfo("file.txt", "file_1.txt", "Docs", Path("/dst/file_1.txt")),
            ConflictInfo("file.txt", "file_2.txt", "Docs", Path("/dst/file_2.txt")),
            ConflictInfo("image.jpg", "image_1.jpg", "Images", Path("/dst/image_1.jpg"))
        ]
        
        assert len(conflicts) == 3
        assert conflicts[0].resolved_name == "file_1.txt"
        assert conflicts[1].resolved_name == "file_2.txt"
        assert conflicts[2].category == "Images"


class TestSkippedFile:
    """Tests for SkippedFile dataclass."""
    
    def test_creation(self):
        """Test SkippedFile creation."""
        skipped = SkippedFile(
            path=Path("/src/unknown.xyz"),
            reason="Unknown extension"
        )
        
        assert skipped.path == Path("/src/unknown.xyz")
        assert skipped.reason == "Unknown extension"
    
    def test_different_reasons(self):
        """Test SkippedFile with different skip reasons."""
        reasons = [
            "Unknown extension",
            "Permission denied",
            "File too large",
            "Invalid filename"
        ]
        
        for reason in reasons:
            skipped = SkippedFile(
                path=Path(f"/src/file_{reason}.txt"),
                reason=reason
            )
            assert skipped.reason == reason
    
    def test_multiple_skipped_files(self):
        """Test creating multiple SkippedFile instances."""
        skipped_files = [
            SkippedFile(Path("/src/file1.xyz"), "Unknown extension"),
            SkippedFile(Path("/src/file2.abc"), "Unknown extension"),
            SkippedFile(Path("/src/file3.def"), "Permission denied")
        ]
        
        assert len(skipped_files) == 3
        assert all(isinstance(sf.path, Path) for sf in skipped_files)
        assert skipped_files[2].reason == "Permission denied"
