"""
test_tetris_logic.py
---------------------
Automated tests for tetris_logic.py.

These tests do NOT open any window -- tetris_logic.py has no turtle/tkinter
code in it at all, so it can be exercised directly with plain Python.

Run all tests with:
    python3 -m unittest test_tetris_logic.py -v

or simply:
    python3 test_tetris_logic.py
"""

import unittest

import tetris_logic as logic


class NewBoardTests(unittest.TestCase):
    """Tests for logic.new_board()."""

    def test_has_correct_number_of_rows(self) -> None:
        board = logic.new_board()
        self.assertEqual(len(board), logic.ROWS)

    def test_every_row_has_correct_number_of_columns(self) -> None:
        board = logic.new_board()
        for row in board:
            self.assertEqual(len(row), logic.COLS)

    def test_every_cell_starts_empty(self) -> None:
        board = logic.new_board()
        for row in board:
            for cell in row:
                self.assertIsNone(cell)

    def test_rows_are_independent_lists(self) -> None:
        # A classic beginner bug is `[[None] * COLS] * ROWS`, which makes
        # every row the SAME list. Editing one row should not affect others.
        board = logic.new_board()
        board[0][0] = "red"
        self.assertIsNone(board[1][0])


class NewPieceTests(unittest.TestCase):
    """Tests for logic.new_piece()."""

    def test_piece_has_all_expected_keys(self) -> None:
        piece = logic.new_piece()
        for key in ("name", "rotation", "col", "row"):
            self.assertIn(key, piece)

    def test_piece_name_is_a_known_shape(self) -> None:
        piece = logic.new_piece()
        self.assertIn(piece["name"], logic.SHAPES)

    def test_piece_starts_at_rotation_zero(self) -> None:
        piece = logic.new_piece()
        self.assertEqual(piece["rotation"], 0)

    def test_piece_spawns_within_column_bounds(self) -> None:
        # It doesn't have to be centered perfectly, but it must not spawn
        # partially off the board horizontally for any shape.
        for _ in range(50):
            piece = logic.new_piece()
            for (dc, _dr) in logic.piece_blocks(piece):
                col = piece["col"] + dc
                self.assertTrue(0 <= col < logic.COLS)

    def test_many_new_pieces_eventually_cover_all_shapes(self) -> None:
        # Not a strict guarantee (it's random!), but with 200 draws the
        # odds of missing a shape are astronomically small, so this also
        # catches an accidental typo in SHAPES.keys().
        seen = {logic.new_piece()["name"] for _ in range(200)}
        self.assertEqual(seen, set(logic.SHAPES.keys()))


class ShapeDataTests(unittest.TestCase):
    """Sanity checks on the raw SHAPES / COLORS data itself."""

    def test_every_shape_has_a_color(self) -> None:
        for name in logic.SHAPES:
            self.assertIn(name, logic.COLORS)

    def test_every_rotation_state_has_exactly_four_blocks(self) -> None:
        for name, states in logic.SHAPES.items():
            for rotation_index, blocks in enumerate(states):
                with self.subTest(shape=name, rotation=rotation_index):
                    self.assertEqual(len(blocks), 4)

    def test_every_block_fits_in_a_4x4_box(self) -> None:
        for name, states in logic.SHAPES.items():
            for rotation_index, blocks in enumerate(states):
                for (col, row) in blocks:
                    with self.subTest(shape=name, rotation=rotation_index):
                        self.assertTrue(0 <= col < 4)
                        self.assertTrue(0 <= row < 4)

    def test_no_duplicate_blocks_within_a_rotation(self) -> None:
        for name, states in logic.SHAPES.items():
            for rotation_index, blocks in enumerate(states):
                with self.subTest(shape=name, rotation=rotation_index):
                    self.assertEqual(len(blocks), len(set(blocks)))


class PieceBlocksTests(unittest.TestCase):
    """Tests for logic.piece_blocks()."""

    def test_defaults_to_pieces_own_rotation(self) -> None:
        piece: logic.Piece = {"name": "T", "rotation": 2, "col": 0, "row": 0}
        expected = logic.SHAPES["T"][2]
        self.assertEqual(logic.piece_blocks(piece), expected)

    def test_explicit_rotation_overrides_pieces_rotation(self) -> None:
        piece: logic.Piece = {"name": "T", "rotation": 0, "col": 0, "row": 0}
        expected = logic.SHAPES["T"][3]
        self.assertEqual(logic.piece_blocks(piece, rotation=3), expected)

    def test_rotation_wraps_around_with_modulo(self) -> None:
        # "T" has 4 rotation states (indices 0-3), so asking for state 4
        # should wrap back around to state 0.
        piece: logic.Piece = {"name": "T", "rotation": 0, "col": 0, "row": 0}
        self.assertEqual(
            logic.piece_blocks(piece, rotation=4),
            logic.piece_blocks(piece, rotation=0),
        )

    def test_single_rotation_shape_ignores_rotation_number(self) -> None:
        # "O" only has one rotation state, so ANY rotation number should
        # land on that same single state.
        piece: logic.Piece = {"name": "O", "rotation": 0, "col": 0, "row": 0}
        only_state = logic.SHAPES["O"][0]
        self.assertEqual(logic.piece_blocks(piece, rotation=7), only_state)


class ValidPositionTests(unittest.TestCase):
    """Tests for logic.valid_position()."""

    def setUp(self) -> None:
        self.board = logic.new_board()
        # An O piece (a simple 2x2 square) sitting in the middle of the
        # board, far from every edge, is our "obviously legal" baseline.
        self.piece: logic.Piece = {"name": "O", "rotation": 0, "col": 4, "row": 4}

    def test_starting_position_is_valid_on_empty_board(self) -> None:
        self.assertTrue(logic.valid_position(self.board, self.piece))

    def test_rejects_moving_off_the_left_edge(self) -> None:
        self.assertFalse(logic.valid_position(self.board, self.piece, d_col=-10))

    def test_rejects_moving_off_the_right_edge(self) -> None:
        self.assertFalse(logic.valid_position(self.board, self.piece, d_col=10))

    def test_rejects_moving_off_the_bottom_edge(self) -> None:
        self.assertFalse(logic.valid_position(self.board, self.piece, d_row=100))

    def test_allows_the_topmost_legal_column(self) -> None:
        edge_piece: logic.Piece = {"name": "O", "rotation": 0, "col": -1, "row": 4}
        # Blocks are at columns (col+1, col+2) = (0, 1) -- exactly on the
        # left wall, so this should be valid.
        self.assertTrue(logic.valid_position(self.board, edge_piece))

    def test_rejects_landing_on_a_locked_block(self) -> None:
        self.board[5][5] = "yellow"  # pretend something already landed here
        self.assertFalse(logic.valid_position(self.board, self.piece))

    def test_allows_landing_next_to_a_locked_block(self) -> None:
        self.board[5][9] = "yellow"  # far away from the O piece at col 4-5
        self.assertTrue(logic.valid_position(self.board, self.piece))

    def test_rotation_argument_is_checked_without_mutating_piece(self) -> None:
        t_piece: logic.Piece = {"name": "T", "rotation": 0, "col": 4, "row": 4}
        before = dict(t_piece)
        logic.valid_position(self.board, t_piece, rotation=1)
        self.assertEqual(t_piece, before)


class LockPieceTests(unittest.TestCase):
    """Tests for logic.lock_piece()."""

    def test_writes_the_pieces_color_into_every_block(self) -> None:
        board = logic.new_board()
        piece: logic.Piece = {"name": "O", "rotation": 0, "col": 0, "row": 0}
        logic.lock_piece(board, piece)
        for (dc, dr) in logic.piece_blocks(piece):
            self.assertEqual(board[dr][dc], "yellow")

    def test_does_not_touch_unrelated_cells(self) -> None:
        board = logic.new_board()
        piece: logic.Piece = {"name": "O", "rotation": 0, "col": 0, "row": 0}
        logic.lock_piece(board, piece)
        self.assertIsNone(board[0][5])

    def test_ignores_blocks_above_the_visible_board(self) -> None:
        # A block with a negative row would be above the top of the
        # screen; locking it should not raise an error or wrap around to
        # the bottom of the board.
        board = logic.new_board()
        piece: logic.Piece = {"name": "O", "rotation": 0, "col": 0, "row": -1}
        logic.lock_piece(board, piece)  # should not raise
        self.assertIsNone(board[-1][0])
        self.assertIsNone(board[-1][1])


class ClearFullRowsTests(unittest.TestCase):
    """Tests for logic.clear_full_rows()."""

    def test_no_lines_cleared_on_an_empty_board(self) -> None:
        board = logic.new_board()
        self.assertEqual(logic.clear_full_rows(board), 0)

    def test_board_shape_is_preserved(self) -> None:
        board = logic.new_board()
        logic.clear_full_rows(board)
        self.assertEqual(len(board), logic.ROWS)
        for row in board:
            self.assertEqual(len(row), logic.COLS)

    def test_clears_exactly_one_full_row(self) -> None:
        board = logic.new_board()
        bottom_row = logic.ROWS - 1
        board[bottom_row] = ["red"] * logic.COLS
        cleared = logic.clear_full_rows(board)
        self.assertEqual(cleared, 1)
        # The now-empty new row should be at the top...
        self.assertTrue(all(cell is None for cell in board[0]))
        # ...and no row should still be completely full of "red".
        self.assertFalse(any(all(cell == "red" for cell in row) for row in board))

    def test_partially_full_row_is_not_cleared(self) -> None:
        board = logic.new_board()
        row_index = 3
        board[row_index] = ["red"] * (logic.COLS - 1) + [None]
        cleared = logic.clear_full_rows(board)
        self.assertEqual(cleared, 0)

    def test_clears_a_tetris_all_four_lines_at_once(self) -> None:
        board = logic.new_board()
        for row_index in range(4):
            board[row_index] = ["blue"] * logic.COLS
        cleared = logic.clear_full_rows(board)
        self.assertEqual(cleared, 4)
        for row in board:
            self.assertTrue(all(cell is None for cell in row))

    def test_rows_above_a_cleared_row_shift_down(self) -> None:
        board = logic.new_board()
        board[0][0] = "green"          # a single block sitting near the top
        board[logic.ROWS - 1] = ["red"] * logic.COLS   # full row beneath it
        logic.clear_full_rows(board)
        # The single green block should have shifted down by one row.
        self.assertEqual(board[1][0], "green")
        self.assertIsNone(board[0][0])


class ScoreForLinesTests(unittest.TestCase):
    """Tests for logic.score_for_lines()."""

    def test_known_line_counts(self) -> None:
        expected = {0: 0, 1: 100, 2: 300, 3: 500, 4: 800}
        for lines_cleared, points in expected.items():
            with self.subTest(lines_cleared=lines_cleared):
                self.assertEqual(logic.score_for_lines(lines_cleared), points)


class IntegrationTests(unittest.TestCase):
    """A couple of end-to-end scenarios combining several functions."""

    def test_dropping_and_locking_a_piece_can_trigger_a_line_clear(self) -> None:
        board = logic.new_board()
        # Fill an entire row except for the two rightmost columns.
        bottom_row = logic.ROWS - 1
        board[bottom_row] = ["red"] * (logic.COLS - 2) + [None, None]

        # An O piece dropped into the last two columns should complete it.
        # The "O" shape's blocks are offset by +1/+2 columns from its
        # anchor (see SHAPES["O"] in tetris_logic.py), so the anchor
        # itself sits three columns from the right edge.
        piece: logic.Piece = {
            "name": "O",
            "rotation": 0,
            "col": logic.COLS - 3,
            "row": bottom_row - 2,
        }
        self.assertTrue(logic.valid_position(board, piece, d_row=1))
        piece["row"] += 1
        logic.lock_piece(board, piece)

        cleared = logic.clear_full_rows(board)
        self.assertEqual(cleared, 1)
        self.assertEqual(logic.score_for_lines(cleared), 100)

    def test_game_over_condition_when_stack_reaches_the_top(self) -> None:
        board = logic.new_board()
        # Fill the very top row completely, simulating a stack that has
        # reached the ceiling.
        board[0] = ["red"] * logic.COLS
        new = logic.new_piece()
        new["col"] = logic.COLS // 2 - 2
        new["row"] = 0
        # However the piece is shaped, it should not fit on top of a
        # completely full top row -- this is exactly the game-over check
        # tetris.py performs after spawning each new piece.
        self.assertFalse(logic.valid_position(board, new))


if __name__ == "__main__":
    unittest.main()
