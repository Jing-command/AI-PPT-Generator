"""
模板模型
预定义的 PPT 模板
"""

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.utils.datetime import utcnow_aware
from app.core.custom_types import GUID, JSONType


class Template(Base):
    """
    PPT 模板模型
    
    预定义的幻灯片模板，包含布局、样式和内容结构
    """
    
    __tablename__ = "templates"
    
    id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        primary_key=True,
        default=uuid.uuid4
    )
    
    # 基本信息
    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="模板名称"
    )
    description: Mapped[str] = mapped_column(
        Text,
        nullable=True,
        comment="模板描述"
    )
    category: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="general",
        comment="分类: business, education, creative, minimal, general"
    )
    
    # 模板内容
    content: Mapped[dict] = mapped_column(
        JSONType(),
        nullable=False,
        comment="模板结构：包含 slides, layouts, styles, theme"
    )
    
    # 预览图
    thumbnail_url: Mapped[str] = mapped_column(
        String(500),
        nullable=True,
        comment="缩略图 URL"
    )
    
    # 使用统计
    usage_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        comment="使用次数"
    )
    
    # 付费/免费
    is_premium: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        comment="是否为付费模板"
    )
    
    # 是否系统模板
    is_system: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        comment="是否为系统预设模板"
    )
    
    # 时间戳
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utcnow_aware
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utcnow_aware,
        onupdate=utcnow_aware
    )
    
    def __repr__(self) -> str:
        return f"<Template(id={self.id}, name={self.name}, category={self.category})>"
