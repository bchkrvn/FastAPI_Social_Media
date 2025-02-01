from datetime import datetime
from getpass import getpass

import regex as re

from application.user.dao import UsersDAO
from application.user.password import get_password_hash


class AdminCreator:
    name_pattern = r"^([А-ЯЁа-яё\-]{1,23}|)$"
    email_pattern = r"^[\w-\.]+@([\w-]+\.)+[\w-]{2,4}$"
    first_name_limit = 25
    last_name_limit = 25
    password_length = 8
    password_symbols = "@#$%^&+="
    password_symbols_pattern = rf"[{password_symbols}]+"

    def __init__(self):
        self.__data = {
            "is_admin": True,
            "is_active": True,
        }

    async def create(self) -> None:
        print("Для создание администратора введите необходимые данные:")

        self._get_first_name()
        self._get_last_name()
        await self._get_email()
        self._get_birthday()
        self._get_password()
        await self._create_admin()

        print("\nПользователь создан!")

    def _get_first_name(self):
        while True:
            first_name = input("Введите имя: ")
            if len(first_name) > self.first_name_limit:
                print(f"Имя должно содержать не более {self.first_name_limit} символов\n")
                continue

            is_correct = bool(re.fullmatch(self.name_pattern, first_name))
            if not is_correct:
                print("Имя должно содержать русские буквы, быть без пробелов, может содержать дефис\n")
                continue

            self.__data["first_name"] = first_name
            break

    def _get_last_name(self):
        while True:
            last_name = input("Введите фамилию: ")
            if len(last_name) > self.last_name_limit:
                print(f"Фамилия должна содержать не более {self.last_name_limit} символов\n")
                continue

            is_correct = bool(re.fullmatch(self.name_pattern, last_name))
            if not is_correct:
                print("Фамилию должна содержать русские буквы, быть без пробелов, может содержать дефис\n")
                continue

            self.__data["last_name"] = last_name
            break

    async def _get_email(self):
        while True:
            email = input("Введите адрес электронной почты: ")

            is_correct = bool(re.fullmatch(self.email_pattern, email))
            if not is_correct:
                print("\nНеверный формат электронной почты\n")
                continue

            is_unique = not await UsersDAO.find_one_or_none(filters={"email": email})
            if not is_unique:
                print("\nПользователь с данной почтой уже существует\n")
                continue

            self.__data["email"] = email
            break

    def _get_birthday(self):
        while True:
            value = input("Введите дату рождения в формате ДД.ММ.ГГГГ: ")
            try:
                date = datetime.strptime(value, "%d.%m.%Y").date()
            except ValueError:
                print("\nНеверный формат даты. Дата должна быть в формате ДД.ММ.ГГГГ\n")
                continue

            self.__data["date_of_birth"] = date
            break

    def _get_password(self):
        while True:
            password = getpass("Введите пароль: ")
            is_correct = self.__check_password(password)
            if not is_correct:
                continue

            password2 = getpass("Подтвердите пароль: ")
            if password != password2:
                print("\nПароли не совпадают\n")
                continue

            self.__data["password"] = get_password_hash(password)
            break

    def __check_password(self, password: str) -> bool:
        errors = []
        if len(password) < self.password_length:
            msg = f"- Пароль должен содержать как минимум {self.password_length} символов"
            errors.append(msg)

        if not re.search(r"[A-ZА-ЯЁ]+", password):
            msg = "- Пароль должен содержать как минимум одну заглавную букву"
            errors.append(msg)

        if not re.search(r"[a-zа-яё]+", password):
            msg = "- Пароль должен содержать как минимум одну строчную букву"
            errors.append(msg)

        if not re.search(r"[0-9]+", password):
            msg = "- Пароль должен содержать как минимум одну цифру"
            errors.append(msg)

        if not re.search(self.password_symbols_pattern, password):
            msg = f"- Пароль должен содержать как минимум один из символов {self.password_symbols}"
            errors.append(msg)

        if errors:
            print("\nПароль не соответствует следующим требованиям:\n")
            print("\n".join(errors))
            print()
            return False

        return True

    async def _create_admin(self):
        await UsersDAO.add(**self.__data)
