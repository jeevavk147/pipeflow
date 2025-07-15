#!/bin/bash
set -e

cd "$(dirname "$0")"  # Ensure you're in shared_layer/

# Clean previous builds
rm -rf python shared_layer.zip

# Create layer folder structure
mkdir -p python

# Install third-party dependencies
pip install -r requirements.txt -t python/

# Copy shared/ modules into layer
cp -r ../shared python/

# Zip for Lambda layer upload
zip -r9 shared_layer.zip python

echo "✅ Shared layer built successfully!"
