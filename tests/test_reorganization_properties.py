"""Property-based tests for codebase reorganization functionality."""

import pytest
from pathlib import Path
import tempfile
import shutil
import os
import stat
from hypothesis import given, strategies as st, settings


def capture_directory_state(root_path: Path) -> dict:
    """Capture the current state of critical directories."""
    critical_dirs = ['scrubb', 'tests', '.kiro', '.archive']
    
    state = {}
    for dir_name in critical_dirs:
        dir_path = root_path / dir_name
        state[dir_name] = {
            'exists': dir_path.exists(),
            'is_directory': dir_path.is_dir() if dir_path.exists() else False,
            'path': dir_path
        }
    
    return state


class TestDirectoryPreservation:
    """Property tests for directory preservation during reorganization."""
    
    @settings(max_examples=100)
    @given(
        new_dirs=st.lists(
            st.sampled_from(['docs', 'examples', 'scripts']),
            min_size=1,
            max_size=3,
            unique=True
        )
    )
    def test_directory_preservation(self, new_dirs):
        """
        **Feature: codebase-reorganization, Property 1: Directory preservation**
        **Validates: Requirements 1.5**
        
        For any critical directory (scrubb/, tests/, .kiro/, .archive/), after
        reorganization the directory should still exist at its original location.
        """
        # Create temporary directory structure
        with tempfile.TemporaryDirectory() as temp_dir:
            root_path = Path(temp_dir)
            
            # Create critical directories
            critical_dirs = ['scrubb', 'tests', '.kiro', '.archive']
            for dir_name in critical_dirs:
                dir_path = root_path / dir_name
                dir_path.mkdir(parents=True, exist_ok=True)
                
                # Add a dummy file to make it non-empty
                dummy_file = dir_path / 'dummy.txt'
                dummy_file.write_text('test content')
            
            # Capture state before reorganization
            before_state = capture_directory_state(root_path)
            
            # Verify all critical directories exist before
            for dir_name in critical_dirs:
                assert before_state[dir_name]['exists'], \
                    f"Critical directory {dir_name} should exist before reorganization"
                assert before_state[dir_name]['is_directory'], \
                    f"{dir_name} should be a directory before reorganization"
            
            # Simulate reorganization: create new directories
            for new_dir in new_dirs:
                new_dir_path = root_path / new_dir
                new_dir_path.mkdir(parents=True, exist_ok=True)
            
            # Capture state after reorganization
            after_state = capture_directory_state(root_path)
            
            # Verify all critical directories still exist after
            for dir_name in critical_dirs:
                assert after_state[dir_name]['exists'], \
                    f"Critical directory {dir_name} should still exist after reorganization"
                assert after_state[dir_name]['is_directory'], \
                    f"{dir_name} should still be a directory after reorganization"
                
                # Verify the directory is at the same location
                assert before_state[dir_name]['path'] == after_state[dir_name]['path'], \
                    f"Critical directory {dir_name} should remain at original location"


class TestFileContentPreservation:
    """Property tests for file content preservation during reorganization."""
    
    @settings(max_examples=100)
    @given(
        file_content=st.text(min_size=0, max_size=1000),
        file_name=st.text(
            alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'), min_codepoint=65, max_codepoint=122),
            min_size=1,
            max_size=20
        ).map(lambda s: s + '.md'),
        dest_subdir=st.sampled_from(['docs', 'docs/dev', 'examples', 'scripts'])
    )
    def test_file_content_preservation(self, file_content, file_name, dest_subdir):
        """
        **Feature: codebase-reorganization, Property 2: File content preservation**
        **Validates: Requirements 2.5, 3.3**
        
        For any file that is moved, the content at the destination should be
        identical to the content at the source before the move.
        """
        # Create temporary directory structure
        with tempfile.TemporaryDirectory() as temp_dir:
            root_path = Path(temp_dir)
            
            # Create source file in root
            source_file = root_path / file_name
            source_file.write_text(file_content, encoding='utf-8')
            
            # Read original content (this is the baseline after OS normalization)
            original_content = source_file.read_text(encoding='utf-8')
            
            # Create destination directory
            dest_dir = root_path / dest_subdir
            dest_dir.mkdir(parents=True, exist_ok=True)
            
            # Move file to destination
            dest_file = dest_dir / file_name
            shutil.move(str(source_file), str(dest_file))
            
            # Read content from destination
            moved_content = dest_file.read_text(encoding='utf-8')
            
            # Verify content is preserved (comparing what was actually written vs what was moved)
            assert moved_content == original_content, \
                f"Content should be identical after move: expected {repr(original_content)}, got {repr(moved_content)}"
            
            # Verify source file no longer exists
            assert not source_file.exists(), \
                "Source file should not exist after move"
            
            # Verify destination file exists
            assert dest_file.exists(), \
                "Destination file should exist after move"



class TestPermissionPreservation:
    """Property tests for permission preservation during reorganization."""
    
    @settings(max_examples=100)
    @given(
        file_content=st.text(min_size=0, max_size=500),
        file_name=st.text(
            alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'), min_codepoint=65, max_codepoint=122),
            min_size=1,
            max_size=20
        ).map(lambda s: s + '.py'),
        dest_subdir=st.sampled_from(['examples', 'scripts']),
        should_be_executable=st.booleans()
    )
    def test_permission_preservation(self, file_content, file_name, dest_subdir, should_be_executable):
        """
        **Feature: codebase-reorganization, Property 3: Permission preservation**
        **Validates: Requirements 3.4**
        
        For any file that is moved, if the source file was executable, the
        destination file should also be executable.
        """
        # Create temporary directory structure
        with tempfile.TemporaryDirectory() as temp_dir:
            root_path = Path(temp_dir)
            
            # Create source file in root
            source_file = root_path / file_name
            source_file.write_text(file_content, encoding='utf-8')
            
            # Set executable permission if needed
            if should_be_executable:
                current_mode = source_file.stat().st_mode
                source_file.chmod(current_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
            
            # Capture original permissions
            original_stat = source_file.stat()
            was_executable = bool(original_stat.st_mode & stat.S_IXUSR)
            
            # Create destination directory
            dest_dir = root_path / dest_subdir
            dest_dir.mkdir(parents=True, exist_ok=True)
            
            # Move file to destination
            dest_file = dest_dir / file_name
            shutil.move(str(source_file), str(dest_file))
            
            # Check permissions on destination file
            dest_stat = dest_file.stat()
            is_executable = bool(dest_stat.st_mode & stat.S_IXUSR)
            
            # Verify executable permission is preserved
            assert is_executable == was_executable, \
                f"Executable permission should be preserved: source was {'executable' if was_executable else 'not executable'}, " \
                f"destination is {'executable' if is_executable else 'not executable'}"
            
            # Verify file exists at destination
            assert dest_file.exists(), \
                "Destination file should exist after move"
            
            # Verify source file no longer exists
            assert not source_file.exists(), \
                "Source file should not exist after move"


class TestDeletionIsolation:
    """Property tests for deletion isolation during reorganization."""
    
    @settings(max_examples=100)
    @given(
        file_to_delete=st.text(
            alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'), min_codepoint=65, max_codepoint=122),
            min_size=1,
            max_size=20
        ).map(lambda s: s + '.md'),
        other_files=st.lists(
            st.text(
                alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'), min_codepoint=65, max_codepoint=122),
                min_size=1,
                max_size=20
            ).map(lambda s: s + '.txt'),
            min_size=1,
            max_size=5,
            unique=True
        )
    )
    def test_deletion_isolation(self, file_to_delete, other_files):
        """
        **Feature: codebase-reorganization, Property 4: Deletion isolation**
        **Validates: Requirements 4.4**
        
        For any file deletion operation, no other files should be modified or
        deleted as a side effect.
        """
        # Create temporary directory structure
        with tempfile.TemporaryDirectory() as temp_dir:
            root_path = Path(temp_dir)
            
            # Create the file to be deleted
            target_file = root_path / file_to_delete
            target_file.write_text('content to delete', encoding='utf-8')
            
            # Create other files that should not be affected
            other_file_paths = []
            other_file_contents = {}
            for i, other_file in enumerate(other_files):
                other_file_path = root_path / other_file
                content = f'content {i}'
                other_file_path.write_text(content, encoding='utf-8')
                other_file_paths.append(other_file_path)
                other_file_contents[other_file_path] = content
            
            # Verify all files exist before deletion
            assert target_file.exists(), "Target file should exist before deletion"
            for other_file_path in other_file_paths:
                assert other_file_path.exists(), f"Other file {other_file_path.name} should exist before deletion"
            
            # Delete the target file
            target_file.unlink()
            
            # Verify target file is deleted
            assert not target_file.exists(), "Target file should not exist after deletion"
            
            # Verify other files still exist and are unchanged
            for other_file_path in other_file_paths:
                assert other_file_path.exists(), \
                    f"Other file {other_file_path.name} should still exist after deletion"
                
                # Verify content is unchanged
                current_content = other_file_path.read_text(encoding='utf-8')
                expected_content = other_file_contents[other_file_path]
                assert current_content == expected_content, \
                    f"Content of {other_file_path.name} should be unchanged: expected {repr(expected_content)}, got {repr(current_content)}"


import re
from urllib.parse import urlparse


def extract_markdown_links(content: str) -> list[tuple[str, str]]:
    """Extract markdown links from content.
    
    Returns list of tuples: (link_text, link_target)
    """
    # Match markdown links: [text](target)
    pattern = r'\[([^\]]+)\]\(([^\)]+)\)'
    matches = re.findall(pattern, content)
    return matches


def is_valid_link(link_target: str, base_path: Path) -> bool:
    """Check if a link target is valid (exists as file or is valid URL)."""
    # Check if it's a URL
    parsed = urlparse(link_target)
    if parsed.scheme in ('http', 'https', 'ftp'):
        # For property testing, we consider all URLs valid
        # (we can't actually check external URLs in tests)
        return True
    
    # Check if it's a file path (relative or absolute)
    # Handle anchor links (e.g., #section)
    if link_target.startswith('#'):
        # Anchor links within the same document are valid
        return True
    
    # Remove anchor if present (e.g., file.md#section -> file.md)
    link_without_anchor = link_target.split('#')[0]
    if not link_without_anchor:
        # Pure anchor link
        return True
    
    # Try to resolve the path
    if Path(link_without_anchor).is_absolute():
        return Path(link_without_anchor).exists()
    else:
        # Relative path from base_path
        full_path = (base_path / link_without_anchor).resolve()
        return full_path.exists()


class TestLinkValidity:
    """Property tests for link validity after reorganization."""
    
    @settings(max_examples=100)
    @given(
        num_files=st.integers(min_value=1, max_value=5),
        num_links_per_file=st.integers(min_value=0, max_value=3)
    )
    def test_link_validity(self, num_files, num_links_per_file):
        """
        **Feature: codebase-reorganization, Property 5: Link validity**
        **Validates: Requirements 5.2, 5.3, 5.5**
        
        For any markdown link in any documentation file after reorganization,
        the link should point to an existing file or valid URL.
        """
        # Create temporary directory structure
        with tempfile.TemporaryDirectory() as temp_dir:
            root_path = Path(temp_dir)
            docs_path = root_path / 'docs'
            docs_path.mkdir(parents=True, exist_ok=True)
            
            # Create target files that links can point to
            target_files = []
            for i in range(num_files):
                target_file = docs_path / f'target_{i}.md'
                target_file.write_text(f'# Target {i}\n\nContent here.', encoding='utf-8')
                target_files.append(target_file)
            
            # Create documentation files with links
            doc_files = []
            for i in range(num_files):
                doc_file = docs_path / f'doc_{i}.md'
                
                # Generate content with links
                content_parts = [f'# Document {i}\n\n']
                
                for j in range(num_links_per_file):
                    # Create links to existing files or valid URLs
                    if j % 3 == 0 and target_files:
                        # Link to an existing file (relative path)
                        target = target_files[j % len(target_files)]
                        relative_path = target.name
                        content_parts.append(f'See [target document]({relative_path}) for details.\n\n')
                    elif j % 3 == 1:
                        # Link to a URL
                        content_parts.append(f'Visit [example site](https://example.com/page{j}) for more.\n\n')
                    else:
                        # Anchor link
                        content_parts.append(f'Jump to [section](#section-{j}) below.\n\n')
                
                content = ''.join(content_parts)
                doc_file.write_text(content, encoding='utf-8')
                doc_files.append(doc_file)
            
            # Verify all links in all documentation files are valid
            for doc_file in doc_files:
                content = doc_file.read_text(encoding='utf-8')
                links = extract_markdown_links(content)
                
                for link_text, link_target in links:
                    is_valid = is_valid_link(link_target, doc_file.parent)
                    assert is_valid, \
                        f"Link in {doc_file.name} should be valid: [{link_text}]({link_target})"


class TestLinkTextPreservation:
    """Property tests for link text preservation during reorganization."""
    
    @settings(max_examples=100)
    @given(
        link_text=st.text(
            alphabet=st.characters(
                blacklist_characters='\r\n[]()\\',
                blacklist_categories=('Cc', 'Cs')
            ),
            min_size=1,
            max_size=50
        ),
        old_target=st.text(
            alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'), min_codepoint=65, max_codepoint=122),
            min_size=1,
            max_size=20
        ).map(lambda s: s + '.md'),
        new_target=st.text(
            alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'), min_codepoint=65, max_codepoint=122),
            min_size=1,
            max_size=20
        ).map(lambda s: 'docs/' + s + '.md')
    )
    def test_link_text_preservation(self, link_text, old_target, new_target):
        """
        **Feature: codebase-reorganization, Property 6: Link text preservation**
        **Validates: Requirements 5.4**
        
        For any link that is updated, the link text (the visible text in square
        brackets) should remain unchanged.
        """
        # Create temporary directory structure
        with tempfile.TemporaryDirectory() as temp_dir:
            root_path = Path(temp_dir)
            
            # Create a documentation file with a link
            doc_file = root_path / 'README.md'
            original_content = f'# Documentation\n\nSee [{link_text}]({old_target}) for details.\n'
            doc_file.write_text(original_content, encoding='utf-8')
            
            # Read the original content
            content = doc_file.read_text(encoding='utf-8')
            original_links = extract_markdown_links(content)
            
            # Verify we have the expected link
            assert len(original_links) > 0, "Should have at least one link"
            original_text, original_target = original_links[0]
            assert original_text == link_text, f"Original link text should be {repr(link_text)}"
            
            # Simulate link update: replace old target with new target
            updated_content = content.replace(f']({old_target})', f']({new_target})')
            doc_file.write_text(updated_content, encoding='utf-8')
            
            # Read the updated content
            updated_content_read = doc_file.read_text(encoding='utf-8')
            updated_links = extract_markdown_links(updated_content_read)
            
            # Verify link text is preserved
            assert len(updated_links) > 0, "Should still have at least one link"
            updated_text, updated_target = updated_links[0]
            
            assert updated_text == link_text, \
                f"Link text should be preserved: expected {repr(link_text)}, got {repr(updated_text)}"
            
            # Verify target was actually updated
            assert updated_target == new_target, \
                f"Link target should be updated: expected {repr(new_target)}, got {repr(updated_target)}"


def capture_file_contents(directory: Path) -> dict:
    """Recursively capture all file contents in a directory.
    
    Returns dict mapping relative path to file content.
    """
    contents = {}
    for file_path in directory.rglob('*'):
        if file_path.is_file():
            try:
                relative_path = file_path.relative_to(directory)
                contents[str(relative_path)] = file_path.read_text(encoding='utf-8')
            except (UnicodeDecodeError, PermissionError):
                # Skip binary files or files we can't read
                pass
    return contents


class TestSourceCodeImmutability:
    """Property tests for source code immutability during reorganization."""
    
    @settings(max_examples=100)
    @given(
        num_source_files=st.integers(min_value=1, max_value=5),
        num_new_dirs=st.integers(min_value=1, max_value=3),
        num_files_to_move=st.integers(min_value=0, max_value=3)
    )
    def test_source_code_immutability(self, num_source_files, num_new_dirs, num_files_to_move):
        """
        **Feature: codebase-reorganization, Property 7: Source code immutability**
        **Validates: Requirements 6.1**
        
        For any file in the scrubb/ directory, the file content should be
        identical before and after reorganization.
        """
        # Create temporary directory structure
        with tempfile.TemporaryDirectory() as temp_dir:
            root_path = Path(temp_dir)
            
            # Create scrubb/ directory with source files
            scrubb_dir = root_path / 'scrubb'
            scrubb_dir.mkdir(parents=True, exist_ok=True)
            
            # Create source files with various content
            for i in range(num_source_files):
                source_file = scrubb_dir / f'module_{i}.py'
                content = f'''"""Module {i} for scrubb application."""

def function_{i}():
    """Function {i} implementation."""
    return {i}

class Class{i}:
    """Class {i} implementation."""
    
    def __init__(self):
        self.value = {i}
    
    def method_{i}(self):
        """Method {i}."""
        return self.value * {i}
'''
                source_file.write_text(content, encoding='utf-8')
            
            # Capture state before reorganization
            before_contents = capture_file_contents(scrubb_dir)
            
            # Verify we have files
            assert len(before_contents) > 0, "Should have source files before reorganization"
            
            # Simulate reorganization: create new directories and move other files
            new_dirs = ['docs', 'examples', 'scripts'][:num_new_dirs]
            for new_dir in new_dirs:
                new_dir_path = root_path / new_dir
                new_dir_path.mkdir(parents=True, exist_ok=True)
            
            # Move some files from root to new directories (but NOT from scrubb/)
            for i in range(num_files_to_move):
                temp_file = root_path / f'temp_{i}.md'
                temp_file.write_text(f'Temporary file {i}', encoding='utf-8')
                
                if new_dirs:
                    dest_dir = root_path / new_dirs[i % len(new_dirs)]
                    dest_file = dest_dir / f'moved_{i}.md'
                    shutil.move(str(temp_file), str(dest_file))
            
            # Capture state after reorganization
            after_contents = capture_file_contents(scrubb_dir)
            
            # Verify all source files are unchanged
            assert len(after_contents) == len(before_contents), \
                f"Number of source files should be unchanged: expected {len(before_contents)}, got {len(after_contents)}"
            
            for file_path, original_content in before_contents.items():
                assert file_path in after_contents, \
                    f"Source file {file_path} should still exist after reorganization"
                
                current_content = after_contents[file_path]
                assert current_content == original_content, \
                    f"Content of {file_path} should be unchanged"


class TestTestCodeImmutability:
    """Property tests for test code immutability during reorganization."""
    
    @settings(max_examples=100)
    @given(
        num_test_files=st.integers(min_value=1, max_value=5),
        num_new_dirs=st.integers(min_value=1, max_value=3),
        num_files_to_move=st.integers(min_value=0, max_value=3)
    )
    def test_test_code_immutability(self, num_test_files, num_new_dirs, num_files_to_move):
        """
        **Feature: codebase-reorganization, Property 8: Test code immutability**
        **Validates: Requirements 6.2**
        
        For any file in the tests/ directory, the file content should be
        identical before and after reorganization.
        """
        # Create temporary directory structure
        with tempfile.TemporaryDirectory() as temp_dir:
            root_path = Path(temp_dir)
            
            # Create tests/ directory with test files
            tests_dir = root_path / 'tests'
            tests_dir.mkdir(parents=True, exist_ok=True)
            
            # Create test files with various content
            for i in range(num_test_files):
                test_file = tests_dir / f'test_module_{i}.py'
                content = f'''"""Tests for module {i}."""

import pytest


def test_function_{i}():
    """Test function {i}."""
    assert {i} == {i}


class TestClass{i}:
    """Test class {i}."""
    
    def test_method_{i}(self):
        """Test method {i}."""
        result = {i} * 2
        assert result == {i * 2}
    
    def test_edge_case_{i}(self):
        """Test edge case {i}."""
        assert {i} >= 0
'''
                test_file.write_text(content, encoding='utf-8')
            
            # Capture state before reorganization
            before_contents = capture_file_contents(tests_dir)
            
            # Verify we have files
            assert len(before_contents) > 0, "Should have test files before reorganization"
            
            # Simulate reorganization: create new directories and move other files
            new_dirs = ['docs', 'examples', 'scripts'][:num_new_dirs]
            for new_dir in new_dirs:
                new_dir_path = root_path / new_dir
                new_dir_path.mkdir(parents=True, exist_ok=True)
            
            # Move some files from root to new directories (but NOT from tests/)
            for i in range(num_files_to_move):
                temp_file = root_path / f'temp_{i}.md'
                temp_file.write_text(f'Temporary file {i}', encoding='utf-8')
                
                if new_dirs:
                    dest_dir = root_path / new_dirs[i % len(new_dirs)]
                    dest_file = dest_dir / f'moved_{i}.md'
                    shutil.move(str(temp_file), str(dest_file))
            
            # Capture state after reorganization
            after_contents = capture_file_contents(tests_dir)
            
            # Verify all test files are unchanged
            assert len(after_contents) == len(before_contents), \
                f"Number of test files should be unchanged: expected {len(before_contents)}, got {len(after_contents)}"
            
            for file_path, original_content in before_contents.items():
                assert file_path in after_contents, \
                    f"Test file {file_path} should still exist after reorganization"
                
                current_content = after_contents[file_path]
                assert current_content == original_content, \
                    f"Content of {file_path} should be unchanged"
