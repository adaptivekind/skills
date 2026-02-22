---
name: push
description: Pushes commits to remote if branch is not main and all commits are GPG signed
---

# Push Skill

This skill pushes commits to the remote repository with validation checks.

## When to Use

- User asks to push changes
- User asks to push to remote
- User wants to upload commits

## Prerequisites

- Git must be installed
- Remote repository must be configured
- There must be commits to push

## Instructions

### Step 1: Verify GPG Signing is Configured

Run the following command to verify GPG signing is configured:

```bash
git config user.email
git config user.signingkey
```

If either command returns empty, fail with error: "GPG signing is not configured. Please set git config user.email and git config user.signingkey"

### Step 2: Check Current Branch

Get the current branch name:
```bash
CURRENT_BRANCH=$(git branch --show-current)
```

If on main or master, fail with error: "Refusing to push to main/master branch. Create a feature branch or use 'git push --force' if necessary."

### Step 3: Verify All Commits are Signed

Check that all commits on the current branch are GPG signed:

```bash
UNSIGNED=$(git log ${CURRENT_BRANCH} --not --remotes --format=%G? | grep -v G | grep -v '^$')
```

If there are unsigned commits, fail with error: "There are unsigned commits. All commits must be signed to push."

### Step 4: Check for Changes to Push

Verify there are commits to push:
```bash
git diff HEAD --quiet
```

If working tree is clean with no commits to push, fail with error: "No commits to push."

### Step 5: Push to Remote

Push the current branch to remote:
```bash
git push -u origin $CURRENT_BRANCH
```

If push fails, display the error and fail.

### Step 6: Verify Push Success

Confirm the push was successful:
```bash
git status
```

## Error Handling

- If GPG signing is not configured, fail with error
- If on main/master branch, refuse to push
- If there are unsigned commits, fail with error
- If push fails, display the error and fail

## Important Notes

- This skill enforces GPG signing on all commits
- Blocks pushes to main/master branches
- Requires remote to be configured
