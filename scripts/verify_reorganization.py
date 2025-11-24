#!/usr/bin/env python3
"""
Verification script for codebase reorganization.
Validates that all requirements have been met.
"""

import os
import sys
from pathlib import Path
from typing import List, Tuple, Dict
import re


class ReorganizationVerifier:
    def __init__(self, root_path: Path):
        self.root = root_path
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.successes: List[str] = []
    
    def verify_all(self) -> bool:
        """Run all verification checks."""
        print("=" * 70)
        print("CODEBASE REORGANIZATION VERIFICATION")
        print("=" * 70)
        print()
        
        self.verify_directory_structure()
        self.verify_file_locations()
        self.verify_documentation_links()
        self.verify_core_preservation()
        
        return self.print_report()
    
    def verify_directory_structure(self):
        """Verify all new directories exist (Requirement 1)."""
        print("📁 Verifying directory structure...")
        
        required_dirs = [
            "docs",
            "docs/dev",
            "examples",
            "scripts",
            # Existing directories that should be preserved
            ".archive",
            ".kiro",
            "scrubb",
            "tests",
        ]
        
        for dir_path in required_dirs:
            full_path = self.root / dir_path
            if full_path.exists() and full_path.is_dir():
                self.successes.append(f"✓ Directory exists: {dir_path}")
            else:
                self.errors.append(f"✗ Missing directory: {dir_path}")
        
        print()
    
    def verify_file_locations(self):
        """Verify all files are in correct locations (Requirements 2, 3, 7, 8)."""
        print("📄 Verifying file locations...")
        
        expected_files = {
            # Documentation files (Requirement 2)
            "docs/COMMAND_REFERENCE.md": "User documentation",
            "docs/dev/DOCUMENTATION_VALIDATION_PLAN.md": "Developer documentation",
            "docs/dev/EMPTY_FOLDER_FIX.md": "Developer documentation",
            "docs/dev/FIXES_SUMMARY.md": "Developer documentation",
            
            # Utility and example files (Requirement 3)
            "examples/demo_empty_folder_fix.py": "Example script",
            "scripts/validate_docs.py": "Utility script",
            
            # New documentation (Requirement 7)
            "docs/ARCHITECTURE.md": "Architecture documentation",
            "docs/dev/CONTRIBUTING.md": "Contributing guidelines",
            "CHANGELOG.md": "Changelog",
            
            # Core files that should remain (Requirement 6)
            "README.md": "Main readme",
            "pyproject.toml": "Project configuration",
            ".gitignore": "Git ignore file",
        }
        
        for file_path, description in expected_files.items():
            full_path = self.root / file_path
            if full_path.exists() and full_path.is_file():
                self.successes.append(f"✓ File exists: {file_path} ({description})")
            else:
                self.errors.append(f"✗ Missing file: {file_path} ({description})")
        
        # Verify deleted files (Requirement 4)
        deleted_files = [".paths.md"]
        for file_path in deleted_files:
            full_path = self.root / file_path
            if not full_path.exists():
                self.successes.append(f"✓ File correctly deleted: {file_path}")
            else:
                self.warnings.append(f"⚠ File should be deleted: {file_path}")
        
        print()
    
    def verify_documentation_links(self):
        """Verify no broken links in documentation (Requirement 5)."""
        print("🔗 Verifying documentation links...")
        
        doc_files = []
        
        # Find all markdown files
        for pattern in ["*.md", "docs/*.md", "docs/dev/*.md"]:
            doc_files.extend(self.root.glob(pattern))
        
        broken_links = []
        total_links = 0
        
        for doc_file in doc_files:
            if not doc_file.is_file():
                continue
                
            try:
                content = doc_file.read_text(encoding='utf-8')
                links = self.extract_markdown_links(content)
                
                for link_text, link_url in links:
                    total_links += 1
                    
                    # Skip external URLs
                    if link_url.startswith(('http://', 'https://', '#')):
                        continue
                    
                    # Resolve relative path
                    link_path = (doc_file.parent / link_url).resolve()
                    
                    if not link_path.exists():
                        broken_links.append({
                            'file': doc_file.relative_to(self.root),
                            'link_text': link_text,
                            'link_url': link_url,
                            'resolved': link_path.relative_to(self.root) if link_path.is_relative_to(self.root) else link_path
                        })
            except Exception as e:
                self.warnings.append(f"⚠ Could not read {doc_file.relative_to(self.root)}: {e}")
        
        if broken_links:
            for link in broken_links:
                self.errors.append(
                    f"✗ Broken link in {link['file']}: "
                    f"[{link['link_text']}]({link['link_url']}) -> {link['resolved']}"
                )
        else:
            self.successes.append(f"✓ All {total_links} documentation links are valid")
        
        print()
    
    def extract_markdown_links(self, content: str) -> List[Tuple[str, str]]:
        """Extract markdown links from content."""
        # Pattern for [text](url)
        pattern = r'\[([^\]]+)\]\(([^\)]+)\)'
        matches = re.findall(pattern, content)
        return matches
    
    def verify_core_preservation(self):
        """Verify core code is preserved (Requirement 6)."""
        print("🔒 Verifying core code preservation...")
        
        # Check that scrubb/ directory has files
        scrubb_files = list((self.root / "scrubb").glob("*.py"))
        if len(scrubb_files) > 0:
            self.successes.append(f"✓ Core source code preserved ({len(scrubb_files)} files in scrubb/)")
        else:
            self.errors.append("✗ No Python files found in scrubb/ directory")
        
        # Check that tests/ directory has files
        test_files = list((self.root / "tests").glob("test_*.py"))
        if len(test_files) > 0:
            self.successes.append(f"✓ Test code preserved ({len(test_files)} test files)")
        else:
            self.errors.append("✗ No test files found in tests/ directory")
        
        # Check critical files unchanged
        critical_files = ["pyproject.toml", ".gitignore"]
        for file_name in critical_files:
            file_path = self.root / file_name
            if file_path.exists():
                self.successes.append(f"✓ Critical file preserved: {file_name}")
            else:
                self.errors.append(f"✗ Critical file missing: {file_name}")
        
        print()
    
    def print_report(self) -> bool:
        """Print verification report and return success status."""
        print("=" * 70)
        print("VERIFICATION REPORT")
        print("=" * 70)
        print()
        
        if self.successes:
            print(f"✅ SUCCESSES ({len(self.successes)}):")
            for success in self.successes:
                print(f"  {success}")
            print()
        
        if self.warnings:
            print(f"⚠️  WARNINGS ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"  {warning}")
            print()
        
        if self.errors:
            print(f"❌ ERRORS ({len(self.errors)}):")
            for error in self.errors:
                print(f"  {error}")
            print()
        
        print("=" * 70)
        
        if self.errors:
            print("❌ VERIFICATION FAILED")
            print(f"   {len(self.errors)} error(s) found")
            return False
        elif self.warnings:
            print("⚠️  VERIFICATION PASSED WITH WARNINGS")
            print(f"   {len(self.warnings)} warning(s) found")
            return True
        else:
            print("✅ VERIFICATION PASSED")
            print("   All checks successful!")
            return True


def main():
    """Main entry point."""
    root_path = Path(__file__).parent.parent
    verifier = ReorganizationVerifier(root_path)
    
    success = verifier.verify_all()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
