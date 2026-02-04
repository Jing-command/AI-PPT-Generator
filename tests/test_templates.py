"""
模板系统测试
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_list_templates(client: AsyncClient):
    """测试获取模板列表"""
    response = await client.get("/api/v1/templates")
    
    assert response.status_code == 200
    data = response.json()
    assert "templates" in data
    assert "total" in data


@pytest.mark.asyncio
async def test_get_template_categories(client: AsyncClient):
    """测试获取模板分类"""
    response = await client.get("/api/v1/templates/categories")
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0


@pytest.mark.asyncio
async def test_filter_templates_by_category(client: AsyncClient):
    """测试按分类筛选模板"""
    response = await client.get("/api/v1/templates?category=business")
    
    assert response.status_code == 200
    data = response.json()
    
    for template in data["templates"]:
        assert template["category"] == "business"
