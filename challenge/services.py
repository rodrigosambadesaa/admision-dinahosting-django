from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Iterable
import re


# Match the original JavaScript form and PHP CLI: ASCII only, exact UTC dates.
DATETIME_PATTERN = re.compile(r"([0-9]{4})-([0-9]{2})-([0-9]{2}) ([0-9]{2}):([0-9]{2}):([0-9]{2})")
INPUT_PATTERN = re.compile(r"(?:[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}|ts:[+-]?[0-9]{1,256})")
MAX_SYNTHETIC_DIGITS = 256


class InputSanitizationError(ValueError):
    pass


@dataclass(frozen=True)
class RangeBoundary:
    label: str
    timestamp: int
    timezone: str


@dataclass(frozen=True)
class DateRange:
    start_timestamp: int
    end_timestamp: int
    start_label: str
    end_label: str
    timezone: str = "UTC"

    def __post_init__(self) -> None:
        if self.start_timestamp <= self.end_timestamp:
            return

        start_timestamp = self.end_timestamp
        end_timestamp = self.start_timestamp
        start_label = self.end_label
        end_label = self.start_label

        object.__setattr__(self, "start_timestamp", start_timestamp)
        object.__setattr__(self, "end_timestamp", end_timestamp)
        object.__setattr__(self, "start_label", start_label)
        object.__setattr__(self, "end_label", end_label)

    def to_dict(self) -> dict[str, str]:
        """Match the PHP CLI range object, including exact string timestamps."""
        def cli_label(label: str) -> str:
            return label[:-4] if label.endswith(" UTC") else label

        return {
            "start": cli_label(self.start_label),
            "end": cli_label(self.end_label),
            "timezone": self.timezone,
            "start_timestamp": str(self.start_timestamp),
            "end_timestamp": str(self.end_timestamp),
        }


class FibonacciSequenceGenerator:
    def generate_up_to(self, limit: int) -> list[int]:
        if limit < 0:
            return []

        sequence = [0]
        if limit == 0:
            return sequence

        sequence.append(1)
        previous, current = 0, 1

        while True:
            next_value = previous + current
            if next_value > limit:
                break

            sequence.append(next_value)
            previous, current = current, next_value

        return sequence


class FibonacciRangeResolver:
    def __init__(self, generator: FibonacciSequenceGenerator | None = None) -> None:
        self.generator = generator or FibonacciSequenceGenerator()

    def resolve(self, date_range: DateRange) -> list[int]:
        return [
            value
            for value in self.generator.generate_up_to(date_range.end_timestamp)
            if date_range.start_timestamp <= value <= date_range.end_timestamp
        ]


class CurrentMonthRangeProvider:
    label = "Mes actual"

    def get_range(self) -> DateRange:
        now = datetime.now(UTC)
        start = datetime(now.year, now.month, 1, 0, 0, 0, tzinfo=UTC)
        if now.month == 12:
            next_month = datetime(now.year + 1, 1, 1, 0, 0, 0, tzinfo=UTC)
        else:
            next_month = datetime(now.year, now.month + 1, 1, 0, 0, 0, tzinfo=UTC)
        end = next_month - timedelta(seconds=1)

        return DateRange(
            start_timestamp=int(start.timestamp()),
            end_timestamp=int(end.timestamp()),
            start_label=format_utc_datetime(start),
            end_label=format_utc_datetime(end),
        )


class CurrentYearRangeProvider:
    label = "Año actual"

    def get_range(self) -> DateRange:
        now = datetime.now(UTC)
        start = datetime(now.year, 1, 1, 0, 0, 0, tzinfo=UTC)
        end = datetime(now.year, 12, 31, 23, 59, 59, tzinfo=UTC)

        return DateRange(
            start_timestamp=int(start.timestamp()),
            end_timestamp=int(end.timestamp()),
            start_label=format_utc_datetime(start),
            end_label=format_utc_datetime(end),
        )


class CustomRangeProvider:
    label = "Rango personalizado"

    def __init__(self, start_value: str, end_value: str) -> None:
        self.start_value = start_value
        self.end_value = end_value

    def get_range(self) -> DateRange:
        start_boundary = parse_range_boundary(self.start_value)
        end_boundary = parse_range_boundary(self.end_value)

        return DateRange(
            start_timestamp=start_boundary.timestamp,
            end_timestamp=end_boundary.timestamp,
            start_label=start_boundary.label,
            end_label=end_boundary.label,
            timezone=(
                start_boundary.timezone
                if start_boundary.timezone == end_boundary.timezone
                else f"{start_boundary.timezone} -> {end_boundary.timezone}"
            ),
        )


def sanitize_range_input(value: str) -> str:
    if not isinstance(value, str):
        raise InputSanitizationError("La entrada recibida no es válida.")

    sanitized = value.strip()
    if not sanitized:
        raise InputSanitizationError("La entrada recibida no es válida.")

    if len(sanitized) > 260 or not INPUT_PATTERN.fullmatch(sanitized):
        raise InputSanitizationError('Usa "Y-m-d H:i:s" o "ts:<bigint>".')

    return sanitized


def parse_range_boundary(value: str) -> RangeBoundary:
    if value.startswith("ts:"):
        raw = value[3:]
        if len(raw.lstrip("+-")) > MAX_SYNTHETIC_DIGITS or not re.fullmatch(r"[+-]?[0-9]{1,256}", raw):
            raise ValueError('Usa el formato "ts:<bigint>" para timestamps sintéticos extremos.')

        return RangeBoundary(
            label=f"ts:{raw}",
            timestamp=int(raw),
            timezone="synthetic-bigint",
        )

    return RangeBoundary(
        label=f"{value} UTC",
        timestamp=parse_utc_datetime(value),
        timezone="UTC",
    )


def parse_utc_datetime(value: str) -> int:
    match = DATETIME_PATTERN.fullmatch(value)
    if not match:
        raise ValueError('Usa el formato "Y-m-d H:i:s".')

    year, month, day, hour, minute, second = (int(part) for part in match.groups())
    # Python datetime has no year 0000, unlike the original browser implementation.
    # Calculate epoch seconds with proleptic Gregorian arithmetic and no floats.
    if not 1 <= month <= 12 or not 0 <= hour <= 23 or not 0 <= minute <= 59 or not 0 <= second <= 59:
        raise ValueError("La fecha indicada no es válida.")
    leap = year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)
    days_in_month = (31, 29 if leap else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)
    if not 1 <= day <= days_in_month[month - 1]:
        raise ValueError("La fecha indicada no es válida.")

    y = year - (month <= 2)
    era = y // 400
    year_of_era = y - era * 400
    shifted_month = month + (-3 if month > 2 else 9)
    day_of_year = (153 * shifted_month + 2) // 5 + day - 1
    year_days = year_of_era * 365 + year_of_era // 4 - year_of_era // 100 + day_of_year
    days_from_epoch = era * 146097 + year_days - 719468
    return days_from_epoch * 86400 + hour * 3600 + minute * 60 + second

def format_utc_datetime(value: datetime) -> str:
    return value.strftime("%Y-%m-%d %H:%M:%S UTC")


def build_fibonacci_sections(start_value: str, end_value: str) -> list[dict[str, str | DateRange | list[int]]]:
    resolver = FibonacciRangeResolver()
    providers: Iterable[object] = (
        CurrentMonthRangeProvider(),
        CurrentYearRangeProvider(),
        CustomRangeProvider(start_value, end_value),
    )

    sections = []
    for provider in providers:
        date_range = provider.get_range()
        sections.append(
            {
                "label": provider.label,
                "range": date_range,
                "values": resolver.resolve(date_range),
            }
        )

    return sections
