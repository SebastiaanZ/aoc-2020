# Advent of Code 2020
This repository contains my solutions to the daily puzzles of the Advent of Code 2020. It also contains a utility to download the puzzle input, run the solutions, and submit the answers to the Advent of Code website.

## Puzzle Utility

I wrote the puzzle utility to easily download puzzle inputs and submit solutions. It support running the solution in various ways, to make it easier to use with a default run configuration in my preferred IDE (PyCharm). It also caches answers and submissions, to shorten rerun times and to prevent me from submitting the same answer multiple times.

### CLI

The utility has a fairly simple CLI:

```
sebastiaan@ubuntu $ python -m aoc --help

usage: __main__.py [-h] (--day PUZZLE | --path PUZZLE | --date) [--debug] [--init] [--time] [--submit] [--ignore-cache]

Advent of Code 2020 — Solution Runner

optional arguments:
  -h, --help        show this help message and exit
  --day PUZZLE      select a puzzle by day number
  --path PUZZLE     select a puzzle by solution path
  --date            select a puzzle by the current date (only works during the event)
  --debug           set logging level to DEBUG
  --init, --create  initialize the puzzle, but do not run it
  --time            profile the running time using `timeit`
  --submit          submit the latest submission to AoC website
  --ignore-cache    ignore cached answers/force rerunning a solution
```

**Note:** The utility expects you to use it to manage the solutions and inputs. It will try to use the paths it would create itself.
