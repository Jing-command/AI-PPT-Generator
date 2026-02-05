"""
导出任务模型
"""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class ExportTask(Base):
    """
    导出任务模型
    
    用于异步跟踪导出任务
    """
    
    __tablename__ = "export_tasks"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    ppt_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("presentations.id", ondelete="CASCADE"),
        nullable=False
    )
    
    # 导出配置
    format: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        comment="格式: pptx, pdf, png, jpg"
    )
    quality: Mapped[str] = mapped_column(
        String(20),
        default="standard",
        comment="质量: standard, high"
    )
    
    # 任务状态
    status: Mapped[str] = mapped_column(
        String(20),
        default="pending",
        comment="状态: pending, processing, completed, failed"
    )
    
    # 结果
    file_path: Mapped[str] = mapped_column(
        String(500),
        nullable=True,
        comment="导出文件路径"
    )
    file_size: Mapped[int] = mapped_column(
        Integer,
        nullable=True,
        comment="文件大小（字节）"
    )
    error_message: Mapped[str] = mapped_column(
        String(500),
        nullable=True
    )
    
    # 过期时间
    expires_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=True,
        comment="下载链接过期时间"
    )
    
    # 时间戳
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )
    completed_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=True
    )
    
    def __repr__(self) -> str:
        return f"<ExportTask(id={self.id}, format={self.format}, status={self.status})>"
