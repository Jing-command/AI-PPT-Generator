"""
PPT 生成服务
处理异步生成任务
"""

from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.presentation import GenerationTask, Presentation
from app.schemas.presentation import GenerateRequest
from app.services.ai_provider import AIProviderFactory
from app.services.api_key_service import APIKeyService


class PPTGenerationService:
    """
    PPT 生成服务
    
    处理 AI 生成流程：
    1. 选择 API Key
    2. 生成大纲
    3. 生成每页内容
    4. 生成配图
    5. 组装 PPT
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_task(
        self,
        user_id: UUID,
        request: GenerateRequest
    ) -> GenerationTask:
        """
        创建生成任务
        
        Args:
            user_id: 用户 ID
            request: 生成请求
            
        Returns:
            创建的任务
        """
        # 选择 API Key
        api_key_service = APIKeyService(self.db)
        provider = request.provider or "openai"
        
        key = await api_key_service.get_default_key(user_id, provider)
        if not key:
            raise ValueError(f"未找到有效的 {provider} API Key，请先添加")
        
        # 创建任务
        task = GenerationTask(
            user_id=user_id,
            provider=provider,
            prompt=request.prompt,
            parameters={
                "num_slides": request.num_slides,
                "language": request.language,
                "style": request.style,
                "template_id": request.template_id
            },
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
    ) -> Optional[GenerationTask]:
        """
        获取任务状态
        
        Args:
            task_id: 任务 ID
            user_id: 用户 ID（权限验证）
            
        Returns:
            任务对象或 None
        """
        result = await self.db.execute(
            select(GenerationTask).where(
                GenerationTask.id == task_id,
                GenerationTask.user_id == user_id
            )
        )
        return result.scalar_one_or_none()
    
    async def cancel_task(
        self,
        task_id: UUID,
        user_id: UUID
    ) -> bool:
        """
        取消任务
        
        Args:
            task_id: 任务 ID
            user_id: 用户 ID
            
        Returns:
            是否成功取消
        """
        task = await self.get_task(task_id, user_id)
        
        if not task:
            return False
        
        if task.status not in ["pending", "processing"]:
            return False
        
        task.status = "cancelled"
        await self.db.commit()
        
        return True


# 便捷函数
def get_ppt_generation_service(db: AsyncSession) -> PPTGenerationService:
    """获取生成服务实例"""
    return PPTGenerationService(db)
