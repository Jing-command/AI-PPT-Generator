"""修复数据库：添加 presentations 表的 description 列"""
import asyncio
import asyncpg

async def fix_database():
    # 数据库连接信息
    conn = await asyncpg.connect(
        host='localhost',
        port=5432,
        user='pptuser',
        password='pptpass',
        database='pptdb'
    )
    
    try:
        # 检查列是否已存在
        result = await conn.fetchval("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'presentations' AND column_name = 'description'
        """)
        
        if result:
            print("✅ description 列已存在")
        else:
            # 添加列
            await conn.execute("""
                ALTER TABLE presentations 
                ADD COLUMN description TEXT
            """)
            print("✅ 成功添加 description 列")
            
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(fix_database())
