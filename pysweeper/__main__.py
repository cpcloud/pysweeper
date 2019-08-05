"""Game entry point."""

import re
import sys

import click

from .pysweeper import Grid


@click.command()
@click.option(
    "-r",
    "--rows",
    type=int,
    default=9,
    help="The number of rows in the grid.",
    show_default=True,
)
@click.option(
    "-c",
    "--columns",
    type=int,
    default=9,
    help="The number of columns in the grid.",
    show_default=True,
)
@click.option(
    "-m",
    "--mines",
    type=int,
    default=10,
    help="The number of mines in the grid.",
    show_default=True,
)
def main(rows: int, columns: int, mines: int) -> None:
    """Your favorite sweeping game, terminal style."""
    tiles = rows * columns
    if mines > tiles:
        raise click.ClickException(
            "Number of mines must be less than the total number of tiles "
            f"({tiles:d})"
        )
    grid = Grid(rows, columns, mines)
    found_mine = False
    total_exposed = 0
    method_map = {"E": grid.expose, "F": grid.flag}
    while total_exposed != len(grid) - grid.mine_count:
        click.clear()
        click.echo(grid)
        action = input(
            f"[E]xpose or [F]lag (\u2691 {grid.available_flags:d})? "
        ).upper()
        if action == "Q":
            return
        if action == "E" or action == "F":
            coord = input("Coordinate to act on (0-based): ").strip()
            i, j = map(int, re.split(r"(?:\s*,\s*)|(?:\s+)", coord))
            exposed = method_map[action](i, j)
            found_mine = exposed == -1
            if found_mine:
                click.echo(grid)
                click.echo("You lose!")
                return
            else:
                total_exposed += exposed

    if grid.num_flagged == grid.mine_count or (
        total_exposed == len(grid) - grid.mine_count
    ):
        click.echo(grid)
        click.echo("You win!")


if __name__ == "__main__":
    main()
