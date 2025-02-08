from typing import Generic, List, TypeVar

from pydantic import BaseModel, Field

M = TypeVar("M")


class PaginatedResponse(BaseModel, Generic[M]):
    count: int = Field(description="Количество записей")
    page: int = Field(description="Номер страницы")
    items: List[M] = Field(description="Список элементов, соответствующий заданным критериям")


def get_paginated_response(items: list, page: int) -> dict:
    result = {
        "count": len(items),
        "page": page,
        "items": items,
    }
    return result
