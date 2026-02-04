"""
PPT CRUD 路由
处理 PPT 管理和单页编辑
"""

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import get_current_user
from app.database import get_db
from app.models.user import User
from app.schemas.presentation import (
    PresentationCreate,
    PresentationDetailResponse,
    PresentationResponse,
    PresentationUpdate,
    SlideCreate,
    SlideUpdate,
)
from app.services.operation_history_service import get_operation_history_service
from app.services.ppt_service import get_ppt_service

router = APIRouter(prefix="/ppt", tags=["PPT 管理"])


# ==================== PPT CRUD ====================

@router.post(
    "",
    response_model=PresentationDetailResponse,
    status_code=status.HTTP_201_CREATED,
    summary="创建 PPT"
)
async def create_ppt(
    data: PresentationCreate,
    current_user: User = Depends(get_current_user),
    db = Depends(get_db)
):
    """创建空白 PPT"""
    service = get_ppt_service(db)
    ppt = await service.create(current_user.id, data)
    return ppt


@router.get(
    "",
    response_model=List[PresentationResponse],
    summary="获取 PPT 列表"
)
async def list_ppts(
    skip: int = 0,
    limit: int = 20,
    status: str = None,
    current_user: User = Depends(get_current_user),
    db = Depends(get_db)
):
    """获取用户的 PPT 列表"""
    service = get_ppt_service(db)
    ppts = await service.get_by_user(current_user.id, skip, limit, status)
    return ppts


@router.get(
    "/{ppt_id}",
    response_model=PresentationDetailResponse,
    summary="获取 PPT 详情"
)
async def get_ppt(
    ppt_id: UUID,
    current_user: User = Depends(get_current_user),
    db = Depends(get_db)
):
    """获取 PPT 详情"""
    service = get_ppt_service(db)
    ppt = await service.get_by_id(ppt_id, current_user.id)
    
    if not ppt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "NOT_FOUND", "message": "PPT 不存在"}
        )
    
    return ppt


@router.patch(
    "/{ppt_id}",
    response_model=PresentationDetailResponse,
    summary="更新 PPT"
)
async def update_ppt(
    ppt_id: UUID,
    data: PresentationUpdate,
    current_user: User = Depends(get_current_user),
    db = Depends(get_db)
):
    """更新 PPT"""
    service = get_ppt_service(db)
    history_service = get_operation_history_service(db)
    
    # 获取原状态
    old_ppt = await service.get_by_id(ppt_id, current_user.id)
    if not old_ppt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "NOT_FOUND", "message": "PPT 不存在"}
        )
    
    # 更新
    ppt = await service.update(ppt_id, current_user.id, data)
    
    # 记录操作历史
    await history_service.record_operation(
        user_id=current_user.id,
        ppt_id=ppt_id,
        operation_type="update_ppt",
        description=f"更新 PPT: {data.title or '属性更新'}",
        before_state={"title": old_ppt.title, "slides": old_ppt.slides},
        after_state={"title": ppt.title, "slides": ppt.slides}
    )
    
    return ppt


@router.delete(
    "/{ppt_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="删除 PPT"
)
async def delete_ppt(
    ppt_id: UUID,
    current_user: User = Depends(get_current_user),
    db = Depends(get_db)
):
    """删除 PPT"""
    service = get_ppt_service(db)
    success = await service.delete(ppt_id, current_user.id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "NOT_FOUND", "message": "PPT 不存在"}
        )
    
    return None


# ==================== 单页编辑 ====================

@router.get(
    "/{ppt_id}/slides/{slide_id}",
    summary="获取单页幻灯片"
)
async def get_slide(
    ppt_id: UUID,
    slide_id: str,
    current_user: User = Depends(get_current_user),
    db = Depends(get_db)
):
    """获取单页详情"""
    service = get_ppt_service(db)
    slide = await service.get_slide(ppt_id, slide_id, current_user.id)
    
    if not slide:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "NOT_FOUND", "message": "幻灯片不存在"}
        )
    
    return slide


@router.patch(
    "/{ppt_id}/slides/{slide_id}",
    summary="更新单页（部分更新）"
)
async def update_slide(
    ppt_id: UUID,
    slide_id: str,
    data: SlideUpdate,
    current_user: User = Depends(get_current_user),
    db = Depends(get_db)
):
    """更新单页幻灯片（增量更新）"""
    service = get_ppt_service(db)
    history_service = get_operation_history_service(db)
    
    # 获取原状态
    old_slide = await service.get_slide(ppt_id, slide_id, current_user.id)
    if not old_slide:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "NOT_FOUND", "message": "幻灯片不存在"}
        )
    
    # 更新
    slide = await service.update_slide(ppt_id, slide_id, current_user.id, data)
    
    # 记录操作历史
    await history_service.record_operation(
        user_id=current_user.id,
        ppt_id=ppt_id,
        operation_type="edit_slide",
        slide_id=slide_id,
        description=f"编辑第 {slide_id} 页",
        before_state=old_slide,
        after_state=slide
    )
    
    return slide


@router.post(
    "/{ppt_id}/slides",
    summary="添加幻灯片"
)
async def add_slide(
    ppt_id: UUID,
    data: SlideCreate,
    current_user: User = Depends(get_current_user),
    db = Depends(get_db)
):
    """添加新幻灯片"""
    service = get_ppt_service(db)
    history_service = get_operation_history_service(db)
    
    slide_dict = data.model_dump()
    
    ppt = await service.add_slide(
        ppt_id, current_user.id, slide_dict, data.position
    )
    
    if not ppt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "NOT_FOUND", "message": "PPT 不存在"}
        )
    
    # 记录操作历史
    await history_service.record_operation(
        user_id=current_user.id,
        ppt_id=ppt_id,
        operation_type="add_slide",
        description=f"添加第 {len(ppt.slides)} 页",
        before_state=None,
        after_state=slide_dict
    )
    
    return ppt


@router.delete(
    "/{ppt_id}/slides/{slide_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="删除幻灯片"
)
async def delete_slide(
    ppt_id: UUID,
    slide_id: str,
    current_user: User = Depends(get_current_user),
    db = Depends(get_db)
):
    """删除幻灯片"""
    service = get_ppt_service(db)
    history_service = get_operation_history_service(db)
    
    # 获取原状态
    old_slide = await service.get_slide(ppt_id, slide_id, current_user.id)
    
    success = await service.delete_slide(ppt_id, slide_id, current_user.id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "NOT_FOUND", "message": "幻灯片不存在"}
        )
    
    # 记录操作历史
    await history_service.record_operation(
        user_id=current_user.id,
        ppt_id=ppt_id,
        operation_type="delete_slide",
        slide_id=slide_id,
        description="删除幻灯片",
        before_state=old_slide,
        after_state=None
    )
    
    return None


# ==================== 撤销/重做 ====================

@router.post(
    "/{ppt_id}/undo",
    summary="撤销操作"
)
async def undo_operation(
    ppt_id: UUID,
    current_user: User = Depends(get_current_user),
    db = Depends(get_db)
):
    """撤销上一步操作"""
    service = get_operation_history_service(db)
    
    success, description, state = await service.undo(
        ppt_id, current_user.id
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "CANNOT_UNDO", "message": description}
        )
    
    return {
        "success": True,
        "description": description,
        "state": state
    }


@router.post(
    "/{ppt_id}/redo",
    summary="重做操作"
)
async def redo_operation(
    ppt_id: UUID,
    current_user: User = Depends(get_current_user),
    db = Depends(get_db)
):
    """重做被撤销的操作"""
    service = get_operation_history_service(db)
    
    success, description, state = await service.redo(
        ppt_id, current_user.id
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "CANNOT_REDO", "message": description}
        )
    
    return {
        "success": True,
        "description": description,
        "state": state
    }


@router.get(
    "/{ppt_id}/history",
    summary="获取操作历史"
)
async def get_operation_history(
    ppt_id: UUID,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db = Depends(get_db)
):
    """获取操作历史列表"""
    service = get_operation_history_service(db)
    history = await service.get_history(ppt_id, current_user.id, limit)
    
    return history
