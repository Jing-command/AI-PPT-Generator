"""
操作历史模型
记录用户的所有操作，支持撤销/重做
"""

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.utils.datetime import utcnow_aware
from app.core.custom_types import GUID, JSONType


class OperationHistory(Base):
    """
    操作历史记录
    
    用于实现撤销/重做功能
    每个操作记录操作前状态（before）和操作后状态（after）
    """
    
    __tablename__ = "operation_history"
    
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
    ppt_id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        ForeignKey("presentations.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # 操作信息
    operation_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="操作类型: generate, edit_slide, add_slide, delete_slide, move_slide, update_ppt"
    )
    slide_id: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="如果是单页操作，记录页 ID"
    )
    
    # 状态快照
    before_state: Mapped[Optional[dict]] = mapped_column(
        JSONType(),
        nullable=True,
        comment="操作前的状态"
    )
    after_state: Mapped[Optional[dict]] = mapped_column(
        JSONType(),
        nullable=True,
        comment="操作后的状态"
    )
    
    # 操作描述
    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="用户可读的操作描述"
    )
    
    # 撤销/重做标记
    is_undone: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        comment="是否已被撤销"
    )
    undone_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    
    # 时间戳
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utcnow_aware
    )
    
    def __repr__(self) -> str:
        return f"<OperationHistory(id={self.id}, type={self.operation_type}, ppt_id={self.ppt_id})>"
