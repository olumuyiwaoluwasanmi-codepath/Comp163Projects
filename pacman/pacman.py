"""
pacman.py
---------
The visible part of Turtle Pac-Man: drawing the maze, the dots, Pac-Man,
and the ghost on screen with the ``turtle`` module, and reacting to
keyboard presses.

All of the actual game *rules* (the maze, moving, eating dots, chasing,
winning, and losing) live in ``pacman_logic.py``. This file is only
responsible for:

    1. Turning the logic module's grid/position data into shapes on screen.
    2. Listening for arrow-key presses and calling the right logic
       functions in response.
    3. Running the game loop that makes the ghost chase Pac-Man
       automatically, on a timer.

Run it with:
    python3 pacman.py

Controls:
    Left / Right / Up / Down - move Pac-Man one square at a time
"""

import turtle

import pacman_logic as logic
from pacman_logic import Grid, Position

# ---------------------------------------------------------------------------
# Layout constants (all plain numbers, named so the rest of the file reads
# like English).
# ---------------------------------------------------------------------------
CELL_SIZE: int = 24
GRID_ROWS: int = len(logic.MAZE_TEMPLATE)
GRID_COLS: int = len(logic.MAZE_TEMPLATE[0])
BOARD_WIDTH: int = GRID_COLS * CELL_SIZE
BOARD_HEIGHT: int = GRID_ROWS * CELL_SIZE

# The maze is drawn with (0, 0) at its top-left corner in "board pixel"
# space; ORIGIN_X/ORIGIN_Y translate that into turtle's screen coordinates,
# which put (0, 0) at the center of the window.
ORIGIN_X: int = -BOARD_WIDTH // 2
ORIGIN_Y: int = BOARD_HEIGHT // 2

GHOST_STEP_MS: int = 400   # how often the ghost takes one chasing step


def cell_top_left(row: int, col: int) -> tuple[float, float]:
    """Convert a grid (row, col) [TUPLE] into the pixel position of that
    cell's top-left corner.

    Used for drawing filled squares (walls), which turtle draws by
    starting a pen at a corner and walking around the shape -- see
    :func:`draw_wall_square`.

    Args:
        row: Zero-based row index (0 is the topmost row).
        col: Zero-based column index (0 is the leftmost column).

    Returns:
        tuple[float, float]: the ``(x, y)`` pixel coordinates of that
        cell's top-left corner, in the turtle window's coordinate system.
    """
    x = ORIGIN_X + col * CELL_SIZE
    y = ORIGIN_Y - row * CELL_SIZE
    return x, y


def cell_center(row: int, col: int) -> tuple[float, float]:
    """Convert a grid (row, col) [TUPLE] into the pixel position of that
    cell's center point.

    Used for anything drawn as a *centered* shape -- dots, Pac-Man, and
    the ghost are all positioned by their center, not their corner.

    Args:
        row: Zero-based row index.
        col: Zero-based column index.

    Returns:
        tuple[float, float]: the ``(x, y)`` pixel coordinates of that
        cell's center, in the turtle window's coordinate system.
    """
    x, y = cell_top_left(row, col)
    return x + CELL_SIZE / 2, y - CELL_SIZE / 2


# ---------------------------------------------------------------------------
# Turtle setup. `screen` is the window itself; `wall_pen` draws every wall
# square once; `dot_pen` redraws the remaining dots every frame (since
# they disappear one at a time); `text_pen` draws the score / status text.
# Pac-Man and the ghost are each their own turtle "sprite", moved with
# goto() instead of being drawn stroke-by-stroke like the walls.
# ---------------------------------------------------------------------------
screen = turtle.Screen()
screen.setup(BOARD_WIDTH + 80, BOARD_HEIGHT + 100)
screen.bgcolor("black")
screen.title("Turtle Pac-Man")
screen.tracer(0)   # we redraw by hand and call screen.update() ourselves

wall_pen = turtle.Turtle(visible=False)
wall_pen.speed(0)
wall_pen.color("blue")
wall_pen.penup()

dot_pen = turtle.Turtle(visible=False)
dot_pen.speed(0)
dot_pen.color("white")
dot_pen.penup()

text_pen = turtle.Turtle(visible=False)
text_pen.speed(0)
text_pen.color("white")
text_pen.penup()

pacman_turtle = turtle.Turtle()
pacman_turtle.shape("circle")
pacman_turtle.color("yellow")
pacman_turtle.shapesize(CELL_SIZE / 20)   # turtle's default circle is 20px across
pacman_turtle.penup()
pacman_turtle.speed(0)

ghost_turtle = turtle.Turtle()
ghost_turtle.shape("circle")
ghost_turtle.color("red")
ghost_turtle.shapesize(CELL_SIZE / 20)
ghost_turtle.penup()
ghost_turtle.speed(0)


def draw_wall_square(row: int, col: int) -> None:
    """Draw one filled wall square using ``wall_pen``.

    A square is drawn by walking a pen in a loop: move forward one side's
    length, turn 90 degrees, and repeat four times -- the same technique
    used for every block in Turtle Tetris (see that project's SPEC.md if
    you want an even more detailed walkthrough of *why* this works).

    Args:
        row: The wall square's row on the grid.
        col: The wall square's column on the grid.

    Returns:
        None. Draws directly into the off-screen buffer.
    """
    x, y = cell_top_left(row, col)
    wall_pen.goto(x, y)
    wall_pen.fillcolor("blue")
    wall_pen.pendown()
    wall_pen.begin_fill()
    for _ in range(4):          # [LOOP] a square has four equal sides
        wall_pen.forward(CELL_SIZE)
        wall_pen.right(90)
    wall_pen.end_fill()
    wall_pen.penup()


def draw_walls(grid: Grid) -> None:
    """Draw every wall square in the maze, once, at startup.

    Walls never move or disappear, so -- unlike the dots -- this only
    needs to run a single time, before the game loop starts.

    Args:
        grid: The maze grid to scan for wall squares.

    Returns:
        None.
    """
    for row_index in range(GRID_ROWS):            # [LOOP]
        for col_index in range(GRID_COLS):           # [LOOP] (nested)
            if logic.is_wall(grid, row_index, col_index):    # [CONDITIONAL]
                draw_wall_square(row_index, col_index)


def draw_dots(grid: Grid) -> None:
    """Redraw every dot still remaining on the grid.

    Dots disappear one at a time as Pac-Man eats them, so -- unlike the
    walls -- this has to be cleared and redrawn every frame to match
    whichever dots are still left.

    Args:
        grid: The current maze grid.

    Returns:
        None.
    """
    dot_pen.clear()
    for row_index in range(GRID_ROWS):             # [LOOP]
        for col_index in range(GRID_COLS):            # [LOOP] (nested)
            if grid[row_index][col_index] == logic.DOT:    # [CONDITIONAL]
                x, y = cell_center(row_index, col_index)
                dot_pen.goto(x, y)
                dot_pen.dot(CELL_SIZE // 4, "white")


def draw_status(score: int, message: str | None) -> None:
    """Draw the score line, plus an optional game-over/win message.

    Args:
        score: The player's current score.
        message: An extra message to show (e.g. ``"YOU WIN!"`` or
            ``"GAME OVER"``), or ``None`` during normal play.

    Returns:
        None.
    """
    text_pen.clear()
    text_pen.goto(ORIGIN_X, ORIGIN_Y + 20)
    line = f"Score: {score}    Arrow keys move Pac-Man"
    if message is not None:                # [CONDITIONAL]
        line = f"Score: {score}    {message} (close the window to quit)"
    text_pen.write(line, font=("Courier New", 13, "bold"))


# ---------------------------------------------------------------------------
# Mutable game state. These are plain module-level variables; the key
# handler and game-loop functions below use `global` to update them.
# ---------------------------------------------------------------------------
def _require_start(position: Position | None, label: str) -> Position:
    """Unwrap a starting position found by parse_maze(), or fail loudly.

    parse_maze() has to report "P"/"G" as possibly missing (``None``)
    since it can be handed *any* maze blueprint, including ones built for
    tests that don't have both. The shipped :data:`pacman_logic.MAZE_TEMPLATE`
    always has exactly one of each (see
    ``test_shipped_maze_template_has_exactly_one_pacman_and_one_ghost`` in
    ``test_pacman_logic.py``), so here -- and only here -- it's safe to
    treat a missing position as a bug rather than something to handle.
    """
    if position is None:                                          # [CONDITIONAL]
        raise ValueError(f"MAZE_TEMPLATE has no {label} start square")
    return position


grid, _pacman_start, _ghost_start = logic.parse_maze(logic.MAZE_TEMPLATE)
pacman_position: Position = _require_start(_pacman_start, "'P'")
ghost_position: Position = _require_start(_ghost_start, "'G'")
score: int = 0
is_game_over: bool = False
status_message: str | None = None


def refresh() -> None:
    """Redraw the dots, Pac-Man, the ghost, and the status line to match
    the current game state, then flip the finished frame onto the screen.
    """
    draw_dots(grid)
    pacman_turtle.goto(*cell_center(*pacman_position))
    ghost_turtle.goto(*cell_center(*ghost_position))
    draw_status(score, status_message)
    screen.update()


def end_game(message: str) -> None:
    """Stop the game and show a final message.

    Args:
        message: The message to display, e.g. ``"YOU WIN!"`` or
            ``"GAME OVER"``.

    Returns:
        None. Sets the module-level ``is_game_over``/``status_message``
        flags that every key handler and :func:`ghost_step` check before
        doing anything else.
    """
    global is_game_over, status_message
    is_game_over = True
    status_message = message


def try_move_pacman(direction: str) -> None:
    """Shared logic for every arrow-key handler: move Pac-Man, eat a dot
    if there is one, and check for a win or a collision with the ghost.

    Args:
        direction: One of the keys of :data:`pacman_logic.DIRECTIONS`.

    Returns:
        None.
    """
    global pacman_position, score

    if is_game_over:                # [CONDITIONAL] ignore key presses once the game has ended
        return

    pacman_position = logic.move_pacman(grid, pacman_position, direction)

    if logic.eat_dot(grid, pacman_position):        # [CONDITIONAL]
        score += logic.SCORE_PER_DOT

    if logic.check_collision(pacman_position, ghost_position):    # [CONDITIONAL]
        end_game("GAME OVER -- the ghost got you!")
    elif logic.has_won(grid):                                       # [CONDITIONAL]
        end_game("YOU WIN!")

    refresh()


def move_up() -> None:
    """Key handler: move Pac-Man up one square."""
    try_move_pacman("UP")


def move_down() -> None:
    """Key handler: move Pac-Man down one square."""
    try_move_pacman("DOWN")


def move_left() -> None:
    """Key handler: move Pac-Man left one square."""
    try_move_pacman("LEFT")


def move_right() -> None:
    """Key handler: move Pac-Man right one square."""
    try_move_pacman("RIGHT")


def ghost_step() -> None:
    """One tick of the automatic ghost-chasing loop.

    Scheduled repeatedly with ``screen.ontimer`` so the ghost keeps
    chasing Pac-Man on its own, whether or not the player presses
    anything.

    Returns:
        None.
    """
    global ghost_position

    if not is_game_over:                        # [CONDITIONAL]
        ghost_position = logic.move_ghost(grid, ghost_position, pacman_position)

        if logic.check_collision(pacman_position, ghost_position):    # [CONDITIONAL]
            end_game("GAME OVER -- the ghost got you!")

        refresh()
        screen.ontimer(ghost_step, GHOST_STEP_MS)


def main() -> None:
    """Wire up key bindings, draw the first frame, and start the game loop."""
    screen.listen()
    screen.onkey(move_up, "Up")
    screen.onkey(move_down, "Down")
    screen.onkey(move_left, "Left")
    screen.onkey(move_right, "Right")

    draw_walls(grid)
    refresh()
    screen.ontimer(ghost_step, GHOST_STEP_MS)
    screen.mainloop()


if __name__ == "__main__":
    main()
