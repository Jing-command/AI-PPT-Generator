"""
图片生成测试 - 使用 gemini-3-pro-image-preview 模型

注意: 这个测试专门测试图片生成，需要一个能访问 gemini-3-pro-image-preview 的 API Key
如果你有单独的"图片 Key"，请在这里使用
"""
import asyncio
from app.services.ai_provider import YunwuProvider

async def test_image_generation():
    """测试图片生成功能"""
    
    print("=" * 60)
    print("图片生成测试")
    print("=" * 60)
    print("\n模型: gemini-3-pro-image-preview")
    print("API: Gemini原生API")
    print("端点: /v1beta/models/gemini-3-pro-image-preview:generateContent")
    print()
    
    # 图片生成 Key（可能和文本 Key 不同）
    image_api_key = input("请输入图片生成 API Key (gemini-3-pro-image-preview): ").strip()
    
    # 创建Provider - 只需要图片 key
    # 由于只测试图片，我们传相同的 key 给两个参数
    provider = YunwuProvider(
        api_key=image_api_key,      # 文本 key（这里也用图片 key）
        image_api_key=image_api_key # 图片 key
    )
    
    print(f"\n确认配置:")
    print(f"  图片模型: {provider.IMAGE_MODEL}")
    print(f"  API Key: {image_api_key[:15]}...")
    
    print("\n" + "=" * 60)
    print("开始测试图片生成")
    print("=" * 60)
    
    test_prompt = "Professional business illustration of AI technology, modern flat design, blue gradient background with geometric shapes, clean corporate aesthetic, suitable for presentation cover"
    
    print(f"\n提示词: {test_prompt[:60]}...")
    print("\n生成中... (通常需要 30-120 秒)")
    
    try:
        result = await provider.generate_image(test_prompt)
        
        if result:
            print(f"\n✓ 图片生成成功!")
            print(f"  数据长度: {len(result)} 字符")
            
            if result.startswith('data:'):
                # 解析并保存图片
                import base64
                header, base64_data = result.split(',', 1)
                mime_type = header.split(':')[1].split(';')[0]
                print(f"  图片格式: {mime_type}")
                
                image_data = base64.b64decode(base64_data)
                output_file = 'test_generated_image.png'
                with open(output_file, 'wb') as f:
                    f.write(image_data)
                print(f"  已保存到: {output_file}")
                print(f"  文件大小: {len(image_data)} bytes")
            else:
                print(f"  结果: {result[:100]}...")
        else:
            print(f"\n✗ 图片生成失败: 返回空结果")
            print("  可能原因:")
            print("  - API Key 没有 gemini-3-pro-image-preview 访问权限")
            print("  - 账户余额不足")
            print("  - 模型暂时不可用")
            
    except Exception as e:
        print(f"\n✗ 发生错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_image_generation())
