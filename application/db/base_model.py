from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, declared_attr

from .base_aliases import created, int_pk, updated


class Base(AsyncAttrs, DeclarativeBase):
    __abstract__ = True

    id: Mapped[int_pk]
    created: Mapped[created]
    updated: Mapped[updated]

    @declared_attr.directive
    def __tablename__(cls) -> str:
        return f"{cls.__name__.lower()}s"

    @property
    def all_fields(self) -> set:
        fields = set(self.__dict__)
        fields.remove("_sa_instance_state")
        return fields
