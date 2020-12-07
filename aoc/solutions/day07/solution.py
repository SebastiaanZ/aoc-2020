from __future__ import annotations

import collections
import dataclasses
import functools
import logging
import typing

from aoc.helpers import Puzzle

__all__ = ["part_one", "part_two", "prepare_puzzle"]
log = logging.getLogger(__name__)


class BagCollection(collections.UserDict):
    """A dict-like Bag Collection."""

    def __getitem__(self, key: typing.Union[str, Bag]) -> Bag:
        """Get a Bag from our bag collection, inserting missing bags as needed."""
        if isinstance(key, Bag):
            key = Bag.name

        if key not in self.data:
            self.data[key] = Bag(key)

        return self.data[key]


@dataclasses.dataclass
class Bag:
    """"A type of bag."""

    name: str
    children: typing.Dict[Bag, int] = dataclasses.field(default_factory=dict, repr=False)
    parents: typing.Set[Bag] = dataclasses.field(default_factory=set, repr=False)

    def __eq__(self, other: Bag) -> bool:
        """Determine whether or not a bag is equal to `other`."""
        if not isinstance(other, Bag):
            return False

        return self.name == other.name

    def __hash__(self) -> int:
        """Return a hash value based on the bag's name."""
        return hash(self.name)

    @functools.cached_property
    def nested_bag_count(self) -> int:
        """
        Return the number of bags necessary to fill this bag.

        The value for this count is cached, as the same bag may be required as
        content for multiple parent bags. This means we only have to go down the
        set of children for each bag once.
        """
        return sum(n + n * child.nested_bag_count for child, n in self.children.items())

    @functools.cached_property
    def ancestors(self) -> typing.Set[Bag]:
        """
        Return the set of ancestors for this bag.

        As the same bag may be an ancestor to multiple bags, we cache the
        ancestry the first time we calculate it.
        """
        ancestors = set(self.parents)
        for parent in self.parents:
            ancestors.update(parent.ancestors)

        return ancestors

    def add_child(self, child: Bag, quantity: int) -> None:
        """Add a child to this bag and add this bag as the parent of the child."""
        self.children[child] = quantity
        child.parents.add(self)


def prepare_puzzle(puzzle: Puzzle) -> None:
    """Prepare the input for today's puzzle."""
    puzzle["bags"] = BagCollection()
    for bag in puzzle.lines:
        bag_name, _sep, children = bag.partition(" bags contain ")
        bag = puzzle["bags"][bag_name]

        if children.startswith("no other bags"):
            continue

        for child in children.rstrip(".").split(", "):
            quantity, _sep, child_name = child.partition(" ")
            child_name = " ".join(child_name.split(" ")[:2])
            child = puzzle["bags"].setdefault(child_name, Bag(child_name))
            bag.add_child(child, int(quantity))


def part_one(puzzle: Puzzle) -> typing.Optional[typing.Union[str, int]]:
    """Count the number of ancestors of my shiny gold back and return it."""
    return len(puzzle["bags"]["shiny gold"].ancestors)


def part_two(puzzle: Puzzle) -> typing.Optional[typing.Union[str, int]]:
    """Count the number of bags my shiny gold bag needs to contain."""
    return puzzle["bags"]["shiny gold"].nested_bag_count
