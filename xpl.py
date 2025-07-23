#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Title : Linux Userland Pwn Exploit
# Author: Axura (@5xura) - https://4xura.com
#
# Description:
# ------------
# A Python script for Linux userland binex interaction
#
# TODO:
# -----
# - Add ld address brute force module 
# - Add some IO exploit helpers
#
# Usage:
# ------
# - Local mode  : ./xpl.py                
# - Remote mode : ./xpl.py [ <IP> <PORT> | <IP:PORT> ]
#

from pwn import *
import sys
import os
import inspect

s       = lambda data                 :io.send(data)
sa      = lambda delim,data           :io.sendafter(delim, data)
sl      = lambda data                 :io.sendline(data)
sla     = lambda delim,data           :io.sendlineafter(delim, data)
r       = lambda num=4096             :io.recv(num)
ru      = lambda delim, drop=True     :io.recvuntil(delim, drop)
uu64    = lambda data                 :u64(data.ljust(8, b"\0"))

# Utils
# ------------------------------------------------------------------------
def g(gdbscript: str = ""):
    if mode["local"]:
        gdb.attach(p, gdbscript=gdbscript)

    elif mode["remote"]:
        gdb.attach((remote_ip, remote_port), gdbscript)
        if gdbscript == "":
            raw_input()

def leak(addr: int) -> None:
    frame = inspect.currentframe().f_back
    variables = {k: v for k, v in frame.f_locals.items() if v is addr}
    desc = next(iter(variables.keys()), "unknown")
    c_addr = f"\033[1;33m{addr:#x}\033[0m"
    success(f"Leak {desc:<16} addr: {c_addr}")

def itoa(a: int) -> bytes:
    return str(a).encode()

# Rop 
# ------------------------------------------------------------------------
class ROPGadgets:
    def __init__(self, libc: ELF, libc_base: int): 
        self.rop = ROP(libc)
        self.addr = lambda x: libc_base + self.rop.find_gadget(x)[0] if self.rop.find_gadget(x) else None

        self.ggs = {
            'p_rdi_r'       : self.addr(['pop rdi', 'ret']),
            'p_rsi_r'       : self.addr(['pop rsi', 'ret']),
            'p_rdx_rbx_r'   : self.addr(['pop rdx', 'pop rbx', 'ret']),
            'p_rax_r'       : self.addr(['pop rax', 'ret']),
            'p_rsp_r'       : self.addr(['pop rsp', 'ret']),
            'leave_r'       : self.addr(['leave', 'ret']),
            'ret'           : self.addr(['ret']),
            'syscall_r'     : self.addr(['syscall', 'ret']),
        }

    def __getitem__(self, k: str) -> int:
        return self.ggs.get(k)

# Protected Pointers
# ------------------------------------------------------------------------
# - Mangle/demangle glibc pointers with per-process TCB guard & bit rotation
class PointerGuard:
    def __init__(self, guard: int, shift: int = 0x11, bit_size: int = 64):
        self.guard = guard
        self.shift = shift
        self.bits = bit_size
        self.mask = (1 << bit_size) - 1

    def rol(self, val: int) -> int:
        return ((val << self.shift) | (val >> (self.bits - self.shift))) & self.mask

    def ror(self, val: int) -> int:
        return ((val >> self.shift) | (val << (self.bits - self.shift))) & self.mask

    def mangle(self, ptr: int) -> int:
        return self.rol(ptr ^ self.guard)

    def demangle(self, mangled: int) -> int:
        return self.ror(mangled) ^ self.guard

# - Encrypt/decrypt fd pointer in single link list (e.g. tcache, fast)
class SafeLinking:
    def __init__(self, heap_base: int):
        self.heap_base = heap_base

    def encrypt(self, fd: int) -> int:
        return fd ^ (self.heap_base >> 12)

    def decrypt(self, enc_fd: int) -> int:
        key = 0
        plain = 0
        for i in range(1, 6):
            bits = 64 - 12 * i
            if bits < 0:
                bits = 0
            plain = ((enc_fd ^ key) >> bits) << bits
            key = plain >> 12
        return plain

# Heap exploit
# ------------------------------------------------------------------------
def menu(n: int):
    opt = itoa(n)
    pass

def add():
    pass

def free():
    pass

def edit():
    pass

def show():
    pass

# Exploit entry
# ------------------------------------------------------------------------
def xpl():





    # pause()
    io.interactive()

if __name__ == '__main__':

    FILE_PATH = ""
    LIBC_PATH = ""

    context(arch="amd64", os="linux", endian="little")
    context.log_level = "debug"
    context.terminal  = ['tmux', 'splitw', '-h']    # ['<terminal_emulator>', '-e', ...]

    elf  = ELF(FILE_PATH, checksec=False)
    mode = {"local": False, "remote": False, }
    env  = None

    print("Usage: python3 xpl.py [<ip> <port> | <ip:port>]\n"
                "  - If no arguments are provided, runs in local mode (default).\n"
                "  - Provide <ip> and <port> to target a remote host.\n")

    if len(sys.argv) == 3:
        if LIBC_PATH:
            libc = ELF(LIBC_PATH)
        remote_ip, remote_port = sys.argv[1], int(sys.argv[2])
        io = remote(remote_ip_addr, remote_port)
        mode["remote"] = True

    elif len(sys.argv) == 2 and ':' in sys.argv[1]::
        if LIBC_PATH:
            libc = ELF(LIBC_PATH)
        remote_ip, remote_port = sys.argv[1].split(":")
        remote_port = int(remote_port)
        io = remote(remote_ip, remote_port)
        mode["remote"] = True

    elif len(sys.argv) == 1:
        if LIBC_PATH:
            libc = ELF(LIBC_PATH)
            env = {
                "LD_PRELOAD": os.path.abspath(LIBC_PATH),
                "LD_LIBRARY_PATH": os.path.dirname(os.path.abspath(LIBC_PATH))
            }
        io = process(FILE_PATH, env=env)
        mode["local"] = True
    else:
        print("[-] Error: Invalid arguments provided.")
        sys.exit(1)

    xpl()
