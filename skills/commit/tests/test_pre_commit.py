#!/usr/bin/env python3
"""
Test suite for pre-commit.py script

These tests verify the deterministic pre-commit logic including:
- GPG signing verification
- Branch creation on main/master
- Semantic branch naming based on change types
- Detached HEAD handling
"""

import os
import subprocess

import pytest


@pytest.fixture
def git_repo(tmp_path):
    os.chdir(tmp_path)
    subprocess.run(["git", "init"], check=True, capture_output=True)
    subprocess.run(
        ["git", "config", "user.email", "test@example.com"],
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "Test User"], check=True, capture_output=True
    )
    subprocess.run(
        ["git", "config", "commit.gpgsign", "false"], check=True, capture_output=True
    )

    script_path = os.path.join(
        os.path.dirname(__file__), "..", "scripts", "pre-commit.py"
    )
    subprocess.run(["cp", script_path, "."], check=True, capture_output=True)
    subprocess.run(["chmod", "+x", "pre-commit.py"], check=True, capture_output=True)

    yield tmp_path


def run_script(cwd, *args):
    env = os.environ.copy()
    # Set PYTHONPATH to project root so the script can find skills package
    project_root = os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    )
    env["PYTHONPATH"] = project_root
    result = subprocess.run(
        ["python3", "./pre-commit.py"] + list(args),
        cwd=cwd,
        capture_output=True,
        text=True,
        env=env,
    )
    return result


class TestPreCommit:
    def test_passes_when_gpg_signing_configured(self, git_repo):
        subprocess.run(
            ["git", "config", "user.email", "test@example.com"],
            cwd=git_repo,
            check=True,
            capture_output=True,
        )
        subprocess.run(
            ["git", "config", "user.signingkey", "12345678"],
            cwd=git_repo,
            check=True,
            capture_output=True,
        )

        (git_repo / "file.txt").write_text("initial\n")
        subprocess.run(
            ["git", "add", "file.txt"], cwd=git_repo, check=True, capture_output=True
        )
        subprocess.run(
            ["git", "commit", "-m", "Initial commit"],
            cwd=git_repo,
            check=True,
            capture_output=True,
        )

        (git_repo / "file.txt").write_text("initial\nnew content\n")

        result = run_script(git_repo)
        assert result.returncode == 0
        assert "GPG signing configured" in result.stdout

    def test_creates_skill_branch_when_on_main_with_skills_changes(self, git_repo):
        subprocess.run(
            ["git", "config", "user.signingkey", "12345678"],
            cwd=git_repo,
            check=True,
            capture_output=True,
        )

        (git_repo / "skills" / "test").mkdir(parents=True)
        (git_repo / "skills" / "test" / "file.txt").write_text("content")
        subprocess.run(
            ["git", "add", "."], cwd=git_repo, check=True, capture_output=True
        )
        subprocess.run(
            ["git", "commit", "-m", "Initial commit"],
            cwd=git_repo,
            check=True,
            capture_output=True,
        )

        (git_repo / "skills" / "test" / "file.txt").write_text("new content")

        result = run_script(git_repo)
        assert result.returncode == 0
        assert "Detected change type: skill" in result.stdout
        assert "Created and switched to branch" in result.stdout

        branch = subprocess.run(
            ["git", "branch", "--show-current"],
            cwd=git_repo,
            capture_output=True,
            text=True,
        ).stdout.strip()
        assert branch.startswith("skill/")

    def test_creates_test_branch_when_on_main_with_test_file_changes(self, git_repo):
        subprocess.run(
            ["git", "config", "user.signingkey", "12345678"],
            cwd=git_repo,
            check=True,
            capture_output=True,
        )

        (git_repo / "app.test.js").write_text("content")
        subprocess.run(
            ["git", "add", "."], cwd=git_repo, check=True, capture_output=True
        )
        subprocess.run(
            ["git", "commit", "-m", "Initial commit"],
            cwd=git_repo,
            check=True,
            capture_output=True,
        )

        (git_repo / "app.test.js").write_text("new content")

        result = run_script(git_repo)
        assert result.returncode == 0
        assert "Detected change type: test" in result.stdout

        branch = subprocess.run(
            ["git", "branch", "--show-current"],
            cwd=git_repo,
            capture_output=True,
            text=True,
        ).stdout.strip()
        assert branch.startswith("test/")

    def test_creates_docs_branch_when_on_main_with_docs_changes(self, git_repo):
        subprocess.run(
            ["git", "config", "user.signingkey", "12345678"],
            cwd=git_repo,
            check=True,
            capture_output=True,
        )

        (git_repo / "docs").mkdir(parents=True)
        (git_repo / "docs" / "README.md").write_text("content")
        subprocess.run(
            ["git", "add", "."], cwd=git_repo, check=True, capture_output=True
        )
        subprocess.run(
            ["git", "commit", "-m", "Initial commit"],
            cwd=git_repo,
            check=True,
            capture_output=True,
        )

        (git_repo / "docs" / "README.md").write_text("new content")

        result = run_script(git_repo)
        assert result.returncode == 0
        assert "Detected change type: docs" in result.stdout

        branch = subprocess.run(
            ["git", "branch", "--show-current"],
            cwd=git_repo,
            capture_output=True,
            text=True,
        ).stdout.strip()
        assert branch.startswith("docs/")

    def test_creates_update_branch_when_on_main_with_other_changes(self, git_repo):
        subprocess.run(
            ["git", "config", "user.signingkey", "12345678"],
            cwd=git_repo,
            check=True,
            capture_output=True,
        )

        (git_repo / "random.txt").write_text("content")
        subprocess.run(
            ["git", "add", "."], cwd=git_repo, check=True, capture_output=True
        )
        subprocess.run(
            ["git", "commit", "-m", "Initial commit"],
            cwd=git_repo,
            check=True,
            capture_output=True,
        )

        (git_repo / "random.txt").write_text("new content")

        result = run_script(git_repo)
        assert result.returncode == 0
        assert "Detected change type: update" in result.stdout

        branch = subprocess.run(
            ["git", "branch", "--show-current"],
            cwd=git_repo,
            capture_output=True,
            text=True,
        ).stdout.strip()
        assert branch.startswith("update/")

    def test_creates_branch_on_master(self, git_repo):
        subprocess.run(
            ["git", "config", "user.signingkey", "12345678"],
            cwd=git_repo,
            check=True,
            capture_output=True,
        )

        (git_repo / "file.txt").write_text("content")
        subprocess.run(
            ["git", "add", "."], cwd=git_repo, check=True, capture_output=True
        )
        subprocess.run(
            ["git", "commit", "-m", "Initial commit"],
            cwd=git_repo,
            check=True,
            capture_output=True,
        )
        subprocess.run(
            ["git", "branch", "-m", "master"],
            cwd=git_repo,
            check=True,
            capture_output=True,
        )

        (git_repo / "file.txt").write_text("new content")

        result = run_script(git_repo)
        assert result.returncode == 0
        assert "On main/master" in result.stdout

        branch = subprocess.run(
            ["git", "branch", "--show-current"],
            cwd=git_repo,
            capture_output=True,
            text=True,
        ).stdout.strip()
        assert branch != "master"

    def test_uses_custom_branch_prefix_when_provided(self, git_repo):
        subprocess.run(
            ["git", "config", "user.signingkey", "12345678"],
            cwd=git_repo,
            check=True,
            capture_output=True,
        )

        (git_repo / "file.txt").write_text("content")
        subprocess.run(
            ["git", "add", "."], cwd=git_repo, check=True, capture_output=True
        )
        subprocess.run(
            ["git", "commit", "-m", "Initial commit"],
            cwd=git_repo,
            check=True,
            capture_output=True,
        )

        (git_repo / "file.txt").write_text("new content")

        result = run_script(git_repo, "feature/custom-branch")
        assert result.returncode == 0
        assert "Creating branch: feature/custom-branch" in result.stdout

        branch = subprocess.run(
            ["git", "branch", "--show-current"],
            cwd=git_repo,
            capture_output=True,
            text=True,
        ).stdout.strip()
        assert branch == "feature/custom-branch"

    def test_does_nothing_when_not_on_main_master_and_has_changes(self, git_repo):
        subprocess.run(
            ["git", "config", "user.signingkey", "12345678"],
            cwd=git_repo,
            check=True,
            capture_output=True,
        )

        (git_repo / "file.txt").write_text("content")
        subprocess.run(
            ["git", "add", "."], cwd=git_repo, check=True, capture_output=True
        )
        subprocess.run(
            ["git", "commit", "-m", "Initial commit"],
            cwd=git_repo,
            check=True,
            capture_output=True,
        )

        subprocess.run(
            ["git", "checkout", "-b", "feature/existing-branch"],
            cwd=git_repo,
            check=True,
            capture_output=True,
        )

        (git_repo / "file.txt").write_text("new content")

        result = run_script(git_repo)
        assert result.returncode == 0
        assert "Current branch: feature/existing-branch" in result.stdout
        assert "Creating feature branch" not in result.stdout

        branch = subprocess.run(
            ["git", "branch", "--show-current"],
            cwd=git_repo,
            capture_output=True,
            text=True,
        ).stdout.strip()
        assert branch == "feature/existing-branch"

    def test_handles_detached_head_state(self, git_repo):
        subprocess.run(
            ["git", "config", "user.signingkey", "12345678"],
            cwd=git_repo,
            check=True,
            capture_output=True,
        )

        (git_repo / "file.txt").write_text("content")
        subprocess.run(
            ["git", "add", "."], cwd=git_repo, check=True, capture_output=True
        )
        subprocess.run(
            ["git", "commit", "-m", "Initial commit"],
            cwd=git_repo,
            check=True,
            capture_output=True,
        )

        (git_repo / "file.txt").write_text("more content")
        subprocess.run(
            ["git", "add", "."], cwd=git_repo, check=True, capture_output=True
        )
        subprocess.run(
            ["git", "commit", "-m", "Second commit"],
            cwd=git_repo,
            check=True,
            capture_output=True,
        )

        subprocess.run(
            ["git", "checkout", "HEAD~1"], cwd=git_repo, check=True, capture_output=True
        )

        (git_repo / "new_file.txt").write_text("detached change")

        result = run_script(git_repo)
        assert result.returncode == 0
        assert "Detached HEAD state detected" in result.stdout
        assert "Creating feature branch" in result.stdout

    def test_handles_case_with_no_changes(self, git_repo):
        subprocess.run(
            ["git", "config", "user.signingkey", "12345678"],
            cwd=git_repo,
            check=True,
            capture_output=True,
        )

        (git_repo / "file.txt").write_text("content")
        subprocess.run(
            ["git", "add", "."], cwd=git_repo, check=True, capture_output=True
        )
        subprocess.run(
            ["git", "commit", "-m", "Initial commit"],
            cwd=git_repo,
            check=True,
            capture_output=True,
        )

        result = run_script(git_repo)
        assert result.returncode == 0
        assert "No changes to commit" in result.stdout
