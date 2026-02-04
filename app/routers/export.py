"""
导出路由
处理 PPT 导出请求
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import get_current_user
from app.database import get_db
from app.models.user import User
from app.schemas.presentation import ExportRequest, ExportResponse
from app.services.export_task_service import get_export_task_service
from app.services.ppt_service import get_ppt_service
from app.tasks.export_tasks import process_export_task

router = APIRouter(prefix="/ppt/{ppt_id}/export", tags=["PPT 导出"])


@router.post(
    "",
    response_model=ExportResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="提交导出任务",
    description="异步导出 PPT 为指定格式"
)
async def submit_export_task(
    ppt_id: UUID,
    request: ExportRequest,
    current_user: User = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    提交导出任务
    
    支持格式：
    - pptx: PowerPoint 格式
    - pdf: PDF 格式
    - png/jpg: 图片格式（每页一张图）
    """
    # 检查 PPT 是否存在
    ppt_service = get_ppt_service(db)
    ppt = await ppt_service.get_by_id(ppt_id, current_user.id)
    
    if not ppt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "NOT_FOUND", "message": "PPT 不存在"}
        )
    
    # 创建导出任务
    task_service = get_export_task_service(db)
    task = await task_service.create_task(
        current_user.id,
        ppt_id,
        request.format,
        request.quality
    )
    
    # 启动异步导出任务
    process_export_task.delay(str(task.id))
    
    return ExportResponse(
        export_task_id=task.id,
        status=task.status,
        download_url=None,
        expires_at=None
    )


@router.get(
    "/{task_id}/status",
    response_model=ExportResponse,
    summary="查询导出状态"
)
async def get_export_status(
    ppt_id: UUID,
    task_id: UUID,
    current_user: User = Depends(get_current_user),
    db = Depends(get_db)
):
    """查询导出任务状态"""
    task_service = get_export_task_service(db)
    task = await task_service.get_task(task_id, current_user.id)
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "NOT_FOUND", "message": "导出任务不存在"}
        )
    
    # 构建下载 URL（如果已完成）
    download_url = None
    if task.status == "completed" and task.file_path:
        from app.services.export_service import get_export_service
        export_service = get_export_service()
        download_url = export_service.get_file_url(task.file_path)
    
    return ExportResponse(
        export_task_id=task.id,
        status=task.status,
        download_url=download_url,
        expires_at=task.expires_at
    )
