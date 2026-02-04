"""
用户数据模型
包含用户基本信息和密码管理
"""

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class User(Base):
    """
    用户模型
    
    字段：
        id: UUID 主键
        email: 邮箱（唯一）
        password_hash: 密码哈希（bcrypt）
        name: 用户名
        is_active: 账户是否激活
        created_at: 创建时间
        updated_at: 更新时间
    """
    
    __tablename__ = "users"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
        comment="用户邮箱，用于登录"
    )
    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="bcrypt 加密的密码"
    )
    name: Mapped[str] = mapped_column(
        String(100),
        nullable=True,
        comment="用户显示名称"
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        comment="账户是否激活"
    )
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
    
    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email})>"
