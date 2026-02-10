#!/usr/bin/env python3
"""
验证 Moonshot API Key 是否有效
"""

import asyncio
import sys
import os

# 添加 backend 到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from openai import AsyncOpenAI


async def test_moonshot_api_key(api_key: str) -> bool:
    """测试 Moonshot API Key"""
    
    client = AsyncOpenAI(
        api_key=api_key,
        base_url="https://api.moonshot.cn/v1"
    )
    
    try:
        # 发送一个简单的测试请求
        response = await client.chat.completions.create(
            model="kimi-k2.5",
            messages=[
                {"role": "user", "content": "Hello"}
            ],
            temperature=0.7,
            max_tokens=50
        )
        
        content = response.choices[0].message.content
        print("[OK] API Key is VALID!")
        print(f"Model response: {content[:50]}...")
        print(f"Model used: {response.model}")
        return True
        
    except Exception as e:
        print("[ERROR] API Key invalid or request failed")
        print(f"Error: {e}")
        
        # 详细错误分析
        error_str = str(e).lower()
        if "401" in error_str or "unauthorized" in error_str:
            print("\nPossible reasons:")
            print("  1. Wrong API Key format (check for extra spaces)")
            print("  2. API Key expired")
            print("  3. API Key not activated")
            print("  4. Using Kimi Code plugin key instead of Moonshot API Key")
            print("\nSolution:")
            print("  Visit https://platform.moonshot.cn/ to get API Key")
            print("  Key should start with 'sk-'")
        elif "429" in error_str or "rate limit" in error_str:
            print("\nRate limit exceeded, please try later")
        elif "connection" in error_str:
            print("\nNetwork connection issue")
            
        return False


def main():
    print("=" * 60)
    print("Moonshot API Key Validator")
    print("=" * 60)
    
    # 从命令行参数或交互式输入获取 Key
    if len(sys.argv) > 1:
        api_key = sys.argv[1]
    else:
        api_key = input("\nEnter your Moonshot API Key: ").strip()
    
    if not api_key:
        print("[ERROR] No API Key provided")
        return
    
    # 隐藏部分 Key 用于显示
    masked_key = api_key[:8] + "..." + api_key[-4:] if len(api_key) > 12 else "***"
    print(f"\nValidating Key: {masked_key}")
    print("-" * 60)
    
    # 运行测试
    result = asyncio.run(test_moonshot_api_key(api_key))
    
    print("-" * 60)
    if result:
        print("[SUCCESS] This Key works!")
    else:
        print("[FAILED] Please check your Key")
    print("=" * 60)


if __name__ == "__main__":
    main()
