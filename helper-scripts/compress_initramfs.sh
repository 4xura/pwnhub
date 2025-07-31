#!/bin/sh
# -----------------------------------------------------------------------------
#  Script: compress_initramfs.sh
#  Author: Axura (https://4xura.com)
#  Description:
#    Compresses the contents of a directory (e.g., ./initramfs) into a
#    cpio archive, then gzips it into initramfs.cpio.gz for use with QEMU.
#
#  Usage:
#    ./compress_initramfs.sh <source-dir> [output-file]
#
#  Requirements:
#    - cpio
#    - gzip
# -----------------------------------------------------------------------------

set -euo pipefail

prog=${0##*/}

# === Input validation ===
if [ $# -lt 1 ] || [ $# -gt 2 ]; then
    echo "Usage: $prog <source-dir> [output-file]" >&2
    exit 2
fi

SRC_DIR="$1"
OUT_FILE="${2:-initramfs.cpio.gz}"

if [ ! -d "$SRC_DIR" ]; then
    echo "[!] Error: Source directory '$SRC_DIR' not found." >&2
    exit 3
fi

SRC_DIR_ABS="$(realpath "$SRC_DIR")"
OUT_FILE_ABS="$(realpath --canonicalize-missing "$OUT_FILE")"

echo "[*] Creating initramfs archive..."
echo "[*] Source directory : $SRC_DIR_ABS"
echo "[*] Output archive   : $OUT_FILE_ABS"

# === Change into source directory and archive ===
(
    cd "$SRC_DIR"
    find . -print0 | cpio --null -ov --format=newc | gzip -9 > "$OUT_FILE_ABS"
)

echo "[+] Archive created: $OUT_FILE_ABS"

