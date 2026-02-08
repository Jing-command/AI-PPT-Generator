"""
认证路由
处理用户注册、登录、Token 刷新等
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token, create_refresh_token
from app.database import get_db
from app.schemas.user import (
    ErrorResponse,
    LoginRequest,
    RefreshTokenRequest,
    Token,
    UserCreate,
    UserResponse,
)
from app.services.user_service import EmailExistsError, PasswordHashError, get_user_service

router = APIRouter(prefix="/auth", tags=["认证"])
security = HTTPBearer()


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="用户注册",
    description="使用邮箱和密码注册新账户",
    responses={
        409: {
            "model": ErrorResponse,
            "description": "邮箱已被注册"
        },
        422: {
            "model": ErrorResponse,
            "description": "参数验证失败"
        }
    }
)
async def register(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
) -> UserResponse:
    """
    用户注册
    
    - 邮箱必须唯一
    - 密码至少8位
    """
    service = get_user_service(db)
    
    try:
        user = await service.create(user_data)
        return user
    except EmailExistsError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "code": "EMAIL_EXISTS",
                "message": str(e)
            }
        )
    except PasswordHashError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "code": "INVALID_PASSWORD",
                "message": str(e)
            }
        )


@router.post(
    "/login",
    response_model=Token,
    summary="用户登录",
    description="使用邮箱和密码登录，获取访问令牌",
    responses={
        401: {
            "model": ErrorResponse,
            "description": "邮箱或密码错误"
        }
    }
)
async def login(
    login_data: LoginRequest,
    db: AsyncSession = Depends(get_db)
) -> Token:
    """
    用户登录
    
    - 验证邮箱和密码
    - 返回访问令牌和刷新令牌
    """
    service = get_user_service(db)
    user = await service.authenticate(
        login_data.email,
        login_data.password
    )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "code": "INVALID_CREDENTIALS",
                "message": "邮箱或密码错误"
            },
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # 创建 Token
    access_token = create_access_token(str(user.id))
    refresh_token = create_refresh_token(str(user.id))
    
    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=1800  # 30分钟
    )


@router.post(
    "/refresh",
    response_model=Token,
    summary="刷新 Token",
    description="使用刷新令牌获取新的访问令牌",
    responses={
        401: {
            "model": ErrorResponse,
            "description": "刷新令牌无效或过期"
        }
    }
)
async def refresh_token(
    refresh_data: RefreshTokenRequest
) -> Token:
    """
    刷新访问令牌
    
    - 使用刷新令牌换取新的访问令牌
    - 刷新令牌本身不变
    """
    from app.core.security import decode_token
    
    user_id, error = decode_token(refresh_data.refresh_token, expected_type="refresh")
    
    if error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "code": "INVALID_REFRESH_TOKEN",
                "message": "刷新令牌无效或已过期"
            },
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # 创建新的访问令牌
    access_token = create_access_token(user_id)
    
    return Token(
        access_token=access_token,
        refresh_token=refresh_data.refresh_token,  # 刷新令牌不变
        token_type="bearer",
        expires_in=1800
    )
