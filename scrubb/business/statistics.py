"""Statistics calculation for directory trees.

This module provides clean statistics calculation without theatrical error handling.
All validation happens at boundaries, and invalid data causes immediate failures.
"""

from dataclasses import dataclass, field
from typing import Dict

from scrubb.tree_models import DirectoryNode, DirectoryStatistics, StatisticsDelta
from scrubb.core.errors import ValidationError


class StatisticsCalculator:
    """Calculate comprehensive directory statistics with fail-fast validation."""
    
    @staticmethod
    def calculate(root_node: DirectoryNode) -> DirectoryStatistics:
        """Calculate statistics from directory tree in a single traversal.
        
        This method validates input at the boundary and fails fast on invalid data.
        No try-except blocks around arithmetic - if data is invalid, we want to know.
        
        Args:
            root_node: Root node of the directory tree
            
        Returns:
            DirectoryStatistics with comprehensive metrics
            
        Raises:
            ValidationError: If root_node is None or invalid
            TypeError: If node structure is invalid
            ValueError: If node data is invalid (negative sizes, etc.)
        """
        # Validate input at boundary
        if root_node is None:
            raise ValidationError(
                "root_node cannot be None",
                context={"parameter": "root_node"}
            )
        
        if not isinstance(root_node, DirectoryNode):
            raise ValidationError(
                f"root_node must be DirectoryNode, got {type(root_node).__name__}",
                context={"parameter": "root_node", "type": type(root_node).__name__}
            )
        
        # Initialize statistics
        stats = DirectoryStatistics()
        
        # Single traversal to collect all statistics
        def traverse(node: DirectoryNode) -> None:
            """Recursively traverse tree to collect statistics."""
            # DirectoryNode.__post_init__ already validates the node structure,
            # so we can trust the data here. If it's invalid, it will have
            # failed at construction time.
            
            if node.is_directory:
                stats.total_directories += 1
                # Update max depth
                if node.depth > stats.max_depth:
                    stats.max_depth = node.depth
                # Traverse children
                for child in node.children:
                    traverse(child)
            else:
                # It's a file
                stats.total_files += 1
                
                # Add size (no try-except - fail fast if invalid)
                stats.total_size += node.size
                
                # Update max depth for files too
                if node.depth > stats.max_depth:
                    stats.max_depth = node.depth
                
                # Categorize file
                if node.category:
                    category_name = node.category.value
                else:
                    category_name = "Unknown"
                
                # Update category counts (no try-except - fail fast)
                stats.files_by_category[category_name] = \
                    stats.files_by_category.get(category_name, 0) + 1
                stats.size_by_category[category_name] = \
                    stats.size_by_category.get(category_name, 0) + node.size
        
        # Execute traversal
        traverse(root_node)
        
        return stats
    
    @staticmethod
    def calculate_delta(before: DirectoryStatistics, after: DirectoryStatistics) -> StatisticsDelta:
        """Calculate differences between two directory states.
        
        Validates inputs at boundary and fails fast on invalid data.
        
        Args:
            before: Statistics from before state
            after: Statistics from after state
            
        Returns:
            StatisticsDelta with all delta values
            
        Raises:
            ValidationError: If before or after is None or invalid
        """
        # Validate inputs at boundary
        if before is None:
            raise ValidationError(
                "before cannot be None",
                context={"parameter": "before"}
            )
        
        if after is None:
            raise ValidationError(
                "after cannot be None",
                context={"parameter": "after"}
            )
        
        if not isinstance(before, DirectoryStatistics):
            raise ValidationError(
                f"before must be DirectoryStatistics, got {type(before).__name__}",
                context={"parameter": "before", "type": type(before).__name__}
            )
        
        if not isinstance(after, DirectoryStatistics):
            raise ValidationError(
                f"after must be DirectoryStatistics, got {type(after).__name__}",
                context={"parameter": "after", "type": type(after).__name__}
            )
        
        # Calculate basic deltas (no try-except - fail fast)
        files_delta = after.total_files - before.total_files
        directories_delta = after.total_directories - before.total_directories
        size_delta = after.total_size - before.total_size
        depth_delta = after.max_depth - before.max_depth
        
        # Calculate category deltas
        category_deltas: Dict[str, int] = {}
        all_categories = set(before.files_by_category.keys()) | set(after.files_by_category.keys())
        
        for category in all_categories:
            before_count = before.files_by_category.get(category, 0)
            after_count = after.files_by_category.get(category, 0)
            category_deltas[category] = after_count - before_count
        
        return StatisticsDelta(
            files_delta=files_delta,
            directories_delta=directories_delta,
            size_delta=size_delta,
            depth_delta=depth_delta,
            category_deltas=category_deltas
        )
    
    @staticmethod
    def format_size(bytes_value: int) -> str:
        """Format byte size in human-readable format (B, KB, MB, GB, TB).
        
        Args:
            bytes_value: Size in bytes
            
        Returns:
            Human-readable size string
            
        Raises:
            ValidationError: If bytes_value is negative
        """
        # Validate input at boundary
        if bytes_value < 0:
            raise ValidationError(
                f"bytes_value must be non-negative, got {bytes_value}",
                context={"parameter": "bytes_value", "value": bytes_value}
            )
        
        units = ['B', 'KB', 'MB', 'GB', 'TB']
        size = float(bytes_value)
        unit_index = 0
        
        while size >= 1024.0 and unit_index < len(units) - 1:
            size /= 1024.0
            unit_index += 1
        
        if unit_index == 0:
            return f"{int(size)} {units[unit_index]}"
        else:
            return f"{size:.2f} {units[unit_index]}"
