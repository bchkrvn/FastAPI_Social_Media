from sqlalchemy import CheckConstraint, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from application.db.base_model import Base


class Subscription(Base):
    follower_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    follower: Mapped["User"] = relationship(
        back_populates="subscriptions",
        foreign_keys="Subscription.follower_id",
    )

    blogger_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    blogger: Mapped["User"] = relationship(
        back_populates="subscribers",
        foreign_keys="Subscription.blogger_id",
    )

    __table_args__ = (
        UniqueConstraint("blogger_id", "follower_id", name="unique_subscribe"),
        CheckConstraint("follower_id != blogger_id", name="check_subscription_for_yourself"),
    )

    def __str__(self):
        return f"Subscription(id={self.id}, blogger_id={self.blogger_id}, follower_id={self.follower_id})"


from application.user.model import User  # noqa: E402
