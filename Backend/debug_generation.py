"""
Debug script to trace image generation flow
"""
import asyncio
import json
from app.services.ai_provider import YunwuProvider

async def debug_generation():
    api_key = input("Enter Yunwu API key: ").strip()
    provider = YunwuProvider(api_key)
    
    print("\n=== Testing Outline Generation ===\n")
    
    # Mock the generate_ppt_outline to see raw output
    import app.services.ai_provider as ai_module
    original_generate = provider.generate_ppt_outline
    
    async def debug_generate(prompt, num_slides, language, style):
        result = await original_generate(prompt, num_slides, language, style)
        
        # Print detailed info
        print(f"\n--- Generated Outline ---")
        print(f"Title: {result.get('title')}")
        print(f"Total slides: {len(result.get('slides', []))}")
        
        for i, slide in enumerate(result.get('slides', [])):
            print(f"\nSlide {i+1}:")
            print(f"  type: {slide.get('type')}")
            print(f"  title: {slide.get('title', 'N/A')[:50]}")
            print(f"  has image_prompt: {'image_prompt' in slide}")
            if 'image_prompt' in slide:
                print(f"  image_prompt: {slide['image_prompt'][:80]}...")
        
        return result
    
    provider.generate_ppt_outline = debug_generate
    
    # Test
    result = await provider.generate_ppt_outline(
        prompt="人工智能发展历史",
        num_slides=3,
        language="zh",
        style="business"
    )
    
    # Check image generation
    print("\n=== Testing Image Generation ===\n")
    
    for i, slide in enumerate(result.get('slides', [])):
        if slide.get('image_prompt'):
            prompt = slide['image_prompt']
            print(f"\nSlide {i+1} image prompt: {prompt[:60]}...")
            print("Generating image...")
            
            image_url = await provider.generate_image(prompt)
            if image_url:
                print(f"✓ Success! Image length: {len(image_url)}")
                print(f"  Preview: {image_url[:100]}...")
            else:
                print("✗ Failed - no image returned")
            break  # Just test one

if __name__ == "__main__":
    asyncio.run(debug_generation())
