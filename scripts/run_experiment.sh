#!/bin/bash
# scripts/run_experiment.sh
# Entry point for running the experiment

set -e

echo "=== Laws of Simplicity Experiment Runner ==="
echo ""

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python version: $python_version"

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Create output directories
mkdir -p data/raw data/results

# Run experiment
echo ""
echo "Starting experiment..."
python -m experiment.runner "$@"

echo ""
echo "Experiment complete. Results in data/results/"