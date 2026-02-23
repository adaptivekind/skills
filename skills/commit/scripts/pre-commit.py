#!/usr/bin/env python3
"""
pre-commit.py - Prepare repository for commit

This script handles the deterministic pre-commit logic:
1. Verifies GPG signing is configured
2. Checks current branch
3. Creates semantic branch if on main/master

Usage: ./scripts/pre-commit.py [branch_prefix]
"""

import os
import sys
import subprocess
import re
from datetime import datetime

RED = '\033[0;31m'
GREEN = '\033[0;32m'
YELLOW = '\033[1;33m'
NC = '\033[0m'


def run_git_command(args, capture_output=True, check=True):
    result = subprocess.run(
        ['git'] + args,
        capture_output=capture_output,
        text=True,
        check=check
    )
    return result.stdout.strip() if capture_output else None


def get_current_branch():
    try:
        return run_git_command(['branch', '--show-current'])
    except subprocess.CalledProcessError:
        return None


def is_detached_head():
    try:
        result = run_git_command(['branch'])
        if not result:
            return True
        return '(HEAD detached' in result
    except subprocess.CalledProcessError:
        return True


def get_head_sha():
    try:
        result = run_git_command(['rev-parse', '--short', 'HEAD'])
        return result if result else 'initial'
    except subprocess.CalledProcessError:
        return 'initial'


def get_changed_files():
    try:
        result = run_git_command(['diff', '--name-only'])
        return result.split('\n') if result else []
    except subprocess.CalledProcessError:
        return []


def detect_change_type(changed_files):
    for f in changed_files:
        if f.startswith('skills/'):
            return 'skill'
        if re.search(r'\.(test|spec)\.', f):
            return 'test'
        if re.match(r'^docs/|README|CHANGELOG', f):
            return 'docs'
    return 'update'


def generate_branch_name(change_type, changed_files, branch_prefix=None):
    if branch_prefix:
        return branch_prefix
    
    first_file = changed_files[0] if changed_files else ''
    
    if first_file:
        dirname = os.path.dirname(first_file)
        filename = os.path.splitext(os.path.basename(first_file))[0]
        
        dirname_slug = re.sub(r'[^a-z0-9]', '', dirname.split('/')[-1].lower()) if dirname else ''
        filename_slug = re.sub(r'[^a-z0-9]', '', filename.lower()) if filename else ''
        
        date_str = datetime.now().strftime('%Y%m%d')
        
        if filename_slug:
            return f"{change_type}/{date_str}-{filename_slug}"
        elif dirname_slug:
            return f"{change_type}/{date_str}-{dirname_slug}"
    
    date_str = datetime.now().strftime('%Y%m%d')
    return f"{change_type}/{date_str}-update"


def check_gpg_config():
    print("Verifying GPG signing configuration...")
    
    try:
        user_email = run_git_command(['config', 'user.email'])
        signing_key = run_git_command(['config', 'user.signingkey'])
    except subprocess.CalledProcessError:
        user_email = ''
        signing_key = ''
    
    if not user_email or not signing_key:
        print(f"{RED}Error: GPG signing is not configured.{NC}")
        print("Please set:")
        print("  git config user.email 'your@email.com'")
        print("  git config user.signingkey 'YOUR_KEY_ID'")
        sys.exit(1)
    
    print(f"{GREEN}GPG signing configured: {user_email}{NC}")


def check_branch(branch_prefix=None):
    current_branch = get_current_branch()
    detached = is_detached_head()
    
    if detached:
        current_branch = get_head_sha()
        print(f"{YELLOW}Detached HEAD state detected. Using ref: {current_branch}{NC}")
    
    print(f"Current branch: {current_branch}")
    
    if current_branch in ('main', 'master') or detached:
        print(f"{YELLOW}On main/master or detached HEAD. Creating feature branch...{NC}")
        
        sha = get_head_sha()
        changed_files = [f for f in get_changed_files() if f]
        change_type = detect_change_type(changed_files)
        
        print(f"Detected change type: {change_type}")
        
        branch_name = generate_branch_name(change_type, changed_files, branch_prefix)
        
        print(f"Creating branch: {branch_name}")
        
        run_git_command(['checkout', '-b', branch_name], capture_output=False)
        
        print(f"{GREEN}Created and switched to branch: {branch_name}{NC}")


def check_changes():
    print("Checking for changes to commit...")
    
    has_unstaged = False
    has_staged = False
    
    try:
        run_git_command(['diff', '--quiet'])
    except subprocess.CalledProcessError:
        has_unstaged = True
    
    try:
        run_git_command(['diff', '--cached', '--quiet'])
    except subprocess.CalledProcessError:
        has_staged = True
    
    if not has_unstaged and not has_staged:
        print(f"{YELLOW}No changes to commit.{NC}")
        sys.exit(0)
    
    print(f"{GREEN}Changes detected. Repository is ready for commit.{NC}")
    print("")
    print("Next steps:")
    print("  1. Stage changes: git add -A")
    print("  2. Create signed commit: git commit -S -m 'Your message'")
    print("  3. Verify: git log -1 --show-signature")


def main():
    branch_prefix = sys.argv[1] if len(sys.argv) > 1 else None
    
    check_gpg_config()
    check_branch(branch_prefix)
    check_changes()


if __name__ == '__main__':
    main()
