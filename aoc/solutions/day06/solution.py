import functools
import logging
import typing

from aoc.helpers import Puzzle

__all__ = ["part_one", "part_two"]
log = logging.getLogger(__name__)

CustomsGroups = typing.NewType("CustomsGroups", typing.List[typing.List[typing.Set[str]]])


def reduced_groups_count(groups: CustomsGroups, reduction_func: typing.Callable) -> int:
    """
    Return the sum of group answer frequencies reduced by a reduction function.

    With `set.union`, this function returns the sum of the number of unique
    answers given per group.

    With `set.intersection`, this function returns the sum of the number of
    answers shared by all members in a group.
    """
    return sum(len(functools.reduce(reduction_func, group)) for group in groups)


def part_one(puzzle: Puzzle) -> typing.Optional[typing.Union[str, int]]:
    """Return the sum of the number of unique answers given per group."""
    puzzle["groups"] = CustomsGroups(
        [
            [set(individual) for individual in group.splitlines()]
            for group in puzzle.input.split("\n\n")
        ]
    )
    return reduced_groups_count(puzzle["groups"], set.union)


def part_two(puzzle: Puzzle) -> typing.Optional[typing.Union[str, int]]:
    """Return the sum of the number of answers shared by all in a group."""
    return reduced_groups_count(puzzle["groups"], set.intersection)
