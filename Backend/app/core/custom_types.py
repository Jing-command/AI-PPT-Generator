"""
数据库类型兼容性处理
为 SQLite 测试提供 UUID 兼容支持
"""

import uuid

from sqlalchemy import JSON, String, TypeDecorator
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID


class GUID(TypeDecorator):
    """
    跨平台的 UUID 类型
    
    PostgreSQL: 使用 UUID 类型
    SQLite: 使用 String(36) 类型
    """
    
    impl = String(36)
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(PG_UUID(as_uuid=True))
        return dialect.type_descriptor(String(36))
    
    def process_bind_param(self, value, dialect):
        """绑定参数时转换"""
        if value is None:
            return None
        if isinstance(value, uuid.UUID):
            return str(value)
        if hasattr(value, "bytes"):
            return str(uuid.UUID(bytes=value.bytes))
        if hasattr(value, "hex"):
            return str(uuid.UUID(hex=value.hex))
        return str(uuid.UUID(str(value)))
    
    def process_result_value(self, value, dialect):
        """结果返回时转换"""
        if value is None:
            return None
        if isinstance(value, uuid.UUID):
            return value
        if hasattr(value, "bytes"):
            return uuid.UUID(bytes=value.bytes)
        if hasattr(value, "hex"):
            return uuid.UUID(hex=value.hex)
        return uuid.UUID(str(value))


class JSONType(TypeDecorator):
    """
    跨平台 JSON 类型

    PostgreSQL: 使用 JSONB
    SQLite: 使用 JSON
    """

    impl = JSON
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(JSONB)
        return dialect.type_descriptor(JSON)
