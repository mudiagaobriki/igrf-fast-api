#!/bin/bash

# This script copies custom files to the pyIGRF site-packages folder during deployment on Render

echo "Starting predeploy script..."

# Create the necessary directories if they don't exist
mkdir -p site-packages/pyIGRF/src
echo "Created local directories"

# Copy the custom files to the pyIGRF site-packages folder
if [ -f "custom_loadCoeffs.py" ]; then
    echo "Copying custom_loadCoeffs.py to site-packages/pyIGRF/loadCoeffs.py"
    cp custom_loadCoeffs.py site-packages/pyIGRF/loadCoeffs.py
fi

if [ -f "custom_igrf14coeffs.txt" ]; then
    echo "Copying custom_igrf14coeffs.txt to site-packages/pyIGRF/src/igrf14coeffs.txt"
    cp custom_igrf14coeffs.txt site-packages/pyIGRF/src/igrf14coeffs.txt
fi

# Create directories for all possible locations first
echo "Creating directories for all possible locations..."
mkdir -p .venv/lib/python3.11/site-packages/pyIGRF/src
mkdir -p /opt/render/project/src/.venv/lib/python3.11/site-packages/pyIGRF/src || true
mkdir -p /opt/render/project/.venv/lib/python3.11/site-packages/pyIGRF/src || true
mkdir -p /opt/render/project/src/.venv/lib/python3.9/site-packages/pyIGRF/src || true

# Copy files to all possible locations first
echo "Copying files to all possible locations..."
if [ -f "custom_loadCoeffs.py" ]; then
    cp custom_loadCoeffs.py .venv/lib/python3.11/site-packages/pyIGRF/loadCoeffs.py || true
    cp custom_loadCoeffs.py /opt/render/project/src/.venv/lib/python3.11/site-packages/pyIGRF/loadCoeffs.py || true
    cp custom_loadCoeffs.py /opt/render/project/.venv/lib/python3.11/site-packages/pyIGRF/loadCoeffs.py || true
    cp custom_loadCoeffs.py /opt/render/project/src/.venv/lib/python3.9/site-packages/pyIGRF/loadCoeffs.py || true
fi

if [ -f "custom_igrf14coeffs.txt" ]; then
    cp custom_igrf14coeffs.txt .venv/lib/python3.11/site-packages/pyIGRF/src/igrf14coeffs.txt || true
    cp custom_igrf14coeffs.txt /opt/render/project/src/.venv/lib/python3.11/site-packages/pyIGRF/src/igrf14coeffs.txt || true
    cp custom_igrf14coeffs.txt /opt/render/project/.venv/lib/python3.11/site-packages/pyIGRF/src/igrf14coeffs.txt || true
    cp custom_igrf14coeffs.txt /opt/render/project/src/.venv/lib/python3.9/site-packages/pyIGRF/src/igrf14coeffs.txt || true
fi

# Try to find the actual pyIGRF site-packages directory using multiple methods
echo "Attempting to find pyIGRF directory..."

# Method 1: Try to import pyIGRF and get its directory
echo "Method 1: Using Python import"
PYIGRF_DIR=$(python -c "
try:
    import pyIGRF
    import os
    print(os.path.dirname(pyIGRF.__file__))
except ImportError as e:
    print(f'ImportError: {e}')
    exit(1)
except Exception as e:
    print(f'Error: {e}')
    exit(1)
" 2>&1) || true

# Check if we got a valid directory
if [ -n "$PYIGRF_DIR" ] && [ ! "$PYIGRF_DIR" == ImportError* ] && [ ! "$PYIGRF_DIR" == Error* ]; then
    echo "Found pyIGRF directory at $PYIGRF_DIR"
else
    echo "Method 1 failed: $PYIGRF_DIR"

    # Method 2: Try to find the site-packages directory and look for pyIGRF
    echo "Method 2: Searching in site-packages directories"
    SITE_PACKAGES_DIRS=$(python -c "
import sys
import os
for path in sys.path:
    if 'site-packages' in path:
        print(path)
" 2>&1)

    for dir in $SITE_PACKAGES_DIRS; do
        if [ -d "$dir/pyIGRF" ]; then
            PYIGRF_DIR="$dir/pyIGRF"
            echo "Found pyIGRF directory at $PYIGRF_DIR"
            break
        fi
    done
fi

# Method 3: Try common locations if we still haven't found it
if [ -z "$PYIGRF_DIR" ] || [ "$PYIGRF_DIR" == ImportError* ] || [ "$PYIGRF_DIR" == Error* ]; then
    echo "Method 3: Checking common locations"

    # Check for virtual environment
    if [ -d ".venv/lib/python3.11/site-packages/pyIGRF" ]; then
        PYIGRF_DIR=".venv/lib/python3.11/site-packages/pyIGRF"
        echo "Found pyIGRF directory at $PYIGRF_DIR"
    elif [ -d "/opt/render/project/src/.venv/lib/python3.11/site-packages/pyIGRF" ]; then
        PYIGRF_DIR="/opt/render/project/src/.venv/lib/python3.11/site-packages/pyIGRF"
        echo "Found pyIGRF directory at $PYIGRF_DIR"
    elif [ -d "/opt/render/project/.venv/lib/python3.11/site-packages/pyIGRF" ]; then
        PYIGRF_DIR="/opt/render/project/.venv/lib/python3.11/site-packages/pyIGRF"
        echo "Found pyIGRF directory at $PYIGRF_DIR"
    elif [ -d "/opt/render/project/src/.venv/lib/python3.9/site-packages/pyIGRF" ]; then
        PYIGRF_DIR="/opt/render/project/src/.venv/lib/python3.9/site-packages/pyIGRF"
        echo "Found pyIGRF directory at $PYIGRF_DIR"
    fi
fi

# If we found a valid pyIGRF directory, copy the custom files there
if [ -n "$PYIGRF_DIR" ] && [ ! "$PYIGRF_DIR" == ImportError* ] && [ ! "$PYIGRF_DIR" == Error* ]; then
    echo "Found valid pyIGRF directory at $PYIGRF_DIR"

    # Create the src directory if it doesn't exist
    mkdir -p "$PYIGRF_DIR/src"

    # Copy the custom files to the actual pyIGRF site-packages directory
    if [ -f "custom_loadCoeffs.py" ]; then
        echo "Copying custom_loadCoeffs.py to $PYIGRF_DIR/loadCoeffs.py"
        cp custom_loadCoeffs.py "$PYIGRF_DIR/loadCoeffs.py"
    fi

    if [ -f "custom_igrf14coeffs.txt" ]; then
        echo "Copying custom_igrf14coeffs.txt to $PYIGRF_DIR/src/igrf14coeffs.txt"
        cp custom_igrf14coeffs.txt "$PYIGRF_DIR/src/igrf14coeffs.txt"
    fi
else
    echo "Warning: Could not find a valid pyIGRF directory."
fi

# Verify that the files exist in the expected locations
echo "Verifying files in expected locations..."

# Check if the files exist in the expected locations
if [ -f "/opt/render/project/src/.venv/lib/python3.11/site-packages/pyIGRF/loadCoeffs.py" ]; then
    echo "Found loadCoeffs.py in /opt/render/project/src/.venv/lib/python3.11/site-packages/pyIGRF/"
else
    echo "loadCoeffs.py not found in /opt/render/project/src/.venv/lib/python3.11/site-packages/pyIGRF/"
fi

if [ -f "/opt/render/project/src/.venv/lib/python3.11/site-packages/pyIGRF/src/igrf14coeffs.txt" ]; then
    echo "Found igrf14coeffs.txt in /opt/render/project/src/.venv/lib/python3.11/site-packages/pyIGRF/src/"
else
    echo "igrf14coeffs.txt not found in /opt/render/project/src/.venv/lib/python3.11/site-packages/pyIGRF/src/"
fi

echo "Predeploy script completed successfully"
