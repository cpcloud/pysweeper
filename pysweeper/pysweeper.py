"""Sweep some mines, terminal style."""

from typing import FrozenSet, MutableSet, Set, Tuple

import collections
import dataclasses
import itertools
import math
import random


Coordinate = Tuple[int, int]


@dataclasses.dataclass
class Tile:
    """A minesweeper tile."""

    adjacent_tiles: FrozenSet[Coordinate]
    mine: bool = False
    exposed: bool = False
    flagged: bool = False
    adjacent_mines: FrozenSet[Coordinate] = frozenset()


def adjacent(
    i: int, j: int, nrows: int, ncolumns: int
) -> FrozenSet[Coordinate]:
    """Compute the tiles that are adjacent to the tile at `i`, `j`."""
    increments = 1, -1, 0
    return frozenset(
        (i + x, j + y)
        for x in increments
        for y in increments
        if x or y
        if 0 <= i + x < nrows
        if 0 <= j + y < ncolumns
    )


class Board:
    """A minesweeper board."""

    def __init__(self, nrows: int, ncolumns: int, nmines: int) -> None:
        self.nrows = nrows
        self.ncolumns = ncolumns
        self.grid = {
            (x, y): Tile(adjacent_tiles=adjacent(x, y, nrows, ncolumns))
            for i, (x, y) in enumerate(
                itertools.product(range(nrows), range(ncolumns))
            )
        }
        for tile in random.choices(list(self.grid.values()), k=nmines):
            tile.mine = True
        for tile in self.grid.values():
            tile.adjacent_mines = frozenset(
                coord for coord in tile.adjacent_tiles if self.grid[coord].mine
            )
        self.nmines = nmines
        self.nflagged = 0

    @property
    def unexposed_tiles(self) -> int:
        """Return the number of unexposed tiles."""
        return self.ntiles - self.nmines

    @property
    def available_flags(self) -> int:
        """Return the number of available_flags."""
        return self.nmines - self.nflagged

    @property
    def ntiles(self) -> int:
        """Return the total number of tiles on the board."""
        return self.nrows * self.ncolumns

    @property
    def total_exposed(self) -> int:
        """Return the total number of tiles exposed."""
        return sum(tile.exposed for tile in self.grid.values())

    @property
    def win(self) -> bool:  # noqa: D213
        """Return whether the game is won.

        The game is won when all mines are correctly flagged and all tiles
        are exposed.

        """
        correctly_flagged_mines = sum(
            tile.flagged and tile.mine for tile in self.grid.values()
        )
        exposed_or_correctly_flagged = (
            self.total_exposed + correctly_flagged_mines
        )
        assert exposed_or_correctly_flagged <= self.ntiles
        return self.ntiles == exposed_or_correctly_flagged

    def expose(self, i: int, j: int) -> Set[Coordinate]:  # noqa: D213
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

        # return early if we exposed a mine
        if grid[i, j].mine:
            grid[i, j].exposed = True
            return {(i, j)}

        seen: MutableSet[Coordinate] = set()
        coordinates = collections.deque([(i, j)])
        exposed = set()

        while coordinates:
            coord = coordinates.popleft()
            x, y = coord
            tile = grid[x, y]
            if coord not in seen:
                seen.add(coord)
                grid[coord].exposed = tile_exposed = not (
                    tile.mine or tile.flagged
                )
                if tile_exposed:
                    exposed.add(coord)

                if not tile.adjacent_mines:
                    coordinates.extend(
                        coord
                        for coord in tile.adjacent_tiles
                        if coord not in seen
                    )
        return exposed

    def flag(self, i: int, j: int) -> bool:
        """Flag the tile at coordinate `i`, `j`."""
        grid = self.grid
        tile = grid[i, j]
        was_flagged = tile.flagged
        flagged = not was_flagged

        if was_flagged:
            if self.nflagged - 1 >= 0:
                grid[i, j].flagged = flagged
                self.nflagged -= 1
        else:
            if self.nflagged + 1 <= self.nmines and not tile.exposed:
                grid[i, j].flagged = flagged
                self.nflagged += 1
        return flagged
