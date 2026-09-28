"""
pacman_logic.py
----------------
This file holds the "brain" of the Pac-Man game: the maze, the rules for
moving around it, eating dots, and deciding which way the ghost walks. It
has NO drawing code in it at all, so you (or a program) can test it
without opening any window.

The actual drawing and keyboard handling live in pacman.py, which imports
everything from this file.

CONCEPTS USED IN THIS FILE (look for the tag in the comments):
    [STRING]      text values, like maze rows and cell characters
    [LIST]        an ordered collection, like a row of the maze grid
    [TUPLE]       a small fixed pair of numbers, like (row, col)
    [DICTIONARY]  a lookup table, like "direction name" -> "(drow, dcol)"
    [LOOP]        for/while loops that repeat an action
    [CONDITIONAL] if/elif/else decisions
"""

from collections import deque

# ---------------------------------------------------------------------------
# Type declarations.
#
# `type NAME = ...` is Python's modern type-alias statement: it gives a
# long type a short, readable name, so the rest of the file can just say
# `Grid` instead of spelling out `list[list[str]]` every time.
#
# Type declarations are optional in Python -- the program runs exactly the
# same without them -- but they document what each function expects, and
# your editor will warn you when you pass the wrong thing.
# ---------------------------------------------------------------------------
type Cell = str                  # a single character: "#", ".", or " "
type Grid = list[list[Cell]]     # a list of rows; each row is a list of cells
type Position = tuple[int, int]  # a (row, col) coordinate on the grid


# ---------------------------------------------------------------------------
# The characters used in the maze "blueprint" below, and what each one
# means. Giving them names instead of writing "#" and "." directly all over
# the file means a typo like "." vs "," would be caught immediately (Python
# would say the name doesn't exist), instead of silently breaking the game.
# ---------------------------------------------------------------------------
WALL: Cell = "#"            # a solid wall -- nothing can move through it
DOT: Cell = "."              # a dot waiting to be eaten, worth SCORE_PER_DOT
EMPTY: Cell = " "            # open floor with no dot (already eaten, or
                             # never had one -- e.g. where Pac-Man/ghost start)

# The two special characters that only ever appear in the *blueprint*
# (MAZE_TEMPLATE below). parse_maze() reads these to find the starting
# positions, then replaces them with EMPTY before the grid is used to
# play the game -- the grid itself never contains a "P" or a "G".
PACMAN_START: Cell = "P"
GHOST_START: Cell = "G"

SCORE_PER_DOT: int = 10


# ---------------------------------------------------------------------------
# [DICTIONARY] DIRECTIONS maps a direction name [STRING] -> a (drow, dcol)
# [TUPLE]: how much the row and column change by if you take one step that
# way. Because the grid is a list of rows (row 0 is the TOP), moving "DOWN"
# means *increasing* the row number, not decreasing it.
# ---------------------------------------------------------------------------
DIRECTIONS: dict[str, tuple[int, int]] = {
    "UP": (-1, 0),
    "DOWN": (1, 0),
    "LEFT": (0, -1),
    "RIGHT": (0, 1),
}


# ---------------------------------------------------------------------------
# MAZE_TEMPLATE is the maze's "blueprint": a plain [LIST] of [STRING]s, one
# per row, with every row exactly 19 characters wide. This is the easiest
# possible way to sketch out a 2D maze -- you can literally see its shape
# just by reading the code.
#
# parse_maze() (below) turns this list of strings into the *actual* grid
# the game plays on: a list of lists of single characters, so individual
# dots can be eaten (erased) one at a time as the game runs. A plain string
# can't be changed one character at a time in Python (strings are
# immutable), which is exactly why the playable grid uses lists instead.
# ---------------------------------------------------------------------------
MAZE_TEMPLATE: list[str] = [
    "###################",
    "#.................#",
    "#.###.........###.#",
    "#.###.........###.#",
    "#.................#",
    "#.................#",
    "#........G........#",
    "#.................#",
    "#.###.........###.#",
    "#.###.........###.#",
    "#.................#",
    "#........P........#",
    "###################",
]


def parse_maze(template: list[str]) -> tuple[Grid, Position | None, Position | None]:
    """Turn a maze blueprint (a list of strings) into a playable grid.

    This is the "string processing" heart of the whole project: every row
    string is walked one character at a time, and turned into a [LIST] of
    single-character cells (so dots can be erased later -- see
    :func:`eat_dot`). Along the way, the one "P" and one "G" character are
    found, remembered as starting positions, and replaced with plain open
    floor so the returned grid only ever contains "#", ".", and " ".

    Args:
        template: The maze blueprint, e.g. :data:`MAZE_TEMPLATE` -- a
            [LIST] of equal-length [STRING]s, one per row.

    Returns:
        tuple[Grid, Position | None, Position | None]: a 3-tuple of
        ``(grid, pacman_start, ghost_start)``, where ``grid`` is the
        mutable playable maze, and the two positions are ``(row, col)``
        [TUPLE]s -- or ``None`` if that template had no "P" (or no "G")
        in it at all.
    """
    grid: Grid = []
    pacman_start: Position | None = None
    ghost_start: Position | None = None

    for row_index, row_string in enumerate(template):        # [LOOP]
        row_cells: list[Cell] = list(row_string)               # [STRING] -> [LIST]
        for col_index, cell in enumerate(row_cells):             # [LOOP] (nested)
            if cell == PACMAN_START:                                # [CONDITIONAL]
                pacman_start = (row_index, col_index)
                row_cells[col_index] = EMPTY
            elif cell == GHOST_START:                               # [CONDITIONAL]
                ghost_start = (row_index, col_index)
                row_cells[col_index] = EMPTY
        grid.append(row_cells)

    return grid, pacman_start, ghost_start


def in_bounds(grid: Grid, row: int, col: int) -> bool:
    """Check whether (row, col) is a real square on the grid.

    Args:
        grid: The maze grid to check against.
        row: The row number to test.
        col: The column number to test.

    Returns:
        bool: ``True`` if ``row``/``col`` land inside ``grid``'s
        dimensions, ``False`` if they fall off any edge.
    """
    if row < 0 or row >= len(grid):        # [CONDITIONAL] above/below the grid
        return False
    if col < 0 or col >= len(grid[row]):   # [CONDITIONAL] left/right of the grid
        return False
    return True


def is_wall(grid: Grid, row: int, col: int) -> bool:
    """Check whether a specific square is a wall.

    Args:
        grid: The maze grid to check.
        row: The row of the square to check.
        col: The column of the square to check.

    Returns:
        bool: ``True`` if that square is a wall character, ``False``
        otherwise (dot or empty floor). The caller is responsible for
        making sure ``row``/``col`` are :func:`in_bounds` first.
    """
    return grid[row][col] == WALL


def can_move(grid: Grid, position: Position, direction: str) -> bool:
    """Check whether something standing at ``position`` can step one
    square in ``direction`` without leaving the grid or walking into a
    wall.

    Args:
        grid: The maze grid to check against.
        position: The ``(row, col)`` [TUPLE] to move from.
        direction: One of the keys of :data:`DIRECTIONS`
            (``"UP"``/``"DOWN"``/``"LEFT"``/``"RIGHT"``).

    Returns:
        bool: ``True`` if the destination square is on the grid and is
        not a wall; ``False`` otherwise.
    """
    row, col = position
    drow, dcol = DIRECTIONS[direction]
    new_row, new_col = row + drow, col + dcol

    if not in_bounds(grid, new_row, new_col):    # [CONDITIONAL] would fall off the grid
        return False
    return not is_wall(grid, new_row, new_col)     # [CONDITIONAL] would hit a wall


def move_position(position: Position, direction: str) -> Position:
    """Compute the square one step away from ``position``, without
    checking whether that step is actually legal.

    This is deliberately "dumb" arithmetic with no wall-checking, so it can
    be reused by both :func:`move_pacman` (which checks first) and by
    anything that wants to peek at "what square is over there?" without
    committing to the move.

    Args:
        position: The ``(row, col)`` [TUPLE] to move from.
        direction: One of the keys of :data:`DIRECTIONS`.

    Returns:
        Position: the new ``(row, col)`` [TUPLE], one step away from
        ``position`` in ``direction``.
    """
    row, col = position
    drow, dcol = DIRECTIONS[direction]
    return (row + drow, col + dcol)


def move_pacman(grid: Grid, position: Position, direction: str | None) -> Position:
    """Work out Pac-Man's new position after a single keypress.

    Args:
        grid: The maze grid, used to check for walls.
        position: Pac-Man's current ``(row, col)`` [TUPLE].
        direction: The direction key that was pressed (one of the keys of
            :data:`DIRECTIONS`), or ``None`` if no key has been pressed
            yet.

    Returns:
        Position: the new position if the move is legal; the unchanged
        ``position`` if ``direction`` is ``None`` or the move would hit a
        wall or leave the grid (bumping into a wall simply does nothing,
        exactly like the original arcade game).
    """
    if direction is None:                              # [CONDITIONAL] no key pressed yet
        return position
    if can_move(grid, position, direction):             # [CONDITIONAL]
        return move_position(position, direction)
    return position


def eat_dot(grid: Grid, position: Position) -> bool:
    """Eat the dot (if any) at ``position``, erasing it from the grid.

    Args:
        grid: The maze grid to modify. Modified in place; nothing is
            returned besides the ``bool`` described below.
        position: The ``(row, col)`` [TUPLE] to check and clear.

    Returns:
        bool: ``True`` if there was a dot at ``position`` (which has now
        been replaced with :data:`EMPTY`); ``False`` if that square was
        already empty (there is nothing to do in that case).
    """
    row, col = position
    if grid[row][col] == DOT:            # [CONDITIONAL]
        grid[row][col] = EMPTY
        return True
    return False


def count_dots(grid: Grid) -> int:
    """Count how many dots are still left on the grid.

    Args:
        grid: The maze grid to scan.

    Returns:
        int: the total number of :data:`DOT` cells remaining, added up
        across every row.
    """
    total = 0
    for row in grid:              # [LOOP]
        total += row.count(DOT)     # [STRING]/[LIST] method: counts matches
    return total


def has_won(grid: Grid) -> bool:
    """Check whether the player has eaten every dot in the maze.

    Args:
        grid: The maze grid to check.

    Returns:
        bool: ``True`` once :func:`count_dots` reaches zero.
    """
    return count_dots(grid) == 0


def check_collision(pacman_position: Position, ghost_position: Position) -> bool:
    """Check whether Pac-Man and the ghost occupy the very same square.

    Args:
        pacman_position: Pac-Man's current ``(row, col)`` [TUPLE].
        ghost_position: The ghost's current ``(row, col)`` [TUPLE].

    Returns:
        bool: ``True`` if the two positions are identical (the ghost has
        caught Pac-Man), ``False`` otherwise.
    """
    return pacman_position == ghost_position


def choose_ghost_direction(
    grid: Grid, ghost_position: Position, pacman_position: Position
) -> str | None:
    """Decide which single direction the ghost should try to move this
    turn, in order to chase Pac-Man.

    The ghost is not a maze-solver -- it doesn't plan a whole route. Every
    turn it just asks: "is Pac-Man mostly above/below me, or mostly
    left/right of me?", tries to close *that* gap first, and only tries
    the other axis if its first choice is blocked by a wall. This is a
    simple [CONDITIONAL]-driven heuristic, not real pathfinding, which
    makes it easy to read, easy to test, and (deliberately) sometimes easy
    to outrun around a pillar.

    Args:
        grid: The maze grid, used to check which moves are legal.
        ghost_position: The ghost's current ``(row, col)`` [TUPLE].
        pacman_position: Pac-Man's current ``(row, col)`` [TUPLE], i.e.
            what the ghost is chasing.

    Returns:
        str | None: the chosen direction name (a key of
        :data:`DIRECTIONS`), or ``None`` if the ghost is completely boxed
        in and cannot legally move at all this turn.
    """
    ghost_row, ghost_col = ghost_position
    pacman_row, pacman_col = pacman_position
    row_gap = pacman_row - ghost_row     # positive => Pac-Man is below the ghost
    col_gap = pacman_col - ghost_col     # positive => Pac-Man is right of the ghost

    row_direction: str | None = None
    if row_gap > 0:                      # [CONDITIONAL]
        row_direction = "DOWN"
    elif row_gap < 0:                    # [CONDITIONAL]
        row_direction = "UP"

    col_direction: str | None = None
    if col_gap > 0:                      # [CONDITIONAL]
        col_direction = "RIGHT"
    elif col_gap < 0:                    # [CONDITIONAL]
        col_direction = "LEFT"

    # Chase along whichever axis has the bigger gap first; fall back to
    # the other axis if the first choice is blocked by a wall.
    if abs(row_gap) >= abs(col_gap):     # [CONDITIONAL]
        preferred, fallback = row_direction, col_direction
    else:
        preferred, fallback = col_direction, row_direction

    for direction in (preferred, fallback):    # [LOOP] (at most two tries)
        if direction is not None and can_move(grid, ghost_position, direction):
            return direction

    return None    # boxed in on both axes -- stay put this turn


def move_ghost(grid: Grid, ghost_position: Position, pacman_position: Position) -> Position:
    """Work out the ghost's new position for one automatic game tick.

    Args:
        grid: The maze grid, used to check for walls.
        ghost_position: The ghost's current ``(row, col)`` [TUPLE].
        pacman_position: Pac-Man's current ``(row, col)`` [TUPLE].

    Returns:
        Position: the ghost's new position after chasing Pac-Man one step,
        via :func:`choose_ghost_direction`; the unchanged ``ghost_position``
        if no legal move is available this turn.
    """
    direction = choose_ghost_direction(grid, ghost_position, pacman_position)
    if direction is None:                # [CONDITIONAL]
        return ghost_position
    return move_position(ghost_position, direction)


def shortest_path_length(grid: Grid, start: Position, goal: Position) -> int | None:
    """Find the length of the shortest open path between two squares.

    This is not used by the playable game itself -- :func:`choose_ghost_direction`
    deliberately uses a much simpler heuristic so students can read and
    predict it. It exists as a reference "real" pathfinding
    algorithm (a breadth-first search, or BFS) for the maze, useful for
    tests (e.g. confirming :data:`MAZE_TEMPLATE` is fully connected) and as
    a stretch-goal starting point for a smarter ghost.

    Args:
        grid: The maze grid to search.
        start: The ``(row, col)`` [TUPLE] to search from.
        goal: The ``(row, col)`` [TUPLE] to search for.

    Returns:
        int | None: the number of steps in the shortest path from
        ``start`` to ``goal`` (``0`` if they're the same square), or
        ``None`` if no path exists.
    """
    if start == goal:                     # [CONDITIONAL]
        return 0

    visited = {start}
    queue = deque([(start, 0)])
    while queue:                          # [LOOP] (breadth-first search)
        position, distance = queue.popleft()
        for direction in DIRECTIONS:        # [LOOP]
            if not can_move(grid, position, direction):    # [CONDITIONAL]
                continue
            next_position = move_position(position, direction)
            if next_position == goal:                       # [CONDITIONAL]
                return distance + 1
            if next_position not in visited:                # [CONDITIONAL]
                visited.add(next_position)
                queue.append((next_position, distance + 1))

    return None
