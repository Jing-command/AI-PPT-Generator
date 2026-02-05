"""
用户 API Key 模型
存储用户的 AI 提供商 API Key（加密）
"""

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class UserAPIKey(Base):
    """
    用户 API Key 模型
    
    支持多 AI 提供商：OpenAI, Anthropic, Kimi, 阿里云, 腾讯云等
    
    安全说明：
    - api_key_encrypted 字段存储 AES-256 加密后的 Key
    - 只在内存中解密使用，不落盘
    - 不支持查询原始 Key，只支持验证和使用
    """
    
    __tablename__ = "user_api_keys"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="关联用户 ID"
    )
    
    # 提供商信息
    provider: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="AI 提供商: openai, anthropic, kimi, aliyun, tencent, azure"
    )
    
    # 加密的 API Key
    api_key_encrypted: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="AES-256 加密后的 API Key"
    )
    
    # 用户自定义名称（便于管理多个 Key）
    name: Mapped[str] = mapped_column(
        String(100),
        nullable=True,
        comment="Key 别名，如'我的 OpenAI Key'"
    )
    
    # 状态管理
    status: Mapped[str] = mapped_column(
        String(20),
        default="active",
        comment="状态: active, invalid, expired"
    )
    
    # 是否是默认 Key
    is_default: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        comment="是否为默认使用的 Key"
    )
    
    # 最后验证时间
    last_verified_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=True,
        comment="最后一次验证成功时间"
    )
    
    # 时间戳
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        comment="创建时间"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        comment="更新时间"
    )
    
    # 关联关系
    user: Mapped["User"] = relationship("User", back_populates="api_keys")
    
    def __repr__(self) -> str:
        return f"<UserAPIKey(id={self.id}, provider={self.provider}, status={self.status})>"


# 在 User 模型中添加反向关系
# 需要在 app/models/user.py 中添加：
# api_keys: Mapped[List["UserAPIKey"]] = relationship("UserAPIKey", back_populates="user")
