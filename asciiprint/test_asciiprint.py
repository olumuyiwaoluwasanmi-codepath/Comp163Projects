"""
test_asciiprint.py
--------------------
Automated tests for asciiprint.py -- the interactive program itself.

Even though this file calls input() and print(), the tests below never
actually wait for a person to type anything: unittest.mock.patch()
temporarily swaps out input() with a stand-in that returns canned
answers, and contextlib.redirect_stdout() captures what print() would
have shown on screen so it can be checked like any other value.

Run all tests with:
    python3 -m unittest test_asciiprint.py -v

or simply:
    python3 test_asciiprint.py
"""

import io
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

import ascii_art_logic as art
import asciiprint


class AskWordTests(unittest.TestCase):
    def test_returns_first_non_empty_answer(self) -> None:
        with patch("builtins.input", return_value="Ada"), redirect_stdout(io.StringIO()):
            self.assertEqual(asciiprint.ask_word(), "Ada")

    def test_strips_surrounding_whitespace(self) -> None:
        with patch("builtins.input", return_value="  Grace Hopper  "), redirect_stdout(io.StringIO()):
            self.assertEqual(asciiprint.ask_word(), "Grace Hopper")

    def test_reprompts_on_blank_answers(self) -> None:
        answers = iter(["", "   ", "Linus"])
        with patch("builtins.input", side_effect=lambda _: next(answers)), redirect_stdout(io.StringIO()):
            self.assertEqual(asciiprint.ask_word(), "Linus")


class AskCharTests(unittest.TestCase):
    def test_empty_answer_defaults_to_star(self) -> None:
        with patch("builtins.input", return_value=""), redirect_stdout(io.StringIO()):
            self.assertEqual(asciiprint.ask_char(), "*")

    def test_accepts_a_single_character(self) -> None:
        with patch("builtins.input", return_value="@"), redirect_stdout(io.StringIO()):
            self.assertEqual(asciiprint.ask_char(), "@")

    def test_reprompts_on_a_space(self) -> None:
        answers = iter([" ", "#"])
        with patch("builtins.input", side_effect=lambda _: next(answers)), redirect_stdout(io.StringIO()):
            self.assertEqual(asciiprint.ask_char(), "#")

    def test_reprompts_on_more_than_one_character(self) -> None:
        answers = iter(["ab", "!"])
        with patch("builtins.input", side_effect=lambda _: next(answers)), redirect_stdout(io.StringIO()):
            self.assertEqual(asciiprint.ask_char(), "!")


class AskSizeTests(unittest.TestCase):
    def test_empty_answer_defaults_to_big(self) -> None:
        with patch("builtins.input", return_value=""), redirect_stdout(io.StringIO()):
            self.assertEqual(asciiprint.ask_size(), "big")

    def test_accepts_a_size_name_typed_directly(self) -> None:
        with patch("builtins.input", return_value="extra-large"), redirect_stdout(io.StringIO()):
            self.assertEqual(asciiprint.ask_size(), "extra-large")

    def test_accepts_a_menu_number(self) -> None:
        size_names = list(art.SIZES.keys())
        with patch("builtins.input", return_value="1"), redirect_stdout(io.StringIO()):
            self.assertEqual(asciiprint.ask_size(), size_names[0])

    def test_reprompts_on_an_out_of_range_number(self) -> None:
        answers = iter(["0", "99", "small"])
        with patch("builtins.input", side_effect=lambda _: next(answers)), redirect_stdout(io.StringIO()):
            self.assertEqual(asciiprint.ask_size(), "small")

    def test_reprompts_on_a_nonsense_answer(self) -> None:
        answers = iter(["gigantic", "big"])
        with patch("builtins.input", side_effect=lambda _: next(answers)), redirect_stdout(io.StringIO()):
            self.assertEqual(asciiprint.ask_size(), "big")

    def test_every_size_name_is_reachable_by_number(self) -> None:
        size_names = list(art.SIZES.keys())
        for position, name in enumerate(size_names, start=1):
            with patch("builtins.input", return_value=str(position)), redirect_stdout(io.StringIO()):
                self.assertEqual(asciiprint.ask_size(), name)


class BuildParserTests(unittest.TestCase):
    def test_no_arguments_gives_all_none(self) -> None:
        args = asciiprint.build_parser().parse_args([])
        self.assertIsNone(args.text)
        self.assertIsNone(args.char)
        self.assertIsNone(args.size)

    def test_positional_text_is_captured(self) -> None:
        args = asciiprint.build_parser().parse_args(["Hello"])
        self.assertEqual(args.text, "Hello")

    def test_char_and_size_flags_are_captured(self) -> None:
        args = asciiprint.build_parser().parse_args(["Hi", "--char", "@", "--size", "small"])
        self.assertEqual(args.text, "Hi")
        self.assertEqual(args.char, "@")
        self.assertEqual(args.size, "small")

    def test_short_flags_work_too(self) -> None:
        args = asciiprint.build_parser().parse_args(["Hi", "-c", "#", "-s", "big"])
        self.assertEqual(args.char, "#")
        self.assertEqual(args.size, "big")

    def test_rejects_a_size_not_in_ascii_art_logic_sizes(self) -> None:
        parser = asciiprint.build_parser()
        with self.assertRaises(SystemExit):
            with redirect_stdout(io.StringIO()), patch("sys.stderr", io.StringIO()):
                parser.parse_args(["Hi", "--size", "gigantic"])

    def test_every_size_in_sizes_is_a_valid_choice(self) -> None:
        parser = asciiprint.build_parser()
        for size_name in art.SIZES:
            args = parser.parse_args(["Hi", "--size", size_name])
            self.assertEqual(args.size, size_name)


class MainEndToEndTests(unittest.TestCase):
    """Drive main() the way a user actually would, start to finish."""

    def run_main(self, argv: list[str]) -> str:
        captured = io.StringIO()
        with patch("sys.argv", ["asciiprint.py", *argv]), redirect_stdout(captured):
            asciiprint.main()
        return captured.getvalue()

    def test_fully_specified_command_line_needs_no_prompts(self) -> None:
        with patch("builtins.input", side_effect=AssertionError("should not prompt")):
            output = self.run_main(["HI", "--char", "#", "--size", "small"])
        expected = "\n".join(art.render_text("HI", "#", "small"))
        self.assertIn(expected, output)

    def test_missing_arguments_fall_back_to_prompts(self) -> None:
        answers = iter(["Ada", "@", "small"])
        with patch("builtins.input", side_effect=lambda _: next(answers)):
            output = self.run_main([])
        expected = "\n".join(art.render_text("Ada", "@", "small"))
        self.assertIn(expected, output)

    def test_invalid_fill_char_from_the_command_line_prints_a_friendly_error(self) -> None:
        output = self.run_main(["Hi", "--char", "##", "--size", "big"])
        self.assertIn("Oops, I can't print that", output)
        self.assertIn("fill_char must be exactly one character", output)

    def test_invalid_fill_char_does_not_crash_the_program(self) -> None:
        # main() must catch ValueError itself rather than letting it propagate.
        try:
            self.run_main(["Hi", "--char", " ", "--size", "big"])
        except ValueError:
            self.fail("main() should catch ValueError from render_text(), not raise it")


if __name__ == "__main__":
    unittest.main()
