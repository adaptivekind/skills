# Development Guide

This guide explains how to set up your local development environment and run tests for the skills repository.

## Prerequisites

- Git (with GPG signing configured)
- GitHub CLI (`gh`)
- Make
- bats-core (for running tests)

## Installing Dependencies

### macOS (using Homebrew)

```bash
# Install bats-core
brew install bats-core

# Verify installation
bats --version
```

### Linux

```bash
# Install bats-core from source
git clone https://github.com/bats-core/bats-core.git
cd bats-core
sudo ./install.sh /usr/local

# Verify installation
bats --version
```

### Alternative: Install via npm

```bash
npm install -g bats
```

## Running Tests Locally

### Run All Tests

```bash
make test
```

This will find and run all `.bats` test files in the `skills/` directory.

### Run Specific Skill Tests

```bash
# Run commit skill tests only
make test-commit

# Or directly with bats
bats skills/commit/tests/pre-commit.bats
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

1. Create `skills/<skill>/tests/<test-name>.bats`
2. Follow the existing pattern in `skills/commit/tests/pre-commit.bats`
3. Use `setup()` and `teardown()` for test isolation
4. Run `make test` to verify

### Test Best Practices

- Each test should be independent and isolated
- Use temporary directories for git operations
- Clean up resources in `teardown()`
- Test both success and failure scenarios

## Local Git Configuration

Ensure GPG signing is configured for commits:

```bash
git config user.email "your@email.com"
git config user.signingkey "YOUR_KEY_ID"
git config commit.gpgsign true
```

## Troubleshooting

### Bats not found

```bash
# Check if bats is in your PATH
which bats

# If not found, install it:
brew install bats-core  # macOS
# or
sudo ./install.sh /usr/local  # Linux from source
```

### Tests failing due to GPG

Tests create isolated git repositories. GPG signing is disabled in tests, but if you see GPG errors:

```bash
# Check your GPG setup
gpg --list-secret-keys

# Ensure git can find your key
git config --global user.signingkey
```

### Permission denied errors

If you get permission errors installing bats:

```bash
# On Linux, use sudo for system-wide install
sudo ./install.sh /usr/local

# Or install to a local directory
./install.sh "$HOME/.local"
export PATH="$HOME/.local/bin:$PATH"
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
