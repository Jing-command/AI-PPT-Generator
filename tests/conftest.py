"""
测试配置和通用夹具
"""

import asyncio
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import AsyncClient

from app.database import close_db, init_db
from app.main import app


@pytest_asyncio.fixture(scope="session")
async def setup_db():
    """初始化测试数据库"""
    await init_db()
    yield
    await close_db()


@pytest_asyncio.fixture
async def client(setup_db) -> AsyncGenerator[AsyncClient, None]:
    """创建测试客户端"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest_asyncio.fixture
async def auth_headers(client: AsyncClient) -> dict:
    """获取认证头（创建用户并登录）"""
    import uuid
    
    # 注册
    email = f"test_{uuid.uuid4().hex[:8]}@example.com"
    password = "testpassword123"
    
    await client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": password,
            "name": "Test User"
        }
    )
    
    # 登录
    login_resp = await client.post(
        "/api/v1/auth/login",
        json={
            "email": email,
            "password": password
        }
    )
    
    token = login_resp.json()["access_token"]
    
    return {"Authorization": f"Bearer {token}"}
