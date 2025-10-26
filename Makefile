
# Makefile for the SAC-D packet reader project.

# List of all known targets in this Makefile.
KNOWN_TARGETS := all install run clean

# This variable will hold all command-line arguments that are not known targets.
# For example, if you run `make run data/raw.dat`, ARGS will be `data/raw.dat`.
ARGS := $(filter-out $(KNOWN_TARGETS),$(MAKECMDGOALS))

.PHONY: all install run clean

# Default target executed when you run `make`
all:
	@echo "Usage: make [install|run|clean]"
	@echo "  install          - Install project dependencies"
	@echo "  run <ARGS>       - Run the script on the specified arguments"
	@echo "  clean            - Remove generated files"

# Install dependencies using poetry
install:
	poetry install

# Run the main script
# Usage: make run path/to/your/datafile.dat
run:
	poetry run python src/main.py $(ARGS)

# Clean up generated files
clean:
	rm -f voltages.png boxplot-voltages-*.png output.txt
