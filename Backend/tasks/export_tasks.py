"""
导出任务
处理 PPT 导出的异步任务
"""

import asyncio
from datetime import datetime
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.config import settings
from app.models.export_task import ExportTask
from app.models.presentation import Presentation
from app.services.export_service import ExportService
from app.tasks import celery_app

# 创建同步数据库引擎用于 Celery
database_url_sync = settings.DATABASE_URL.replace("+asyncpg", "")
engine = create_async_engine(settings.DATABASE_URL, future=True)


@celery_app.task(bind=True, max_retries=3)
def process_export_task(self, task_id: str):
    """
    处理导出任务
    
    Args:
        task_id: 导出任务 ID
    """
    # 在异步上下文中运行
    return asyncio.run(_process_export_async(self, task_id))


async def _process_export_async(task_self, task_id: str):
    """异步处理导出"""
    from app.database import AsyncSessionLocal
    
    async with AsyncSessionLocal() as db:
        try:
            # 获取任务
            result = await db.execute(
                select(ExportTask).where(ExportTask.id == task_id)
            )
            task = result.scalar_one_or_none()
            
            if not task:
                print(f"[Export] 任务 {task_id} 不存在")
                return
            
            if task.status == "cancelled":
                print(f"[Export] 任务 {task_id} 已取消")
                return
            
            # 更新状态为处理中
            task.status = "processing"
            await db.commit()
            
            # 获取 PPT
            ppt_result = await db.execute(
                select(Presentation).where(Presentation.id == task.ppt_id)
            )
            presentation = ppt_result.scalar_one_or_none()
            
            if not presentation:
                task.status = "failed"
                task.error_message = "PPT 不存在"
                await db.commit()
                return
            
            # 执行导出
            export_service = ExportService()
            
            if task.format == "pptx":
                file_path = await export_service.export_pptx(presentation)
            elif task.format == "pdf":
                file_path = await export_service.export_pdf(presentation)
            elif task.format in ["png", "jpg"]:
                file_paths = await export_service.export_images(
                    presentation, format=task.format
                )
                file_path = file_paths[0] if file_paths else None
            else:
                raise ValueError(f"不支持的格式: {task.format}")
            
            # 更新任务状态
            task.status = "completed"
            task.file_path = file_path
            if file_path:
                task.file_size = Path(file_path).stat().st_size
            task.completed_at = datetime.utcnow()
            
            print(f"[Export] 任务 {task_id} 完成: {file_path}")
            
        except Exception as exc:
            print(f"[Export] 任务 {task_id} 失败: {exc}")
            
            # 更新失败状态
            try:
                result = await db.execute(
                    select(ExportTask).where(ExportTask.id == task_id)
                )
                task = result.scalar_one_or_none()
                if task:
                    task.status = "failed"
                    task.error_message = str(exc)
                    await db.commit()
            except Exception as e:
                print(f"[Export] 更新失败状态出错: {e}")
            
            # 重试
            raise task_self.retry(exc=exc, countdown=60)
        
        finally:
            await db.commit()


@celery_app.task
def cleanup_old_exports(max_age_hours: int = 24):
    """
    清理过期导出文件
    
    Args:
        max_age_hours: 文件最大保留时间（小时）
    """
    return asyncio.run(_cleanup_old_exports_async(max_age_hours))


async def _cleanup_old_exports_async(max_age_hours: int):
    """异步清理过期文件"""
    from app.database import AsyncSessionLocal
    
    async with AsyncSessionLocal() as db:
        from datetime import timedelta
        
        cutoff_time = datetime.utcnow() - timedelta(hours=max_age_hours)
        
        # 查找过期任务
        result = await db.execute(
            select(ExportTask).where(
                ExportTask.status == "completed",
                ExportTask.completed_at < cutoff_time,
                ExportTask.file_path.isnot(None)
            )
        )
        
        expired_tasks = result.scalars().all()
        
        deleted_count = 0
        for task in expired_tasks:
            try:
                # 删除文件
                if task.file_path and Path(task.file_path).exists():
                    Path(task.file_path).unlink()
                    deleted_count += 1
                
                # 清除文件路径
                task.file_path = None
                task.file_size = None
                
            except Exception as e:
                print(f"[Cleanup] 删除文件失败 {task.file_path}: {e}")
        
        await db.commit()
        print(f"[Cleanup] 清理完成，删除 {deleted_count} 个文件")
        
        return deleted_count
