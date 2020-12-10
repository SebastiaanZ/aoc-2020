import collections
import logging
import typing

from aoc.helpers import Puzzle


__all__ = ["part_one", "part_two"]
log = logging.getLogger(__name__)


def part_one(puzzle: Puzzle) -> typing.Optional[typing.Union[str, int]]:
    """Return the longest adapter path between the power source and my device."""
    puzzle["adapters"] = [0] + sorted(puzzle.intlines)
    c = collections.Counter(b - a for a, b in zip(puzzle["adapters"], puzzle["adapters"][1:]))
    return c[1] * (c[3]+1)


def part_two(puzzle: Puzzle) -> typing.Optional[typing.Union[str, int]]:
    """Return the number of possible combinations of adapters I could use."""
    connections = {puzzle["adapters"][0]: 1}
    for adapter in puzzle["adapters"][1:]:
        connections[adapter] = sum(connections.get(adapter-i, 0) for i in range(1, 4))
    return connections.popitem()[1]
