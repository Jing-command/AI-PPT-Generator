"""
模板路由
"""

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import get_current_user
from app.database import get_db
from app.models.user import User
from app.schemas.template import (
    TemplateCategoryResponse,
    TemplateDetailResponse,
    TemplateListResponse,
)
from app.services.template_service import get_template_service

router = APIRouter(prefix="/templates", tags=["模板"])


@router.get(
    "",
    response_model=TemplateListResponse,
    summary="获取模板列表"
)
async def list_templates(
    category: str = None,
    is_premium: bool = None,
    limit: int = 50,
    db = Depends(get_db)
):
    """
    获取 PPT 模板列表
    
    可按分类和是否付费筛选
    """
    service = get_template_service(db)
    templates = await service.get_templates(category, is_premium, limit)
    
    return {
        "templates": templates,
        "total": len(templates)
    }


@router.get(
    "/categories",
    response_model=List[TemplateCategoryResponse],
    summary="获取模板分类"
)
async def get_categories():
    """获取所有模板分类"""
    return [
        {"id": "business", "name": "商务", "icon": "💼"},
        {"id": "education", "name": "教育", "icon": "📚"},
        {"id": "creative", "name": "创意", "icon": "🎨"},
        {"id": "minimal", "name": "极简", "icon": "⚪"},
        {"id": "general", "name": "通用", "icon": "📄"},
    ]


@router.get(
    "/{template_id}",
    response_model=TemplateDetailResponse,
    summary="获取模板详情"
)
async def get_template(
    template_id: UUID,
    db = Depends(get_db)
):
    """获取模板详细信息"""
    service = get_template_service(db)
    template = await service.get_by_id(template_id)
    
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "NOT_FOUND", "message": "模板不存在"}
        )
    
    return template


@router.post(
    "/{template_id}/use",
    summary="使用模板（增加使用次数）"
)
async def use_template(
    template_id: UUID,
    current_user: User = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    记录模板使用
    
    创建 PPT 时调用，增加模板使用统计
    """
    service = get_template_service(db)
    template = await service.get_by_id(template_id)
    
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "NOT_FOUND", "message": "模板不存在"}
        )
    
    await service.increment_usage(template_id)
    
    return {"message": "模板使用已记录"}
