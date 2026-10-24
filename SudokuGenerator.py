#!/usr/bin/env python3

################################################################
## CLI Wrapper for a Sudoku generator
##  by Chad Crawford, using code from Gareth Rees
################################################################

import random
from functools import *

## From Gareth Rees at https://codereview.stackexchange.com/a/88866
def make_board(m=3):
    """Return a random filled m**2 x m**2 Sudoku board."""
    n = m**2
    board = [[None for _ in range(n)] for _ in range(n)]

    def search(c=0):
        "Recursively search for a solution starting at position c."
        i, j = divmod(c, n)
        i0, j0 = i - i % m, j - j % m # Origin of mxm block
        numbers = list(range(1, n + 1))
        random.shuffle(numbers)
        for x in numbers:
            if (x not in board[i]                     # row
                and all(row[j] != x for row in board) # column
                and all(x not in row[j0:j0+m]         # block
                        for row in board[i0:i])):
                board[i][j] = x
                if c + 1 >= n**2 or search(c + 1):
                    return board
        else:
            # No number is valid in this cell: backtrack and try again.
            board[i][j] = None
            return None

    return search()

## CUSTOM CODE
if __name__ == '__main__':
    import json
    import argparse
    parser = argparse.ArgumentParser(description='Generates random Sudoku board configurations. Represented as a Python list of lists.')
    parser.add_argument('num_missing', type=int, help='Number of empty slots in the board. Must be less than 81.')
    parser.add_argument('--output_file', type=str, default='sudoku.json', help='File to write the board configuration to.')
    parser.add_argument('--block_size', type=int, default=3, help='Size of the blocks on the Sudoku board.')
    args = parser.parse_args()

    board = make_board(args.block_size)

    ms = int(pow(args.block_size, 2))
    indices = random.sample(list(range(ms * ms)), args.num_missing)
    for index in indices:
        r = int(index / ms)
        c = int(index % ms)
        board[r][c] = 0

    ## Write to file
    with open(args.output_file, 'w') as f:
        f.write(json.dumps(board))

    print("""Board written to '{0}'.

To read the file with Python, use the code:

import json
with open('{0}', 'r') as f:
    board = json.load(f)
""".format(args.output_file))
