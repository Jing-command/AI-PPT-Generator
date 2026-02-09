"""测试更新 slide API"""
import asyncio
import httpx

async def test():
    async with httpx.AsyncClient() as client:
        # 先登录获取 token
        login_resp = await client.post(
            "http://localhost:8000/api/v1/auth/login",
            json={"email": "test@example.com", "password": "password123"}
        )
        print(f"Login status: {login_resp.status_code}")
        
        if login_resp.status_code == 200:
            token = login_resp.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}
            
            # 测试更新 slide
            update_resp = await client.patch(
                "http://localhost:8000/api/v1/ppt/74129c8e-a684-49cc-8e89-9ff1053f33ed/slides/35bff2b2-9136-45f6-9c2e-1c23933c1ff0",
                headers=headers,
                json={"content": {"title": "测试标题123"}}
            )
            print(f"Update status: {update_resp.status_code}")
            print(f"Response: {update_resp.text}")
        else:
            print(f"Login failed: {login_resp.text}")

if __name__ == "__main__":
    asyncio.run(test())
