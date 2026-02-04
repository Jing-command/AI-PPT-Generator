"""
路由包初始化
注册所有路由
"""

from fastapi import APIRouter

from app.routers import auth, users

# 创建主路由
api_router = APIRouter(prefix="/api/v1")

# 注册子路由
api_router.include_router(auth.router)
api_router.include_router(users.router)

__all__ = ["api_router"]
