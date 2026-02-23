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
import re
import subprocess
from datetime import datetime

# Add project root to path so we can import skills.git
# Check PYTHONPATH first, then fall back to script location
def find_project_root():
    # First check PYTHONPATH environment variable
    pythonpath = os.environ.get('PYTHONPATH', '')
    if pythonpath and os.path.isdir(os.path.join(pythonpath, 'skills')):
        return pythonpath
    
    # Then try script location
    script_dir = os.path.dirname(os.path.abspath(__file__))
    commit_dir = os.path.dirname(script_dir)
    skills_dir = os.path.dirname(commit_dir)
    project_root = os.path.dirname(skills_dir)
    return project_root

sys.path.insert(0, find_project_root())

from common.git import Git

RED = '\033[0;31m'
GREEN = '\033[0;32m'
YELLOW = '\033[1;33m'
NC = '\033[0m'


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


def check_gpg_config(git):
    print("Verifying GPG signing configuration...")
    
    user_email = git.user_email
    signing_key = git.user_signingkey
    
    if not user_email or not signing_key:
        print(f"{RED}Error: GPG signing is not configured.{NC}")
        print("Please set:")
        print("  git config user.email 'your@email.com'")
        print("  git config user.signingkey 'YOUR_KEY_ID'")
        sys.exit(1)
    
    print(f"{GREEN}GPG signing configured: {user_email}{NC}")


def check_branch(git, branch_prefix=None):
    current_branch = git.branch_show_current()
    detached = git.is_detached_head()
    
    if detached:
        current_branch = git.rev_parse_short_head()
        print(f"{YELLOW}Detached HEAD state detected. Using ref: {current_branch}{NC}")
    
    print(f"Current branch: {current_branch}")
    
    if current_branch in ('main', 'master') or detached:
        print(f"{YELLOW}On main/master or detached HEAD. Creating feature branch...{NC}")
        
        sha = git.rev_parse_short_head()
        changed_files = [f for f in git.diff_name_only() if f]
        change_type = detect_change_type(changed_files)
        
        print(f"Detected change type: {change_type}")
        
        branch_name = generate_branch_name(change_type, changed_files, branch_prefix)
        
        print(f"Creating branch: {branch_name}")
        
        git.checkout_new_branch(branch_name)
        
        print(f"{GREEN}Created and switched to branch: {branch_name}{NC}")


def check_changes(git):
    print("Checking for changes to commit...")
    
    if not git.has_changes():
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
    
    git = Git()
    
    check_gpg_config(git)
    check_branch(git, branch_prefix)
    check_changes(git)


if __name__ == '__main__':
    main()
