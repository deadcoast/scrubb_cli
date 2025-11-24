"""Data models for tree visualization feature."""

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from scrubb.file_classifier import FileCategory


@dataclass
class DirectoryNode:
    """Node in directory tree structure."""
    path: Path
    name: str
    is_directory: bool
    size: int = 0
    children: List['DirectoryNode'] = field(default_factory=list)
    category: Optional[FileCategory] = None
    depth: int = 0
    is_new: bool = False
    is_removed: bool = False
    
    def __post_init__(self):
        """Validate DirectoryNode after initialization."""
        # Validate that path is a Path object
        if not isinstance(self.path, Path):
            raise TypeError(f"path must be a Path object, got {type(self.path)}")
        
        # Validate that name is a string
        if not isinstance(self.name, str):
            raise TypeError(f"name must be a string, got {type(self.name)}")
        
        # Validate that size is non-negative
        if self.size < 0:
            raise ValueError(f"size must be non-negative, got {self.size}")
        
        # Validate that depth is non-negative
        if self.depth < 0:
            raise ValueError(f"depth must be non-negative, got {self.depth}")
        
        # Validate that directories have no category
        if self.is_directory and self.category is not None:
            raise ValueError("Directories should not have a category")
        
        # Validate that files have size >= 0
        if not self.is_directory and self.size < 0:
            raise ValueError(f"File size must be non-negative, got {self.size}")


@dataclass
class DirectoryStatistics:
    """Statistics for directory structure."""
    total_files: int = 0
    total_directories: int = 0
    total_size: int = 0
    max_depth: int = 0
    files_by_category: Dict[str, int] = field(default_factory=dict)
    size_by_category: Dict[str, int] = field(default_factory=dict)


@dataclass
class StatisticsDelta:
    """Delta between two directory states."""
    files_delta: int
    directories_delta: int
    size_delta: int
    depth_delta: int
    category_deltas: Dict[str, int] = field(default_factory=dict)
    
    def format_delta_value(self, value: int) -> str:
        """
        Format delta with +/- prefix and color.
        
        Args:
            value: The delta value to format
            
        Returns:
            Formatted string with rich markup for color
        """
        if value > 0:
            return f"[green]+{value}[/green]"
        elif value < 0:
            return f"[red]{value}[/red]"
        else:
            return f"[dim]{value}[/dim]"


@dataclass
class DirectorySnapshot:
    """Complete snapshot of directory state."""
    root_path: Path
    root_node: DirectoryNode
    statistics: DirectoryStatistics
    timestamp: datetime
    is_simulated: bool = False
