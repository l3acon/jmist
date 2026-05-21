#!/usr/bin/env bash
# Download the Mist OpenAPI spec from the upstream repository.
# Run this before using tools/mist_spec_parser.py.
set -euo pipefail

SPEC_URL="https://raw.githubusercontent.com/mistsys/mist_openapi/master/mist.openapi.json"
DEST_DIR="$(cd "$(dirname "$0")/.." && pwd)/specs"

mkdir -p "$DEST_DIR"
echo "Downloading Mist OpenAPI spec..."
curl -sL "$SPEC_URL" -o "$DEST_DIR/mist.openapi.json"
echo "Saved to $DEST_DIR/mist.openapi.json ($(du -h "$DEST_DIR/mist.openapi.json" | cut -f1))"
