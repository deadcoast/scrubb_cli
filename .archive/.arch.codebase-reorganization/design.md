# Design Document

## Overview

This document describes the design for reorganizing the scrubb codebase to improve project structure, maintainability, and professionalism. The reorganization will create a clean, well-organized directory structure while preserving all functionality and test coverage.

### Goals
- Clean up root directory by moving documentation and utility files to appropriate folders
- Establish clear documentation structure with user and developer sections
- Organize auxiliary files (examples, scripts) into dedicated folders
- Remove irrelevant personal content from the repository
- Update all documentation references to reflect new structure
- Preserve all core functionality and test coverage

### Non-Goals
- Modifying core source code in scrubb/ directory
- Changing test implementations
- Altering project configuration (pyproject.toml)
- Refactoring application logic

## Architecture

### High-Level Design

The reorganization follows a simple file system operation pattern:
1. **Analysis Phase** - Identify files to move, delete, or create
2. **Validation Phase** - Verify operations won't break functionality
3. **Execution Phase** - Perform file operations in safe order
4. **Verification Phase** - Validate results and update references

### Component Overview

```
Reorganization System
 File Analyzer - Identifies files and their target locations
 Content Validator - Verifies file content and links
 File Mover - Performs safe file operations
 Link Updater - Updates documentation references
 Verification Runner - Validates final state
```

## Components and Interfaces

### File Analyzer

**Purpose:** Identify files that need to be moved, deleted, or created.

**Interface:**
```python
class FileAnalyzer:
    def analyze_root_directory(self, root_path: Path) -> AnalysisResult
    def identify_documentation_files(self) -> List[Path]
    def identify_utility_files(self) -> List[Path]
    def identify_files_to_delete(self) -> List[Path]
```

**Responsibilities:**
- Scan root directory for documentation files
- Identify utility scripts and demo files
- Flag files for deletion (.paths.md, potentially OVERVIEW.md)
- Generate file operation plan


### Content Validator

**Purpose:** Validate file content and verify links before and after operations.

**Interface:**
```python
class ContentValidator:
    def validate_file_content(self, file_path: Path) -> bool
    def extract_links(self, markdown_file: Path) -> List[str]
    def verify_links_exist(self, links: List[str], base_path: Path) -> List[str]
    def compare_file_content(self, original: Path, moved: Path) -> bool
```

**Responsibilities:**
- Extract markdown links from documentation
- Verify links point to existing files
- Compare file content before/after moves
- Validate file integrity

### File Mover

**Purpose:** Perform safe file system operations.

**Interface:**
```python
class FileMover:
    def create_directory(self, dir_path: Path) -> bool
    def move_file(self, source: Path, destination: Path) -> bool
    def delete_file(self, file_path: Path) -> bool
    def preserve_permissions(self, source: Path, destination: Path) -> bool
```

**Responsibilities:**
- Create new directory structure
- Move files to new locations
- Delete irrelevant files
- Preserve file permissions and attributes

### Link Updater

**Purpose:** Update documentation references to reflect new file locations.

**Interface:**
```python
class LinkUpdater:
    def update_links_in_file(self, file_path: Path, link_map: Dict[str, str]) -> bool
    def generate_link_map(self, moves: List[FileMove]) -> Dict[str, str]
    def update_readme(self, readme_path: Path, new_structure: Dict) -> bool
```

**Responsibilities:**
- Generate mapping of old to new file locations
- Update links in documentation files
- Update README with new structure
- Preserve link text and context


### Verification Runner

**Purpose:** Validate the final state after reorganization.

**Interface:**
```python
class VerificationRunner:
    def verify_directory_structure(self, expected: Dict) -> bool
    def verify_file_locations(self, expected_moves: List[FileMove]) -> bool
    def run_test_suite(self) -> TestResult
    def verify_no_broken_links(self, docs_path: Path) -> List[str]
```

**Responsibilities:**
- Verify new directory structure exists
- Confirm files are in expected locations
- Run test suite to verify functionality
- Check for broken links in documentation

## Data Models

### AnalysisResult

```python
@dataclass
class AnalysisResult:
    files_to_move: List[FileMove]
    files_to_delete: List[Path]
    directories_to_create: List[Path]
    files_to_create: List[FileCreate]
```

### FileMove

```python
@dataclass
class FileMove:
    source: Path
    destination: Path
    file_type: FileType  # DOCUMENTATION, UTILITY, EXAMPLE
    preserve_permissions: bool = True
```

### FileCreate

```python
@dataclass
class FileCreate:
    path: Path
    content_template: str
    file_type: FileType
```

### FileType

```python
class FileType(Enum):
    DOCUMENTATION = "documentation"
    DEV_DOCUMENTATION = "dev_documentation"
    UTILITY_SCRIPT = "utility_script"
    EXAMPLE_SCRIPT = "example_script"
    CHANGELOG = "changelog"
```


## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system-essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Directory preservation

*For any* critical directory (scrubb/, tests/, .kiro/, .archive/), after reorganization the directory should still exist at its original location.
**Validates: Requirements 1.5**

### Property 2: File content preservation

*For any* file that is moved, the content at the destination should be identical to the content at the source before the move.
**Validates: Requirements 2.5, 3.3**

### Property 3: Permission preservation

*For any* file that is moved, if the source file was executable, the destination file should also be executable.
**Validates: Requirements 3.4**

### Property 4: Deletion isolation

*For any* file deletion operation, no other files should be modified or deleted as a side effect.
**Validates: Requirements 4.4**

### Property 5: Link validity

*For any* markdown link in any documentation file after reorganization, the link should point to an existing file or valid URL.
**Validates: Requirements 5.2, 5.3, 5.5**

### Property 6: Link text preservation

*For any* link that is updated, the link text (the visible text in square brackets) should remain unchanged.
**Validates: Requirements 5.4**

### Property 7: Source code immutability

*For any* file in the scrubb/ directory, the file content should be identical before and after reorganization.
**Validates: Requirements 6.1**

### Property 8: Test code immutability

*For any* file in the tests/ directory, the file content should be identical before and after reorganization.
**Validates: Requirements 6.2**


## Error Handling

### File Operation Errors

**Scenario:** File move operation fails due to permissions or disk space

**Handling:**
- Log the error with full context (source, destination, error message)
- Roll back any partial operations
- Report failed operations to user
- Continue with remaining operations if possible

### Link Update Errors

**Scenario:** Unable to update links in a documentation file

**Handling:**
- Log the file and specific links that couldn't be updated
- Create a report of manual fixes needed
- Don't fail the entire operation
- Warn user about manual intervention required

### Validation Errors

**Scenario:** Post-reorganization validation fails (broken links, missing files)

**Handling:**
- Generate detailed validation report
- List all validation failures
- Provide remediation steps
- Don't automatically roll back (allow manual inspection)

### Test Suite Failures

**Scenario:** Test suite fails after reorganization

**Handling:**
- Report which tests failed
- Provide diff of any changed files
- Suggest rollback if core functionality affected
- Allow user to decide whether to proceed

## Testing Strategy

### Unit Testing

Unit tests will cover:
- File analyzer correctly identifies files by type
- Content validator accurately extracts and validates links
- File mover handles edge cases (existing files, permissions)
- Link updater correctly transforms links
- Verification runner detects missing files and broken links

### Property-Based Testing

Property-based tests will verify:
- File content preservation across all moves
- Permission preservation for executable files
- Link validity after updates
- Source code immutability
- Test code immutability

**Testing Framework:** pytest with Hypothesis for property-based testing

**Test Configuration:** Minimum 100 iterations per property test

**Property Test Tagging:** Each property test will include a comment:
`# Feature: codebase-reorganization, Property N: [property description]`


### Integration Testing

Integration tests will verify:
- Complete reorganization workflow from analysis to verification
- Multiple file moves in sequence
- Link updates across multiple documentation files
- Test suite execution after reorganization

### Manual Testing

Manual verification will include:
- Visual inspection of new directory structure
- Spot-checking moved file content
- Clicking links in documentation to verify they work
- Running application commands to ensure functionality
- Reviewing generated documentation (CHANGELOG, ARCHITECTURE, CONTRIBUTING)

## Implementation Phases

### Phase 1: Analysis and Planning
1. Scan root directory and identify all files
2. Classify files by type (documentation, utility, example, etc.)
3. Generate file operation plan (moves, deletes, creates)
4. Validate plan doesn't conflict with existing structure

### Phase 2: Directory Creation
1. Create docs/ directory
2. Create docs/dev/ subdirectory
3. Create examples/ directory
4. Create scripts/ directory
5. Verify all directories created successfully

### Phase 3: File Relocation
1. Move documentation files to docs/
2. Move developer documentation to docs/dev/
3. Move example scripts to examples/
4. Move utility scripts to scripts/
5. Verify all files moved successfully
6. Verify file content preserved

### Phase 4: File Deletion
1. Delete .paths.md
2. Evaluate and potentially delete OVERVIEW.md
3. Verify deletions completed
4. Verify no unintended deletions

### Phase 5: Link Updates
1. Extract all links from documentation files
2. Generate link mapping (old → new locations)
3. Update links in all documentation files
4. Update README with new structure
5. Verify all links valid

### Phase 6: New Documentation Creation
1. Create CHANGELOG.md with version 0.1.0
2. Create docs/ARCHITECTURE.md
3. Create docs/dev/CONTRIBUTING.md
4. Verify all new files created

### Phase 7: Verification
1. Verify directory structure matches expected
2. Verify all files in correct locations
3. Run test suite (all 71 tests should pass)
4. Verify no broken links in documentation
5. Generate verification report

## Rollback Strategy

If critical errors occur during reorganization:

1. **Preserve Original State:** Create backup of root directory before starting
2. **Incremental Operations:** Perform operations in phases with checkpoints
3. **Rollback Capability:** Maintain operation log to reverse changes
4. **Validation Gates:** Don't proceed to next phase if current phase fails validation

**Rollback Triggers:**
- Test suite failures after reorganization
- More than 5 broken links detected
- Core source files modified unexpectedly
- User manually requests rollback

