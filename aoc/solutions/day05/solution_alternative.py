import dataclasses
import logging
import operator
import typing

from aoc.helpers import Puzzle

__all__ = ["part_one", "part_two"]
log = logging.getLogger(__name__)


def bin_to_int(bin_string: str, *, zero: str = "0", one: str = "1") -> int:
    """
    Convert a binary string to an integer.

    This function accepts optional keyword arguments to specify
    the characters used for 0 and 1 in the string to support
    different encodings.
    """
    return int(bin_string.replace(zero, "0").replace(one, "1"), base=2)


@dataclasses.dataclass
class BoardingPass:
    """A dataclass to represent a boarding pass."""

    space_partition: str
    row: int = dataclasses.field(init=False)
    column: int = dataclasses.field(init=False)
    seat_id: int = dataclasses.field(init=False)

    def __post_init__(self) -> None:
        """Calculate the row and column of each boarding pass."""
        self.row = bin_to_int(self.space_partition[:7], zero="F", one="B")
        self.column = bin_to_int(self.space_partition[7:], zero="L", one="R")
        self.seat_id = self.row * 8 + self.column


def part_one(puzzle: Puzzle) -> typing.Optional[typing.Union[str, int]]:
    """Return the solution for part one of this day."""
    puzzle["boardingpasses"] = [BoardingPass(entry) for entry in puzzle.lines]
    return max(boardingpass.seat_id for boardingpass in puzzle["boardingpasses"])


def part_two(puzzle: Puzzle) -> typing.Optional[typing.Union[str, int]]:
    """Return the solution for part two of this day."""
    sorted_passes = sorted(puzzle["boardingpasses"], key=operator.attrgetter('seat_id'))
    for neighbor_one, neighbor_two in zip(sorted_passes, sorted_passes[1:]):
        if neighbor_two.seat_id - neighbor_one.seat_id == 2:
            return neighbor_one.seat_id + 1
