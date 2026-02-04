"""
依赖注入模块
FastAPI Depends 使用的依赖函数
"""

from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import decode_token
from app.database import get_db
from app.models.user import User
from app.schemas.user import ErrorResponse

# HTTP Bearer 认证
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    获取当前登录用户
    
    用法：
        @app.get("/me")
        async def get_me(current_user: User = Depends(get_current_user)):
            return current_user
    
    Args:
        credentials: HTTP Bearer Token
        db: 数据库会话
        
    Returns:
        User 模型实例
        
    Raises:
        HTTPException: 401 如果 Token 无效或用户不存在
    """
    token = credentials.credentials
    user_id, error = decode_token(token)
    
    if error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "code": "INVALID_TOKEN",
                "message": "无效的认证令牌",
                "details": {"error": error}
            },
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # 查询用户
    from sqlalchemy import select
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "code": "USER_NOT_FOUND",
                "message": "用户不存在"
            },
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "USER_INACTIVE",
                "message": "用户账户已被禁用"
            }
        )
    
    return user


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(
        lambda: security
    ),
    db: AsyncSession = Depends(get_db)
) -> Optional[User]:
    """
    可选地获取当前用户
    
    用于某些接口既支持认证用户，也支持匿名访问
    
    Returns:
        User 或 None
    """
    if not credentials:
        return None
    
    try:
        return await get_current_user(credentials, db)
    except HTTPException:
        return None
