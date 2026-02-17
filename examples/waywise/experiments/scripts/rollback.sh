#!/bin/bash
set -e  # Exit on any error

#
# Rollback
#

PROJECT_ROOT_DIR="$(pwd)"
EXP_DIR="$PROJECT_ROOT_DIR/examples/waywise/experiments"
TARGET_CODE_DIR="$EXP_DIR/src/precise-truck"

echo "==> Cleaning up source directory"
rm -rf "$TARGET_CODE_DIR"
