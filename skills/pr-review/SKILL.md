---
name: pr-review
description: Reviews a PR to verify it does what the summary claims and has no security vulnerabilities
---

# PR Review Skill

This skill performs a thorough review of a pull request to verify its quality and security.

## When to Use

- User asks to review a PR
- User asks to check a pull request
- User wants to verify PR quality before merging

## Prerequisites

- GitHub CLI (`gh`) must be installed and authenticated
- Must be run from a repository with an open PR

## Instructions

### Step 1: Verify gh is Authenticated

Check if gh is authenticated:
```bash
gh auth status
```

If not authenticated, fail with error: "GitHub CLI is not authenticated. Run 'gh auth login' first."

### Step 2: Identify the PR

1. If user provided a PR number, use it:
   ```bash
   PR_NUMBER="123"
   ```

2. Otherwise, get the PR for the current branch:
   ```bash
   CURRENT_BRANCH=$(git branch --show-current)
   PR_NUMBER=$(gh pr list --head "$CURRENT_BRANCH" --json number --jq '.[0].number')
   ```

If no PR found, fail with error: "No PR found for current branch. Create a PR first."

### Step 3: Get PR Details

Get the PR title and body:
```bash
gh pr view $PR_NUMBER --json title,body,files,additions,deletions,commits
```

### Step 4: Verify PR Does What It Claims

1. Get the PR summary/description:
   ```bash
   PR_SUMMARY=$(gh pr view $PR_NUMBER --json body --jq '.body')
   ```

2. List the files changed:
   ```bash
   FILES=$(gh pr view $PR_NUMBER --json files --jq '.files[].path')
   ```

3. Review each file to verify it aligns with the summary:
   - Check commit messages match the summary
   - Verify all changes are intentional
   - Ensure no unrelated changes

4. Report findings:
   - If changes don't match summary, note: "Files changed do not match PR summary claims"
   - If all changes align, note: "Changes align with PR summary"

### Step 5: Check for Security Vulnerabilities

1. **Dependency vulnerabilities**:
   ```bash
   # Check for package-lock.json, Cargo.lock, Gemfile.lock, go.sum, etc.
   # If using npm:
   npm audit --audit-level=high --prefix /tmp/pr-review-$$
   ```

2. **Secret exposure**:
   Check that no secrets are committed:
   ```bash
   git diff ${BASE_BRANCH}...HEAD | grep -i -E "(password|secret|api_key|token|private)" || echo "No secrets found"
   ```

3. **Common vulnerability patterns**:
   ```bash
   # SQL injection patterns
   git diff ${BASE_BRANCH}...HEAD | grep -i -E "execute\s*\(|query\s*\(|\.sql" || true

   # Command injection
   git diff ${BASE_BRANCH}...HEAD | grep -i -E "exec\s*\(|system\s*\(|eval\s*\(" || true

   # Hardcoded credentials
   git diff ${BASE_BRANCH}...HEAD | grep -i -E "password\s*=\s*['\"]|api[_-]?key\s*=\s*['\"]" || true
   ```

4. **Dependency changes**:
   Check if package.json, requirements.txt, Cargo.toml, go.mod were changed:
   ```bash
   DEPENDENCY_FILES=$(git diff ${BASE_BRANCH}...HEAD --name-only | grep -E "(package\.json|requirements\.txt|Cargo\.toml|go\.mod|Gemfile|Podfile|pubspec\.yaml)" || true)
   ```
   If changed, note: "Review new dependencies carefully"

5. **Prompt injection patterns**:
   Check for prompt injection vulnerabilities in AI-related code:
   ```bash
   # Direct user input to LLM prompts without sanitization
   git diff ${BASE_BRANCH}...HEAD | grep -i -E "(prompt|system.?prompt|instructions).*\$|concat.*prompt|\+.*prompt" || true

   # System prompt modification
   git diff ${BASE_BRANCH}...HEAD | grep -i -E "system\s*[:=].*prompt|override\s+system" || true

   # User input in dangerous contexts (exec, eval, innerHTML)
   git diff ${BASE_BRANCH}...HEAD | grep -iE "\.innerHTML\s*=.*\$|dangerouslySetInnerHTML|exec\s*\(.*\$|eval\s*\(.*\$" || true
   ```
   If found, note: "Potential prompt injection risk - review user input handling"

6. **External URLs and resources**:
   Check for external resource fetching:
   ```bash
   # HTTP requests to external domains
   git diff ${BASE_BRANCH}...HEAD | grep -iE "(fetch\s*\(|axios\.|http\.get|http\.post|requests\.get|wget|curl)" || true

   # CDN and external resources in HTML/JS
   git diff ${BASE_BRANCH}...HEAD | grep -iE "cdn\.|\.cloudfront\.|\.cloudflare\.|https?://[^/]+(?!.*internal)" | grep -v "github.com" || true

   # External scripts and resources
   git diff ${BASE_BRANCH}...HEAD | grep -iE "<script\s+src=|<link\s+href=|<img\s+src=" || true
   ```
   If found, note: "External URLs detected - verify they are trusted and necessary"

   Also check for data being sent to external endpoints:
   ```bash
   git diff ${BASE_BRANCH}...HEAD | grep -iE "analytics|tracking|telemetry|sentry|datadog|newrelic" || true
   ```

### Step 6: Check for Common Issues

1. **No test coverage**:
   If code was added but no tests, warn: "No test files were modified"

2. **Documentation**:
   If public API changed without docs, warn: "Public API changed but no documentation updated"

3. **Breaking changes**:
   If version files changed, check for semver-major changes

### Step 7: Generate Review Summary

Compile findings into a review:
```bash
REVIEW_SUMMARY="## PR Review Summary

### Summary Alignment
[Findings from Step 4]

### Security Check
- Secrets: [PASS/FAIL]
- Vulnerabilities: [PASS/FAIL with details]
- Dependency changes: [Details if any]
- Prompt Injection: [PASS/FAIL with details]
- External URLs: [PASS/FAIL with details]

### Code Quality
- Tests: [PASS/FAIL]
- Documentation: [PASS/FAIL]
- Breaking changes: [Details if any]

### Recommendation
[Approve / Request Changes / Needs Security Review]
"
```

Output the review summary to the user.

### Step 8: Post Review to PR

Post the review summary as a PR review comment:
```bash
# Determine review event based on recommendation
if [ "$RECOMMENDATION" = "Approve" ]; then
    REVIEW_EVENT="--approve"
elif [ "$RECOMMENDATION" = "Request Changes" ]; then
    REVIEW_EVENT="--request-changes"
else
    REVIEW_EVENT="--comment"
fi

# Post the review to the PR
gh pr review $PR_NUMBER $REVIEW_EVENT --body "$REVIEW_SUMMARY"

echo "Review posted to PR #$PR_NUMBER"
```

## Error Handling

- If gh is not authenticated, fail with error
- If no PR found, fail with error
- If security scan fails, report but continue with review

## Important Notes

- This is a helper review, not a substitute for human review
- Always manually verify critical changes
- Check for business logic correctness separately
- Review test coverage thoroughly
