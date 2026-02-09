"""
Pydantic 数据验证模型
用于请求/响应数据验证和序列化
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


# ==================== 用户相关 ====================

class UserBase(BaseModel):
    """用户基础模型"""
    email: EmailStr = Field(..., description="用户邮箱")
    name: Optional[str] = Field(None, max_length=100, description="用户名")
    
    model_config = ConfigDict(from_attributes=True)


class UserCreate(UserBase):
    """用户注册请求模型"""
    password: str = Field(
        ...,
        min_length=8,
        max_length=100,
        description="密码，至少8位"
    )

    @field_validator("password")
    @classmethod
    def validate_password_length(cls, value: str) -> str:
        password_bytes = value.encode("utf-8")
        if len(password_bytes) > 72:
            raise ValueError("密码不能超过 72 个字节（bcrypt 限制）")
        if len(value) < 8:
            raise ValueError("密码至少需要 8 个字符")
        return value
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "user@example.com",
                "password": "securepassword123",
                "name": "张三"
            }
        }
    )


class UserResponse(UserBase):
    """用户响应模型（不包含密码）"""
    id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class UserUpdate(BaseModel):
    """用户更新请求模型"""
    name: Optional[str] = Field(None, max_length=100, description="用户名")
    email: Optional[EmailStr] = Field(None, description="用户邮箱")
    
    model_config = ConfigDict(from_attributes=True)


class PasswordUpdate(BaseModel):
    """密码更新请求模型"""
    current_password: str = Field(..., description="当前密码")
    new_password: str = Field(
        ...,
        min_length=8,
        max_length=100,
        description="新密码，至少8位"
    )

    @field_validator("new_password")
    @classmethod
    def validate_password_length(cls, value: str) -> str:
        if len(value.encode("utf-8")) > 72:
            raise ValueError("密码不能超过 72 个字节")
        return value
    
    model_config = ConfigDict(from_attributes=True)


# ==================== 认证相关 ====================

class Token(BaseModel):
    """Token 响应模型"""
    access_token: str = Field(..., description="访问令牌")
    refresh_token: str = Field(..., description="刷新令牌")
    token_type: str = Field(default="bearer", description="令牌类型")
    expires_in: int = Field(..., description="过期时间（秒）")


class LoginRequest(BaseModel):
    """登录请求模型"""
    email: EmailStr = Field(..., description="用户邮箱")
    password: str = Field(..., description="密码")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "user@example.com",
                "password": "securepassword123"
            }
        }
    )


class RefreshTokenRequest(BaseModel):
    """刷新 Token 请求"""
    refresh_token: str = Field(..., description="刷新令牌")


# ==================== 错误响应 ====================

class ErrorResponse(BaseModel):
    """标准错误响应"""
    code: str = Field(..., description="错误代码")
    message: str = Field(..., description="错误信息")
    details: Optional[dict] = Field(None, description="详细错误信息")
