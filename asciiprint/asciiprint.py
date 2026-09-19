"""
asciiprint.py
--------------
The interactive program. This file asks the user questions with input()
and prints the answer with print() -- all the actual "how do we turn a
word into big letters" logic lives in ascii_art_logic.py, which this file
imports.

Run it with no arguments for a fully interactive experience:
    python3 asciiprint.py

Or skip the questions by passing them on the command line:
    python3 asciiprint.py "HI" --char "@" --size extra-large
"""

import argparse

import ascii_art_logic


def ask_word() -> str:
    """[LOOP] Keep asking until the user types a non-empty word."""
    while True:
        text = input("What word or short phrase should I print? ").strip()
        if text != "":  # [CONDITIONAL]
            return text
        print("Please type at least one character.")


def ask_char() -> str:
    """[LOOP] Keep asking until the user gives one usable character."""
    while True:
        raw = input("Which character should draw it? (press Enter for '*'): ")
        if raw == "":  # [CONDITIONAL] empty answer -> use the default
            return "*"
        if len(raw) == 1 and raw != " ":
            return raw
        print("Please enter exactly one character (not a space).")


def ask_size() -> str:
    """[LOOP] Show a numbered menu built from ascii_art_logic.SIZES."""
    size_names = list(ascii_art_logic.SIZES.keys())  # [LIST]
    while True:
        print("Choose a size:")
        for position, name in enumerate(size_names, start=1):  # [LOOP]
            print(f"  {position}. {name}")
        raw = input(f"Enter a number (1-{len(size_names)}), or press Enter for 'big': ").strip()
        if raw == "":  # [CONDITIONAL]
            return "big"
        if raw in size_names:
            return raw
        if raw.isdigit() and 1 <= int(raw) <= len(size_names):
            return size_names[int(raw) - 1]
        print("Please enter a number from the list, or type a size name.")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Print a word or name on the screen in big ASCII-art letters."
    )
    parser.add_argument("text", nargs="?", default=None, help="the word or phrase to print")
    parser.add_argument(
        "--char", "-c", default=None, help="the single character used to draw the letters"
    )
    parser.add_argument(
        "--size",
        "-s",
        choices=sorted(ascii_art_logic.SIZES.keys()),
        default=None,
        help="how large to print the word",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()

    text = args.text if args.text is not None else ask_word()
    fill_char = args.char if args.char is not None else ask_char()
    size = args.size if args.size is not None else ask_size()

    try:
        lines = ascii_art_logic.render_text(text, fill_char, size)
    except ValueError as error:
        print(f"Oops, I can't print that: {error}")
        return

    print()
    for line in lines:  # [LOOP]
        print(line)
    print()


if __name__ == "__main__":
    main()
