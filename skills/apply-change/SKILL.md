---
name: apply-change
description: Creates PR, reviews it, and merges if approved - otherwise asks for guidance
---

# Apply Change Skill

This skill automates the complete workflow: commit changes, push, create PR, review, and merge if approved.

## When to Use

- User asks to apply changes
- User wants to commit, push, create PR, review and merge in one go
- User wants automated change application with review gate

## Prerequisites

- Git must be installed
- GPG signing must be configured
- GitHub CLI (`gh`) must be installed and authenticated

## Instructions

### Step 1: Verify Prerequisites

Check all required tools are configured:
```bash
# Check GPG
git config user.email || fail "GPG signing not configured"
git config user.signingkey || fail "GPG signing not configured"

# Check GitHub CLI
gh auth status || fail "GitHub CLI not authenticated"
```

### Step 2: Commit Uncommitted Changes

Check if there are uncommitted changes and commit them:
```bash
if ! git diff --quiet || ! git diff --cached --quiet; then
    echo "Uncommitted changes detected. Committing..."

    # Get current branch
    CURRENT=$(git branch --show-current)

    # Create semantic branch if on main/master
    if [ "$CURRENT" = "main" ] || [ "$CURRENT" = "master" ] || [ -z "$CURRENT" ]; then
        TYPE="update"
        if git diff --name-only | grep -q "skills/"; then TYPE="skill"; fi
        FILENAME=$(git diff --name-only | head -1 | xargs basename 2>/dev/null | sed 's/\.[^.]*$//' | tr '[:upper:]' '[:lower:]' | tr ' ' '-')
        BRANCH_NAME="$TYPE/$(date +%Y%m%d)-${FILENAME:-update}"
        git checkout -b "$BRANCH_NAME"
    fi

    # Stage and commit
    git add -A
    git commit -S -m "Your commit message" || git commit -S
fi
```

### Step 3: Push Unpushed Commits

Check if there are commits not on remote and push:
```bash
CURRENT_BRANCH=$(git branch --show-current)
if [ "$CURRENT_BRANCH" != "main" ] && [ "$CURRENT_BRANCH" != "master" ]; then
    if git log origin/$CURRENT_BRANCH..HEAD --oneline 2>/dev/null | grep -q .; then
        echo "Unpushed commits detected. Pushing..."

        # Verify commits are signed
        UNSIGNED=$(git log $CURRENT_BRANCH --not --remotes --format=%G? 2>/dev/null | grep -v G | grep -v '^$' || true)
        if [ -n "$UNSIGNED" ]; then fail "There are unsigned commits"; fi

        git push -u origin $CURRENT_BRANCH
    fi
fi
```

### Step 4: Create PR

Create a pull request if one doesn't exist:
```bash
CURRENT_BRANCH=$(git branch --show-current)
BASE_BRANCH=$(git branch --list main master | head -1 | sed 's/.* //')
if [ -z "$BASE_BRANCH" ]; then BASE_BRANCH="main"; fi

# Check if PR already exists
EXISTING_PR=$(gh pr list --head "$CURRENT_BRANCH" --json number --jq '.[0].number' 2>/dev/null)
if [ -n "$EXISTING_PR" ]; then
    echo "PR already exists: #$EXISTING_PR"
    PR_NUMBER=$EXISTING_PR
else
    # Generate PR title and body
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
    gh pr create --title "$TITLE" --body "$BODY"
    PR_NUMBER=$(gh pr list --head "$CURRENT_BRANCH" --json number --jq '.[0].number')
fi
```

### Step 5: Review PR

Perform security and quality review:
```bash
# Get PR details
PR_DETAILS=$(gh pr view $PR_NUMBER --json title,body,files)

# Get diff for analysis
DIFF=$(git diff ${BASE_BRANCH}...HEAD)

# Run security checks
ISSUES=""

# Check for secrets
if echo "$DIFF" | grep -iE "(password|secret|api_key|token|private)" >/dev/null; then
    ISSUES="$ISSUES
- Potential secrets detected in changes"
fi

# Check for external URLs
if echo "$DIFF" | grep -iE "(fetch|axios|http\.|\.cdn\.|script.*src)" >/dev/null; then
    ISSUES="$ISSUES
- External URLs detected - verify they are trusted"
fi

# Check for prompt injection
if echo "$DIFF" | grep -iE "(prompt.*\$|system\s*[:=].*prompt|eval\(|exec\()" >/dev/null; then
    ISSUES="$ISSUES
- Potential prompt injection or unsafe execution patterns"
fi

# Check for dependency changes
if git diff ${BASE_BRANCH}...HEAD --name-only | grep -qE "(package\.json|requirements\.txt|Cargo\.toml|go\.mod)"; then
    ISSUES="$ISSUES
- Dependency files changed - review carefully"
fi
```

### Step 6: Present Review Results

Present findings to user:
```bash
if [ -n "$ISSUES" ]; then
    echo "## Review Findings

The following issues were detected:
$ISSUES

Would you like to:
1. Merge anyway
2. Cancel and fix issues
3. View the full diff"
    # Ask user for guidance
else
    echo "## Review Complete

All checks passed:
- No secrets detected
- No external URLs found
- No prompt injection risks
- No suspicious patterns

Ready to merge with squash."
fi
```

### Step 7: Merge (if approved)

If user approves, merge with squash:
```bash
# Get user approval
read -p "Proceed with squash merge? (yes/no): " CONFIRM
if [ "$CONFIRM" = "yes" ]; then
    gh pr merge $PR_NUMBER --squash --delete-branch
    echo "Changes merged successfully!"
else
    echo "Merge cancelled."
fi
```

## Error Handling

- If GPG not configured, fail with error
- If gh not authenticated, fail with error
- If PR review finds issues, ask user before proceeding
- If merge fails, display error and suggest manual resolution

## Important Notes

- This skill acts as a gatekeeper - it won't auto-merge if issues found
- User is always asked for confirmation before merge when issues detected
- All commits must be GPG signed
- Squash merge is the only merge method used
