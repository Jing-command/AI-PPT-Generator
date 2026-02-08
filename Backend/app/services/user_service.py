"""
用户服务层
处理用户相关的业务逻辑
"""

from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_password_hash, verify_password
from app.models.user import User
from app.schemas.user import UserCreate


class EmailExistsError(ValueError):
    """Raised when the email is already registered."""


class PasswordHashError(ValueError):
    """Raised when password hashing fails due to invalid input."""


class UserService:
    """
    用户服务类
    封装用户相关的数据库操作和业务逻辑
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_by_email(self, email: str) -> Optional[User]:
        """
        通过邮箱获取用户
        
        Args:
            email: 用户邮箱
            
        Returns:
            User 对象或 None
        """
        result = await self.db.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()
    
    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        """
        通过 ID 获取用户
        
        Args:
            user_id: 用户 UUID
            
        Returns:
            User 对象或 None
        """
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()
    
    async def create(self, user_data: UserCreate) -> User:
        """
        创建新用户
        
        Args:
            user_data: 用户创建数据
            
        Returns:
            创建的 User 对象
            
        Raises:
            ValueError: 如果邮箱已存在
        """
        # 检查邮箱是否已存在
        existing = await self.get_by_email(user_data.email)
        if existing:
            raise EmailExistsError(f"邮箱 {user_data.email} 已被注册")
        
        # 创建用户
        try:
            password_hash = get_password_hash(user_data.password)
        except ValueError as exc:
            raise PasswordHashError("密码格式不合法") from exc

        db_user = User(
            email=user_data.email,
            password_hash=password_hash,
            name=user_data.name
        )
        
        self.db.add(db_user)
        await self.db.commit()
        await self.db.refresh(db_user)
        
        return db_user
    
    async def authenticate(self, email: str, password: str) -> Optional[User]:
        """
        验证用户登录
        
        Args:
            email: 用户邮箱
            password: 明文密码
            
        Returns:
            User 对象（验证成功）或 None（验证失败）
        """
        user = await self.get_by_email(email)
        
        if not user:
            return None
        
        if not verify_password(password, user.password_hash):
            return None
        
        if not user.is_active:
            return None
        
        return user


# 便捷函数
def get_user_service(db: AsyncSession) -> UserService:
    """获取用户服务实例"""
    return UserService(db)
