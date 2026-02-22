.PHONY: test test-all test-commit test-help

# Default target - run all tests
test: test-all

# Run all skill tests
test-all:
	@echo "Running all skill tests..."
	@find skills -name "*.bats" -path "*/tests/*" -exec bats {} +

# Run commit skill tests specifically
test-commit:
	@echo "Running commit skill tests..."
	@bats skills/commit/tests/pre-commit.bats

# Show test help
test-help:
	@echo "Available test targets:"
	@echo "  make test        - Run all skill tests (default)"
	@echo "  make test-all    - Run all skill tests"
	@echo "  make test-commit - Run commit skill tests only"
	@echo ""
	@echo "To run individual test files:"
	@echo "  bats skills/<skill>/tests/<test>.bats"
