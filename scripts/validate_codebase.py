#!/usr/bin/env python3
"""
Comprehensive Codebase Validation

Runs all validation checks and provides a summary report.
"""

import subprocess
import sys
from pathlib import Path
from typing import List, Tuple


class ValidationResult:
    def __init__(self, name: str, passed: bool, output: str = ""):
        self.name = name
        self.passed = passed
        self.output = output


def run_command(cmd: List[str], name: str) -> ValidationResult:
    """Run a command and return validation result."""
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False
        )
        passed = result.returncode == 0
        output = result.stdout + result.stderr
        return ValidationResult(name, passed, output)
    except FileNotFoundError:
        return ValidationResult(name, False, f"Command not found: {cmd[0]}")


def validate_tests() -> ValidationResult:
    """Run pytest test suite."""
    return run_command(
        ["python", "-m", "pytest", "tests/", "-v", "--tb=short"],
        "Test Suite"
    )


def validate_types() -> ValidationResult:
    """Run mypy type checking."""
    return run_command(
        ["python", "-m", "mypy", "scrubb/", "--ignore-missing-imports"],
        "Type Checking"
    )


def validate_lint() -> ValidationResult:
    """Run ruff linting."""
    return run_command(
        ["python", "-m", "ruff", "check", "scrubb/"],
        "Code Linting"
    )


def validate_docs() -> ValidationResult:
    """Run documentation validation."""
    return run_command(
        ["python", "scripts/validate_docs.py"],
        "Documentation"
    )


def check_architecture() -> ValidationResult:
    """Check for architecture violations."""
    violations = []
    
    # Check 1: Domain layer shouldn't import from infrastructure
    domain_path = Path("scrubb/domain")
    if domain_path.exists():
        for file in domain_path.glob("*.py"):
            content = file.read_text()
            if "from scrubb.infrastructure" in content or "from scrubb.cli" in content:
                violations.append(f"{file.name}: Domain imports from infrastructure")
    
    # Check 2: No circular imports (basic check)
    # This would need more sophisticated analysis
    
    if violations:
        return ValidationResult(
            "Architecture",
            False,
            "\n".join(violations)
        )
    return ValidationResult("Architecture", True, "No violations found")


def print_header():
    """Print validation header."""
    print("=" * 70)
    print("CODEBASE VALIDATION REPORT")
    print("=" * 70)
    print()


def print_result(result: ValidationResult):
    """Print a single validation result."""
    status = " PASS" if result.passed else " FAIL"
    color = "\033[92m" if result.passed else "\033[91m"
    reset = "\033[0m"
    
    print(f"{color}{status}{reset} {result.name}")
    
    if not result.passed and result.output:
        # Print first few lines of output
        lines = result.output.split("\n")[:10]
        for line in lines:
            if line.strip():
                print(f"    {line}")
        if len(result.output.split("\n")) > 10:
            print("    ... (output truncated)")
    print()


def print_summary(results: List[ValidationResult]):
    """Print validation summary."""
    passed = sum(1 for r in results if r.passed)
    failed = len(results) - passed
    
    print("=" * 70)
    print(f"SUMMARY: {passed} passed, {failed} failed")
    print("=" * 70)
    
    if failed > 0:
        print("\nFailed checks:")
        for result in results:
            if not result.passed:
                print(f"  - {result.name}")
        print("\nRun individual checks for details:")
        print("  make test      - Run tests")
        print("  make typecheck - Run type checking")
        print("  make lint      - Run linting")
        print("  make docs      - Validate documentation")


def main():
    """Run all validations."""
    print_header()
    
    # Run all validations
    validations = [
        ("Tests", validate_tests),
        ("Type Checking", validate_types),
        ("Linting", validate_lint),
        ("Documentation", validate_docs),
        ("Architecture", check_architecture),
    ]
    
    results = []
    for name, validator in validations:
        print(f"Running {name}...")
        result = validator()
        results.append(result)
        print_result(result)
    
    print_summary(results)
    
    # Exit with error if any validation failed
    if any(not r.passed for r in results):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
