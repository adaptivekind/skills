#!/bin/bash
#
# uncommitted-changes.sh - Display all uncommitted changes in the repository
#
# This script shows a comprehensive overview of local changes that are
# yet to be committed, including staged, unstaged, and untracked files.
#
# Usage: ./scripts/uncommitted-changes.sh
#
# Output includes:
# - Staged files (ready to commit)
# - Unstaged modifications
# - Deleted files
# - Untracked files
# - Summary statistics
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${CYAN}========================================${NC}"
echo -e "${CYAN}   Uncommitted Changes Report${NC}"
echo -e "${CYAN}========================================${NC}"
echo ""

# Check if we're in a git repository
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo -e "${RED}Error: Not a git repository${NC}"
    exit 1
fi

# Get current branch info
echo -e "${BLUE}Repository:${NC} $(basename $(git rev-parse --show-toplevel))"
echo -e "${BLUE}Branch:${NC} $(git branch --show-current 2>/dev/null || echo 'detached HEAD')"
echo ""

# Check if there are any changes at all
if git diff --quiet && git diff --cached --quiet && [ -z "$(git ls-files --others --exclude-standard)" ]; then
    echo -e "${GREEN}✓ Working directory clean - no uncommitted changes${NC}"
    exit 0
fi

# Staged changes (ready to commit)
STAGED_ADDED=$(git diff --cached --name-only --diff-filter=A 2>/dev/null || true)
STAGED_MODIFIED=$(git diff --cached --name-only --diff-filter=M 2>/dev/null || true)
STAGED_DELETED=$(git diff --cached --name-only --diff-filter=D 2>/dev/null || true)
STAGED_TOTAL=$(git diff --cached --name-only 2>/dev/null || true)

if [ -n "$STAGED_TOTAL" ]; then
    echo -e "${GREEN}STAGED CHANGES (ready to commit):${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    if [ -n "$STAGED_ADDED" ]; then
        echo -e "${GREEN}Added (${#STAGED_ADDED} files):${NC}"
        echo "$STAGED_ADDED" | while read -r file; do
            echo "  + $file"
        done
        echo ""
    fi
    
    if [ -n "$STAGED_MODIFIED" ]; then
        echo -e "${YELLOW}Modified (${#STAGED_MODIFIED} files):${NC}"
        echo "$STAGED_MODIFIED" | while read -r file; do
            echo "  ~ $file"
        done
        echo ""
    fi
    
    if [ -n "$STAGED_DELETED" ]; then
        echo -e "${RED}Deleted (${#STAGED_DELETED} files):${NC}"
        echo "$STAGED_DELETED" | while read -r file; do
            echo "  - $file"
        done
        echo ""
    fi
    
    # Show staged diff stats
    echo -e "${CYAN}Staged Changes Summary:${NC}"
    git diff --cached --stat | tail -1
    echo ""
fi

# Unstaged changes (modified but not staged)
UNSTAGED_MODIFIED=$(git diff --name-only --diff-filter=M 2>/dev/null || true)
UNSTAGED_DELETED=$(git diff --name-only --diff-filter=D 2>/dev/null || true)
UNSTAGED_TOTAL=$(git diff --name-only 2>/dev/null || true)

if [ -n "$UNSTAGED_TOTAL" ]; then
    echo -e "${YELLOW}UNSTAGED CHANGES (not ready to commit):${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    if [ -n "$UNSTAGED_MODIFIED" ]; then
        echo -e "${YELLOW}Modified (${#UNSTAGED_MODIFIED} files):${NC}"
        echo "$UNSTAGED_MODIFIED" | while read -r file; do
            echo "  ~ $file"
        done
        echo ""
    fi
    
    if [ -n "$UNSTAGED_DELETED" ]; then
        echo -e "${RED}Deleted (${#UNSTAGED_DELETED} files):${NC}"
        echo "$UNSTAGED_DELETED" | while read -r file; do
            echo "  - $file"
        done
        echo ""
    fi
    
    # Show unstaged diff stats
    echo -e "${CYAN}Unstaged Changes Summary:${NC}"
    git diff --stat | tail -1
    echo ""
fi

# Untracked files
UNTRACKED_FILES=$(git ls-files --others --exclude-standard 2>/dev/null || true)

if [ -n "$UNTRACKED_FILES" ]; then
    echo -e "${BLUE}UNTRACKED FILES:${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "$UNTRACKED_FILES" | while read -r file; do
        echo "  ? $file"
    done
    echo ""
fi

# Summary statistics
echo -e "${CYAN}========================================${NC}"
echo -e "${CYAN}   Summary${NC}"
echo -e "${CYAN}========================================${NC}"

STAGED_COUNT=$(echo "$STAGED_TOTAL" | grep -c . || echo "0")
UNSTAGED_COUNT=$(echo "$UNSTAGED_TOTAL" | grep -c . || echo "0")
UNTRACKED_COUNT=$(echo "$UNTRACKED_FILES" | grep -c . || echo "0")

echo "  Staged files:     $STAGED_COUNT"
echo "  Unstaged files:   $UNSTAGED_COUNT"
echo "  Untracked files:  $UNTRACKED_COUNT"
echo "  Total changes:    $((STAGED_COUNT + UNSTAGED_COUNT + UNTRACKED_COUNT))"
echo ""

if [ -n "$STAGED_TOTAL" ]; then
    echo -e "${GREEN}Run 'git commit' to commit staged changes${NC}"
fi

if [ -n "$UNSTAGED_TOTAL" ]; then
    echo -e "${YELLOW}Run 'git add <file>' to stage unstaged changes${NC}"
fi

if [ -n "$UNTRACKED_FILES" ]; then
    echo -e "${BLUE}Run 'git add <file>' to track untracked files${NC}"
fi
