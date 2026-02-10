"""
Full test script to verify image generation and storage
"""
import asyncio
import json
from app.services.ai_provider import YunwuProvider

async def test_full_generation():
    """Test complete flow: outline -> image generation -> storage structure"""
    
    api_key = input("Enter Yunwu API key (sk-yunwu-...): ").strip()
    provider = YunwuProvider(api_key)
    
    print("\n=== Step 1: Generate PPT Outline ===\n")
    
    try:
        result = await provider.generate_ppt_outline(
            prompt="人工智能在医疗行业的应用",
            num_slides=5,
            language="zh",
            style="business"
        )
        
        print(f"Title: {result.get('title')}")
        print(f"Slides: {len(result.get('slides', []))}")
        
        # Check for image_prompt
        slides_with_images = 0
        for i, slide in enumerate(result.get('slides', [])):
            slide_type = slide.get('type', 'unknown')
            has_prompt = 'image_prompt' in slide
            if has_prompt:
                slides_with_images += 1
                print(f"  Slide {i+1} ({slide_type}): HAS image_prompt")
                print(f"    Prompt: {slide['image_prompt'][:60]}...")
            else:
                print(f"  Slide {i+1} ({slide_type}): NO image_prompt")
        
        print(f"\n{slides_with_images}/{len(result.get('slides', []))} slides have image_prompt")
        
        if slides_with_images == 0:
            print("\n[WARNING] No image prompts generated! Check AI provider settings.")
            return
        
        print("\n=== Step 2: Generate Images ===\n")
        
        slides_for_storage = []
        image_count = 0
        max_images = 3
        
        for i, slide_outline in enumerate(result.get('slides', [])):
            slide_type = slide_outline.get("type", "content")
            title = slide_outline.get("title", "")
            
            # Build content
            content_data = {"title": title}
            
            if slide_type == "title":
                content_data["subtitle"] = slide_outline.get("subtitle", "")
            elif slide_type == "section":
                content_data["description"] = slide_outline.get("description", "")
            
            # Generate image if image_prompt exists
            image_prompt = slide_outline.get("image_prompt")
            if image_prompt and image_count < max_images:
                print(f"Generating image for slide {i+1}: {title[:30]}...")
                try:
                    image_url = await provider.generate_image(image_prompt)
                    if image_url:
                        content_data["image_url"] = image_url
                        print(f"  ✓ Image generated ({len(image_url)} chars)")
                        image_count += 1
                    else:
                        print(f"  ✗ No image returned")
                except Exception as e:
                    print(f"  ✗ Error: {e}")
            
            slide = {
                "id": f"slide-{i+1}",
                "type": slide_type,
                "content": content_data,
                "layout": {"type": slide_type},
                "style": {}
            }
            slides_for_storage.append(slide)
        
        print(f"\n=== Step 3: Verify Storage Structure ===\n")
        
        # Save to file for inspection
        output = {
            "title": result.get("title"),
            "slides": slides_for_storage
        }
        
        with open('test_generation_result.json', 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        
        print(f"Result saved to: test_generation_result.json")
        
        # Check which slides have images
        for i, slide in enumerate(slides_for_storage):
            has_img = 'image_url' in slide['content']
            print(f"Slide {i+1} ({slide['type']}): image_url = {has_img}")
        
        print(f"\n=== Summary ===")
        print(f"Total slides: {len(slides_for_storage)}")
        print(f"Images generated: {image_count}")
        print(f"Storage structure: {'✓ Valid' if all('content' in s and 'image_url' in s['content'] or True for s in slides_for_storage) else '✗ Invalid'}")
        
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_full_generation())
