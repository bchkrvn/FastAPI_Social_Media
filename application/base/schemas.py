from typing import Generic, List, TypeVar

from pydantic import Field
from pydantic.generics import GenericModel

M = TypeVar("M")


class PaginatedResponse(GenericModel, Generic[M]):
    count: int = Field(description="Количество записей")
    items: List[M] = Field(description="Список элементов, соответствующий заданным критериям")
