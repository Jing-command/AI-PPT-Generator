"""
Test script to verify image_prompt generation
"""
import asyncio
import json
from app.services.ai_provider import YunwuProvider

async def test_outline_generation():
    """Test that outline includes image_prompt"""
    
    # Use a test API key or get from environment
    api_key = input("Enter Yunwu API key (sk-yunwu-...): ").strip()
    
    provider = YunwuProvider(api_key)
    
    print("\n=== Testing PPT Outline Generation ===\n")
    
    try:
        result = await provider.generate_ppt_outline(
            prompt="人工智能在医疗行业的应用",
            num_slides=5,
            language="zh",
            style="business"
        )
        
        print(f"\n✅ Outline generated successfully!")
        print(f"Title: {result.get('title')}")
        print(f"Slides count: {len(result.get('slides', []))}")
        
        # Check for image_prompt in each slide
        print("\n=== Image Prompt Analysis ===")
        for i, slide in enumerate(result.get('slides', [])):
            slide_type = slide.get('type', 'unknown')
            title = slide.get('title', 'No title')[:30]
            has_image_prompt = 'image_prompt' in slide
            
            status = "✅" if has_image_prompt else "❌"
            print(f"{status} Slide {i+1} ({slide_type}): {title}...")
            
            if has_image_prompt:
                prompt = slide['image_prompt']
                print(f"   Image prompt: {prompt[:80]}...")
        
        # Summary
        slides_with_images = sum(1 for s in result.get('slides', []) if s.get('image_prompt'))
        total_slides = len(result.get('slides', []))
        print(f"\n=== Summary ===")
        print(f"Slides with image_prompt: {slides_with_images}/{total_slides}")
        
        # Save full result for inspection
        with open('test_outline_result.json', 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"\nFull result saved to: test_outline_result.json")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_outline_generation())
