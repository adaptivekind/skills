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
   gh api repos/$OWNER/$NAME/protection/main 2>/dev/null || echo "NO_PROTECTION"
   ```

2. **Check required status checks**:
   ```bash
   gh api repos/$OWNER/$NAME/protection/main/required_status_checks 2>/dev/null || true
   ```

3. **Check require PR reviews**:
   ```bash
   gh api repos/$OWNER/$NAME/protection/main/required_pull_request_reviews 2>/dev/null || true
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
REPORT="## Repository Healthcheck

### Branch Protection
- Main branch protected: [YES/NO]
- Require PR reviews: [YES/NO]
- Require status checks: [YES/NO]
- Require up-to-date branches: [YES/NO]
- Require signed commits: [YES/NO]
- Allow force push: [YES/NO]
- Allow branch deletion: [YES/NO]

### Merge Settings
- Squash merge allowed: [YES/NO]
- Rebase merge allowed: [YES/NO]
- Merge commit allowed: [YES/NO]

### Issues Found
[List any issues]

### Recommendation
[If issues found, ask user whether to apply fixes]
"
```

### Step 7: Report and Offer Fixes

If issues found, present the report to the user and ask:

> The following issues were found:
> - [List issues]
>
> Would you like me to apply these fixes? (yes/no)

If user says yes, proceed to Step 8.

### Step 8: Apply Fixes (if requested)

1. **Enable branch protection**:
   ```bash
   gh api -X PUT repos/$OWNER/$NAME/protection/main \
     -f required_status_checks='null' \
     -f enforce_admins=true \
     -f require_up_to_date_branches=true \
     -f require_signed_commits=true \
     -f required_pull_request_reviews='{"dismiss_stale_reviews":true,"require_code_owner_reviews":true}' \
     -f restrictions='null' \
     -f allow_force_pushes=false \
     -f allow_deletions=false
   ```

2. **Set default merge method** (note: GitHub doesn't allow setting default via API, user must set in UI):
   ```bash
   echo "Note: Set default merge method to 'Squash' in GitHub repository settings > General > Merge pull request"
   ```

3. **Confirm changes**:
   ```bash
   echo "Branch protection applied. Please verify in GitHub settings."
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
