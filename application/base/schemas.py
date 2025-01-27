from typing import Generic, List, TypeVar

from pydantic import BaseModel, Field

M = TypeVar("M")


class PaginatedResponse(BaseModel, Generic[M]):
    count: int = Field(description="Количество записей")
    page: int = Field(description="Номер страницы")
    items: List[M] = Field(description="Список элементов, соответствующий заданным критериям")
