"""The urwid UI for PySweeper."""

import itertools

from typing import Any, Callable, Iterator, Optional, Sequence, Tuple, TypeVar

import urwid

from .pysweeper import Board, Coordinate, Tile

T = TypeVar("T", covariant=True)


def chunked(iterable: Sequence[T], nchunks: int) -> Iterator[Sequence[T]]:
    """Yield chunks of a sequence `iterable`."""
    for i in range(0, len(iterable), nchunks):
        yield iterable[i : i + nchunks]


MINE_TILE = """\
╭───╮
│💣 │
╰───╯"""

NUMBERED_TILE = """\
╭───╮
│ {} │
╰───╯"""

UNCOVERED_TILE = """\
╭───╮
│▓▓▓│
╰───╯"""

FLAGGED_TILE = """\
╭───╮
│ ⛿ │
╰───╯"""


TileWidgetCallback = Callable[["TileWidget"], None]


class TileWidget(urwid.WidgetWrap):
    """A PySweeper tile widget."""

    signals = ["click", "left_click", "right_click"]

    def __init__(
        self,
        position: Coordinate,
        tile: Tile,
        on_left_click: TileWidgetCallback,
        on_right_click: TileWidgetCallback,
        on_click: TileWidgetCallback,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        self.position = position
        self.tile = tile
        self.text = urwid.Text(str(self), align=urwid.CENTER)
        self.on_left_click = on_left_click
        self.on_right_click = on_right_click
        self.on_click = on_click
        super().__init__(self.text, *args, **kwargs)
        urwid.connect_signal(self, "left_click", self.on_left_click)
        urwid.connect_signal(self, "right_click", self.on_right_click)
        urwid.connect_signal(self, "click", self.on_click)

    def disable(self) -> None:
        urwid.disconnect_signal(self, "left_click", self.on_left_click)
        urwid.disconnect_signal(self, "right_click", self.on_right_click)
        urwid.disconnect_signal(self, "click", self.on_click)

    @property
    def exposed(self) -> bool:
        """Return whether this tile is exposed."""
        return self.tile.exposed

    @exposed.setter
    def exposed(self, exposed: bool) -> None:
        self.tile.exposed = exposed

    @property
    def flagged(self) -> bool:
        """Return whether this tile is flagged."""
        return self.tile.flagged

    @flagged.setter
    def flagged(self, flagged: bool) -> None:
        self.tile.flagged = flagged

    def selectable(self) -> bool:
        """Return whether the tile is selectable."""
        return not self.exposed

    def keypress(self, size: Tuple[int, ...], key: str) -> str:
        """Do nothing."""
        return key

    def mouse_event(
        self,
        size: Tuple[int, ...],
        event: str,
        button: int,
        col: int,
        row: int,
        focus: bool,
    ) -> bool:
        """Click on a tile."""
        if self.selectable():
            if event == "mouse press":
                if button == 1:
                    signal_name = "left_click"
                elif button == 3:
                    signal_name = "right_click"
                else:
                    return False
                urwid.emit_signal(self, signal_name, self)
                urwid.emit_signal(self, "click", self)
                return True
        return False

    def __str__(self) -> str:
        """Draw the tile."""
        tile = self.tile
        if not tile.exposed:
            if tile.flagged:
                return FLAGGED_TILE
            return UNCOVERED_TILE
        if tile.mine:
            return MINE_TILE
        adjacent_mines = tile.adjacent_mines
        if not adjacent_mines:
            return NUMBERED_TILE.format(" ")
        return NUMBERED_TILE.format(tile.adjacent_mines)

    def redraw(self) -> None:
        """Redraw the widget."""
        self.text.set_text(str(self))


class PySweeperUI:
    """The urwid based UI class for PySweeper."""

    def __init__(self, rows: int, columns: int, mines: int) -> None:
        self.board = Board(rows, columns, mines)
        self.grid = [
            urwid.Columns(
                [
                    TileWidget(
                        tile=tile,
                        position=position,
                        on_left_click=self.on_left_click,
                        on_right_click=self.on_right_click,
                        on_click=self.on_click,
                    )
                    for position, tile in chunk
                ]
            )
            for chunk in chunked(list(self.board.grid.items()), columns)
        ]
        self.widgets = {
            widget.position: widget
            for widget in itertools.chain.from_iterable(
                columns.widget_list for columns in self.grid
            )
        }
        self.info_header = urwid.Text(
            f"Flags: {self.board.available_flags:d}", align=urwid.CENTER
        )
        self.main_layout = urwid.Pile([self.info_header] + self.grid)
        self.lost = False
        self.loop = urwid.MainLoop(urwid.Filler(self.main_layout))

    def on_left_click(self, widget: TileWidget) -> None:
        """Expose `widget`."""
        assert not widget.exposed, "Widget is exposed"
        if not widget.flagged:
            for pos in self.board.expose(*widget.position):
                self.widgets[pos].redraw()

    def on_right_click(self, widget: TileWidget) -> None:
        """Expose `widget`."""
        assert not widget.exposed, "Widget is exposed when flagging"
        flagged = self.board.flag(*widget.position)
        if flagged:
            if self.board.available_flags:
                widget.flagged = flagged
        else:
            widget.flagged = flagged
        self.info_header.set_text(f"Flags: {self.board.available_flags:d}")

    def on_click(self, widget: TileWidget) -> None:
        """Redraw a widget on click."""
        widget.redraw()
        if widget.tile.mine and widget.exposed:
            self.disable()
            self.info_header.set_text("You lose!")
        elif self.board.win:  # all mines are flagged
            self.disable()
            self.info_header.set_text("You win!")

    def disable(self) -> None:
        """Disable tiles."""
        for tile in self.widgets.values():
            tile.disable()

    def main(self) -> None:
        """Run the main loop of the game."""
        self.loop.run()
