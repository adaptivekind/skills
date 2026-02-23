#!/usr/bin/env python3
"""
Tests for common.git.Git class
"""

import subprocess

import pytest


@pytest.fixture
def git_repo(tmp_path):
    subprocess.run(["git", "init"], cwd=tmp_path, check=True, capture_output=True)
    subprocess.run(
        ["git", "config", "--local", "user.email", "test@example.com"],
        cwd=tmp_path,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "config", "--local", "user.name", "Test User"],
        cwd=tmp_path,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "config", "--local", "commit.gpgsign", "false"],
        cwd=tmp_path,
        check=True,
        capture_output=True,
    )
    yield tmp_path


@pytest.fixture
def git(git_repo):
    from common.git import Git

    return Git(cwd=str(git_repo))


class TestGit:
    def test_user_email(self, git):
        assert git.user_email == "test@example.com"

    def test_user_signingkey_empty(self, git):
        # Signing key not set in local config (ignores global)
        result = git.config("user.signingkey", local=True)
        assert result == ""

    def test_toplevel(self, git, git_repo):
        assert git.toplevel == str(git_repo)

    def test_git_dir(self, git):
        assert ".git" in git.git_dir

    def test_branch_show_current_main(self, git, git_repo):
        (git_repo / "file.txt").write_text("content")
        subprocess.run(
            ["git", "add", "."], cwd=git_repo, check=True, capture_output=True
        )
        subprocess.run(
            ["git", "commit", "-m", "init"],
            cwd=git_repo,
            check=True,
            capture_output=True,
        )
        branch = git.branch_show_current()
        assert branch in ("main", "master")

    def test_branch_show_current_after_rename(self, git, git_repo):
        (git_repo / "file.txt").write_text("content")
        subprocess.run(
            ["git", "add", "."], cwd=git_repo, check=True, capture_output=True
        )
        subprocess.run(
            ["git", "commit", "-m", "init"],
            cwd=git_repo,
            check=True,
            capture_output=True,
        )
        git.branch_rename("master")
        assert git.branch_show_current() == "master"

    def test_is_detached_head_after_first_commit(self, git, git_repo):
        # After first commit, should not be detached
        (git_repo / "file.txt").write_text("content")
        subprocess.run(
            ["git", "add", "."], cwd=git_repo, check=True, capture_output=True
        )
        subprocess.run(
            ["git", "commit", "-m", "init"],
            cwd=git_repo,
            check=True,
            capture_output=True,
        )
        assert git.is_detached_head() is False

    def test_is_detached_head_after_checkout(self, git, git_repo):
        (git_repo / "file.txt").write_text("content")
        subprocess.run(
            ["git", "add", "."], cwd=git_repo, check=True, capture_output=True
        )
        subprocess.run(
            ["git", "commit", "-m", "init"],
            cwd=git_repo,
            check=True,
            capture_output=True,
        )
        subprocess.run(
            ["git", "commit", "--allow-empty", "-m", "second"],
            cwd=git_repo,
            check=True,
            capture_output=True,
        )
        subprocess.run(
            ["git", "checkout", "HEAD~1"], cwd=git_repo, check=True, capture_output=True
        )
        assert git.is_detached_head() is True

    def test_rev_parse_short_head(self, git, git_repo):
        (git_repo / "file.txt").write_text("content")
        subprocess.run(
            ["git", "add", "."], cwd=git_repo, check=True, capture_output=True
        )
        subprocess.run(
            ["git", "commit", "-m", "init"],
            cwd=git_repo,
            check=True,
            capture_output=True,
        )
        sha = git.rev_parse_short_head()
        assert len(sha) == 7

    def test_diff_name_only_no_changes(self, git, git_repo):
        assert git.diff_name_only() == []

    def test_diff_name_only_with_changes(self, git, git_repo):
        # First make an initial commit so we can test tracked file changes
        (git_repo / "file.txt").write_text("original")
        git.add("file.txt")
        git.commit("Initial")
        # Now modify the file
        (git_repo / "file.txt").write_text("modified")
        assert git.diff_name_only() == ["file.txt"]

    def test_diff_name_only_staged(self, git, git_repo):
        (git_repo / "file.txt").write_text("content")
        git.add("file.txt")
        assert git.diff_name_only(cached=True) == ["file.txt"]

    def test_diff_quiet_no_changes(self, git, git_repo):
        assert git.diff_quiet() is True

    def test_diff_quiet_with_changes(self, git, git_repo):
        # First make an initial commit so we can test tracked file changes
        (git_repo / "file.txt").write_text("original")
        git.add("file.txt")
        git.commit("Initial")
        # Now modify the file
        (git_repo / "file.txt").write_text("modified")
        assert git.diff_quiet() is False

    def test_has_changes_false(self, git, git_repo):
        assert git.has_changes() is False

    def test_has_changes_true(self, git, git_repo):
        # First make an initial commit so we can test tracked file changes
        (git_repo / "file.txt").write_text("original")
        git.add("file.txt")
        git.commit("Initial")
        # Now modify the file
        (git_repo / "file.txt").write_text("modified")
        assert git.has_changes() is True

    def test_ls_files_others(self, git, git_repo):
        (git_repo / "new.txt").write_text("content")
        assert git.ls_files_others() == ["new.txt"]

    def test_diff_stat(self, git, git_repo):
        # First make an initial commit so we can test tracked file changes
        (git_repo / "file.txt").write_text("original")
        git.add("file.txt")
        git.commit("Initial")
        # Now modify the file
        (git_repo / "file.txt").write_text("modified")
        stat = git.diff_stat()
        assert "file.txt" in stat

    def test_diff_stat_cached(self, git, git_repo):
        (git_repo / "file.txt").write_text("content")
        git.add("file.txt")
        stat = git.diff_stat(cached=True)
        assert "file.txt" in stat

    def test_checkout_new_branch(self, git, git_repo):
        (git_repo / "file.txt").write_text("content")
        subprocess.run(
            ["git", "add", "."], cwd=git_repo, check=True, capture_output=True
        )
        subprocess.run(
            ["git", "commit", "-m", "init"],
            cwd=git_repo,
            check=True,
            capture_output=True,
        )
        git.checkout_new_branch("feature/test")
        assert git.branch_show_current() == "feature/test"

    def test_add_and_commit(self, git, git_repo):
        (git_repo / "file.txt").write_text("content")
        git.add("file.txt")
        git.commit("Initial commit")
        assert git.diff_quiet() is True
        assert git.diff_quiet(cached=True) is True
