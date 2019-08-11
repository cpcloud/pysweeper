"""Game entry point."""

import click

from .ui import PySweeperUI


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
    ui = PySweeperUI(rows, columns, mines)
    ui.main()


if __name__ == "__main__":
    main()
