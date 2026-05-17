from math import ceil

from app.schemas.base import PaginationMetaSchema


def calculate_pagination(total: int, limit: int, offset: int) -> PaginationMetaSchema:
    current_page = (offset // limit) + 1 if not total < limit else 1
    last_page = ceil(total / limit) if total > 0 else 1
    return PaginationMetaSchema(
        limit=limit,
        total=total,
        current_page=current_page,
        last_page=last_page,
    )
