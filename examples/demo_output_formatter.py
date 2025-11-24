"""Demo script to showcase the OutputFormatter functionality."""

from pathlib import Path
from scrubb.output_formatter import OutputFormatter

def main():
    """Demonstrate the OutputFormatter capabilities."""
    formatter = OutputFormatter()
    
    print("\n" + "="*60)
    print("OutputFormatter Demo")
    print("="*60 + "\n")
    
    # Success message
    formatter.print_success("Successfully processed 42 files")
    
    # Info message
    formatter.print_info("Starting file organization process...")
    
    # Warning message
    formatter.print_warning("Some files were skipped due to permissions")
    
    # Error message with suggestion
    formatter.print_error(
        "Failed to access directory: /invalid/path",
        suggestion="Check that the path exists and you have read permissions"
    )
    
    # Statistics table
    print("\n")
    stats = {
        "files_processed": 150,
        "files_modified": 42,
        "files_skipped": 8,
        "errors": 2,
        "emojis_removed": 327
    }
    table = formatter.create_stats_table(stats)
    formatter.console.print(table)
    
    # Panel
    print("\n")
    panel = formatter.create_panel(
        "This is a grouped information panel\nwith multiple lines of content",
        title="Information",
        border_style="cyan"
    )
    formatter.console.print(panel)
    
    # File lists with different statuses
    print("\n")
    modified_files = [
        "src/main.py",
        "docs/README.md",
        "tests/test_example.py"
    ]
    formatter.print_file_list(modified_files, status="modified", title="Modified Files")
    
    print("\n")
    error_files = [
        "data/locked_file.txt",
        "config/protected.json"
    ]
    formatter.print_file_list(error_files, status="error", title="Error Files")
    
    print("\n")
    moved_files = [
        "images/photo1.jpg",
        "images/photo2.png",
        "videos/clip.mp4"
    ]
    formatter.print_file_list(moved_files, status="moved", title="Moved Files")
    
    print("\n" + "="*60)
    print("Demo Complete!")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()
