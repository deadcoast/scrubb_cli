"""Enhanced file classification with configurable rules.

This module provides a flexible file classification system that supports
priority-based rule ordering and configurable classification rules.
"""

from dataclasses import dataclass
from pathlib import Path
from enum import Enum


class FileCategory(Enum):
    """Categories for file organization."""
    IMAGE = "Images"
    VIDEO = "Video"
    MARKDOWN = "Docs/Markdown"
    DOCUMENT = "Docs/Other Docs"
    DEVELOPMENT = "Development"
    OTHER = "Other"


@dataclass(frozen=True)
class ClassificationRule:
    """Rule for classifying files.
    
    Attributes:
        extensions: Set of file extensions (including the dot, e.g., '.py')
        category: The category to assign to files matching these extensions
        priority: Higher priority rules are checked first (default: 0)
    """
    extensions: frozenset[str]
    category: FileCategory
    priority: int = 0


class EnhancedFileClassifier:
    """Enhanced file classifier with configurable rules.
    
    This classifier supports:
    - Priority-based rule ordering
    - Configurable classification rules
    - Case-insensitive extension matching
    
    Example:
        >>> classifier = EnhancedFileClassifier()
        >>> category = classifier.classify(Path("document.pdf"))
        >>> print(category.value)
        'Docs/Other Docs'
    """
    
    def __init__(self, rules: list[ClassificationRule] | None = None):
        """Initialize classifier with optional custom rules.
        
        Args:
            rules: Optional list of classification rules. If None, uses default rules.
        """
        self.rules = rules if rules is not None else self._default_rules()
        # Sort by priority (highest first)
        self.rules.sort(key=lambda r: r.priority, reverse=True)
    
    def classify(self, path: Path) -> FileCategory:
        """Classify file by extension.
        
        Args:
            path: Path to the file to classify
            
        Returns:
            FileCategory for the file
        """
        extension = path.suffix.lower()
        
        if not extension:
            return FileCategory.OTHER
        
        for rule in self.rules:
            if extension in rule.extensions:
                return rule.category
        
        return FileCategory.OTHER
    
    def get_category_name(self, category: FileCategory) -> str:
        """Get display name for category.
        
        Args:
            category: The file category
            
        Returns:
            Display name for the category
        """
        return category.value
    
    @staticmethod
    def _default_rules() -> list[ClassificationRule]:
        """Default classification rules.
        
        Returns:
            List of default classification rules with standard file extensions
        """
        return [
            ClassificationRule(
                extensions=frozenset({
                    ".jpg", ".jpeg", ".png", ".gif", ".bmp",
                    ".svg", ".webp", ".ico", ".tiff", ".tif"
                }),
                category=FileCategory.IMAGE,
                priority=10
            ),
            ClassificationRule(
                extensions=frozenset({
                    ".mp4", ".avi", ".mov", ".mkv", ".flv",
                    ".wmv", ".webm", ".m4v", ".mpeg", ".mpg"
                }),
                category=FileCategory.VIDEO,
                priority=10
            ),
            ClassificationRule(
                extensions=frozenset({".md", ".markdown"}),
                category=FileCategory.MARKDOWN,
                priority=10
            ),
            ClassificationRule(
                extensions=frozenset({
                    ".pdf", ".doc", ".docx", ".txt", ".rtf",
                    ".odt", ".xls", ".xlsx", ".ppt", ".pptx", ".csv"
                }),
                category=FileCategory.DOCUMENT,
                priority=10
            ),
            ClassificationRule(
                extensions=frozenset({
                    ".py", ".js", ".ts", ".jsx", ".tsx", ".java",
                    ".c", ".cpp", ".h", ".hpp", ".rs", ".go",
                    ".rb", ".php", ".html", ".css", ".scss",
                    ".json", ".xml", ".yaml", ".yml", ".toml",
                    ".sh", ".bash", ".sql", ".r", ".swift", ".kt"
                }),
                category=FileCategory.DEVELOPMENT,
                priority=10
            ),
        ]
