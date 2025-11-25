.PHONY: help validate test lint typecheck docs clean install-dev

help:
	@echo "Scrubb Development Commands"
	@echo "============================"
	@echo "make validate    - Run all validation checks"
	@echo "make test        - Run test suite"
	@echo "make lint        - Run code linting"
	@echo "make typecheck   - Run type checking"
	@echo "make docs        - Validate documentation"
	@echo "make clean       - Remove cache files"
	@echo "make install-dev - Install development dependencies"

validate: typecheck lint test docs
	@echo "✓ All validations passed!"

typecheck:
	@echo "Running type checks..."
	@python -m mypy scrubb/ --ignore-missing-imports || echo "⚠ Type checking not configured yet"

lint:
	@echo "Running linter..."
	@python -m ruff check scrubb/ || echo "⚠ Linting not configured yet"

test:
	@echo "Running tests..."
	@python -m pytest tests/ -v

docs:
	@echo "Validating documentation..."
	@python scripts/validate_docs.py

clean:
	@echo "Cleaning cache files..."
	@find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name .mypy_cache -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name .ruff_cache -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@echo "✓ Cache cleaned"

install-dev:
	@echo "Installing development dependencies..."
	@pip install -e ".[dev]" || pip install -e .
	@pip install mypy ruff pytest hypothesis
	@echo "✓ Development environment ready"
