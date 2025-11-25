"""File classification module for categorizing files by extension."""

from enum import Enum
from pathlib import Path


class FileCategory(Enum):
    """Categories for file organization."""
    IMAGE = "Images"
    VIDEO = "Video"
    MARKDOWN = "Docs/Markdown"
    DOCUMENT = "Docs/Other Docs"
    DEVELOPMENT = "Development"
    OTHER = "Other"
    UNKNOWN = None  # Deprecated: Use OTHER instead


class FileClassifier:
    """Classifies files based on their extensions."""
    
    def __init__(self):
        """Initialize the file classifier with extension mappings."""
        self.image_extensions = {
            ".jpg", ".jpeg", ".png", ".gif", ".bmp",
            ".svg", ".webp", ".ico", ".tiff", ".tif"
        }
        
        self.video_extensions = {
            ".mp4", ".avi", ".mov", ".mkv", ".flv",
            ".wmv", ".webm", ".m4v", ".mpeg", ".mpg"
        }
        
        self.markdown_extensions = {
            ".md", ".markdown"
        }
        
        self.document_extensions = {
            ".pdf", ".doc", ".docx", ".txt", ".rtf",
            ".odt", ".xls", ".xlsx", ".ppt", ".pptx", ".csv"
        }
        
        self.development_extensions = {
            ".py", ".js", ".ts", ".jsx", ".tsx", ".java",
            ".c", ".cpp", ".h", ".hpp", ".rs", ".go",
            ".rb", ".php", ".html", ".css", ".scss",
            ".json", ".xml", ".yaml", ".yml", ".toml",
            ".sh", ".bash", ".sql", ".r", ".swift", ".kt"
        }
    
    def classify(self, file_path: Path) -> FileCategory:
        """
        Classify a file based on its extension.
        Returns FileCategory.OTHER for unknown extensions instead of UNKNOWN.
        
        Args:
            file_path: Path to the file to classify
            
        Returns:
            FileCategory enum value indicating the file's category
        """
        # Get the extension in lowercase for case-insensitive matching
        extension = file_path.suffix.lower()
        
        # Return OTHER if no extension
        if not extension:
            return FileCategory.OTHER
        
        # Check each category
        if extension in self.image_extensions:
            return FileCategory.IMAGE
        elif extension in self.video_extensions:
            return FileCategory.VIDEO
        elif extension in self.markdown_extensions:
            return FileCategory.MARKDOWN
        elif extension in self.document_extensions:
            return FileCategory.DOCUMENT
        elif extension in self.development_extensions:
            return FileCategory.DEVELOPMENT
        else:
            return FileCategory.OTHER
