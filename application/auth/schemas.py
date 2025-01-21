from datetime import date, datetime

from pydantic import BaseModel, Field, field_validator


class SchemaRegister(BaseModel):
    email: str = Field(..., description="Электронная почта")
    password: str = Field(..., min_length=8, max_length=50, description="Пароль, от 5 до 50 знаков")
    first_name: str = Field(..., min_length=3, max_length=50, description="Имя")
    last_name: str = Field(..., min_length=3, max_length=50, description="Фамилия")
    date_of_birth: date = Field(..., examples=["01.01.2025"], description="Дата рождения в формате ДД.ММ.ГГГГ")

    @field_validator("date_of_birth", mode="before")
    def parse_date_of_birth(cls, value):
        return datetime.strptime(value, "%d.%m.%Y").date()


class SchemaLogin(BaseModel):
    email: str = Field(..., description="Электронная почта")
    password: str = Field(..., min_length=8, max_length=50, description="Пароль, от 5 до 50 знаков")
