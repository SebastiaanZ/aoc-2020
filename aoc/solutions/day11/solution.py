from __future__ import annotations

import functools
import logging
import typing
from collections import Callable, Generator

from aoc.helpers import Puzzle


__all__ = ["part_one", "part_two"]
log = logging.getLogger(__name__)

# For every seat, we only have to check for existing neighbors in the direction
# of seats we've already processed. THere's no use in looking at locations we've
# not processed yet. Neighbor relationships "in the future" will be back filled
# when we process the future neighbor.
DIRECTIONS_TO_CHECK = (complex(-1, 0), complex(-1, -1), complex(0, -1), complex(1, -1))

# New types
SeatStates = typing.NewType('SeatStates', dict[complex, bool])
Neighbors = typing.NewType('Neighbors', dict[complex, list[complex]])
BoundsCheck = typing.NewType("BoundsCheck", Callable[[complex], bool])


def adjacent_neighbors(seats: SeatStates, location: complex) -> Generator[complex, None, None]:
    """Yield known adjacent neighbors for this location."""
    for direction in DIRECTIONS_TO_CHECK:
        if (neighbor := location + direction) in seats:
            yield neighbor


def visible_neighbors(
        seats: SeatStates, location: complex, *, in_bounds: BoundsCheck
) -> Generator[complex, None, None]:
    """Yield neighbors visible from the current location."""
    for direction in DIRECTIONS_TO_CHECK:
        neighbor = location
        while in_bounds(neighbor := neighbor + direction):
            if neighbor in seats:
                yield neighbor
                break


def parse_seats(grid: list[str], neighbor_generator: Callable) -> tuple[SeatStates, Neighbors]:
    """
    Parse the grid to find seats and register which neighbors they have.

    The passed `neighbor_generator` will be used to find the relevant neighbors
    for the current seat. The generator function should only check for neighbors
    in the direction of locations we've already processed (the three directions
    towards to top of the room and left), as it's no use looking for neighbors
    that haven't been indexed yet.

    As detecting a neighbor appends the relationship in both directions, the
    neighbours towards the bottom and right of the current location will be
    filled in once we reach them.
    """
    seats = SeatStates({})
    neighbors = Neighbors({})

    for y, row in enumerate(grid):
        for x, cell in enumerate(row):
            if cell != "L":
                continue

            # Initialize this seat location
            location = complex(x, y)
            seats[location] = False
            neighbors[location] = []

            # Iterate over all the neighbors for this seat and add a
            # bidirectional relationship between the seats.
            for neighbor in neighbor_generator(seats, location):
                neighbors[neighbor].append(location)
                neighbors[location].append(neighbor)

    return seats, neighbors


def seating_simulation(seats: SeatStates, neighbors: Neighbors, neighbor_limit: int) -> int:
    """Return the number of occupied seats after finding a stable state."""
    while True:
        # We need a copy to prevent using a partially updated state for
        # all seats after seat 1.
        old_seats = seats.copy()
        for seat, taken in old_seats.items():
            occupied_neighbors = sum(old_seats[n] for n in neighbors[seat])
            seats[seat] = occupied_neighbors < neighbor_limit if taken else occupied_neighbors == 0

        # Check if the situation has stabilized.
        if old_seats == seats:
            return sum(seats.values())


def part_one(puzzle: Puzzle) -> typing.Optional[typing.Union[str, int]]:
    """Return the number of occupied seats after the seating arrangements stabilizes."""
    seats, neighbors = parse_seats(puzzle.lines, adjacent_neighbors)
    return seating_simulation(seats, neighbors, neighbor_limit=4)


def part_two(puzzle: Puzzle) -> typing.Optional[typing.Union[str, int]]:
    """Return the number of occupied seats after the seating arrangements stabilizes."""
    width = len(puzzle.lines[0])

    def bounds_check(location: complex) -> bool:
        """Check if this location is still within bounds of the waiting room."""
        return 0 <= location.real < width and 0 <= location.imag

    neighbor_generator = functools.partial(visible_neighbors, in_bounds=bounds_check)

    seats, neighbors = parse_seats(puzzle.lines, neighbor_generator)
    return seating_simulation(seats, neighbors, neighbor_limit=5)
