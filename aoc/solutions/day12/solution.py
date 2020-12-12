import dataclasses
import enum
import functools
import logging
import typing
from collections import Generator

from aoc.helpers import Puzzle

__all__ = ["part_one", "part_two"]
log = logging.getLogger(__name__)


# Relate a human-readable cardinal direction to a heading on the
# complex plane. Note that the x-axis (WEST-EAST) maps to the real
# part of the complex coordinate and the x-axis (NORTH-SOUTH) maps
# to the imaginary part of the complex coordinate.
class CardinalDirection(enum.Enum):
    NORTH = complex(0, 1)
    SOUTH = complex(0, -1)
    EAST = complex(1, 0)
    WEST = complex(-1, 0)


# Relate a human-readable rotation direction to a multiplication factor
# to rotate around the origin of the complex plane.
class Rotation(enum.Enum):
    LEFT = complex(0, 1)
    RIGHT = complex(0, -1)

    def by_degrees(self, degrees: int) -> complex:
        """Calculate the total rotation factor based on the specified degrees."""
        rotation_factor = degrees // 90
        return self.value ** rotation_factor


@dataclasses.dataclass
class Ferry:
    """
    A ferry used to travel to remove, tropical islands.

    This ferry can operate in two distinct navigation modes:
    1. The ferry can navigate using a waypoint relative to the ferry's location;
    2. The ferry can navigate without using a waypoint.

    The waypoint functionality can be enabled by passing the initial location
    of the waypoint relative to the ferry in the constructor call.
    """

    location: complex = complex(0, 0)
    heading: complex = complex(1, 0)
    waypoint: typing.Optional[complex] = None

    def cardinal_move(self, distance: int, *, direction: CardinalDirection) -> None:
        """
        Move the ferry or the waypoint in the specified Cardinal direction.

        If the ferry is using a waypoint, this function will move the waypoint
        in the specified direction. If the ferry is operating without a waypoint,
        the ferry itself will be moved in the specified direction; it's heading
        will remain the same.
        """
        if self.waypoint is None:
            self.location += distance * direction.value
        else:
            self.waypoint += distance * direction.value

    def rotate(self, degrees: int, *, rotation: Rotation) -> None:
        """
        Rotate the ferry or the waypoint the specified degrees left or right.

        If the ferry is using a waypoint to navigate, the waypoint will be
        rotated around the ship by the specified degrees. If the ferry is
        currently operating without a waypoint, the ferry itself will be
        rotated.
        """
        if self.waypoint is None:
            self.heading *= rotation.by_degrees(degrees)
        else:
            self.waypoint *= rotation.by_degrees(degrees)

    def forward(self, distance: int) -> None:
        """Move the ferry forward using the current heading or waypoint location."""
        if self.waypoint is None:
            self.location += self.heading * distance
        else:
            self.location += self.waypoint * distance

    # Define partialmethods and method aliases we need to relate instructions
    # directly to the Ferry methods that need to be executed for them.
    N = functools.partialmethod(cardinal_move, direction=CardinalDirection.NORTH)
    S = functools.partialmethod(cardinal_move, direction=CardinalDirection.SOUTH)
    E = functools.partialmethod(cardinal_move, direction=CardinalDirection.EAST)
    W = functools.partialmethod(cardinal_move, direction=CardinalDirection.WEST)
    L = functools.partialmethod(rotate, rotation=Rotation.LEFT)
    R = functools.partialmethod(rotate, rotation=Rotation.RIGHT)
    F = forward

    @property
    def distance_from_origin(self) -> int:
        """Return the Manhattan distance from the ferry's original location."""
        return int(abs(self.location.real) + abs(self.location.imag))


def instructions(raw_instructions: list[str]) -> Generator[tuple[str, int], None, None]:
    """Yield the next instruction for our ferry."""
    for line in raw_instructions:
        yield line[0], int(line[1:])


def part_one(puzzle: Puzzle) -> typing.Optional[typing.Union[str, int]]:
    """Move the ferry using the provided instructions."""
    ferry = Ferry()
    for instruction, units in instructions(puzzle.lines):
        getattr(ferry, instruction)(int(units))

    return ferry.distance_from_origin


def part_two(puzzle: Puzzle) -> typing.Optional[typing.Union[str, int]]:
    """Move the ferry using the provided instructions and its waypoint."""
    ferry = Ferry(waypoint=complex(10, 1))
    for instruction, units in instructions(puzzle.lines):
        getattr(ferry, instruction)(int(units))

    return ferry.distance_from_origin
