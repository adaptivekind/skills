# Development Guide

This guide explains how to set up your local development environment and run tests for the skills repository.

## Prerequisites

- Git (with GPG signing configured)
- GitHub CLI (`gh`)
- Make
- Python 3.x with pytest (for running tests)
- pre-commit (for git hooks)

## Installing Dependencies

### macOS (using Homebrew)

```bash
# Install Python if not present
brew install python

# Install pytest
pip install pytest

# Install pre-commit
brew install pre-commit
```

### Linux

```bash
# Install Python if not present
sudo apt-get install python3 python3-pip

# Install pytest
pip3 install pytest

# Install pre-commit
pip3 install pre-commit
```

## Setting Up Pre-Commit Hooks

This repository uses [pre-commit](https://pre-commit.com/) to run checks before commits.

### Install pre-commit hooks:

```bash
pre-commit install
```

### Run hooks manually:

```bash
# Run all hooks on all files
pre-commit run --all-files

# Run specific hook
pre-commit run black
```

### Update hooks:

```bash
pre-commit autoupdate
```

The pre-commit config includes:
- trailing-whitespace, end-of-file-fixer
- check-yaml, check-json, check-toml
- check-added-large-files, check-merge-conflict
- black (code formatting)
- isort (import sorting)
- flake8 (linting)
- gitleaks (secret detection)

## Running Tests Locally

### Run All Tests

```bash
make test
```

This will find and run all Python test files in the `skills/` directory.

### Run Specific Skill Tests

```bash
# Run commit skill tests only
make test-commit

# Or directly with pytest
pytest skills/commit/tests/test_pre_commit.py -v
```

### Test Help

```bash
make test-help
```

Shows available test targets and usage information.

## Testing Individual Skills

Each skill has its own test suite in `skills/<skill>/tests/`:

```bash
# List available test files
find skills -name "*.bats" -path "*/tests/*"

# Run a specific test file
bats skills/<skill>/tests/<test-name>.bats
```

## Understanding Test Output

Bats provides clear output for each test:

```
$ make test-commit
Running commit skill tests...
1..10
ok 1 passes when GPG signing is configured
ok 2 creates skill branch when on main with skills/ changes
...
```

- `ok` = Test passed
- `not ok` = Test failed (with detailed error message)

## Writing New Tests

When adding a new skill, include tests in `skills/<skill>/tests/`:

1. Create `skills/<skill>/tests/test_<name>.py`
2. Follow the existing pattern in `skills/commit/tests/test_pre_commit.py`
3. Use pytest fixtures for test isolation
4. Run `make test` to verify

### Test Best Practices

- Each test should be independent and isolated
- Use pytest's `tmp_path` fixture for temporary directories
- Test both success and failure scenarios

## Local Git Configuration

Ensure GPG signing is configured for commits:

```bash
git config user.email "your@email.com"
git config user.signingkey "YOUR_KEY_ID"
git config commit.gpgsign true
```

## Troubleshooting

### pytest not found

```bash
# Check if pytest is installed
pip show pytest

# If not found, install it:
pip install pytest
```

### Tests failing due to GPG

Tests create isolated git repositories. GPG signing is disabled in tests, but if you see GPG errors:

```bash
# Check your GPG setup
gpg --list-secret-keys

# Ensure git can find your key
git config --global user.signingkey
```

## Continuous Integration

Tests run automatically on:
- Every push to `main` or `master`
- Every pull request to `main` or `master`

See `.github/workflows/test.yml` for the CI configuration.

## Contributing

1. Write tests for new skills
2. Run `make test` locally before pushing
3. Ensure all tests pass
4. Ship changes using the ship skill or manual PR workflow
