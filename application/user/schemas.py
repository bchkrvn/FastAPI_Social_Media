from datetime import date, datetime

from pydantic import BaseModel, Field, field_validator

from application.auth.schemas import SchemaPassword


class SchemaMeGet(BaseModel):
    id: int = Field(..., description="Идентификатор")
    email: str = Field(..., description="Электронная почта")
    first_name: str = Field(..., description="Имя")
    last_name: str = Field(..., description="Фамилия")
    date_of_birth: date = Field(..., examples=["01.01.2025"], description="Дата рождения")
    is_active: bool = Field(..., description="Активен")
    created: datetime = Field(..., description="Создан")
    updated: datetime = Field(..., description="Обновлен")


class SchemaMeGetWithSubscriptions(SchemaMeGet):
    followers_count: int = Field(..., description="Количество подписчиков")
    subscriptions_count: int = Field(..., description="Количество подписок")


class SchemaMePut(BaseModel):
    email: str = Field(..., description="Электронная почта")
    first_name: str = Field(..., min_length=3, examples=["Иван"], max_length=50, description="Имя")
    last_name: str = Field(..., min_length=3, max_length=50, examples=["Иванов"], description="Фамилия")
    date_of_birth: str = Field(..., examples=["01.01.2025"], description="Дата рождения в формате ДД.ММ.ГГГГ")

    @field_validator("date_of_birth", mode="after")
    def parse_date_of_birth(cls, value):
        return datetime.strptime(value, "%d.%m.%Y").date()


class SchemaChangePassword(SchemaPassword):
    old_password: str = Field(..., description="Старый пароль")
