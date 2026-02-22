# Testing the Commit Skill

This document describes how to test the commit skill.

## Test Suite

This skill includes a comprehensive test suite using [bats-core](https://github.com/bats-core/bats-core).

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
bats skills/commit/tests/pre-commit.bats
```

### Test Coverage

The test suite (`tests/pre-commit.bats`) includes:
- GPG signing configuration validation
- Branch creation on main/master
- Semantic branch naming (skill/, test/, docs/, update/ prefixes)
- Custom branch prefix support
- Detached HEAD state handling
- No changes handling

### Test Structure

Tests use isolated temporary git repositories created in `setup()` and cleaned up in `teardown()` to ensure test isolation.

## Writing Tests

When adding tests for this skill:
1. Add test cases to `tests/pre-commit.bats`
2. Use `setup()` and `teardown()` for isolation
3. Test both success and failure scenarios
4. Use `BATS_TEST_DIRNAME` for portable paths
