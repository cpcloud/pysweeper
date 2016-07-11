#!/usr/bin/env python

import random

from math import ceil, log10

from collections import deque
from itertools import product


class Tile(object):

    def __init__(self, exposed, flagged, content):
        self.exposed = exposed
        self.flagged = flagged
        self.content = content

    def __str__(self):
        if self.content is not None:
            return str(self.content)
        if self.exposed:
            assert not self.flagged, 'Cannot be both exposed and flagged'
        if not self.exposed:
            return '\u2691' if self.flagged else '\u25A0'
        else:
            return '\u25A1'


class Bomb(Tile):
    def __str__(self):
        return '\u2600' if self.exposed else super(Bomb, self).__str__()


def random_points(n, m, k):
    points = list(product(range(n), range(m)))
    random.shuffle(points)
    return points


class Grid(object):

    def __init__(self, nrows, ncolumns, bomb_count):
        self.nrows = nrows
        self.ncolumns = ncolumns
        self.grid = {
            (i, j): (
                Bomb(False, False, None)
                if k < bomb_count else Tile(False, False, None)
            )
            for k, (i, j) in enumerate(
                random_points(nrows, ncolumns, bomb_count)
            )
        }
        self.bomb_count = bomb_count
        self.num_flagged = 0

    def __str__(self):
        nspaces = max(ceil(log10(self.nrows)), ceil(log10(self.ncolumns)))
        padding = ' ' * nspaces
        rows = [
            padding + ' '.join(
                '{:>{}}'.format(i, nspaces + 1) for i in range(self.ncolumns)
            )
        ]
        for i in range(self.nrows):
            rows.append(
                '{:>{}}{}'.format(
                    i,
                    nspaces,
                    ' '.join(
                        padding + str(self.grid[i, j])
                        for j in range(self.ncolumns)
                    )
                )
            )
        return '\n'.join(rows)

    def adjacent(self, i, j, types=(Tile,)):
        increments = 1, -1, 0

        return {
            (i + x, j + y): self.grid[i + x, j + y]
            for x, y in product(increments, repeat=2)
            if (
                (x or y) and
                0 <= i + x < self.nrows and
                0 <= j + y < self.ncolumns and
                isinstance(self.grid[i + x, j + y], types)
            )
        }

    def expose(self, i, j):
        """Exposure algorithm.

        Treat the grid as graph, where nodes are tiles and edges are links to
        immediately adjacent nodes.

        * If we're a bomb, fail
        * Else expose the current tile
        * Count the number of adajacent tiles that are bombs
        * If the count is > 0, then replace that tile with a CountedTile
        2. For every adjacent tile, if any adjacent tiles are bombs, halt
        3. Else expose the tile
        """
        if isinstance(self.grid[i, j], Bomb):
            self.grid[i, j].exposed = True
            return -1

        seen = set()
        c = deque([((i, j), self.grid[i, j])])
        exposed = 0

        while c:
            (x, y), tile = c.popleft()
            if (x, y) not in seen:
                seen.add((x, y))
                adjacent = self.adjacent(x, y)
                n_adjacent_bombs = sum(
                    isinstance(t, Bomb) for t in adjacent.values()
                )
                tile_exposed = not isinstance(tile, Bomb)
                self.grid[x, y].exposed = tile_exposed
                exposed += tile_exposed

                if n_adjacent_bombs:
                    self.grid[x, y].content = n_adjacent_bombs
                else:
                    c.extend(
                        (coord, tile) for coord, tile in adjacent.items()
                        if coord not in seen
                    )
        return exposed

    def flag(self, i, j):
        node = self.grid[i, j]
        was_flagged = node.flagged
        new_flagged = not was_flagged

        if was_flagged:
            if self.num_flagged - 1 >= 0:
                self.grid[i, j].flagged = new_flagged
                self.num_flagged -= 1
        else:
            if self.num_flagged + 1 <= self.bomb_count and not node.exposed:
                self.grid[i, j].flagged = new_flagged
                self.num_flagged += 1
        return False
