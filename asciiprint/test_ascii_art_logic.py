"""
test_ascii_art_logic.py
------------------------
Automated tests for ascii_art_logic.py.

These tests do NOT call input() or print() for real -- ascii_art_logic.py
has no interactive code in it at all, so it can be exercised directly.

Run all tests with:
    python3 -m unittest test_ascii_art_logic.py -v

or simply:
    python3 test_ascii_art_logic.py
"""

import string
import unittest

import ascii_art_logic as art


class FontDataTests(unittest.TestCase):
    """Every glyph in FONT must have the same, correct shape."""

    def test_contains_every_uppercase_letter(self) -> None:
        for letter in string.ascii_uppercase:
            self.assertIn(letter, art.FONT)

    def test_contains_every_digit(self) -> None:
        for digit in "0123456789":
            self.assertIn(digit, art.FONT)

    def test_contains_space_and_basic_punctuation(self) -> None:
        for character in [" ", "!", "?", ".", ",", "'", "-"]:
            self.assertIn(character, art.FONT)

    def test_every_glyph_has_correct_height(self) -> None:
        for character, glyph in art.FONT.items():
            self.assertEqual(len(glyph), art.GLYPH_HEIGHT, msg=f"glyph for {character!r}")

    def test_every_glyph_row_has_correct_width(self) -> None:
        for character, glyph in art.FONT.items():
            for row in glyph:
                self.assertEqual(len(row), art.GLYPH_WIDTH, msg=f"glyph for {character!r}")

    def test_every_glyph_uses_only_hash_and_dot(self) -> None:
        for character, glyph in art.FONT.items():
            for row in glyph:
                for symbol in row:
                    self.assertIn(symbol, "#.", msg=f"glyph for {character!r}")


class GetGlyphTests(unittest.TestCase):
    def test_returns_font_entry_for_known_uppercase_letter(self) -> None:
        self.assertEqual(art.get_glyph("A"), art.FONT["A"])

    def test_is_case_insensitive(self) -> None:
        self.assertEqual(art.get_glyph("a"), art.FONT["A"])

    def test_unknown_character_falls_back_to_unknown_glyph(self) -> None:
        self.assertEqual(art.get_glyph("@"), art.UNKNOWN_GLYPH)

    def test_digit_looks_up_correctly(self) -> None:
        self.assertEqual(art.get_glyph("7"), art.FONT["7"])


class BuildBaseGridTests(unittest.TestCase):
    def test_has_correct_number_of_rows(self) -> None:
        grid = art.build_base_grid("HI")
        self.assertEqual(len(grid), art.GLYPH_HEIGHT)

    def test_row_width_matches_number_of_characters(self) -> None:
        text = "CAT"
        grid = art.build_base_grid(text)
        expected_width = len(text) * (art.GLYPH_WIDTH + 1)  # +1 for the gap column
        for row in grid:
            self.assertEqual(len(row), expected_width)

    def test_empty_text_gives_empty_rows(self) -> None:
        grid = art.build_base_grid("")
        self.assertEqual(grid, [""] * art.GLYPH_HEIGHT)

    def test_only_uses_hash_and_dot(self) -> None:
        grid = art.build_base_grid("Hi There!")
        for row in grid:
            for symbol in row:
                self.assertIn(symbol, "#.")


class ScaleGridTests(unittest.TestCase):
    def test_multiplier_one_leaves_grid_unchanged(self) -> None:
        grid = ["#.#", ".#."]
        self.assertEqual(art.scale_grid(grid, 1), grid)

    def test_multiplier_doubles_width_and_height(self) -> None:
        grid = ["#."]
        scaled = art.scale_grid(grid, 2)
        self.assertEqual(len(scaled), 2)
        for row in scaled:
            self.assertEqual(row, "##..")

    def test_multiplier_three_matches_expected_block(self) -> None:
        grid = ["#."]
        scaled = art.scale_grid(grid, 3)
        self.assertEqual(scaled, ["###...", "###...", "###..."])


class RenderTextTests(unittest.TestCase):
    def test_output_line_count_matches_size(self) -> None:
        for size, multiplier in art.SIZES.items():
            lines = art.render_text("HI", "#", size)
            self.assertEqual(len(lines), art.GLYPH_HEIGHT * multiplier, msg=size)

    def test_output_only_contains_fill_char_and_space(self) -> None:
        lines = art.render_text("Go Team!", "@", "big")
        for line in lines:
            for symbol in line:
                self.assertIn(symbol, "@ ")

    def test_different_fill_characters_are_honored(self) -> None:
        star_lines = art.render_text("A", "*", "small")
        hash_lines = art.render_text("A", "#", "small")
        for star_line, hash_line in zip(star_lines, hash_lines):
            self.assertEqual(star_line.replace("*", "#"), hash_line)

    def test_lowercase_input_renders_same_as_uppercase(self) -> None:
        self.assertEqual(
            art.render_text("hello", "#", "small"),
            art.render_text("HELLO", "#", "small"),
        )

    def test_rejects_empty_text(self) -> None:
        with self.assertRaises(ValueError):
            art.render_text("   ", "#", "small")

    def test_rejects_multi_character_fill_char(self) -> None:
        with self.assertRaises(ValueError):
            art.render_text("Hi", "##", "small")

    def test_rejects_space_as_fill_char(self) -> None:
        with self.assertRaises(ValueError):
            art.render_text("Hi", " ", "small")

    def test_rejects_unknown_size(self) -> None:
        with self.assertRaises(ValueError):
            art.render_text("Hi", "#", "gigantic")


class RegressionTests(unittest.TestCase):
    """Pin exact output for a few known inputs.

    If a future change to FONT, build_base_grid(), or scale_grid()
    accidentally shifts a pixel or changes spacing, these tests will fail
    even though the "shape" based tests above might still pass. If you
    intentionally change how letters look, update the expected values
    here to match -- but look closely first, since a failure here usually
    means something broke by accident.
    """

    def test_small_hi_matches_known_good_output(self) -> None:
        self.assertEqual(
            art.render_text("HI", "#", "small"),
            [
                "#   # ##### ",
                "#   #   #   ",
                "#   #   #   ",
                "#####   #   ",
                "#   #   #   ",
                "#   #   #   ",
                "#   # ##### ",
            ],
        )

    def test_small_period_matches_known_good_output(self) -> None:
        self.assertEqual(
            art.render_text(".", "#", "small"),
            [
                "      ",
                "      ",
                "      ",
                "      ",
                "      ",
                "      ",
                "  #   ",
            ],
        )

    def test_big_a_matches_known_good_output(self) -> None:
        self.assertEqual(
            art.render_text("A", "*", "big"),
            [
                "  ******    ",
                "  ******    ",
                "**      **  ",
                "**      **  ",
                "**      **  ",
                "**      **  ",
                "**********  ",
                "**********  ",
                "**      **  ",
                "**      **  ",
                "**      **  ",
                "**      **  ",
                "**      **  ",
                "**      **  ",
            ],
        )

    def test_extra_large_size_multiplies_small_size_by_three(self) -> None:
        small = art.render_text("OK", "#", "small")
        extra_large = art.render_text("OK", "#", "extra-large")
        self.assertEqual(len(extra_large), len(small) * 3)
        self.assertEqual(len(extra_large[0]), len(small[0]) * 3)

    def test_unknown_character_renders_as_question_mark_glyph(self) -> None:
        self.assertEqual(
            art.render_text("@", "#", "small"),
            art.render_text("?", "#", "small"),
        )


if __name__ == "__main__":
    unittest.main()
