"""测试数据库连接和查询"""
import asyncio
from app.database import get_db
from app.services.ppt_service import get_ppt_service
from uuid import UUID

async def test():
    async for db in get_db():
        service = get_ppt_service(db)
        
        # 查询 PPT
        ppt_id = UUID("74129c8e-a684-49cc-8e89-9ff1053f33ed")
        user_id = UUID("2258f59e-bd39-4357-b221-52bfa0288a30")  # 假设的用户ID
        
        ppt = await service.get_by_id(ppt_id, user_id)
        if ppt:
            print(f"PPT Title: {ppt.title}")
            print(f"Slides count: {len(ppt.slides)}")
            for i, slide in enumerate(ppt.slides):
                print(f"Slide {i}: {slide}")
        else:
            print("PPT not found")
        break

if __name__ == "__main__":
    asyncio.run(test())
