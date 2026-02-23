.PHONY: test test-all test-commit test-help

# Default target - run all tests
test: test-all

# Run all skill tests
test-all:
	@echo "Running all skill tests..."
	@pytest skills/ -v

# Run commit skill tests specifically
test-commit:
	@echo "Running commit skill tests..."
	@pytest skills/commit/tests/test_pre_commit.py -v

# Show test help
test-help:
	@echo "Available test targets:"
	@echo "  make test        - Run all skill tests (default)"
	@echo "  make test-all    - Run all skill tests"
	@echo "  make test-commit - Run commit skill tests only"
	@echo ""
	@echo "To run individual test files:"
	@echo "  pytest skills/<skill>/tests/test_<name>.py"
