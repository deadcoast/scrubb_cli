# Execution Guide: Architectural Unification

**For:** Development Team  
**Purpose:** Step-by-step guide for executing the architectural refactoring  
**Duration:** 4 weeks  
**Commitment:** Professional code standards, no shortcuts

---

## Before You Start

### Prerequisites

1. **Read all specifications**
   - `requirements.md` - Understand what we're building
   - `design.md` - Understand how we're building it
   - `tasks.md` - Understand the implementation plan

2. **Understand the audit findings**
   - Read `CODEBASE_AUDIT.md`
   - Understand what's broken
   - Understand why it's broken

3. **Set up development environment**
   - Python 3.11+
   - All dependencies installed (`pip install -e ".[dev]"`)
   - Pre-commit hooks configured
   - IDE configured for type checking

4. **Create feature branch**
   ```bash
   git checkout -b feature/architectural-unification
   ```

### Ground Rules

1. **NO SHORTCUTS** - If it's not done right, it's not done
2. **NO QUICK FIXES** - Fix the root cause, not the symptom
3. **NO SURFACE PATCHES** - Refactor properly, don't patch over
4. **TEST EVERYTHING** - Every change must have tests
5. **DOCUMENT EVERYTHING** - Every public API must have docstrings
6. **TYPE EVERYTHING** - Every function must have type hints
7. **VALIDATE EVERYTHING** - Every input must be validated

---

## Execution Process

### For Each Task

1. **Read the task description**
   - Understand what needs to be done
   - Understand why it needs to be done
   - Understand the requirements it validates

2. **Mark task as in progress**
   ```bash
   # Use Kiro's task status tool
   # This updates the checkbox in tasks.md
   ```

3. **Implement the task**
   - Write the code
   - Follow the design document
   - Use the interfaces defined
   - Add type hints
   - Add docstrings

4. **Write tests**
   - Unit tests for the implementation
   - Property-based tests if specified
   - Integration tests if specified
   - Ensure 100% coverage of new code

5. **Run quality checks**
   ```bash
   # Type checking
   mypy scrubb/
   
   # Linting
   ruff check scrubb/
   
   # Formatting
   black --check scrubb/
   
   # Security
   bandit -r scrubb/
   
   # Tests
   pytest tests/
   ```

6. **Mark task as complete**
   ```bash
   # Use Kiro's task status tool
   # Only mark complete when ALL checks pass
   ```

7. **Commit changes**
   ```bash
   git add .
   git commit -m "feat: [task description]"
   ```

### For Each Checkpoint

1. **Run full test suite**
   ```bash
   pytest tests/ -v
   ```

2. **Run all quality checks**
   ```bash
   make validate  # Or equivalent command
   ```

3. **Review code**
   - Check for duplication
   - Check for proper error handling
   - Check for type safety
   - Check for documentation

4. **Ask user for review**
   - Present results
   - Show test output
   - Show quality check results
   - Get approval before proceeding

5. **Only proceed if all checks pass**
   - If any check fails, fix it
   - Don't move to next phase with failing tests
   - Don't compromise on quality

---

## Phase-by-Phase Guide

### Phase 1: Foundation (Week 1)

**Goal:** Create the core architecture

**Tasks:** 1.1 - 1.6

**Key Deliverables:**
- `scrubb/core/interfaces.py` - All interface definitions
- `scrubb/core/result.py` - Result types
- `scrubb/core/errors.py` - Exception hierarchy
- `scrubb/core/constants.py` - Named constants
- `scrubb/core/validation.py` - Validation functions

**Success Criteria:**
- All interfaces defined
- All result types implemented
- All exceptions implemented
- All constants defined
- Property test for error propagation passes

**Checkpoint:** Task 1.6 complete, all tests pass

---

### Phase 2: I/O Layer (Week 1)

**Goal:** Implement file and directory operations

**Tasks:** 2.1 - 2.4, Checkpoint 3

**Key Deliverables:**
- `scrubb/io/file_operations.py` - File I/O abstraction
- `scrubb/io/directory_operations.py` - Directory I/O abstraction
- `scrubb/io/path_validator.py` - Path validation and security

**Success Criteria:**
- All I/O operations return Result types
- All exceptions are handled properly
- Path validation prevents traversal attacks
- Property test for path security passes
- Unit tests for I/O layer pass

**Checkpoint:** Task 3 complete, all tests pass

---

### Phase 3: Business Logic (Week 2)

**Goal:** Implement core business logic

**Tasks:** 4.1 - 4.9, Checkpoint 5

**Key Deliverables:**
- `scrubb/business/classifier.py` - Enhanced file classifier
- `scrubb/business/conflict_resolver.py` - Conflict resolution
- `scrubb/business/organizer.py` - File organization (O(n))
- `scrubb/business/tree_builder.py` - Tree building and simulation
- `scrubb/business/statistics.py` - Statistics calculation
- `scrubb/business/emoji_detector.py` - Emoji detection

**Success Criteria:**
- All algorithms are O(n)
- All business logic uses dependency injection
- Tree simulation works without filesystem access
- Emoji detection uses grapheme clusters
- Property tests for efficiency and correctness pass
- Unit tests for business logic pass

**Checkpoint:** Task 5 complete, all tests pass

---

### Phase 4: CLI Layer (Week 2)

**Goal:** Refactor CLI to use new architecture

**Tasks:** 6.1 - 6.6, Checkpoint 7

**Key Deliverables:**
- `scrubb/cli/shared.py` - Shared utilities (no duplication)
- `scrubb/cli/output.py` - Output formatting
- `scrubb/cli/input.py` - Input handling
- `scrubb/cli/commands.py` - Command handlers
- Updated `scrubb/cli.py` - Main CLI module

**Success Criteria:**
- Zero code duplication in CLI
- All command handlers use dependency injection
- CLI layer doesn't access filesystem directly
- Property test for layer separation passes
- Unit tests for CLI layer pass

**Checkpoint:** Task 7 complete, all tests pass

---

### Phase 5: Integration (Week 3)

**Goal:** Integrate everything and migrate existing code

**Tasks:** 8.1 - 8.7, Checkpoint 9

**Key Deliverables:**
- Updated `scrubb/config.py` - Configuration validation
- `scrubb/core/logging.py` - Structured logging
- Updated existing modules to use new architecture
- Integration tests
- Property-based tests for integration

**Success Criteria:**
- Configuration validation works
- Structured logging works
- All existing modules use new architecture
- Integration tests pass
- Property tests for code quality pass
- Zero mypy errors
- Zero ruff warnings

**Checkpoint:** Task 9 complete, all tests pass

---

### Phase 6: Quality (Week 3)

**Goal:** Ensure production readiness

**Tasks:** 10.1 - 10.4, Checkpoint 11

**Key Deliverables:**
- Performance benchmarks
- Code quality gates
- CI configuration
- Updated documentation
- Updated CHANGELOG

**Success Criteria:**
- Performance benchmarks pass
- All quality gates pass
- CI runs successfully
- Documentation is complete
- CHANGELOG is updated

**Checkpoint:** Task 11 complete, all tests pass

---

### Phase 7: Release (Week 4)

**Goal:** Clean up and release

**Tasks:** 12.1 - 12.3, Checkpoint 13

**Key Deliverables:**
- Removed deprecated code
- Final validation
- Version 2.0.0 release
- Rollback strategy

**Success Criteria:**
- No deprecated code remains
- All tests pass
- All quality checks pass
- Release is tagged
- Rollback strategy is documented

**Final Checkpoint:** Task 13 complete, ready for deployment

---

## Quality Standards

### Code Quality

Every file must:
- Have type hints on all functions
- Have docstrings on all public APIs
- Have zero mypy errors
- Have zero ruff warnings
- Have zero bandit security issues
- Have test coverage

### Testing Standards

Every component must have:
- Unit tests (test in isolation)
- Integration tests (test with real dependencies)
- Property-based tests (test with generated inputs)
- 100% coverage of new code

### Documentation Standards

Every public API must have:
- Docstring with description
- Parameter documentation
- Return value documentation
- Exception documentation
- Usage examples (where appropriate)

### Performance Standards

Every algorithm must:
- Have documented time complexity
- Have documented space complexity
- Have performance benchmarks
- Not regress from previous version

---

## Common Pitfalls to Avoid

### 1. Skipping Tests
**DON'T:** "I'll write tests later"  
**DO:** Write tests as you implement

### 2. Bare Except Clauses
**DON'T:** `except:` or `except Exception:`  
**DO:** `except SpecificException:`

### 3. Returning None on Error
**DON'T:** `return None` when operation fails  
**DO:** `return Failure(error)`

### 4. Direct File System Access
**DON'T:** `Path.read_text()` in business logic  
**DO:** Use `FileOperations` interface

### 5. Duplicating Code
**DON'T:** Copy-paste similar code  
**DO:** Extract shared function

### 6. Missing Type Hints
**DON'T:** `def func(x):` without types  
**DO:** `def func(x: int) -> str:`

### 7. Vague Error Messages
**DON'T:** `raise ValueError("Invalid")`  
**DO:** `raise ValidationError("Path must be absolute", context={"path": str(path)})`

### 8. Ignoring Checkpoints
**DON'T:** Continue with failing tests  
**DO:** Fix all issues before proceeding

---

## When Things Go Wrong

### Test Failures

1. **Don't skip the test** - Fix the code or fix the test
2. **Don't comment out the test** - That's hiding the problem
3. **Understand why it failed** - Read the error message
4. **Fix the root cause** - Don't patch the symptom

### Type Errors

1. **Don't use `# type: ignore`** - Fix the type issue
2. **Don't use `Any`** - Use proper types
3. **Don't remove type hints** - Add correct type hints

### Performance Issues

1. **Don't optimize prematurely** - But don't write O(n²) either
2. **Profile before optimizing** - Measure, don't guess
3. **Document complexity** - Help future maintainers

### Merge Conflicts

1. **Don't force push** - Resolve conflicts properly
2. **Don't delete others' code** - Understand what it does
3. **Test after resolving** - Ensure nothing broke

---

## Getting Help

### When Stuck

1. **Read the specification** - The answer is probably there
2. **Read the design document** - Understand the architecture
3. **Read the audit** - Understand what's broken
4. **Ask for clarification** - Don't guess

### When Unsure

1. **Ask before implementing** - Better to ask than to redo
2. **Propose alternatives** - If you have a better idea
3. **Document decisions** - Help future maintainers

### When Blocked

1. **Identify the blocker** - What's preventing progress?
2. **Communicate early** - Don't wait until deadline
3. **Propose solutions** - Come with options, not just problems

---

## Success Metrics

### Week 1
- ✅ Foundation complete
- ✅ I/O layer complete
- ✅ All tests passing
- ✅ Zero mypy errors

### Week 2
- ✅ Business logic complete
- ✅ CLI layer complete
- ✅ All tests passing
- ✅ Zero code duplication

### Week 3
- ✅ Integration complete
- ✅ Quality gates complete
- ✅ All tests passing
- ✅ Documentation complete

### Week 4
- ✅ Cleanup complete
- ✅ Release ready
- ✅ All tests passing
- ✅ Version 2.0.0 tagged

---

## Final Checklist

Before marking the refactoring complete:

- [ ] All tasks completed
- [ ] All tests passing
- [ ] Zero mypy errors
- [ ] Zero ruff warnings
- [ ] Zero bandit issues
- [ ] All documentation updated
- [ ] CHANGELOG updated
- [ ] Performance benchmarks passing
- [ ] CI passing
- [ ] Code review complete
- [ ] User acceptance testing complete
- [ ] Rollback strategy documented
- [ ] Release notes written
- [ ] Version tagged

---

## Remember

**WE ARE PROFESSIONAL DEVELOPERS**

We don't take shortcuts.  
We don't make quick fixes.  
We don't apply surface patches.  
We fix things properly.  
We maintain high standards.  
We write correct code.  

**THIS IS OUR COMMITMENT TO EXCELLENCE.**

---

**NOW GO BUILD SOMETHING GREAT.**
