from datetime import date

from sqlalchemy.orm import Mapped, relationship

from application.db.base_aliases import bool_false, bool_true, str_uniq
from application.db.base_model import Base


class User(Base):
    first_name: Mapped[str]
    last_name: Mapped[str]
    email: Mapped[str_uniq]
    date_of_birth: Mapped[date]
    is_active: Mapped[bool_true]
    password: Mapped[str]
    is_admin: Mapped[bool_false]

    posts: Mapped[list["Post"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )

    def __str__(self):
        return f"User(id={self.id}, first_name={self.first_name}, last_name={self.last_name})"

    def __repr__(self):
        return str(self)


from application.post.model import Post  # noqa: E402
