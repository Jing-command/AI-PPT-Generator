"""
认证接口测试
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register_success(client: AsyncClient):
    """测试用户注册成功"""
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",
            "password": "securepassword123",
            "name": "测试用户"
        }
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["name"] == "测试用户"
    assert "id" in data


@pytest.mark.asyncio
async def test_register_duplicate_email(client: AsyncClient):
    """测试重复邮箱注册失败"""
    # 先注册一个用户
    await client.post(
        "/api/v1/auth/register",
        json={
            "email": "duplicate@example.com",
            "password": "password123"
        }
    )
    
    # 再次注册相同邮箱
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "duplicate@example.com",
            "password": "password123"
        }
    )
    
    assert response.status_code == 409
    assert response.json()["code"] == "EMAIL_EXISTS"


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient):
    """测试登录成功"""
    # 先注册
    await client.post(
        "/api/v1/auth/register",
        json={
            "email": "login@example.com",
            "password": "password123"
        }
    )
    
    # 登录
    response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": "login@example.com",
            "password": "password123"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_invalid_credentials(client: AsyncClient):
    """测试登录失败 - 错误密码"""
    response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": "nonexistent@example.com",
            "password": "wrongpassword"
        }
    )
    
    assert response.status_code == 401
    assert response.json()["code"] == "INVALID_CREDENTIALS"
