"""
Test with dual API keys - text and image generation
"""
import asyncio
from app.services.ai_provider import YunwuProvider

async def test_dual_api():
    print("=== Dual API Key Test ===\n")
    
    # Test 1: Same API key for both
    print("Test 1: Using same API key for both text and image")
    api_key = input("Enter your yunwu.ai API key: ").strip()
    
    provider = YunwuProvider(api_key=api_key)
    print(f"  Text API key: {provider.api_key[:20]}...")
    print(f"  Image API key: {provider.image_api_key[:20]}...")
    print(f"  Keys match: {provider.api_key == provider.image_api_key}")
    
    # Test outline generation
    print("\n  Testing text generation...")
    try:
        outline = await provider.generate_ppt_outline(
            prompt="AI technology",
            num_slides=2,
            language="en",
            style="business"
        )
        print(f"  ✓ Generated outline with {len(outline.get('slides', []))} slides")
    except Exception as e:
        print(f"  ✗ Failed: {e}")
    
    # Test image generation
    print("\n  Testing image generation...")
    try:
        image_url = await provider.generate_image(
            "Professional business illustration, modern flat design, blue gradient"
        )
        if image_url:
            print(f"  ✓ Generated image ({len(image_url)} chars)")
        else:
            print("  ✗ No image returned")
    except Exception as e:
        print(f"  ✗ Failed: {e}")
    
    # Test 2: Different API keys
    print("\n\nTest 2: Using different API keys")
    text_key = input("Enter API key for text (or press Enter to skip): ").strip()
    image_key = input("Enter API key for image (or press Enter to skip): ").strip()
    
    if text_key and image_key:
        provider2 = YunwuProvider(api_key=text_key, image_api_key=image_key)
        print(f"  Text API key: {provider2.api_key[:20]}...")
        print(f"  Image API key: {provider2.image_api_key[:20]}...")
        print(f"  Keys match: {provider2.api_key == provider2.image_api_key}")
        
        # Quick image test
        print("\n  Testing image generation with separate key...")
        try:
            image_url = await provider2.generate_image(
                "Professional business illustration, modern flat design, blue gradient"
            )
            if image_url:
                print(f"  ✓ Generated image ({len(image_url)} chars)")
            else:
                print("  ✗ No image returned")
        except Exception as e:
            print(f"  ✗ Failed: {e}")
    else:
        print("  Skipped (no keys provided)")
    
    print("\n=== Test Complete ===")

if __name__ == "__main__":
    asyncio.run(test_dual_api())
