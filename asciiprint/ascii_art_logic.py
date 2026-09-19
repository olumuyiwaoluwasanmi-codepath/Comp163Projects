"""
ascii_art_logic.py
-------------------
This file holds the "brain" of ASCIIPrint: the font data and the rules for
turning a word into big ASCII-art letters. It has NO input()/print() calls
in it at all, so it can be tested without running the interactive program.

The actual interactive program (asking the user for a word, a character,
and a size, then printing the result) lives in asciiprint.py, which
imports everything it needs from this file.

CONCEPTS USED IN THIS FILE (look for the tag in the comments):
    [STRING]      text values, like a row of a letter's pattern
    [LIST]        an ordered collection, like the 7 rows of a letter
    [DICTIONARY]  a lookup table, like "letter" -> "its pattern"
    [LOOP]        for loops that repeat an action
    [CONDITIONAL] if/elif/else decisions
"""

from typing import TypeAlias

# ---------------------------------------------------------------------------
# Type aliases.
#
# `NAME: TypeAlias = ...` gives a plain `str` or `list[str]` a name that
# says what it actually *means* in this file, so a function signature
# like `get_glyph(character: str) -> Glyph` reads as English instead of
# just repeating `list[str]` everywhere.
#
# Type hints are optional in Python -- the program runs exactly the same
# without them -- but they document what each function expects, your
# editor can autocomplete and flag mistakes with them, and a checker like
# mypy can catch a wrong type before you ever run the code.
# ---------------------------------------------------------------------------
Row: TypeAlias = str            # one printable row, e.g. "#...#" or "*   *"
Glyph: TypeAlias = list[Row]    # one character's pattern: GLYPH_HEIGHT rows
Grid: TypeAlias = list[Row]     # a whole rendered word: also a list of rows

# ---------------------------------------------------------------------------
# [DICTIONARY] SIZES maps a size name [STRING] -> how many times bigger each
# little square of the letter should be drawn. "small" draws each square as
# 1 character, "big" as a 2x2 block, "extra-large" as a 3x3 block.
# ---------------------------------------------------------------------------
SIZES: dict[str, int] = {
    "small": 1,
    "big": 2,
    "extra-large": 3,
}

# ---------------------------------------------------------------------------
# [DICTIONARY] FONT maps a single character [STRING] -> a Glyph: a [LIST] of
# 7 rows. Each row is a 5-character [STRING] made only of "#" (part of the
# letter) and "." (empty space). Together the 7 rows draw the letter on a
# 5-wide, 7-tall grid -- the same idea as the dot-matrix signs on old
# scoreboards.
#
# Try printing one yourself to see it:
#   for row in FONT["A"]:
#       print(row)
# ---------------------------------------------------------------------------
FONT: dict[str, Glyph] = {
    "A": [
        ".###.",
        "#...#",
        "#...#",
        "#####",
        "#...#",
        "#...#",
        "#...#",
    ],
    "B": [
        "####.",
        "#...#",
        "#...#",
        "####.",
        "#...#",
        "#...#",
        "####.",
    ],
    "C": [
        ".####",
        "#....",
        "#....",
        "#....",
        "#....",
        "#....",
        ".####",
    ],
    "D": [
        "###..",
        "#..#.",
        "#...#",
        "#...#",
        "#...#",
        "#..#.",
        "###..",
    ],
    "E": [
        "#####",
        "#....",
        "#....",
        "####.",
        "#....",
        "#....",
        "#####",
    ],
    "F": [
        "#####",
        "#....",
        "#....",
        "####.",
        "#....",
        "#....",
        "#....",
    ],
    "G": [
        ".####",
        "#....",
        "#....",
        "#.###",
        "#...#",
        "#...#",
        ".####",
    ],
    "H": [
        "#...#",
        "#...#",
        "#...#",
        "#####",
        "#...#",
        "#...#",
        "#...#",
    ],
    "I": [
        "#####",
        "..#..",
        "..#..",
        "..#..",
        "..#..",
        "..#..",
        "#####",
    ],
    "J": [
        "..###",
        "...#.",
        "...#.",
        "...#.",
        "...#.",
        "#..#.",
        ".##..",
    ],
    "K": [
        "#...#",
        "#..#.",
        "#.#..",
        "##...",
        "#.#..",
        "#..#.",
        "#...#",
    ],
    "L": [
        "#....",
        "#....",
        "#....",
        "#....",
        "#....",
        "#....",
        "#####",
    ],
    "M": [
        "#...#",
        "##.##",
        "#.#.#",
        "#...#",
        "#...#",
        "#...#",
        "#...#",
    ],
    "N": [
        "#...#",
        "##..#",
        "#.#.#",
        "#..##",
        "#...#",
        "#...#",
        "#...#",
    ],
    "O": [
        ".###.",
        "#...#",
        "#...#",
        "#...#",
        "#...#",
        "#...#",
        ".###.",
    ],
    "P": [
        "####.",
        "#...#",
        "#...#",
        "####.",
        "#....",
        "#....",
        "#....",
    ],
    "Q": [
        ".###.",
        "#...#",
        "#...#",
        "#...#",
        "#.#.#",
        "#..#.",
        ".##.#",
    ],
    "R": [
        "####.",
        "#...#",
        "#...#",
        "####.",
        "#.#..",
        "#..#.",
        "#...#",
    ],
    "S": [
        ".####",
        "#....",
        "#....",
        ".###.",
        "....#",
        "....#",
        "####.",
    ],
    "T": [
        "#####",
        "..#..",
        "..#..",
        "..#..",
        "..#..",
        "..#..",
        "..#..",
    ],
    "U": [
        "#...#",
        "#...#",
        "#...#",
        "#...#",
        "#...#",
        "#...#",
        ".###.",
    ],
    "V": [
        "#...#",
        "#...#",
        "#...#",
        "#...#",
        "#...#",
        ".#.#.",
        "..#..",
    ],
    "W": [
        "#...#",
        "#...#",
        "#...#",
        "#.#.#",
        "#.#.#",
        "##.##",
        "#...#",
    ],
    "X": [
        "#...#",
        "#...#",
        ".#.#.",
        "..#..",
        ".#.#.",
        "#...#",
        "#...#",
    ],
    "Y": [
        "#...#",
        "#...#",
        ".#.#.",
        "..#..",
        "..#..",
        "..#..",
        "..#..",
    ],
    "Z": [
        "#####",
        "....#",
        "...#.",
        "..#..",
        ".#...",
        "#....",
        "#####",
    ],
    "0": [
        ".###.",
        "#...#",
        "#..##",
        "#.#.#",
        "##..#",
        "#...#",
        ".###.",
    ],
    "1": [
        "..#..",
        ".##..",
        "..#..",
        "..#..",
        "..#..",
        "..#..",
        "#####",
    ],
    "2": [
        ".###.",
        "#...#",
        "....#",
        "...#.",
        "..#..",
        ".#...",
        "#####",
    ],
    "3": [
        "####.",
        "....#",
        "....#",
        "..##.",
        "....#",
        "....#",
        "####.",
    ],
    "4": [
        "...#.",
        "..##.",
        ".#.#.",
        "#..#.",
        "#####",
        "...#.",
        "...#.",
    ],
    "5": [
        "#####",
        "#....",
        "#....",
        "####.",
        "....#",
        "....#",
        "####.",
    ],
    "6": [
        "..##.",
        ".#...",
        "#....",
        "####.",
        "#...#",
        "#...#",
        ".###.",
    ],
    "7": [
        "#####",
        "....#",
        "...#.",
        "..#..",
        ".#...",
        ".#...",
        ".#...",
    ],
    "8": [
        ".###.",
        "#...#",
        "#...#",
        ".###.",
        "#...#",
        "#...#",
        ".###.",
    ],
    "9": [
        ".###.",
        "#...#",
        "#...#",
        ".####",
        "....#",
        "...#.",
        ".##..",
    ],
    " ": [
        ".....",
        ".....",
        ".....",
        ".....",
        ".....",
        ".....",
        ".....",
    ],
    "!": [
        "..#..",
        "..#..",
        "..#..",
        "..#..",
        "..#..",
        ".....",
        "..#..",
    ],
    "?": [
        ".###.",
        "#...#",
        "....#",
        "...#.",
        "..#..",
        ".....",
        "..#..",
    ],
    ".": [
        ".....",
        ".....",
        ".....",
        ".....",
        ".....",
        ".....",
        "..#..",
    ],
    ",": [
        ".....",
        ".....",
        ".....",
        ".....",
        ".....",
        "..#..",
        ".#...",
    ],
    "'": [
        "..#..",
        "..#..",
        ".....",
        ".....",
        ".....",
        ".....",
        ".....",
    ],
    "-": [
        ".....",
        ".....",
        ".....",
        "#####",
        ".....",
        ".....",
        ".....",
    ],
}

# How tall (in rows) and wide (in columns) every glyph in FONT is.
GLYPH_HEIGHT = 7
GLYPH_WIDTH = 5

# The glyph shown for any character that isn't in FONT, so a typo never
# crashes the program -- it just shows up as an obvious "?" instead.
UNKNOWN_GLYPH: Glyph = FONT["?"]


def get_glyph(character: str) -> Glyph:
    """Return the 7-row [LIST] pattern for one character [STRING].

    Lowercase letters are converted to uppercase first, since FONT only
    stores capital letters. Any character not in FONT (an emoji, an
    accented letter, and so on) falls back to UNKNOWN_GLYPH.
    """
    return FONT.get(character.upper(), UNKNOWN_GLYPH)  # [CONDITIONAL] (inside .get)


def build_base_grid(text: str) -> Grid:
    """Turn `text` into 7 [STRING] rows of "#"/"." at actual size (1x).

    Each character's glyph is glued onto the end of every row, with one
    extra "." column added after it as a small gap -- otherwise letters
    would touch each other with no space between them.
    """
    rows: Grid = ["" for _ in range(GLYPH_HEIGHT)]  # [LIST] one entry per row
    for character in text:  # [LOOP] one character at a time, left to right
        glyph = get_glyph(character)
        for row_index in range(GLYPH_HEIGHT):  # [LOOP] stack this glyph's rows on
            rows[row_index] += glyph[row_index] + "."
    return rows


def scale_grid(rows: Grid, multiplier: int) -> Grid:
    """Blow up a grid of rows by `multiplier`, both wider and taller.

    Each character becomes a multiplier x multiplier block: repeated
    `multiplier` times across (so "#" becomes "##" at 2x), and each whole
    row is then repeated `multiplier` times down, so the block is square.
    """
    scaled_rows: Grid = []
    for row in rows:  # [LOOP] widen this row, then duplicate it downward
        wide_row = "".join(character * multiplier for character in row)
        for _ in range(multiplier):  # [LOOP] repeat the widened row `multiplier` times
            scaled_rows.append(wide_row)
    return scaled_rows


def render_text(text: str, fill_char: str = "*", size: str = "big") -> Grid:
    """Turn `text` into a [LIST] of printable ASCII-art rows.

    `fill_char` is the single character drawn for every "on" pixel of a
    letter (spaces are left blank). `size` must be one of the keys in
    SIZES ("small", "big", or "extra-large").

    Raises ValueError if any argument is unusable, so the caller can show
    a friendly message instead of the program crashing.
    """
    if text.strip() == "":
        raise ValueError("text must contain at least one non-space character")
    if len(fill_char) != 1:
        raise ValueError("fill_char must be exactly one character")
    if fill_char == " ":
        raise ValueError("fill_char can't be a space -- the letters would be invisible")
    if size not in SIZES:
        valid = ", ".join(sorted(SIZES))
        raise ValueError(f"size must be one of: {valid}")

    multiplier = SIZES[size]
    base_grid = build_base_grid(text)
    scaled_grid = scale_grid(base_grid, multiplier)
    return [row.replace("#", fill_char).replace(".", " ") for row in scaled_grid]
