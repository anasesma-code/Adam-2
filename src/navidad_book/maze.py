"""Perfect-maze generation (iterative depth-first search) and solving.

Mazes are deterministic for a given seed, so the solutions page can rebuild
exactly the same mazes that were printed.
"""
import random
from collections import deque


class Maze:
    def __init__(self, cols, rows):
        self.cols, self.rows = cols, rows
        # open[(c, r)] = set of neighbouring cells reachable from (c, r)
        self.open = {(c, r): set() for c in range(cols) for r in range(rows)}

    def neighbours(self, cell):
        c, r = cell
        for dc, dr in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            n = (c + dc, r + dr)
            if n in self.open:
                yield n

    def connect(self, a, b):
        self.open[a].add(b)
        self.open[b].add(a)

    def solve(self, start, end):
        prev = {start: None}
        queue = deque([start])
        while queue:
            cur = queue.popleft()
            if cur == end:
                break
            for n in self.open[cur]:
                if n not in prev:
                    prev[n] = cur
                    queue.append(n)
        path, cur = [], end
        while cur is not None:
            path.append(cur)
            cur = prev[cur]
        return path[::-1]


def generate(cols, rows, seed):
    """Row 0 is the top row. Start = top-left cell, end = bottom-right."""
    rng = random.Random(seed)
    m = Maze(cols, rows)
    start = (0, 0)
    stack, seen = [start], {start}
    while stack:
        cur = stack[-1]
        options = [n for n in m.neighbours(cur) if n not in seen]
        if not options:
            stack.pop()
            continue
        nxt = rng.choice(options)
        m.connect(cur, nxt)
        seen.add(nxt)
        stack.append(nxt)
    return m
