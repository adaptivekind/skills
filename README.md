# Skills

A collection of agent skills for AI coding assistants.

## Available Skills

### commit

Creates a signed commit in the local repository. If on main or master branch,
creates a new branch first. Fails if GPG signing is not configured.

**Usage:** Triggered when you ask to commit changes.

### push

Pushes commits to remote if branch is not main and all commits are GPG signed.

**Usage:** Triggered when you ask to push changes.

### create-pr

Creates a GitHub pull request using gh CLI with auto-generated title and description.
Commits and pushes uncommitted changes if needed.

**Usage:** Triggered when you ask to create a PR.

### pr-review

Reviews a PR to verify it does what the summary claims and has no security vulnerabilities.
Checks for secrets, prompt injection, external URLs, and dependency changes.

**Usage:** Triggered when you ask to review a PR.

### repository-healthcheck

Checks repository is correctly configured - branch protection, PR requirements, and merge settings.

**Usage:** Triggered when you ask to check repository health.

### ship

Commits, pushes, creates PR, reviews, and merges to main with safety checks.
Performs automated security review and auto-merges if no issues are found.

**Usage:** Triggered when you ask to apply changes or ship changes.

## Installation

### From GitHub

```bash
npx skills add adaptivekind/skills
```

Or to install globally:

```bash
npx skills add -g adaptivekind/skills
```

### From local clone

```bash
git clone https://github.com/adaptivekind/skills.git /path/to/skills
cd /path/to/skills
npx skills add .
```

## Usage

The agent will automatically use these skills when relevant tasks are detected.
For example, when you ask to "commit changes", the agent will load the commit
skill and follow its instructions to create a signed commit.

**Common commands:**
- "Commit my changes" - Creates a signed commit
- "Push to remote" - Pushes commits to remote
- "Create a PR" - Creates a GitHub pull request
- "Review this PR" - Performs security and quality review
- "Ship these changes" - Full workflow: commit, push, PR, review, merge
- "Check repository health" - Verifies branch protection and settings

## Prerequisites

- Git configured with GPG signing (`user.email` and `user.signingkey`)
- GitHub CLI (`gh`) installed and authenticated for PR operations
- Write access to the repository for merge operations
