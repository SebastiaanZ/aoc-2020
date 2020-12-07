from __future__ import annotations

import dataclasses
import logging
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
    min_seat_id: typing.ClassVar[float] = float('inf')
    max_seat_id: typing.ClassVar[float] = float('-inf')
    seat_ids: typing.ClassVar[set] = set()

    row: int
    column: int
    seat_id: int

    @classmethod
    def from_space_partition(cls, space_partition: str) -> BoardingPass:
        """Create a boardingpass from a space partition string."""
        row = bin_to_int(space_partition[:7], zero="F", one="B")
        col = bin_to_int(space_partition[7:], zero="L", one="R")
        seat_id = row * 8 + col

        # Keep track of the seat IDs we've seen.
        cls.min_seat_id = cls.min_seat_id if cls.min_seat_id < seat_id else seat_id
        cls.max_seat_id = cls.max_seat_id if cls.max_seat_id > seat_id else seat_id
        cls.seat_ids.add(seat_id)

        return cls(row, col, seat_id)


def part_one(puzzle: Puzzle) -> typing.Optional[typing.Union[str, float, int]]:
    """Return the solution for part one of this day."""
    puzzle["boardingpasses"] = [BoardingPass.from_space_partition(entry) for entry in puzzle.lines]
    return BoardingPass.max_seat_id


def part_two(_puzzle: Puzzle) -> typing.Optional[typing.Union[str, int]]:
    """
    Return the ID of my seat.

    This solution uses a set-approach to avoid sorting the know seat IDs. It
    keeps track of the minimum and the maximum while creating the set so we
    can compare the entire range to know IDs. The only one that's missing
    should be my seat ID.
    """
    known_ids = BoardingPass.seat_ids
    minimum = int(BoardingPass.min_seat_id)
    maximum = int(BoardingPass.max_seat_id)
    return int(*known_ids.symmetric_difference(range(minimum, maximum+1)))
