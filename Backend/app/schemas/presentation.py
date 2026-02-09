"""
PPT 相关的 Pydantic 模型
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator


# ==================== Slide 模型 ====================

class SlideContent(BaseModel):
    """幻灯片内容"""
    title: Optional[str] = None
    subtitle: Optional[str] = None
    text: Optional[str] = None
    second_column: Optional[str] = None
    bullets: Optional[List[str]] = None
    image_url: Optional[str] = None
    chart_data: Optional[Dict[str, Any]] = None


class SlideLayout(BaseModel):
    """幻灯片布局"""
    type: str = Field(..., description="布局类型: title, content, split, image, chart")
    background: Optional[str] = None
    theme: Optional[str] = None


class SlideStyle(BaseModel):
    """幻灯片样式"""
    font_family: Optional[str] = None
    font_size: Optional[int] = None
    color: Optional[str] = None
    alignment: Optional[str] = None


class Slide(BaseModel):
    """幻灯片"""
    id: Optional[str] = None
    type: str = Field(default="content", description="幻灯片类型")
    content: SlideContent
    layout: Optional[SlideLayout] = None
    style: Optional[SlideStyle] = None
    notes: Optional[str] = None


# ==================== PPT 请求/响应 ====================

class PresentationBase(BaseModel):
    """PPT 基础模型"""
    title: str = Field(..., min_length=1, max_length=255)


class PresentationCreate(PresentationBase):
    """创建 PPT 请求"""
    description: Optional[str] = Field(None, max_length=1000, description="PPT 描述")
    template_id: Optional[str] = None
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "title": "AI 产品介绍",
                "description": "这是一个关于 AI 产品的介绍 PPT",
                "template_id": "business-modern"
            }
        }
    )


class PresentationUpdate(BaseModel):
    """更新 PPT 请求"""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    slides: Optional[List[Slide]] = None
    status: Optional[str] = Field(None, pattern="^(draft|published|archived)$")


class PresentationResponse(PresentationBase):
    """PPT 响应"""
    id: UUID
    user_id: UUID
    slides: List[Slide]
    slide_count: int = Field(default=0, description="幻灯片数量")
    status: str
    version: int
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
    
    @model_validator(mode='before')
    @classmethod
    def calculate_slide_count(cls, data: any) -> any:
        """自动计算 slide_count"""
        if hasattr(data, 'slides'):
            slides = data.slides
            if isinstance(slides, list):
                data = dict(data.__dict__) if hasattr(data, '__dict__') else dict(data)
                data['slide_count'] = len(slides)
        return data


class PresentationDetailResponse(PresentationResponse):
    """PPT 详情"""
    ai_prompt: Optional[str] = None
    ai_parameters: Optional[Dict[str, Any]] = None


# ==================== 幻灯片操作 ====================

class SlideCreate(BaseModel):
    """添加幻灯片"""
    type: str = "content"
    content: SlideContent
    layout: Optional[SlideLayout] = None
    position: Optional[int] = Field(None, description="插入位置，None 表示末尾")


class SlideUpdate(BaseModel):
    """更新幻灯片"""
    type: Optional[str] = None
    content: Optional[SlideContent] = None
    layout: Optional[SlideLayout] = None
    style: Optional[SlideStyle] = None
    notes: Optional[str] = None


# ==================== 生成请求 ====================

class GenerateRequest(BaseModel):
    """生成 PPT 请求"""
    prompt: str = Field(..., min_length=10, max_length=2000, description="生成提示词")
    template_id: Optional[str] = Field(None, description="模板 ID")
    num_slides: int = Field(default=10, ge=1, le=50, description="幻灯片数量")
    language: str = Field(default="zh", pattern="^(zh|en)$")
    style: str = Field(default="business", description="风格: business, education, creative, minimal")
    provider: Optional[str] = Field(None, description="指定 AI 提供商")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "prompt": "制作一个关于人工智能发展历程的 PPT",
                "num_slides": 8,
                "language": "zh",
                "style": "business"
            }
        }
    )


class GenerateResponse(BaseModel):
    """生成任务响应"""
    task_id: UUID
    status: str
    estimated_time: int = Field(..., description="预估秒数")
    message: str


class GenerateStatusResponse(BaseModel):
    """生成状态响应"""
    task_id: UUID
    status: str  # pending, processing, completed, failed, cancelled
    progress: int  # 0-100
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


# ==================== 导出请求 ====================

class ExportRequest(BaseModel):
    """导出请求"""
    format: str = Field(..., pattern="^(pptx|pdf|png|jpg)$")
    quality: str = Field(default="standard", pattern="^(standard|high)$")
    slide_range: Optional[str] = Field(None, description="页面范围，如 '1-5' 或 'all'")


class ExportResponse(BaseModel):
    """导出任务响应"""
    export_task_id: UUID
    status: str
    download_url: Optional[str] = None
    expires_at: Optional[datetime] = None
