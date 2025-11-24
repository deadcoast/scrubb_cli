"""Tree rendering with rich library for professional formatting."""

import logging
from pathlib import Path
from typing import Optional

from scrubb.tree_models import DirectorySnapshot, DirectoryNode
from scrubb.file_classifier import FileCategory

# Set up logging
logger = logging.getLogger(__name__)

try:
    from rich.tree import Tree
    from rich.console import Console
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    logger.warning("rich library not available, falling back to simple tree rendering")


class TreeRenderer:
    """Render directory trees with professional formatting using rich library."""
    
    def __init__(self, max_depth: Optional[int] = None, max_files_per_dir: Optional[int] = None):
        """Initialize renderer with display constraints.
        
        Args:
            max_depth: Maximum depth to display (None for unlimited)
            max_files_per_dir: Maximum files to show per directory (None for unlimited)
        """
        self.max_depth = max_depth
        self.max_files_per_dir = max_files_per_dir
        
        if RICH_AVAILABLE:
            self.console = Console()
        else:
            self.console = None
    
    def render(self, snapshot: DirectorySnapshot, title: str) -> None:
        """Render directory tree to console with title.
        
        Args:
            snapshot: DirectorySnapshot containing the tree to render
            title: Title to display at the top of the tree
        """
        try:
            if not RICH_AVAILABLE or self.console is None:
                # Fall back to simple renderer
                self._render_simple(snapshot, title)
                return
            
            # Create rich Tree with title
            tree = Tree(f"[bold cyan]{title}[/bold cyan]")
            
            # Build the tree structure
            self._build_tree(snapshot.root_node, tree, depth=0)
            
            # Print tree using Console
            self.console.print(tree)
            
        except Exception as e:
            # Handle rendering errors gracefully
            logger.error(f"Failed to render tree: {e}", exc_info=True)
            print(f"\n⚠️  Warning: Tree rendering failed: {e}")
            print(f"Root path: {snapshot.root_path}")
            print("The cleanup operation will continue.\n")
            
            # Try to fall back to simple rendering
            try:
                self._render_simple(snapshot, title)
            except Exception as fallback_error:
                logger.error(f"Fallback rendering also failed: {fallback_error}", exc_info=True)
                print(f"⚠️  Unable to display tree structure. Error: {fallback_error}")
    
    def _render_simple(self, snapshot: DirectorySnapshot, title: str) -> None:
        """Simple fallback renderer when rich is unavailable.
        
        Args:
            snapshot: DirectorySnapshot containing the tree to render
            title: Title to display at the top of the tree
        """
        try:
            print(f"\n{title}")
            print("=" * len(title))
            self._print_simple_tree(snapshot.root_node, prefix="", depth=0)
        except Exception as e:
            logger.error(f"Simple rendering failed: {e}", exc_info=True)
            print(f"⚠️  Unable to render tree: {e}")
    
    def _print_simple_tree(self, node: DirectoryNode, prefix: str, depth: int) -> None:
        """Recursively print tree using simple ASCII characters.
        
        Args:
            node: Current node to print
            prefix: Prefix string for indentation
            depth: Current depth in the tree
        """
        # Check max_depth constraint
        if self.max_depth is not None and depth > self.max_depth:
            return
        
        # Print current node
        if node.is_directory:
            print(f"{prefix}{node.name}/")
        else:
            print(f"{prefix}{node.name}")
        
        # Print children
        if node.is_directory and node.children:
            # Respect max_files_per_dir constraint
            children_to_show = node.children
            if self.max_files_per_dir is not None:
                children_to_show = node.children[:self.max_files_per_dir]
            
            for i, child in enumerate(children_to_show):
                is_last = (i == len(children_to_show) - 1)
                new_prefix = prefix + ("    " if is_last else "|   ")
                child_prefix = prefix + ("+-- " if is_last else "+-- ")
                print(child_prefix, end="")
                self._print_simple_tree(child, "", depth + 1)
            
            # Show ellipsis if truncated
            if self.max_files_per_dir is not None and len(node.children) > self.max_files_per_dir:
                print(f"{prefix}... ({len(node.children) - self.max_files_per_dir} more items)")

    def _build_tree(self, node: DirectoryNode, tree: Tree, depth: int = 0) -> None:
        """Recursively build rich Tree structure.
        
        Args:
            node: Current DirectoryNode to add to tree
            tree: Rich Tree object to add nodes to
            depth: Current depth in the tree
        """
        try:
            # Check max_depth constraint
            if self.max_depth is not None and depth > self.max_depth:
                return
            
            # Process children if this is a directory
            if node.is_directory and node.children:
                # Respect max_files_per_dir constraint
                children_to_show = node.children
                truncated = False
                
                if self.max_files_per_dir is not None and len(node.children) > self.max_files_per_dir:
                    children_to_show = node.children[:self.max_files_per_dir]
                    truncated = True
                
                # Add each child to the tree
                for child in children_to_show:
                    try:
                        if child.is_directory:
                            # Format directory and add as a branch
                            formatted_dir = self._format_directory(child.name, child.is_new)
                            branch = tree.add(formatted_dir)
                            # Recursively build subtree
                            self._build_tree(child, branch, depth + 1)
                        else:
                            # Format file and add as a leaf
                            formatted_file = self._format_file(child.path, child.category)
                            tree.add(formatted_file)
                    except Exception as e:
                        # Log error but continue with other children
                        logger.warning(f"Failed to add node {child.name} to tree: {e}")
                        tree.add(f"[dim]{child.name} [Error][/dim]")
                
                # Add ellipsis for truncated content
                if truncated:
                    remaining = len(node.children) - self.max_files_per_dir
                    tree.add(f"[dim]... ({remaining} more items)[/dim]")
        except Exception as e:
            logger.error(f"Failed to build tree for node {node.name}: {e}", exc_info=True)
            # Don't re-raise, allow rendering to continue

    def _format_file(self, file_path: Path, category: Optional[FileCategory]) -> str:
        """Format file name with color based on category.
        
        Args:
            file_path: Path to the file
            category: FileCategory for the file
            
        Returns:
            Formatted string with rich markup for color
        """
        file_name = file_path.name
        
        # Apply color based on file category
        if category == FileCategory.IMAGE:
            return f"[magenta]{file_name}[/magenta]"
        elif category == FileCategory.VIDEO:
            return f"[blue]{file_name}[/blue]"
        elif category == FileCategory.MARKDOWN:
            return f"[cyan]{file_name}[/cyan]"
        elif category == FileCategory.DOCUMENT:
            return f"[yellow]{file_name}[/yellow]"
        elif category == FileCategory.DEVELOPMENT:
            return f"[green]{file_name}[/green]"
        else:  # UNKNOWN or None
            return f"[white]{file_name}[/white]"

    def _format_directory(self, dir_name: str, is_new: bool = False) -> str:
        """Format directory name with appropriate styling.
        
        Args:
            dir_name: Name of the directory
            is_new: Whether this is a newly created directory
            
        Returns:
            Formatted string with rich markup
        """
        # Apply bold styling for directories
        formatted = f"[bold]{dir_name}/[/bold]"
        
        # Add indicator for new directories
        if is_new:
            formatted = f"[bold green]{dir_name}/ [NEW][/bold green]"
        
        return formatted



class SimpleTreeRenderer:
    """Simple fallback tree renderer using ASCII characters."""
    
    def __init__(self, max_depth: Optional[int] = None, max_files_per_dir: Optional[int] = None):
        """Initialize simple renderer with display constraints.
        
        Args:
            max_depth: Maximum depth to display (None for unlimited)
            max_files_per_dir: Maximum files to show per directory (None for unlimited)
        """
        self.max_depth = max_depth
        self.max_files_per_dir = max_files_per_dir
    
    def render(self, snapshot: DirectorySnapshot, title: str) -> None:
        """Render directory tree using simple ASCII characters.
        
        Args:
            snapshot: DirectorySnapshot containing the tree to render
            title: Title to display at the top of the tree
        """
        try:
            print(f"\n{title}")
            print("=" * len(title))
            self._print_tree(snapshot.root_node, prefix="", is_last=True, depth=0)
        except Exception as e:
            logger.error(f"Simple tree rendering failed: {e}", exc_info=True)
            print(f"\n⚠️  Warning: Unable to render tree: {e}")
            print(f"Root path: {snapshot.root_path}")
            print("The cleanup operation will continue.\n")
    
    def _print_tree(self, node: DirectoryNode, prefix: str, is_last: bool, depth: int) -> None:
        """Recursively print tree using ASCII characters.
        
        Args:
            node: Current node to print
            prefix: Prefix string for indentation
            is_last: Whether this is the last child of its parent
            depth: Current depth in the tree
        """
        # Check max_depth constraint
        if self.max_depth is not None and depth > self.max_depth:
            return
        
        # Print current node
        connector = "+-- " if is_last else "|-- "
        if depth > 0:
            print(f"{prefix}{connector}", end="")
        
        if node.is_directory:
            dir_indicator = " [NEW]" if node.is_new else ""
            print(f"{node.name}/{dir_indicator}")
        else:
            print(f"{node.name}")
        
        # Print children
        if node.is_directory and node.children:
            # Respect max_files_per_dir constraint
            children_to_show = node.children
            truncated = False
            
            if self.max_files_per_dir is not None and len(node.children) > self.max_files_per_dir:
                children_to_show = node.children[:self.max_files_per_dir]
                truncated = True
            
            # Calculate new prefix
            extension = "    " if is_last else "|   "
            new_prefix = prefix + extension if depth > 0 else ""
            
            for i, child in enumerate(children_to_show):
                child_is_last = (i == len(children_to_show) - 1) and not truncated
                self._print_tree(child, new_prefix, child_is_last, depth + 1)
            
            # Show ellipsis if truncated
            if truncated:
                remaining = len(node.children) - self.max_files_per_dir
                ellipsis_connector = "+-- " if True else "|-- "
                print(f"{new_prefix}{ellipsis_connector}... ({remaining} more items)")
