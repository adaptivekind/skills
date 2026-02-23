"""
Git class for executing git commands.
"""

import subprocess
from typing import List, Optional


class Git:
    """Wrapper class for git commands."""
    
    def __init__(self, cwd: Optional[str] = None):
        self.cwd = cwd
    
    def _run(self, args: List[str], check: bool = True, capture_output: bool = True) -> subprocess.CompletedProcess:
        result = subprocess.run(
            ['git'] + args,
            cwd=self.cwd,
            capture_output=capture_output,
            text=True,
            check=check
        )
        return result
    
    def config(self, key: str, local: bool = True) -> str:
        """Get a git config value."""
        try:
            args = ['config']
            if local and self.cwd:
                args.append('--local')
            args.append(key)
            return self._run(args).stdout.strip()
        except subprocess.CalledProcessError:
            return ''
    
    @property
    def user_email(self) -> str:
        return self.config('user.email')
    
    @property
    def user_signingkey(self) -> str:
        return self.config('user.signingkey')
    
    def branch_show_current(self) -> str:
        """Get the current branch name."""
        try:
            return self._run(['branch', '--show-current']).stdout.strip()
        except subprocess.CalledProcessError:
            return ''
    
    def branch_list(self) -> str:
        """List all branches."""
        try:
            return self._run(['branch']).stdout.strip()
        except subprocess.CalledProcessError:
            return ''
    
    def is_detached_head(self) -> bool:
        """Check if HEAD is detached."""
        result = self.branch_list()
        if not result:
            return True
        return '(HEAD detached' in result
    
    def rev_parse(self, *args: str) -> str:
        """Run git rev-parse with given arguments."""
        try:
            return self._run(['rev-parse'] + list(args)).stdout.strip()
        except subprocess.CalledProcessError:
            return ''
    
    def rev_parse_short_head(self) -> str:
        """Get short SHA of HEAD."""
        result = self.rev_parse('--short', 'HEAD')
        return result if result else 'initial'
    
    @property
    def toplevel(self) -> str:
        """Get the repository root."""
        return self.rev_parse('--show-toplevel')
    
    @property
    def git_dir(self) -> str:
        """Get the .git directory path."""
        return self.rev_parse('--git-dir')
    
    def diff_name_only(self, cached: bool = False, diff_filter: str = '') -> List[str]:
        """Get list of changed files."""
        args = ['diff', '--name-only']
        if cached:
            args.insert(1, '--cached')
        if diff_filter:
            args.extend(['--diff-filter', diff_filter])
        try:
            result = self._run(args).stdout.strip()
            return result.split('\n') if result else []
        except subprocess.CalledProcessError:
            return []
    
    def diff_quiet(self, cached: bool = False) -> bool:
        """Check if there are no changes (returns True if quiet/no changes)."""
        args = ['diff', '--quiet']
        if cached:
            args.insert(1, '--cached')
        try:
            self._run(args)
            return True
        except subprocess.CalledProcessError:
            return False
    
    def has_changes(self) -> bool:
        """Check if there are any uncommitted changes."""
        return not (self.diff_quiet() and self.diff_quiet(cached=True))
    
    def ls_files_others(self) -> List[str]:
        """Get list of untracked files."""
        try:
            result = self._run(['ls-files', '--others', '--exclude-standard']).stdout.strip()
            return result.split('\n') if result else []
        except subprocess.CalledProcessError:
            return []
    
    def diff_stat(self, cached: bool = False) -> str:
        """Get diff stat summary."""
        args = ['diff', '--stat']
        if cached:
            args.insert(1, '--cached')
        try:
            return self._run(args).stdout.strip()
        except subprocess.CalledProcessError:
            return ''
    
    def checkout_new_branch(self, branch_name: str) -> None:
        """Create and switch to a new branch."""
        self._run(['checkout', '-b', branch_name], capture_output=False)
    
    def add(self, *files: str) -> None:
        """Stage files."""
        self._run(['add'] + list(files), capture_output=False)
    
    def commit(self, message: str, sign: bool = False) -> None:
        """Create a commit."""
        args = ['commit', '-m', message]
        if sign:
            args.insert(0, '-S')
        self._run(args, capture_output=False)
    
    def branch_rename(self, new_name: str) -> None:
        """Rename current branch."""
        self._run(['branch', '-m', new_name], capture_output=False)
