"""
导出任务服务
"""

from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.export_task import ExportTask
from app.models.presentation import Presentation
from app.services.export_service import get_export_service


class ExportTaskService:
    """
    导出任务服务
    
    管理导出任务的创建和状态跟踪
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_task(
        self,
        user_id: UUID,
        ppt_id: UUID,
        format: str,
        quality: str = "standard"
    ) -> ExportTask:
        """
        创建导出任务
        
        Args:
            user_id: 用户 ID
            ppt_id: PPT ID
            format: 导出格式
            quality: 质量
            
        Returns:
            创建的任务
        """
        task = ExportTask(
            user_id=user_id,
            ppt_id=ppt_id,
            format=format,
            quality=quality,
            status="pending"
        )
        
        self.db.add(task)
        await self.db.commit()
        await self.db.refresh(task)
        
        return task
    
    async def get_task(
        self,
        task_id: UUID,
        user_id: UUID
    ) -> Optional[ExportTask]:
        """
        获取任务
        
        Args:
            task_id: 任务 ID
            user_id: 用户 ID
            
        Returns:
            任务对象或 None
        """
        result = await self.db.execute(
            select(ExportTask).where(
                ExportTask.id == task_id,
                ExportTask.user_id == user_id
            )
        )
        return result.scalar_one_or_none()
    
    async def process_task(
        self,
        task: ExportTask,
        presentation: Presentation
    ) -> None:
        """
        处理导出任务
        
        Args:
            task: 导出任务
            presentation: PPT 数据
        """
        export_service = get_export_service()
        
        try:
            task.status = "processing"
            await self.db.commit()
            
            # 执行导出
            if task.format == "pptx":
                file_path = await export_service.export_pptx(presentation)
            elif task.format == "pdf":
                file_path = await export_service.export_pdf(presentation)
            elif task.format in ["png", "jpg"]:
                file_paths = await export_service.export_images(
                    presentation,
                    format=task.format
                )
                file_path = file_paths[0] if file_paths else None
            else:
                raise ValueError(f"不支持的格式: {task.format}")
            
            # 更新任务状态
            task.status = "completed"
            task.file_path = file_path
            task.file_size = Path(file_path).stat().st_size if file_path else 0
            task.completed_at = datetime.utcnow()
            task.expires_at = datetime.utcnow() + timedelta(days=1)
            
        except Exception as e:
            task.status = "failed"
            task.error_message = str(e)
        
        await self.db.commit()


from pathlib import Path


def get_export_task_service(db: AsyncSession) -> ExportTaskService:
    """获取导出任务服务实例"""
    return ExportTaskService(db)
