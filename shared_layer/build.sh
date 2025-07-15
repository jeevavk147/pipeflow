#!/bin/bash
set -e

cd "$(dirname "$0")"

rm -rf python shared_layer.zip
mkdir -p python

# Install third-party dependencies to layer
pip install -r requirements.txt -t python/

# ✅ Copy shared modules inside python/ directory (so import works)
cp -r ../shared python/

# Zip layer
zip -r9 shared_layer.zip python

echo "✅ Shared layer built successfully!"
