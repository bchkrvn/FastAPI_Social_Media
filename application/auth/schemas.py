from datetime import date, datetime

from pydantic import BaseModel, Field, field_validator
from pydantic_core.core_schema import FieldValidationInfo

from application.config import settings
from application.user.password import PasswordValidator


class SchemaPassword(BaseModel):
    password: str = Field(
        ...,
        min_length=settings.PASSWORD_LENGTH,
        max_length=50,
        description=f"Пароль, от {settings.PASSWORD_LENGTH} до 50 знаков",
    )
    password2: str = Field(..., description="Подтвердите пароль")

    @field_validator("password")
    def validate_password(cls, password):
        errors = PasswordValidator(password).validate_password()
        if errors:
            msg = "Пароль должен соответствовать следующим требованиям:\n" + "\n".join(errors)
            raise ValueError(msg)

        return password

    @field_validator("password2")
    def validate_password2(cls, password2, info: FieldValidationInfo):
        if "password" in info.data and password2 != info.data["password"]:
            msg = "Пароли не совпадают"
            raise ValueError(msg)

        return password2


class SchemaRegister(SchemaPassword):
    email: str = Field(..., description="Электронная почта")
    first_name: str = Field(..., min_length=3, max_length=50, description="Имя")
    last_name: str = Field(..., min_length=3, max_length=50, description="Фамилия")
    date_of_birth: date = Field(..., examples=["01.01.2025"], description="Дата рождения в формате ДД.ММ.ГГГГ")

    @field_validator("date_of_birth", mode="before")
    def parse_date_of_birth(cls, value):
        return datetime.strptime(value, "%d.%m.%Y").date()


class SchemaLogin(BaseModel):
    email: str = Field(..., description="Электронная почта")
    password: str = Field(..., min_length=8, max_length=50, description="Пароль, от 5 до 50 знаков")
