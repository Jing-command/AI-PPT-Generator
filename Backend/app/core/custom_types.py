"""
数据库类型兼容性处理
为 SQLite 测试提供 UUID 兼容支持
"""

import uuid

from sqlalchemy import String, TypeDecorator


class GUID(TypeDecorator):
    """
    跨平台的 UUID 类型
    
    PostgreSQL: 使用 UUID 类型
    SQLite: 使用 String(36) 类型
    """
    
    impl = String(36)
    cache_ok = True
    
    def process_bind_param(self, value, dialect):
        """绑定参数时转换"""
        if value is None:
            return None
        if isinstance(value, uuid.UUID):
            return str(value)
        return str(uuid.UUID(value))
    
    def process_result_value(self, value, dialect):
        """结果返回时转换"""
        if value is None:
            return None
        return uuid.UUID(value)
