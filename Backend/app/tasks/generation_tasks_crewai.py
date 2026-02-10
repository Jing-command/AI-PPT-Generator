"""
PPT Generation Tasks (CrewAI Version)
使用CrewAI多Agent架构生成PPT
"""

import asyncio
import json
import uuid
from datetime import datetime

from sqlalchemy import select, create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.presentation import GenerationTask, Presentation
from app.services.api_key_service import APIKeyService
from app.services.encryption_service import api_key_encryption
from app.tasks import celery_app
from app.utils.datetime import utcnow_aware

# CrewAI导入
from app.crew.ppt_crew import create_ppt_crew


# Create sync engine for Celery tasks
sync_engine = create_engine(
    settings.DATABASE_URL.replace('postgresql+asyncpg', 'postgresql'),
    pool_pre_ping=True,
    pool_recycle=3600
)
SyncSessionLocal = sessionmaker(bind=sync_engine)


@celery_app.task(bind=True, max_retries=3)
def process_generation_task(self, task_id: str):
    """
    使用CrewAI多Agent架构处理PPT生成任务
    
    Args:
        task_id: 生成任务ID
    """
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        result = loop.run_until_complete(_process_with_crewai(self, task_id))
        return result
    except Exception as exc:
        print(f"[CrewAI Generation] Task {task_id} error: {exc}")
        import traceback
        traceback.print_exc()
        raise self.retry(exc=exc, countdown=60)
    finally:
        try:
            loop.run_until_complete(loop.shutdown_asyncgens())
            loop.close()
        except:
            pass


async def _process_with_crewai(task_self, task_id: str):
    """
    使用CrewAI处理生成任务
    """
    
    # Step 1: 获取任务信息
    with SyncSessionLocal() as sync_db:
        task = sync_db.query(GenerationTask).filter(GenerationTask.id == task_id).first()
        
        if not task:
            print(f"[CrewAI] Task {task_id} does not exist")
            return
        
        if task.status == "cancelled":
            print(f"[CrewAI] Task {task_id} has been cancelled")
            return
        
        # 更新为处理中
        task.status = "processing"
        task.progress = 5
        sync_db.commit()
        
        # 获取API Key
        from app.database import AsyncSessionLocal
        
        async with AsyncSessionLocal() as async_db:
            api_key_service = APIKeyService(async_db)
            
            # 首先尝试获取 Moonshot (Kimi) 的 Key
            key = await api_key_service.get_default_key(task.user_id, "moonshot")
            
            # 如果没有 Moonshot Key，再尝试任务指定的 provider
            if not key:
                key = await api_key_service.get_default_key(task.user_id, task.provider)
            
            # 如果还是没有，尝试获取任意可用 Key
            if not key:
                key = await api_key_service.get_any_active_key(task.user_id)
            
            if not key:
                with SyncSessionLocal() as db2:
                    t = db2.query(GenerationTask).filter(GenerationTask.id == task_id).first()
                    if t:
                        t.status = "failed"
                        t.error_message = "未找到有效的 API Key，请先添加 Moonshot (Kimi) 或其他提供商的 Key"
                        db2.commit()
                raise ValueError("No valid API Key found")
            
            # 解密API Key
            api_key = api_key_encryption.decrypt(key.api_key_encrypted)
            
            # 获取参数
            parameters = task.parameters or {}
            num_slides = parameters.get('num_slides', 10)
            language = parameters.get('language', 'zh-CN')
            style = parameters.get('style', 'professional')
            
            # 更新进度回调函数
            async def update_progress(progress: int, message: str):
                with SyncSessionLocal() as db:
                    t = db.query(GenerationTask).filter(GenerationTask.id == task_id).first()
                    if t and t.status != "cancelled":
                        t.progress = progress
                        # 可以将message也保存到task中（如果需要）
                        db.commit()
                print(f"[CrewAI] Task {task_id} - {progress}%: {message}")
            
            try:
                # Step 2: 创建Crew并生成PPT
                print(f"[CrewAI] Starting generation for task {task_id}")
                
                # 确定 provider，优先使用 moonshot
                provider = key.provider if key.provider else "moonshot"
                
                crew = create_ppt_crew(
                    provider=provider,
                    api_key=api_key,
                    model=key.model if key.model else "kimi-k2-5"
                )
                
                result = await crew.generate_ppt(
                    user_prompt=task.prompt,
                    num_slides=num_slides,
                    references="",  # 可以扩展支持参考资料
                    style_preference=style,
                    progress_callback=update_progress
                )
                
                if result['status'] == 'error':
                    raise Exception(result['error'])
                
                # Step 3: 保存生成的PPT
                ppt_data = result['data']
                
                # 创建Presentation记录
                with SyncSessionLocal() as db:
                    # 构建slides数组
                    slides = []
                    for slide_content in ppt_data.get('slides', []):
                        slides.append({
                            'id': str(uuid.uuid4()),
                            'title': slide_content.get('title', ''),
                            'content': slide_content.get('bullet_points', []),
                            'speaker_notes': slide_content.get('speaker_notes', ''),
                            'chart_type': slide_content.get('chart_type', 'none'),
                            'chart_data': slide_content.get('chart_data', {}),
                            'layout': slide_content.get('layout', 'title-content')
                        })
                    
                    # 提取主题
                    topic = ppt_data.get('requirement', {}).get('topic', task.prompt[:50])
                    
                    presentation = Presentation(
                        user_id=task.user_id,
                        title=topic,
                        description=task.prompt,
                        slides=slides,
                        status="completed",
                        metadata={
                            'generation_method': 'crewai_multi_agent',
                            'provider': task.provider,
                            'model': key.model,
                            'visual_design': ppt_data.get('visual_design', {}),
                            'outline': ppt_data.get('outline', {}),
                            'quality_report': result.get('quality_report', {})
                        }
                    )
                    
                    db.add(presentation)
                    db.commit()
                    db.refresh(presentation)
                    
                    # 更新任务状态
                    task_ref = db.query(GenerationTask).filter(GenerationTask.id == task_id).first()
                    if task_ref:
                        task_ref.status = "completed"
                        task_ref.progress = 100
                        task_ref.result_ppt_id = presentation.id
                        task_ref.completed_at = utcnow_aware()
                        db.commit()
                    
                    print(f"[CrewAI] Task {task_id} completed successfully")
                    return {
                        'task_id': task_id,
                        'ppt_id': str(presentation.id),
                        'status': 'completed'
                    }
                    
            except Exception as e:
                # 更新失败状态
                with SyncSessionLocal() as db:
                    t = db.query(GenerationTask).filter(GenerationTask.id == task_id).first()
                    if t:
                        t.status = "failed"
                        t.error_message = str(e)
                        db.commit()
                
                print(f"[CrewAI] Task {task_id} failed: {e}")
                raise


# 保持向后兼容的函数名
process_generation_task_crewai = process_generation_task
