#!/bin/bash

echo "=========================================="
echo "2D Heat Equation Simulation"
echo "=========================================="

# Check if C compiler is available
if ! command -v gcc &> /dev/null; then
    echo "Error: gcc compiler not found. Please install build-essential."
    exit 1
fi

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "Error: python3 not found. Please install Python 3."
    exit 1
fi

# Create necessary directories
mkdir -p plots

echo "1. Compiling the simulation..."
make

if [ $? -ne 0 ]; then
    echo "Error: Compilation failed!"
    exit 1
fi

echo "2. Running the simulation..."
./heat_simulation

if [ $? -ne 0 ]; then
    echo "Error: Simulation failed!"
    exit 1
fi

echo "3. Generating visualizations..."
python3 visualize.py

if [ $? -ne 0 ]; then
    echo "Error: Visualization failed!"
    exit 1
fi

echo "=========================================="
echo "Simulation completed successfully!"
echo "=========================================="
echo "Generated files:"
echo " - output_*.txt: Temperature data at different time steps"
echo " - plots/heatmap_*.png: Individual heatmap images"
echo " - heat_simulation.gif: Animation of the simulation"
echo " - final_temperature.png: Final temperature distribution"
echo "=========================================="
