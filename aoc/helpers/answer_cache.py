from __future__ import annotations

import hashlib
import json
import logging
import pathlib
import typing
import warnings

__all__ = ["AnswerCache", "CacheValue"]

log = logging.getLogger(__name__)

CacheValue = typing.Optional[typing.Union[str, int, dict]]


class AnswerCacheSingleton(type):
    _instances = {}

    def __call__(cls, solution_directory: pathlib.Path) -> AnswerCache:
        """Make sure that we only have a single AnswerCache instance for each file."""
        if solution_directory not in cls._instances:
            cls._instances[solution_directory] = super().__call__(solution_directory)

        return cls._instances[solution_directory]


class AnswerCache(metaclass=AnswerCacheSingleton):
    """A answer cache class that can be used as a context manager."""

    def __init__(self, solution_directory: pathlib.Path):
        self.cache_path = solution_directory / "answer_cache.json"

        if not self.cache_path.exists():
            self.cache_path.write_text("{}\n", encoding="utf-8")  # noqa: P103

        self._data = None
        self._uncommitted_changes = False
        self._file_hash = None

    def __repr__(self) -> str:
        """Return the official representation of a AnswerCache instance."""
        cls_name = type(self).__name__
        return f"<{cls_name} path='{self.cache_path}'>"

    def __enter__(self) -> AnswerCache:
        """Open the AnswerCache and return it for the managed context."""
        return self.open()

    def __exit__(self, *exc_information) -> None:
        """Commit changes and close the AnswerCache."""
        if all(arg is None for arg in exc_information):
            self.close(commit=True)

    def open(self) -> AnswerCache:
        """Open the AnswerCache instance and return `self`."""
        if self._data is not None:
            raise ValueError("cache is already opened.")

        file_contents = self.cache_path.read_bytes()
        self._data = json.loads(file_contents.decode(encoding="utf-8"))
        self._file_hash = hashlib.sha1(file_contents).hexdigest()
        return self

    def close(self, *, commit: bool = False) -> None:
        """Close the AnswerCache instance, optionally committing changes."""
        if self._data is None:
            raise ValueError("cache is already closed.")

        if commit:
            self.commit()

        if self._uncommitted_changes:
            warnings.warn("Closing a cache with uncommitted changes. Changes will be lost.")

        self._data = None

    def get(self, *keys, default: typing.Optional[CacheValue] = None) -> CacheValue:
        """Get a value from the cache from the nested `keys`."""
        if self._data is None:
            raise ValueError("I/O operation on closed cache.")

        value = self._data
        for key in keys[:-1]:
            value = value.get(str(key), {})

        return value.get(str(keys[-1]), default)

    def set(self, *keys, value: CacheValue) -> None:
        """
        Set the value at the `nested_keys` path in the cache.

        Note: Changes won't be committed to disk until `.commit` is called!
        """
        if self._data is None:
            raise ValueError("I/O operation on closed cache.")

        current_depth = self._data
        for key in keys[:-1]:
            current_depth = current_depth.setdefault(str(key), {})

        # The final key is assigned to the value, not another dictionary.
        current_depth[str(keys[-1])] = value
        self._uncommitted_changes = True

    def commit(self) -> None:
        """Commit the changes made to the cache to disk."""
        if self._data is None:
            raise ValueError("can't commit a closed cache.")

        if not self._uncommitted_changes:
            log.debug(f"{self}: commit called, but no changes to commit.")
            return

        if hashlib.sha1(self.cache_path.read_bytes()).hexdigest() != self._file_hash:
            warnings.warn("cache file changed on disk after opening; changes will be overwritten!")

        json.dump(self._data, self.cache_path.open(mode="w", encoding="utf-8"))
        self._uncommitted_changes = False
