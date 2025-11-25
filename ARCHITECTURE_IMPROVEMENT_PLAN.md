# Architecture Improvement Plan

## Current State Analysis

### Problems Identified
1. **Dual Error Tracking Systems**: Both `OrganizationStats` (legacy) and `OperationSummary` (new) exist
2. **Inconsistent Naming**: `folder_organizer.py` vs `operation_results.py` - unclear module boundaries
3. **Validation Tools Unused**: Scripts exist but aren't integrated into development workflow
4. **No Type Checking**: No mypy or type validation
5. **No Linting**: No consistent code style enforcement
6. **Fragmented Testing**: Tests don't validate architecture compliance

### Root Cause
**We've been patching symptoms instead of fixing the architecture.**

The permission error issue is a symptom of poor error classification. Instead of fixing it properly, we added another layer on top.

---

## Solution: Clean Architecture Refactoring

### Phase 1: Establish Module Boundaries (Week 1)

#### 1.1 Core Domain Layer
```
scrubb/
 domain/              # Core business logic (no dependencies)
    models.py       # Data models (FileCategory, etc.)
    errors.py       # Error types and classification
    results.py      # Operation results
```

#### 1.2 Application Layer
```
scrubb/
 application/         # Use cases and orchestration
    organize_files.py    # File organization use case
    classify_files.py    # File classification use case
    cleanup_dirs.py      # Directory cleanup use case
```

#### 1.3 Infrastructure Layer
```
scrubb/
 infrastructure/      # External dependencies
    filesystem.py   # File system operations
    cli.py          # CLI interface
    formatters.py   # Output formatting
```

### Phase 2: Implement Validation Pipeline (Week 1)

#### 2.1 Pre-commit Hooks
```bash
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: mypy
        name: mypy type checking
        entry: mypy scrubb/
        language: system
        types: [python]
      
      - id: ruff
        name: ruff linting
        entry: ruff check scrubb/
        language: system
        types: [python]
      
      - id: validate-docs
        name: validate documentation
        entry: python scripts/validate_docs.py
        language: system
        pass_filenames: false
```

#### 2.2 CI/CD Pipeline
```yaml
# .github/workflows/validate.yml
name: Validate Codebase
on: [push, pull_request]
jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          pip install -e .
          pip install mypy ruff pytest hypothesis
      - name: Type check
        run: mypy scrubb/
      - name: Lint
        run: ruff check scrubb/
      - name: Run tests
        run: pytest tests/
      - name: Validate docs
        run: python scripts/validate_docs.py
```

### Phase 3: Refactor Error Handling (Week 2)

#### 3.1 Single Source of Truth
**Remove**: `OrganizationStats` (deprecated)
**Keep**: `OperationSummary` with proper error classification

#### 3.2 Error Hierarchy
```python
# scrubb/domain/errors.py
from enum import Enum
from dataclasses import dataclass
from pathlib import Path

class ErrorSeverity(Enum):
    CRITICAL = "critical"  # Blocks primary function
    WARNING = "warning"    # Doesn't block primary function
    INFO = "info"          # Informational only

class OperationType(Enum):
    FILE_MOVE = "file_move"
    DIR_REMOVE = "dir_remove"
    DIR_CREATE = "dir_create"

@dataclass
class OperationError:
    severity: ErrorSeverity
    operation: OperationType
    path: Path
    message: str
    suggestion: str | None = None
```

#### 3.3 Result Types
```python
# scrubb/domain/results.py
from dataclasses import dataclass
from typing import List

@dataclass
class FileOperationResult:
    files_moved: int
    files_by_category: dict[str, int]
    failed_operations: List[OperationError]

@dataclass
class DirectoryCleanupResult:
    directories_removed: int
    permission_denied: List[Path]
    other_failures: List[OperationError]

@dataclass
class OrganizationResult:
    file_ops: FileOperationResult
    dir_cleanup: DirectoryCleanupResult
    
    @property
    def is_successful(self) -> bool:
        """Success = files moved, even if cleanup failed"""
        return self.file_ops.files_moved > 0
    
    @property
    def has_critical_errors(self) -> bool:
        """Critical = file moves failed"""
        return len(self.file_ops.failed_operations) > 0
```

### Phase 4: Integration & Testing (Week 2)

#### 4.1 Architecture Tests
```python
# tests/test_architecture.py
def test_domain_has_no_external_dependencies():
    """Domain layer should not import from infrastructure"""
    domain_files = Path('scrubb/domain').glob('*.py')
    for file in domain_files:
        content = file.read_text()
        assert 'from scrubb.infrastructure' not in content
        assert 'import typer' not in content
        assert 'import rich' not in content

def test_all_public_functions_have_types():
    """All public functions must have type hints"""
    # Use mypy programmatically to validate
    pass
```

#### 4.2 Integration Tests
```python
# tests/test_integration.py
def test_permission_errors_dont_fail_operation():
    """Permission errors on cleanup shouldn't mark operation as failed"""
    # Create files, mock permission errors on cleanup
    # Verify: files moved successfully, operation marked as success
    pass
```

### Phase 5: Documentation & Tooling (Week 3)

#### 5.1 Architecture Decision Records
```
docs/adr/
 001-separate-error-types.md
 002-clean-architecture.md
 003-validation-pipeline.md
```

#### 5.2 Developer Guide
```markdown
# docs/DEVELOPMENT.md
## Code Organization
- `domain/`: Core business logic, no external dependencies
- `application/`: Use cases, orchestrates domain objects
- `infrastructure/`: External dependencies (CLI, filesystem)

## Adding New Features
1. Start with domain models
2. Add use case in application layer
3. Wire up in infrastructure layer
4. Add tests at each layer
5. Run validation: `make validate`

## Validation Pipeline
- Type checking: `mypy scrubb/`
- Linting: `ruff check scrubb/`
- Tests: `pytest tests/`
- Docs: `python scripts/validate_docs.py`
```

#### 5.3 Makefile for Common Tasks
```makefile
# Makefile
.PHONY: validate test lint typecheck docs

validate: typecheck lint test docs
	@echo " All validations passed"

typecheck:
	mypy scrubb/

lint:
	ruff check scrubb/

test:
	pytest tests/ -v

docs:
	python scripts/validate_docs.py

install-dev:
	pip install -e ".[dev]"
	pre-commit install

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type d -name .pytest_cache -exec rm -rf {} +
	find . -type d -name .mypy_cache -exec rm -rf {} +
```

---

## Migration Strategy

### Step 1: Add Validation (No Breaking Changes)
- Add mypy configuration
- Add ruff configuration  
- Add pre-commit hooks
- Fix type errors incrementally

### Step 2: Refactor Error Handling (Breaking Change)
- Create new `domain/` module structure
- Deprecate `OrganizationStats`
- Update all code to use `OrganizationResult`
- Update tests

### Step 3: Clean Up (Breaking Change)
- Remove deprecated code
- Reorganize modules into clean architecture
- Update all imports

### Step 4: Document & Enforce
- Add architecture tests
- Update documentation
- Enforce in CI/CD

---

## Success Metrics

1. **Code Quality**
   - 100% type coverage (mypy strict mode)
   - 0 linting errors
   - All tests passing

2. **Architecture**
   - Clear module boundaries
   - No circular dependencies
   - Domain layer has zero external dependencies

3. **Developer Experience**
   - `make validate` runs all checks
   - Pre-commit hooks catch issues early
   - Clear documentation for contributors

4. **Maintainability**
   - Single source of truth for errors
   - Consistent naming conventions
   - Automated validation prevents regression

---

## Timeline

- **Week 1**: Validation pipeline + Module structure
- **Week 2**: Error handling refactor + Integration tests
- **Week 3**: Documentation + Cleanup
- **Week 4**: Buffer for issues

---

## Next Steps

1. **Immediate**: Stop adding features, focus on architecture
2. **This Session**: Set up validation pipeline
3. **Next Session**: Begin clean architecture refactoring

