"""
tetris_logic.py
----------------
This file holds the "brain" of the Tetris game: the rules for how pieces
move, rotate, land, and clear lines. It has NO drawing code in it at all,
so you (or a program) can test it without opening any window.

The actual drawing and keyboard handling live in tetris.py, which imports
everything from this file.

CONCEPTS USED IN THIS FILE (look for the tag in the comments):
    [STRING]      text values, like piece names and colors
    [LIST]        an ordered collection, like a row of the board
    [DICTIONARY]  a lookup table, like "piece name" -> "its shapes"
    [TUPLE]       a small fixed pair of numbers, like (column, row)
    [LOOP]        for/while loops that repeat an action
    [CONDITIONAL] if/elif/else decisions
"""

import random
from typing import TypedDict

# ---------------------------------------------------------------------------
# Type declarations.
#
# `type NAME = ...` is Python's modern type-alias statement: it gives a
# long type a short, readable name, so the rest of the file can just say
# `Board` instead of spelling out `list[list[str | None]]` every time.
#
# Type declarations are optional in Python -- the program runs exactly the
# same without them -- but they document what each function expects, and
# your editor will warn you when you pass the wrong thing.
# ---------------------------------------------------------------------------
type Cell = str | None          # a color name like "cyan", or None if empty
type Board = list[list[Cell]]   # a list of rows; each row is a list of cells


class Piece(TypedDict):
    """A single falling tetromino.

    At runtime a piece is an ordinary Python [DICTIONARY] -- you build one
    with a normal `{...}` literal and read it with `piece["name"]`.
    `TypedDict` simply records *which* keys it has and what type each
    value is, so your editor can autocomplete the keys and flag typos.
    """

    name: str       # which tetromino it is, e.g. "T"      [STRING]
    rotation: int   # index into SHAPES[name]; starts at 0
    col: int        # the board column of the piece's anchor
    row: int        # the board row of the piece's anchor

# ---------------------------------------------------------------------------
# Board size (just plain numbers, but we give them names so the rest of the
# code reads like English instead of a wall of magic numbers).
# ---------------------------------------------------------------------------
COLS = 10
ROWS = 16

# ---------------------------------------------------------------------------
# [DICTIONARY] SHAPES maps a piece name [STRING] -> a [LIST] of "rotation
# states". Each rotation state is itself a [LIST] of [TUPLE] coordinates
# (column, row) that say which of the 4 squares in a piece are filled in,
# inside an imaginary 4x4 box.
#
# Rotating a piece is as simple as moving to the *next* list in the list!
# ---------------------------------------------------------------------------
SHAPES: dict[str, list[list[tuple[int, int]]]] = {
    "I": [
        [(0, 1), (1, 1), (2, 1), (3, 1)],
        [(2, 0), (2, 1), (2, 2), (2, 3)],
    ],
    "O": [
        [(1, 0), (2, 0), (1, 1), (2, 1)],
    ],
    "T": [
        [(0, 1), (1, 1), (2, 1), (1, 0)],
        [(1, 0), (1, 1), (1, 2), (2, 1)],
        [(0, 1), (1, 1), (2, 1), (1, 2)],
        [(1, 0), (1, 1), (1, 2), (0, 1)],
    ],
    "S": [
        [(1, 0), (2, 0), (0, 1), (1, 1)],
        [(1, 0), (1, 1), (2, 1), (2, 2)],
    ],
    "Z": [
        [(0, 0), (1, 0), (1, 1), (2, 1)],
        [(2, 0), (1, 1), (2, 1), (1, 2)],
    ],
    "J": [
        [(0, 0), (0, 1), (1, 1), (2, 1)],
        [(1, 0), (2, 0), (1, 1), (1, 2)],
        [(0, 1), (1, 1), (2, 1), (2, 2)],
        [(1, 0), (1, 1), (1, 2), (0, 2)],
    ],
    "L": [
        [(2, 0), (0, 1), (1, 1), (2, 1)],
        [(1, 0), (1, 1), (1, 2), (2, 2)],
        [(0, 1), (1, 1), (2, 1), (0, 2)],
        [(0, 0), (1, 0), (1, 1), (1, 2)],
    ],
}

# [DICTIONARY] piece name [STRING] -> color name [STRING] used when drawing.
COLORS: dict[str, str] = {
    "I": "cyan",
    "O": "yellow",
    "T": "purple",
    "S": "green",
    "Z": "red",
    "J": "blue",
    "L": "orange",
}


def new_board() -> Board:
    """Create a brand-new, empty game board.

    The board is a [LIST] of rows, and each row is itself a [LIST] of
    cells. Each cell holds either ``None`` (empty square) or a color name
    [STRING] (a locked-in, filled square). A "list of lists" like this is
    often called a 2D list, or a grid.

    Args:
        (none)

    Returns:
        Board: a new grid with ``ROWS`` rows and ``COLS`` columns, where
        every single cell is ``None`` (i.e. the board starts completely
        empty).
    """
    board: Board = []
    for _row in range(ROWS):                       # [LOOP]
        row: list[Cell] = [None for _col in range(COLS)]  # [LOOP] (list comprehension)
        board.append(row)
    return board


def new_piece() -> Piece:
    """Create a new falling tetromino, chosen at random.

    The piece is a [DICTIONARY] with the four keys described by the
    ``Piece`` declaration at the top of this file.

    Args:
        (none)

    Returns:
        Piece: a new piece dictionary, roughly centered horizontally and
        anchored at row 0, so its blocks occupy the top few rows of the
        board (every shape's offsets start at row 0, so a new piece is
        always fully on the board).
    """
    name: str = random.choice(list(SHAPES.keys()))
    piece: Piece = {
        "name": name,
        "rotation": 0,
        "col": COLS // 2 - 2,
        "row": 0,
    }
    return piece


def piece_blocks(piece: Piece, rotation: int | None = None) -> list[tuple[int, int]]:
    """Look up the (column, row) offsets that make up a piece's shape.

    Args:
        piece: The piece dictionary to look up, as produced by
            :func:`new_piece`. Only ``piece["name"]`` is required; the
            ``rotation`` argument below can override ``piece["rotation"]``.
        rotation: Which rotation state to use. If ``None`` (the default),
            the piece's own current ``"rotation"`` value is used instead.
            Passing a specific number lets you "try before you buy" --
            check what a rotation would look like before committing to it.

    Returns:
        list[tuple[int, int]]: the [LIST] of ``(col, row)`` [TUPLE] offsets
        for the requested rotation state, measured from the piece's
        ``"col"``/``"row"`` anchor point.
    """
    if rotation is None:                # [CONDITIONAL]
        rotation = piece["rotation"]
    states = SHAPES[piece["name"]]
    return states[rotation % len(states)]


def valid_position(
    board: Board,
    piece: Piece,
    d_col: int = 0,
    d_row: int = 0,
    rotation: int | None = None,
) -> bool:
    """Check whether a piece would legally fit on the board.

    This is used before every move: "can this piece shift left?", "can it
    drop one row?", "can it rotate?" -- all by testing a hypothetical
    position without actually changing the piece yet.

    Args:
        board: The current board grid to test against.
        piece: The piece to test.
        d_col: How many columns to shift the piece by for this test
            (negative moves left, positive moves right). Defaults to 0.
        d_row: How many rows to shift the piece by for this test
            (positive moves down, since row numbers increase downward).
            Defaults to 0.
        rotation: An alternate rotation state to test, or ``None`` to keep
            the piece's current rotation. Defaults to ``None``.

    Returns:
        bool: ``True`` if every block of the piece would land inside the
        board and on top of empty cells; ``False`` if any block would go
        off the left/right edge, off the bottom, or overlap an
        already-filled cell.
    """
    for (dc, dr) in piece_blocks(piece, rotation):    # [LOOP] over [TUPLE]s
        col = piece["col"] + dc + d_col
        row = piece["row"] + dr + d_row

        if col < 0 or col >= COLS:          # [CONDITIONAL] off the left/right edge
            return False
        if row >= ROWS:                     # [CONDITIONAL] off the bottom edge
            return False
        if row >= 0 and board[row][col] is not None:  # [CONDITIONAL] hits a locked block
            return False

    return True


def lock_piece(board: Board, piece: Piece) -> None:
    """Permanently stamp a piece's color into the board.

    Called once a piece can no longer move down. After this, the piece's
    squares are just part of the landscape, the same as any other locked
    block.

    Args:
        board: The board grid to modify. Modified in place; nothing is
            returned.
        piece: The piece to lock into place, at its current position and
            rotation.

    Returns:
        None. ``board`` is mutated directly.
    """
    color = COLORS[piece["name"]]
    for (dc, dr) in piece_blocks(piece):    # [LOOP]
        col = piece["col"] + dc
        row = piece["row"] + dr
        if row >= 0:                        # [CONDITIONAL] ignore rows above the visible board
            board[row][col] = color


def clear_full_rows(board: Board) -> int:
    """Remove every completely-full row and refill the top with empty rows.

    A row counts as "full" when it contains no ``None`` cells at all --
    every column has a locked block in it.

    Args:
        board: The board grid to check and modify. Modified in place.

    Returns:
        int: how many rows were cleared (0 to 4 for a single piece drop).
        The caller can feed this straight into :func:`score_for_lines`.
    """
    remaining_rows: list[list[Cell]] = []
    cleared = 0

    for row in board:              # [LOOP]
        if None in row:              # [CONDITIONAL] row still has empty space
            remaining_rows.append(row)
        else:                        # row is completely full -> clear it
            cleared += 1

    while len(remaining_rows) < ROWS:        # [LOOP] (a while loop!)
        remaining_rows.insert(0, [None for _ in range(COLS)])

    # Replace the contents of the board in place, so anyone else holding a
    # reference to this same board list sees the update too.
    board[:] = remaining_rows
    return cleared


def score_for_lines(lines_cleared: int) -> int:
    """Convert a number of simultaneously-cleared lines into points.

    Uses classic Tetris-style scoring, where clearing several lines at
    once (with a single piece) is worth disproportionately more than
    clearing them one at a time.

    Args:
        lines_cleared: How many rows were cleared by the most recent piece,
            typically the return value of :func:`clear_full_rows`.
            Expected to be between 0 and 4.

    Returns:
        int: the number of points earned. ``0`` lines is worth ``0``
        points, and 1/2/3/4 lines follow the classic 100/300/500/800
        point table. Any larger number (shouldn't happen with a
        4-square piece) is scored the same as 4.
    """
    points_per_line_count: dict[int, int] = {
        0: 0,
        1: 100,
        2: 300,
        3: 500,
        4: 800,
    }
    if lines_cleared in points_per_line_count:    # [CONDITIONAL]
        return points_per_line_count[lines_cleared]
    return 800   # shouldn't happen with 4 blocks per piece, but just in case
