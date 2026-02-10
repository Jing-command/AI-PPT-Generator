"""
PPT Generation Tasks
Handle AI-generated PPT asynchronous tasks
"""

import asyncio
import uuid
from datetime import datetime

from sqlalchemy import select, create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.presentation import GenerationTask, Presentation
from app.services.ai_provider import AIProviderFactory
from app.services.api_key_service import APIKeyService
from app.tasks import celery_app
from app.utils.datetime import utcnow_aware


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
    Process PPT generation task
    
    Args:
        task_id: Generation task ID
    """
    # Run async code in new event loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        result = loop.run_until_complete(_process_with_sync_db(self, task_id))
        return result
    except Exception as exc:
        print(f"[Generation] Task {task_id} error: {exc}")
        import traceback
        traceback.print_exc()
        raise self.retry(exc=exc, countdown=60)
    finally:
        try:
            loop.run_until_complete(loop.shutdown_asyncgens())
            loop.close()
        except:
            pass


async def _process_with_sync_db(task_self, task_id: str):
    """Process with sync database operations"""
    
    # Step 1: Get task info using sync DB
    with SyncSessionLocal() as sync_db:
        task = sync_db.query(GenerationTask).filter(GenerationTask.id == task_id).first()
        
        if not task:
            print(f"[Generation] Task {task_id} does not exist")
            return
        
        if task.status == "cancelled":
            print(f"[Generation] Task {task_id} has been cancelled")
            return
        
        # Update to processing
        task.status = "processing"
        task.progress = 10
        sync_db.commit()
        
        # Get API Key using async service
        from app.database import AsyncSessionLocal
        
        async with AsyncSessionLocal() as async_db:
            api_key_service = APIKeyService(async_db)
            key = await api_key_service.get_default_key(task.user_id, task.provider)
            
            if not key:
                # Update failure status
                with SyncSessionLocal() as db2:
                    t = db2.query(GenerationTask).filter(GenerationTask.id == task_id).first()
                    if t:
                        t.status = "failed"
                        t.error_message = f"No valid {task.provider} API Key found"
                        db2.commit()
                raise ValueError(f"No valid {task.provider} API Key found")
            
            # Decrypt API Key
            from app.services.encryption_service import api_key_encryption
            api_key = api_key_encryption.decrypt(key.api_key_encrypted)
            
            # Create AI provider
            provider = AIProviderFactory.create(task.provider, api_key)
            
            # Get parameters
            params = task.parameters or {}
            num_slides = params.get("num_slides", 10)
            language = params.get("language", "zh")
            style = params.get("style", "business")
            
            # Step 2: Generate outline
            with SyncSessionLocal() as db2:
                t = db2.query(GenerationTask).filter(GenerationTask.id == task_id).first()
                if t:
                    t.progress = 20
                    db2.commit()
            
            outline = await provider.generate_ppt_outline(
                prompt=task.prompt,
                num_slides=num_slides,
                language=language,
                style=style
            )
            
            theme = outline.get("theme", {})
            
            # Step 3: Build slides
            with SyncSessionLocal() as db2:
                t = db2.query(GenerationTask).filter(GenerationTask.id == task_id).first()
                if t:
                    t.progress = 40
                    db2.commit()
            
            slides = []
            outline_slides = outline.get("slides", [])
            
            for i, slide_outline in enumerate(outline_slides):
                slide_type = slide_outline.get("type", "content")
                title = slide_outline.get("title", "")
                
                # Build content based on layout type
                content_data = {"title": title}
                
                if slide_type == "title":
                    content_data["subtitle"] = slide_outline.get("subtitle", "")
                elif slide_type == "section":
                    content_data["description"] = slide_outline.get("description", "")
                elif slide_type == "two-column":
                    left = slide_outline.get("left", {})
                    right = slide_outline.get("right", {})
                    content_data["left"] = {
                        "title": left.get("title", ""),
                        "points": left.get("points", [])
                    }
                    content_data["right"] = {
                        "title": right.get("title", ""),
                        "points": right.get("points", [])
                    }
                elif slide_type == "timeline":
                    events = slide_outline.get("events", [])
                    content_data["events"] = events if events else []
                elif slide_type == "process":
                    steps = slide_outline.get("steps", [])
                    content_data["steps"] = steps if steps else []
                elif slide_type == "grid":
                    items = slide_outline.get("items", [])
                    content_data["items"] = items if items else []
                elif slide_type == "comparison":
                    items = slide_outline.get("items", [])
                    content_data["items"] = items if items else []
                elif slide_type == "data":
                    stats = slide_outline.get("stats", [])
                    content_data["stats"] = stats if stats else []
                elif slide_type == "quote":
                    content_data["quote"] = slide_outline.get("quote", "")
                    content_data["author"] = slide_outline.get("author", "")
                    content_data["title"] = slide_outline.get("title", "")
                elif slide_type == "image-text":
                    content_data["image_url"] = slide_outline.get("image_url", "")
                    content_data["text"] = slide_outline.get("text", "")
                else:  # content
                    points = slide_outline.get("points", [])
                    content_data["bullets"] = points
                    content_data["text"] = slide_outline.get("content", "")
                
                slide_style = slide_outline.get("style", {})
                
                slide = {
                    "id": str(uuid.uuid4()),
                    "type": slide_type,
                    "content": content_data,
                    "layout": {"type": slide_type},
                    "style": {**slide_style, "theme": theme}
                }
                slides.append(slide)
                
                # Update progress
                progress = 40 + int((i + 1) / len(outline_slides) * 40)
                with SyncSessionLocal() as db2:
                    t = db2.query(GenerationTask).filter(GenerationTask.id == task_id).first()
                    if t:
                        t.progress = min(progress, 80)
                        db2.commit()
            
            # Step 4: Create presentation
            with SyncSessionLocal() as db2:
                t = db2.query(GenerationTask).filter(GenerationTask.id == task_id).first()
                if t:
                    t.progress = 90
                    db2.commit()
            
            # Create presentation using sync DB
            with SyncSessionLocal() as db2:
                presentation = Presentation(
                    user_id=task.user_id,
                    title=outline.get("title", "Untitled Presentation"),
                    slides=slides,
                    ai_prompt=task.prompt,
                    ai_parameters=params,
                    status="draft",
                    version=1
                )
                db2.add(presentation)
                db2.commit()
                db2.refresh(presentation)
                
                # Update task completion
                t = db2.query(GenerationTask).filter(GenerationTask.id == task_id).first()
                if t:
                    t.status = "completed"
                    t.progress = 100
                    t.ppt_id = presentation.id
                    t.result = {
                        "ppt_id": str(presentation.id),
                        "title": presentation.title,
                        "slide_count": len(slides)
                    }
                    t.completed_at = utcnow_aware()
                    db2.commit()
                
                print(f"[Generation] Task {task_id} completed, PPT: {presentation.id}")


@celery_app.task
def cleanup_stalled_tasks(max_minutes: int = 30):
    """Clean up stalled tasks"""
    with SyncSessionLocal() as db:
        from datetime import timedelta
        cutoff_time = utcnow_aware() - timedelta(minutes=max_minutes)
        
        stalled_tasks = db.query(GenerationTask).filter(
            GenerationTask.status == "processing",
            GenerationTask.updated_at < cutoff_time
        ).all()
        
        for task in stalled_tasks:
            task.status = "failed"
            task.error_message = f"Task processing timeout (exceeded {max_minutes} minutes)"
            print(f"[Cleanup] Marked timed out task: {task.id}")
        
        db.commit()
        return len(stalled_tasks)
