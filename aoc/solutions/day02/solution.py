import logging
import typing
import re

from aoc.helpers import Puzzle

__all__ = ["part_one", "part_two"]
log = logging.getLogger(__name__)


def part_one(puzzle: Puzzle) -> typing.Optional[typing.Union[str, int]]:
    """
    Analyze the passwords for both parts and return the answer to part one.

    This function calculates the answers for both parts in one go, as it's
    easy to do in a single `for`-loop. While not strictly necessary, I've
    chosen to use a regex pattern, as it's straightforward and readable.

    The answer for `part_two` is cached within the Puzzle instance so
    `part_two` can simply access it and return it as the answer.
    """
    answer_one = 0
    answer_two = 0
    for low, hi, char, pw in re.findall(r"^(\d+)-(\d+) ([a-z]): ([a-z]+)$", puzzle.input, re.M):
        low, hi = int(low), int(hi)
        answer_one += low <= pw.count(char) <= hi
        answer_two += (pw[low-1] == char) ^ (pw[hi-1] == char)

    puzzle["answer_two"] = answer_two
    return answer_one


def part_two(puzzle: Puzzle) -> typing.Optional[typing.Union[str, int]]:
    """Return the answer for part two of day two."""
    return puzzle["answer_two"]
