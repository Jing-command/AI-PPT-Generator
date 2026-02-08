"""
AI PPT Generator - FastAPI 主应用入口

大厂级代码规范：
- 清晰的模块划分
- 完善的错误处理
- 详细的 API 文档
- 性能监控
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from app.config import settings
from app.database import close_db, init_db
from app.routers import api_router

# 创建限流器
limiter = Limiter(key_func=get_remote_address)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    应用生命周期管理
    
    启动时：
        - 初始化数据库
        - 加载配置
    
    关闭时：
        - 关闭数据库连接
        - 清理资源
    """
    # 启动
    await init_db()
    print(f"🚀 {settings.APP_NAME} v{settings.APP_VERSION} 启动成功")
    
    yield
    
    # 关闭
    await close_db()
    print("👋 应用已关闭")


# 创建 FastAPI 应用
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="""
    AI 驱动的 PPT 生成服务
    
    ## 特性
    - 🤖 支持多种 AI 提供商（OpenAI, Claude, 国产模型）
    - 📝 对话式 PPT 编辑
    - 🎨 丰富的模板系统
    - 📤 多格式导出（PPTX, PDF）
    
    ## 认证
    所有需要认证的接口都需要在 Header 中传递：
    ```
    Authorization: Bearer {your_token}
    ```
    """,
    docs_url="/docs",  # Swagger UI
    redoc_url="/redoc",  # ReDoc 文档
    openapi_url="/openapi.json",
    lifespan=lifespan
)

# 注册限流器
app.state.limiter = limiter

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 限流异常处理
@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    """限流异常处理"""
    return JSONResponse(
        status_code=429,
        content={
            "code": "RATE_LIMIT_EXCEEDED",
            "message": "请求过于频繁，请稍后再试",
            "retry_after": 60
        }
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """统一 HTTP 异常返回格式"""
    if isinstance(exc.detail, dict):
        content = exc.detail
    else:
        content = {
            "code": "HTTP_ERROR",
            "message": exc.detail
        }

    return JSONResponse(status_code=exc.status_code, content=content)


# 全局异常处理
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """全局异常处理，返回统一的错误格式"""
    return JSONResponse(
        status_code=500,
        content={
            "code": "INTERNAL_ERROR",
            "message": "服务器内部错误",
            "details": {"error": str(exc)} if settings.DEBUG else None
        }
    )


# 健康检查
@app.get("/health", tags=["系统"], summary="健康检查")
async def health_check():
    """
    健康检查端点
    
    用于监控系统和服务发现
    """
    return {
        "status": "healthy",
        "version": settings.APP_VERSION,
        "service": settings.APP_NAME
    }


# 注册 API 路由
app.include_router(api_router)


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        workers=1 if settings.DEBUG else 4
    )
