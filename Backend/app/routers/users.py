"""
用户路由
处理用户信息相关接口
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import get_current_user
from app.core.security import verify_password, get_password_hash
from app.database import get_db
from app.models.user import User
from app.schemas.user import (
    UserResponse,
    UserUpdate,
    PasswordUpdate,
    ErrorResponse,
)
from app.services.user_service import get_user_service, EmailExistsError

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


@router.patch(
    "/me",
    response_model=UserResponse,
    summary="更新当前用户信息",
    description="更新用户名或邮箱",
    responses={
        409: {
            "model": ErrorResponse,
            "description": "邮箱已被使用"
        }
    }
)
async def update_me(
    data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> UserResponse:
    """
    更新当前登录用户信息
    
    - 可以更新用户名和邮箱
    - 邮箱必须唯一
    """
    service = get_user_service(db)
    
    # 如果修改邮箱，检查是否已被使用
    if data.email and data.email != current_user.email:
        existing = await service.get_by_email(data.email)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "code": "EMAIL_EXISTS",
                    "message": "该邮箱已被其他用户使用"
                }
            )
    
    # 更新用户信息
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(current_user, field, value)
    
    await db.commit()
    await db.refresh(current_user)
    
    return current_user


@router.post(
    "/me/password",
    status_code=status.HTTP_200_OK,
    summary="修改密码",
    description="修改当前用户密码",
    responses={
        400: {
            "model": ErrorResponse,
            "description": "当前密码错误"
        }
    }
)
async def update_password(
    data: PasswordUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> dict:
    """
    修改当前用户密码
    
    - 需要提供当前密码进行验证
    - 新密码至少8位
    """
    # 验证当前密码
    if not verify_password(data.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "INVALID_PASSWORD",
                "message": "当前密码错误"
            }
        )
    
    # 更新密码
    current_user.hashed_password = get_password_hash(data.new_password)
    await db.commit()
    
    return {
        "message": "密码修改成功",
        "code": "PASSWORD_UPDATED"
    }


@router.delete(
    "/me",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="注销账户",
    description="删除当前用户账户（危险操作）"
)
async def delete_me(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> None:
    """
    注销当前用户账户
    
    ⚠️ 此操作不可恢复，将删除所有相关数据
    """
    await db.delete(current_user)
    await db.commit()
    
    return None
