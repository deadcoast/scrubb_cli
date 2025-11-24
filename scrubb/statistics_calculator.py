"""Calculate comprehensive directory statistics."""

import logging
from scrubb.tree_models import DirectoryNode, DirectoryStatistics, StatisticsDelta
from scrubb.file_classifier import FileClassifier

# Set up logging
logger = logging.getLogger(__name__)


class StatisticsCalculator:
    """Calculate comprehensive directory statistics."""
    
    @staticmethod
    def calculate(root_node: DirectoryNode, classifier: FileClassifier) -> DirectoryStatistics:
        """Calculate statistics from directory tree.
        
        Args:
            root_node: Root node of the directory tree
            classifier: FileClassifier instance for categorizing files
            
        Returns:
            DirectoryStatistics with comprehensive metrics (may be partial if errors occur)
        """
        stats = DirectoryStatistics()
        error_count = 0
        
        def traverse(node: DirectoryNode):
            """Recursively traverse tree to collect statistics."""
            nonlocal error_count
            
            try:
                if node.is_directory:
                    stats.total_directories += 1
                    # Update max depth
                    if node.depth > stats.max_depth:
                        stats.max_depth = node.depth
                    # Traverse children
                    for child in node.children:
                        try:
                            traverse(child)
                        except Exception as e:
                            error_count += 1
                            logger.warning(f"Failed to process child node {child.name}: {e}")
                else:
                    # It's a file
                    stats.total_files += 1
                    
                    # Safely add size
                    try:
                        stats.total_size += node.size
                    except (TypeError, ValueError) as e:
                        logger.warning(f"Invalid size for file {node.name}: {e}")
                        error_count += 1
                    
                    # Update max depth for files too
                    if node.depth > stats.max_depth:
                        stats.max_depth = node.depth
                    
                    # Categorize file
                    try:
                        if node.category:
                            category_name = node.category.value if node.category.value else "Unknown"
                        else:
                            category_name = "Unknown"
                        
                        # Update category counts
                        stats.files_by_category[category_name] = stats.files_by_category.get(category_name, 0) + 1
                        stats.size_by_category[category_name] = stats.size_by_category.get(category_name, 0) + node.size
                    except Exception as e:
                        logger.warning(f"Failed to categorize file {node.name}: {e}")
                        error_count += 1
                        # Add to Unknown category
                        stats.files_by_category["Unknown"] = stats.files_by_category.get("Unknown", 0) + 1
                        stats.size_by_category["Unknown"] = stats.size_by_category.get("Unknown", 0) + node.size
            except Exception as e:
                error_count += 1
                logger.error(f"Failed to process node {node.name}: {e}", exc_info=True)
        
        try:
            traverse(root_node)
        except Exception as e:
            logger.error(f"Statistics calculation failed: {e}", exc_info=True)
            print(f"\n⚠️  Warning: Statistics calculation encountered errors.")
            print(f"Partial statistics will be displayed.\n")
        
        if error_count > 0:
            logger.warning(f"Statistics calculation completed with {error_count} errors")
            print(f"\n⚠️  Warning: {error_count} errors occurred during statistics calculation.")
            print(f"Statistics may be incomplete.\n")
        
        return stats
    
    @staticmethod
    def calculate_delta(before: DirectoryStatistics, after: DirectoryStatistics) -> StatisticsDelta:
        """Calculate differences between two directory states.
        
        Args:
            before: Statistics from before state
            after: Statistics from after state
            
        Returns:
            StatisticsDelta with all delta values (may have partial data if errors occur)
        """
        try:
            # Calculate basic deltas
            files_delta = after.total_files - before.total_files
            directories_delta = after.total_directories - before.total_directories
            size_delta = after.total_size - before.total_size
            depth_delta = after.max_depth - before.max_depth
            
            # Calculate category deltas
            category_deltas = {}
            all_categories = set(before.files_by_category.keys()) | set(after.files_by_category.keys())
            
            for category in all_categories:
                try:
                    before_count = before.files_by_category.get(category, 0)
                    after_count = after.files_by_category.get(category, 0)
                    category_deltas[category] = after_count - before_count
                except Exception as e:
                    logger.warning(f"Failed to calculate delta for category {category}: {e}")
                    category_deltas[category] = 0
            
            return StatisticsDelta(
                files_delta=files_delta,
                directories_delta=directories_delta,
                size_delta=size_delta,
                depth_delta=depth_delta,
                category_deltas=category_deltas
            )
        except Exception as e:
            logger.error(f"Delta calculation failed: {e}", exc_info=True)
            print(f"\n⚠️  Warning: Failed to calculate statistics delta: {e}")
            print(f"Returning zero deltas.\n")
            # Return zero deltas as fallback
            return StatisticsDelta(
                files_delta=0,
                directories_delta=0,
                size_delta=0,
                depth_delta=0,
                category_deltas={}
            )
    
    @staticmethod
    def format_size(bytes_value: int) -> str:
        """Format byte size in human-readable format (B, KB, MB, GB, TB).
        
        Args:
            bytes_value: Size in bytes
            
        Returns:
            Human-readable size string
        """
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
