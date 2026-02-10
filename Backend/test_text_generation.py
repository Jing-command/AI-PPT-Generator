"""
文本生成测试 - 使用 gemini-3-flash-preview 模型

注意: 这个测试专门测试文本生成，需要一个能访问 gemini-3-flash-preview 的 API Key
如果你有单独的"文字 Key"，请在这里使用
"""
import asyncio
from app.services.ai_provider import YunwuProvider

async def test_text_generation():
    """测试文本生成功能"""
    
    print("=" * 60)
    print("文本生成测试")
    print("=" * 60)
    print("\n模型: gemini-3-flash-preview")
    print("API: OpenAI兼容API")
    print("端点: /v1/chat/completions")
    print()
    
    # 文本生成 Key（可能和图片 Key 不同）
    text_api_key = input("请输入文本生成 API Key (gemini-3-flash-preview): ").strip()
    
    # 创建Provider - 只需要文本 key
    provider = YunwuProvider(
        api_key=text_api_key,       # 文本 key
        image_api_key=text_api_key  # 图片 key（这里也用文本 key，因为不会用到）
    )
    
    print(f"\n确认配置:")
    print(f"  文本模型: {provider.TEXT_MODEL}")
    print(f"  API Key: {text_api_key[:15]}...")
    
    print("\n" + "=" * 60)
    print("测试 1: 生成PPT大纲")
    print("=" * 60)
    
    try:
        outline = await provider.generate_ppt_outline(
            prompt="人工智能在医疗行业的应用",
            num_slides=3,
            language="zh",
            style="business"
        )
        
        print(f"\n✓ 大纲生成成功")
        print(f"  标题: {outline.get('title')}")
        print(f"  幻灯片数: {len(outline.get('slides', []))}")
        
        # 检查 image_prompt
        for i, slide in enumerate(outline.get('slides', [])):
            has_prompt = 'image_prompt' in slide
            print(f"  Slide {i+1} ({slide.get('type')}): image_prompt = {has_prompt}")
            
    except Exception as e:
        print(f"\n✗ 失败: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("测试 2: 生成幻灯片内容")
    print("=" * 60)
    
    try:
        content = await provider.generate_slide_content(
            title="AI诊断技术",
            slide_type="content",
            context="医疗AI应用场景",
            language="zh"
        )
        print(f"\n✓ 内容生成成功")
        print(f"  预览: {content[:100]}...")
    except Exception as e:
        print(f"\n✗ 失败: {e}")
    
    print("\n" + "=" * 60)
    print("测试 3: 生成图片提示词")
    print("=" * 60)
    
    try:
        image_prompt = await provider.generate_image_prompt(
            slide_content="AI医疗诊断技术，提高诊断准确率"
        )
        print(f"\n✓ 提示词生成成功")
        print(f"  结果: {image_prompt}")
    except Exception as e:
        print(f"\n✗ 失败: {e}")
    
    print("\n" + "=" * 60)
    print("文本生成测试完成")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_text_generation())
