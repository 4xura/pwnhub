#!/bin/sh
# -----------------------------------------------------------------------------
# extract-image.sh - Extract uncompressed vmlinux ELF from a compressed kernel image
#
# Author: Axura
# Website: https://4xura.com
#
# Description:
#   This script locates and decompresses the embedded vmlinux ELF file from
#   a compressed Linux kernel image (e.g., vmlinuz, bzImage).
#   Supports gzip, xz, bzip2, lzma, lzop, lz4, and zstd formats.
#
# Usage:
#   ./extract-image.sh <kernel-image> > vmlinux
# -----------------------------------------------------------------------------

#set -x

# Validate and emit ELF if found
is_vmlinux() {
	readelf -h $1 > /dev/null 2>&1 || return 1
	cat $1
	exit 0
}

# Attempt decompression from located magic headers
probe() {
	local magic="$1"
	local tag="$2"
	shift 2
	local cmd=("$@")  

	for pos in $(tr "$magic\n$tag" "\n$tag=" < "$img" | grep -abo "^$tag"); 
	do
		offset=${pos%%:*}
		tail -c+"$offset" "$img" | "${cmd[@]}" > "$tmp" 2>/dev/null
		is_vmlinux "$tmp" 
	done
}

# Main entry point
prog=${0##*/}
img="$1"

[ $# -eq 1 ] && [ -s "$img" ] || {
	echo "Usage: $prog <compressed-kernel-image>" >&2
	exit 2
}

tmp=$(mktemp /tmp/vmlinux-XXXXXX)
trap 'rm -f "$tmp"' EXIT

# Try each known compression type
probe '\037\213\010'     AX      gunzip
probe '\3757zXZ\000'     AXURA   unxz
probe 'BZh'              AX      bunzip2
probe '\135\0\0\0'       AXU     unlzma
probe '\211\114\132'     AX      'lzop -d'
probe '\002!L\030'       AXU     'lz4 -d'
probe '(\265/\375'       AXU     unzstd

# Final fallback: maybe it's already ELF
is_vmlinux "$img"

# Nothing worked
echo "$prog: failed to find a valid vmlinux image in '$img'" >&2
exit 1

