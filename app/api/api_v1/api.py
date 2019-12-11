from fastapi import APIRouter

from app.api.api_v1.endpoints import health, login
from app.users.router import router as user_router

api_router = APIRouter()
api_router.include_router(login.router, tags=["login"])
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(user_router, prefix="/users", tags=["users"])

