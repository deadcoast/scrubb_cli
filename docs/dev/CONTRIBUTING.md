# Contributing to scrubb

Thank you for your interest in contributing to scrubb! This document provides guidelines and instructions for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Development Workflow](#development-workflow)
- [Testing](#testing)
- [Code Style](#code-style)
- [Commit Guidelines](#commit-guidelines)
- [Pull Request Process](#pull-request-process)
- [Project Structure](#project-structure)
- [Adding New Features](#adding-new-features)

## Code of Conduct

### Our Standards

- Be respectful and inclusive
- Welcome newcomers and help them learn
- Focus on constructive feedback
- Prioritize the project's best interests
- Show empathy towards other contributors

### Unacceptable Behavior

- Harassment, discrimination, or offensive comments
- Trolling or insulting remarks
- Publishing others' private information
- Any conduct that would be inappropriate in a professional setting

## Getting Started

### Prerequisites

- Python 3.10 or higher
- UV package manager (recommended) or pip
- Git for version control
- A GitHub account

### Installing UV

UV is the recommended package manager for this project:

**macOS/Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows:**
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**Alternative (using pip):**
```bash
pip install uv
```

## Development Setup

1. **Fork the repository** on GitHub

2. **Clone your fork:**
   ```bash
   git clone https://github.com/YOUR_USERNAME/scrubb.git
   cd scrubb
   ```

3. **Add upstream remote:**
   ```bash
   git remote add upstream https://github.com/ORIGINAL_OWNER/scrubb.git
   ```

4. **Install in development mode:**
   ```bash
   uv pip install -e .
   ```

5. **Install development dependencies:**
   ```bash
   uv pip install pytest hypothesis pytest-cov
   ```

6. **Verify installation:**
   ```bash
   scrubb --help
   pytest
   ```

## Development Workflow

### Creating a Feature Branch

```bash
# Update your main branch
git checkout main
git pull upstream main

# Create a feature branch
git checkout -b feature/your-feature-name
```

### Making Changes

1. Make your changes in the feature branch
2. Write or update tests for your changes
3. Run tests to ensure everything passes
4. Update documentation if needed
5. Commit your changes with clear messages

### Keeping Your Branch Updated

```bash
# Fetch upstream changes
git fetch upstream

# Rebase your branch on upstream main
git rebase upstream/main

# If conflicts occur, resolve them and continue
git rebase --continue
```

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_cli.py

# Run tests matching a pattern
pytest -k "dry_run"

# Run with coverage report
pytest --cov=scrubb --cov-report=html
```

### Writing Tests

#### Unit Tests

Unit tests should test individual components in isolation:

```python
def test_file_classifier_categorizes_images():
    """Test that image files are correctly categorized."""
    classifier = FileClassifier()
    assert classifier.classify("photo.jpg") == "Images"
    assert classifier.classify("image.png") == "Images"
```

#### Property-Based Tests

Property-based tests verify invariants across many random inputs:

```python
from hypothesis import given, strategies as st

@given(st.text())
def test_emoji_removal_preserves_length_or_reduces(text):
    """Property: Removing emojis never increases text length."""
    result = remove_emojis(text)
    assert len(result) <= len(text)
```

### Test Requirements

- All new features must include tests
- Bug fixes should include regression tests
- Aim for high code coverage (>80%)
- Tests must pass on all supported platforms
- Property-based tests should run at least 100 iterations

## Code Style

### Python Style Guide

We follow PEP 8 with some modifications:

- **Line length**: 100 characters (not 79)
- **Indentation**: 4 spaces (no tabs)
- **Quotes**: Double quotes for strings, single quotes for dict keys
- **Imports**: Grouped and sorted (standard library, third-party, local)

### Type Hints

Use type hints for all function signatures:

```python
def process_file(file_path: Path, dry_run: bool = False) -> ProcessResult:
    """Process a single file."""
    ...
```

### Docstrings

Use Google-style docstrings:

```python
def calculate_statistics(tree: TreeNode) -> TreeStatistics:
    """Calculate statistics for a directory tree.
    
    Args:
        tree: The root node of the directory tree
        
    Returns:
        TreeStatistics object containing file counts, sizes, and depths
        
    Raises:
        ValueError: If tree is None or invalid
    """
    ...
```

### Naming Conventions

- **Functions/methods**: `snake_case`
- **Classes**: `PascalCase`
- **Constants**: `UPPER_SNAKE_CASE`
- **Private members**: `_leading_underscore`
- **Modules**: `snake_case.py`

## Commit Guidelines

### Commit Message Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

- **feat**: New feature
- **fix**: Bug fix
- **docs**: Documentation changes
- **style**: Code style changes (formatting, no logic change)
- **refactor**: Code refactoring
- **test**: Adding or updating tests
- **chore**: Maintenance tasks

### Examples

```
feat(folder): add tree visualization support

Implement before/after tree visualization for folder cleanup
command using rich library for formatted output.

Closes #42
```

```
fix(scrubber): handle emoji variants correctly

Fix issue where emoji variants with skin tone modifiers
were not being detected properly.

Fixes #38
```

### Commit Best Practices

- Use present tense ("add feature" not "added feature")
- Use imperative mood ("move cursor to..." not "moves cursor to...")
- Keep subject line under 50 characters
- Separate subject from body with blank line
- Wrap body at 72 characters
- Reference issues and pull requests in footer

## Pull Request Process

### Before Submitting

1. **Ensure all tests pass:**
   ```bash
   pytest
   ```

2. **Check code coverage:**
   ```bash
   pytest --cov=scrubb --cov-report=term-missing
   ```

3. **Update documentation:**
   - Update README.md if adding user-facing features
   - Update CHANGELOG.md with your changes
   - Add docstrings to new functions/classes
   - Update relevant documentation files

4. **Verify your changes work:**
   ```bash
   # Test emoji scrubbing
   scrubb --help
   scrubb .
   
   # Test folder cleanup
   scrubb folder --dry
   scrubb folder --tree --dry
   ```

### Submitting a Pull Request

1. **Push your branch:**
   ```bash
   git push origin feature/your-feature-name
   ```

2. **Create pull request** on GitHub

3. **Fill out the PR template:**
   - Describe what changes you made
   - Explain why you made them
   - Reference any related issues
   - Include screenshots if relevant
   - Note any breaking changes

4. **Wait for review:**
   - Address reviewer feedback
   - Make requested changes
   - Push updates to your branch
   - Respond to comments

### PR Requirements

- All tests must pass
- Code coverage should not decrease
- Documentation must be updated
- Commit messages follow guidelines
- Code follows style guide
- No merge conflicts with main branch

## Project Structure

```
scrubb/
├── scrubb/                 # Main package
│   ├── __init__.py
│   ├── cli.py             # CLI commands and interface
│   ├── config.py          # Configuration management
│   ├── scrubber.py        # Emoji scrubbing logic
│   ├── ignore.py          # File filtering
│   ├── file_classifier.py # File type classification
│   ├── folder_organizer.py # Folder cleanup logic
│   ├── directory_scanner.py # Directory traversal
│   ├── tree_visualizer.py  # Tree visualization
│   ├── tree_renderer.py    # Tree rendering
│   ├── tree_comparator.py  # Tree comparison
│   ├── statistics_calculator.py # Statistics
│   └── tree_models.py      # Data models
├── tests/                  # Test suite
│   ├── test_cli.py
│   ├── test_scrubber.py
│   ├── test_folder_organizer.py
│   └── ...
├── docs/                   # Documentation
│   ├── COMMAND_REFERENCE.md
│   ├── ARCHITECTURE.md
│   └── dev/
│       ├── CONTRIBUTING.md
│       └── ...
├── examples/               # Example scripts
├── scripts/                # Utility scripts
├── pyproject.toml         # Project configuration
├── README.md              # Main documentation
└── CHANGELOG.md           # Version history
```

## Adding New Features

### Feature Development Checklist

- [ ] Create feature branch from main
- [ ] Implement feature with clear, modular code
- [ ] Add comprehensive tests (unit + property-based)
- [ ] Update relevant documentation
- [ ] Add entry to CHANGELOG.md
- [ ] Ensure all tests pass
- [ ] Verify code coverage remains high
- [ ] Test on multiple platforms if possible
- [ ] Create pull request with detailed description
- [ ] Address review feedback

### Adding a New File Category

To add a new file category to folder cleanup:

1. **Update `file_classifier.py`:**
   ```python
   CATEGORY_EXTENSIONS = {
       "YourCategory": [".ext1", ".ext2"],
       # ... existing categories
   }
   ```

2. **Update `folder_organizer.py`** if custom path needed

3. **Add tests:**
   ```python
   def test_new_category_classification():
       classifier = FileClassifier()
       assert classifier.classify("file.ext1") == "YourCategory"
   ```

4. **Update documentation:**
   - Add category to README.md
   - Update COMMAND_REFERENCE.md
   - Add to CHANGELOG.md

### Adding a New CLI Command

1. **Add command to `cli.py`:**
   ```python
   @app.command()
   def your_command(
       option: str = typer.Option(..., help="Description")
   ):
       """Command description."""
       # Implementation
   ```

2. **Add business logic** in appropriate module

3. **Add tests:**
   ```python
   def test_your_command():
       result = runner.invoke(app, ["your-command", "--option", "value"])
       assert result.exit_code == 0
   ```

4. **Update documentation:**
   - Add to README.md usage section
   - Add to COMMAND_REFERENCE.md
   - Add to CHANGELOG.md

## Getting Help

### Resources

- **Documentation**: Check the [docs/](../../docs/) directory
- **Issues**: Browse [existing issues](https://github.com/OWNER/scrubb/issues)
- **Discussions**: Join [GitHub Discussions](https://github.com/OWNER/scrubb/discussions)

### Asking Questions

When asking for help:

1. Search existing issues and discussions first
2. Provide context about what you're trying to do
3. Include relevant code snippets or error messages
4. Specify your environment (OS, Python version, etc.)
5. Describe what you've already tried

### Reporting Bugs

Include in your bug report:

- Clear description of the bug
- Steps to reproduce
- Expected behavior
- Actual behavior
- Environment details (OS, Python version, scrubb version)
- Relevant logs or error messages
- Screenshots if applicable

## Recognition

Contributors will be recognized in:

- CHANGELOG.md for their contributions
- GitHub contributors page
- Release notes for significant features

Thank you for contributing to scrubb! Your efforts help make this tool better for everyone.
