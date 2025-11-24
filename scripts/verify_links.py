#!/usr/bin/env python3
"""Verify all links in documentation files."""

import re
from pathlib import Path
from urllib.parse import urlparse


def extract_markdown_links(content: str):
    """Extract markdown links from content."""
    pattern = r'\[([^\]]+)\]\(([^\)]+)\)'
    return re.findall(pattern, content)


def verify_links():
    """Verify all links in documentation."""
    root = Path('.')
    docs = [
        root / 'README.md',
        root / 'docs' / 'COMMAND_REFERENCE.md',
    ]
    
    # Add all docs/dev files
    docs_dev = root / 'docs' / 'dev'
    if docs_dev.exists():
        docs.extend(docs_dev.glob('*.md'))
    
    broken_links = []
    total_links = 0
    
    for doc in docs:
        if not doc.exists():
            continue
        
        content = doc.read_text(encoding='utf-8')
        links = extract_markdown_links(content)
        
        for link_text, link_target in links:
            total_links += 1
            
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
                full_path = (doc.parent / link_without_anchor).resolve()
                exists = full_path.exists()
            
            if not exists:
                broken_links.append((doc, link_text, link_target))
    
    print(f"Total links checked: {total_links}")
    print(f"Broken links: {len(broken_links)}")
    
    if broken_links:
        print("\nBroken links found:")
        for doc, text, target in broken_links:
            print(f"  {doc}: [{text}]({target})")
    else:
        print("\n✓ All links are valid!")
    
    return len(broken_links) == 0


if __name__ == '__main__':
    import sys
    sys.exit(0 if verify_links() else 1)
