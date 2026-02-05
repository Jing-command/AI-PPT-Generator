"""
API Key 管理路由
处理用户 AI 提供商 API Key 的 CRUD
"""

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import get_current_user
from app.database import get_db
from app.models.user import User
from app.schemas.api_key import (
    APIKeyCreate,
    APIKeyDetailResponse,
    APIKeyResponse,
    APIKeyUpdate,
    APIKeyVerifyResponse,
)
from app.services.api_key_service import get_api_key_service

router = APIRouter(prefix="/api-keys", tags=["API Key 管理"])


@router.get(
    "",
    response_model=List[APIKeyResponse],
    summary="获取用户的所有 API Key",
    description="返回用户添加的所有 API Key（脱敏，不包含原始 Key）"
)
async def list_api_keys(
    current_user: User = Depends(get_current_user),
    db = Depends(get_db)
) -> List[APIKeyResponse]:
    """获取 API Key 列表"""
    service = get_api_key_service(db)
    keys = await service.get_by_user(current_user.id)
    return keys


@router.post(
    "",
    response_model=APIKeyDetailResponse,
    status_code=status.HTTP_201_CREATED,
    summary="添加 API Key",
    description="添加新的 AI 提供商 API Key"
)
async def create_api_key(
    data: APIKeyCreate,
    current_user: User = Depends(get_current_user),
    db = Depends(get_db)
) -> APIKeyDetailResponse:
    """创建 API Key"""
    service = get_api_key_service(db)
    
    try:
        key = await service.create(current_user.id, data)
        return key
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "INVALID_PROVIDER",
                "message": str(e)
            }
        )


@router.get(
    "/{key_id}",
    response_model=APIKeyDetailResponse,
    summary="获取 API Key 详情",
    description="获取指定 API Key 的详细信息"
)
async def get_api_key(
    key_id: UUID,
    current_user: User = Depends(get_current_user),
    db = Depends(get_db)
) -> APIKeyDetailResponse:
    """获取单个 API Key"""
    service = get_api_key_service(db)
    key = await service.get_by_id(key_id, current_user.id)
    
    if not key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "NOT_FOUND",
                "message": "API Key 不存在"
            }
        )
    
    return key


@router.patch(
    "/{key_id}",
    response_model=APIKeyDetailResponse,
    summary="更新 API Key",
    description="更新 API Key 的名称、状态或默认设置"
)
async def update_api_key(
    key_id: UUID,
    data: APIKeyUpdate,
    current_user: User = Depends(get_current_user),
    db = Depends(get_db)
) -> APIKeyDetailResponse:
    """更新 API Key"""
    service = get_api_key_service(db)
    key = await service.update(key_id, current_user.id, data)
    
    if not key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "NOT_FOUND",
                "message": "API Key 不存在"
            }
        )
    
    return key


@router.delete(
    "/{key_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="删除 API Key",
    description="删除指定的 API Key"
)
async def delete_api_key(
    key_id: UUID,
    current_user: User = Depends(get_current_user),
    db = Depends(get_db)
):
    """删除 API Key"""
    service = get_api_key_service(db)
    success = await service.delete(key_id, current_user.id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "NOT_FOUND",
                "message": "API Key 不存在"
            }
        )
    
    return None


@router.post(
    "/{key_id}/verify",
    response_model=APIKeyVerifyResponse,
    summary="验证 API Key",
    description="验证 API Key 是否有效（尝试解密）"
)
async def verify_api_key(
    key_id: UUID,
    current_user: User = Depends(get_current_user),
    db = Depends(get_db)
) -> APIKeyVerifyResponse:
    """验证 API Key"""
    service = get_api_key_service(db)
    
    key = await service.get_by_id(key_id, current_user.id)
    if not key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "NOT_FOUND",
                "message": "API Key 不存在"
            }
        )
    
    is_valid = await service.verify_key(key_id, current_user.id)
    
    return APIKeyVerifyResponse(
        valid=is_valid,
        provider=key.provider,
        message="验证成功" if is_valid else "验证失败，Key 可能已失效"
    )
