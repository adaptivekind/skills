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

### Step 3: Check Branch Protection Rules

Check if main branch has protection rules:

1. **Check if branch protection exists**:
   ```bash
   PROTECTION=$(gh api repos/$OWNER/$NAME/protection/main 2>/dev/null || echo "NO_PROTECTION")
   ```

2. **Check required status checks**:
   ```bash
   STATUS_CHECKS=$(gh api repos/$OWNER/$NAME/protection/main/required_status_checks 2>/dev/null || echo "NONE")
   ```

3. **Check require PR reviews**:
   ```bash
   PR_REVIEWS=$(gh api repos/$OWNER/$NAME/protection/main/required_pull_request_reviews 2>/dev/null || echo "NONE")
   ```

4. **Verify status checks configuration**:
   ```bash
   # Check if status checks are required
   if [ "$STATUS_CHECKS" = "NONE" ] || [ -z "$(echo $STATUS_CHECKS | jq -r '.checks[]' 2>/dev/null)" ]; then
       echo "WARNING: No required status checks configured!"
   fi
   
   # Check if branches must be up to date
   REQUIRE_BRANCHES_UP_TO_DATE=$(echo "$PROTECTION" | jq -r '.required_status_checks.strict' 2>/dev/null)
   if [ "$REQUIRE_BRANCHES_UP_TO_DATE" != "true" ]; then
       echo "WARNING: Branches must be up to date before merging is DISABLED!"
   fi
   ```

### Step 4: Check Push and Force Push Settings

From the protection settings, verify:
- `allow_force_pushes` is false/disabled
- `allow_deletions` is false/disabled
- `require_branches_up_to_date` is enabled (true)
- `require_signed_commits` is enabled (true)
- `dismiss_stale_reviews` is enabled

### Step 5: Check Merge Settings

Get the repository merge settings:
```bash
gh api repos/$OWNER/$NAME --jq '.merge_commit_title,.allow_merge_commit,.allow_squash_merge,.allow_rebase_merge'
```

Check:
- `allow_squash_merge` should be true
- Check if squash merge is preferred (this is typically set via GitHub UI, not API)

### Step 6: Generate Healthcheck Report

Compile findings:
```bash
# Check if status checks are configured
HAS_STATUS_CHECKS=false
if [ "$STATUS_CHECKS" != "NONE" ] && [ -n "$(echo $STATUS_CHECKS | jq -r '.checks[]' 2>/dev/null)" ]; then
    HAS_STATUS_CHECKS=true
fi

# Check branch up to date requirement
REQUIRE_BRANCHES_UP_TO_DATE=$(echo "$PROTECTION" | jq -r '.required_status_checks.strict' 2>/dev/null)

# Collect issues
ISSUES=""
if [ "$PROTECTION" = "NO_PROTECTION" ]; then
    ISSUES="$ISSUES
- Main branch has NO protection rules"
fi

if [ "$HAS_STATUS_CHECKS" != "true" ]; then
    ISSUES="$ISSUES
- No required status checks configured (CI tests can be bypassed!)"
fi

if [ "$REQUIRE_BRANCHES_UP_TO_DATE" != "true" ]; then
    ISSUES="$ISSUES
- Branches do NOT need to be up to date before merging"
fi

REPORT="## Repository Healthcheck

### Branch Protection
- Main branch protected: $([ "$PROTECTION" = "NO_PROTECTION" ] && echo "NO" || echo "YES")
- Require PR reviews: $([ "$PR_REVIEWS" = "NONE" ] && echo "NO" || echo "YES")
- Require status checks: $HAS_STATUS_CHECKS
- Require up-to-date branches: $([ "$REQUIRE_BRANCHES_UP_TO_DATE" = "true" ] && echo "YES" || echo "NO")
- Require signed commits: $(echo "$PROTECTION" | jq -r '.require_signed_commits' 2>/dev/null || echo "NO")
- Allow force push: $(echo "$PROTECTION" | jq -r '.allow_force_pushes.enabled' 2>/dev/null || echo "N/A")
- Allow branch deletion: $(echo "$PROTECTION" | jq -r '.allow_deletions' 2>/dev/null || echo "N/A")

### Merge Settings
- Squash merge allowed: $(echo "$MERGE_SETTINGS" | jq -r '.[2]')
- Rebase merge allowed: $(echo "$MERGE_SETTINGS" | jq -r '.[3]')
- Merge commit allowed: $(echo "$MERGE_SETTINGS" | jq -r '.[1]')

### Issues Found
$(if [ -z "$ISSUES" ]; then echo "None"; else echo "$ISSUES"; fi)

### Recommendation
$(if [ -z "$ISSUES" ]; then echo "Repository is properly configured!"; else echo "Issues found - fix recommended"; fi)
"
```

### Step 7: Report and Offer Fixes

First, check for critical issues that must be fixed:
```bash
# Critical issues that MUST be fixed
CRITICAL_ISSUES=""
if [ "$PROTECTION" = "NO_PROTECTION" ]; then
    CRITICAL_ISSUES="$CRITICAL_ISSUES
- Main branch has NO protection rules"
fi

if [ "$HAS_STATUS_CHECKS" != "true" ]; then
    CRITICAL_ISSUES="$CRITICAL_ISSUES
- CRITICAL: No required status checks! This allows bypassing CI tests!"
fi

# If there are critical issues, fail the healthcheck
if [ -n "$CRITICAL_ISSUES" ]; then
    echo "=========================================="
    echo "   REPOSITORY HEALTHCHECK FAILED"
    echo "=========================================="
    echo ""
    echo "Critical issues found:"
    echo "$CRITICAL_ISSUES"
    echo ""
    echo "These issues allow unsafe merges and must be fixed!"
    echo "Would you like me to apply fixes now? (yes/no)"
    read -p "> " FIX_CHOICE
    
    if [ "$FIX_CHOICE" = "yes" ]; then
        # Proceed to Step 8
    else
        echo "Healthcheck failed. Please fix the issues manually."
        exit 1
    fi
fi
```

If non-critical issues found, present the report to the user and ask:

> The following issues were found:
> - [List issues]
>
> Would you like me to apply these fixes? (yes/no)

If user says yes, proceed to Step 8.

### Step 8: Apply Fixes (if requested)

1. **Check existing branch protection settings**:
   ```bash
   # Get current protection settings to preserve existing configurations
   CURRENT_PROTECTION=$(gh api repos/$OWNER/$NAME/protection/main 2>/dev/null || echo "NONE")
   
   # Check if status checks are already configured
   if echo "$CURRENT_PROTECTION" | grep -q "required_status_checks"; then
       # Preserve existing status checks
       REQUIRED_STATUS_CHECKS=$(echo "$CURRENT_PROTECTION" | jq -r '.required_status_checks // null')
   else
       # No existing status checks
       REQUIRED_STATUS_CHECKS="null"
   fi
   
   # Check if restrictions are already configured
   if echo "$CURRENT_PROTECTION" | grep -q "restrictions"; then
       # Preserve existing restrictions
       RESTRICTIONS=$(echo "$CURRENT_PROTECTION" | jq -r '.restrictions // null')
   else
       # No existing restrictions
       RESTRICTIONS="null"
   fi
   ```

2. **Enable branch protection** (preserving existing settings):
   ```bash
   gh api -X PUT repos/$OWNER/$NAME/protection/main \
     -f required_status_checks="$REQUIRED_STATUS_CHECKS" \
     -f enforce_admins=true \
     -f require_up_to_date_branches=true \
     -f require_signed_commits=true \
     -f required_pull_request_reviews='{"dismiss_stale_reviews":true,"require_code_owner_reviews":true}' \
     -f restrictions="$RESTRICTIONS" \
     -f allow_force_pushes=false \
     -f allow_deletions=false
   ```

3. **Confirm changes**:
   ```bash
   echo "Branch protection applied with:"
   echo "  - Required up-to-date branches: ENABLED"
   echo "  - Required signed commits: ENABLED"
   echo "  - Existing status checks: $(if [ "$REQUIRED_STATUS_CHECKS" != "null" ]; then echo "PRESERVED"; else echo "NONE"; fi)"
   echo "  - Existing restrictions: $(if [ "$RESTRICTIONS" != "null" ]; then echo "PRESERVED"; else echo "NONE"; fi)"
   echo ""
   echo "Please verify in GitHub settings."
   ```

4. **Set default merge method** (note: GitHub doesn't allow setting default via API, user must set in UI):
   ```bash
   echo "Note: Set default merge method to 'Squash' in GitHub repository settings > General > Merge pull request"

2. **Set default merge method** (note: GitHub doesn't allow setting default via API, user must set in UI):
   ```bash
   echo "Note: Set default merge method to 'Squash' in GitHub repository settings > General > Merge pull request"
   ```

## Error Handling

- If gh is not authenticated, fail with error
- If repository not found, fail with error
- If API call fails, report the error and suggest manual verification

## Important Notes

- This skill checks main branch protection
- Requires admin/repository permissions to modify settings
- Some settings can only be changed via GitHub UI
- Branch protection rules affect all collaborators
