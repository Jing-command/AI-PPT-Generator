"""
模板服务
"""

from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.template import Template


class TemplateService:
    """
    模板服务
    
    功能：
    - 获取模板列表
    - 获取模板详情
    - 应用模板到 PPT
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_templates(
        self,
        category: Optional[str] = None,
        is_premium: Optional[bool] = None,
        limit: int = 50
    ) -> List[Template]:
        """
        获取模板列表
        
        Args:
            category: 分类筛选
            is_premium: 是否付费筛选
            limit: 数量限制
            
        Returns:
            模板列表
        """
        query = select(Template).order_by(Template.usage_count.desc())
        
        if category:
            query = query.where(Template.category == category)
        
        if is_premium is not None:
            query = query.where(Template.is_premium == is_premium)
        
        query = query.limit(limit)
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def get_by_id(self, template_id: UUID) -> Optional[Template]:
        """
        获取模板详情
        
        Args:
            template_id: 模板 ID
            
        Returns:
            模板对象或 None
        """
        result = await self.db.execute(
            select(Template).where(Template.id == template_id)
        )
        return result.scalar_one_or_none()
    
    async def increment_usage(self, template_id: UUID) -> None:
        """
        增加模板使用次数
        
        Args:
            template_id: 模板 ID
        """
        template = await self.get_by_id(template_id)
        if template:
            template.usage_count += 1
            await self.db.commit()
    
    async def create_default_templates(self) -> None:
        """
        创建默认系统模板
        
        在应用启动时调用，创建预设模板
        """
        # 检查是否已有系统模板
        result = await self.db.execute(
            select(Template).where(Template.is_system == True).limit(1)
        )
        if result.scalar_one_or_none():
            return  # 已存在
        
        # 商务模板
        business_template = Template(
            name="商务简约",
            description="适合商业演示的简约风格",
            category="business",
            is_system=True,
            content={
                "theme": {
                    "primary_color": "#1a365d",
                    "secondary_color": "#3182ce",
                    "background": "#ffffff",
                    "font_family": "Microsoft YaHei"
                },
                "layouts": [
                    {
                        "type": "title",
                        "background": "gradient",
                        "title_style": {"font_size": 44, "bold": True},
                        "subtitle_style": {"font_size": 24}
                    },
                    {
                        "type": "content",
                        "title_style": {"font_size": 32, "bold": True},
                        "content_style": {"font_size": 18}
                    }
                ]
            }
        )
        
        # 教育模板
        education_template = Template(
            name="教育课件",
            description="适合教学演示的清新风格",
            category="education",
            is_system=True,
            content={
                "theme": {
                    "primary_color": "#38a169",
                    "secondary_color": "#68d391",
                    "background": "#f7fafc",
                    "font_family": "Microsoft YaHei"
                },
                "layouts": [
                    {
                        "type": "title",
                        "background": "solid",
                        "title_style": {"font_size": 40, "bold": True},
                        "subtitle_style": {"font_size": 22}
                    }
                ]
            }
        )
        
        # 创意模板
        creative_template = Template(
            name="创意展示",
            description="适合创意提案的活泼风格",
            category="creative",
            is_system=True,
            content={
                "theme": {
                    "primary_color": "#d53f8c",
                    "secondary_color": "#ed64a6",
                    "background": "#fff5f5",
                    "font_family": "Microsoft YaHei"
                }
            }
        )
        
        # 极简模板
        minimal_template = Template(
            name="极简风格",
            description="黑白极简设计",
            category="minimal",
            is_system=True,
            content={
                "theme": {
                    "primary_color": "#000000",
                    "secondary_color": "#718096",
                    "background": "#ffffff",
                    "font_family": "Arial"
                }
            }
        )
        
        self.db.add_all([
            business_template,
            education_template,
            creative_template,
            minimal_template
        ])
        await self.db.commit()


def get_template_service(db: AsyncSession) -> TemplateService:
    """获取模板服务实例"""
    return TemplateService(db)
