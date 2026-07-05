from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass(frozen=True)
class Interaction:
    kind: str
    account: str
    timestamp: datetime | None = None
    source: str = ""


@dataclass(frozen=True)
class PostMetric:
    index: int
    likes: int
    comments: int
    timestamp: datetime | None = None
    owner: str = ""
    source: str = ""


def timestamp_to_datetime(value: object) -> datetime | None:
    if value is None:
        return None

    if isinstance(value, datetime):
        return value

    if isinstance(value, (int, float)):
        try:
            return datetime.fromtimestamp(value, tz=timezone.utc)
        except (OverflowError, OSError, ValueError):
            return None

    if isinstance(value, str):
        stripped = value.strip()
        if not stripped:
            return None
        if stripped.isdigit():
            return timestamp_to_datetime(int(stripped))
        try:
            return datetime.fromisoformat(stripped.replace("Z", "+00:00"))
        except ValueError:
            return None

    return None
