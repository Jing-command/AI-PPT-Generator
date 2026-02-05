"""
模板相关的 Pydantic 模型
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class TemplateTheme(BaseModel):
    """模板主题"""
    primary_color: str
    secondary_color: str
    background: str
    font_family: str


class TemplateLayout(BaseModel):
    """模板布局"""
    type: str
    background: Optional[str] = None
    title_style: Optional[Dict[str, Any]] = None
    content_style: Optional[Dict[str, Any]] = None


class TemplateContent(BaseModel):
    """模板内容"""
    theme: TemplateTheme
    layouts: List[TemplateLayout]


class TemplateResponse(BaseModel):
    """模板响应"""
    id: UUID
    name: str
    description: Optional[str]
    category: str
    thumbnail_url: Optional[str]
    usage_count: int
    is_premium: bool
    
    class Config:
        from_attributes = True


class TemplateDetailResponse(TemplateResponse):
    """模板详情"""
    content: Dict[str, Any]
    created_at: datetime
    updated_at: datetime


class TemplateListResponse(BaseModel):
    """模板列表响应"""
    templates: List[TemplateResponse]
    total: int


class TemplateCategoryResponse(BaseModel):
    """模板分类"""
    id: str
    name: str
    icon: str
