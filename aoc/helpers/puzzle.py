from __future__ import annotations

import datetime
import hashlib
import importlib
import logging
import os
import pathlib
import re
import time
import timeit
import typing
import webbrowser

import pytz
import requests
from bs4 import BeautifulSoup

from .answer_cache import AnswerCache, CacheValue

__all__ = ["Puzzle"]

log = logging.getLogger(__name__)


PUZZLE_BASE_URL = "https://adventofcode.com/2020/day/{day}"
PUZZLE_INPUT_URL = PUZZLE_BASE_URL + "/input"
PUZZLE_ANSWER_URL = PUZZLE_BASE_URL + "/answer"
SOLUTIONS_DIR = pathlib.Path(__file__).parent.parent / 'solutions'
INPUTS_DIR = pathlib.Path(__file__).parent.parent / 'inputs'

WAIT_RE = re.compile(r'You have (?:(?P<minutes>\d+)m )?(?P<seconds>\d+)s left to wait')

SOLUTION_TEMPLATE = '''
import logging
import typing

from aoc.helpers import Puzzle

__all__ = ["part_one", "part_two"]
log = logging.getLogger(__name__)


def part_one(puzzle: Puzzle) -> typing.Optional[typing.Union[str, int]]:
    """Return the solution for part one of this day."""


def part_two(puzzle: Puzzle) -> typing.Optional[typing.Union[str, int]]:
    """Return the solution for part two of this day."""
'''.lstrip()


class NotYetAvailable(RuntimeError):
    """Raised when the puzzle input is not yet available."""


class CookieNotSet(RuntimeError):
    """Raised when no environment variable with an AoC session cookie was set."""


class DownloadFailed(RuntimeError):
    """Raised when downloading a puzzle input failed unexpectedly."""


class SubmissionFailed(RuntimeError):
    """Raised when submitting an answer to the website failed."""


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

        # Now, open the browser to start our puzzle!
        webbrowser.open(PUZZLE_BASE_URL.format(day=day))

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

    if not all(path.exists() for path in (day_dir, day_init, day_solution)):
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
        self.solution_directory = get_solution_dir(self.day)
        self.solution_path = self.solution_directory / "solution.py"
        self.solution_import = f'aoc.solutions.day{self.day:0>2}'
        self.answer_cache = AnswerCache(self.solution_directory)
        self._helper_cache = {}

    @classmethod
    def from_path(cls, path: str) -> Puzzle:
        """Create a Puzzle instance from a solution path."""
        path = pathlib.Path(path)
        day = path.parent.stem
        return cls(day)

    @classmethod
    def from_date(cls) -> Puzzle:
        """Create a Puzzle instance from a solution path."""
        today = datetime.datetime.now(pytz.timezone("EST"))
        if today.month != 12 or today.day > 25:
            raise ValueError("You can only use this classmethod during the event!")

        return cls(str(today.day))

    def __repr__(self) -> str:
        """Return the official representation of this puzzle."""
        cls_name = type(self).__name__
        return f"<{cls_name} day={self.day}>"

    def __getitem__(self, key: typing.Hashable) -> typing.Any:
        """Get an item from the helper cache."""
        return self._helper_cache[key]

    def __setitem__(self, key: typing.Hashable, value: typing.Any) -> None:
        """Get an item from the helper cache."""
        self._helper_cache[key] = value

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

    @property
    def puzzle_hash(self) -> str:
        """
        Return the hex digest of the combined input and solution hash.

        This hash can be used to determine whether we have to run the solution
        to get the answers or can use a cached answer.
        """
        hash_input = hashlib.sha1(self.input.encode("utf-8"))
        hash_solution = hashlib.sha1(self.solution_path.read_bytes())
        hash_puzzle = hashlib.sha1(hash_input.digest() + hash_solution.digest())
        return hash_puzzle.hexdigest()

    def run(self, *, submit: bool = False, ignore_cache: bool = False) -> None:
        """
        Run the puzzle solutions and print the solution.

        If `submit` is set to True, the solution will be submitted to the Advent
        of Code website automatically, unless the same answer has been submitted
        before or the current answer is `None`.
        """
        puzzle_hash = self.puzzle_hash
        cache_path = ("cached_answers", puzzle_hash)

        with AnswerCache(self.solution_directory) as cache:
            cached_answers = cache.get(*cache_path)

        if ignore_cache or not cached_answers:
            solution = importlib.import_module(self.solution_import)

            # Get puzzle preparation function
            prepare_function = getattr(solution, "prepare_puzzle", None)

            start = timeit.default_timer()
            if prepare_function:
                print("Running prepare function!")
                prepare_function(self)
            answer_one = solution.part_one(self)
            answer_two = solution.part_two(self)
            run_time = timeit.default_timer() - start

            with AnswerCache(self.solution_directory) as cache:
                cache.set(*cache_path, "answer_one", value=answer_one)
                cache.set(*cache_path, "answer_two", value=answer_two)
        else:
            log.info("no changes detected, fetching answers from cache")
            answer_one = cached_answers.get("answer_one")
            answer_two = cached_answers.get("answer_two")
            run_time = 0.0

        if submit:
            part, answer = ("1", answer_one) if answer_two is None else ("2", answer_two)
            log.info(f"Submitting `{answer}` as the answer of day {self.day} - part {part}.")
            self.submit(part, answer)

        with AnswerCache(self.solution_directory) as cache:
            answer_one_status = cache.get(
                "cached_submissions", "1", str(answer_one), default="not submitted"
            )
            answer_two_status = cache.get(
                "cached_submissions", "2", str(answer_two), default="not submitted"
            )

        title = f"Advent of Code — Solutions for day {self.day}"
        separator = "—" * len(title)

        print(separator)
        print(title)
        print(separator)
        print(f"Part one: {answer_one} ({answer_one_status})")
        print(f"Part two: {answer_two} ({answer_two_status})")
        print(separator)
        if run_time:
            print(f"Running time: {run_time:.6f}s")
        else:
            print("Running time: cached solution")

    def time(self) -> None:
        """Time the solution for this puzzle."""
        solution = importlib.import_module(self.solution_import)
        prepare_function = getattr(solution, "prepare_puzzle", None)

        results = []
        for _part in (prepare_function, solution.part_one, solution.part_two):
            if _part is None:
                results.append(None)
                continue
            timer = timeit.Timer("_part(self)", globals=locals())
            result = timer.autorange()
            results.append(result)

        title = f"Advent of Code — Runtimes for day {self.day}"
        separator = "—" * len(title)

        print(separator)
        print(title)
        print(separator)
        combined_runtime = 0
        if results[0] is not None:
            runs, run_time = results[0]
            avg_runtime = run_time / runs
            print(f"Data parsing: {avg_runtime:.6f}s avg in {runs} runs")
            combined_runtime += avg_runtime

        for i, (runs, run_time) in enumerate(results[1:], start=1):
            avg_runtime = run_time/runs
            combined_runtime += avg_runtime
            print(f"Part {i}:       {avg_runtime:.6f}s avg in {runs} runs")
        print(separator)
        print(f"Combined avg runtime: {combined_runtime:.6f}s")

    def submit(self, part: str, answer: CacheValue) -> None:
        """
        Submit the answer to the Advent of Code website.

        If `answer_two` is `None`, this function will submit the answer to part
        one. If both are `None`, no answer is submitted.

        To avoid duplicate submissions, the result for each unique answer is
        cached in the solution directory.
        """
        if answer is None:
            raise ValueError("Can't submit `None` as an answer!")

        with AnswerCache(self.solution_directory) as cache:
            cached_result = cache.get("cached_submissions", part, answer)

        if cached_result:
            log.info(
                f"this answer, `{answer}`, for day {self.day} part {part} was already submitted "
                f"and came back as {cached_result!r}"
            )
            return

        session = os.environ.get("AOC_SESSION_COOKIE")
        if not session:
            raise CookieNotSet("the environment variable `AOC_SESSION_COOKIE` was not set")

        cookies = {"session": session}

        result = None
        body_text = "[no response]"
        for retry in range(1, 3):
            log.info(f"Trying to submit answer (attempt {retry}/2)")
            r = requests.post(
                PUZZLE_ANSWER_URL.format(day=self.day),
                cookies=cookies,
                data={"level": part, "answer": answer},
            )
            if not r.ok:
                raise SubmissionFailed(
                    f"failed to submit answer `{answer}` for part {part} of day {self.day}. "
                    f"Status code: {r.status_code}"
                )

            soup = BeautifulSoup(r.text, 'html.parser')
            body_text = soup.html.body.main.article.p.text

            if body_text.startswith("That's the right answer"):
                result = "correct"
                break
            elif body_text.startswith("You gave an answer too recently"):
                result = "pending"
                log.info("answered too fast after an incorrect answer")
                if retry == 1:
                    # Calculate the required waiting time and try again...
                    d = WAIT_RE.search(body_text).groupdict(default='0')
                    waiting_time = 60 * int(d["minutes"]) + int(d["seconds"]) + 1
                    log.info(f"retrying in {waiting_time} seconds...")
                    time.sleep(waiting_time)
                else:
                    log.info("out of retries, aborting answer submission")
            elif body_text.startswith("That's not the right answer"):
                result = "wrong"
                break
            elif body_text.startswith("You don't seem to be solving the right level."):
                log.info(
                    "got a response that indicates that you've either already solved the level "
                    "or are trying to submit an answer for a part you've not unlocked yet. "
                    "See browser."
                )
                webbrowser.open(r.url)
                result = "failed"
                break
            else:
                result = "failed"
                log.error(f"received an unexpected answer from the website:\n\n{body_text}")
                break

        if result not in ("correct", "wrong"):
            log.warning("failed to submit answer!")
            return

        print(f"Submitted `{answer}` as the answer of day {self.day}, part {part}.")
        print(f"The answer is {result}")

        if answer == "wrong":
            print(f"Response: {body_text}")

        with AnswerCache(self.solution_directory) as cache:
            cache.set("cached_submissions", part, str(answer), value=result)

        # If we've just correctly submitted part 1, we probably want to see part 2
        if part == "1" and result == "correct":
            webbrowser.open(PUZZLE_BASE_URL.format(day=self.day))
