---
name: commit
description: Creates a signed commit in the local repository. If on main or master branch, creates a new branch first. Fails if GPG signing is not configured.
---

# Commit Skill

This skill creates a signed commit with the current changes in the repository.

## When to Use

- User asks to commit changes
- User asks to create a commit
- User wants to save changes with a commit

## Prerequisites

- Git must be installed
- GPG signing must be configured (user.email must be set and gpg.key configured)
- There must be changes to commit (unstaged or staged)

## Instructions

### Step 1: Run Pre-Commit Script

Run the pre-commit script to verify GPG signing and handle branch creation:

```bash
./scripts/pre-commit.sh [optional_branch_prefix]
```

This script will:
1. Verify GPG signing is configured
2. Check current branch
3. Create semantic branch if on main/master
4. Check for changes to commit

If the script exits with an error, fail with the error message.

### Step 2: Stage All Changes

Stage all changes:

```bash
git add -A
```

### Step 3: Create Signed Commit

**Option A: Let git open editor**
```bash
git commit -S
```

**Option B: Use message from user or default**
If the user provided a commit message, use:
```bash
git commit -S -m "Your commit message here"
```

If no message provided, use a default descriptive message like "Update changes" or similar appropriate message based on the changes.

### Step 4: Verify Commit is Signed

Verify the commit was created and is signed:
```bash
git log -1 --show-signature
```

If the commit is not signed, fail with error: "Commit was not signed properly"

## Error Handling

- If GPG signing fails, fail with error: "GPG signing failed. Check your GPG configuration."
- If there are no changes to commit, inform the user and ask what changes they want to commit
- If git command fails, display the error message and fail

## Important Notes

- Always use `-S` flag with git commit to enable GPG signing
- The commit MUST be signed - do not proceed if signing fails
- This skill works with local repositories only
- See `scripts/pre-commit.sh` for the deterministic pre-commit logic

## Testing

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
