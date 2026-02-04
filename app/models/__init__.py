"""
模型包初始化
导出所有模型
"""

from app.models.user import User

# 导出所有模型，方便 Alembic 导入
__all__ = ["User"]
