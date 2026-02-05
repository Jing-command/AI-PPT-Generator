"""
用户路由
处理用户信息相关接口
"""

from fastapi import APIRouter, Depends

from app.core import get_current_user
from app.models.user import User
from app.schemas.user import UserResponse

router = APIRouter(prefix="/users", tags=["用户"])


@router.get(
    "/me",
    response_model=UserResponse,
    summary="获取当前用户信息",
    description="获取当前登录用户的详细信息"
)
async def get_me(
    current_user: User = Depends(get_current_user)
) -> UserResponse:
    """获取当前登录用户信息"""
    return current_user
