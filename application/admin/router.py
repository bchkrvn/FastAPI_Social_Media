from fastapi import APIRouter, Depends

from application.admin.depends import get_current_admin
from application.admin.routers.user_routers import user_admin_router

admin_router = APIRouter(
    prefix="/admin",
    tags=["Панель администратора"],
    include_in_schema=False,
    dependencies=[Depends(get_current_admin)],
)

routers = (user_admin_router,)

for r in routers:
    admin_router.include_router(r)
