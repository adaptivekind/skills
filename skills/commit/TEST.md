# Testing the Commit Skill

This document describes how to test the commit skill.

## Test Suite

This skill includes a comprehensive test suite using [pytest](https://docs.pytest.org/).

### Running Tests

**Run all skill tests:**
```bash
make test
```

**Run only commit skill tests:**
```bash
make test-commit
```

**Run specific test file:**
```bash
pytest skills/commit/tests/test_pre_commit.py -v
```

### Test Coverage

The test suite (`tests/test_pre_commit.py`) includes:
- GPG signing configuration validation
- Branch creation on main/master
- Semantic branch naming (skill/, test/, docs/, update/ prefixes)
- Custom branch prefix support
- Detached HEAD state handling
- No changes handling

### Test Structure

Tests use pytest fixtures with isolated temporary git repositories created for each test and cleaned up automatically to ensure test isolation.

## Writing Tests

When adding tests for this skill:
1. Add test cases to `tests/test_pre_commit.py`
2. Use pytest fixtures for isolation
3. Test both success and failure scenarios
4. Use the `git_repo` fixture for git repository setup
