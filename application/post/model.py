from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from application.db.base_model import Base


class Post(Base):
    text: Mapped[str]
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    user: Mapped["User"] = relationship(
        "User",
        back_populates="posts",
    )

    def __str__(self):
        return f"Post(id={self.id}, user_id={self.user_id}, text={self.text[:20]}...)"


from application.user.model import User  # noqa: E402
