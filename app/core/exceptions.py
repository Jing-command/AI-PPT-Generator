"""
自定义异常类
统一错误处理
"""

from fastapi import HTTPException, status


class BaseAPIException(HTTPException):
    """
    API 异常基类
    
    Attributes:
        status_code: HTTP 状态码
        code: 业务错误代码
        message: 错误信息
        details: 详细错误信息（可选）
    """
    
    def __init__(
        self,
        status_code: int,
        code: str,
        message: str,
        details: dict = None
    ):
        super().__init__(status_code=status_code, detail=message)
        self.code = code
        self.message = message
        self.details = details


class AuthenticationError(BaseAPIException):
    """认证错误（401）"""
    
    def __init__(self, message: str = "认证失败", details: dict = None):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            code="AUTHENTICATION_ERROR",
            message=message,
            details=details
        )


class PermissionDenied(BaseAPIException):
    """权限不足（403）"""
    
    def __init__(self, message: str = "权限不足", details: dict = None):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            code="PERMISSION_DENIED",
            message=message,
            details=details
        )


class NotFoundError(BaseAPIException):
    """资源不存在（404）"""
    
    def __init__(self, resource: str = "资源", details: dict = None):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            code="NOT_FOUND",
            message=f"{resource}不存在",
            details=details
        )


class ValidationError(BaseAPIException):
    """参数验证错误（422）"""
    
    def __init__(self, message: str = "参数验证失败", details: dict = None):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            code="VALIDATION_ERROR",
            message=message,
            details=details
        )


class ConflictError(BaseAPIException):
    """资源冲突（409）"""
    
    def __init__(self, message: str = "资源已存在", details: dict = None):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            code="CONFLICT_ERROR",
            message=message,
            details=details
        )


class RateLimitError(BaseAPIException):
    """请求频率限制（429）"""
    
    def __init__(self, message: str = "请求过于频繁", details: dict = None):
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            code="RATE_LIMIT_EXCEEDED",
            message=message,
            details=details
        )


class InternalError(BaseAPIException):
    """服务器内部错误（500）"""
    
    def __init__(self, message: str = "服务器内部错误", details: dict = None):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            code="INTERNAL_ERROR",
            message=message,
            details=details
        )
