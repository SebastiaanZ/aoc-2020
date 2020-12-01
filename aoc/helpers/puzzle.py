from __future__ import annotations

import datetime
import importlib
import logging
import os
import pathlib
import timeit

import pytz
import requests

__all__ = ["Puzzle"]

log = logging.getLogger(__name__)


PUZZLE_INPUT_URL = "https://adventofcode.com/2020/day/{day}/input"
SOLUTIONS_DIR = pathlib.Path(__file__).parent.parent / 'solutions'
INPUTS_DIR = pathlib.Path(__file__).parent.parent / 'inputs'

SOLUTION_TEMPLATE = '''
import logging
import typing

from aoc.helpers import Puzzle

__all__ = ["part_one", "part_two"]
log = logging.getLogger(__name__)


def part_one(puzzle_input: Puzzle) -> typing.Optional[typing.Union[str, int]]:
    """Return the solution for part one of this day."""


def part_two(puzzle_input: Puzzle) -> typing.Optional[typing.Union[str, int]]:
    """Return the solution for part two of this day."""
'''.lstrip()


class NotYetAvailable(RuntimeError):
    """Raised when the puzzle input is not yet available."""


class CookieNotSet(RuntimeError):
    """Raised when no environment variable with an AoC session cookie was set."""


class DownloadFailed(RuntimeError):
    """Raise when downloading a puzzle input failed unexpectedly."""


class InvalidSolutionDirectory(ValueError):
    """Raised when an invalid solution directory was observed."""


def day_should_be_available(day: int) -> bool:
    """Check if the input for this day should be available."""
    now = datetime.datetime.now(pytz.timezone("EST"))
    available = datetime.datetime(2020, 12, day, 0, 0, 0, tzinfo=pytz.timezone("EST"))
    return now >= available


def get_puzzle_input(day: int) -> str:
    """Get the input for the given day."""
    puzzle_input = INPUTS_DIR / f"day{day:0>2}.txt"

    if not puzzle_input.exists():
        if not INPUTS_DIR.exists():
            log.info(f"the inputs dir '{INPUTS_DIR}' has not been created yet, creating...")
            INPUTS_DIR.mkdir()

        log.info(f"downloading puzzle input for day {day}.")
        if not day_should_be_available(day):
            raise NotYetAvailable(
                f"the puzzle input for day {day} is not yet available!"
            )

        session = os.environ.get("AOC_SESSION_COOKIE")
        if not session:
            raise CookieNotSet("the environment variable `AOC_SESSION_COOKIE` was not set")

        response = requests.get(
            PUZZLE_INPUT_URL.format(day=day),
            cookies={"session": session}
        )

        if response.status_code != 200:
            raise DownloadFailed(
                f"downloading the puzzle input for day {day} failed "
                f"with status code `{response.status_code}`."
            )

        puzzle_input.write_text(response.text, encoding="utf-8")

    log.debug(f"reading and returning input for day {day} from '{puzzle_input}'")
    return puzzle_input.read_text(encoding="utf-8")


def get_solution_dir(day: int) -> pathlib.Path:
    """
    Get the location of the solution for this day.

    If no solution directory yet exists for this day, it will be created.
    """
    day_dir = SOLUTIONS_DIR / f"day{day:0>2}"
    day_init = day_dir / "__init__.py"
    day_solution = day_dir / "solution.py"

    if not day_dir.exists():
        if not SOLUTIONS_DIR.exists():
            log.info(f"the solutions dir '{SOLUTIONS_DIR}' has not been created yet, creating...")
            SOLUTIONS_DIR.mkdir()

        log.info(f"creating missing solution directory for day {day}.")
        day_dir.mkdir()
        day_solution.write_text(SOLUTION_TEMPLATE, encoding="utf-8")
        day_init.write_text("from .solution import *\n", encoding="utf-8")

    if not day_dir.is_dir() or not day_solution.exists() or not day_init.exists():
        raise InvalidSolutionDirectory(f"the solution directory '{day_dir}' for {day} is invalid.")

    log.debug(f"returning '{day_dir}' as the solution directory for day {day}.")
    return day_dir


class Puzzle:
    """An  Advent of Code day with associated puzzle input."""

    def __init__(self, day: str):
        self.day = int(day.removeprefix("day"))
        self.input = get_puzzle_input(self.day)
        self._lines = None
        self._intlines = None
        self.solution_dir = get_solution_dir(self.day)
        self.solution_import = f'aoc.solutions.day{self.day:0>2}'

    @classmethod
    def from_path(cls, path: str) -> Puzzle:
        """Create a Puzzle instance from a solution path."""
        path = pathlib.Path(path)
        day = path.parent.stem
        return cls(day)

    def __repr__(self) -> str:
        """Return the official representation of this puzzle."""
        cls_name = type(self).__name__
        return f"<{cls_name} day={self.day}>"

    @property
    def lines(self) -> list[str]:
        """Get a list of lines for this puzzle input."""
        if self._lines is None:
            self._lines = self.input.splitlines()
        return self._lines

    @property
    def intlines(self) -> list[int]:
        """Get a list of lines converted to integers for this puzzle input."""
        if self._intlines is None:
            self._intlines = [int(line) for line in self.input.splitlines()]
        return self._intlines

    def run(self) -> None:
        """Run the puzzle solutions and print the solution."""
        solution = importlib.import_module(self.solution_import)
        start = timeit.default_timer()
        answer_one = solution.part_one(self)
        answer_two = solution.part_two(self)
        run_time = timeit.default_timer() - start

        title = f"Advent of Code — Solutions for day {self.day}"
        separator = "—" * len(title)

        print(separator)
        print(title)
        print(separator)
        print(f"Part one: {answer_one}")
        print(f"Part two: {answer_two}")
        print(separator)
        print(f"Running time: {run_time:.6f}s")

    def time(self) -> None:
        """Time the solution for this puzzle."""
        solution = importlib.import_module(self.solution_import)

        results = []
        for _part in (solution.part_one, solution.part_two):
            timer = timeit.Timer("_part(self)", globals=locals())
            result = timer.autorange()
            results.append(result)

        title = f"Advent of Code — Runtimes for day {self.day}"
        separator = "—" * len(title)

        print(separator)
        print(title)
        print(separator)
        combined_runtime = 0
        for i, (runs, run_time) in enumerate(results, start=1):
            avg_runtime = run_time/runs
            combined_runtime += avg_runtime
            print(f"Part {i}: {avg_runtime:.6f}s avg in {runs} runs")
        print(separator)
        print(f"Combined avg runtime: {combined_runtime:.6f}s")
