#!/usr/bin/env bash
# ------------------------------------------------------------------------------
# run_test.sh - Launch a custom Linux kernel in QEMU with optional initramfs
#
# Author: Axura
# Website: https://4xura.com
#
# Usage:
#   ./run_test.sh [options]
#
# Description:
#   - Runs QEMU with a specified kernel and optional initramfs
#   - Provides a serial console via stdio for interactive debugging
#   - Supports custom memory, CPU model, kernel arguments, and debug flags
#
# Options:
#   --kernel PATH       Path to kernel image (default: ./vmlinux)
#   --initrd PATH       Path to initramfs (default: ./initramfs.cpio.gz)
#   --mem SIZE          Memory size (default: 256M)
#   --cpu STRING        QEMU CPU model (default: qemu64)
#   --hdb FILE          Attach file as second hard disk (default: flag.txt)
#   --append ARGS       Additional kernel command-line arguments
#   --debug             Enable QEMU internal debug logging
#   -h, --help          Show this help message
#
# Example:
#   ./run_test.sh --kernel ./vmlinux --initrd ./initramfs.cpio.gz --mem 512M --debug
# ------------------------------------------------------------------------------

set -euo pipefail

# Default values
KERNEL="./vmlinux"
INITRD="./initramfs.cpio.gz"
MEM="256M"
CPU="kvm64,+smep,+smap"
HDB="flag.txt"
APPEND="console=ttyS0 root=/dev/ram rw"
QEMU="qemu-system-x86_64"
DEBUG=0

usage() {
    echo "Usage: $0 [options]"
    echo ""
    echo "Options:"
    echo "  --kernel PATH       Path to kernel image (default: $KERNEL)"
    echo "  --initrd PATH       Path to initramfs (default: $INITRD)"
    echo "  --mem SIZE          Memory size (default: $MEM)"
    echo "  --cpu STRING        QEMU CPU model (default: $CPU)"
    echo "  --hdb FILE          Second hard disk image (default: $HDB)"
    echo "  --append ARGS       Kernel command-line arguments"
    echo "  --debug             Enable QEMU debug output"
    echo "  -h, --help          Show this help message"
    exit 1
}

log() {
    echo "[*] $*"
}

# Argument parsing
while [[ $# -gt 0 ]]; do
    case $1 in
        --kernel) KERNEL="$2"; shift 2 ;;
        --initrd) INITRD="$2"; shift 2 ;;
        --mem)    MEM="$2"; shift 2 ;;
        --cpu)    CPU="$2"; shift 2 ;;
        --hdb)    HDB="$2"; shift 2 ;;
        --append) APPEND="$2"; shift 2 ;;
        --debug)  DEBUG=1; shift ;;
        -h|--help) usage ;;
        *) echo "[!] Unknown option: $1"; usage ;;
    esac
done

# Validations
[[ -f "$KERNEL" ]] || { echo "[!] Kernel not found: $KERNEL"; exit 1; }
[[ -f "$INITRD" ]] || { echo "[!] Initramfs not found: $INITRD"; exit 1; }
[[ -f "$HDB" ]]    || { echo "[!] hdb file not found: $HDB"; exit 1; }

log "Launching QEMU with serial console..."
log "Kernel : $KERNEL"
log "Initrd : $INITRD"
log "Memory : $MEM"
log "CPU    : $CPU"
log "HDB    : $HDB"
log "Append : $APPEND"

sleep 1

$QEMU \
    -cpu "$CPU" \
    -m "$MEM" \
    -kernel "$KERNEL" \
    -initrd "$INITRD" \
    -hdb "$HDB" -snapshot \
    -nographic \
    -append "$APPEND" \
    -monitor /dev/null \
    -serial mon:stdio \
    -no-reboot \
    $([ "$DEBUG" -eq 1 ] && echo "-d int,cpu_reset,guest_errors")

