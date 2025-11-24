# Documentation Validation Plan

This document outlines the process for validating that documentation accurately reflects the source code.

## Validation Checklist

### 1. Command Syntax Validation

**Files to Check:**
- `README.md`
- `COMMAND_REFERENCE.md`
- `OVERVIEW.md`

**Validation Steps:**
1. Extract all command examples from documentation
2. Compare against actual CLI command definitions in `scrubb/cli.py`
3. Verify command names, options, and flags match exactly

**Current Commands (from cli.py):**
- `scrubb [PATH] [EXECUTOR]` - Main emoji scrubbing (default command)
- `scrubb stats [--top] [--reset]` - View/manage statistics
- `scrubb config [-p PATH] [--show] [--edit]` - Configuration management
- `scrubb folder [--dry]` - Folder cleanup (NOT `--folder`)

### 2. Option/Flag Validation

**Validation Steps:**
1. List all options/flags mentioned in documentation
2. Verify each exists in the corresponding `@app.command()` definition
3. Check that help text matches between docs and code

**Current Flags:**
- `--dry` (folder command) - Dry-run mode
- `--top` (stats command) - Show top emoji tokens
- `--reset` (stats command) - Reset statistics
- `--show` (config command) - Show configuration
- `--edit` (config command) - Edit configuration
- `-p PATH` (config command) - Path parameter

### 3. Path Handling Validation

**Test Cases:**
1. Absolute paths: `/full/path/to/directory`
2. Relative paths: `./relative/path`
3. Tilde expansion: `~/home/directory`
4. Paths with spaces: `"C:\Users\Name\My Documents"`
5. Quoted paths: Both single and double quotes

**Code Implementation:**
```python
# In cli.py folder() command:
path_input = typer.prompt("Enter the directory path to organize")
path_input = path_input.strip().strip('"').strip("'")  # Strip quotes
target_path = Path(path_input).expanduser().resolve()
```

### 4. Output Format Validation

**Validation Steps:**
1. Run each command with various inputs
2. Compare actual output with documented examples
3. Verify all mentioned output sections appear

**Commands to Test:**
- `scrubb folder --dry` - Check dry-run output format
- `scrubb folder` - Check regular output format
- `scrubb stats` - Check statistics output
- `scrubb stats --top` - Check top emoji output
- `scrubb config` - Check configuration output

### 5. File Category Validation

**Validation Steps:**
1. Extract file extensions from documentation
2. Compare with `FileClassifier` definitions in `scrubb/file_classifier.py`
3. Ensure all documented extensions are actually supported

**Categories to Verify:**
- Images
- Video
- Markdown Documents
- Other Documents
- Development Files

### 6. Error Message Validation

**Validation Steps:**
1. List all error messages mentioned in documentation
2. Search for corresponding error messages in source code
3. Verify error codes match

**Error Scenarios:**
- Non-existent path
- Path is not a directory
- Permission errors
- Invalid configuration

## Automated Validation Script

Create a script to automate validation:

```python
# validate_docs.py
import re
from pathlib import Path

def extract_commands_from_docs(doc_file):
    """Extract all command examples from markdown files."""
    with open(doc_file) as f:
        content = f.read()
    
    # Find all code blocks with bash/shell commands
    pattern = r'```(?:bash|shell|powershell)\n(.*?)```'
    matches = re.findall(pattern, content, re.DOTALL)
    
    commands = []
    for match in matches:
        lines = match.strip().split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith('scrubb ') and not line.startswith('#'):
                commands.append(line)
    
    return commands

def validate_command_syntax(commands):
    """Validate that commands match actual CLI structure."""
    valid_commands = [
        'scrubb',
        'scrubb stats',
        'scrubb config',
        'scrubb folder'
    ]
    
    valid_flags = [
        '--dry',
        '--top',
        '--reset',
        '--show',
        '--edit',
        '-p'
    ]
    
    errors = []
    for cmd in commands:
        # Check for deprecated --folder syntax
        if '--folder' in cmd and 'scrubb --folder' in cmd:
            errors.append(f"Deprecated syntax: {cmd} (should be 'scrubb folder')")
    
    return errors

def main():
    docs = ['README.md', 'COMMAND_REFERENCE.md', 'OVERVIEW.md']
    
    all_errors = []
    for doc in docs:
        if Path(doc).exists():
            print(f"\nValidating {doc}...")
            commands = extract_commands_from_docs(doc)
            errors = validate_command_syntax(commands)
            
            if errors:
                print(f"   Found {len(errors)} issues:")
                for error in errors:
                    print(f"    - {error}")
                all_errors.extend(errors)
            else:
                print(f"   No issues found")
    
    if all_errors:
        print(f"\n Total issues: {len(all_errors)}")
        return 1
    else:
        print("\n All documentation validated successfully!")
        return 0

if __name__ == '__main__':
    exit(main())
```

## Manual Testing Checklist

### Test 1: Basic Folder Command
```bash
scrubb folder --dry
# Enter a valid path when prompted
# Verify output matches documented format
```

### Test 2: Path with Spaces
```bash
scrubb folder --dry
# Enter: "C:\Users\Name\My Documents"
# Verify path is correctly parsed without quotes in error message
```

### Test 3: Quoted Paths
```bash
scrubb folder
# Enter: '/path/with spaces/directory'
# Verify single quotes are stripped
```

### Test 4: All Commands
```bash
scrubb --help
scrubb stats
scrubb stats --top
scrubb config
scrubb config --show
scrubb folder --help
```

## Continuous Validation

**Pre-commit Hook:**
1. Run validation script before each commit
2. Fail commit if documentation is out of sync

**CI/CD Integration:**
1. Add documentation validation to test suite
2. Run on every pull request
3. Block merge if validation fails

## Update Process

When updating commands or features:

1. **Update Source Code First**
   - Modify `cli.py` or other source files
   - Update tests to match new behavior

2. **Update Documentation**
   - Update `README.md` with user-facing changes
   - Update `COMMAND_REFERENCE.md` with detailed command info
   - Update `OVERVIEW.md` with high-level changes

3. **Validate**
   - Run validation script
   - Manually test all documented examples
   - Fix any discrepancies

4. **Commit Together**
   - Commit source code and documentation changes together
   - Reference validation in commit message

## Known Issues Fixed

### Issue 1: Command Syntax
- **Problem**: Documentation used `scrubb --folder` but actual command is `scrubb folder`
- **Fix**: Updated all documentation to use correct `scrubb folder` syntax
- **Files Updated**: README.md, COMMAND_REFERENCE.md, OVERVIEW.md

### Issue 2: Path Handling with Quotes
- **Problem**: Paths with quotes were not stripped, causing path resolution errors
- **Fix**: Added `.strip('"').strip("'")` to path input processing
- **File Updated**: scrubb/cli.py

### Issue 3: Path with Spaces
- **Problem**: Paths with spaces required quotes but quotes were included in path
- **Fix**: Strip quotes from user input before path resolution
- **File Updated**: scrubb/cli.py

## Validation Status

-  Command syntax corrected across all documentation
-  Path handling fixed to strip quotes
-  All tests passing
- ⏳ Automated validation script (to be implemented)
- ⏳ CI/CD integration (to be implemented)
