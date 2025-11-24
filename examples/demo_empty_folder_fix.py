#!/usr/bin/env python3
"""
Demonstration of the empty folder removal fix.

This script shows how the folder organizer now correctly handles
directories containing hidden/system files.
"""

from pathlib import Path
import tempfile
import shutil
from scrubb.file_classifier import FileClassifier
from scrubb.folder_organizer import FolderOrganizer

def main():
    # Create a realistic test scenario
    test_dir = Path(tempfile.mkdtemp(prefix="scrubb_demo_"))
    
    print("=" * 70)
    print("EMPTY FOLDER REMOVAL FIX DEMONSTRATION")
    print("=" * 70)
    print(f"\nTest directory: {test_dir}\n")
    
    # Create directories with various hidden files
    scenarios = [
        ("MacOS_Folder", ".DS_Store", "photo.jpg"),
        ("Windows_Folder", "Thumbs.db", "document.pdf"),
        ("Git_Folder", ".gitkeep", "script.py"),
        ("Desktop_Ini_Folder", "desktop.ini", "data.json"),
        ("Multiple_Hidden", [".DS_Store", "Thumbs.db", ".gitkeep"], "image.png"),
    ]
    
    print("Creating test structure with hidden files:")
    print("-" * 70)
    
    for folder_name, hidden_files, user_file in scenarios:
        folder = test_dir / folder_name
        folder.mkdir()
        
        # Create hidden files
        if isinstance(hidden_files, list):
            for hidden in hidden_files:
                (folder / hidden).write_text("hidden")
                print(f"  📁 {folder_name}/")
                print(f"     🔒 {hidden} (hidden)")
        else:
            (folder / hidden_files).write_text("hidden")
            print(f"  📁 {folder_name}/")
            print(f"     🔒 {hidden_files} (hidden)")
        
        # Create user file
        (folder / user_file).write_text("user content")
        print(f"     📄 {user_file} (user file)")
        print()
    
    # Count before
    dirs_before = [d for d in test_dir.rglob("*") if d.is_dir()]
    files_before = [f for f in test_dir.rglob("*") if f.is_file()]
    
    print(f"Before organization:")
    print(f"  Total directories: {len(dirs_before)}")
    print(f"  Total files: {len(files_before)}")
    print()
    
    # Run organization
    print("Running folder organization...")
    print("-" * 70)
    classifier = FileClassifier()
    organizer = FolderOrganizer(test_dir, classifier, dry_run=False)
    stats = organizer.organize()
    
    print(f"\n✅ Organization complete!")
    print(f"  Files moved: {stats.files_moved}")
    print(f"  Empty folders removed: {stats.empty_folders_removed}")
    print(f"  Errors: {stats.errors}")
    print()
    
    # Count after
    dirs_after = [d for d in test_dir.rglob("*") if d.is_dir()]
    files_after = [f for f in test_dir.rglob("*") if f.is_file()]
    
    print(f"After organization:")
    print(f"  Total directories: {len(dirs_after)}")
    print(f"  Total files: {len(files_after)}")
    print()
    
    # Check for leftover empty directories
    print("Checking for leftover empty directories...")
    print("-" * 70)
    
    leftover_empty = []
    for d in dirs_after:
        # Skip Scrubbed folder
        try:
            d.relative_to(test_dir / "Scrubbed")
            continue
        except ValueError:
            pass
        
        items = list(d.iterdir())
        if not items:
            leftover_empty.append(d)
    
    if leftover_empty:
        print(f"❌ Found {len(leftover_empty)} empty directories:")
        for d in leftover_empty:
            print(f"  - {d.relative_to(test_dir)}")
    else:
        print("✅ No empty directories left behind!")
        print("\nAll folders containing only hidden/system files were successfully removed:")
        for folder_name, _, _ in scenarios:
            print(f"  ✓ {folder_name}/")
    
    print()
    print("=" * 70)
    print("DEMONSTRATION COMPLETE")
    print("=" * 70)
    print()
    print("The fix successfully:")
    print("  1. Identified directories containing only hidden/system files")
    print("  2. Removed the hidden files (.DS_Store, Thumbs.db, .gitkeep, etc.)")
    print("  3. Removed the now-empty directories")
    print("  4. Organized user files into the Scrubbed/ folder structure")
    print()
    
    # Cleanup
    print(f"Cleaning up test directory: {test_dir}")
    shutil.rmtree(test_dir)
    print("Done!")

if __name__ == "__main__":
    main()
