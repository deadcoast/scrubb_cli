"""Property-based tests for FileClassifier functionality."""

import pytest
from pathlib import Path
from hypothesis import given, strategies as st, settings

from scrubb.file_classifier import FileClassifier, FileCategory


# Define known extensions for each category
KNOWN_EXTENSIONS = {
    ".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp", ".ico", ".tiff", ".tif",  # Images
    ".mp4", ".avi", ".mov", ".mkv", ".flv", ".wmv", ".webm", ".m4v", ".mpeg", ".mpg",  # Video
    ".md", ".markdown",  # Markdown
    ".pdf", ".doc", ".docx", ".txt", ".rtf", ".odt", ".xls", ".xlsx", ".ppt", ".pptx", ".csv",  # Documents
    ".py", ".js", ".ts", ".jsx", ".tsx", ".java", ".c", ".cpp", ".h", ".hpp", ".rs", ".go",  # Development
    ".rb", ".php", ".html", ".css", ".scss", ".json", ".xml", ".yaml", ".yml", ".toml",
    ".sh", ".bash", ".sql", ".r", ".swift", ".kt"
}


@st.composite
def unknown_extension(draw):
    """Generate file extensions that are not in the known categories."""
    # Generate random extension that's not in KNOWN_EXTENSIONS
    # Use alphanumeric characters for the extension
    ext_name = draw(st.text(
        alphabet="abcdefghijklmnopqrstuvwxyz0123456789",
        min_size=1,
        max_size=10
    ))
    extension = f".{ext_name}"
    
    # Ensure it's not in known extensions (case-insensitive)
    if extension.lower() not in KNOWN_EXTENSIONS:
        return extension
    else:
        # If by chance we generated a known extension, use a guaranteed unknown one
        return ".unknownext123"


@st.composite
def filename_without_extension(draw):
    """Generate filenames without extensions."""
    # Generate filename with ASCII characters only
    name = draw(st.text(
        alphabet="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-",
        min_size=1,
        max_size=20
    ))
    return name


class TestOtherCategoryAssignment:
    """Property tests for OTHER category assignment."""
    
    @settings(max_examples=100)
    @given(extension=unknown_extension())
    def test_unknown_extensions_return_other(self, extension):
        """
        **Feature: unknown-file-handling, Property 2: OTHER category assignment**
        **Validates: Requirements 1.1, 2.3**
        
        For any file with an extension not in the predefined category mappings,
        the FileClassifier SHALL return FileCategory.OTHER.
        """
        classifier = FileClassifier()
        
        # Create a file path with the unknown extension
        filename = f"testfile{extension}"
        file_path = Path(filename)
        
        # Classify the file
        result = classifier.classify(file_path)
        
        # Verify it returns OTHER
        assert result == FileCategory.OTHER, \
            f"File with unknown extension '{extension}' should return OTHER, got {result}"
    
    @settings(max_examples=100)
    @given(filename=filename_without_extension())
    def test_files_without_extension_return_other(self, filename):
        """
        **Feature: unknown-file-handling, Property 2: OTHER category assignment**
        **Validates: Requirements 1.1, 2.3**
        
        For any file with no extension, the FileClassifier SHALL return
        FileCategory.OTHER.
        """
        classifier = FileClassifier()
        
        # Create a file path without extension
        file_path = Path(filename)
        
        # Classify the file
        result = classifier.classify(file_path)
        
        # Verify it returns OTHER
        assert result == FileCategory.OTHER, \
            f"File without extension '{filename}' should return OTHER, got {result}"
