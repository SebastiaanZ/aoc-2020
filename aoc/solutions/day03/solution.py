import logging
import typing

from aoc.helpers import Puzzle

__all__ = ["part_one", "part_two"]
log = logging.getLogger(__name__)


def part_one(puzzle: Puzzle) -> typing.Optional[typing.Union[str, int]]:
    """
    Return the solution for part one of day 3.

    In this day, we have to traverse a grid of open spaces and trees at certain
    integer slopes like "1 down, 3 right". The answer is based on the number of
    trees you encounter along the way. An open space is indicated by a `.` on
    the map and the symbol for a tree is `#`.

    My initial guess was that I'd have to find the optimal integer heading of
    the form "1 down, n right" in part two, so I coded part one to make that
    trivial. While the code written wasn't exactly useless for part two, my
    guess for the goal of part two was completely wrong.
    """
    width = len(puzzle.lines[0])

    # Create a starting dictionary for all possible 1 down, n right headings
    # Note: I expected that I'd need them all for part two...
    puzzle["headings"] = dict.fromkeys(range(width), 0)

    # Initialize count for part two's 2 down, 1 right heading
    puzzle["right_one_down_two"] = 0

    # Count trees! This gives me each new row, keeping track of the
    # number of moves we've currently done.
    for moves, line in enumerate(puzzle.lines[1:], start=1):
        # Check if we're colliding with a tree for all "1 down" headings
        for heading in range(len(puzzle.lines[0])):
            puzzle["headings"][heading] += line[moves*heading % width] == "#"

        # Precalculate answer for 2 down, 1 right for part two
        if moves % 2 == 0:
            puzzle["right_one_down_two"] += line[(moves // 2) % width] == "#"

    # Return the result for the heading of part one
    return puzzle["headings"][3]


def part_two(puzzle: Puzzle) -> typing.Optional[typing.Union[str, int]]:
    """
    Return the solution for part two of day 3.

    Unfortunately, the question for part two was not the one I was expecting,
    so I had to go back and adjust part one slightly. The work done in part
    one was still useful albeit overkill for the problem at hand.
    """
    # Calculate the multiplication of 1 down, 1, 3, 5, 7 right headings.
    answer = 1
    for heading in range(1, 8, 2):
        answer *= puzzle["headings"][heading]

    # Multiply by 2 down, 1 right for the answer
    return answer * puzzle["right_one_down_two"]
