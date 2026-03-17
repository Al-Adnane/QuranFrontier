#!/bin/bash
# AraBERT Semantic Embedding Pipeline Runner
# Generates 250K+ embeddings for Islamic corpus using Arabic-aware AraBERT

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "=================================================="
echo "AraBERT Semantic Embedding Pipeline"
echo "=================================================="
echo "Project root: $PROJECT_ROOT"
echo "Script directory: $SCRIPT_DIR"
echo "Time: $(date)"
echo "=================================================="

# Set Python path to include project
export PYTHONPATH="${PROJECT_ROOT}:${PYTHONPATH}"

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python3 not found"
    exit 1
fi

# Check if required packages are installed
echo "Checking dependencies..."
python3 -c "import torch; print(f'PyTorch version: {torch.__version__}')"
python3 -c "import transformers; print(f'Transformers version: {transformers.__version__}')"
python3 -c "import numpy; print(f'NumPy version: {numpy.__version__}')"

echo ""
echo "Starting embedding generation..."
echo ""

# Run the embedding generation pipeline
cd "$SCRIPT_DIR"
python3 generate_embeddings.py

echo ""
echo "=================================================="
echo "Embedding pipeline completed!"
echo "Output files saved to: $SCRIPT_DIR"
echo "=================================================="
