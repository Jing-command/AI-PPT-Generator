"""
Schemas 包初始化
导出所有 Pydantic 模型
"""

from app.schemas.api_key import (
    APIKeyBase,
    APIKeyCreate,
    APIKeyDetailResponse,
    APIKeyResponse,
    APIKeyUpdate,
    APIKeyVerifyResponse,
)
from app.schemas.presentation import (
    ExportRequest,
    ExportResponse,
    GenerateRequest,
    GenerateResponse,
    GenerateStatusResponse,
    PresentationCreate,
    PresentationDetailResponse,
    PresentationResponse,
    PresentationUpdate,
    Slide,
    SlideContent,
    SlideCreate,
    SlideLayout,
    SlideStyle,
    SlideUpdate,
)
from app.schemas.user import (
    ErrorResponse,
    LoginRequest,
    RefreshTokenRequest,
    Token,
    UserBase,
    UserCreate,
    UserResponse,
)

__all__ = [
    # User
    "UserBase",
    "UserCreate",
    "UserResponse",
    "Token",
    "LoginRequest",
    "RefreshTokenRequest",
    "ErrorResponse",
    # API Key
    "APIKeyBase",
    "APIKeyCreate",
    "APIKeyUpdate",
    "APIKeyResponse",
    "APIKeyDetailResponse",
    "APIKeyVerifyResponse",
    # Presentation
    "PresentationCreate",
    "PresentationUpdate",
    "PresentationResponse",
    "PresentationDetailResponse",
    "Slide",
    "SlideContent",
    "SlideLayout",
    "SlideStyle",
    "SlideCreate",
    "SlideUpdate",
    "GenerateRequest",
    "GenerateResponse",
    "GenerateStatusResponse",
    "ExportRequest",
    "ExportResponse",
]
