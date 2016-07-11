#!/usr/bin/env python

"""
Main game control
"""

from __future__ import absolute_import, division, print_function

import sys
import re

from .pysweeper import Grid


def clear():
    sys.stderr.write("\x1b[2J\x1b[H")
    sys.stderr.flush()


def play(nrows, ncolumns, nmines):
    grid = Grid(nrows, ncolumns, nmines)
    found_bomb = False
    total_exposed = 0
    while not found_bomb and total_exposed != len(grid.grid) - grid.bomb_count:
        clear()
        print(grid)
        action = input(
            '[E]xpose or [F]lag (\u2691 {})? '.format(
                grid.bomb_count - grid.num_flagged
            )
        ).upper()
        if action != 'E' and action != 'F':
            print('action must be either E or F')
        else:
            coord = input('Coordinate to act on (0-based): ').strip()
            i, j = map(int, re.split(r'(?:\s*,\s*)|(?:\s+)', coord))
            method = grid.expose if action == 'E' else grid.flag
            exposed = method(i, j)
            total_exposed += exposed
            found_bomb = exposed == -1


    if found_bomb:
        print(grid)
        print('You lost!')

    if grid.num_flagged == grid.bomb_count or (
        total_exposed == len(grid.grid) - grid.bomb_count
    ):
        print(grid)
        print('Epic win!')

    return grid


def main():
    """Main entry point for the game
    """
    import argparse
    parser = argparse.ArgumentParser()

    parser.add_argument('-r', '--rows', default=9, type=int)
    parser.add_argument('-c', '--columns', default=9, type=int)
    parser.add_argument('-m', '--mines', default=10, type=int)

    args = parser.parse_args()

    assert args.mines <= args.rows * args.columns, \
        'number of mines must be less than the total number of tiles'

    grid = play(args.rows, args.columns, args.mines)
    return grid


if __name__ == '__main__':
    main()
