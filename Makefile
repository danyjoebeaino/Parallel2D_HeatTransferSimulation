# Compiler and flags
CC = gcc
CFLAGS = -Wall -Wextra -O2 -std=c99
LIBS = -lm

# Targets
SERIAL_TARGET = heat_simulation
ADVANCED_TARGET = heat_simulation_advanced
VALIDATION_TARGET = validation_tool
VISUALIZATION_SCRIPT = visualize.py
ADVANCED_VISUALIZATION_SCRIPT = advanced_visualize.py

# Source files
SERIAL_SRC = heat_serial.c
ADVANCED_SRC = heat_serial_advanced.c
VALIDATION_SRC = validation_simple.c

# Default target - build everything
all: serial advanced validation

# Serial version (original)
serial: $(SERIAL_SRC)
	$(CC) $(CFLAGS) -o $(SERIAL_TARGET) $(SERIAL_SRC) $(LIBS)
	@echo "✅ Built serial version: $(SERIAL_TARGET)"

# Advanced version with progress monitoring
advanced: $(ADVANCED_SRC)
	$(CC) $(CFLAGS) -o $(ADVANCED_TARGET) $(ADVANCED_SRC) $(LIBS)
	@echo "✅ Built advanced version: $(ADVANCED_TARGET)"

# Validation tool
validation: $(VALIDATION_SRC)
	$(CC) $(CFLAGS) -o $(VALIDATION_TARGET) $(VALIDATION_SRC) $(LIBS)
	@echo "✅ Built validation tool: $(VALIDATION_TARGET)"

# Run the basic simulation
run: serial
	@echo "🚀 Running basic simulation..."
	./$(SERIAL_TARGET)

# Run the advanced simulation
run-advanced: advanced
	@echo "🚀 Running advanced simulation..."
	./$(ADVANCED_TARGET)

# Run validation
validate: validation
	@echo "🔍 Running validation..."
	./$(VALIDATION_TARGET)

# Run basic visualization
visualize:
	@echo "📊 Running basic visualization..."
	python3 $(VISUALIZATION_SCRIPT)

# Run advanced visualization
visualize-advanced:
	@echo "📊 Running advanced visualization..."
	python3 $(ADVANCED_VISUALIZATION_SCRIPT)

# Run everything: validate → simulate → visualize
all-in-one: validate run-advanced visualize-advanced
	@echo "🎉 Complete pipeline finished!"

# Install Python dependencies
install-deps:
	@echo "📦 Installing Python dependencies..."
	pip3 install numpy matplotlib scipy

# Clean up build files
clean:
	rm -f $(SERIAL_TARGET) $(ADVANCED_TARGET) $(VALIDATION_TARGET)
	@echo "🧹 Cleaned up executables"

# Clean everything including output files
clean-all: clean
	rm -f output_*.txt *.png *.gif
	rm -rf plots
	@echo "🧹 Cleaned up everything"

# Create output directories
setup:
	mkdir -p plots
	@echo "📁 Created output directories"

# Help message
help:
	@echo "Available targets:"
	@echo "  all           - Build all versions"
	@echo "  serial        - Build basic serial version"
	@echo "  advanced      - Build advanced version with progress bars"
	@echo "  validation    - Build validation tool"
	@echo "  run           - Run basic simulation"
	@echo "  run-advanced  - Run advanced simulation"
	@echo "  validate      - Run parameter validation"
	@echo "  visualize     - Run basic visualization"
	@echo "  visualize-advanced - Run advanced visualization"
	@echo "  all-in-one    - Run complete pipeline"
	@echo "  install-deps  - Install Python dependencies"
	@echo "  clean         - Remove executables"
	@echo "  clean-all     - Remove everything"
	@echo "  setup         - Create output directories"
	@echo "  help          - Show this help message"

.PHONY: all serial advanced validation run run-advanced validate visualize visualize-advanced all-in-one install-deps clean clean-all setup help
