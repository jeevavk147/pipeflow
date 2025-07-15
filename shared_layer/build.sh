#!/bin/bash
set -e

cd "$(dirname "$0")"  # go to shared_layer

# Clean previous builds
rm -rf python shared_layer.zip

# Create folder structure for layer
mkdir -p python

# Install packages into layer
pip install -r requirements.txt -t python/

# Copy shared code
cp -r ../shared python/

# Zip for layer publishing
zip -r9 shared_layer.zip python

echo "✅ Lambda layer built successfully!"
