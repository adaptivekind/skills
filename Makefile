.PHONY: test test-all test-commit test-common test-help

# Default target - run all tests
test: test-all

# Run all tests (skills and common)
test-all:
	@echo "Running all tests..."
	@PYTHONPATH=. pytest skills/ common/ -v

# Run commit skill tests specifically
test-commit:
	@echo "Running commit skill tests..."
	@PYTHONPATH=. pytest skills/commit/tests/test_pre_commit.py -v

# Run common package tests
test-common:
	@echo "Running common package tests..."
	@PYTHONPATH=. pytest common/git/test_git.py -v

# Show test help
test-help:
	@echo "Available test targets:"
	@echo "  make test         - Run all tests (default)"
	@echo "  make test-all    - Run all tests"
	@echo "  make test-commit - Run commit skill tests only"
	@echo "  make test-common - Run common package tests only"
	@echo ""
	@echo "To run individual test files:"
	@echo "  pytest skills/<skill>/tests/test_<name>.py"
