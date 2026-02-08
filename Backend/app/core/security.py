"""
安全工具模块
包含密码加密、JWT 处理等
"""

from datetime import datetime, timedelta, timezone
import logging
from typing import Optional, Tuple

try:
    from jose import JWTError, jwt
except ImportError:
    raise ImportError(
        "python-jose is not installed. Please install it using: pip install python-jose[cryptography]"
    )

try:
    from passlib.context import CryptContext
except ImportError:
    raise ImportError(
        "passlib is not installed. Please install it using: pip install passlib[bcrypt]"
    )

from app.config import settings

# 密码加密上下文
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__truncate_error=False
)

logger = logging.getLogger(__name__)


def _password_byte_len(password: str) -> int:
    return len(password.encode("utf-8"))


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    验证密码
    
    Args:
        plain_password: 明文密码
        hashed_password: 哈希后的密码
        
    Returns:
        是否匹配
    """
    byte_len = _password_byte_len(plain_password)
    if byte_len > 72:
        return False

    try:
        return pwd_context.verify(plain_password, hashed_password)
    except ValueError:
        logger.exception("Password verify failed: byte_len=%s", byte_len)
        return False


def get_password_hash(password: str) -> str:
    """
    获取密码哈希
    
    Args:
        password: 明文密码
        
    Returns:
        bcrypt 哈希值
    """
    byte_len = _password_byte_len(password)
    if byte_len > 72:
        raise ValueError("password too long")

    try:
        return pwd_context.hash(password)
    except ValueError:
        logger.exception("Password hash failed: byte_len=%s", byte_len)
        raise


def create_access_token(
    user_id: str,
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    创建访问令牌（JWT）
    
    Args:
        user_id: 用户 ID
        expires_delta: 过期时间，默认30分钟
        
    Returns:
        JWT 字符串
    """
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
        )
    
    to_encode = {
        "sub": str(user_id),
        "exp": expire,
        "type": "access",
        "iat": datetime.now(timezone.utc)
    }
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt


def create_refresh_token(user_id: str) -> str:
    """
    创建刷新令牌
    
    Args:
        user_id: 用户 ID
        
    Returns:
        JWT 字符串
    """
    expire = datetime.now(timezone.utc) + timedelta(
        days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS
    )
    
    to_encode = {
        "sub": str(user_id),
        "exp": expire,
        "type": "refresh",
        "iat": datetime.now(timezone.utc)
    }
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt


def decode_token(token: str, expected_type: str = "access") -> Tuple[Optional[str], Optional[str]]:
    """
    解码并验证 JWT
    
    Args:
        token: JWT 字符串
        expected_type: 期望的 token 类型 ("access" 或 "refresh")
        
    Returns:
        (user_id, error_message)
        如果验证失败，user_id 为 None，error_message 包含错误信息
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        user_id: str = payload.get("sub")
        token_type: str = payload.get("type", "access")
        
        if user_id is None:
            return None, "Invalid token: missing user ID"
        
        # 验证 token 类型
        if token_type != expected_type:
            return None, f"Invalid token type: expected {expected_type}, got {token_type}"
            
        return user_id, None
        
    except JWTError:
        return None, "Invalid token"
