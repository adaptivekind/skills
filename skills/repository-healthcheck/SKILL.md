---
name: repository-healthcheck
description: Checks repository is correctly configured - branch protection, PR requirements, and merge settings
---

# Repository Healthcheck Skill

This skill verifies that a repository is correctly configured for safe collaboration.

## When to Use

- User asks to check repository health
- User asks to verify repository settings
- User wants to ensure branch protection is enabled

## Prerequisites

- GitHub CLI (`gh`) must be installed and authenticated
- Must be run from a git repository with a remote

## Instructions

### Step 1: Verify gh is Authenticated

Check if gh is authenticated:
```bash
gh auth status
```

If not authenticated, fail with error: "GitHub CLI is not authenticated. Run 'gh auth login' first."

### Step 2: Get Repository Information

Get the current repository:
```bash
REPO=$(git remote get-url origin | sed 's|.*github.com/||' | sed 's|\.git$||')
OWNER=$(echo $REPO | cut -d'/' -f1)
NAME=$(echo $REPO | cut -d'/' -f2)
```

### Step 3: Check Branch Protection

Check branch protection status:
```bash
# Get branch info
BRANCH_INFO=$(gh api repos/$OWNER/$NAME/branches/main 2>/dev/null)

# Check if protected
PROTECTED=$(echo "$BRANCH_INFO" | jq -r '.protected')
if [ "$PROTECTED" = "true" ]; then
    PROTECTION=$(gh api repos/$OWNER/$NAME/branches/main/protection 2>/dev/null || echo "NO_PROTECTION")
else
    PROTECTION="NO_PROTECTION"
fi
```

### Step 4: Check Status Checks

Check if required status checks are configured:
```bash
if [ "$PROTECTION" != "NO_PROTECTION" ]; then
    STATUS_CHECKS=$(echo "$PROTECTION" | jq -r '.required_status_checks // null')
    HAS_STATUS_CHECKS=false
    if [ "$STATUS_CHECKS" != "null" ] && [ -n "$(echo $STATUS_CHECKS | jq -r '.checks[]' 2>/dev/null)" ]; then
        HAS_STATUS_CHECKS=true
    fi
    REQUIRE_BRANCHES_UP_TO_DATE=$(echo "$PROTECTION" | jq -r '.required_status_checks.strict' 2>/dev/null)
else
    HAS_STATUS_CHECKS=false
    REQUIRE_BRANCHES_UP_TO_DATE="false"
fi
```

### Step 5: Check PR Reviews

Check if PR reviews are required:
```bash
if [ "$PROTECTION" != "NO_PROTECTION" ]; then
    PR_REVIEWS=$(echo "$PROTECTION" | jq -r '.required_pull_request_reviews // null')
    HAS_PR_REVIEWS=true
    if [ "$PR_REVIEWS" = "null" ]; then
        HAS_PR_REVIEWS=false
    fi
    DISMISS_STALE=$(echo "$PROTECTION" | jq -r '.required_pull_request_reviews.dismiss_stale_reviews' 2>/dev/null)
    REQUIRE_CODE_OWNER=$(echo "$PROTECTION" | jq -r '.required_pull_request_reviews.require_code_owner_reviews' 2>/dev/null)
else
    HAS_PR_REVIEWS=false
    DISMISS_STALE="N/A"
    REQUIRE_CODE_OWNER="N/A"
fi
```

### Step 6: Check Push Settings

Check force push and deletion settings:
```bash
if [ "$PROTECTION" != "NO_PROTECTION" ]; then
    ALLOW_FORCE_PUSH=$(echo "$PROTECTION" | jq -r '.allow_force_pushes.enabled' 2>/dev/null || echo "null")
    ALLOW_DELETIONS=$(echo "$PROTECTION" | jq -r '.allow_deletions' 2>/dev/null || echo "null")
else
    ALLOW_FORCE_PUSH="N/A"
    ALLOW_DELETIONS="N/A"
fi
```

### Step 7: Check Merge Settings

Get the repository merge settings:
```bash
MERGE_SETTINGS=$(gh api repos/$OWNER/$NAME --jq '.allow_squash_merge,.allow_merge_commit,.allow_rebase_merge')
SQUASH_MERGE=$(echo "$MERGE_SETTINGS" | jq -r '.[0]')
MERGE_COMMIT=$(echo "$MERGE_SETTINGS" | jq -r '.[1]')
REBASE_MERGE=$(echo "$MERGE_SETTINGS" | jq -r '.[2]')
```

### Step 8: Generate and Display Report

Compile and display the healthcheck report:
```bash
echo "=========================================="
echo "   REPOSITORY HEALTHCHECK REPORT"
echo "=========================================="
echo ""

echo "### Branch Protection"
echo "- Main branch protected: $PROTECTED"
echo "- Require PR reviews: $HAS_PR_REVIEWS"
echo "  - Dismiss stale reviews: $DISMISS_STALE"
echo "  - Require code owner reviews: $REQUIRE_CODE_OWNER"
echo "- Require status checks: $HAS_STATUS_CHECKS"
echo "- Require up-to-date branches: $REQUIRE_BRANCHES_UP_TO_DATE"
echo "- Allow force push: $ALLOW_FORCE_PUSH"
echo "- Allow branch deletion: $ALLOW_DELETIONS"
echo ""

echo "### Merge Settings"
echo "- Squash merge allowed: $SQUASH_MERGE"
echo "- Merge commit allowed: $MERGE_COMMIT"
echo "- Rebase merge allowed: $REBASE_MERGE"
echo ""

# Determine issues
ISSUES=""
if [ "$PROTECTED" = "false" ]; then
    ISSUES="$ISSUES
- Main branch is NOT protected"
fi

if [ "$HAS_STATUS_CHECKS" != "true" ]; then
    ISSUES="$ISSUES
- No required status checks (CI can be bypassed!)"
fi

if [ "$REQUIRE_BRANCHES_UP_TO_DATE" != "true" ]; then
    ISSUES="$ISSUES
- Branches do NOT need to be up to date before merging"
fi

if [ "$ALLOW_DELETIONS" = "true" ]; then
    ISSUES="$ISSUES
- Branch deletion is ALLOWED"
fi

echo "### Issues Found"
if [ -z "$ISSUES" ]; then
    echo "None"
else
    echo "$ISSUES"
fi
echo ""

echo "### Recommendation"
if [ -z "$ISSUES" ]; then
    echo "Repository is properly configured!"
else
    echo "Issues found - please fix manually in GitHub settings"
fi
echo ""

# Exit with error if critical issues found
if [ "$PROTECTED" = "false" ] || [ "$HAS_STATUS_CHECKS" != "true" ]; then
    echo "=========================================="
    echo "   HEALTHCHECK FAILED"
    echo "=========================================="
    echo "Critical issues found. Please fix in GitHub:"
    echo "  Settings > Branches > Branch protection rules"
    exit 1
fi
```

## Error Handling

- If gh is not authenticated, fail with error
- If repository not found, fail with error
- If API call fails, report the error and suggest manual verification

## Important Notes

- This skill only reports on configuration - it does NOT apply fixes
- Fixes must be done manually in GitHub settings
- This skill checks main branch protection
- Branch protection rules affect all collaborators
