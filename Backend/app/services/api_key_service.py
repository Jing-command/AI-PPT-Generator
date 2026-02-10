"""
API Key 服务层
处理 API Key 的 CRUD 和验证
"""

from typing import List, Optional
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.api_key import UserAPIKey
from app.schemas.api_key import APIKeyCreate, APIKeyUpdate
from app.services.encryption_service import api_key_encryption


class APIKeyService:
    """
    API Key 服务类
    
    功能：
    - 添加/删除/更新 API Key
    - 验证 Key 有效性
    - 自动检测提供商
    - 管理默认 Key
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_by_id(self, key_id: UUID, user_id: UUID) -> Optional[UserAPIKey]:
        """
        获取指定用户的 API Key
        
        Args:
            key_id: Key ID
            user_id: 用户 ID（权限验证）
            
        Returns:
            UserAPIKey 或 None
        """
        result = await self.db.execute(
            select(UserAPIKey).where(
                UserAPIKey.id == key_id,
                UserAPIKey.user_id == user_id
            )
        )
        return result.scalar_one_or_none()
    
    async def get_by_user(self, user_id: UUID) -> List[UserAPIKey]:
        """
        获取用户的所有 API Key（脱敏）
        
        Args:
            user_id: 用户 ID
            
        Returns:
            API Key 列表
        """
        result = await self.db.execute(
            select(UserAPIKey)
            .where(UserAPIKey.user_id == user_id)
            .order_by(UserAPIKey.created_at.desc())
        )
        return result.scalars().all()
    
    async def get_default_key(self, user_id: UUID, provider: str) -> Optional[UserAPIKey]:
        """
        获取用户的默认 Key，如果没有默认则返回该提供商的任意有效 Key
        
        Args:
            user_id: 用户 ID
            provider: 提供商
            
        Returns:
            默认的 API Key 或任意有效 Key
        """
        # 首先查找默认 Key
        result = await self.db.execute(
            select(UserAPIKey).where(
                UserAPIKey.user_id == user_id,
                UserAPIKey.provider == provider,
                UserAPIKey.is_default == True,
                UserAPIKey.status == "active"
            ).limit(1)
        )
        key = result.scalar_one_or_none()
        if key:
            return key
        
        # 如果没有默认 Key，返回该提供商的任意有效 Key
        result = await self.db.execute(
            select(UserAPIKey).where(
                UserAPIKey.user_id == user_id,
                UserAPIKey.provider == provider,
                UserAPIKey.status == "active"
            ).limit(1)
        )
        return result.scalar_one_or_none()
    
    async def get_image_key(self, user_id: UUID, provider: str) -> Optional[UserAPIKey]:
        """
        获取用户用于图片生成的 API Key
        
        策略：
        1. 首先查找 provider 为 "{provider}-image" 的专用 Key
        2. 如果没有，使用默认的 provider Key
        
        Args:
            user_id: 用户 ID
            provider: 基础提供商（如 "yunwu"）
            
        Returns:
            图片生成的 API Key 或默认 Key
        """
        # 首先查找专用的图片生成 Key
        image_provider = f"{provider}-image"
        result = await self.db.execute(
            select(UserAPIKey).where(
                UserAPIKey.user_id == user_id,
                UserAPIKey.provider == image_provider,
                UserAPIKey.status == "active"
            ).limit(1)
        )
        key = result.scalar_one_or_none()
        if key:
            print(f"[APIKeyService] Found dedicated image key for provider: {provider}")
            return key
        
        # 如果没有专用 Key，返回默认 Key
        print(f"[APIKeyService] No dedicated image key found, using default key")
        return await self.get_default_key(user_id, provider)
    
    async def get_any_active_key(self, user_id: UUID) -> Optional[UserAPIKey]:
        """
        获取用户的任意有效 API Key（优先默认，其次按优先级顺序）
        
        优先级：默认 Key > openai > moonshot > deepseek > anthropic > 其他
        
        Args:
            user_id: 用户 ID
            
        Returns:
            任意有效的 API Key
        """
        # 首先查找任意默认 Key
        result = await self.db.execute(
            select(UserAPIKey).where(
                UserAPIKey.user_id == user_id,
                UserAPIKey.is_default == True,
                UserAPIKey.status == "active"
            ).limit(1)
        )
        key = result.scalar_one_or_none()
        if key:
            return key
        
        # 按优先级查找
        priority_order = ["openai", "moonshot", "deepseek", "anthropic", "aliyun", "tencent", "azure", "yunwu"]
        
        for provider in priority_order:
            result = await self.db.execute(
                select(UserAPIKey).where(
                    UserAPIKey.user_id == user_id,
                    UserAPIKey.provider == provider,
                    UserAPIKey.status == "active"
                ).limit(1)
            )
            key = result.scalar_one_or_none()
            if key:
                return key
        
        # 最后尝试任意 active key（排除图片专用key）
        from sqlalchemy import not_
        result = await self.db.execute(
            select(UserAPIKey).where(
                UserAPIKey.user_id == user_id,
                UserAPIKey.status == "active",
                not_(UserAPIKey.provider.like('%-image'))
            ).limit(1)
        )
        return result.scalar_one_or_none()
    
    async def create(self, user_id: UUID, data: APIKeyCreate) -> UserAPIKey:
        """
        创建新的 API Key
        
        Args:
            user_id: 用户 ID
            data: API Key 数据
            
        Returns:
            创建的 API Key
        """
        # 自动检测提供商（如果用户未指定或指定为 auto）
        provider = data.provider
        if provider == 'auto':
            detected = api_key_encryption.detect_provider(data.api_key)
            if detected:
                provider = detected
        
        # 加密 Key
        encrypted_key = api_key_encryption.encrypt(data.api_key)
        
        # 如果设为默认，先取消其他默认
        if data.is_default:
            await self.db.execute(
                update(UserAPIKey)
                .where(
                    UserAPIKey.user_id == user_id,
                    UserAPIKey.provider == provider
                )
                .values(is_default=False)
            )
        
        # 创建记录
        db_key = UserAPIKey(
            user_id=user_id,
            provider=provider,
            api_key_encrypted=encrypted_key,
            name=data.name,
            is_default=data.is_default,
            status="active"
        )
        
        self.db.add(db_key)
        await self.db.commit()
        await self.db.refresh(db_key)
        
        return db_key
    
    async def update(
        self,
        key_id: UUID,
        user_id: UUID,
        data: APIKeyUpdate
    ) -> Optional[UserAPIKey]:
        """
        更新 API Key
        
        Args:
            key_id: Key ID
            user_id: 用户 ID
            data: 更新数据
            
        Returns:
            更新后的 API Key
        """
        key = await self.get_by_id(key_id, user_id)
        if not key:
            return None
        
        # 如果设为默认，先取消其他
        if data.is_default and not key.is_default:
            await self.db.execute(
                update(UserAPIKey)
                .where(
                    UserAPIKey.user_id == user_id,
                    UserAPIKey.provider == key.provider,
                    UserAPIKey.id != key_id
                )
                .values(is_default=False)
            )
        
        # 更新字段
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(key, field, value)
        
        await self.db.commit()
        await self.db.refresh(key)
        
        return key
    
    async def delete(self, key_id: UUID, user_id: UUID) -> bool:
        """
        删除 API Key
        
        Args:
            key_id: Key ID
            user_id: 用户 ID
            
        Returns:
            是否成功删除
        """
        key = await self.get_by_id(key_id, user_id)
        if not key:
            return False
        
        await self.db.delete(key)
        await self.db.commit()
        
        return True
    
    async def verify_key(self, key_id: UUID, user_id: UUID) -> bool:
        """
        验证 API Key 是否有效
        
        实际验证需要调用对应提供商的 API
        这里只做简单的解密测试
        
        Args:
            key_id: Key ID
            user_id: 用户 ID
            
        Returns:
            是否有效
        """
        key = await self.get_by_id(key_id, user_id)
        if not key:
            return False
        
        try:
            # 尝试解密
            api_key_encryption.decrypt(key.api_key_encrypted)
            return True
        except Exception:
            return False


# 便捷函数
def get_api_key_service(db: AsyncSession) -> APIKeyService:
    """获取 API Key 服务实例"""
    return APIKeyService(db)
