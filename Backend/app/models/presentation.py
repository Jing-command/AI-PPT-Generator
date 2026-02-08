"""
PPT 数据模型
存储 PPT 结构、幻灯片内容、AI 生成信息
"""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.core.custom_types import GUID, JSONType
from app.utils.datetime import utcnow_aware

if TYPE_CHECKING:
    from app.models.user import User


class Presentation(Base):
    """
    PPT 演示文稿模型
    
    字段：
        id: UUID 主键
        user_id: 创建者
        title: 标题
        slides: 幻灯片内容（JSONB）
        status: 状态（draft, published, archived）
        ai_prompt: 生成时使用的提示词
        ai_parameters: AI 生成参数
        version: 版本号
    """
    
    __tablename__ = "presentations"
    
    id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        primary_key=True,
        default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # 基本信息
    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        default="未命名演示文稿"
    )
    
    # 幻灯片内容（JSONB 存储完整结构）
    slides: Mapped[list] = mapped_column(
        JSONType(),
        nullable=False,
        default=list,
        comment="幻灯片数组，每个元素包含 type, content, layout, style"
    )
    
    # 状态管理
    status: Mapped[str] = mapped_column(
        String(20),
        default="draft",
        comment="状态: draft, published, archived"
    )
    
    # AI 生成信息
    ai_prompt: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="生成时使用的提示词"
    )
    ai_parameters: Mapped[Optional[dict]] = mapped_column(
        JSONType(),
        nullable=True,
        comment="AI 生成参数：model, temperature, max_tokens 等"
    )
    
    # 版本控制
    version: Mapped[int] = mapped_column(
        Integer,
        default=1,
        comment="版本号，每次编辑递增"
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
    
    # 关联关系
    user: Mapped["User"] = relationship("User", back_populates="presentations")
    generation_tasks: Mapped[List["GenerationTask"]] = relationship(
        "GenerationTask",
        back_populates="presentation",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self) -> str:
        return f"<Presentation(id={self.id}, title={self.title})>"


class GenerationTask(Base):
    """
    PPT 生成任务模型
    
    用于异步跟踪 AI 生成任务的状态
    """
    
    __tablename__ = "generation_tasks"
    
    id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        primary_key=True,
        default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    ppt_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        GUID(),
        ForeignKey("presentations.id", ondelete="SET NULL"),
        nullable=True
    )
    
    # 任务状态
    status: Mapped[str] = mapped_column(
        String(20),
        default="pending",
        comment="状态: pending, processing, completed, failed, cancelled"
    )
    progress: Mapped[int] = mapped_column(
        Integer,
        default=0,
        comment="进度百分比 0-100"
    )
    
    # AI 配置
    provider: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="使用的 AI 提供商"
    )
    prompt: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="生成提示词"
    )
    parameters: Mapped[Optional[dict]] = mapped_column(
        JSONType(),
        nullable=True,
        comment="生成参数"
    )
    
    # 结果
    result: Mapped[Optional[dict]] = mapped_column(
        JSONType(),
        nullable=True,
        comment="生成结果：包含 ppt_id 和 slides"
    )
    error_message: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="错误信息（如果失败）"
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
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    
    # 关联关系
    user: Mapped["User"] = relationship("User", back_populates="generation_tasks")
    presentation: Mapped[Optional["Presentation"]] = relationship(
        "Presentation",
        back_populates="generation_tasks"
    )
    
    def __repr__(self) -> str:
        return f"<GenerationTask(id={self.id}, status={self.status}, progress={self.progress}%)>"
