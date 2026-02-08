"""
操作历史服务
处理撤销/重做功能
"""

from datetime import datetime
from typing import List, Optional, Tuple
from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.operation_history import OperationHistory
from app.utils.datetime import utcnow_aware
from app.models.presentation import Presentation


class OperationHistoryService:
    """
    操作历史服务
    
    功能：
    - 记录操作
    - 撤销（Undo）
    - 重做（Redo）
    - 历史列表
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def record_operation(
        self,
        user_id: UUID,
        ppt_id: UUID,
        operation_type: str,
        description: str,
        before_state: Optional[dict],
        after_state: Optional[dict],
        slide_id: Optional[str] = None
    ) -> OperationHistory:
        """
        记录操作
        
        Args:
            user_id: 用户 ID
            ppt_id: PPT ID
            operation_type: 操作类型
            description: 描述
            before_state: 操作前状态
            after_state: 操作后状态
            slide_id: 幻灯片 ID（可选）
            
        Returns:
            创建的记录
        """
        # 删除该 PPT 所有已撤销的操作（redo 栈清空）
        # 当用户进行新操作时，之前的撤销历史不能再恢复
        await self.db.execute(
            delete(OperationHistory)
            .where(
                OperationHistory.ppt_id == ppt_id,
                OperationHistory.is_undone == True
            )
        )
        
        operation = OperationHistory(
            user_id=user_id,
            ppt_id=ppt_id,
            operation_type=operation_type,
            slide_id=slide_id,
            before_state=before_state,
            after_state=after_state,
            description=description,
            is_undone=False
        )
        
        self.db.add(operation)
        await self.db.commit()
        await self.db.refresh(operation)
        
        return operation
    
    async def get_history(
        self,
        ppt_id: UUID,
        user_id: UUID,
        limit: int = 50
    ) -> List[OperationHistory]:
        """
        获取操作历史
        
        Args:
            ppt_id: PPT ID
            user_id: 用户 ID
            limit: 数量限制
            
        Returns:
            操作历史列表（按时间倒序）
        """
        result = await self.db.execute(
            select(OperationHistory)
            .where(
                OperationHistory.ppt_id == ppt_id,
                OperationHistory.user_id == user_id
            )
            .order_by(OperationHistory.created_at.desc())
            .limit(limit)
        )
        
        return result.scalars().all()
    
    async def undo(
        self,
        ppt_id: UUID,
        user_id: UUID
    ) -> Tuple[bool, Optional[str], Optional[dict]]:
        """
        撤销操作
        
        Args:
            ppt_id: PPT ID
            user_id: 用户 ID
            
        Returns:
            (是否成功, 操作描述, 恢复后的状态)
        """
        # 找到最后一个未撤销的操作
        result = await self.db.execute(
            select(OperationHistory)
            .where(
                OperationHistory.ppt_id == ppt_id,
                OperationHistory.user_id == user_id,
                OperationHistory.is_undone == False
            )
            .order_by(OperationHistory.created_at.desc())
            .limit(1)
        )
        
        operation = result.scalar_one_or_none()
        
        if not operation:
            return False, "没有可撤销的操作", None
        
        # 标记为已撤销
        operation.is_undone = True
        operation.undone_at = utcnow_aware()
        
        # 恢复 PPT 状态
        if operation.before_state:
            ppt_result = await self.db.execute(
                select(Presentation).where(
                    Presentation.id == ppt_id,
                    Presentation.user_id == user_id
                )
            )
            ppt = ppt_result.scalar_one_or_none()
            if ppt and 'slides' in operation.before_state:
                ppt.slides = operation.before_state['slides']
                if 'title' in operation.before_state:
                    ppt.title = operation.before_state['title']
                ppt.version += 1
        
        await self.db.commit()
        
        return True, operation.description, operation.before_state
    
    async def redo(
        self,
        ppt_id: UUID,
        user_id: UUID
    ) -> Tuple[bool, Optional[str], Optional[dict]]:
        """
        重做操作
        
        Args:
            ppt_id: PPT ID
            user_id: 用户 ID
            
        Returns:
            (是否成功, 操作描述, 恢复后的状态)
        """
        # 找到最后一个被撤销的操作
        result = await self.db.execute(
            select(OperationHistory)
            .where(
                OperationHistory.ppt_id == ppt_id,
                OperationHistory.user_id == user_id,
                OperationHistory.is_undone == True
            )
            .order_by(OperationHistory.undone_at.desc())  # 最晚撤销的先恢复
            .limit(1)
        )
        
        operation = result.scalar_one_or_none()
        
        if not operation:
            return False, "没有可重做的操作", None
        
        # 取消撤销标记
        operation.is_undone = False
        operation.undone_at = None
        
        # 应用操作后的状态
        if operation.after_state:
            ppt_result = await self.db.execute(
                select(Presentation).where(
                    Presentation.id == ppt_id,
                    Presentation.user_id == user_id
                )
            )
            ppt = ppt_result.scalar_one_or_none()
            if ppt and 'slides' in operation.after_state:
                ppt.slides = operation.after_state['slides']
                if 'title' in operation.after_state:
                    ppt.title = operation.after_state['title']
                ppt.version += 1
        
        await self.db.commit()
        
        return True, operation.description, operation.after_state
    
    async def can_undo(self, ppt_id: UUID, user_id: UUID) -> bool:
        """检查是否可以撤销"""
        result = await self.db.execute(
            select(OperationHistory)
            .where(
                OperationHistory.ppt_id == ppt_id,
                OperationHistory.user_id == user_id,
                OperationHistory.is_undone == False
            )
            .limit(1)
        )
        return result.scalar_one_or_none() is not None
    
    async def can_redo(self, ppt_id: UUID, user_id: UUID) -> bool:
        """检查是否可以重做"""
        result = await self.db.execute(
            select(OperationHistory)
            .where(
                OperationHistory.ppt_id == ppt_id,
                OperationHistory.user_id == user_id,
                OperationHistory.is_undone == True
            )
            .limit(1)
        )
        return result.scalar_one_or_none() is not None


def get_operation_history_service(db: AsyncSession) -> OperationHistoryService:
    """获取操作历史服务实例"""
    return OperationHistoryService(db)
