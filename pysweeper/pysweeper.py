"""Sweep some mines, terminal style."""

from typing import List, MutableSet, Optional, Set, Tuple

import collections
import dataclasses
import math
import random


Coordinate = Tuple[int, int]


@dataclasses.dataclass
class Tile:
    """A minesweeper tile."""

    exposed: bool = False
    flagged: bool = False
    content: Optional[int] = None

    def __str__(self) -> str:
        if self.content is not None:
            return str(self.content)
        if self.exposed:
            assert (
                not self.flagged
            ), "{} instance cannot be both exposed and flagged".format(
                type(self).__name__
            )
        if not self.exposed:
            return "\u2691" if self.flagged else "\u25A0"
        else:
            return "\u25A1"


@dataclasses.dataclass
class Mine(Tile):
    """A minesweeper mine."""

    def __str__(self) -> str:
        return "\u2600" if self.exposed else super().__str__()


def random_points(n: int, m: int) -> List[Coordinate]:
    r"""Return a list of coordinates of size :math:`n \times m`."""
    points = [(x, y) for x in range(n) for y in range(m)]
    random.shuffle(points)
    return points


class Grid:
    """A minesweeper grid."""

    def __init__(self, nrows: int, ncolumns: int, mine_count: int) -> None:
        self.nrows = nrows
        self.ncolumns = ncolumns
        self.grid = {
            point: Mine() if i < mine_count else Tile()
            for i, point in enumerate(random_points(nrows, ncolumns))
        }
        self.mine_count = mine_count
        self.num_flagged = 0

    @property
    def available_flags(self) -> int:
        """Return the number of available_flags."""
        return self.mine_count - self.num_flagged

    def __len__(self) -> int:
        return len(self.grid)

    def __str__(self) -> str:
        nrows = self.nrows
        ncolumns = self.ncolumns
        nspaces = max(
            math.ceil(math.log10(nrows)), math.ceil(math.log10(ncolumns))
        )
        padding = " " * nspaces
        rows = [
            "{}{}".format(
                padding,
                " ".join(str(i).rjust(nspaces + 1) for i in range(ncolumns)),
            )
        ]
        grid = self.grid
        rows.extend(
            "{}{}".format(
                str(i).rjust(nspaces),
                " ".join(f"{padding}{grid[i, j]}" for j in range(ncolumns)),
            )
            for i in range(nrows)
        )
        return "\n".join(rows)

    def adjacent(self, i: int, j: int) -> Set[Coordinate]:
        """Compute the tiles that are adjacent to the tile at `i`, `j`."""
        increments = 1, -1, 0
        nrows = self.nrows
        ncolumns = self.ncolumns
        return {
            (i + x, j + y)
            for x in increments
            for y in increments
            if x or y
            if 0 <= i + x < nrows
            if 0 <= j + y < ncolumns
        }

    def expose(self, i: int, j: int) -> int:  # noqa: D213
        """Tile exposure algorithm.

        Treat the grid as graph.

        Nodes are tiles, edges are between nodes that are immediately adjacent.

        * If we're a mine, fail
        * Else expose the current tile
        * Count the number of adajacent tiles that are mines. 
        * If the count is > 0, then replace that tile with a CountedTile
        2. For every adjacent tile, if any adjacent tiles are mines, halt
        3. Else expose the tile

        """
        grid = self.grid
        if isinstance(grid[i, j], Mine):
            grid[i, j].exposed = True
            return -1

        seen: MutableSet[Coordinate] = set()
        coordinates = collections.deque([(i, j)])
        exposed = 0

        while coordinates:
            coord = coordinates.popleft()
            x, y = coord
            tile = grid[x, y]
            if coord not in seen:
                seen.add(coord)
                adjacent = self.adjacent(x, y)
                adjacent_mines = sum(
                    isinstance(grid[adj_coord], Mine) for adj_coord in adjacent
                )
                grid[coord].exposed = tile_exposed = not isinstance(tile, Mine)
                exposed += tile_exposed

                if adjacent_mines:
                    grid[coord].content = adjacent_mines
                else:
                    coordinates.extend(
                        coord for coord in adjacent if coord not in seen
                    )
        return exposed

    def flag(self, i: int, j: int) -> int:
        """Flag the tile at coordinate `i`, `j`."""
        grid = self.grid
        tile = grid[i, j]
        was_flagged = tile.flagged
        flagged = not was_flagged

        if was_flagged:
            if self.num_flagged - 1 >= 0:
                grid[i, j].flagged = flagged
                self.num_flagged -= 1
        else:
            if self.num_flagged + 1 <= self.mine_count and not tile.exposed:
                grid[i, j].flagged = flagged
                self.num_flagged += 1
        return 0
