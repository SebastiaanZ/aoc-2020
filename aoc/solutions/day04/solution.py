from __future__ import annotations

import dataclasses
import functools
import logging
import string
import typing

from aoc.helpers import Puzzle

__all__ = ["part_one", "part_two"]
log = logging.getLogger(__name__)


HEXDIGITS = string.hexdigits.removesuffix("ABCDEF")


def validate_year(year: str, low: str, high: str) -> bool:
    """
    Validate a year by the given lower and upper bound.

    Note: since all years should have four digits, we can compare the
    year to the lower and upper bounds as a string.
    """
    return len(year) == 4 and low <= year <= high


def validate_height(height: str) -> bool:
    """
    Validate the height field of the password.

    This validator accepts heights in the units centimeter and inch.
    """
    if height.endswith("cm"):
        return "150" <= height[:-2] <= "193"
    elif height.endswith("in"):
        return "59" <= height[:-2] <= "76"
    else:
        return False


def validate_hair_color(hair_color: str) -> bool:
    """Validate a hair color code."""
    return hair_color.startswith("#") and all(c in HEXDIGITS for c in hair_color[1:])


def validate_eye_color(eye_color: str) -> bool:
    """Validate an eye color."""
    return eye_color in ("amb", "blu", "brn", "gry", "grn", "hzl", "oth")


def validate_passport_number(passport_number: str) -> bool:
    """Validate a passport number."""
    return len(passport_number) == 9 and all(c in string.digits for c in passport_number)


VALIDATED_FIELDS = {
    "byr": functools.partial(validate_year, low="1920", high="2002"),
    "iyr": functools.partial(validate_year, low="2010", high="2020"),
    "eyr": functools.partial(validate_year, low="2020", high="2030"),
    "hgt": validate_height,
    "hcl": validate_hair_color,
    "ecl": validate_eye_color,
    "pid": validate_passport_number,
}


@dataclasses.dataclass()
class Passport:
    """
    A Passport dataclass with field validation logic.

    Note: to cheat border control, the validators ignore the country code!
    """

    byr: typing.Optional[str] = None
    iyr: typing.Optional[str] = None
    eyr: typing.Optional[str] = None
    hgt: typing.Optional[str] = None
    hcl: typing.Optional[str] = None
    ecl: typing.Optional[str] = None
    pid: typing.Optional[str] = None
    cid: typing.Optional[str] = None
    _has_required_fields: bool = dataclasses.field(init=False)
    _has_valid_fields: bool = dataclasses.field(init=False)

    @classmethod
    def from_raw_data(cls, data: str) -> Passport:
        """Create a Passport from a raw passport data string."""
        return cls(**dict(field.split(":") for field in data.split()))

    def __post_init__(self) -> None:
        """Validate this Passport instance."""
        self._has_required_fields = all(getattr(self, field) for field in VALIDATED_FIELDS)
        field_validators = (v(getattr(self, field)) for field, v in VALIDATED_FIELDS.items())
        self._has_valid_fields = self._has_required_fields and all(field_validators)

    @property
    def has_required_fields(self) -> bool:
        """Return True is this Passport has all required fields."""
        return self._has_required_fields

    @property
    def is_valid(self) -> bool:
        """Check if this passport meets the validation criteria."""
        return self._has_valid_fields


def part_one(puzzle: Puzzle) -> typing.Optional[typing.Union[str, int]]:
    """Return the solution for part one of this day."""
    puzzle["passports"] = [Passport.from_raw_data(raw) for raw in puzzle.input.split("\n\n")]
    return sum(passport.has_required_fields for passport in puzzle["passports"])


def part_two(puzzle: Puzzle) -> typing.Optional[typing.Union[str, int]]:
    """Return the solution for part two of this day."""
    return sum(passport.is_valid for passport in puzzle["passports"])
