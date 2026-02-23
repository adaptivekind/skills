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

**IMPORTANT: This skill automatically posts the review to the PR in Step 7. You MUST execute Step 7 to post the review before considering the review complete.**

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

4. Capture findings in variable for review report:
   ```bash
   if [ "$CHANGES_ALIGN" = true ]; then
       SUMMARY_FINDINGS="Changes align with PR summary"
   else
       SUMMARY_FINDINGS="Files changed do not match PR summary claims"
   fi
   ```

### Step 5: Check for Security Vulnerabilities

Capture all security check results in variables for the review report:

1. **Dependency vulnerabilities**:
   ```bash
   # Check for package-lock.json, Cargo.lock, Gemfile.lock, go.sum, etc.
   # If using npm:
   npm audit --audit-level=high --prefix /tmp/pr-review-$$ || VULNERABILITIES_FOUND=true
   if [ "$VULNERABILITIES_FOUND" = true ]; then
       VULNERABILITIES_STATUS="FAIL - Dependency vulnerabilities found"
   else
       VULNERABILITIES_STATUS="PASS"
   fi
   ```

2. **Secret exposure**:
   Check that no secrets are committed:
   ```bash
   if git diff ${BASE_BRANCH}...HEAD | grep -i -E "(password|secret|api_key|token|private)" >/dev/null; then
       SECRETS_STATUS="FAIL - Potential secrets detected"
   else
       SECRETS_STATUS="PASS"
   fi
   ```

3. **Common vulnerability patterns**:
   ```bash
   VULNERABILITY_ISSUES=""

   # SQL injection patterns
   if git diff ${BASE_BRANCH}...HEAD | grep -i -E "execute\s*\(|query\s*\(|\.sql" >/dev/null; then
       VULNERABILITY_ISSUES="${VULNERABILITY_ISSUES}SQL injection patterns detected. "
   fi

   # Command injection
   if git diff ${BASE_BRANCH}...HEAD | grep -i -E "exec\s*\(|system\s*\(|eval\s*\(" >/dev/null; then
       VULNERABILITY_ISSUES="${VULNERABILITY_ISSUES}Command injection patterns detected. "
   fi

   # Hardcoded credentials
   if git diff ${BASE_BRANCH}...HEAD | grep -i -E "password\s*=\s*['\"]|api[_-]?key\s*=\s*['\"]" >/dev/null; then
       VULNERABILITY_ISSUES="${VULNERABILITY_ISSUES}Hardcoded credentials detected. "
   fi

   if [ -n "$VULNERABILITY_ISSUES" ]; then
       VULNERABILITIES_STATUS="FAIL - $VULNERABILITY_ISSUES"
   fi
   ```

4. **Dependency changes**:
   Check if package.json, requirements.txt, Cargo.toml, go.mod were changed:
   ```bash
   DEPENDENCY_FILES=$(git diff ${BASE_BRANCH}...HEAD --name-only | grep -E "(package\.json|requirements\.txt|Cargo\.toml|go\.mod|Gemfile|Podfile|pubspec\.yaml)" || true)
   if [ -n "$DEPENDENCY_FILES" ]; then
       DEPENDENCY_STATUS="WARNING - Dependency files changed: $DEPENDENCY_FILES"
   else
       DEPENDENCY_STATUS="PASS - No dependency changes"
   fi
   ```

5. **Prompt injection patterns**:
   Check for prompt injection vulnerabilities in AI-related code:
   ```bash
   PROMPT_INJECTION_ISSUES=""

   # Direct user input to LLM prompts without sanitization
   if git diff ${BASE_BRANCH}...HEAD | grep -i -E "(prompt|system.?prompt|instructions).*\$|concat.*prompt|\+.*prompt" >/dev/null; then
       PROMPT_INJECTION_ISSUES="${PROMPT_INJECTION_ISSUES}Potential prompt injection in user input handling. "
   fi

   # System prompt modification
   if git diff ${BASE_BRANCH}...HEAD | grep -i -E "system\s*[:=].*prompt|override\s+system" >/dev/null; then
       PROMPT_INJECTION_ISSUES="${PROMPT_INJECTION_ISSUES}System prompt modification detected. "
   fi

   # User input in dangerous contexts (exec, eval, innerHTML)
   if git diff ${BASE_BRANCH}...HEAD | grep -iE "\.innerHTML\s*=.*\$|dangerouslySetInnerHTML|exec\s*\(.*\$|eval\s*\(.*\$" >/dev/null; then
       PROMPT_INJECTION_ISSUES="${PROMPT_INJECTION_ISSUES}User input in dangerous execution context. "
   fi

   if [ -n "$PROMPT_INJECTION_ISSUES" ]; then
       PROMPT_INJECTION_STATUS="FAIL - $PROMPT_INJECTION_ISSUES"
   else
       PROMPT_INJECTION_STATUS="PASS"
   fi
   ```

6. **External URLs and resources**:
   Check for external resource fetching:
   ```bash
   EXTERNAL_URLS_FOUND=""

   # HTTP requests to external domains
   if git diff ${BASE_BRANCH}...HEAD | grep -iE "(fetch\s*\(|axios\.|http\.get|http\.post|requests\.get|wget|curl)" >/dev/null; then
       EXTERNAL_URLS_FOUND="${EXTERNAL_URLS_FOUND}HTTP requests found. "
   fi

   # CDN and external resources in HTML/JS
   if git diff ${BASE_BRANCH}...HEAD | grep -iE "cdn\.|\.cloudfront\.|\.cloudflare\.|https?://[^/]+(?!.*internal)" | grep -v "github.com" >/dev/null; then
       EXTERNAL_URLS_FOUND="${EXTERNAL_URLS_FOUND}CDN/external resources found. "
   fi

   # External scripts and resources
   if git diff ${BASE_BRANCH}...HEAD | grep -iE "<script\s+src=|<link\s+href=|<img\s+src=" >/dev/null; then
       EXTERNAL_URLS_FOUND="${EXTERNAL_URLS_FOUND}External scripts/resources found. "
   fi

   # Analytics/tracking
   if git diff ${BASE_BRANCH}...HEAD | grep -iE "analytics|tracking|telemetry|sentry|datadog|newrelic" >/dev/null; then
       EXTERNAL_URLS_FOUND="${EXTERNAL_URLS_FOUND}Analytics/telemetry detected. "
   fi

   if [ -n "$EXTERNAL_URLS_FOUND" ]; then
       EXTERNAL_URLS_STATUS="WARNING - $EXTERNAL_URLS_FOUND"
   else
       EXTERNAL_URLS_STATUS="PASS"
   fi
   ```

### Step 6: Check for Common Issues

Capture code quality findings in variables:

1. **No test coverage**:
   ```bash
   if git diff ${BASE_BRANCH}...HEAD --name-only | grep -qE "\.(test|spec)\.|^tests?/"; then
       TESTS_STATUS="PASS - Test files modified"
   else
       TESTS_STATUS="WARNING - No test files were modified"
   fi
   ```

2. **Documentation**:
   ```bash
   if git diff ${BASE_BRANCH}...HEAD --name-only | grep -qE "\.md$|^docs/"; then
       DOCUMENTATION_STATUS="PASS - Documentation updated"
   else
       DOCUMENTATION_STATUS="WARNING - No documentation changes detected"
   fi
   ```

3. **Breaking changes**:
   ```bash
   if git diff ${BASE_BRANCH}...HEAD --name-only | grep -qE "version|CHANGELOG|breaking"; then
       BREAKING_CHANGES_STATUS="WARNING - Version/breaking change files modified - review carefully"
   else
       BREAKING_CHANGES_STATUS="PASS - No breaking change indicators"
   fi
   ```

4. **Determine final recommendation**:
   ```bash
   # Check if there are any failures
   if [[ "$SECRETS_STATUS" == FAIL* ]] || [[ "$VULNERABILITIES_STATUS" == FAIL* ]] || [[ "$PROMPT_INJECTION_STATUS" == FAIL* ]]; then
       RECOMMENDATION="Request Changes"
   elif [[ "$SECRETS_STATUS" == WARNING* ]] || [[ "$VULNERABILITIES_STATUS" == WARNING* ]] || [[ "$EXTERNAL_URLS_STATUS" == WARNING* ]]; then
       RECOMMENDATION="Comment"
   else
       RECOMMENDATION="Approve"
   fi
   ```

### Step 7: Generate and Post Review Summary

Compile findings into a review and post it to the PR:

```bash
# Get the AI model being used
AI_MODEL="${OPENCODE_MODEL:-Kimi K2.5}"

# Build the review summary with actual findings
REVIEW_SUMMARY="## PR Review Summary

*Reviewed by: $AI_MODEL*

### Summary Alignment
$SUMMARY_FINDINGS

### Security Check
- Secrets: $SECRETS_STATUS
- Vulnerabilities: $VULNERABILITIES_STATUS
- Dependency changes: $DEPENDENCY_STATUS
- Prompt Injection: $PROMPT_INJECTION_STATUS
- External URLs: $EXTERNAL_URLS_STATUS

### Code Quality
- Tests: $TESTS_STATUS
- Documentation: $DOCUMENTATION_STATUS
- Breaking changes: $BREAKING_CHANGES_STATUS

### Recommendation
$RECOMMENDATION
"

# Output to console for user visibility
echo "$REVIEW_SUMMARY"

# Post the review to PR for historical record
if [ "$RECOMMENDATION" = "Approve" ]; then
    gh pr review $PR_NUMBER --approve --body "$REVIEW_SUMMARY"
elif [ "$RECOMMENDATION" = "Request Changes" ]; then
    gh pr review $PR_NUMBER --request-changes --body "$REVIEW_SUMMARY"
else
    gh pr review $PR_NUMBER --comment --body "$REVIEW_SUMMARY"
fi

echo "Review posted to PR #$PR_NUMBER"
```

The review is now posted as a PR comment for historical record and team visibility.

## Error Handling

- If gh is not authenticated, fail with error
- If no PR found, fail with error
- If security scan fails, report but continue with review

## Important Notes

- This is a helper review, not a substitute for human review
- Always manually verify critical changes
- Check for business logic correctness separately
- Review test coverage thoroughly
- All review output is automatically posted to the PR as a comment for historical record
- Reviews use GitHub's PR review feature (approve/request-changes/comment) for proper tracking
