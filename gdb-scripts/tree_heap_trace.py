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
    op, frames = None, []
    for ln in lines:
        m = OP_HDR.match(ln)
        if m:
            if op:
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
class Node(object):
    __slots__ = ('name', 'count', 'kids')
    def __init__(self, name):
        self.name  = name
        self.count = 0
        self.kids  = collections.OrderedDict()   # keep insertion order

def add_stack(root, rev_stack):
    # - Insert one stack (root→leaf) into tree, bumping counts
    node = root
    node.count += 1
    for frame in rev_stack:
        if frame not in node.kids:
            node.kids[frame] = Node(frame)
        node = node.kids[frame]
        node.count += 1

def print_tree(node, indent=''):
    # - Recursive pretty-printer (skip printing the artificial root)
    for i, (name, kid) in enumerate(node.kids.items()):
        branch = '└─ ' if i == len(node.kids) - 1 else '├─ '
        print(indent + branch + u'{} [{}]'.format(name, kid.count))
        next_indent = indent + ('   ' if i == len(node.kids) - 1 else '│  ')
        print_tree(kid, next_indent)

# Build tree
# ------------------------------------------------------------------------
roots = collections.defaultdict(lambda: Node('ROOT'))

with open(LOG) as fp:
    for op, frames in events(fp):
        if not frames:
            continue

        root_first = list(reversed(frames))      # #N … #0  →  root→leaf

        # - Optional: drop everything above main() 
        try:
            idx = root_first.index('main')
            root_first = root_first[idx:]        # start at main
        except ValueError:
            pass                                 # stacks that run before main

        add_stack(roots[op], trimmed)            # root→leaf

# Output
# ------------------------------------------------------------------------
for op in sorted(roots):
    root = roots[op]
    print('\n{}   ({} calls)'.format(op, root.count))
    print_tree(root)


