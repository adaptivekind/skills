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

### Step 2: Get Current Branch and Base Branch

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

### Step 3: Check for Remote

Verify remote is configured:
```bash
git remote get-url origin
```

If no remote, fail with error: "No remote configured. Please add a remote with 'git remote add origin <url>'"

### Step 4: Get Commit Summary

Get the commits that will be in the PR:
```bash
COMMITS_SUMMARY=$(git log ${BASE_BRANCH}..HEAD --oneline)
```

If no commits, fail with error: "No commits to create a PR. Commit your changes first."

### Step 5: Create the PR

1. If user provided a title and description, use them:
   ```bash
   gh pr create --title "Your Title" --body "Your description"
   ```

2. If no title provided, use a default:
   - Get the first commit message as title
   - Get the diff stat as description

   ```bash
   TITLE=$(git log -1 --format=%s)
   BODY=$(git diff ${BASE_BRANCH}...HEAD --stat | head -20)
   gh pr create --title "$TITLE" --body "$BODY"
   ```

### Step 6: Confirm PR Creation

Verify the PR was created:
```bash
gh pr view --web
```

## Error Handling

- If gh is not authenticated, fail with error
- If no commits to PR, fail with error
- If PR creation fails, display the error and fail

## Important Notes

- This skill uses the GitHub CLI (`gh`)
- Requires proper GitHub authentication
- Only works with GitHub repositories
