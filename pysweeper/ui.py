"""The PySweeper UI."""

from typing import Any, Callable, Iterable, Tuple, Union

import toolz
import urwid

from .pysweeper import Board, Coordinate, Tile


MINE_TILE = "💣"
NUMBERED_TILE = "{:d}"
EMPTY_TILE = " "
UNCOVERED_TILE = "▓"
FLAGGED_TILE = "⛿"


TileWidgetCallback = Callable[["TileWidget"], None]


class TileWidget(urwid.WidgetWrap):
    """A PySweeper tile widget."""

    signals = ["left_click", "right_click"]

    WIDTH = 5

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
        self.widget = urwid.AttrMap(
            urwid.Text(self.text, align=urwid.CENTER), "unexposed", "unexposed"
        )
        self.on_left_click = on_left_click
        self.on_right_click = on_right_click
        super().__init__(self.widget, *args, **kwargs)
        urwid.connect_signal(self, "left_click", self.on_left_click)
        urwid.connect_signal(self, "right_click", self.on_right_click)

    def disable(self) -> None:
        """Disable the tile.

        Called when the game is finished.

        """
        urwid.disconnect_signal(self, "left_click", self.on_left_click)
        urwid.disconnect_signal(self, "right_click", self.on_right_click)

    @property
    def exposed(self) -> bool:
        """Return whether this tile is exposed."""
        return self.tile.exposed

    @exposed.setter
    def exposed(self, exposed: bool) -> None:
        """Set the tile exposure state to `exposed`."""
        self.tile.exposed = exposed

    @property
    def flagged(self) -> bool:
        """Return whether this tile is flagged."""
        return self.tile.flagged

    @flagged.setter
    def flagged(self, flagged: bool) -> None:
        """Set the tile flagged state to `flagged`."""
        self.tile.flagged = flagged

    def selectable(self) -> bool:
        """Return whether the tile is selectable.

        A tile is selectable if it is not :attr:`exposed`.

        """
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
        """React to a click on a tile."""
        if self.selectable():
            if event == "mouse press":
                if button == 1:
                    signal_name = "left_click"
                elif button == 3:
                    signal_name = "right_click"
                else:
                    return False
                urwid.emit_signal(self, signal_name, self)
                return True
        return False

    @property
    def text(self) -> str:
        """Produce text needed for display."""
        tile = self.tile
        if not tile.exposed:
            if tile.flagged:
                return FLAGGED_TILE
            return UNCOVERED_TILE
        if tile.mine:
            return MINE_TILE
        adjacent_mines = tile.adjacent_mines
        if not adjacent_mines:
            return EMPTY_TILE
        return NUMBERED_TILE.format(adjacent_mines)

    @property
    def palette_member(self) -> str:
        tile = self.tile
        if not tile.exposed:
            if tile.flagged:
                return "flagged"
            return "unexposed"
        if tile.mine:
            return "mine"
        adjacent_mines = tile.adjacent_mines
        if not adjacent_mines:
            return "empty"
        return "bright"

    def redraw(self) -> None:
        """Redraw the widget."""
        self.widget.original_widget.set_text(self.text)
        self.widget.set_attr_map({None: self.palette_member})


PALETTE = [
    ("flagged", "default", "default"),
    ("unexposed", "dark cyan", "default"),
    ("mine", "standout", ""),
    ("empty", "default", "default"),
    ("bright", "dark cyan,bold", "default"),
]


class PySweeperUI:
    """The urwid-based UI for PySweeper."""

    def __init__(self, rows: int, columns: int, mines: int) -> None:
        self.board = Board(rows, columns, mines)
        self.grid = [
            urwid.Columns(
                [
                    urwid.LineBox(
                        TileWidget(
                            tile=tile,
                            position=position,
                            on_left_click=self.on_left_click,
                            on_right_click=self.on_right_click,
                        ),
                        tlcorner="╭",
                        tline="┈",
                        lline="┊",
                        trcorner="╮",
                        blcorner="╰",
                        rline="┊",
                        bline="┈",
                        brcorner="╯",
                    )
                    for position, tile in chunk
                ]
            )
            for chunk in toolz.partition_all(columns, self.board.grid.items())
        ]
        self.widgets = {
            widget.base_widget.position: widget.base_widget
            for widget in toolz.concat(
                columns.widget_list for columns in self.grid
            )
        }
        self.info_header = urwid.Text(
            f"Flags: {self.board.available_flags:d}", align=urwid.CENTER
        )
        all_widgets = [self.info_header] + self.grid
        pile = urwid.Padding(
            urwid.Pile(all_widgets), align=urwid.CENTER, width=("relative", 30)
        )
        top = urwid.Filler(pile)
        self.loop = urwid.MainLoop(top, PALETTE, unhandled_input=self.exit)

    def exit(self, key: Union[Tuple[str, int, int, int], str]) -> None:
        if isinstance(key, str):
            lowered = key.lower()
            if lowered == "q":
                raise urwid.ExitMainLoop()

    def expose(self, i: int,  j: int) -> Set[Coordinate]:
        return

    def on_left_click(self, widget: TileWidget) -> None:
        """Expose `widget`."""
        assert not widget.exposed, "Widget is exposed"
        if widget.tile.mine and widget.exposed:
            self.disable()
            self.board.expose_all()
            self.redraw(self.widgets.keys())
            self.info_header.set_text("You lose!")
        else:
            if not widget.flagged:
                i, j = widget.position
                self.redraw(self.board.expose(i, j))

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
        if self.board.win:
            self.disable()
            self.info_header.set_text("You win!")

    def redraw(self, positions: Iterable[Coordinate]) -> None:
        for position in positions:
            self.widgets[position].redraw()

    def disable(self) -> None:
        """Disable tiles."""
        for tile in self.widgets.values():
            tile.disable()

    def main(self) -> None:
        """Run the main loop of the game."""
        self.loop.run()
