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
import re, sys, collections, pathlib                 

LOG = sys.argv[1] if len(sys.argv) == 2 else None
if not LOG or not pathlib.Path(LOG).is_file():
    sys.exit("usage: tree_heap_trace.py <heap_trace.log>")

# Regex
# ------------------------------------------------------------------------
# - Extract frames from MALLOC, CALLOC … banners, keeping full tail
OP_HDR = re.compile(r'^========= \[([A-Z]+)\]')
# - Capture up to the first " ("  or the end of line, discarding args
FRAME  = re.compile(r'^#\d+\s+\S+\s+in\s+([^( \t]+)')

# Generator
# ------------------------------------------------------------------------
def events(lines):
    op, frames = None, []
    for ln in lines:
        m = OP_HDR.match(ln)
        if m:                                            # new operation header
            if op is not None:
                yield op, frames
            op, frames = m.group(1), []
            continue

        m = FRAME.match(ln)
        if m:
            frames.append(m.group(1))
    if op is not None:
        yield op, frames

# Tree model
# ------------------------------------------------------------------------
class Node(object):
    __slots__ = ('name', 'count', 'kids')
    def __init__(self, name):
        self.name  = name
        self.count = 0
        self.kids  = collections.OrderedDict()   # preserves first-seen order


def add_stack(root, stack):
    """
    Insert one call-stack (root ➜ leaf order) under *root*,
    incrementing counters along the way.
    """
    node = root
    node.count += 1
    for frame in stack:
        if frame not in node.kids:
            node.kids[frame] = Node(frame)
        node = node.kids[frame]
        node.count += 1


def print_tree(node, indent=''):
    """
    Pretty-print the tree (depth-first).
    The artificial ROOT is never printed, only its children.
    """
    last_idx = len(node.kids) - 1
    for i, (name, kid) in enumerate(node.kids.items()):
        branch = '└─ ' if i == last_idx else '├─ '
        print(indent + branch + '{} [{}]'.format(name, kid.count))
        next_indent = indent + ('   ' if i == last_idx else '│  ')
        print_tree(kid, next_indent)

# Parse & Build
# ------------------------------------------------------------------------
roots = collections.defaultdict(lambda: Node('ROOT'))

with open(LOG, 'r', encoding='utf-8', errors='replace') as fp:
    for op, frames in events(fp):
        # Keep only the segment from main() (inclusive) down to #0
        if 'main' not in frames:
            continue                      # ignore pre-main noise
        cut = frames.index('main') + 1    # frames[cut:] are above main()
        pruned = frames[:cut]             # #0 … main
        add_stack(roots[op], reversed(pruned))   # store as root→leaf

# Output
# ------------------------------------------------------------------------
for op in sorted(roots):
    root = roots[op]
    print('\n{}   ({} calls)'.format(op, root.count))
    print_tree(root)


