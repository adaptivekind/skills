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

### Step 6: Determine High Confidence

Determine if the change is safe to auto-merge:
```bash
# High confidence = no issues found
HIGH_CONFIDENCE=false
if [ -z "$ISSUES" ]; then
    HIGH_CONFIDENCE=true
fi

# Present findings
if [ "$HIGH_CONFIDENCE" = true ]; then
    echo "## Review Complete

All checks passed:
- No secrets detected
- No external URLs found
- No prompt injection risks
- No suspicious patterns

High confidence - proceeding with merge."
else
    echo "## Review Findings

The following issues were detected:
$ISSUES

Asking user for guidance..."
fi
```

### Step 7: Merge (if high confidence)

If high confidence, auto-merge without user confirmation. Otherwise, ask user:
```bash
if [ "$HIGH_CONFIDENCE" = true ]; then
    # Auto-merge with squash
    gh pr merge $PR_NUMBER --squash --delete-branch
    
    # Checkout main and pull to sync
    MAIN_BRANCH=$(git branch --list main master | head -1 | sed 's/.* //')
    if [ -z "$MAIN_BRANCH" ]; then MAIN_BRANCH="main"; fi
    
    echo "Switching to $MAIN_BRANCH and pulling latest..."
    git checkout $MAIN_BRANCH
    git pull origin $MAIN_BRANCH
    
    echo "Changes applied successfully!"
else
    # Ask user for guidance when issues detected
    echo "Would you like to:
1. Merge anyway
2. Cancel and fix issues
3. View the full diff"
    read -p "Enter your choice: " USER_CHOICE
    
    case "$USER_CHOICE" in
        1)
            gh pr merge $PR_NUMBER --squash --delete-branch
            MAIN_BRANCH=$(git branch --list main master | head -1 | sed 's/.* //')
            if [ -z "$MAIN_BRANCH" ]; then MAIN_BRANCH="main"; fi
            git checkout $MAIN_BRANCH
            git pull origin $MAIN_BRANCH
            echo "Changes merged successfully!"
            ;;
        2)
            echo "Merge cancelled. Please fix the issues and try again."
            ;;
        3)
            git diff ${BASE_BRANCH}...HEAD
            echo "View the diff above and run the skill again with your decision."
            ;;
        *)
            echo "Invalid choice. Merge cancelled."
            ;;
    esac
fi
```

## Error Handling

- If GPG not configured, fail with error
- If gh not authenticated, fail with error
- If PR review finds issues, ask user before proceeding
- If merge fails, display error and suggest manual resolution
- If checkout/pull fails after merge, warn but don't fail

## Important Notes

- This skill auto-merges when there are no issues (high confidence)
- User is only asked for confirmation when issues are detected
- After successful merge, main branch is checked out and pulled
- All commits must be GPG signed
- Squash merge is the only merge method used
