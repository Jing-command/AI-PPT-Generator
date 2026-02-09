"""
PPT 管理服务
处理 PPT 的 CRUD 和单页编辑
"""

from typing import List, Optional
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.presentation import Presentation
from app.schemas.presentation import PresentationCreate, PresentationUpdate, Slide, SlideUpdate


class PPTService:
    """
    PPT 服务类
    
    功能：
    - PPT CRUD
    - 单页编辑
    - 版本控制
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create(
        self,
        user_id: UUID,
        data: PresentationCreate,
        slides: Optional[List[dict]] = None
    ) -> Presentation:
        """
        创建 PPT
        
        Args:
            user_id: 用户 ID
            data: 创建数据
            slides: 初始幻灯片（可选）
            
        Returns:
            创建的 PPT
        """
        ppt = Presentation(
            user_id=user_id,
            title=data.title,
            description=getattr(data, 'description', None),
            slides=slides or [],
            status="draft",
            version=1
        )
        
        self.db.add(ppt)
        await self.db.commit()
        await self.db.refresh(ppt)
        
        return ppt
    
    async def get_by_id(
        self,
        ppt_id: UUID,
        user_id: Optional[UUID] = None
    ) -> Optional[Presentation]:
        """
        获取 PPT
        
        Args:
            ppt_id: PPT ID
            user_id: 用户 ID（如果提供则验证权限）
            
        Returns:
            PPT 对象或 None
        """
        query = select(Presentation).where(Presentation.id == ppt_id)
        
        if user_id:
            query = query.where(Presentation.user_id == user_id)
        
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_by_user(
        self,
        user_id: UUID,
        skip: int = 0,
        limit: int = 20,
        status: Optional[str] = None
    ) -> List[Presentation]:
        """
        获取用户的 PPT 列表
        
        Args:
            user_id: 用户 ID
            skip: 分页偏移
            limit: 每页数量
            status: 状态筛选
            
        Returns:
            PPT 列表
        """
        query = select(Presentation).where(
            Presentation.user_id == user_id
        ).order_by(Presentation.updated_at.desc())
        
        if status:
            query = query.where(Presentation.status == status)
        
        query = query.offset(skip).limit(limit)
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def update(
        self,
        ppt_id: UUID,
        user_id: UUID,
        data: PresentationUpdate
    ) -> Optional[Presentation]:
        """
        更新 PPT
        
        Args:
            ppt_id: PPT ID
            user_id: 用户 ID
            data: 更新数据
            
        Returns:
            更新后的 PPT
        """
        ppt = await self.get_by_id(ppt_id, user_id)
        if not ppt:
            return None
        
        # 更新字段
        update_data = data.model_dump(exclude_unset=True)
        
        # 如果有 slides 更新，版本号 +1
        if 'slides' in update_data:
            ppt.version += 1
        
        for field, value in update_data.items():
            setattr(ppt, field, value)
        
        await self.db.commit()
        await self.db.refresh(ppt)
        
        return ppt
    
    async def delete(
        self,
        ppt_id: UUID,
        user_id: UUID
    ) -> bool:
        """
        删除 PPT
        
        Args:
            ppt_id: PPT ID
            user_id: 用户 ID
            
        Returns:
            是否成功删除
        """
        ppt = await self.get_by_id(ppt_id, user_id)
        if not ppt:
            return False
        
        await self.db.delete(ppt)
        await self.db.commit()
        
        return True
    
    # ==================== 单页编辑 ====================
    
    async def get_slide(
        self,
        ppt_id: UUID,
        slide_id: str,
        user_id: UUID
    ) -> Optional[dict]:
        """
        获取单页幻灯片
        
        Args:
            ppt_id: PPT ID
            slide_id: 幻灯片 ID
            user_id: 用户 ID
            
        Returns:
            幻灯片数据
        """
        ppt = await self.get_by_id(ppt_id, user_id)
        if not ppt:
            return None
        
        for slide in ppt.slides:
            if slide.get('id') == slide_id:
                return slide
        
        return None
    
    async def update_slide(
        self,
        ppt_id: UUID,
        slide_id: str,
        user_id: UUID,
        data: SlideUpdate
    ) -> Optional[dict]:
        """
        更新单页幻灯片（部分更新）
        """
        print(f"[SERVICE] update_slide called: ppt_id={ppt_id}, slide_id={slide_id}", flush=True)
        ppt = await self.get_by_id(ppt_id, user_id)
        if not ppt:
            return None
        
        # 查找幻灯片
        slide_index = None
        for i, slide in enumerate(ppt.slides):
            if slide.get('id') == slide_id:
                slide_index = i
                break
        
        if slide_index is None:
            return None
        
        # 部分更新
        update_data = data.model_dump(exclude_unset=True, exclude_none=True, mode='json')
        
        # 深度合并（创建新对象，不修改原对象）
        import copy
        def deep_merge(original: dict, update: dict) -> dict:
            """深度合并字典，返回新对象"""
            result = copy.deepcopy(original)
            for key, value in update.items():
                if isinstance(value, dict) and key in result and isinstance(result[key], dict):
                    result[key] = deep_merge(result[key], value)
                else:
                    result[key] = value
            return result
        
        # 创建全新的 slides 列表
        slides = copy.deepcopy(list(ppt.slides))
        updated_slide = deep_merge(slides[slide_index], update_data)
        slides[slide_index] = updated_slide
        ppt.slides = slides  # 赋值新列表，触发 SQLAlchemy 变更检测
        
        # 版本号 +1
        ppt.version += 1
        
        await self.db.commit()
        await self.db.refresh(ppt)
        
        # 直接返回更新后的数据
        return updated_slide
    
    async def add_slide(
        self,
        ppt_id: UUID,
        user_id: UUID,
        slide: dict,
        position: Optional[int] = None
    ) -> Optional[Presentation]:
        """
        添加幻灯片
        
        Args:
            ppt_id: PPT ID
            user_id: 用户 ID
            slide: 幻灯片数据
            position: 插入位置（None 表示末尾）
            
        Returns:
            更新后的 PPT
        """
        ppt = await self.get_by_id(ppt_id, user_id)
        if not ppt:
            return None
        
        # 确保有 ID
        if 'id' not in slide:
            import uuid
            slide['id'] = str(uuid.uuid4())
        
        slides = list(ppt.slides)

        # 插入到指定位置
        if position is None or position >= len(slides):
            slides.append(slide)
        else:
            slides.insert(position, slide)

        ppt.slides = slides
        
        ppt.version += 1
        
        await self.db.commit()
        await self.db.refresh(ppt)
        
        return ppt
    
    async def delete_slide(
        self,
        ppt_id: UUID,
        slide_id: str,
        user_id: UUID
    ) -> bool:
        """
        删除幻灯片
        
        Args:
            ppt_id: PPT ID
            slide_id: 幻灯片 ID
            user_id: 用户 ID
            
        Returns:
            是否成功删除
        """
        ppt = await self.get_by_id(ppt_id, user_id)
        if not ppt:
            return False
        
        original_len = len(ppt.slides)
        ppt.slides = [s for s in ppt.slides if s.get('id') != slide_id]
        
        if len(ppt.slides) == original_len:
            return False  # 没找到
        
        ppt.version += 1
        
        await self.db.commit()
        await self.db.refresh(ppt)
        
        return True


# 便捷函数
def get_ppt_service(db: AsyncSession) -> PPTService:
    """获取 PPT 服务实例"""
    return PPTService(db)
