"""Utilities for parsing and managing time related objects."""

from __future__ import annotations

import enum
import math
from calendar import Calendar
from calendar import month_name
from collections.abc import Sequence
from typing import Any
from typing import Iterator
from typing import Protocol
from typing import TypeAlias
from typing import TypeVar

from whenever import Date
from whenever import DateDelta
from whenever import Time
from whenever import TimeDelta


def breakdown_seconds(total_seconds: int) -> tuple[int, int, int]:
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    return hours, minutes, seconds


def format_seconds(total_seconds: int, *, include_seconds: bool = True) -> str:
    hours, minutes, seconds = breakdown_seconds(total_seconds)
    result = f"{hours:0>2}:{minutes:0>2}"
    if include_seconds:
        result += f":{seconds:0>2}"
    return result


class DateTime(Protocol):
    @property
    def hour(self) -> int: ...
    @property
    def minute(self) -> int: ...
    @property
    def second(self) -> int: ...


def time_to_seconds(ts: DateTime) -> int:
    return (ts.hour * 3600) + (ts.minute * 60) + (ts.second)


class DateScope(enum.Enum):
    MONTH = enum.auto()
    YEAR = enum.auto()
    DECADE = enum.auto()
    CENTURY = enum.auto()


Scope: TypeAlias = list[list[int]] | list[list[str]]


def _get_year_scope() -> list[list[str]]:
    year_scope: list[list[str]] = []
    month_names = list(month_name)[1:]
    for i in range(4):
        year_scope.append([])
        year_scope[i].extend(month_names[i * 3 : i * 3 + 3])
    return year_scope


def _get_decade_scope(period: Date) -> list[list[int]]:
    data: list[list[int]] = []
    year = math.floor(period.year / 10) * 10
    for i, y in enumerate(range(year, year + 10)):
        if i % 3 == 0:
            data.append([])
        data[i // 3].append(y)
    return data


def _get_century_scopee(period: Date) -> list[list[int]]:
    data: list[list[int]] = []
    century = math.floor(period.year / 100) * 100
    for i, year in enumerate(range(century, century + 100, 10)):
        if i % 3 == 0:
            data.append([])
        data[i // 3].append(year)
    return data


def get_scope(scope: DateScope, period: Date) -> Scope:
    """Creates a two dimensional array depending on supplied scope.

    Args:
        scope: The scope of time the data should encompass.
        period: Period to filter for the data.

    Raises:
        NotImplementedError: If the wrong date scope is supplied.

    Returns:
        The range of times in a two dimensional array.
    """

    if scope == DateScope.MONTH:
        return Calendar().monthdayscalendar(period.year, period.month)
    if scope == DateScope.YEAR:
        return _get_year_scope()
    if scope == DateScope.DECADE:
        return _get_decade_scope(period)
    if scope == DateScope.CENTURY:
        return _get_century_scopee(period)

    raise NotImplementedError(f"{scope.name} scope is not implemented!")


def add_time(time: DateTime, delta: TimeDelta) -> Time:
    value = time_to_seconds(time) + int(delta.in_seconds())
    if value <= 0:
        return Time()
    return Time.parse_common_iso(format_seconds(min(value, 86399)))


def round_time(time: DateTime, multiple: int) -> Time:
    seconds = round((time_to_seconds(time) / multiple) * multiple)
    return Time.parse_common_iso(format_seconds(seconds))


def iterate_timespan(
    start: Date,
    increment: DateDelta,
    total: int,
) -> Iterator[Date]:
    for _ in range(total):
        yield start
        try:
            start += increment
        except ValueError:
            return


def _nomalize_value(
    value: float | None, min_val: float, denom: float
) -> float | None:
    if value is None:
        return None
    try:
        return (value - min_val) / denom
    except ZeroDivisionError:
        return 0


def normalize_values(values: Sequence[float | None]) -> list[float | None]:
    """Normalizes an sequence of values to the range of 0 to 1."""
    min_val, max_val = (
        min(v for v in values if v is not None),
        max(v for v in values if v is not None),
    )
    denom = max_val - min_val
    return [
        _nomalize_value(values[i], min_val, denom) for i in range(len(values))
    ]


T = TypeVar("T")


def flat_to_shape(
    values: Sequence[T],
    shape: list[list[Any]],
) -> list[list[T]]:
    """Transform a flat iterable back into a two dimensional one."""
    total = 0
    for row in range(len(shape)):
        for i in range(len(shape[row])):
            shape[row][i] = values[total]
            total += 1

    return shape
