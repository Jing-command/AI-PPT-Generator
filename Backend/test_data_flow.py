"""
完整数据流测试 - 验证文本生成和图片生成的完整流程

说明: 本测试支持使用两个不同的 API Key
  - 文本生成 Key: 用于 gemini-3-flash-preview (只能生成文字)
  - 图片生成 Key: 用于 gemini-3-pro-image-preview (只能生成图片)
"""
import asyncio
import json
from app.services.ai_provider import YunwuProvider

async def test_data_flow():
    """测试完整的数据流: 大纲生成 -> 图片生成 -> 存储结构验证"""
    
    print("=" * 60)
    print("完整数据流测试")
    print("=" * 60)
    print("\n模型配置:")
    print("  文本生成: gemini-3-flash-preview (OpenAI兼容API)")
    print("  图片生成: gemini-3-pro-image-preview (Gemini原生API)")
    print()
    
    # 分别获取两个 API Key
    print("请输入两个 API Key (如果相同可以直接回车):")
    text_api_key = input("  文本生成 API Key (gemini-3-flash): ").strip()
    image_api_key = input("  图片生成 API Key (gemini-3-pro-image): ").strip()
    
    # 如果图片 key 为空，使用文本 key
    if not image_api_key:
        image_api_key = text_api_key
        print("\n使用同一个 API Key 进行文本和图片生成")
    else:
        print(f"\n使用不同的 API Key:")
        print(f"  文本 Key: {text_api_key[:15]}...")
        print(f"  图片 Key: {image_api_key[:15]}...")
    
    # 创建Provider，传入两个 key
    provider = YunwuProvider(
        api_key=text_api_key,
        image_api_key=image_api_key
    )
    
    print(f"\n确认配置:")
    print(f"  文本模型: {provider.TEXT_MODEL}")
    print(f"  图片模型: {provider.IMAGE_MODEL}")
    print(f"  使用不同Key: {text_api_key != image_api_key}")
    
    print("\n" + "=" * 60)
    print("Step 1: 生成PPT大纲 (gemini-3-flash-preview)")
    print("=" * 60)
    
    try:
        outline = await provider.generate_ppt_outline(
            prompt="人工智能在医疗行业的应用",
            num_slides=5,
            language="zh",
            style="business"
        )
        
        print(f"\n✓ 大纲生成成功")
        print(f"  标题: {outline.get('title')}")
        print(f"  幻灯片数量: {len(outline.get('slides', []))}")
        
        # 检查每个幻灯片的 image_prompt
        print("\n  各幻灯片详情:")
        slides_with_image_prompt = 0
        for i, slide in enumerate(outline.get('slides', [])):
            slide_type = slide.get('type', 'unknown')
            title = slide.get('title', '无标题')[:30]
            has_prompt = 'image_prompt' in slide
            
            if has_prompt:
                slides_with_image_prompt += 1
                status = "✓"
                prompt_preview = slide['image_prompt'][:50]
            else:
                status = "✗"
                prompt_preview = "无"
            
            print(f"    {status} Slide {i+1} [{slide_type:10}] {title}...")
            print(f"       image_prompt: {prompt_preview}...")
        
        print(f"\n  总结: {slides_with_image_prompt}/{len(outline.get('slides', []))} 个幻灯片有 image_prompt")
        
        if slides_with_image_prompt == 0:
            print("\n✗ 错误: 没有生成 image_prompt，请检查文本生成 Key 配置")
            return
        
    except Exception as e:
        print(f"\n✗ 大纲生成失败: {e}")
        import traceback
        traceback.print_exc()
        return
    
    print("\n" + "=" * 60)
    print("Step 2: 生成图片 (gemini-3-pro-image-preview)")
    print("=" * 60)
    
    slides = []
    image_count = 0
    max_images = 3  # 限制生成图片数量
    
    for i, slide_outline in enumerate(outline.get('slides', [])):
        slide_type = slide_outline.get("type", "content")
        title = slide_outline.get("title", "")
        
        # 构建 content 数据
        content_data = {"title": title}
        
        if slide_type == "title":
            content_data["subtitle"] = slide_outline.get("subtitle", "")
        elif slide_type == "section":
            content_data["description"] = slide_outline.get("description", "")
        elif slide_type == "two-column":
            left = slide_outline.get("left", {})
            right = slide_outline.get("right", {})
            content_data["left"] = {
                "title": left.get("title", ""),
                "points": left.get("points", [])
            }
            content_data["right"] = {
                "title": right.get("title", ""),
                "points": right.get("points", [])
            }
        elif slide_type == "timeline":
            content_data["events"] = slide_outline.get("events", [])
        elif slide_type == "process":
            content_data["steps"] = slide_outline.get("steps", [])
        elif slide_type == "grid":
            content_data["items"] = slide_outline.get("items", [])
        elif slide_type == "comparison":
            content_data["items"] = slide_outline.get("items", [])
        elif slide_type == "data":
            content_data["stats"] = slide_outline.get("stats", [])
        elif slide_type == "quote":
            content_data["quote"] = slide_outline.get("quote", "")
            content_data["author"] = slide_outline.get("author", "")
        elif slide_type == "image-text":
            content_data["text"] = slide_outline.get("text", "")
        else:  # content
            content_data["bullets"] = slide_outline.get("points", [])
            content_data["text"] = slide_outline.get("content", "")
        
        # 检查是否需要生成图片
        image_prompt = slide_outline.get("image_prompt")
        
        if image_prompt and image_count < max_images:
            print(f"\n  生成图片 for Slide {i+1} ({slide_type}): {title[:30]}...")
            print(f"    Prompt: {image_prompt[:60]}...")
            
            try:
                image_url = await provider.generate_image(image_prompt)
                
                if image_url:
                    content_data["image_url"] = image_url
                    image_count += 1
                    print(f"    ✓ 成功! ({len(image_url)} 字符)")
                    print(f"      URL前缀: {image_url[:50]}...")
                else:
                    print(f"    ✗ 失败: 返回空结果")
            except Exception as e:
                print(f"    ✗ 失败: {e}")
        elif image_prompt:
            print(f"\n  Slide {i+1}: 跳过图片生成 (已达到上限 {max_images})")
        
        # 构建幻灯片对象
        slide = {
            "id": f"slide-{i+1}",
            "type": slide_type,
            "content": content_data,
            "layout": {"type": slide_type},
            "style": {}
        }
        slides.append(slide)
    
    print(f"\n  图片生成总结: {image_count} 张图片已生成")
    
    print("\n" + "=" * 60)
    print("Step 3: 验证存储数据结构")
    print("=" * 60)
    
    # 模拟完整的PPT数据（与后端API返回格式一致）
    presentation = {
        "id": "test-ppt-id",
        "title": outline.get("title"),
        "slides": slides,
        "status": "draft"
    }
    
    print("\n  各幻灯片 image_url 状态:")
    for i, slide in enumerate(presentation['slides']):
        has_image = 'image_url' in slide['content']
        img_status = "✓ 有图片" if has_image else "✗ 无图片"
        print(f"    Slide {i+1} ({slide['type']:10}): {img_status}")
    
    # 保存完整数据到文件
    output_file = 'test_data_flow_result.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(presentation, f, ensure_ascii=False, indent=2)
    print(f"\n  完整数据已保存: {output_file}")
    
    print("\n" + "=" * 60)
    print("Step 4: 前端渲染模拟")
    print("=" * 60)
    
    print("\n  模拟前端渲染:")
    for i, slide in enumerate(presentation['slides']):
        content = slide['content']
        layout_type = slide['layout']['type']
        
        if layout_type == 'title':
            if content.get('image_url'):
                print(f"    Slide {i+1} (title): 使用背景图片 ✓")
            else:
                print(f"    Slide {i+1} (title): 无背景图片")
                
        elif layout_type == 'section':
            if content.get('image_url'):
                print(f"    Slide {i+1} (section): 使用背景图片 ✓")
            else:
                print(f"    Slide {i+1} (section): 无背景图片")
                
        elif layout_type == 'image-text':
            if content.get('image_url'):
                print(f"    Slide {i+1} (image-text): 显示图片 ✓")
            else:
                print(f"    Slide {i+1} (image-text): 显示占位符")
        else:
            print(f"    Slide {i+1} ({layout_type}): 无需图片")
    
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    print(f"\n  总幻灯片数: {len(slides)}")
    print(f"  有 image_prompt: {slides_with_image_prompt}")
    print(f"  成功生成图片: {image_count}")
    print(f"  使用文本 Key: {text_api_key[:15]}...")
    print(f"  使用图片 Key: {image_api_key[:15]}...")
    print(f"  Key是否相同: {text_api_key == image_api_key}")
    
    if image_count > 0:
        print("\n✓ 数据流测试通过! 图片已正确生成并关联到幻灯片。")
    else:
        print("\n✗ 数据流测试失败! 没有图片被生成。")
        print("  可能原因:")
        print("  - 图片 API Key 没有 gemini-3-pro-image-preview 访问权限")
        print("  - 账户余额不足")
        print("  - 模型暂时不可用")

if __name__ == "__main__":
    asyncio.run(test_data_flow())
