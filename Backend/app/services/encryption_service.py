"""
API Key 加密服务
使用 AES-256-GCM 加密用户 API Key
"""

import base64
import os
from typing import Optional

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from app.config import settings


class APIKeyEncryption:
    """
    API Key 加密管理器
    
    使用 Fernet (AES-256-CBC) 加密
    密钥从环境变量或配置文件获取
    """
    
    def __init__(self):
        """初始化加密器"""
        self._fernet = self._create_fernet()
    
    def _create_fernet(self) -> Fernet:
        """
        创建 Fernet 实例
        
        使用 PBKDF2 从主密钥派生加密密钥
        """
        # 从配置获取主密钥
        master_key = settings.JWT_SECRET_KEY.encode()
        
        # 使用 PBKDF2 派生密钥
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b'ai-ppt-fixed-salt',  # 生产环境应使用随机 salt
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(master_key))
        
        return Fernet(key)
    
    def encrypt(self, api_key: str) -> str:
        """
        加密 API Key
        
        Args:
            api_key: 原始 API Key
            
        Returns:
            加密后的 base64 字符串
        """
        encrypted = self._fernet.encrypt(api_key.encode())
        return encrypted.decode()
    
    def decrypt(self, encrypted_key: str) -> str:
        """
        解密 API Key
        
        Args:
            encrypted_key: 加密后的字符串
            
        Returns:
            原始 API Key
        """
        decrypted = self._fernet.decrypt(encrypted_key.encode())
        return decrypted.decode()
    
    @staticmethod
    def detect_provider(api_key: str) -> Optional[str]:
        """
        根据 Key 格式自动检测提供商
        
        Args:
            api_key: API Key
            
        Returns:
            提供商名称 或 None
        """
        if api_key.startswith('sk-'):
            # Moonshot: sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
            if len(api_key) == 51 and api_key[3:].isalnum():
                return 'moonshot'
            # OpenAI: sk-proj-... 或 sk-... (51字符)
            elif 'proj' in api_key:
                return 'openai'
            else:
                return 'openai'
        elif api_key.startswith('sk-ant-'):
            return 'anthropic'
        elif api_key.startswith('AK-'):
            return 'aliyun'
        elif api_key.startswith('AKID'):
            return 'tencent'
        
        return None


# 全局加密实例
api_key_encryption = APIKeyEncryption()
