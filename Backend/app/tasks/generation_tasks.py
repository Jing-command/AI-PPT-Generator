"""
PPT 生成任务
处理 AI 生成 PPT 的异步任务
"""

import asyncio
import uuid
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.presentation import GenerationTask, Presentation
from app.services.ai_provider import AIProviderFactory
from app.services.api_key_service import APIKeyService
from app.tasks import celery_app
from app.utils.datetime import utcnow_aware


@celery_app.task(bind=True, max_retries=3)
def process_generation_task(self, task_id: str):
    """
    处理 PPT 生成任务
    
    Args:
        task_id: 生成任务 ID
    """
    return asyncio.run(_process_generation_async(self, task_id))


async def _process_generation_async(task_self, task_id: str):
    """异步处理生成任务"""
    from app.database import AsyncSessionLocal
    
    async with AsyncSessionLocal() as db:
        try:
            # 获取任务
            result = await db.execute(
                select(GenerationTask).where(GenerationTask.id == task_id)
            )
            task = result.scalar_one_or_none()
            
            if not task:
                print(f"[Generation] 任务 {task_id} 不存在")
                return
            
            if task.status == "cancelled":
                print(f"[Generation] 任务 {task_id} 已取消")
                return
            
            # 更新状态为处理中
            task.status = "processing"
            task.progress = 10
            await db.commit()
            
            # 获取 API Key
            api_key_service = APIKeyService(db)
            key = await api_key_service.get_default_key(task.user_id, task.provider)
            
            if not key:
                raise ValueError(f"未找到有效的 {task.provider} API Key")
            
            # 解密 API Key
            from app.services.encryption_service import api_key_encryption
            api_key = api_key_encryption.decrypt(key.encrypted_key)
            
            # 创建 AI 提供商
            provider = AIProviderFactory.create(task.provider, api_key)
            
            # 获取参数
            params = task.parameters or {}
            num_slides = params.get("num_slides", 10)
            language = params.get("language", "zh")
            
            # 步骤 1: 生成大纲
            task.progress = 20
            await db.commit()
            
            outline = await provider.generate_ppt_outline(
                prompt=task.prompt,
                num_slides=num_slides,
                language=language
            )
            
            # 步骤 2: 生成每页内容
            task.progress = 40
            await db.commit()
            
            slides = []
            outline_slides = outline.get("slides", [])
            
            for i, slide_outline in enumerate(outline_slides):
                slide_type = slide_outline.get("type", "content")
                title = slide_outline.get("title", "")
                
                # 生成详细内容
                content = await provider.generate_slide_content(
                    title=title,
                    slide_type=slide_type,
                    context=task.prompt,
                    language=language
                )
                
                # 构建幻灯片
                slide = {
                    "id": str(uuid.uuid4()),
                    "type": slide_type,
                    "content": {
                        "title": title,
                        "text": content,
                        "bullets": slide_outline.get("points", [])
                    },
                    "layout": {"type": slide_type},
                    "style": {}
                }
                
                slides.append(slide)
                
                # 更新进度
                progress = 40 + int((i + 1) / len(outline_slides) * 40)
                task.progress = min(progress, 80)
                await db.commit()
            
            # 步骤 3: 创建 PPT
            task.progress = 90
            await db.commit()
            
            presentation = Presentation(
                user_id=task.user_id,
                title=outline.get("title", "未命名演示文稿"),
                slides=slides,
                ai_prompt=task.prompt,
                ai_parameters=params,
                status="draft",
                version=1
            )
            
            db.add(presentation)
            await db.flush()
            
            # 更新任务完成状态
            task.status = "completed"
            task.progress = 100
            task.ppt_id = presentation.id
            task.result = {
                "ppt_id": str(presentation.id),
                "title": presentation.title,
                "slide_count": len(slides)
            }
            task.completed_at = utcnow_aware()
            
            await db.commit()
            
            print(f"[Generation] 任务 {task_id} 完成，PPT: {presentation.id}")
            
        except Exception as exc:
            print(f"[Generation] 任务 {task_id} 失败: {exc}")
            
            # 更新失败状态
            try:
                result = await db.execute(
                    select(GenerationTask).where(GenerationTask.id == task_id)
                )
                task = result.scalar_one_or_none()
                if task:
                    task.status = "failed"
                    task.error_message = str(exc)
                    await db.commit()
            except Exception as e:
                print(f"[Generation] 更新失败状态出错: {e}")
            
            # 重试
            raise task_self.retry(exc=exc, countdown=60)


@celery_app.task
def cleanup_stalled_tasks(max_minutes: int = 30):
    """
    清理卡住的任务
    
    将超过指定时间还在 processing 状态的任务标记为失败
    
    Args:
        max_minutes: 最大处理时间（分钟）
    """
    return asyncio.run(_cleanup_stalled_async(max_minutes))


async def _cleanup_stalled_async(max_minutes: int):
    """异步清理卡住的任务"""
    from app.database import AsyncSessionLocal
    from datetime import timedelta
    
    async with AsyncSessionLocal() as db:
        cutoff_time = utcnow_aware() - timedelta(minutes=max_minutes)
        
        # 查找卡住的任务
        result = await db.execute(
            select(GenerationTask).where(
                GenerationTask.status == "processing",
                GenerationTask.updated_at < cutoff_time
            )
        )
        
        stalled_tasks = result.scalars().all()
        
        for task in stalled_tasks:
            task.status = "failed"
            task.error_message = f"任务处理超时（超过 {max_minutes} 分钟）"
            print(f"[Cleanup] 标记超时任务: {task.id}")
        
        await db.commit()
        
        return len(stalled_tasks)
