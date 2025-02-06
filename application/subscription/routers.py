from fastapi import APIRouter, Depends

from application.auth.depends import get_current_user
from application.base.exceptions import BaseAppException, get_404_http_exception, get_409_http_exception
from application.subscription.dao import SubscriptionDAO
from application.subscription.messages import (
    BLOGGER_NOT_FOUND_ERROR,
    SUBSCRIBE_FOR_YOURSELF_ERROR,
    SUBSCRIPTION_NOT_FOUND,
    SUCCESS_SUBSCRIBE,
    SUCCESS_UNSUBSCRIBE,
)
from application.subscription.schemas import SubscribeCreateSchema
from application.user.dao import UserDAO
from application.user.model import User

subscription_router = APIRouter(
    prefix="/subscriptions",
    tags=["Подписки"],
)


@subscription_router.post("/")
async def create_subscription(subscription_data: SubscribeCreateSchema, current_user: User = Depends(get_current_user)):
    data = subscription_data.model_dump()
    filters = dict(
        id=data["blogger_id"],
        is_active=True,
    )
    blogger = await UserDAO.find_one_or_none(filters=filters)
    if not blogger:
        raise get_404_http_exception(BLOGGER_NOT_FOUND_ERROR)

    if blogger.id == current_user.id:
        raise get_409_http_exception(SUBSCRIBE_FOR_YOURSELF_ERROR)

    data["follower_id"] = current_user.id

    try:
        await SubscriptionDAO.add(**data)
    except BaseAppException as ex:
        raise get_409_http_exception(ex.msg)

    return {"message": SUCCESS_SUBSCRIBE}


@subscription_router.delete("/{subscription_id:int}")
async def delete_subscription(subscription_id: int, current_user: User = Depends(get_current_user)):
    filters = dict(
        id=subscription_id,
        follower_id=current_user.id,
    )
    subscription = await SubscriptionDAO.find_one_or_none(filters=filters)
    if not subscription:
        raise get_404_http_exception(SUBSCRIPTION_NOT_FOUND)

    await SubscriptionDAO.delete(subscription)
    return {"message": SUCCESS_UNSUBSCRIBE}
