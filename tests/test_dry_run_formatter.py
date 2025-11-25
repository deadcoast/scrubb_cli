"""Unit tests for DryRunFormatter."""

import pytest
from pathlib import Path

from scrubb.file_classifier import FileCategory
from scrubb.folder_organizer import (
    DryRunStats,
    DryRunFormatter,
    FileOperation,
    ConflictInfo,
    SkippedFile
)


class TestDryRunFormatter:
    """Tests for DryRunFormatter class."""
    
    def test_all_sections_present_in_output(self):
        """Test that all required sections are present in output."""
        # Create comprehensive stats with all types of data
        stats = DryRunStats(
            files_to_move=3,
            files_by_category={"Docs": 2, "Images": 1},
            empty_folders_to_remove=1,
            file_operations=[
                FileOperation(
                    source=Path("/root/file1.txt"),
                    destination=Path("/root/Scrubbed/Docs/file1.txt"),
                    category=FileCategory.DOCUMENT
                )
            ],
            directories_to_create=[Path("/root/Scrubbed/Docs")],
            directories_to_remove=[Path("/root/empty")],
            conflicts=[
                ConflictInfo(
                    original_name="file.txt",
                    resolved_name="file_1.txt",
                    category="Docs",
                    destination_path=Path("/root/Scrubbed/Docs/file_1.txt")
                )
            ],
            skipped_files=[
                SkippedFile(Path("/root/unknown.xyz"), "Unknown extension")
            ],
            potential_errors=["Permission denied: /root/locked.txt"]
        )
        
        output = DryRunFormatter.format_output(stats, Path("/root"))
        
        # Check for all required sections
        assert "DRY RUN PREVIEW" in output
        assert " SUMMARY" in output
        assert " FILES BY CATEGORY" in output
        assert " DIRECTORIES TO CREATE" in output
        assert " FILE OPERATIONS" in output
        assert "  NAME CONFLICTS" in output
        assert "⏭  SKIPPED FILES" in output
        assert "  EMPTY DIRECTORIES TO REMOVE" in output
        assert " POTENTIAL ERRORS" in output
        assert "This was a DRY RUN" in output
    
    def test_formatting_of_file_operations(self):
        """Test formatting of file operations."""
        stats = DryRunStats(
            files_to_move=2,
            files_by_category={"Docs": 2},
            file_operations=[
                FileOperation(
                    source=Path("/root/file1.txt"),
                    destination=Path("/root/Scrubbed/Docs/file1.txt"),
                    category=FileCategory.DOCUMENT,
                    is_conflict=False
                ),
                FileOperation(
                    source=Path("/root/file2.txt"),
                    destination=Path("/root/Scrubbed/Docs/file2_1.txt"),
                    category=FileCategory.DOCUMENT,
                    is_conflict=True,
                    resolved_name="file2_1.txt"
                )
            ]
        )
        
        output = DryRunFormatter.format_output(stats, Path("/root"))
        
        # Check file operations are listed
        assert "file1.txt" in output
        assert "file2.txt" in output
        assert "[CONFLICT RESOLVED]" in output
        assert "Docs:" in output
    
    def test_formatting_of_conflicts(self):
        """Test formatting of conflicts."""
        stats = DryRunStats(
            conflicts=[
                ConflictInfo(
                    original_name="document.txt",
                    resolved_name="document_1.txt",
                    category="Docs",
                    destination_path=Path("/root/Scrubbed/Docs/document_1.txt")
                ),
                ConflictInfo(
                    original_name="image.jpg",
                    resolved_name="image_1.jpg",
                    category="Images",
                    destination_path=Path("/root/Scrubbed/Images/image_1.jpg")
                )
            ]
        )
        
        output = DryRunFormatter.format_output(stats, Path("/root"))
        
        # Check conflicts are listed
        assert "  NAME CONFLICTS" in output
        assert "document.txt → document_1.txt" in output
        assert "image.jpg → image_1.jpg" in output
        assert "Category: Docs" in output
        assert "Category: Images" in output
    
    def test_formatting_of_skipped_files(self):
        """Test formatting of skipped files."""
        stats = DryRunStats(
            skipped_files=[
                SkippedFile(Path("/root/unknown1.xyz"), "Unknown extension"),
                SkippedFile(Path("/root/unknown2.abc"), "Unknown extension")
            ]
        )
        
        output = DryRunFormatter.format_output(stats, Path("/root"))
        
        # Check skipped files are listed
        assert "⏭  SKIPPED FILES" in output
        assert "unknown1.xyz" in output
        assert "unknown2.abc" in output
        assert "Unknown extension" in output
    
    def test_formatting_of_potential_errors(self):
        """Test formatting of potential errors."""
        stats = DryRunStats(
            potential_errors=[
                "Permission denied: /root/locked.txt",
                "Error accessing /root/missing.txt: File not found"
            ]
        )
        
        output = DryRunFormatter.format_output(stats, Path("/root"))
        
        # Check potential errors are listed
        assert " POTENTIAL ERRORS" in output
        assert "Permission denied: /root/locked.txt" in output
        assert "Error accessing /root/missing.txt" in output
    
    def test_edge_case_no_conflicts(self):
        """Test output when there are no conflicts."""
        stats = DryRunStats(
            files_to_move=2,
            files_by_category={"Docs": 2},
            file_operations=[
                FileOperation(
                    source=Path("/root/file1.txt"),
                    destination=Path("/root/Scrubbed/Docs/file1.txt"),
                    category=FileCategory.DOCUMENT
                )
            ]
        )
        
        output = DryRunFormatter.format_output(stats, Path("/root"))
        
        # Conflicts section should not appear
        assert "  NAME CONFLICTS" not in output
    
    def test_edge_case_no_errors(self):
        """Test output when there are no potential errors."""
        stats = DryRunStats(
            files_to_move=1,
            potential_errors=[]
        )
        
        output = DryRunFormatter.format_output(stats, Path("/root"))
        
        # Should show "No potential errors detected"
        assert " No potential errors detected" in output
        assert " POTENTIAL ERRORS" not in output
    
    def test_edge_case_no_skipped_files(self):
        """Test output when there are no skipped files."""
        stats = DryRunStats(
            files_to_move=2,
            skipped_files=[]
        )
        
        output = DryRunFormatter.format_output(stats, Path("/root"))
        
        # Skipped files section should not appear
        assert "⏭  SKIPPED FILES" not in output
    
    def test_edge_case_empty_stats(self):
        """Test output with completely empty stats."""
        stats = DryRunStats()
        
        output = DryRunFormatter.format_output(stats, Path("/root"))
        
        # Should still have header, summary, and footer
        assert "DRY RUN PREVIEW" in output
        assert " SUMMARY" in output
        assert "Files to move: 0" in output
        assert "This was a DRY RUN" in output
        assert " No potential errors detected" in output
    
    def test_summary_statistics_accuracy(self):
        """Test that summary statistics are accurately displayed."""
        stats = DryRunStats(
            files_to_move=10,
            files_by_category={"Docs": 5, "Images": 3, "Video": 2},
            empty_folders_to_remove=3,
            directories_to_create=[Path("/d1"), Path("/d2")],
            conflicts=[ConflictInfo("f1", "f1_1", "Docs", Path("/d"))],
            skipped_files=[SkippedFile(Path("/s1"), "reason")]
        )
        
        output = DryRunFormatter.format_output(stats, Path("/root"))
        
        # Check all summary values
        assert "Files to move: 10" in output
        assert "Directories to create: 2" in output
        assert "Empty directories to remove: 3" in output
        assert "Files to skip: 1" in output
        assert "Potential conflicts: 1" in output
    
    def test_files_grouped_by_category(self):
        """Test that file operations are grouped by category."""
        stats = DryRunStats(
            files_to_move=4,
            files_by_category={"Docs/Other Docs": 2, "Images": 2},
            file_operations=[
                FileOperation(
                    source=Path("/root/doc1.txt"),
                    destination=Path("/root/Scrubbed/Docs/doc1.txt"),
                    category=FileCategory.DOCUMENT
                ),
                FileOperation(
                    source=Path("/root/img1.jpg"),
                    destination=Path("/root/Scrubbed/Images/img1.jpg"),
                    category=FileCategory.IMAGE
                ),
                FileOperation(
                    source=Path("/root/doc2.txt"),
                    destination=Path("/root/Scrubbed/Docs/doc2.txt"),
                    category=FileCategory.DOCUMENT
                ),
                FileOperation(
                    source=Path("/root/img2.jpg"),
                    destination=Path("/root/Scrubbed/Images/img2.jpg"),
                    category=FileCategory.IMAGE
                )
            ]
        )
        
        output = DryRunFormatter.format_output(stats, Path("/root"))
        
        # Check that categories appear as headers
        assert "Docs/Other Docs:" in output or "Docs:" in output
        assert "Images:" in output
        
        # Check files are listed (they should be in the output somewhere)
        assert "doc1.txt" in output
        assert "doc2.txt" in output
        assert "img1.jpg" in output
        assert "img2.jpg" in output
    
    def test_header_and_footer_formatting(self):
        """Test that header and footer have proper formatting."""
        stats = DryRunStats()
        
        output = DryRunFormatter.format_output(stats, Path("/root"))
        
        # Check header
        assert output.startswith("\n" + "=" * 70)
        assert "DRY RUN PREVIEW - No changes will be made" in output
        
        # Check footer
        assert "This was a DRY RUN - No files were moved or modified" in output
        assert "Run without --dry flag to execute these changes" in output
        assert output.rstrip().endswith("=" * 70)
    
    def test_consistent_path_formatting(self):
        """Test that paths are formatted consistently throughout output."""
        stats = DryRunStats(
            directories_to_create=[
                Path("/root/Scrubbed/Docs"),
                Path("/root/Scrubbed/Images")
            ],
            directories_to_remove=[
                Path("/root/empty1"),
                Path("/root/empty2")
            ],
            file_operations=[
                FileOperation(
                    source=Path("/root/file.txt"),
                    destination=Path("/root/Scrubbed/Docs/file.txt"),
                    category=FileCategory.DOCUMENT
                )
            ]
        )
        
        output = DryRunFormatter.format_output(stats, Path("/root"))
        
        # All paths should be present (platform-independent check)
        assert "Scrubbed" in output and "Docs" in output
        assert "file.txt" in output
        assert "empty1" in output
        assert "empty2" in output
    
    def test_other_category_in_files_by_category(self):
        """Test that OTHER category appears in files by category section."""
        stats = DryRunStats(
            files_to_move=3,
            files_by_category={"Other": 2, "Images": 1},
            file_operations=[
                FileOperation(
                    source=Path("/root/unknown1.xyz"),
                    destination=Path("/root/Scrubbed/Other/unknown1.xyz"),
                    category=FileCategory.OTHER
                ),
                FileOperation(
                    source=Path("/root/unknown2.abc"),
                    destination=Path("/root/Scrubbed/Other/unknown2.abc"),
                    category=FileCategory.OTHER
                ),
                FileOperation(
                    source=Path("/root/image.jpg"),
                    destination=Path("/root/Scrubbed/Images/image.jpg"),
                    category=FileCategory.IMAGE
                )
            ]
        )
        
        output = DryRunFormatter.format_output(stats, Path("/root"))
        
        # Check that "Other" category appears in FILES BY CATEGORY section
        assert " FILES BY CATEGORY" in output
        assert "Other: 2 files" in output
        assert "Images: 1 files" in output
    
    def test_other_category_in_file_operations(self):
        """Test that OTHER category files appear in file operations section."""
        stats = DryRunStats(
            files_to_move=2,
            files_by_category={"Other": 2},
            file_operations=[
                FileOperation(
                    source=Path("/root/unknown1.xyz"),
                    destination=Path("/root/Scrubbed/Other/unknown1.xyz"),
                    category=FileCategory.OTHER
                ),
                FileOperation(
                    source=Path("/root/unknown2.abc"),
                    destination=Path("/root/Scrubbed/Other/unknown2.abc"),
                    category=FileCategory.OTHER
                )
            ]
        )
        
        output = DryRunFormatter.format_output(stats, Path("/root"))
        
        # Check that "Other" category appears as a header in FILE OPERATIONS
        assert " FILE OPERATIONS" in output
        assert "Other:" in output
        
        # Check that files are listed under Other category
        assert "unknown1.xyz" in output
        assert "unknown2.abc" in output
    
    def test_other_category_formatting_consistency(self):
        """Test that OTHER category formatting is consistent with other categories."""
        stats = DryRunStats(
            files_to_move=4,
            files_by_category={"Other": 2, "Images": 1, "Docs/Other Docs": 1},
            file_operations=[
                FileOperation(
                    source=Path("/root/unknown.xyz"),
                    destination=Path("/root/Scrubbed/Other/unknown.xyz"),
                    category=FileCategory.OTHER
                ),
                FileOperation(
                    source=Path("/root/unknown2.abc"),
                    destination=Path("/root/Scrubbed/Other/unknown2.abc"),
                    category=FileCategory.OTHER
                ),
                FileOperation(
                    source=Path("/root/image.jpg"),
                    destination=Path("/root/Scrubbed/Images/image.jpg"),
                    category=FileCategory.IMAGE
                ),
                FileOperation(
                    source=Path("/root/doc.pdf"),
                    destination=Path("/root/Scrubbed/Docs/doc.pdf"),
                    category=FileCategory.DOCUMENT
                )
            ]
        )
        
        output = DryRunFormatter.format_output(stats, Path("/root"))
        
        # Verify all categories appear in FILES BY CATEGORY with same format
        assert "Other: 2 files" in output
        assert "Images: 1 files" in output
        
        # Verify all categories appear as headers in FILE OPERATIONS
        assert "Other:" in output
        assert "Images:" in output
        
        # Verify files are listed under their respective categories
        lines = output.split("\n")
        
        # Find the FILE OPERATIONS section
        in_file_ops = False
        current_category = None
        
        for line in lines:
            if " FILE OPERATIONS" in line:
                in_file_ops = True
                continue
            
            if in_file_ops:
                # Check for category headers
                if "Other:" in line:
                    current_category = "Other"
                elif "Images:" in line:
                    current_category = "Images"
                
                # Verify files appear under correct category
                if current_category == "Other":
                    if "unknown.xyz" in line or "unknown2.abc" in line:
                        assert "→" in line  # Should have arrow showing destination
                elif current_category == "Images":
                    if "image.jpg" in line:
                        assert "→" in line
