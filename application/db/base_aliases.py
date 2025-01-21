from datetime import datetime
from typing import Annotated

from sqlalchemy import func, text
from sqlalchemy.orm import mapped_column

int_pk = Annotated[int, mapped_column(primary_key=True)]
created = Annotated[datetime, mapped_column(server_default=func.now())]
updated = Annotated[datetime, mapped_column(server_default=func.now(), onupdate=datetime.now)]
str_uniq = Annotated[str, mapped_column(unique=True, nullable=False)]
str_null_true = Annotated[str, mapped_column(nullable=True)]
bool_true = Annotated[bool, mapped_column(default=True, server_default=text("true"), nullable=False)]
bool_false = Annotated[bool, mapped_column(default=False, server_default=text("false"), nullable=False)]
