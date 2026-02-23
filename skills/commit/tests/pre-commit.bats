#!/usr/bin/env bats
#
# Test suite for pre-commit.py script
#
# These tests verify the deterministic pre-commit logic including:
# - GPG signing verification
# - Branch creation on main/master
# - Semantic branch naming based on change types
# - Detached HEAD handling
#

setup() {
    # Create a temporary directory for each test
    TEST_DIR=$(mktemp -d)
    cd "$TEST_DIR"
    
    # Initialize a fresh git repository
    git init
    git config user.email "test@example.com"
    git config user.name "Test User"
    # Disable GPG signing for test commits (we test the script logic, not actual signing)
    git config commit.gpgsign false
    
    # Copy the script to test location (use BATS_TEST_DIRNAME for portability)
    cp "${BATS_TEST_DIRNAME}/../scripts/pre-commit.py" .
    chmod +x pre-commit.py
}

teardown() {
    # Clean up temporary directory
    cd "$BATS_TEST_DIRNAME"
    rm -rf "$TEST_DIR"
}

@test "passes when GPG signing is configured" {
    # Set up GPG signing
    git config user.email "test@example.com"
    git config user.signingkey "12345678"
    
    # Create initial commit (needed to be on a branch with history)
    echo "initial" > file.txt
    git add file.txt
    git commit -m "Initial commit"
    
    # Create a new file to have changes
    echo "new content" >> file.txt
    
    # Run script
    run ./pre-commit.py
    [ "$status" -eq 0 ]
    [[ "$output" == *"GPG signing configured"* ]]
}

@test "creates skill branch when on main with skills/ changes" {
    # Set up GPG signing
    git config user.email "test@example.com"
    git config user.signingkey "12345678"
    
    # Create initial commit on main
    mkdir -p skills/test
    echo "content" > skills/test/file.txt
    git add .
    git commit -m "Initial commit"
    
    # Create a change in skills directory
    echo "new content" > skills/test/file.txt
    
    # Run script
    run ./pre-commit.py
    [ "$status" -eq 0 ]
    [[ "$output" == *"Detected change type: skill"* ]]
    [[ "$output" == *"Created and switched to branch"* ]]
    
    # Verify branch was created with skill/ prefix
    CURRENT_BRANCH=$(git branch --show-current)
    [[ "$CURRENT_BRANCH" == skill/* ]]
}

@test "creates test branch when on main with test file changes" {
    # Set up GPG signing
    git config user.email "test@example.com"
    git config user.signingkey "12345678"
    
    # Create initial commit on main
    echo "content" > app.test.js
    git add .
    git commit -m "Initial commit"
    
    # Create a change in test file
    echo "new content" > app.test.js
    
    # Run script
    run ./pre-commit.py
    [ "$status" -eq 0 ]
    [[ "$output" == *"Detected change type: test"* ]]
    
    # Verify branch was created with test/ prefix
    CURRENT_BRANCH=$(git branch --show-current)
    [[ "$CURRENT_BRANCH" == test/* ]]
}

@test "creates docs branch when on main with docs/ changes" {
    # Set up GPG signing
    git config user.email "test@example.com"
    git config user.signingkey "12345678"
    
    # Create initial commit on main
    mkdir -p docs
    echo "content" > docs/README.md
    git add .
    git commit -m "Initial commit"
    
    # Create a change in docs directory
    echo "new content" > docs/README.md
    
    # Run script
    run ./pre-commit.py
    [ "$status" -eq 0 ]
    [[ "$output" == *"Detected change type: docs"* ]]
    
    # Verify branch was created with docs/ prefix
    CURRENT_BRANCH=$(git branch --show-current)
    [[ "$CURRENT_BRANCH" == docs/* ]]
}

@test "creates update branch when on main with other changes" {
    # Set up GPG signing
    git config user.email "test@example.com"
    git config user.signingkey "12345678"
    
    # Create initial commit on main
    echo "content" > random.txt
    git add .
    git commit -m "Initial commit"
    
    # Create a change
    echo "new content" > random.txt
    
    # Run script
    run ./pre-commit.py
    [ "$status" -eq 0 ]
    [[ "$output" == *"Detected change type: update"* ]]
    
    # Verify branch was created with update/ prefix
    CURRENT_BRANCH=$(git branch --show-current)
    [[ "$CURRENT_BRANCH" == update/* ]]
}

@test "creates branch on master (same as main)" {
    # Set up GPG signing
    git config user.email "test@example.com"
    git config user.signingkey "12345678"
    
    # Create initial commit on main, then rename to master
    echo "content" > file.txt
    git add .
    git commit -m "Initial commit"
    git branch -m master
    
    # Create a change
    echo "new content" > file.txt
    
    # Run script
    run ./pre-commit.py
    [ "$status" -eq 0 ]
    [[ "$output" == *"On main/master"* ]]
    
    # Verify branch was created
    CURRENT_BRANCH=$(git branch --show-current)
    [[ "$CURRENT_BRANCH" != "master" ]]
}

@test "uses custom branch prefix when provided" {
    # Set up GPG signing
    git config user.email "test@example.com"
    git config user.signingkey "12345678"
    
    # Create initial commit on main
    echo "content" > file.txt
    git add .
    git commit -m "Initial commit"
    
    # Create a change
    echo "new content" > file.txt
    
    # Run script with custom prefix
    run ./pre-commit.py "feature/custom-branch"
    [ "$status" -eq 0 ]
    [[ "$output" == *"Creating branch: feature/custom-branch"* ]]
    
    # Verify branch was created with custom name
    CURRENT_BRANCH=$(git branch --show-current)
    [ "$CURRENT_BRANCH" = "feature/custom-branch" ]
}

@test "does nothing when not on main/master and has changes" {
    # Set up GPG signing
    git config user.email "test@example.com"
    git config user.signingkey "12345678"
    
    # Create initial commit on main
    echo "content" > file.txt
    git add .
    git commit -m "Initial commit"
    
    # Create and switch to a feature branch
    git checkout -b feature/existing-branch
    
    # Create a change
    echo "new content" > file.txt
    
    # Run script
    run ./pre-commit.py
    [ "$status" -eq 0 ]
    [[ "$output" == *"Current branch: feature/existing-branch"* ]]
    [[ "$output" != *"Creating feature branch"* ]]
    
    # Verify still on same branch
    CURRENT_BRANCH=$(git branch --show-current)
    [ "$CURRENT_BRANCH" = "feature/existing-branch" ]
}

@test "handles detached HEAD state" {
    # Set up GPG signing
    git config user.email "test@example.com"
    git config user.signingkey "12345678"
    
    # Create initial commit on main
    echo "content" > file.txt
    git add .
    git commit -m "Initial commit"
    
    # Create a second commit
    echo "more content" >> file.txt
    git add .
    git commit -m "Second commit"
    
    # Detach HEAD
    git checkout HEAD~1
    
    # Create a change
    echo "detached change" > new_file.txt
    
    # Run script
    run ./pre-commit.py
    [ "$status" -eq 0 ]
    [[ "$output" == *"Detached HEAD state detected"* ]]
    [[ "$output" == *"Creating feature branch"* ]]
}

@test "handles case with no changes" {
    # Set up GPG signing
    git config user.email "test@example.com"
    git config user.signingkey "12345678"
    
    # Create initial commit on main
    echo "content" > file.txt
    git add .
    git commit -m "Initial commit"
    
    # Run script without any changes
    run ./pre-commit.py
    [ "$status" -eq 0 ]
    [[ "$output" == *"No changes to commit"* ]]
}
