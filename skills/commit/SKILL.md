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

Create a commit with a message based on the changes being made. Analyze the staged files to generate an appropriate commit message:

```bash
# Analyze what changed and create appropriate message
CHANGED_FILES=$(git diff --cached --name-only)
ADDED_FILES=$(git diff --cached --name-only --diff-filter=A)
MODIFIED_FILES=$(git diff --cached --name-only --diff-filter=M)
DELETED_FILES=$(git diff --cached --name-only --diff-filter=D)

# Create commit message based on changes
if [ -n "$ADDED_FILES" ] && [ -z "$MODIFIED_FILES" ] && [ -z "$DELETED_FILES" ]; then
    # Only additions
    if echo "$ADDED_FILES" | grep -q "^skills/"; then
        COMMIT_MSG="Add $(echo "$ADDED_FILES" | head -1 | xargs basename)"
    elif echo "$ADDED_FILES" | grep -q "^\.github/workflows/"; then
        COMMIT_MSG="Add GitHub Actions workflow"
    elif echo "$ADDED_FILES" | grep -q "^docs/\|README\|DEVELOP\|HISTORY"; then
        COMMIT_MSG="Add documentation: $(echo "$ADDED_FILES" | head -1 | xargs basename)"
    else
        COMMIT_MSG="Add $(echo "$ADDED_FILES" | head -1 | xargs basename)"
    fi
elif [ -n "$MODIFIED_FILES" ] && [ -z "$ADDED_FILES" ] && [ -z "$DELETED_FILES" ]; then
    # Only modifications
    if echo "$MODIFIED_FILES" | grep -q "^skills/"; then
        SKILL_NAME=$(echo "$MODIFIED_FILES" | grep "^skills/" | head -1 | cut -d'/' -f2)
        COMMIT_MSG="Update $SKILL_NAME skill"
    elif echo "$MODIFIED_FILES" | grep -q "\.md$"; then
        COMMIT_MSG="Update documentation"
    elif echo "$MODIFIED_FILES" | grep -q "^\.github/"; then
        COMMIT_MSG="Update GitHub Actions configuration"
    else
        COMMIT_MSG="Update $(echo "$MODIFIED_FILES" | head -1 | xargs basename)"
    fi
elif [ -n "$DELETED_FILES" ] && [ -z "$ADDED_FILES" ] && [ -z "$MODIFIED_FILES" ]; then
    # Only deletions
    COMMIT_MSG="Remove $(echo "$DELETED_FILES" | head -1 | xargs basename)"
else
    # Mixed changes
    if echo "$CHANGED_FILES" | grep -q "^skills/"; then
        COMMIT_MSG="Update skills configuration and implementation"
    elif echo "$CHANGED_FILES" | grep -q "^\.github/"; then
        COMMIT_MSG="Update CI/CD and repository configuration"
    elif echo "$CHANGED_FILES" | grep -q "\.md$"; then
        COMMIT_MSG="Update documentation"
    else
        COMMIT_MSG="Update repository files"
    fi
fi

# Create the signed commit with the generated message
git commit -S -m "$COMMIT_MSG"
```

The commit message should be concise but descriptive, based on what files were changed and the nature of the changes.

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
