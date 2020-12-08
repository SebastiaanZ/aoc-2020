from __future__ import annotations

import collections
import logging
import typing

from aoc.helpers import Puzzle

__all__ = ["part_one", "part_two", "prepare_puzzle"]
log = logging.getLogger(__name__)


class Instruction(typing.NamedTuple):
    """A ConsoleApplication instruction."""

    operation: str
    argument: int

    @classmethod
    def from_text(cls, instruction: str) -> Instruction:
        """Parse a raw text instruction and return an Instruction instance."""
        operation, raw_argument = instruction.split(" ")
        return cls(operation=operation, argument=int(raw_argument))


class ApplicationState(typing.NamedTuple):
    """An application exit state."""

    success: bool
    value: int


class ConsoleApplication:
    """A virtual handheld game console."""

    def __init__(self, instructions: dict[int, Instruction]) -> None:
        """Parse the instructions and load the application into memory."""
        self.instructions = dict(instructions)
        self.pointer = 0
        self.accumulator = 0

    @classmethod
    def from_raw_instructions(
            cls: type[ConsoleApplication],
            instructions: list[str]
    ) -> ConsoleApplication:
        """Create an application from a raw instruction set."""
        instructions = {
            i: Instruction.from_text(instruction) for i, instruction in enumerate(instructions)
        }
        return cls(instructions=instructions)

    def copy(self) -> ConsoleApplication:
        """Create a copy of the application."""
        return type(self)(self.instructions)

    def run(self, debug_mode: bool = False) -> ApplicationState:
        """
        Run the application and return the final accumulator value as the exit code.

        If run in safe mode, the application returns whenever it detects it has
        entered an infinite loop by keeping track of the instructions it has
        executed previously.
        """
        if debug_mode:
            seen = set()
            while True:
                if self.pointer in seen:
                    return ApplicationState(success=False, value=self.accumulator)
                if self.pointer == len(self.instructions):
                    return ApplicationState(success=True, value=self.accumulator)

                seen.add(self.pointer)
                self.step()
        else:
            while True:
                self.step()
                if self.pointer == len(self.instructions):
                    return ApplicationState(success=True, value=self.accumulator)

    def step(self) -> None:
        """Perform a single step in the application."""
        operation, argument = self.instructions[self.pointer]
        getattr(self, operation)(argument)

    def acc(self, value: int) -> None:
        """Add a `value` to the accumulator and increase the pointer by one."""
        self.accumulator += value
        self.pointer += 1

    def jmp(self, steps: int) -> None:
        """Execute a jump to another instruction relative to its own location."""
        self.pointer += steps

    def nop(self, _argument: int) -> None:
        """Do not do anything at all except going to the next instruction."""
        self.pointer += 1


def debugger(application: ConsoleApplication) -> int:
    """
    Debug a ConsoleApplication by tracing terminating paths.

    This debugger works by taking the followings steps:

    1. For each instruction position, determine which instructions end up there;
    2. Use the instruction targets to trace which instructions will end up at
       the termination location;
    3. Run to the application, checking if an operation flip would make us jump
       to a halting path target location.

    It returns the final value after the application has halted successfully.
    """
    # 1. For each instruction location, determine which instructions end up there.
    instruction_locations = collections.defaultdict(list)
    for i, (instruction, value) in reversed(application.instructions.items()):
        if instruction == "jmp":
            instruction_locations[i + value].append(i)
        else:
            instruction_locations[i + 1].append(i)

    # 2. Use the target locations of instructions to determine which
    # instructions already lead naturally to the halting position.
    targets = {len(application.instructions)}
    targets_to_check = {len(application.instructions)}
    while True:
        new_targets = set()
        for target in targets_to_check:
            new_targets.update(instruction_locations[target])
        if not new_targets:
            # No other instructions end up at an identified target instruction.
            break

        targets_to_check = new_targets
        targets.update(new_targets)

    # 3. Run the application, checking for each `jmp` or `nop` instruction if
    # flipping it would result in the application hitting a target instruction.
    changed = False
    while application.pointer != len(application.instructions):
        operation, argument = application.instructions[application.pointer]
        if not changed and operation == "jmp" and application.pointer + 1 in targets:
            application.pointer += 1
            changed = True
        elif not changed and operation == "nop" and application.pointer + argument in targets:
            application.pointer += argument
            changed = True
        else:
            getattr(application, operation)(argument)

    # Return the final value of the accumulator
    return application.accumulator


def prepare_puzzle(puzzle: Puzzle) -> None:
    """Prepare the ConsoleApplication for today's puzzle."""
    puzzle["application"] = ConsoleApplication.from_raw_instructions(puzzle.lines)


def part_one(puzzle: Puzzle) -> typing.Optional[typing.Union[str, int]]:
    """Return the solution for part one of this day."""
    return puzzle["application"].run(debug_mode=True).value


def part_two(puzzle: Puzzle) -> typing.Optional[typing.Union[str, int]]:
    """Return the solution for part two of this day."""
    return debugger(puzzle["application"].copy())
