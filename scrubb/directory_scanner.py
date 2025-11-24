"""Directory scanning and structure collection."""

from datetime import datetime
from pathlib import Path

from scrubb.tree_models import DirectoryNode, DirectorySnapshot
from scrubb.statistics_calculator import StatisticsCalculator


class DirectoryScanner:
    """Scan and collect directory structure information."""
    
    def __init__(self, classifier):
        """Initialize with file classifier for categorization.
        
        Args:
            classifier: FileClassifier instance for file categorization
        """
        self.classifier = classifier
    
    def scan(self, root_path: Path) -> DirectorySnapshot:
        """Scan directory and return snapshot with statistics.
        
        Args:
            root_path: Path to the root directory to scan
            
        Returns:
            DirectorySnapshot containing the directory tree and statistics
        """
        # Build directory tree
        root_node = self._traverse(root_path, depth=0)
        
        # Calculate statistics
        statistics = StatisticsCalculator.calculate(root_node, self.classifier)
        
        # Create and return snapshot
        return DirectorySnapshot(
            root_path=root_path,
            root_node=root_node,
            statistics=statistics,
            timestamp=datetime.now(),
            is_simulated=False
        )
    
    def _traverse(self, path: Path, depth: int = 0) -> DirectoryNode:
        """Recursively traverse directory structure.
        
        Args:
            path: Path to traverse
            depth: Current depth in the directory tree
            
        Returns:
            DirectoryNode representing the path and its children
        """
        # Create node for current path
        node = DirectoryNode(
            path=path,
            name=path.name,
            is_directory=path.is_dir(),
            depth=depth
        )
        
        if path.is_dir():
            # It's a directory - traverse children
            try:
                children = []
                for child_path in sorted(path.iterdir()):
                    try:
                        child_node = self._traverse(child_path, depth + 1)
                        children.append(child_node)
                    except PermissionError:
                        # Handle permission errors for individual children
                        # Create a marker node for restricted access
                        restricted_node = DirectoryNode(
                            path=child_path,
                            name=f"{child_path.name} [Access Denied]",
                            is_directory=child_path.is_dir(),
                            depth=depth + 1,
                            size=0
                        )
                        children.append(restricted_node)
                
                node.children = children
            except PermissionError:
                # Handle permission error for the directory itself
                node.name = f"{node.name} [Access Denied]"
        else:
            # It's a file - get size and classify
            try:
                node.size = path.stat().st_size
                node.category = self.classifier.classify(path)
            except (OSError, PermissionError):
                # If we can't get file info, set size to 0
                node.size = 0
                node.category = None
        
        return node
