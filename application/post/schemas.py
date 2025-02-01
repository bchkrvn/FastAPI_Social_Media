from datetime import datetime

from pydantic import BaseModel, Field


class PostCreateSchema(BaseModel):
    text: str = Field(..., description="Текст")


class PostUserSchema(BaseModel):
    id: int = Field(..., description="Идентификатор")
    first_name: str = Field(..., description="Имя")
    last_name: str = Field(..., description="Фамилия")


class PostGetSchema(BaseModel):
    id: int = Field(..., description="Идентификатор")
    text: str = Field(..., description="Текст")
    created: datetime = Field(..., description="Создан")
    updated: datetime = Field(..., description="Обновлен")
    user: PostUserSchema


class PostUpdateSchema(BaseModel):
    text: str = Field(..., description="Текст")
