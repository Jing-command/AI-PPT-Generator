"""
API Key 相关的 Pydantic 模型
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


class APIKeyBase(BaseModel):
    """API Key 基础模型"""
    provider: str = Field(..., description="AI 提供商")
    name: Optional[str] = Field(None, max_length=100, description="Key 别名")
    
    @field_validator('provider')
    @classmethod
    def validate_provider(cls, v: str) -> str:
        """验证提供商是否支持"""
        allowed = {'openai', 'moonshot', 'anthropic', 'gemini', 'qwen', 'ernie', 'deepseek', 'aliyun', 'tencent', 'azure', 'yunwu', 'yunwu-image'}
        if v.lower() not in allowed:
            raise ValueError(f'不支持的提供商: {v}. 支持的: {allowed}')
        return v.lower()


class APIKeyCreate(APIKeyBase):
    """创建 API Key 请求"""
    api_key: str = Field(..., min_length=10, description="API Key 值")
    is_default: bool = Field(False, description="是否设为默认")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "provider": "openai",
                "api_key": "sk-xxxxxxxxxxxxxxxxxxxxxxxx",
                "name": "我的 OpenAI Key",
                "is_default": True
            }
        }
    )


class APIKeyUpdate(BaseModel):
    """更新 API Key 请求"""
    name: Optional[str] = Field(None, max_length=100)
    is_default: Optional[bool] = None
    status: Optional[str] = Field(None, pattern="^(active|invalid|expired)$")


class APIKeyResponse(BaseModel):
    """API Key 响应（脱敏）"""
    id: UUID
    provider: str
    name: Optional[str]
    status: str
    is_default: bool
    last_verified_at: Optional[datetime]
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class APIKeyVerifyResponse(BaseModel):
    """API Key 验证响应"""
    valid: bool = Field(..., description="是否有效")
    provider: str = Field(..., description="检测到的提供商")
    message: str = Field(..., description="验证结果信息")


class APIKeyDetailResponse(APIKeyResponse):
    """API Key 详情（包含更多字段）"""
    updated_at: datetime
