import logging
import typing

from aoc.helpers import Puzzle

__all__ = ["part_one", "part_two"]
log = logging.getLogger(__name__)


def part_one(puzzle_input: Puzzle) -> typing.Optional[typing.Union[str, int]]:
    """
    Return the solution for part one of this day.

    This solution sorts the list of integers that we get as input and then
    iterates of that sorted list using two (nested) for-loops. As the lists
    are sorted, we know that we can break the inner-loop as we go over 2020
    as an intermediate result.

    An alternative approach would be to use a (sorted?) set instead.
    """
    puzzle_input.sorted = sorted(puzzle_input.intlines)

    for i, number_one in enumerate(puzzle_input.sorted[:-1]):
        for number_two in puzzle_input.sorted[i+1:]:
            if number_one + number_two > 2020:
                break

            if number_one + number_two == 2020:
                return number_one * number_two


def part_two(puzzle_input: Puzzle) -> typing.Optional[typing.Union[str, int]]:
    """
    Return the solution for part two of this day.

    This approach is similar to part one, except that we're now dealing with
    three loops. To break early, an additional check was added to the first
    inner loop that breaks it off when the initial third number would already
    take it over the total.
    """
    for i, number_one in enumerate(puzzle_input.sorted[:-2]):
        for j, number_two in enumerate(puzzle_input.sorted[i+1:-1], start=i+1):
            if number_one + number_two + puzzle_input.sorted[j+1] > 2020:
                break

            for number_three in puzzle_input.sorted[j+1:]:
                number_sum = number_one + number_two + number_three
                if number_sum > 2020:
                    break

                if number_sum == 2020:
                    return number_one * number_two * number_three
