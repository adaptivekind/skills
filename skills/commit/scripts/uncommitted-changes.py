#!/usr/bin/env python3
"""
uncommitted-changes.py - Display all uncommitted changes in the repository

This script shows a comprehensive overview of local changes that are
yet to be committed, including staged, unstaged, and untracked files.

Usage: ./scripts/uncommitted-changes.py

Output includes:
- Staged files (ready to commit)
- Unstaged modifications
- Deleted files
- Untracked files
- Summary statistics
"""

import os
import sys

from common.git import Git

RED = "\033[0;31m"
GREEN = "\033[0;32m"
YELLOW = "\033[1;33m"
BLUE = "\033[0;34m"
CYAN = "\033[0;36m"
NC = "\033[0m"


def print_files(files, prefix, color):
    if not files:
        return
    for f in files:
        if f:
            print(f"  {prefix} {f}")
    print("")


def print_header():
    print(f"{CYAN}========================================{NC}")
    print(f"{CYAN}   Uncommitted Changes Report{NC}")
    print(f"{CYAN}========================================{NC}")
    print("")


def print_repo_info(git):
    repo_name = os.path.basename(git.toplevel)
    branch = git.branch_show_current() or "detached HEAD"
    print(f"{BLUE}Repository:{NC} {repo_name}")
    print(f"{BLUE}Branch:{NC} {branch}")
    print("")


def print_staged_changes(git):
    staged_added = git.diff_name_only(cached=True, diff_filter="A")
    staged_modified = git.diff_name_only(cached=True, diff_filter="M")
    staged_deleted = git.diff_name_only(cached=True, diff_filter="D")
    staged_total = git.diff_name_only(cached=True)

    if not staged_total:
        return

    print(f"{GREEN}STAGED CHANGES (ready to commit):{NC}")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    if staged_added:
        count = len([f for f in staged_added if f])
        print(f"{GREEN}Added ({count} files):{NC}")
        print_files(staged_added, "+", GREEN)

    if staged_modified:
        count = len([f for f in staged_modified if f])
        print(f"{YELLOW}Modified ({count} files):{NC}")
        print_files(staged_modified, "~", YELLOW)

    if staged_deleted:
        count = len([f for f in staged_deleted if f])
        print(f"{RED}Deleted ({count} files):{NC}")
        print_files(staged_deleted, "-", RED)

    print(f"{CYAN}Staged Changes Summary:{NC}")
    stat = git.diff_stat(cached=True)
    if stat:
        lines = stat.split("\n")
        if lines:
            print(f"  {lines[-1]}")
    print("")


def print_unstaged_changes(git):
    unstaged_modified = git.diff_name_only(diff_filter="M")
    unstaged_deleted = git.diff_name_only(diff_filter="D")
    unstaged_total = git.diff_name_only()

    if not unstaged_total:
        return

    print(f"{YELLOW}UNSTAGED CHANGES (not ready to commit):{NC}")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    if unstaged_modified:
        count = len([f for f in unstaged_modified if f])
        print(f"{YELLOW}Modified ({count} files):{NC}")
        print_files(unstaged_modified, "~", YELLOW)

    if unstaged_deleted:
        count = len([f for f in unstaged_deleted if f])
        print(f"{RED}Deleted ({count} files):{NC}")
        print_files(unstaged_deleted, "-", RED)

    print(f"{CYAN}Unstaged Changes Summary:{NC}")
    stat = git.diff_stat()
    if stat:
        lines = stat.split("\n")
        if lines:
            print(f"  {lines[-1]}")
    print("")


def print_untracked(git):
    untracked = [f for f in git.ls_files_others() if f]

    if not untracked:
        return

    print(f"{BLUE}UNTRACKED FILES:{NC}")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print_files(untracked, "?", BLUE)
    print("")


def print_summary(git):
    staged = git.diff_name_only(cached=True)
    unstaged = git.diff_name_only()
    untracked = git.ls_files_others()

    staged_count = len([f for f in staged if f])
    unstaged_count = len([f for f in unstaged if f])
    untracked_count = len([f for f in untracked if f])
    total = staged_count + unstaged_count + untracked_count

    print(f"{CYAN}========================================{NC}")
    print(f"{CYAN}   Summary{NC}")
    print(f"{CYAN}========================================{NC}")
    print(f"  Staged files:     {staged_count}")
    print(f"  Unstaged files:   {unstaged_count}")
    print(f"  Untracked files:  {untracked_count}")
    print(f"  Total changes:    {total}")
    print("")

    if staged:
        print(f"{GREEN}Run 'git commit' to commit staged changes{NC}")

    if unstaged:
        print(f"{YELLOW}Run 'git add <file>' to stage unstaged changes{NC}")

    if untracked:
        print(f"{BLUE}Run 'git add <file>' to track untracked files{NC}")


def main():
    git = Git()

    if not git.git_dir:
        print(f"{RED}Error: Not a git repository{NC}")
        sys.exit(1)

    print_header()
    print_repo_info(git)

    if not git.has_changes() and not git.ls_files_others():
        print(f"{GREEN}✓ Working directory clean - no uncommitted changes{NC}")
        sys.exit(0)

    print_staged_changes(git)
    print_unstaged_changes(git)
    print_untracked(git)
    print_summary(git)


if __name__ == "__main__":
    main()
