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

# Parse log
# ------------------------------------------------------------------------
# Yield (operation, frame_list) blocks
def events(lines):
    """Yield (operation, [frames…]) tuples in the order they appear."""
    op, frames = None, []
    for ln in lines:
        m = OP_HDR.match(ln)
        if m:
            if op:                                 # flush previous block
                yield op, frames
            op, frames = m.group(1), []
            continue
        m = FRAME.match(ln)
        if m:
            frames.append(m.group(1).rstrip())
    if op:
        yield op, frames

# Tree model
# ------------------------------------------------------------------------
class Node:
    __slots__ = ('name', 'count', 'kids')
    def __init__(self, name):
        self.name  = name
        self.count = 0
        self.kids  = collections.OrderedDict()

def add_stack(root, stack):
    """Insert one root→leaf stack into the tree, bumping counts."""
    node = root
    node.count += 1
    for frame in stack:
        if frame not in node.kids:
            node.kids[frame] = Node(frame)
        node               = node.kids[frame]
        node.count        += 1

def print_tree(node, indent=''):
    kids = sorted(node.kids.values(), key=lambda k: -k.count)  # hot first
    for i, kid in enumerate(kids):
        branch = '└─ ' if i == len(kids) - 1 else '├─ '
        print(indent + branch + '{} [{}]'.format(kid.name, kid.count))
        next_indent = indent + ('   ' if i == len(kids) - 1 else '│  ')
        print_tree(kid, next_indent)

def trim_stack(frames):
    """Return frames in caller→callee order, pruned of obvious junk."""
    frames = list(reversed(frames))           # #N … #0  →  root→leaf

    # keep only from the first 'main' downward, if present
    try:
        frames = frames[frames.index('main'):]
    except ValueError:
        pass

    # cut when a frame repeats within the same trace (loop protection)
    seen, out = set(), []
    for fr in frames:
        if fr in seen:
            break
        seen.add(fr)
        out.append(fr)
    return out if out else ['«empty-stack»']

# Build tree
# ------------------------------------------------------------------------
roots = collections.defaultdict(lambda: Node('ROOT'))

with open(LOG, 'r', errors='replace') as fp:
    for op, raw in events(fp):
        stack = trim_stack(raw)
        if not stack or stack[0] == 'main':           # “normal” stacks
            add_stack(roots[op], stack)
        else:                                         # pre-main activity
            add_stack(roots['pre-main-' + op], stack)

# Output
# ------------------------------------------------------------------------
for op in sorted(roots):
    root = roots[op]
    print('\n{}   ({} calls)'.format(op, root.count))
    print_tree(root)


