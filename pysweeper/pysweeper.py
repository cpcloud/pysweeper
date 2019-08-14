"""Sweep some mines, terminal style."""

from typing import MutableSet, Set, Tuple

import collections
import dataclasses
import math
import random


Coordinate = Tuple[int, int]


@dataclasses.dataclass
class Tile:
    """A minesweeper tile."""

    mine: bool = False
    exposed: bool = False
    flagged: bool = False
    adjacent_mines: int = 0


class Board:
    """A minesweeper board."""

    def __init__(self, nrows: int, ncolumns: int, nmines: int) -> None:
        self.nrows = nrows
        self.ncolumns = ncolumns
        self.grid = {
            (x, y): Tile() for x in range(nrows) for y in range(ncolumns)
        }
        for tile in random.choices(list(self.grid.values()), k=nmines):
            tile.mine = True
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
                adjacent = self.adjacent(x, y)
                adjacent_mines = sum(
                    grid[adj_coord].mine for adj_coord in adjacent
                )
                grid[coord].exposed = tile_exposed = (
                    not tile.mine and not tile.flagged
                )
                if tile_exposed:
                    exposed.add(coord)

                if adjacent_mines:
                    grid[coord].adjacent_mines = adjacent_mines
                else:
                    coordinates.extend(
                        coord for coord in adjacent if coord not in seen
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
