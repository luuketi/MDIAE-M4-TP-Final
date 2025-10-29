
# Makefile for the SAC-D packet reader project.

# List of all known targets in this Makefile.
KNOWN_TARGETS := all install run clean format tests coverage lint

# This variable will hold all command-line arguments that are not known targets.
# For example, if you run `make run data/raw.dat`, ARGS will be `data/raw.dat`.
ARGS := $(filter-out $(KNOWN_TARGETS),$(MAKECMDGOALS))

.PHONY: all install run clean format tests coverage lint

# Default target executed when you run `make`
all:
	@echo "Usage: make [install|run|clean|format|tests|coverage|lint]"
	@echo "  install          - Install project dependencies"
	@echo "  run <ARGS>       - Run the script on the specified arguments"
	@echo "  clean            - Remove generated files"
	@echo "  format           - Format python files using ruff"
	@echo "  tests            - Run all tests using pytest"
	@echo "  coverage         - Run tests with coverage report"
	@echo "  lint             - Check code style using ruff"

# Install dependencies using poetry
install:
	poetry install

# Run the main script
# Usage: make run path/to/your/datafile.dat
run:
	poetry run python -m src.main $(ARGS)

# Clean up generated files
clean:
	rm -f voltages.png boxplot-voltages-*.png output.txt

# Format python files
format:
	poetry run ruff format .

.PHONY: tests
tests:
	poetry run pytest

.PHONY: coverage
coverage:
	poetry run pytest --cov=src --cov-report=term-missing

.PHONY: lint
lint:
	poetry run ruff check .
