from datetime import datetime, timedelta, timezone

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from application.db.base_model import Base
from application.post.constants import POST_UPDATE_TIMEOUT


class Post(Base):
    text: Mapped[str]
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    user: Mapped["User"] = relationship(
        "User",
        back_populates="posts",
    )

    def __str__(self):
        return f"Post(id={self.id}, user_id={self.user_id}, text={self.text[:20]}...)"

    def can_update(self):
        limit_time = (self.created + timedelta(seconds=POST_UPDATE_TIMEOUT)).replace(tzinfo=timezone.utc)
        return limit_time > datetime.now(tz=timezone.utc)


from application.user.model import User  # noqa: E402
