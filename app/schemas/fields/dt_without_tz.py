from datetime import UTC, datetime
from typing import Annotated

from pydantic import AfterValidator, BeforeValidator, PlainSerializer


def _accept_timezone_and_to_utc_naive(value: datetime | str | int | float) -> datetime:
    if isinstance(value, (int, float)):
        value = datetime.fromtimestamp(value, tz=UTC).replace(tzinfo=None)
    elif isinstance(value, str):
        value = datetime.fromisoformat(value)
    if value.tzinfo is not None:
        return value.astimezone(UTC).replace(tzinfo=None)
    return value


def _strip_tz(value: datetime) -> datetime:
    return value.replace(tzinfo=None)


def _to_naive_iso_str(value: datetime) -> str:
    if value.tzinfo is not None:
        value = value.astimezone(UTC).replace(tzinfo=None)
    return value.isoformat()


dt_without_tz = Annotated[
    datetime,
    BeforeValidator(_accept_timezone_and_to_utc_naive),
    AfterValidator(_strip_tz),
    PlainSerializer(_to_naive_iso_str, return_type=str, when_used='json'),
]
