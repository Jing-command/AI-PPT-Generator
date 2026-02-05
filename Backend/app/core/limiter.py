"""
限流中间件
基于 SlowAPI 的 API 限流
"""

from slowapi import Limiter
from slowapi.util import get_remote_address

# 创建限流器
# 使用客户端 IP 作为限流键
limiter = Limiter(key_func=get_remote_address)
