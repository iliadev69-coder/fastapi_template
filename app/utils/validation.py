from typing import Any

from app.resources import strings


def validate_exclusive_presence(first: Any | None, second: Any | None) -> None:
    """Validates that exactly one of `first` or `second` is provided."""
    is_first = first is not None
    is_second = second is not None
    if is_first == is_second:
        raise ValueError(strings.EXCLUSIVE_PRESENCE)
