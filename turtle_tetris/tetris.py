"""
tetris.py
---------
The visible part of Turtle Tetris: drawing the board and pieces on
screen with the ``turtle`` module, and reacting to keyboard presses.

All of the actual game *rules* (how pieces move, collide, lock, and clear
lines) live in ``tetris_logic.py``. This file is only responsible for:

    1. Turning the logic module's board/piece data into shapes on screen.
    2. Listening for arrow-key / space-bar presses and calling the right
       logic functions in response.
    3. Running the game loop that makes pieces fall automatically.

Run it with:
    python3 tetris.py

Controls:
    Left / Right  - move the piece sideways
    Down          - soft drop (move down one row early)
    Up            - rotate the piece
    Space         - hard drop (slam the piece straight to the bottom)
"""

import turtle

import tetris_logic as logic
from tetris_logic import Board, Piece

# ---------------------------------------------------------------------------
# Layout constants (all plain numbers, named so the rest of the file reads
# like English).
# ---------------------------------------------------------------------------
CELL_SIZE: int = 30
BOARD_WIDTH: int = logic.COLS * CELL_SIZE
BOARD_HEIGHT: int = logic.ROWS * CELL_SIZE

# The board is drawn with (0, 0) at its top-left corner in "board pixel"
# space; ORIGIN_X/ORIGIN_Y translate that into turtle's screen coordinates,
# which put (0, 0) at the center of the window.
ORIGIN_X: int = -BOARD_WIDTH // 2
ORIGIN_Y: int = BOARD_HEIGHT // 2

FALL_DELAY_MS: int = 500   # how often the piece drops one row on its own


def cell_to_pixels(col: int, row: int) -> tuple[float, float]:
    """Convert a board (column, row) [TUPLE] into an on-screen (x, y) pixel.

    Args:
        col: Zero-based column index (0 is the leftmost column).
        row: Zero-based row index (0 is the topmost row).

    Returns:
        tuple[float, float]: the ``(x, y)`` pixel coordinates of that
        cell's top-left corner, in the turtle window's coordinate system.
    """
    x = ORIGIN_X + col * CELL_SIZE
    y = ORIGIN_Y - row * CELL_SIZE
    return x, y


# ---------------------------------------------------------------------------
# Turtle setup. `screen` is the window itself; `board_pen` draws the board
# border once; `blocks_pen` redraws the falling/locked squares every frame;
# `text_pen` draws the score / game-over text.
# ---------------------------------------------------------------------------
screen = turtle.Screen()
screen.setup(BOARD_WIDTH + 80, BOARD_HEIGHT + 100)
screen.bgcolor("black")
screen.title("Turtle Tetris")
screen.tracer(0)   # we redraw by hand and call screen.update() ourselves

board_pen = turtle.Turtle(visible=False)
board_pen.speed(0)
board_pen.color("white")
board_pen.penup()

blocks_pen = turtle.Turtle(visible=False)
blocks_pen.speed(0)
blocks_pen.penup()

text_pen = turtle.Turtle(visible=False)
text_pen.speed(0)
text_pen.color("white")
text_pen.penup()


def draw_square(pen: turtle.Turtle, x: float, y: float, color: str) -> None:
    """Draw one filled square of the board using a turtle.

    Args:
        pen: Which turtle to draw with.
        x: The x pixel coordinate of the square's top-left corner.
        y: The y pixel coordinate of the square's top-left corner.
        color: The fill color name [STRING], e.g. ``"cyan"``.

    Returns:
        None. The square is drawn directly onto the screen (well, into an
        off-screen buffer until :func:`turtle.Screen.update` is called).
    """
    pen.goto(x, y)
    pen.fillcolor(color)
    pen.pendown()
    pen.begin_fill()
    for _ in range(4):          # [LOOP] a square has four equal sides
        pen.forward(CELL_SIZE)
        pen.right(90)
    pen.end_fill()
    pen.penup()


def draw_border() -> None:
    """Draw the board's outer rectangle once, using ``board_pen``.

    This never needs to be redrawn every frame, since it never changes --
    that's why it uses its own turtle, separate from ``blocks_pen``.
    """
    board_pen.goto(ORIGIN_X, ORIGIN_Y)
    board_pen.pendown()
    for _ in range(2):           # [LOOP] a rectangle has two pairs of sides
        board_pen.forward(BOARD_WIDTH)
        board_pen.right(90)
        board_pen.forward(BOARD_HEIGHT)
        board_pen.right(90)
    board_pen.penup()


def draw_board(board: Board, piece: Piece, is_game_over: bool) -> None:
    """Redraw every locked block and the current falling piece.

    Args:
        board: The current board grid ([LIST] of [LIST] of colors/None).
        piece: The piece currently falling ([DICTIONARY]).
        is_game_over: Whether the game has ended; if so, the falling
            piece is not drawn (it "froze" at the moment of game over).

    Returns:
        None. Draws to the screen and calls ``screen.update()``.
    """
    blocks_pen.clear()

    for row_index in range(logic.ROWS):          # [LOOP]
        for col_index in range(logic.COLS):        # [LOOP] (nested!)
            color = board[row_index][col_index]
            if color is not None:                    # [CONDITIONAL]
                x, y = cell_to_pixels(col_index, row_index)
                draw_square(blocks_pen, x, y, color)

    if not is_game_over:                          # [CONDITIONAL]
        piece_color = logic.COLORS[piece["name"]]
        for (dc, dr) in logic.piece_blocks(piece):   # [LOOP]
            col_index = piece["col"] + dc
            row_index = piece["row"] + dr
            if row_index >= 0:                          # [CONDITIONAL]
                x, y = cell_to_pixels(col_index, row_index)
                draw_square(blocks_pen, x, y, piece_color)

    screen.update()


def draw_status(score: int, is_game_over: bool) -> None:
    """Draw the score line (or the game-over message) above the board.

    Args:
        score: The player's current score.
        is_game_over: Whether to show "GAME OVER" instead of the controls
            reminder.

    Returns:
        None.
    """
    text_pen.clear()
    text_pen.goto(ORIGIN_X, ORIGIN_Y + 20)
    if is_game_over:                                # [CONDITIONAL]
        message = f"GAME OVER -- final score: {score}   (close the window to quit)"
    else:
        message = f"Score: {score}    Left/Right move, Up rotates, Down soft-drops, Space hard-drops"
    text_pen.write(message, font=("Courier New", 13, "bold"))


# ---------------------------------------------------------------------------
# Mutable game state. These are plain module-level variables; the key
# handler and game-loop functions below use `global` to update them.
# ---------------------------------------------------------------------------
board: Board = logic.new_board()
current_piece: Piece = logic.new_piece()
score: int = 0
is_game_over: bool = False


def refresh() -> None:
    """Redraw the board and status line to match the current game state."""
    draw_board(board, current_piece, is_game_over)
    draw_status(score, is_game_over)
    screen.update()


def spawn_next_piece() -> None:
    """Replace ``current_piece`` with a fresh one, and check for game over.

    Called right after a piece locks into place. If the brand-new piece
    immediately overlaps something already on the board, there is no room
    left near the top, and the game ends.

    Returns:
        None. Updates the module-level ``current_piece`` and
        ``is_game_over`` variables.
    """
    global current_piece, is_game_over
    current_piece = logic.new_piece()
    if not logic.valid_position(board, current_piece):   # [CONDITIONAL]
        is_game_over = True


def land_current_piece() -> None:
    """Lock the current piece in place, score any cleared lines, and spawn
    the next piece.

    Returns:
        None.
    """
    global score
    logic.lock_piece(board, current_piece)
    lines_cleared = logic.clear_full_rows(board)
    score += logic.score_for_lines(lines_cleared)
    spawn_next_piece()


def move_left() -> None:
    """Key handler: move the falling piece one column to the left."""
    if is_game_over:                                       # [CONDITIONAL]
        return
    if logic.valid_position(board, current_piece, d_col=-1):  # [CONDITIONAL]
        current_piece["col"] -= 1
        refresh()


def move_right() -> None:
    """Key handler: move the falling piece one column to the right."""
    if is_game_over:
        return
    if logic.valid_position(board, current_piece, d_col=1):
        current_piece["col"] += 1
        refresh()


def rotate_piece() -> None:
    """Key handler: rotate the falling piece to its next rotation state."""
    if is_game_over:
        return
    states = logic.SHAPES[current_piece["name"]]
    next_rotation = (current_piece["rotation"] + 1) % len(states)
    if logic.valid_position(board, current_piece, rotation=next_rotation):
        current_piece["rotation"] = next_rotation
        refresh()


def soft_drop() -> None:
    """Key handler: move the falling piece down one row early."""
    if is_game_over:
        return
    if logic.valid_position(board, current_piece, d_row=1):
        current_piece["row"] += 1
        refresh()


def hard_drop() -> None:
    """Key handler: instantly drop the piece as far down as it can go."""
    if is_game_over:
        return
    while logic.valid_position(board, current_piece, d_row=1):   # [LOOP]
        current_piece["row"] += 1
    land_current_piece()
    refresh()


def game_step() -> None:
    """One tick of the automatic game loop: try to fall, or lock and spawn.

    Scheduled repeatedly with ``screen.ontimer`` so the piece falls on its
    own even if the player never presses a key.

    Returns:
        None.
    """
    if not is_game_over:                                       # [CONDITIONAL]
        if logic.valid_position(board, current_piece, d_row=1):  # [CONDITIONAL]
            current_piece["row"] += 1
        else:
            land_current_piece()
        refresh()
        screen.ontimer(game_step, FALL_DELAY_MS)


def main() -> None:
    """Wire up key bindings, draw the first frame, and start the game loop."""
    screen.listen()
    screen.onkey(move_left, "Left")
    screen.onkey(move_right, "Right")
    screen.onkey(soft_drop, "Down")
    screen.onkey(rotate_piece, "Up")
    screen.onkey(hard_drop, "space")

    draw_border()
    refresh()
    screen.ontimer(game_step, FALL_DELAY_MS)
    screen.mainloop()


if __name__ == "__main__":
    main()
