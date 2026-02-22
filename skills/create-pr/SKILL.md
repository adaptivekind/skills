---
name: create-pr
description: Creates a GitHub pull request using gh CLI with title and description
---

# Create PR Skill

This skill creates a GitHub pull request for the current branch.

## When to Use

- User asks to create a PR
- User asks to open a pull request
- User wants to submit changes for review
- User asks to update PR title or description

## Prerequisites

- GitHub CLI (`gh`) must be installed and authenticated
- Current branch must have commits not in main/master
- Remote repository must be configured

## Instructions

### Step 1: Verify gh is Authenticated

Check if gh is authenticated:
```bash
gh auth status
```

If not authenticated, fail with error: "GitHub CLI is not authenticated. Run 'gh auth login' first."

### Step 2: Commit Uncommitted Changes

Check if there are uncommitted changes:
```bash
if ! git diff --quiet || ! git diff --cached --quiet; then
    echo "Uncommitted changes detected. Running commit skill..."

    # Commit skill steps:
    # 1. Verify GPG signing
    git config user.email || fail "GPG signing not configured"
    git config user.signingkey || fail "GPG signing not configured"

    # 2. Check current branch
    CURRENT=$(git branch --show-current)
    if [ "$CURRENT" = "main" ] || [ "$CURRENT" = "master" ] || [ -z "$CURRENT" ]; then
        # Create semantic branch name
        TYPE="update"
        if git diff --name-only | grep -q "skills/"; then TYPE="skill"; fi
        BRANCH_NAME="$TYPE/$(date +%Y%m%d)-$(git diff --name-only | head -1 | xargs basename | sed 's/\.[^.]*$//' | tr '[:upper:]' '[:lower:]' | tr ' ' '-')"
        git checkout -b "$BRANCH_NAME"
    fi

    # 3. Stage and commit
    git add -A
    git commit -S -m "Your commit message" || git commit -S  # Use message or open editor
fi
```

### Step 3: Push Unpushed Commits

Check if there are commits not on remote:
```bash
CURRENT_BRANCH=$(git branch --show-current)
if [ "$CURRENT_BRANCH" != "main" ] && [ "$CURRENT_BRANCH" != "master" ]; then
    if git log origin/$CURRENT_BRANCH..HEAD --oneline 2>/dev/null | grep -q .; then
        echo "Unpushed commits detected. Running push skill..."

        # Push skill steps:
        # 1. Verify GPG signing
        git config user.signingkey || fail "GPG signing not configured"

        # 2. Verify all commits are signed
        UNSIGNED=$(git log $CURRENT_BRANCH --not --remotes --format=%G? | grep -v G | grep -v '^$')
        if [ -n "$UNSIGNED" ]; then fail "There are unsigned commits"; fi

        # 3. Push
        git push -u origin $CURRENT_BRANCH
    fi
fi
```

### Step 4: Get Current Branch and Base Branch

Get the current branch:
```bash
CURRENT_BRANCH=$(git branch --show-current)
```

Determine the base branch (main or master):
```bash
BASE_BRANCH=$(git branch --list main master | head -1 | sed 's/.* //')
if [ -z "$BASE_BRANCH" ]; then
    BASE_BRANCH="main"
fi
```

### Step 5: Check for Remote

Verify remote is configured:
```bash
git remote get-url origin
```

If no remote, fail with error: "No remote configured. Please add a remote with 'git remote add origin <url>'"

### Step 6: Get Commit Summary

Get the commits that will be in the PR:
```bash
COMMITS_SUMMARY=$(git log ${BASE_BRANCH}..HEAD --oneline)
```

If no commits, fail with error: "No commits to create a PR. Commit your changes first."

### Step 7: Create the PR

1. If user provided a title and description, use them:
   ```bash
   gh pr create --title "Your Title" --body "Your description"
   ```

2. If no title provided, generate a PR summary:

   **Title**: First commit message
   ```bash
   TITLE=$(git log -1 --format=%s)
   ```

   **Description**: Build a comprehensive PR summary:
   ```bash
   # Get commit messages
   COMMITS=$(git log ${BASE_BRANCH}..HEAD --format="- %s (%h)" | head -10)

   # Get file changes
   FILE_CHANGES=$(git diff ${BASE_BRANCH}...HEAD --stat)

   # Build body
   BODY="## Summary
   $COMMITS

   ## Changes
   \`\`\`
   $FILE_CHANGES
   \`\`\`
   "

   gh pr create --title "$TITLE" --body "$BODY"
   ```

   The summary includes:
   - List of commits with short hashes
   - File change statistics (additions/deletions)

### Step 6: Confirm PR Creation

Verify the PR was created:
```bash
gh pr view --web
```

### Step 7: Update PR (Optional)

If user asks to update an existing PR:

1. First, find the PR number for the current branch:
   ```bash
   PR_NUMBER=$(gh pr list --head "$CURRENT_BRANCH" --json number --jq '.[0].number')
   ```

2. If user provided a new title:
   ```bash
   gh pr edit $PR_NUMBER --title "New Title"
   ```

3. If user provided a new body/description:
   ```bash
   gh pr edit $PR_NUMBER --body "New description"
   ```

4. If user wants to regenerate the summary:
   ```bash
   # Regenerate summary (same as Step 5)
   TITLE=$(git log -1 --format=%s)
   COMMITS=$(git log ${BASE_BRANCH}..HEAD --format="- %s (%h)" | head -10)
   FILE_CHANGES=$(git diff ${BASE_BRANCH}...HEAD --stat)
   BODY="## Summary
   $COMMITS

   ## Changes
   \`\`\`
   $FILE_CHANGES
   \`\`\`
   "
   gh pr edit $PR_NUMBER --title "$TITLE" --body "$BODY"
   ```

## Error Handling

- If gh is not authenticated, fail with error
- If no commits to PR, fail with error
- If PR creation fails, display the error and fail

## Important Notes

- This skill uses the GitHub CLI (`gh`)
- Requires proper GitHub authentication
- Only works with GitHub repositories
