# Development Guide

## Getting Started

### Prerequisites
- Python 3.11 or higher
- pip or uv package manager

### Setup Development Environment

```bash
# Clone the repository
git clone <repository-url>
cd scrubb_cli

# Install in development mode with dev dependencies
make install-dev

# Or manually:
pip install -e ".[dev]"
```

## Code Organization

### Current Structure (Being Refactored)
```
scrubb/
 cli.py                    # CLI interface (infrastructure)
 file_classifier.py        # File classification logic
 folder_organizer.py       # File organization logic
 operation_results.py      # Result types (NEW)
 output_formatter.py       # Output formatting
 prompt_utils.py           # User prompts
 tree_*.py                 # Tree visualization
 verbosity.py              # Logging configuration
```

### Target Structure (Clean Architecture)
```
scrubb/
 domain/                   # Core business logic (no external deps)
    models.py            # Data models
    errors.py            # Error types
    results.py           # Operation results
 application/              # Use cases
    organize_files.py    # File organization use case
    classify_files.py    # Classification use case
 infrastructure/           # External dependencies
     cli.py               # CLI interface
     filesystem.py        # File system operations
     formatters.py        # Output formatting
```

## Development Workflow

### 1. Before Making Changes

```bash
# Ensure all tests pass
make test

# Run full validation
make validate
```

### 2. Making Changes

1. **Write tests first** (TDD approach)
2. **Implement the feature**
3. **Run validation** after each change

```bash
# Quick feedback loop
make test          # Run tests
make lint          # Check code style
make typecheck     # Check types
```

### 3. Before Committing

```bash
# Run full validation
make validate

# This runs:
# - Type checking (mypy)
# - Linting (ruff)
# - Tests (pytest)
# - Documentation validation
```

## Validation Pipeline

### Type Checking (mypy)
```bash
make typecheck
```

We use mypy for static type checking. Configuration in `pyproject.toml`:
- Domain layer: Strict typing required
- Other layers: Gradual typing (being improved)

### Linting (ruff)
```bash
make lint
```

We use ruff for fast Python linting. It checks:
- Code style (PEP 8)
- Common bugs
- Import sorting
- Code simplification opportunities

### Testing (pytest + hypothesis)
```bash
make test
```

We use:
- **pytest** for unit and integration tests
- **hypothesis** for property-based testing

Test organization:
- `tests/test_*.py` - Unit tests
- `tests/test_*_properties.py` - Property-based tests
- `tests/test_*_integration.py` - Integration tests

### Documentation Validation
```bash
make docs
```

Validates that:
- Command examples in docs match actual CLI
- File extensions in docs match code
- Links are valid

## Architecture Guidelines

### Layer Dependencies
```
Infrastructure → Application → Domain
```

**Rules:**
1. Domain layer has NO external dependencies
2. Application layer depends only on domain
3. Infrastructure layer can depend on both

### Error Handling

**DO:**
- Classify errors by severity (CRITICAL, WARNING, INFO)
- Separate file operation errors from cleanup errors
- Provide actionable error messages

**DON'T:**
- Mix error types in the same counter
- Treat warnings as failures
- Use generic error messages

### Example: Adding a New Feature

```python
# 1. Define domain model (scrubb/domain/models.py)
@dataclass
class FileOperation:
    source: Path
    destination: Path
    category: FileCategory

# 2. Define use case (scrubb/application/organize_files.py)
class OrganizeFilesUseCase:
    def execute(self, directory: Path) -> OrganizationResult:
        # Business logic here
        pass

# 3. Wire up in CLI (scrubb/infrastructure/cli.py)
@app.command()
def organize(path: str):
    use_case = OrganizeFilesUseCase()
    result = use_case.execute(Path(path))
    # Display result
```

## Testing Guidelines

### Unit Tests
- Test individual functions/classes
- Mock external dependencies
- Fast execution

```python
def test_file_classifier_returns_correct_category():
    classifier = FileClassifier()
    assert classifier.classify(Path("test.jpg")) == FileCategory.IMAGE
```

### Property-Based Tests
- Test properties that should hold for ALL inputs
- Use hypothesis to generate test cases
- Tag with the property being tested

```python
@given(st.text())
def test_round_trip_property(filename: str):
    """For any filename, classify then format should be consistent"""
    # Property test here
```

### Integration Tests
- Test multiple components together
- Use real file system (in temp directories)
- Verify end-to-end behavior

```python
def test_folder_command_organizes_files():
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create test files
        # Run command
        # Verify results
```

## Common Tasks

### Adding a New File Category

1. Update `FileCategory` enum
2. Add extensions to `FileClassifier`
3. Update tests
4. Update documentation
5. Run validation

### Fixing a Bug

1. Write a failing test that reproduces the bug
2. Fix the bug
3. Verify test passes
4. Run full validation
5. Update documentation if needed

### Refactoring

1. Ensure tests pass before starting
2. Make small, incremental changes
3. Run tests after each change
4. Keep tests passing throughout
5. Update documentation

## Troubleshooting

### Tests Failing
```bash
# Run specific test
pytest tests/test_file_classifier.py::test_specific_function -v

# Run with more output
pytest tests/ -vv --tb=long

# Run only failed tests
pytest --lf
```

### Type Errors
```bash
# Check specific file
mypy scrubb/file_classifier.py

# See all errors
mypy scrubb/ --ignore-missing-imports
```

### Linting Errors
```bash
# Auto-fix what's possible
ruff check scrubb/ --fix

# See specific rule
ruff check scrubb/ --select E501
```

## Resources

- [Architecture Improvement Plan](../ARCHITECTURE_IMPROVEMENT_PLAN.md)
- [Testing Strategy](test_strategy.md)
- [API Documentation](api.md)

## Getting Help

- Check existing tests for examples
- Review architecture plan for design decisions
- Ask questions in issues/discussions
