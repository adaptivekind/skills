#!/bin/bash
#
# pre-commit.sh - Prepare repository for commit
#
# This script handles the deterministic pre-commit logic:
# 1. Verifies GPG signing is configured
# 2. Checks current branch
# 3. Creates semantic branch if on main/master
#
# Usage: ./scripts/pre-commit.sh [branch_prefix]
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Step 1: Verify GPG Signing is Configured
echo "Verifying GPG signing configuration..."

USER_EMAIL=$(git config user.email)
SIGNING_KEY=$(git config user.signingkey)

if [ -z "$USER_EMAIL" ] || [ -z "$SIGNING_KEY" ]; then
    echo -e "${RED}Error: GPG signing is not configured.${NC}"
    echo "Please set:"
    echo "  git config user.email 'your@email.com'"
    echo "  git config user.signingkey 'YOUR_KEY_ID'"
    exit 1
fi

echo -e "${GREEN}GPG signing configured: $USER_EMAIL${NC}"

# Step 2: Check Current Branch
CURRENT_BRANCH=$(git branch --show-current)

# If in detached HEAD state, use the current HEAD ref
if [ -z "$CURRENT_BRANCH" ]; then
    CURRENT_BRANCH=$(git rev-parse HEAD)
    echo -e "${YELLOW}Detached HEAD state detected. Using ref: ${CURRENT_BRANCH}${NC}"
fi

echo "Current branch: $CURRENT_BRANCH"

# Step 3: Handle Branch Creation (if on main or master or detached HEAD)
if [ "$CURRENT_BRANCH" = "main" ] || [ "$CURRENT_BRANCH" = "master" ] || [ -z "$(git branch --show-current)" ]; then
    echo -e "${YELLOW}On main/master or detached HEAD. Creating feature branch...${NC}"
    
    # Check if there are any commits in the repository
    if git rev-parse --verify HEAD >/dev/null 2>&1; then
        SHA=$(git rev-parse --short HEAD)
    else
        SHA="initial"
    fi
    
    # Detect change type from file paths
    CHANGED_FILES=$(git diff --name-only)
    
    if echo "$CHANGED_FILES" | grep -q "skills/"; then
        TYPE="skill"
    elif echo "$CHANGED_FILES" | grep -qE "\.(test|spec)\."; then
        TYPE="test"
    elif echo "$CHANGED_FILES" | grep -qE "^docs/|README|CHANGELOG"; then
        TYPE="docs"
    else
        TYPE="update"
    fi
    
    echo "Detected change type: $TYPE"
    
    # Generate branch name
    BRANCH_PREFIX="$1"
    
    if [ -n "$BRANCH_PREFIX" ]; then
        BRANCH_NAME="$BRANCH_PREFIX"
    else
        # Convert first word of commit message to slug, or use dirname
        FIRST_DIR=$(echo "$CHANGED_FILES" | head -1 | xargs dirname 2>/dev/null | sed 's|.*/||' | tr '[:upper:]' '[:lower:]' | tr ' ' '-')
        FILENAME=$(echo "$CHANGED_FILES" | head -1 | xargs basename 2>/dev/null | sed 's/\.[^.]*$//' | tr '[:upper:]' '[:lower:]' | tr ' ' '-')
        
        if [ -n "$FILENAME" ]; then
            BRANCH_NAME="$TYPE/$(date +%Y%m%d)-$FILENAME"
        elif [ -n "$FIRST_DIR" ]; then
            BRANCH_NAME="$TYPE/$(date +%Y%m%d)-$FIRST_DIR"
        else
            BRANCH_NAME="$TYPE/$(date +%Y%m%d)-update"
        fi
    fi
    
    echo "Creating branch: $BRANCH_NAME"
    
    # Create and switch to the new branch
    git checkout -b "$BRANCH_NAME"
    
    echo -e "${GREEN}Created and switched to branch: $BRANCH_NAME${NC}"
fi

# Step 4: Check for Changes
echo "Checking for changes to commit..."

if git diff --quiet && git diff --cached --quiet; then
    echo -e "${YELLOW}No changes to commit.${NC}"
    exit 0
fi

echo -e "${GREEN}Changes detected. Repository is ready for commit.${NC}"
echo ""
echo "Next steps:"
echo "  1. Stage changes: git add -A"
echo "  2. Create signed commit: git commit -S -m 'Your message'"
echo "  3. Verify: git log -1 --show-signature"
