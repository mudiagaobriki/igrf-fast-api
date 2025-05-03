#!/bin/bash

# This script copies custom files to the pyIGRF site-packages folder during deployment on Render

# Create the necessary directories if they don't exist
mkdir -p site-packages/pyIGRF/src

# Copy the custom files to the pyIGRF site-packages folder
if [ -f "custom_loadCoeffs.py" ]; then
    echo "Copying custom_loadCoeffs.py to site-packages/pyIGRF/loadCoeffs.py"
    cp custom_loadCoeffs.py site-packages/pyIGRF/loadCoeffs.py
fi

if [ -f "custom_igrf14coeffs.txt" ]; then
    echo "Copying custom_igrf14coeffs.txt to site-packages/pyIGRF/src/igrf14coeffs.txt"
    cp custom_igrf14coeffs.txt site-packages/pyIGRF/src/igrf14coeffs.txt
fi

# Find the actual pyIGRF site-packages directory
PYIGRF_DIR=$(python -c "import pyIGRF; import os; print(os.path.dirname(pyIGRF.__file__))")

if [ -n "$PYIGRF_DIR" ]; then
    echo "Found pyIGRF directory at $PYIGRF_DIR"
    
    # Copy the custom files to the actual pyIGRF site-packages directory
    if [ -f "custom_loadCoeffs.py" ]; then
        echo "Copying custom_loadCoeffs.py to $PYIGRF_DIR/loadCoeffs.py"
        cp custom_loadCoeffs.py "$PYIGRF_DIR/loadCoeffs.py"
    fi
    
    if [ -f "custom_igrf14coeffs.txt" ]; then
        echo "Copying custom_igrf14coeffs.txt to $PYIGRF_DIR/src/igrf14coeffs.txt"
        mkdir -p "$PYIGRF_DIR/src"
        cp custom_igrf14coeffs.txt "$PYIGRF_DIR/src/igrf14coeffs.txt"
    fi
else
    echo "Could not find pyIGRF directory"
    exit 1
fi

echo "Predeploy script completed successfully"