# Turtle Tetris

A small, real, playable Tetris — built with Python's built-in `turtle`
graphics module — designed as a first project for students who are brand
new to Python. It exists to give you hands-on practice with six core
ideas: **strings, tuples, lists, dictionaries, loops, and conditionals**,
all working together in one program you can actually play.

For a deep dive into *how* it's built (with diagrams), read
[`SPEC.md`](./SPEC.md). This file just gets you running and playing.

![Turtle Tetris mid-game, showing several locked tetrominoes of different colors stacked on the board, with the score and controls reminder at the top](./docs/screenshot.png)

*(Captured from an automated test run, so the window is cropped a bit oddly — run it yourself for the full picture!)*

## Getting started (never used Python before? Start here)

Three steps: install Python, download this project, run the game. If
you've done this before, skip to [Step 3](#step-3--run-the-game).

> **A note on `python` vs `python3`:** on Windows the command is usually
> `python`; on macOS and Linux it's usually `python3`. Wherever you see
> `python3` below, Windows users should type `python` instead. If one
> doesn't work, try the other — that's the single most common hiccup.

### Step 1 — Install Python 3.14 or later

First check whether you already have it. Open a terminal
(**Windows:** press Start, type `cmd`, hit Enter · **macOS:** press
`Cmd+Space`, type `terminal`, hit Enter · **Linux:** `Ctrl+Alt+T`) and
run:

```bash
python3 --version
```

If that prints `Python 3.14.0` or higher, you're done — skip to Step 2.
If it prints an older version, or says the command isn't found, install
Python:

**Windows**
1. Go to <https://www.python.org/downloads/> and click the big download
   button.
2. Run the installer, and — this part matters — **tick the box that says
   "Add python.exe to PATH"** at the bottom of the first screen *before*
   clicking Install Now. If you forget, the `python` command won't work
   in your terminal.
3. Close and reopen your terminal, then check with `python --version`.

**macOS**
1. Go to <https://www.python.org/downloads/> and download the macOS
   installer, then run it and click through.
2. Close and reopen Terminal, then check with `python3 --version`.

(If you already use Homebrew, `brew install python@3.14` works too.)

**Linux (Ubuntu / Debian)**

The version in your system's package list is often older than 3.14, so
the simplest reliable route is the installer from
<https://www.python.org/downloads/>. You also need the `tkinter` package
that turtle graphics draws with:

```bash
sudo apt-get install python3-tk
```

### Step 2 — Download the project from GitHub

Pick **one** of these two options.

**Option A — Download a ZIP (easiest, no extra tools)**

1. Open
   <https://github.com/olumuyiwaoluwasanmi-codepath/Comp163Projects> in
   your browser.
2. Click the green **Code** button, then **Download ZIP**.
3. Unzip the downloaded file somewhere you'll remember, like your
   Desktop.

**Option B — Clone it with Git (what most programmers do)**

This keeps your copy easy to update later with `git pull`. If you don't
have Git, get it from <https://git-scm.com/downloads> first, then run:

```bash
git clone https://github.com/olumuyiwaoluwasanmi-codepath/Comp163Projects.git
```

That creates a folder named `Comp163Projects` in whatever directory your
terminal is currently in.

### Step 3 — Run the game

In your terminal, move into the project folder and start it. `cd` means
"change directory":

```bash
cd Comp163Projects/turtle_tetris
python3 tetris.py
```

A window will open with an empty board and a piece already falling.
Have fun!

> **If you downloaded the ZIP**, your folder may be named
> `Comp163Projects-main` or similar — use that name in the `cd` command
> instead. Tip: on Windows and macOS you can type `cd ` (with a space)
> and then drag the folder from your file manager onto the terminal
> window to fill in the path for you.

### If something goes wrong

| What you see | What it means |
|---|---|
| `python3: command not found` | Python isn't installed, or wasn't added to PATH. Redo Step 1 — on Windows, watch for that PATH checkbox. Try `python` instead of `python3`. |
| `No module named 'tkinter'` | Turtle graphics needs `tkinter`. On Linux run `sudo apt-get install python3-tk`; on Windows/macOS, reinstall Python from python.org, which bundles it. |
| `can't open file 'tetris.py'` | You're in the wrong folder. Run `cd turtle_tetris` first; `ls` (macOS/Linux) or `dir` (Windows) should list `tetris.py`. |
| `SyntaxError: invalid syntax` pointing at `type Cell` | Your Python is much too old (3.11 or earlier). Check with `python3 --version` and install 3.14+ as in Step 1. |

Beyond Python itself there are **no dependencies to install**, and you
don't need an internet connection to play once you have the files.

## Controls

| Key | Action |
|---|---|
| `←` | Move the piece one column left |
| `→` | Move the piece one column right |
| `↓` | Soft drop — move down one row early |
| `↑` | Rotate the piece |
| `Space` | Hard drop — instantly slam the piece to the bottom |

The piece also falls on its own every half second, whether you press
anything or not — just like real Tetris.

The board is 10 columns wide and 16 rows tall. Clearing 1/2/3/4 rows at
once with a single piece scores 100/300/500/800 points, in that order —
so it's worth trying to clear several lines at once!

## Project files

| File | What's in it |
|---|---|
| `tetris_logic.py` | All the game **rules** — the board, the seven tetromino shapes, collision checking, locking pieces, clearing lines, scoring. No drawing code, no window, no keyboard handling. |
| `tetris.py` | The **window** — turns the board/piece data from `tetris_logic.py` into on-screen squares, and turns key presses into moves. |
| `test_tetris_logic.py` | 39 automated tests for `tetris_logic.py`. |
| `SPEC.md` | A guided tour of the design, with diagrams. |

Splitting the *rules* from the *drawing* is the single most important
design idea in this project — see [`SPEC.md`](./SPEC.md#2-file-layout)
for why, and how the two files talk to each other.

## Running the tests

`tetris_logic.py` has zero dependency on `turtle` or any window, so its
tests run instantly, with no graphics involved at all:

```bash
cd turtle_tetris
python3 -m unittest test_tetris_logic.py -v
```

You should see all 39 tests pass. If you change a rule in
`tetris_logic.py` — say, the scoring table, or a piece's shape — try
running the tests again and see what (if anything) breaks. That's the
whole point of having them!

## Type checking (optional)

Every function in this project declares the types of what it takes in
and what it gives back. Python doesn't check those declarations when it
runs — they're there for you and your editor — but you can have a tool
check them for you:

```bash
pip install mypy
mypy --strict tetris_logic.py tetris.py test_tetris_logic.py
```

All three files pass `--strict` with no errors. Try deliberately
breaking one — for example, change `piece["col"] -= 1` to
`piece["col"] -= "1"` in `tetris.py` — and run it again to see the kind
of mistake this catches *before* you ever start the game.

## Where each concept lives

This is a quick index. [`SPEC.md`](./SPEC.md#10-concept-map-with-fileline-references)
has the full table with exact file/line references and more context —
this is just enough to get you started reading the code with a purpose.

* **Strings** — piece names like `"T"` and color names like `"cyan"`,
  all through `SHAPES` and `COLORS` in `tetris_logic.py`.
* **Tuples** — every block position, like `(1, 0)`, is a `(column, row)`
  tuple. See any entry inside `SHAPES`.
* **Lists** — the board itself (`new_board()`), and each piece's shape
  data (`SHAPES["T"]` is a list of rotation states).
* **Dictionaries** — `SHAPES`, `COLORS`, and every `piece` object are all
  plain dictionaries. Try `print(piece)` anywhere in `tetris.py` to see
  one for yourself.
* **Loops** — `for` loops scan the board to draw it (`draw_board()`) and
  check every block of a piece (`valid_position()`); a `while` loop
  refills the board after clearing lines (`clear_full_rows()`).
* **Conditionals** — collision checks, "is this row full?", and "is the
  game over?" are all plain `if` statements.

Every `[TAG]` comment inside `tetris_logic.py` and `tetris.py` marks one
of these six ideas in the exact spot it's being used — search the files
for `[LOOP]`, `[CONDITIONAL]`, `[STRING]`, `[LIST]`, `[DICTIONARY]`, and
`[TUPLE]` to find every occurrence.

## How does the drawing part work?

Everything on screen is drawn with Python's built-in `turtle` module — a
pen you steer with commands like `forward(30)` and `right(90)`.
[`SPEC.md` section 6](./SPEC.md#6-how-turtle-graphics-actually-works)
explains it from scratch: how a turtle draws and fills a square, why
turtle's `(0, 0)` is the middle of the window, why this game uses three
separate turtles as layers, how `tracer(0)` + `update()` stop the screen
flickering, and how the game loop runs on timers instead of a
`while` loop.

## Stretch goals

Once you're comfortable reading the code, here are some good next
projects, roughly in order of difficulty:

1. **Change the board size or fall speed.** Edit `COLS`/`ROWS` in
   `tetris_logic.py` or `FALL_DELAY_MS` in `tetris.py`. (Loops/constants)
2. **Add a "next piece" preview** in the corner of the window. You'll
   need to generate the *next* piece ahead of time instead of only when
   the current one locks. (Dictionaries, functions)
3. **Speed the game up as the score increases** — e.g. shrink
   `FALL_DELAY_MS` every time the score crosses a multiple of 1000.
   (Conditionals)
4. **Save a high score to a text file** between runs, using Python's
   built-in `open()`. (File I/O, strings)
5. **Add a "ghost piece"** — a faint outline showing where the current
   piece would land if hard-dropped right now. (Reuse `valid_position()`
   in a loop, just like `hard_drop()` already does.)
6. **Add wall kicks** — when a rotation would normally be rejected near
   a wall, try shifting the piece 1 column left or right before giving
   up. (Conditionals, and a great excuse to re-read
   `valid_position()`.)
7. **Rewrite `Piece` as a `@dataclass`** — a real object with
   `piece.col` attributes — replacing the `TypedDict` and every
   `piece["col"]` lookup. Do this once dictionaries feel completely
   natural; it's a good way to see *why* classes exist, having already
   done the same job with a dictionary.

Have fun, and don't be afraid to break it — `test_tetris_logic.py` will
tell you exactly what you broke.
