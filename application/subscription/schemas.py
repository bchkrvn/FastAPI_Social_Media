from pydantic import BaseModel, Field


class SubscriptionCreateSchema(BaseModel):
    user_id: int = Field(..., description="id пользователя")


class UserForSubscriptionSchema(BaseModel):
    id: int = Field(..., description="Идентификатор")
    first_name: str = Field(..., description="Имя")
    last_name: str = Field(..., description="Фамилия")


class SubscriptionSchema(BaseModel):
    id: int = Field(..., description="Идентификатор")
    user: UserForSubscriptionSchema = Field(..., validation_alias="blogger")


class FollowersSchema(BaseModel):
    id: int = Field(..., description="Идентификатор")
    user: UserForSubscriptionSchema = Field(..., validation_alias="follower")
