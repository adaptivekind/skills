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
import subprocess
from pathlib import Path

RED = '\033[0;31m'
GREEN = '\033[0;32m'
YELLOW = '\033[1;33m'
BLUE = '\033[0;34m'
CYAN = '\033[0;36m'
NC = '\033[0m'


def run_git_command(args, capture_output=True, check=True):
    result = subprocess.run(
        ['git'] + args,
        capture_output=capture_output,
        text=True,
        check=check
    )
    return result.stdout.strip() if capture_output else None


def is_git_repo():
    try:
        run_git_command(['rev-parse', '--git-dir'])
        return True
    except subprocess.CalledProcessError:
        return False


def get_repo_name():
    try:
        toplevel = run_git_command(['rev-parse', '--show-toplevel'])
        return os.path.basename(toplevel) if toplevel else 'unknown'
    except subprocess.CalledProcessError:
        return 'unknown'


def get_branch():
    try:
        return run_git_command(['branch', '--show-current'])
    except subprocess.CalledProcessError:
        return 'detached HEAD'


def get_staged_files(diff_filter=''):
    args = ['diff', '--cached', '--name-only']
    if diff_filter:
        args.extend(['--diff-filter', diff_filter])
    try:
        result = run_git_command(args)
        return result.split('\n') if result else []
    except subprocess.CalledProcessError:
        return []


def get_unstaged_files(diff_filter=''):
    args = ['diff', '--name-only']
    if diff_filter:
        args.extend(['--diff-filter', diff_filter])
    try:
        result = run_git_command(args)
        return result.split('\n') if result else []
    except subprocess.CalledProcessError:
        return []


def get_untracked_files():
    try:
        result = run_git_command(['ls-files', '--others', '--exclude-standard'])
        return result.split('\n') if result else []
    except subprocess.CalledProcessError:
        return []


def has_changes():
    unstaged = get_unstaged_files()
    staged = get_staged_files()
    untracked = get_untracked_files()
    return bool(unstaged or staged or untracked)


def print_section(title, color):
    print(f"{color}{title}{NC}")


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


def print_repo_info():
    repo_name = get_repo_name()
    branch = get_branch()
    print(f"{BLUE}Repository:{NC} {repo_name}")
    print(f"{BLUE}Branch:{NC} {branch}")
    print("")


def print_staged_changes():
    staged_added = get_staged_files('A')
    staged_modified = get_staged_files('M')
    staged_deleted = get_staged_files('D')
    staged_total = get_staged_files()
    
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
    try:
        result = run_git_command(['diff', '--cached', '--stat'])
        if result:
            lines = result.split('\n')
            if lines:
                print(f"  {lines[-1]}")
    except subprocess.CalledProcessError:
        pass
    print("")


def print_unstaged_changes():
    unstaged_modified = get_unstaged_files('M')
    unstaged_deleted = get_unstaged_files('D')
    unstaged_total = get_unstaged_files()
    
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
    try:
        result = run_git_command(['diff', '--stat'])
        if result:
            lines = result.split('\n')
            if lines:
                print(f"  {lines[-1]}")
    except subprocess.CalledProcessError:
        pass
    print("")


def print_untracked():
    untracked = get_untracked_files()
    untracked = [f for f in untracked if f]
    
    if not untracked:
        return
    
    print(f"{BLUE}UNTRACKED FILES:{NC}")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print_files(untracked, "?", BLUE)
    print("")


def print_summary():
    staged = get_staged_files()
    unstaged = get_unstaged_files()
    untracked = get_untracked_files()
    
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
    if not is_git_repo():
        print(f"{RED}Error: Not a git repository{NC}")
        sys.exit(1)
    
    print_header()
    print_repo_info()
    
    if not has_changes():
        print(f"{GREEN}✓ Working directory clean - no uncommitted changes{NC}")
        sys.exit(0)
    
    print_staged_changes()
    print_unstaged_changes()
    print_untracked()
    print_summary()


if __name__ == '__main__':
    main()
