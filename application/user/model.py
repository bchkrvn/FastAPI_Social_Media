from datetime import date

from sqlalchemy.orm import Mapped

from application.db.base_aliases import str_uniq
from application.db.base_model import Base


class User(Base):
    first_name: Mapped[str]
    last_name: Mapped[str]
    email: Mapped[str_uniq]
    date_of_birth: Mapped[date]

    def __str__(self):
        return f"Пользователь {self.id}. {self.first_name} {self.last_name}"

    def __repr__(self):
        return str(self)
