import collections
import functools
import itertools
import logging
import operator
import typing

from aoc.helpers import Puzzle

__all__ = ["part_one", "part_two"]
log = logging.getLogger(__name__)


class ValidationError(ValueError):
    """Raised when a number fails to validate while being processed by the cipher."""

    def __init__(self, number: int):
        super().__init__(f"number `{number}` failed preamble validation!")
        self.number = number


class XMASStreamCipher:
    """An eXchange-Masking Addition System Streaming Cipher."""

    def __init__(self, *, buffer_size: int):
        self._buffer_size = buffer_size
        self._buffer = collections.deque(maxlen=buffer_size)
        self._buffer_set = set()

    def consume(self, stream: typing.Sequence[int]) -> None:
        """Consumes and validates a stream of numbers."""
        stream_iterator = iter(stream)

        # Determine if the buffer reached the target buffer size; if not,
        # add the missing number of elements to the buffer.
        spots_left = self._buffer_size - len(self._buffer)
        if spots_left > 0:
            preamble_elements = list(itertools.islice(stream_iterator, spots_left))
            self._buffer.extend(preamble_elements)
            self._buffer_set.update(preamble_elements)

        for number in stream_iterator:
            self.process(number)

    def process(self, number: int) -> None:
        """Process a number a through the stream, validating it as we go."""
        if len(self._buffer) < self._buffer_size:
            self.add(number)
            return

        subtract = functools.partial(operator.sub, number)
        if all(d not in self._buffer_set for d in map(subtract, self._buffer_set) if d != number):
            raise ValidationError(number=number)

        self.add(number)

    def add(self, number: int) -> None:
        """Add a number to the current buffer, removing one if necessary."""
        if len(self._buffer) == self._buffer_size:
            removal = self._buffer.popleft()
            self._buffer_set.remove(removal)

        self._buffer.append(number)
        self._buffer_set.add(number)


def part_one(puzzle: Puzzle) -> typing.Optional[typing.Union[str, int]]:
    """Return the solution for part one of this day."""
    cipher = XMASStreamCipher(buffer_size=25)
    try:
        cipher.consume(puzzle.intlines)
    except ValidationError as e:
        puzzle["answer_one"] = e.number
        return e.number
    else:
        raise RuntimeError("expected to find a non-validating number, but found none.")


def part_two(puzzle: Puzzle) -> typing.Optional[typing.Union[str, int]]:
    """Return the solution for part two of this day."""
    current_sequence = collections.deque()
    current_sequence_sum = 0

    for number in puzzle.intlines:
        current_sequence_sum += number
        current_sequence.append(number)

        # If we're at or over the target value, we need to
        # check the sum and shrink the sequence if needed.
        while current_sequence_sum >= puzzle["answer_one"]:
            if current_sequence_sum == puzzle["answer_one"]:
                return min(current_sequence) + max(current_sequence)

            # We're over the target sum, remove a number from the
            # left side of the sequence.
            current_sequence_sum -= current_sequence.popleft()

    raise RuntimeError("I expected to find a result by now!")
