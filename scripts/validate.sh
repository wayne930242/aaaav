#!/usr/bin/env bash
set -euo pipefail

# Quick validation runner for aaaav-loop-boot

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "=== Running Workspace Validation ==="
python3 "$REPO_ROOT/hooks/validate_all.py" "$REPO_ROOT"

echo "=== Running Unit Tests ==="
python3 -m unittest discover -s "$REPO_ROOT/tests"

echo "✓ All checks passed successfully."
