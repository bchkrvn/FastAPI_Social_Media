from pydantic import BaseModel, Field


class SubscribeCreateSchema(BaseModel):
    blogger_id: int = Field(..., description="id пользователя")
