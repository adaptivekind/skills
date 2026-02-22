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

### Step 1: Verify GPG Signing is Configured

Run the following command to verify GPG signing is configured:

```bash
git config user.email
git config user.signingkey
```

If either command returns empty, fail with error: "GPG signing is not configured. Please set git config user.email and git config user.signingkey"

### Step 2: Check Current Branch

Determine the current branch name:

```bash
CURRENT_BRANCH=$(git branch --show-current)
```

If in detached HEAD state (empty result), use the current HEAD ref:
```bash
if [ -z "$CURRENT_BRANCH" ]; then
    CURRENT_BRANCH=$(git rev-parse HEAD)
fi
```

### Step 3: Handle Branch Creation (if on main or master)

If the current branch is `main` or `master`, or if in detached HEAD state:

1. First, check if there are any commits in the repository:
   ```bash
   if git rev-parse --verify HEAD >/dev/null 2>&1; then
       SHA=$(git rev-parse --short HEAD)
   else
       SHA="initial"
   fi
   ```

2. Generate a new branch name using the pattern `commit/<timestamp>-<short-sha>`:
   ```bash
   BRANCH_NAME="commit/$(date +%Y%m%d%H%M%S)-$SHA"
   ```

3. Create and switch to the new branch:
   ```bash
   git checkout -b "$BRANCH_NAME"
   ```

### Step 4: Check for Changes and Stage

1. First, determine if there are any changes to commit:
   ```bash
   git diff --quiet && git diff --cached --quiet
   ```
   If this succeeds (exit code 0), there are no changes to commit. Fail with appropriate message.

2. Stage all changes:
   ```bash
   git add -A
   ```

### Step 5: Create Signed Commit

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

### Step 6: Verify Commit is Signed

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
