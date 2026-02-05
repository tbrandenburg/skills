#!/usr/bin/env bash
# Setup virtual environment for pdf-to-markdown skill.
# This script creates a venv and installs docling if not already present.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/.venv"

# Check if venv exists
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
fi

# Activate venv
source "$VENV_DIR/bin/activate"

# Check if docling is installed
if ! python -c "import docling" 2>/dev/null; then
    echo "Installing docling..."
    pip install --quiet docling
fi

echo "✓ Virtual environment ready at: $VENV_DIR"
echo "To activate manually: source $VENV_DIR/bin/activate"
