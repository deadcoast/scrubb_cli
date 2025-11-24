#!/usr/bin/env python3
"""
Documentation Validation Script

Validates that documentation accurately reflects the source code by:
1. Extracting command examples from markdown files
2. Checking for deprecated command syntax
3. Verifying file extensions match classifier definitions
"""

import re
from pathlib import Path
from typing import List, Tuple


def extract_commands_from_docs(doc_file: Path) -> List[str]:
    """Extract all scrubb command examples from markdown files."""
    if not doc_file.exists():
        return []
    
    with open(doc_file, encoding='utf-8') as f:
        content = f.read()
    
    # Find all code blocks with bash/shell commands
    pattern = r'```(?:bash|shell|powershell|ps1)?\n(.*?)```'
    matches = re.findall(pattern, content, re.DOTALL)
    
    commands = []
    for match in matches:
        lines = match.strip().split('\n')
        for line in lines:
            line = line.strip()
            # Skip comments and non-scrubb commands
            if line.startswith('scrubb ') or line == 'scrubb':
                if not line.startswith('#'):
                    commands.append(line)
    
    return commands


def validate_command_syntax(commands: List[str]) -> List[str]:
    """Validate that commands match actual CLI structure."""
    errors = []
    
    for cmd in commands:
        # Check for deprecated --folder syntax (should be 'folder' subcommand)
        if '--folder' in cmd and 'scrubb --folder' in cmd:
            errors.append(f" Deprecated syntax: '{cmd}' (should be 'scrubb folder')")
    
    return errors


def extract_file_extensions_from_docs(doc_file: Path) -> dict:
    """Extract documented file extensions by category."""
    if not doc_file.exists():
        return {}
    
    with open(doc_file, encoding='utf-8') as f:
        content = f.read()
    
    categories = {}
    
    # Pattern to find extension lists
    # Looking for lines like: "- Extensions: `.jpg`, `.jpeg`, `.png`"
    pattern = r'\*\*(\w+)\*\*.*?Extensions?:?\s*([^\n]+)'
    matches = re.findall(pattern, content, re.IGNORECASE)
    
    for category, extensions_str in matches:
        # Extract extensions like .jpg, .png, etc.
        exts = re.findall(r'\.(\w+)', extensions_str)
        if exts:
            categories[category] = exts
    
    return categories


def validate_file_extensions() -> List[str]:
    """Validate that documented extensions match FileClassifier."""
    errors = []
    
    # Import the classifier to check actual extensions
    try:
        from scrubb.file_classifier import FileClassifier
        classifier = FileClassifier()
        
        # Get actual extensions from classifier
        actual_extensions = {
            'Images': [ext.lstrip('.') for ext in classifier.image_extensions],
            'Video': [ext.lstrip('.') for ext in classifier.video_extensions],
            'Markdown': [ext.lstrip('.') for ext in classifier.markdown_extensions],
            'Documents': [ext.lstrip('.') for ext in classifier.document_extensions],
            'Development': [ext.lstrip('.') for ext in classifier.development_extensions],
        }
        
        # Check README.md for documented extensions
        readme = Path('README.md')
        if readme.exists():
            doc_extensions = extract_file_extensions_from_docs(readme)
            
            for category, doc_exts in doc_extensions.items():
                if category in actual_extensions:
                    actual_exts = set(actual_extensions[category])
                    documented_exts = set(doc_exts)
                    
                    # Check for missing extensions in docs
                    missing = actual_exts - documented_exts
                    if missing:
                        errors.append(
                            f"  {category}: Missing from docs: {', '.join(sorted(missing))}"
                        )
                    
                    # Check for extra extensions in docs
                    extra = documented_exts - actual_exts
                    if extra:
                        errors.append(
                            f" {category}: In docs but not in code: {', '.join(sorted(extra))}"
                        )
    
    except ImportError as e:
        errors.append(f"  Could not import FileClassifier: {e}")
    
    return errors


def validate_help_text() -> List[str]:
    """Validate that help text in docs matches actual CLI help."""
    errors = []
    
    # This would require running the CLI and capturing help output
    # For now, we'll just note it as a manual check
    errors.append("ℹ  Manual check required: Verify help text matches CLI output")
    
    return errors


def main():
    """Run all validation checks."""
    print("=" * 70)
    print("Documentation Validation Report")
    print("=" * 70)
    
    docs = [
        Path('README.md'),
        Path('COMMAND_REFERENCE.md'),
        Path('OVERVIEW.md')
    ]
    
    all_errors = []
    
    # Check 1: Command Syntax
    print("\n Checking command syntax...")
    for doc in docs:
        if doc.exists():
            print(f"  Checking {doc.name}...")
            commands = extract_commands_from_docs(doc)
            errors = validate_command_syntax(commands)
            
            if errors:
                for error in errors:
                    print(f"    {error}")
                all_errors.extend(errors)
            else:
                print(f"     No syntax issues found")
    
    # Check 2: File Extensions
    print("\n Checking file extension documentation...")
    ext_errors = validate_file_extensions()
    if ext_errors:
        for error in ext_errors:
            print(f"  {error}")
        all_errors.extend(ext_errors)
    else:
        print("   File extensions match code")
    
    # Summary
    print("\n" + "=" * 70)
    error_count = len([e for e in all_errors if e.startswith('')])
    warning_count = len([e for e in all_errors if e.startswith('')])
    info_count = len([e for e in all_errors if e.startswith('ℹ')])
    
    if error_count > 0:
        print(f" Validation FAILED: {error_count} errors, {warning_count} warnings")
        return 1
    elif warning_count > 0:
        print(f"  Validation passed with {warning_count} warnings")
        return 0
    else:
        print(" All documentation validated successfully!")
        return 0


if __name__ == '__main__':
    exit(main())
