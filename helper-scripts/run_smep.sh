#!/usr/bin/env bash
# ------------------------------------------------------------------------------
# run_smep.sh - Launch QEMU for kernel exploits when SMEP is enabled
#
# Author: Axura
# Website: https://4xura.com
#
# Description:
#   - Enables SMEP (Supervisor Mode Execution Protection), a CPU feature that 
#     prevents the kernel from executing code from user-space memory. This is 
#     controlled by the 20th bit of CR4, and can be toggled via QEMU using 
#     `+smep` or boot parameters like `nosmep`.
#   - This script configures a QEMU environment with SMEP enabled, while disabling 
#     other mitigations like SMAP, KPTI, and KASLR.
#   - Useful for testing SMEP bypasses (e.g., ROP to kernel gadgets).
#
# Usage:
#   ./run_smep.sh [options]
#
# Options:
#   --kernel PATH       Kernel image (default: ./vmlinuz)
#   --initrd PATH       Initramfs (default: ./initramfs.cpio.gz)
#   --mem SIZE          Memory size (default: 256M)
#   --cpu STRING        QEMU CPU model (default: qemu64,smep=on,smap=off)
#   --hdb FILE          Attach file as second hard disk (default: flag.txt)
#   --append ARGS       Kernel cmdline (default: disable all mitigations except SMEP)
#   -h, --help          Show this help message
# ------------------------------------------------------------------------------

set -euo pipefail

# Defaults
KERNEL="./vmlinuz"
INITRD="./initramfs.cpio.gz"
MEM="256M"
CPU="kvm64,smep=on,smap=off"
HDB="flag.txt"
APPEND="console=ttyS0 root=/dev/ram rw nopti nokaslr quiet panic=1"
QEMU="qemu-system-x86_64"

usage() {
    echo "Usage: $0 [options]"
    echo ""
    echo "Options:"
    echo "  --kernel PATH       Kernel image (default: $KERNEL)"
    echo "  --initrd PATH       Initramfs (default: $INITRD)"
    echo "  --mem SIZE          Memory size (default: $MEM)"
    echo "  --cpu STRING        QEMU CPU model (default: $CPU)"
    echo "  --hdb FILE          Second hard disk image (default: $HDB)"
    echo "  --append ARGS       Kernel cmdline (default: $APPEND)"
    echo "  -h, --help          Show this help message"
    exit 1
}

# Parse args
while [[ $# -gt 0 ]]; do
    case $1 in
        --kernel) KERNEL="$2"; shift 2 ;;
        --initrd) INITRD="$2"; shift 2 ;;
        --mem)    MEM="$2"; shift 2 ;;
        --cpu)    CPU="$2"; shift 2 ;;
        --hdb)    HDB="$2"; shift 2 ;;
        --append) APPEND="$2"; shift 2 ;;
        -h|--help) usage ;;
        *) echo "[!] Unknown option: $1"; usage ;;
    esac
done

[[ -f "$KERNEL" ]] || { echo "[!] Kernel not found: $KERNEL"; exit 1; }
[[ -f "$INITRD" ]] || { echo "[!] Initramfs not found: $INITRD"; exit 1; }
[[ -f "$HDB" ]]    || { echo "[!] hdb file not found: $HDB"; exit 1; }

echo "[*] Launching QEMU to test SMEP..."
echo "[*] Kernel : $KERNEL"
echo "[*] Initrd : $INITRD"
echo "[*] Memory : $MEM"
echo "[*] CPU    : $CPU"
echo "[*] HDB    : $HDB"
echo "[*] Append : $APPEND"

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
    #-serial stdio \
    -no-reboot

