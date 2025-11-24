#!/usr/bin/env python3
"""Script to update documentation links after file reorganization."""

import re
from pathlib import Path
from typing import Dict, List, Tuple


def extract_markdown_links(content: str) -> List[Tuple[str, str, int]]:
    """Extract markdown links from content.
    
    Returns list of tuples: (link_text, link_target, position)
    """
    pattern = r'\[([^\]]+)\]\(([^\)]+)\)'
    matches = []
    for match in re.finditer(pattern, content):
        link_text = match.group(1)
        link_target = match.group(2)
        position = match.start()
        matches.append((link_text, link_target, position))
    return matches


def generate_link_mapping() -> Dict[str, str]:
    """Generate mapping of old file paths to new file paths.
    
    Based on the reorganization that has already been completed.
    """
    return {
        'COMMAND_REFERENCE.md': 'docs/COMMAND_REFERENCE.md',
        'DOCUMENTATION_VALIDATION_PLAN.md': 'docs/dev/DOCUMENTATION_VALIDATION_PLAN.md',
        'EMPTY_FOLDER_FIX.md': 'docs/dev/EMPTY_FOLDER_FIX.md',
        'FIXES_SUMMARY.md': 'docs/dev/FIXES_SUMMARY.md',
        'demo_empty_folder_fix.py': 'examples/demo_empty_folder_fix.py',
        'validate_docs.py': 'scripts/validate_docs.py',
    }


def update_links_in_content(content: str, link_mapping: Dict[str, str], base_path: Path) -> str:
    """Update links in content based on the link mapping.
    
    Args:
        content: The file content
        link_mapping: Dictionary mapping old paths to new paths
        base_path: Base path for resolving relative links
    
    Returns:
        Updated content with corrected links
    """
    links = extract_markdown_links(content)
    
    # Process links in reverse order to maintain positions
    links_reversed = sorted(links, key=lambda x: x[2], reverse=True)
    
    for link_text, link_target, position in links_reversed:
        # Skip URLs and anchors
        if link_target.startswith(('http://', 'https://', '#')):
            continue
        
        # Remove anchor if present
        link_without_anchor = link_target.split('#')[0]
        anchor = '#' + link_target.split('#')[1] if '#' in link_target else ''
        
        if not link_without_anchor:
            continue
        
        # Check if this link needs updating
        # Extract just the filename from the link
        link_path = Path(link_without_anchor)
        filename = link_path.name
        
        if filename in link_mapping:
            # Calculate the new relative path from base_path
            new_absolute_path = Path(link_mapping[filename])
            
            # If base_path is in docs/, calculate relative path
            try:
                if 'docs' in str(base_path):
                    # Calculate relative path from base_path to new location
                    new_relative_path = Path(link_mapping[filename])
                    # Make it relative to base_path
                    if base_path.name == 'docs':
                        # From docs/ to docs/something
                        new_target = str(new_relative_path.relative_to('docs'))
                    elif base_path.parent.name == 'docs':
                        # From docs/dev/ to docs/something
                        new_target = '../' + str(new_relative_path.relative_to('docs'))
                    else:
                        new_target = str(new_relative_path)
                else:
                    # From root, just use the new path
                    new_target = link_mapping[filename]
                
                new_target += anchor
                
                # Replace the link target in content
                old_link = f']({link_target})'
                new_link = f']({new_target})'
                
                # Find and replace this specific occurrence
                before = content[:position]
                after = content[position:]
                after = after.replace(old_link, new_link, 1)
                content = before + after
            except (ValueError, KeyError):
                # If we can't calculate relative path, skip
                continue
    
    return content


def update_readme_structure(readme_path: Path) -> None:
    """Update README.md with new structure references."""
    content = readme_path.read_text(encoding='utf-8')
    
    # Check if Documentation section already exists
    if '## Documentation' not in content:
        # Add Documentation section before License section
        doc_section = """
## Documentation

- [Command Reference](docs/COMMAND_REFERENCE.md) - Complete command-line reference
- [Architecture](docs/ARCHITECTURE.md) - System design and architecture
- [Contributing](docs/dev/CONTRIBUTING.md) - Contribution guidelines
- [Development Documentation](docs/dev/) - Developer-focused documentation

"""
        
        # Insert before License section
        if '## License' in content:
            content = content.replace('## License', doc_section + '## License')
        else:
            # Append at the end
            content += '\n' + doc_section
    
    # Check if Project Structure section already exists
    if '## Project Structure' not in content:
        structure_section = """
## Project Structure

```
scrubb/
├── docs/                    # Documentation
│   ├── COMMAND_REFERENCE.md
│   ├── ARCHITECTURE.md
│   └── dev/                # Developer documentation
│       ├── CONTRIBUTING.md
│       ├── DOCUMENTATION_VALIDATION_PLAN.md
│       ├── EMPTY_FOLDER_FIX.md
│       └── FIXES_SUMMARY.md
├── examples/               # Example scripts and demos
│   └── demo_empty_folder_fix.py
├── scripts/                # Utility scripts
│   └── validate_docs.py
├── scrubb/                 # Main package
│   ├── __init__.py
│   ├── cli.py
│   ├── config.py
│   ├── directory_scanner.py
│   ├── file_classifier.py
│   ├── folder_organizer.py
│   ├── ignore.py
│   ├── scrubber.py
│   ├── statistics_calculator.py
│   ├── tree_comparator.py
│   ├── tree_models.py
│   ├── tree_renderer.py
│   └── tree_visualizer.py
├── tests/                  # Test suite
├── .kiro/                  # Kiro specs and configuration
├── pyproject.toml          # Project configuration
└── README.md               # This file
```

"""
        
        # Insert before License section or at the end
        if '## License' in content:
            content = content.replace('## License', structure_section + '## License')
        else:
            content += '\n' + structure_section
    
    readme_path.write_text(content, encoding='utf-8')


def main():
    """Main function to update all documentation links."""
    root_path = Path('.')
    
    # Generate link mapping
    link_mapping = generate_link_mapping()
    
    print("Updating documentation links...")
    print(f"Link mapping: {link_mapping}")
    
    # Update README.md
    readme_path = root_path / 'README.md'
    if readme_path.exists():
        print(f"\nUpdating {readme_path}...")
        content = readme_path.read_text(encoding='utf-8')
        updated_content = update_links_in_content(content, link_mapping, root_path)
        readme_path.write_text(updated_content, encoding='utf-8')
        
        # Add structure sections
        update_readme_structure(readme_path)
        print(f"  ✓ Updated {readme_path}")
    
    # Update docs/COMMAND_REFERENCE.md
    command_ref_path = root_path / 'docs' / 'COMMAND_REFERENCE.md'
    if command_ref_path.exists():
        print(f"\nUpdating {command_ref_path}...")
        content = command_ref_path.read_text(encoding='utf-8')
        updated_content = update_links_in_content(content, link_mapping, command_ref_path.parent)
        command_ref_path.write_text(updated_content, encoding='utf-8')
        print(f"  ✓ Updated {command_ref_path}")
    
    # Update docs/dev/ files
    docs_dev_path = root_path / 'docs' / 'dev'
    if docs_dev_path.exists():
        for doc_file in docs_dev_path.glob('*.md'):
            print(f"\nUpdating {doc_file}...")
            content = doc_file.read_text(encoding='utf-8')
            updated_content = update_links_in_content(content, link_mapping, doc_file.parent)
            doc_file.write_text(updated_content, encoding='utf-8')
            print(f"  ✓ Updated {doc_file}")
    
    # Verify all links
    print("\n" + "="*70)
    print("Verifying all links...")
    print("="*70)
    
    all_valid = True
    for doc_file in [readme_path, command_ref_path] + list(docs_dev_path.glob('*.md')):
        if not doc_file.exists():
            continue
        
        content = doc_file.read_text(encoding='utf-8')
        links = extract_markdown_links(content)
        
        for link_text, link_target, _ in links:
            # Skip URLs and anchors
            if link_target.startswith(('http://', 'https://', '#')):
                continue
            
            # Remove anchor
            link_without_anchor = link_target.split('#')[0]
            if not link_without_anchor:
                continue
            
            # Check if file exists
            if Path(link_without_anchor).is_absolute():
                exists = Path(link_without_anchor).exists()
            else:
                full_path = (doc_file.parent / link_without_anchor).resolve()
                exists = full_path.exists()
            
            if not exists:
                print(f"  ✗ Broken link in {doc_file}: [{link_text}]({link_target})")
                all_valid = False
    
    if all_valid:
        print("  ✓ All links are valid!")
    else:
        print("\n⚠ Some links are broken. Please review and fix manually.")
    
    print("\n" + "="*70)
    print("Link update complete!")
    print("="*70)


if __name__ == '__main__':
    main()
