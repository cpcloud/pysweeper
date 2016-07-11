#!/usr/bin/env python

import os

from .pysweeper import Grid


def clear():
    os.system('cls' if os.name=='nt' else 'clear')


def main(nrows, ncolumns, nmines):
    grid = Grid(nrows, ncolumns, nmines)
    found_bomb = False
    total_exposed = 0
    while not found_bomb and total_exposed != len(grid.grid) - grid.bomb_count:
        clear()
        print(grid)
        action = input('[E]xpose or [F]lag (\u2691 {})? '.format(grid.bomb_count - grid.num_flagged)).upper()
        if action != 'E' and action != 'F':
            print('action must be either E or F')
        else:
            coord = input('Coordinate to act on (0-based): ').strip()
            i, j = map(int, re.split('(?:\s*,\s*)|(?:\s+)', coord))
            method = grid.expose if action == 'E' else grid.flag
            exposed = method(i, j)
            total_exposed += exposed
            found_bomb = exposed == -1

    print(grid)

    if found_bomb:
        print('You lost!')

    if grid.num_flagged == grid.bomb_count or total_exposed == len(grid.grid) - grid.bomb_count:
        print('Epic win!')

    return grid


if __name__ == '__main__':
    import argparse
    p = argparse.ArgumentParser()

    p.add_argument('-r', '--rows', default=9, type=int)
    p.add_argument('-c', '--columns', default=9, type=int)
    p.add_argument('-m', '--mines', default=10, type=int)

    args = p.parse_args()

    assert args.mines <= args.rows * args.columns, \
        'number of mines must be less than the total number of tiles'

    grid = main(args.rows, args.columns, args.mines)
