import regex as re
from passlib.context import CryptContext

from application.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password, hashed_password) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


class PasswordValidator:
    password_length = settings.PASSWORD_LENGTH
    password_symbols = "@#$%^&+=-"

    short_password_msg = f"- Пароль должен содержать как минимум {password_length} символов"
    upper_letter_msg = "- Пароль должен содержать как минимум одну заглавную букву"
    lower_letter_msg = "- Пароль должен содержать как минимум одну строчную букву"
    digit_msg = "- Пароль должен содержать как минимум одну цифру"
    symbol_msg = f"- Пароль должен содержать как минимум один из символов {password_symbols}"

    upper_letter_pattern = r"[A-ZА-ЯЁ]+"
    lower_letter_pattern = r"[a-zа-яё]+"
    digit_pattern = r"[0-9]+"
    symbols_pattern = rf"[{password_symbols}]+"

    def __init__(self, password: str):
        self._errors = []
        self._password = password

    def validate_password(self) -> list:
        self._check_length()
        self._check_upper_letter()
        self._check_lower_letter()
        self._check_digit()
        self._check_symbol()
        return self._errors

    def _check_length(self) -> None:
        if len(self._password) < self.password_length:
            self._errors.append(self.short_password_msg)

    def _check_upper_letter(self) -> None:
        if not re.search(self.upper_letter_pattern, self._password):
            self._errors.append(self.upper_letter_msg)

    def _check_lower_letter(self) -> None:
        if not re.search(self.lower_letter_pattern, self._password):
            self._errors.append(self.lower_letter_msg)

    def _check_digit(self) -> None:
        if not re.search(self.digit_pattern, self._password):
            self._errors.append(self.digit_msg)

    def _check_symbol(self) -> None:
        if not re.search(self.symbols_pattern, self._password):
            self._errors.append(self.symbol_msg)
