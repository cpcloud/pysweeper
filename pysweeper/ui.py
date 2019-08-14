"""The urwid UI for PySweeper."""

import enum

from typing import Any, Callable, Tuple

import toolz
import urwid

from .pysweeper import Board, Coordinate, Tile


MINE_TILE = """\
╭───╮
│💣 │
╰───╯"""

NUMBERED_TILE = """\
╭───╮
│ {:d} │
╰───╯"""

EMPTY_TILE = """\
╭───╮
│   │
╰───╯"""

COVERED_TILE = """\
╭───╮
│▓▓▓│
╰───╯"""

FLAGGED_TILE = """\
╭───╮
│ ⛿ │
╰───╯"""


TileWidgetCallback = Callable[["TileWidget"], None]


class MouseButton(enum.Enum):
    """Named mouse button types."""

    LEFT = 1
    MIDDLE = 2
    RIGHT = 3
    SCROLL_UP = 4
    SCROLL_DOWN = 5


class TileWidget(urwid.WidgetWrap):
    """A PySweeper tile widget."""

    signals = ["left_click", "right_click"]

    def __init__(
        self,
        position: Coordinate,
        tile: Tile,
        on_left_click: TileWidgetCallback,
        on_right_click: TileWidgetCallback,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        self.position = position
        self.tile = tile
        self.text = urwid.Text(str(self), align=urwid.CENTER)
        self.on_left_click = on_left_click
        self.on_right_click = on_right_click
        super().__init__(self.text, *args, **kwargs)
        urwid.connect_signal(self, "left_click", self.on_left_click)
        urwid.connect_signal(self, "right_click", self.on_right_click)

    def disable(self) -> None:
        """Disable the tile."""
        urwid.disconnect_signal(self, "left_click", self.on_left_click)
        urwid.disconnect_signal(self, "right_click", self.on_right_click)

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
        """Do nothing on keypress."""
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
        if not self.selectable():
            return False
        if event != "mouse press":
            return False
        if button == MouseButton.LEFT.value:
            signal_name = "left_click"
        elif button == MouseButton.RIGHT.value:
            signal_name = "right_click"
        else:
            return False
        urwid.emit_signal(self, signal_name, self)
        return True

    def __str__(self) -> str:
        """Display the tile widget."""
        tile = self.tile

        # not exposed, so either a flag or a covered tile
        if not tile.exposed:
            if tile.flagged:
                return FLAGGED_TILE
            return COVERED_TILE

        # a mine
        if tile.mine:
            return MINE_TILE

        # numbered tile, indicating adjacent mine count or empty tile
        # indicating zero adjacent mines
        adjacent_mines = tile.adjacent_mines
        if not adjacent_mines:
            return EMPTY_TILE
        return NUMBERED_TILE.format(adjacent_mines)

    def redraw(self) -> None:
        """Redraw the widget."""
        self.text.set_text(str(self))


class PySweeperUI:
    """The urwid based UI class for PySweeper."""

    def __init__(self, rows: int, columns: int, mines: int) -> None:
        self.board = Board(rows, columns, mines)
        self.grid = [
            urwid.Columns(
                TileWidget(
                    tile=tile,
                    position=position,
                    on_left_click=self.on_left_click,
                    on_right_click=self.on_right_click,
                )
                for position, tile in chunk
            )
            for chunk in toolz.partition_all(columns, self.board.grid.items())
        ]
        self.widgets = {
            widget.position: widget
            for widget in toolz.concat(
                columns.widget_list for columns in self.grid
            )
        }
        self.info_header = urwid.Text(
            f"Flags: {self.board.available_flags:d}", align=urwid.CENTER
        )
        self.main_layout = urwid.Pile([self.info_header] + self.grid)
        self.loop = urwid.MainLoop(urwid.Filler(self.main_layout))

    def on_left_click(self, widget: TileWidget) -> None:
        """Expose `widget`."""
        assert not widget.exposed, "Widget is exposed"
        if not widget.flagged:
            for pos in self.board.expose(*widget.position):
                self.widgets[pos].redraw()

        widget.redraw()
        if widget.tile.mine and widget.exposed:
            self.expose_all()
            self.disable_all()
            self.info_header.set_text("You lose!")

    def on_right_click(self, widget: TileWidget) -> None:
        """Flag `widget`."""
        position = widget.position
        assert (
            not widget.exposed
        ), f"Tile at {position} is exposed when flagging"

        flagged = self.board.flag(*position)
        if flagged:
            if self.board.available_flags:
                widget.flagged = flagged
        else:
            widget.flagged = flagged
        self.info_header.set_text(f"Flags: {self.board.available_flags:d}")

        widget.redraw()
        if self.board.win:
            self.disable_all()
            self.info_header.set_text("You win!")

    def expose_all(self) -> None:
        """Expose every tile."""
        for position, tile in self.widgets.items():
            if not tile.exposed:
                self.board.expose(*position)
            tile.redraw()
            assert tile.exposed or tile.flagged

    def disable_all(self) -> None:
        """Disable all tiles."""
        for tile in self.widgets.values():
            tile.disable()

    def main(self) -> None:
        """Run the main loop of the game."""
        self.loop.run()
