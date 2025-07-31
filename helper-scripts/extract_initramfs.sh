#!/bin/sh
# -----------------------------------------------------------------------------
#  Script: extract-initramfs.sh
#  Author: Axura (https://4xura.com)
#  Description:
#    Extracts a compressed filesystem (initramfs.cpio.gz) passed as an argument
#    into a working directory for inspection or modification.
#
#  Usage:
#    ./extract-initramfs.sh <initramfs.cpio.gz>
#
#  Requirements:
#    - cpio
#    - gzip
# -----------------------------------------------------------------------------

set -euo pipefail

prog=${0##*/}

# === Input validation ===
if [ $# -ne 1 ]; then
    echo "Usage: $prog <initramfs.cpio.gz>" >&2
    exit 2
fi

INITRAMFS_ARCHIVE="$1"

if [ ! -s "$INITRAMFS_ARCHIVE" ]; then
    echo "[!] Error: '$INITRAMFS_ARCHIVE' does not exist or is empty." >&2
    exit 3
fi

# === Config ===
INITRAMFS_ARCHIVE_ABS="$(realpath "$INITRAMFS_ARCHIVE")"
OUT_DIR="./initramfs"
OUT_DIR_ABS="$(realpath --canonicalize-missing "$OUT_DIR")"

echo "[*] Starting initramfs extraction..."
echo "[*] Archive file     : $INITRAMFS_ARCHIVE_ABS"
echo "[*] Output directory : $OUT_DIR_ABS"

# === Clean up old output dir if exists ===
if [ -d "$OUT_DIR" ]; then
    echo "[!] Warning: Removing existing directory: $OUT_DIR"
    rm -rf "$OUT_DIR"
fi

mkdir -p "$OUT_DIR"
cp "$INITRAMFS_ARCHIVE_ABS" "$OUT_DIR"

# === Change into output dir and begin extraction ===
cd "$OUT_DIR"

ARCHIVE_BASENAME="$(basename "$INITRAMFS_ARCHIVE_ABS")"
CPIO_GZ_NAME="$ARCHIVE_BASENAME"
CPIO_NAME="${CPIO_GZ_NAME%.gz}"

echo "[*] Decompressing archive..."
gunzip -f "$CPIO_GZ_NAME"

echo "[*] Extracting CPIO contents..."
cpio -idmu < "$CPIO_NAME"

echo "[*] Cleaning up temporary CPIO file..."
rm -f "$CPIO_NAME"

# === Done ===
echo "[+] Extraction complete!"
echo "[+] Files are available at: $OUT_DIR_ABS"

