"""
API Key 管理测试
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_add_api_key(client: AsyncClient, auth_headers):
    """测试添加 API Key"""
    response = await client.post(
        "/api/v1/api-keys",
        json={
            "name": "我的 OpenAI Key",
            "api_key": "sk-test123456789",
            "provider": "openai",
            "is_default": True
        },
        headers=auth_headers
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "我的 OpenAI Key"
    assert data["provider"] == "openai"
    assert "id" in data
    
    return data["id"]


@pytest.mark.asyncio
async def test_list_api_keys(client: AsyncClient, auth_headers):
    """测试获取 API Key 列表"""
    response = await client.get(
        "/api/v1/api-keys",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_delete_api_key(client: AsyncClient, auth_headers):
    """测试删除 API Key"""
    # 先添加
    add_resp = await client.post(
        "/api/v1/api-keys",
        json={
            "name": "待删除",
            "api_key": "sk-todelete",
            "provider": "openai"
        },
        headers=auth_headers
    )
    key_id = add_resp.json()["id"]
    
    # 删除
    response = await client.delete(
        f"/api/v1/api-keys/{key_id}",
        headers=auth_headers
    )
    
    assert response.status_code == 204
