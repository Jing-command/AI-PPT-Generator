"""
PPT CRUD 测试
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_ppt(client: AsyncClient, auth_headers):
    """测试创建 PPT"""
    response = await client.post(
        "/api/v1/ppt",
        json={"title": "测试 PPT"},
        headers=auth_headers
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "测试 PPT"
    assert data["status"] == "draft"
    assert "id" in data
    
    return data["id"]


@pytest.mark.asyncio
async def test_get_ppt_list(client: AsyncClient, auth_headers):
    """测试获取 PPT 列表"""
    response = await client.get(
        "/api/v1/ppt",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_get_ppt_detail(client: AsyncClient, auth_headers):
    """测试获取 PPT 详情"""
    # 先创建
    create_resp = await client.post(
        "/api/v1/ppt",
        json={"title": "详情测试"},
        headers=auth_headers
    )
    ppt_id = create_resp.json()["id"]
    
    # 再获取
    response = await client.get(
        f"/api/v1/ppt/{ppt_id}",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "详情测试"


@pytest.mark.asyncio
async def test_update_ppt(client: AsyncClient, auth_headers):
    """测试更新 PPT"""
    # 创建
    create_resp = await client.post(
        "/api/v1/ppt",
        json={"title": "原标题"},
        headers=auth_headers
    )
    ppt_id = create_resp.json()["id"]
    
    # 更新
    response = await client.patch(
        f"/api/v1/ppt/{ppt_id}",
        json={"title": "新标题"},
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "新标题"


@pytest.mark.asyncio
async def test_delete_ppt(client: AsyncClient, auth_headers):
    """测试删除 PPT"""
    # 创建
    create_resp = await client.post(
        "/api/v1/ppt",
        json={"title": "待删除"},
        headers=auth_headers
    )
    ppt_id = create_resp.json()["id"]
    
    # 删除
    response = await client.delete(
        f"/api/v1/ppt/{ppt_id}",
        headers=auth_headers
    )
    
    assert response.status_code == 204
    
    # 确认已删除
    get_resp = await client.get(
        f"/api/v1/ppt/{ppt_id}",
        headers=auth_headers
    )
    assert get_resp.status_code == 404


# ==================== 单页编辑测试 ====================

@pytest.mark.asyncio
async def test_add_slide(client: AsyncClient, auth_headers):
    """测试添加幻灯片"""
    # 创建 PPT
    create_resp = await client.post(
        "/api/v1/ppt",
        json={"title": "单页测试"},
        headers=auth_headers
    )
    ppt_id = create_resp.json()["id"]
    
    # 添加幻灯片
    response = await client.post(
        f"/api/v1/ppt/{ppt_id}/slides",
        json={
            "type": "content",
            "content": {
                "title": "第一页",
                "text": "内容"
            }
        },
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data["slides"]) == 1


@pytest.mark.asyncio
async def test_undo_redo(client: AsyncClient, auth_headers):
    """测试撤销/重做"""
    # 创建 PPT
    create_resp = await client.post(
        "/api/v1/ppt",
        json={"title": "撤销测试"},
        headers=auth_headers
    )
    ppt_id = create_resp.json()["id"]
    
    # 修改标题（记录历史）
    await client.patch(
        f"/api/v1/ppt/{ppt_id}",
        json={"title": "修改后标题"},
        headers=auth_headers
    )
    
    # 撤销
    undo_resp = await client.post(
        f"/api/v1/ppt/{ppt_id}/undo",
        headers=auth_headers
    )
    
    assert undo_resp.status_code == 200
    undo_data = undo_resp.json()
    assert undo_data["success"] is True
    
    # 重做
    redo_resp = await client.post(
        f"/api/v1/ppt/{ppt_id}/redo",
        headers=auth_headers
    )
    
    assert redo_resp.status_code == 200
    redo_data = redo_resp.json()
    assert redo_data["success"] is True
