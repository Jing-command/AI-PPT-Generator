"""
PPT 生成路由
处理 PPT 生成任务
"""

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import get_current_user
from app.database import get_db
from app.models.user import User
from app.schemas.presentation import (
    GenerateRequest,
    GenerateResponse,
    GenerateStatusResponse,
)
from app.services.ppt_generation_service import get_ppt_generation_service
from app.tasks.generation_tasks import process_generation_task

router = APIRouter(prefix="/ppt/generate", tags=["PPT 生成"])


@router.post(
    "",
    response_model=GenerateResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="提交 PPT 生成任务",
    description="异步生成 PPT，返回任务 ID"
)
async def submit_generation_task(
    request: GenerateRequest,
    current_user: User = Depends(get_current_user),
    db = Depends(get_db)
) -> GenerateResponse:
    """
    提交 PPT 生成任务
    
    任务将异步执行，使用轮询或 WebSocket 获取结果
    """
    service = get_ppt_generation_service(db)
    
    try:
        task = await service.create_task(current_user.id, request)
        
        # 启动异步生成任务
        process_generation_task.delay(str(task.id))
        
        return GenerateResponse(
            task_id=task.id,
            status=task.status,
            estimated_time=60,  # 预估 60 秒
            message="任务已提交，正在生成中..."
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "NO_API_KEY",
                "message": str(e)
            }
        )


@router.get(
    "/{task_id}/status",
    response_model=GenerateStatusResponse,
    summary="查询生成任务状态",
    description="获取任务进度和结果"
)
async def get_generation_status(
    task_id: UUID,
    current_user: User = Depends(get_current_user),
    db = Depends(get_db)
) -> GenerateStatusResponse:
    """查询生成状态"""
    service = get_ppt_generation_service(db)
    task = await service.get_task(task_id, current_user.id)
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "NOT_FOUND",
                "message": "任务不存在"
            }
        )
    
    return task


@router.post(
    "/{task_id}/cancel",
    summary="取消生成任务",
    description="取消正在进行的生成任务"
)
async def cancel_generation_task(
    task_id: UUID,
    current_user: User = Depends(get_current_user),
    db = Depends(get_db)
):
    """取消任务"""
    service = get_ppt_generation_service(db)
    success = await service.cancel_task(task_id, current_user.id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "CANCEL_FAILED",
                "message": "任务无法取消（可能已完成或不存在）"
            }
        )
    
    return {"message": "任务已取消"}
