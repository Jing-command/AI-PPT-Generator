"""
服务层包初始化
"""

from app.services.user_service import UserService, get_user_service

__all__ = ["UserService", "get_user_service"]
