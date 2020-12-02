import itertools
import logging
import typing

from aoc.helpers import Puzzle

__all__ = ["part_one", "part_two"]
log = logging.getLogger(__name__)


def part_one(puzzle: Puzzle) -> typing.Optional[typing.Union[str, int]]:
    """
    Return the solution for part one of this day.

    This solution uses a set to quickly look up if the complement we need
    to add to 2020 is present in the current list of numbers. Assuming that
    we're dealing with a set without critical hash collisions, this brings
    the solution down to an O(N) complexity.
    """
    puzzle["set"] = set(puzzle.intlines)

    for number_one in puzzle["set"]:
        if (2020 - number_one) in puzzle["set"]:
            return (2020 - number_one) * number_one


def part_two(puzzle: Puzzle) -> typing.Optional[typing.Union[str, int]]:
    """
    Return the solution for part two of this day.

    This approach is similar to `part_one`: It looks at all combinations of
    numbers, at a complexity cost of O(N^2), and determines whether or not
    the third number required to sum to 2020 is present in the set.
    """
    for number_one, number_two in itertools.combinations(puzzle["set"], 2):
        if (2020 - number_one - number_two) in puzzle["set"]:
            return (2020 - number_one - number_two) * number_one * number_two
