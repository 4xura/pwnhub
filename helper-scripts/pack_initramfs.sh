#!/bin/sh
# --------------------------------------------------------------------------
# pack_initramfs.sh - Build and package exploit into initramfs
#
# Author: Axura
# Website: https://4xura.com
#
# Usage:
#   ./pack_initramfs.sh <exploit_source.c> [output_binary_name]
#
# Description:
#   - Compiles a statically linked exploit binary from the given C source
#   - Moves the binary into the 'initramfs/' directory
#   - Packs the initramfs directory into 'initramfs.cpio.gz' using cpio+gzip
#
# Example:
#   ./pack_initramfs.sh xpl.c
#   ./pack_initramfs.sh xpl.c custom_name
# --------------------------------------------------------------------------

set -euo pipefail

# --- Input Parsing ---
if [ $# -lt 1 ]; then
    echo "Usage: $0 <exploit_source.c> [output_binary_name]"
    exit 1
fi

SRC_FILE="$1"
BIN_NAME="${2:-xpl}"
INITRAMFS_DIR="./initramfs"
OUTPUT_NAME="initramfs.cpio.gz"

# --- Sanity Checks ---
[ -f "$SRC_FILE" ] || { echo "Error: source file '$SRC_FILE' not found."; exit 1; }
[ -d "$INITRAMFS_DIR" ] || { echo "Error: directory '$INITRAMFS_DIR' not found."; exit 1; }

# --- Build ---
echo "[*] Building '$BIN_NAME' statically using Makefile..."
make release TARGET="$BIN_NAME" SRCS="$SRC_FILE"

# --- Move binary ---
echo "[*] Moving '$BIN_NAME' into '$INITRAMFS_DIR/'..."
mv -f "./$BIN_NAME" "$INITRAMFS_DIR/"

# --- Pack initramfs ---
echo "[*] Repacking initramfs to ../$OUTPUT_NAME..."
cd "$INITRAMFS_DIR"
find . -print0 | cpio --null -ov --format=newc | gzip -9 > "../$OUTPUT_NAME"
cd ..

echo "[+] Done: $OUTPUT_NAME created."

