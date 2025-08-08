#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Title		: Build A Calltree from A Heap Trace Log
# Date		: 2025-08-08
# Author	: Axura (@4xura) - https://4xura.com
# Version	: Python 3.5+
#
# Description:
# ------------
# Build a per-operation call tree from a GDB heap_trace.log produced by
# heap_trace.gdb
#
# TODO:
# -----
# - Improve regex
#
# Usage:
# ------
# python3 tree_heap_trace.py heap_trace.log  > calltree.txt
#

from __future__ import print_function
import re, sys, collections, pathlib                 # itertools was unused

LOG = sys.argv[1] if len(sys.argv) == 2 else None
if not LOG or not pathlib.Path(LOG).is_file():
    sys.exit("usage: tree_heap_trace.py <heap_trace.log>")

# Regex
# ------------------------------------------------------------------------
# - Extract frames from MALLOC, CALLOC … banners, keeping full tail
OP_HDR = re.compile(r'^========= \[([A-Z]+)\]')
# - Capture up to the first " ("  or the end of line, discarding args
FRAME  = re.compile(r'^#\d+\s+\S+\s+in\s+([^( \t]+)')

# Helpers
# ------------------------------------------------------------------------
class Node:
    __slots__ = ('name', 'count', 'kids')
    def __init__(self, name):
        self.name  = name
        self.count = 0
        self.kids  = collections.OrderedDict()

def add_stack(root, stack):                  # stack == root→leaf
    node = root
    node.count += 1
    for f in stack:
        node = node.kids.setdefault(f, Node(f))
        node.count += 1

def print_tree(node, indent=''):
    for i, (name, kid) in enumerate(node.kids.items()):
        branch = '└─ ' if i == len(node.kids)-1 else '├─ '
        print(indent + branch + '{} [{}]'.format(name, kid.count))
        print_tree(kid, indent + ('   ' if i == len(node.kids)-1 else '│  '))

# Parse & Build
# ------------------------------------------------------------------------
roots = collections.defaultdict(lambda: Node('ROOT'))

with open(LOG) as fp:
    op, frames = None, []
    for ln in fp:
        hdr = OP_HDR.match(ln)
        if hdr:                                            # banner line
            if op and frames:
                # ---------- finish previous event -------------------------#
                # trim everything *above* main() if main is present
                if 'main' in frames:
                    frames = frames[:frames.index('main')+1]
                add_stack(roots[op], reversed(frames))     # root→leaf
            op, frames = hdr.group(1), []
            continue
        fr = FRAME.match(ln)
        if fr:
            frames.append(fr.group(1).rstrip())

    # last event in file
    if op and frames:
        if 'main' in frames:
            frames = frames[:frames.index('main')+1]
        add_stack(roots[op], reversed(frames))

# Output
# ------------------------------------------------------------------------
for op in sorted(roots):
    root = roots[op]
    print('\n{}   ({} calls)'.format(op, root.count))
    print_tree(root)


