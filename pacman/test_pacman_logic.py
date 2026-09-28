"""
test_pacman_logic.py
---------------------
Automated tests for pacman_logic.py.

These tests do NOT open any window -- pacman_logic.py has no turtle/tkinter
code in it at all, so it can be exercised directly with plain Python.

Run all tests with:
    python3 -m unittest test_pacman_logic.py -v

or simply:
    python3 test_pacman_logic.py
"""

import unittest

import pacman_logic as logic


def make_grid(rows: list[str]) -> logic.Grid:
    """Test helper: build a small grid directly from strings, without going
    through parse_maze() (useful when a test doesn't need a P/G start)."""
    return [list(row) for row in rows]


class ParseMazeTests(unittest.TestCase):
    """Tests for logic.parse_maze()."""

    def test_grid_has_one_row_per_template_line(self) -> None:
        grid, _pacman, _ghost = logic.parse_maze(logic.MAZE_TEMPLATE)
        self.assertEqual(len(grid), len(logic.MAZE_TEMPLATE))

    def test_every_row_matches_its_template_length(self) -> None:
        grid, _pacman, _ghost = logic.parse_maze(logic.MAZE_TEMPLATE)
        for row_index, row in enumerate(grid):
            with self.subTest(row=row_index):
                self.assertEqual(len(row), len(logic.MAZE_TEMPLATE[row_index]))

    def test_finds_pacman_start_position(self) -> None:
        template = [
            "###",
            "#P#",
            "###",
        ]
        _grid, pacman_start, _ghost = logic.parse_maze(template)
        self.assertEqual(pacman_start, (1, 1))

    def test_finds_ghost_start_position(self) -> None:
        template = [
            "#####",
            "#.G.#",
            "#####",
        ]
        _grid, _pacman, ghost_start = logic.parse_maze(template)
        self.assertEqual(ghost_start, (1, 2))

    def test_start_squares_become_empty_floor_not_walls_or_dots(self) -> None:
        template = [
            "#####",
            "#P.G#",
            "#####",
        ]
        grid, pacman_start, ghost_start = logic.parse_maze(template)
        assert pacman_start is not None
        assert ghost_start is not None
        prow, pcol = pacman_start
        grow, gcol = ghost_start
        self.assertEqual(grid[prow][pcol], logic.EMPTY)
        self.assertEqual(grid[grow][gcol], logic.EMPTY)

    def test_dots_and_walls_are_preserved(self) -> None:
        template = [
            "#####",
            "#P.G#",
            "#####",
        ]
        grid, _pacman, _ghost = logic.parse_maze(template)
        self.assertEqual(grid[0], list("#####"))
        self.assertEqual(grid[1][2], logic.DOT)

    def test_rows_are_independent_lists(self) -> None:
        # A classic beginner bug is building a grid where every row is
        # secretly the SAME list. Editing one row should not affect others.
        grid, _pacman, _ghost = logic.parse_maze(logic.MAZE_TEMPLATE)
        original = grid[2][2]
        grid[1][1] = "Z"
        self.assertEqual(grid[2][2], original)

    def test_shipped_maze_template_has_exactly_one_pacman_and_one_ghost(self) -> None:
        pacman_count = sum(row.count(logic.PACMAN_START) for row in logic.MAZE_TEMPLATE)
        ghost_count = sum(row.count(logic.GHOST_START) for row in logic.MAZE_TEMPLATE)
        self.assertEqual(pacman_count, 1)
        self.assertEqual(ghost_count, 1)

    def test_shipped_maze_template_rows_are_all_equal_length(self) -> None:
        widths = {len(row) for row in logic.MAZE_TEMPLATE}
        self.assertEqual(len(widths), 1)


class InBoundsTests(unittest.TestCase):
    """Tests for logic.in_bounds()."""

    def setUp(self) -> None:
        self.grid = make_grid(["###", "#.#", "###"])

    def test_center_square_is_in_bounds(self) -> None:
        self.assertTrue(logic.in_bounds(self.grid, 1, 1))

    def test_negative_row_is_out_of_bounds(self) -> None:
        self.assertFalse(logic.in_bounds(self.grid, -1, 1))

    def test_negative_col_is_out_of_bounds(self) -> None:
        self.assertFalse(logic.in_bounds(self.grid, 1, -1))

    def test_row_past_the_last_row_is_out_of_bounds(self) -> None:
        self.assertFalse(logic.in_bounds(self.grid, 3, 1))

    def test_col_past_the_last_col_is_out_of_bounds(self) -> None:
        self.assertFalse(logic.in_bounds(self.grid, 1, 3))


class IsWallTests(unittest.TestCase):
    """Tests for logic.is_wall()."""

    def setUp(self) -> None:
        self.grid = make_grid(["###", "#.#", "###"])

    def test_border_square_is_a_wall(self) -> None:
        self.assertTrue(logic.is_wall(self.grid, 0, 0))

    def test_dot_square_is_not_a_wall(self) -> None:
        self.assertFalse(logic.is_wall(self.grid, 1, 1))


class CanMoveTests(unittest.TestCase):
    """Tests for logic.can_move()."""

    def setUp(self) -> None:
        self.grid = make_grid(
            [
                "#####",
                "#...#",
                "#.#.#",
                "#...#",
                "#####",
            ]
        )

    def test_can_move_into_open_floor(self) -> None:
        self.assertTrue(logic.can_move(self.grid, (1, 1), "RIGHT"))

    def test_cannot_move_into_a_wall(self) -> None:
        self.assertFalse(logic.can_move(self.grid, (1, 2), "DOWN"))

    def test_cannot_move_off_the_top_edge(self) -> None:
        self.assertFalse(logic.can_move(self.grid, (0, 1), "UP"))

    def test_cannot_move_off_the_left_edge(self) -> None:
        self.assertFalse(logic.can_move(self.grid, (1, 0), "LEFT"))

    def test_every_direction_key_is_recognized(self) -> None:
        # A quick sanity check that all four DIRECTIONS keys work with
        # can_move() without raising a KeyError.
        for direction in logic.DIRECTIONS:
            with self.subTest(direction=direction):
                logic.can_move(self.grid, (1, 1), direction)  # should not raise


class MovePositionTests(unittest.TestCase):
    """Tests for logic.move_position()."""

    def test_up_decreases_row(self) -> None:
        self.assertEqual(logic.move_position((5, 5), "UP"), (4, 5))

    def test_down_increases_row(self) -> None:
        self.assertEqual(logic.move_position((5, 5), "DOWN"), (6, 5))

    def test_left_decreases_col(self) -> None:
        self.assertEqual(logic.move_position((5, 5), "LEFT"), (5, 4))

    def test_right_increases_col(self) -> None:
        self.assertEqual(logic.move_position((5, 5), "RIGHT"), (5, 6))

    def test_does_not_mutate_the_original_tuple(self) -> None:
        # Tuples are immutable in Python, but this test documents that
        # move_position() always returns a brand-new tuple rather than
        # (somehow) changing the one it was given.
        start = (2, 2)
        result = logic.move_position(start, "UP")
        self.assertEqual(start, (2, 2))
        self.assertNotEqual(result, start)


class MovePacmanTests(unittest.TestCase):
    """Tests for logic.move_pacman()."""

    def setUp(self) -> None:
        self.grid = make_grid(
            [
                "#####",
                "#...#",
                "#.#.#",
                "#...#",
                "#####",
            ]
        )

    def test_no_direction_yet_leaves_position_unchanged(self) -> None:
        self.assertEqual(logic.move_pacman(self.grid, (1, 1), None), (1, 1))

    def test_legal_move_updates_position(self) -> None:
        self.assertEqual(logic.move_pacman(self.grid, (1, 1), "RIGHT"), (1, 2))

    def test_bumping_into_a_wall_leaves_position_unchanged(self) -> None:
        self.assertEqual(logic.move_pacman(self.grid, (1, 2), "DOWN"), (1, 2))

    def test_bumping_into_the_edge_leaves_position_unchanged(self) -> None:
        self.assertEqual(logic.move_pacman(self.grid, (1, 1), "UP"), (1, 1))


class EatDotTests(unittest.TestCase):
    """Tests for logic.eat_dot()."""

    def test_eating_a_dot_returns_true_and_clears_the_cell(self) -> None:
        grid = make_grid(["#.#"])
        ate = logic.eat_dot(grid, (0, 1))
        self.assertTrue(ate)
        self.assertEqual(grid[0][1], logic.EMPTY)

    def test_eating_empty_floor_returns_false_and_changes_nothing(self) -> None:
        grid = make_grid(["# #"])
        ate = logic.eat_dot(grid, (0, 1))
        self.assertFalse(ate)
        self.assertEqual(grid[0][1], logic.EMPTY)

    def test_eating_the_same_dot_twice_only_counts_once(self) -> None:
        grid = make_grid(["#.#"])
        first = logic.eat_dot(grid, (0, 1))
        second = logic.eat_dot(grid, (0, 1))
        self.assertTrue(first)
        self.assertFalse(second)


class CountDotsTests(unittest.TestCase):
    """Tests for logic.count_dots()."""

    def test_counts_zero_on_an_empty_grid(self) -> None:
        grid = make_grid(["#####", "#   #", "#####"])
        self.assertEqual(logic.count_dots(grid), 0)

    def test_counts_dots_across_multiple_rows(self) -> None:
        grid = make_grid(["#.#.#", "#...#", "#.#.#"])
        self.assertEqual(logic.count_dots(grid), 7)

    def test_matches_the_shipped_maze_templates_dot_count(self) -> None:
        grid, _pacman, _ghost = logic.parse_maze(logic.MAZE_TEMPLATE)
        expected = sum(row.count(logic.DOT) for row in logic.MAZE_TEMPLATE)
        self.assertEqual(logic.count_dots(grid), expected)


class HasWonTests(unittest.TestCase):
    """Tests for logic.has_won()."""

    def test_false_while_dots_remain(self) -> None:
        grid = make_grid(["#.#"])
        self.assertFalse(logic.has_won(grid))

    def test_true_once_every_dot_is_eaten(self) -> None:
        grid = make_grid(["#.#"])
        logic.eat_dot(grid, (0, 1))
        self.assertTrue(logic.has_won(grid))

    def test_true_on_a_grid_that_never_had_any_dots(self) -> None:
        grid = make_grid(["#  #"])
        self.assertTrue(logic.has_won(grid))


class CheckCollisionTests(unittest.TestCase):
    """Tests for logic.check_collision()."""

    def test_same_square_is_a_collision(self) -> None:
        self.assertTrue(logic.check_collision((3, 4), (3, 4)))

    def test_different_squares_are_not_a_collision(self) -> None:
        self.assertFalse(logic.check_collision((3, 4), (3, 5)))


class ChooseGhostDirectionTests(unittest.TestCase):
    """Tests for logic.choose_ghost_direction()."""

    def setUp(self) -> None:
        # A big open room with no interior walls, so every test below is
        # only about the *choice* of direction, not wall-dodging.
        self.open_grid = make_grid(
            [
                "#######",
                "#.....#",
                "#.....#",
                "#.....#",
                "#.....#",
                "#.....#",
                "#######",
            ]
        )

    def test_prefers_moving_down_when_pacman_is_mostly_below(self) -> None:
        direction = logic.choose_ghost_direction(self.open_grid, (1, 3), (5, 3))
        self.assertEqual(direction, "DOWN")

    def test_prefers_moving_up_when_pacman_is_mostly_above(self) -> None:
        direction = logic.choose_ghost_direction(self.open_grid, (5, 3), (1, 3))
        self.assertEqual(direction, "UP")

    def test_prefers_moving_right_when_pacman_is_mostly_to_the_right(self) -> None:
        direction = logic.choose_ghost_direction(self.open_grid, (3, 1), (3, 5))
        self.assertEqual(direction, "RIGHT")

    def test_prefers_moving_left_when_pacman_is_mostly_to_the_left(self) -> None:
        direction = logic.choose_ghost_direction(self.open_grid, (3, 5), (3, 1))
        self.assertEqual(direction, "LEFT")

    def test_prefers_the_larger_gap_when_both_axes_differ(self) -> None:
        # Pac-Man is 1 row below but 4 columns to the right: the column
        # gap is bigger, so the ghost should try RIGHT first.
        direction = logic.choose_ghost_direction(self.open_grid, (3, 1), (4, 5))
        self.assertEqual(direction, "RIGHT")

    def test_falls_back_to_the_other_axis_when_preferred_move_is_blocked(self) -> None:
        # Pac-Man is mostly below the ghost (the bigger gap, so DOWN is
        # preferred), but a wall sits immediately south of the ghost -- it
        # should fall back to closing the smaller, sideways gap instead.
        grid = make_grid(
            [
                "#######",
                "#.....#",
                "#..#..#",
                "#..#..#",
                "#.....#",
                "#######",
            ]
        )
        direction = logic.choose_ghost_direction(grid, (1, 3), (4, 4))
        self.assertEqual(direction, "RIGHT")

    def test_gives_up_this_turn_when_the_only_preferred_axis_is_blocked(self) -> None:
        # This heuristic is deliberately NOT real pathfinding: when
        # Pac-Man is directly behind a pillar with no sideways gap to
        # fall back on, the ghost simply does not move this turn, even
        # though a path around the pillar exists.
        grid = make_grid(
            [
                "#######",
                "#.....#",
                "#..#..#",
                "#..#..#",
                "#.....#",
                "#######",
            ]
        )
        direction = logic.choose_ghost_direction(grid, (1, 3), (4, 3))
        self.assertIsNone(direction)

    def test_returns_none_when_completely_boxed_in(self) -> None:
        grid = make_grid(
            [
                "#####",
                "##.##",
                "#####",
            ]
        )
        direction = logic.choose_ghost_direction(grid, (1, 2), (1, 2))
        self.assertIsNone(direction)

    def test_standing_on_pacmans_square_returns_none(self) -> None:
        # Zero gap on both axes -- there is nothing to chase.
        direction = logic.choose_ghost_direction(self.open_grid, (3, 3), (3, 3))
        self.assertIsNone(direction)


class MoveGhostTests(unittest.TestCase):
    """Tests for logic.move_ghost()."""

    def setUp(self) -> None:
        self.open_grid = make_grid(
            [
                "#######",
                "#.....#",
                "#.....#",
                "#.....#",
                "#######",
            ]
        )

    def test_moves_one_step_closer_to_pacman(self) -> None:
        new_position = logic.move_ghost(self.open_grid, (1, 1), (1, 5))
        self.assertEqual(new_position, (1, 2))

    def test_stays_put_when_boxed_in(self) -> None:
        grid = make_grid(["#####", "##.##", "#####"])
        new_position = logic.move_ghost(grid, (1, 2), (1, 2))
        self.assertEqual(new_position, (1, 2))


class ShortestPathLengthTests(unittest.TestCase):
    """Tests for logic.shortest_path_length()."""

    def test_zero_when_start_equals_goal(self) -> None:
        grid = make_grid(["#.#"])
        self.assertEqual(logic.shortest_path_length(grid, (0, 1), (0, 1)), 0)

    def test_counts_steps_in_a_straight_corridor(self) -> None:
        grid = make_grid(["#.....#"])
        self.assertEqual(logic.shortest_path_length(grid, (0, 1), (0, 5)), 4)

    def test_none_when_goal_is_unreachable(self) -> None:
        grid = make_grid(
            [
                "#####",
                "#.#.#",
                "#####",
            ]
        )
        self.assertIsNone(logic.shortest_path_length(grid, (1, 1), (1, 3)))

    def test_shipped_maze_template_is_fully_connected(self) -> None:
        # Every open square must be reachable from Pac-Man's own starting
        # square, or the game could spawn dots (or the ghost) somewhere
        # the player can never reach.
        grid, pacman_start, ghost_start = logic.parse_maze(logic.MAZE_TEMPLATE)
        assert pacman_start is not None
        assert ghost_start is not None
        self.assertIsNotNone(
            logic.shortest_path_length(grid, pacman_start, ghost_start)
        )
        for row_index, row in enumerate(grid):
            for col_index, cell in enumerate(row):
                if cell != logic.WALL:
                    with self.subTest(row=row_index, col=col_index):
                        distance = logic.shortest_path_length(
                            grid, pacman_start, (row_index, col_index)
                        )
                        self.assertIsNotNone(distance)


class IntegrationTests(unittest.TestCase):
    """A couple of end-to-end scenarios combining several functions."""

    def test_eating_every_dot_in_a_tiny_maze_wins_the_game(self) -> None:
        template = ["######", "#P..G#", "######"]
        grid, pacman_start, _ghost = logic.parse_maze(template)
        assert pacman_start is not None
        position = pacman_start
        self.assertFalse(logic.has_won(grid))

        position = logic.move_pacman(grid, position, "RIGHT")
        logic.eat_dot(grid, position)
        self.assertFalse(logic.has_won(grid))

        position = logic.move_pacman(grid, position, "RIGHT")
        logic.eat_dot(grid, position)
        self.assertTrue(logic.has_won(grid))

    def test_ghost_chasing_pacman_into_a_corner_eventually_catches_up(self) -> None:
        grid = make_grid(
            [
                "#######",
                "#.....#",
                "#######",
            ]
        )
        pacman_position = (1, 5)
        ghost_position = (1, 1)

        caught = False
        for _step in range(10):    # a generous number of ticks
            ghost_position = logic.move_ghost(grid, ghost_position, pacman_position)
            if logic.check_collision(pacman_position, ghost_position):
                caught = True
                break
        self.assertTrue(caught)


if __name__ == "__main__":
    unittest.main()
