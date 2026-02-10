"""
AI Provider Service Wrapper
Unified interface for different AI services
"""

import json
import re
from abc import ABC, abstractmethod
from typing import AsyncGenerator, Dict, List, Optional

import httpx
from openai import AsyncOpenAI

from app.config import settings


def robust_json_parse(content: str) -> Dict:
    """
    Robust JSON parser
    
    Handles:
    1. Extract ```json code blocks
    2. Extract ``` code blocks  
    3. Fix unterminated strings
    4. Find first valid JSON object
    """
    # Try to extract code blocks
    if "```json" in content:
        match = re.search(r'```json\s*(.*?)\s*```', content, re.DOTALL)
        if match:
            content = match.group(1)
    elif "```" in content:
        match = re.search(r'```\s*(.*?)\s*```', content, re.DOTALL)
        if match:
            content = match.group(1)
    
    content = content.strip()
    
    # Try direct parse
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        pass
    
    # Try to find first JSON object
    try:
        match = re.search(r'\{.*\}', content, re.DOTALL)
        if match:
            return json.loads(match.group(0))
    except json.JSONDecodeError:
        pass
    
    # Try to fix truncated content
    fixed_content = _fix_json_content(content)
    try:
        return json.loads(fixed_content)
    except json.JSONDecodeError:
        pass
    
    raise ValueError(f"Cannot parse JSON content: {content[:200]}...")


def _fix_json_content(content: str) -> str:
    """Fix common JSON format errors"""
    # Remove comments
    content = re.sub(r'//.*?\n', '\n', content)
    content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
    
    # Track quotes and brackets
    in_string = False
    escape = False
    stack = []
    
    for i, char in enumerate(content):
        if escape:
            escape = False
            continue
        if char == '\\':
            escape = True
            continue
        if char == '"' and not in_string:
            in_string = True
            stack.append('"')
        elif char == '"' and in_string:
            in_string = False
            if stack and stack[-1] == '"':
                stack.pop()
    
    # Fix unterminated string
    if in_string:
        content += '"'
    
    # Fix unclosed brackets
    closing_map = {'{': '}', '[': ']', '(': ')', '"': '"'}
    while stack:
        opener = stack.pop()
        if opener in closing_map:
            content += closing_map[opener]
    
    # Remove trailing commas
    content = re.sub(r',\s*}', '}', content)
    content = re.sub(r',\s*]', ']', content)
    
    return content


class AIProviderBase(ABC):
    """AI Provider Base Class"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
    
    @abstractmethod
    async def generate_ppt_outline(
        self,
        prompt: str,
        num_slides: int,
        language: str = "zh",
        style: str = "business"
    ) -> Dict:
        """Generate PPT outline with rich content"""
        pass
    
    @abstractmethod
    async def generate_slide_content(
        self,
        title: str,
        slide_type: str,
        context: str,
        language: str = "zh"
    ) -> str:
        """Generate detailed slide content"""
        pass
    
    @abstractmethod
    async def generate_image_prompt(
        self,
        slide_content: str
    ) -> str:
        """Generate image prompt"""
        pass
    
    async def generate_image(self, prompt: str) -> str:
        """
        Generate image from prompt
        
        Default implementation returns empty string (not supported)
        Override in provider that supports image generation
        
        Returns:
            Base64 encoded image data or URL
        """
        return ""


class YunwuProvider(AIProviderBase):
    """
    Yunwu AI (yunwu.ai) Provider
    
    Uses two different models:
    1. gemini-3-flash-preview: Text generation (outline, content)
       - API: OpenAI-compatible /v1/chat/completions
    2. gemini-3-pro-image-preview: Image generation
       - API: Gemini native /v1beta/models/gemini-3-pro-image-preview:generateContent
    """
    
    # Model configurations
    TEXT_MODEL = "gemini-3-flash-preview"      # For text generation (outline)
    IMAGE_MODEL = "gemini-3-pro-image-preview"  # For image generation
    
    def __init__(self, api_key: str, image_api_key: str = None):
        """
        Args:
            api_key: API key for text generation (gemini-3-flash-preview)
            image_api_key: Optional separate API key for image generation.
                          If not provided, uses api_key for both.
        """
        super().__init__(api_key)
        
        # Client for text generation (OpenAI-compatible)
        self.client = AsyncOpenAI(
            api_key=api_key,
            base_url="https://yunwu.ai/v1"
        )
        self.model = self.TEXT_MODEL
        
        # API key for image generation (may be same or different)
        self.image_api_key = image_api_key or api_key
        
        print(f"[YunwuProvider] Text model: {self.TEXT_MODEL}")
        print(f"[YunwuProvider] Image model: {self.IMAGE_MODEL}")
        print(f"[YunwuProvider] Using {'same' if api_key == self.image_api_key else 'different'} API key for image generation")
    
    async def generate_ppt_outline(
        self,
        prompt: str,
        num_slides: int,
        language: str = "zh",
        style: str = "business"
    ) -> Dict:
        """Generate detailed PPT outline with rich content"""
        
        style_descriptions = {
            "business": "Professional business style, deep blue tones, clean and elegant",
            "education": "Educational style, green tones, fresh and clear",
            "creative": "Creative style, pink/purple tones, modern and lively",
            "minimal": "Minimalist style, black/white/gray tones, simple and elegant",
            "tech": "Tech style, cyan/blue tones, futuristic"
        }
        style_desc = style_descriptions.get(style, style_descriptions["business"])
        
        system_prompt = f"""You are a professional PPT content strategist. Generate content-rich, data-driven, well-structured presentations based on user topics.

**Critical Requirements**:
1. Generate {num_slides} slides
2. Use {language} language
3. Design style: {style_desc}
4. **IMPORTANT**: Each page must have complete, valuable content with data/cases/analysis, not just simple titles
5. **CRITICAL - MUST FOLLOW**: EVERY single slide MUST include an "image_prompt" field. This is REQUIRED for ALL slides without exception. The image_prompt should describe a professional business illustration suitable for that slide.

**Content Quality Standards**:
- Each page must have specific data, cases, analysis or insights
- Avoid "outline-style" short titles, provide expanded explanations
- Use realistic and credible data (placeholders like "about XX%", "over XXX million" are acceptable)
- Include industry trends, market size, competitive analysis
- Use structured expressions like comparison, causality, timeline appropriately

**Available Layout Types** (auto-selected based on content):
- "title": Cover - Main title + subtitle + speaker info
- "section": Section divider - Chapter title + brief description  
- "content": Content page - Detailed body with paragraph explanations
- "two-column": Two-column comparison - Left/right comparative analysis
- "timeline": Timeline - Development history, milestones
- "process": Process flow - Step-by-step explanation
- "grid": Grid - Features/capabilities showcase
- "comparison": Comparison table - Multi-dimensional data comparison
- "data": Data page - Big numbers + explanatory notes
- "quote": Quote page - Core viewpoint + source
- "image-text": Image-text mix - Case study display

**Image Generation Support (REQUIRED)**:
- You MUST add "image_prompt" field to the following slide types:
  * ALL "title" (cover) slides - MUST have image_prompt
  * ALL "section" (chapter divider) slides - MUST have image_prompt
  * At least 1-2 "content" or "image-text" slides - SHOULD have image_prompt
- Image prompts should be 30-80 words, describing professional business illustrations
- Include visual style, key elements, colors, and mood in the prompt
- Examples:
  * Title: "Professional business illustration of [TOPIC], modern flat design, blue gradient background with geometric shapes, clean corporate aesthetic, suitable for presentation cover, minimalist style"
  * Section: "Abstract geometric illustration representing [SECTION_TOPIC], gradient background from blue to purple, modern minimalist style, professional business aesthetic, subtle patterns"
  * Content: "Conceptual business illustration showing [CONCEPT], isometric design, soft shadows, corporate color palette, clean background, professional presentation style"

**Output Format (JSON)**:
{{
    "title": "Attractive, specific main PPT title",
    "summary": "Overall content summary, around 200 words",
    "theme": {{
        "name": "Theme name",
        "primary_color": "Primary color, e.g., #1a365d",
        "secondary_color": "Secondary color, e.g., #3182ce", 
        "background_color": "Background color, e.g., #ffffff",
        "text_color": "Text color, e.g., #1a202c",
        "accent_color": "Accent color, e.g., #ed8936",
        "font_family": "Font, e.g., Microsoft YaHei"
    }},
    "slides": [
        {{
            "type": "title",
            "title": "Specific attractive main title",
            "subtitle": "Subtitle explaining the core of the presentation",
            "image_prompt": "Professional business illustration related to the topic, modern flat design, gradient colors matching theme, clean corporate aesthetic, suitable for presentation cover"
        }},
        {{
            "type": "content",
            "title": "Specific chapter title",
            "content": "Detailed paragraph content including data, analysis, insights - not just simple titles. At least 100 words of complete explanation.",
            "bullets": [
                "Point 1: Detailed explanation with data support",
                "Point 2: Case analysis or comparison", 
                "Point 3: Trend prediction or recommendations"
            ],
            "data": {{"key": "Key metric", "value": "Specific value"}},
            "image_prompt": "Conceptual business illustration showing data analysis and insights, modern isometric design, charts and graphs visualization, blue color scheme, clean professional style"
        }},
        {{
            "type": "section",
            "title": "Chapter Transition Title",
            "description": "Brief description of this section's content",
            "image_prompt": "Abstract geometric illustration representing new section topic, gradient background, modern minimalist style, professional business aesthetic"
        }},
        {{
            "type": "two-column",
            "title": "Comparison analysis title",
            "left": {{
                "title": "Option A name",
                "points": [
                    "Advantage 1: Specific explanation + data",
                    "Advantage 2: Detailed analysis", 
                    "Disadvantage: Objective evaluation"
                ]
            }},
            "right": {{
                "title": "Option B name",
                "points": [
                    "Advantage 1: Specific explanation + data",
                    "Advantage 2: Detailed analysis",
                    "Disadvantage: Objective evaluation"  
                ]
            }},
            "conclusion": "Comparison summary with recommendations",
            "image_prompt": "Split-screen comparison illustration showing two different approaches side by side, modern flat design, contrasting colors, professional business style"
        }},
        {{
            "type": "timeline",
            "title": "Development history title",
            "events": [
                {{
                    "year": "2019",
                    "title": "Milestone event",
                    "description": "What specifically happened, what was the significance, what were the metrics"
                }},
                {{
                    "year": "2021", 
                    "title": "Major breakthrough",
                    "description": "Detailed explanation of breakthrough content and impact"
                }}
            ],
            "image_prompt": "Timeline visualization illustration showing progression and growth, arrow moving upward through milestones, gradient background, modern corporate style"
        }},
        {{
            "type": "data",
            "title": "Core data display",
            "stats": [
                {{
                    "value": "85%",
                    "label": "Market share",
                    "description": "Leading position in XX field"
                }},
                {{
                    "value": "250M",
                    "label": "User scale", 
                    "description": "Year-over-year growth XX%"
                }}
            ],
            "insight": "Insights and analysis behind the data",
            "image_prompt": "Big data visualization illustration with floating numbers and charts, modern tech style, blue and cyan gradient, digital aesthetic, professional business look"
        }},
        {{
            "type": "grid",
            "title": "Core advantages/features",
            "items": [
                {{
                    "title": "Advantage 1 name",
                    "description": "Detailed explanation of what this advantage is, how it manifests, what value it brings"
                }},
                {{
                    "title": "Advantage 2 name",
                    "description": "Detailed explanation + data support"
                }}
            ],
            "image_prompt": "Grid layout illustration showing multiple feature icons in organized tiles, modern UI design, consistent color palette, clean professional style"
        }}
    ]
}}"""
        
        print(f"[TextGen] Using model: {self.TEXT_MODEL} for outline generation")
        
        response = await self.client.chat.completions.create(
            model=self.TEXT_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=8000
        )
        
        content = response.choices[0].message.content
        
        # Debug: Check if image_prompt is in raw response
        if '"image_prompt"' in content:
            print(f"[AI Provider] Raw response contains image_prompt fields")
        else:
            print(f"[AI Provider] WARNING: Raw response does NOT contain image_prompt fields")
        
        # Check if truncated
        if response.choices[0].finish_reason == "length":
            content = _fix_json_content(content)
        
        result = robust_json_parse(content)
        
        # Debug: Check parsed result
        slides = result.get("slides", [])
        image_prompt_count = sum(1 for s in slides if s.get("image_prompt"))
        print(f"[AI Provider] Parsed {len(slides)} slides, {image_prompt_count} have image_prompt")
        
        return result
    
    async def generate_slide_content(
        self,
        title: str,
        slide_type: str,
        context: str,
        language: str = "zh"
    ) -> str:
        """Generate detailed slide content"""
        
        prompt = f"""Generate detailed slide content with data and analysis.

Title: {title}
Type: {slide_type}
Context: {context}
Language: {language}

Requirements:
1. Provide specific data, examples, or case studies
2. Include analysis and insights, not just surface descriptions
3. Use structured formatting (bullet points, numbered lists)
4. Each point should have supporting details
5. Total length: 150-300 words

Output format: Rich text with markdown-style formatting."""
        
        response = await self.client.chat.completions.create(
            model=self.TEXT_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=2000
        )
        
        return response.choices[0].message.content
    
    async def generate_image_prompt(
        self,
        slide_content: str
    ) -> str:
        """Generate image prompt"""
        
        prompt = f"""Generate an image prompt based on the following content:
{slide_content}

Requirements:
1. Concise and clear
2. Professional business style
3. Suitable for PPT use

Output only the prompt itself, no other text."""
        
        response = await self.client.chat.completions.create(
            model=self.TEXT_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=200
        )
        
        return response.choices[0].message.content.strip()
    
    async def generate_image(self, prompt: str) -> str:
        """
        Generate image using gemini-3-pro-image-preview model
        
        API: Gemini native API (NOT OpenAI-compatible)
        Endpoint: /v1beta/models/gemini-3-pro-image-preview:generateContent
        
        Returns:
            Base64 encoded image data URL (data:image/png;base64,...)
        """
        try:
            import httpx
            
            print(f"[ImageGen] Using model: {self.IMAGE_MODEL}")
            print(f"[ImageGen] Prompt: {prompt[:50]}...")
            
            # Gemini native API endpoint for image generation
            api_url = f"https://yunwu.ai/v1beta/models/{self.IMAGE_MODEL}:generateContent"
            
            payload = {
                "contents": [
                    {
                        "role": "user",
                        "parts": [
                            {
                                "text": prompt
                            }
                        ]
                    }
                ],
                "generationConfig": {
                    "responseModalities": ["Text", "Image"]
                }
            }
            
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.image_api_key}"
            }
            
            print(f"[ImageGen] Sending request to {api_url}")
            
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(api_url, json=payload, headers=headers)
                
                print(f"[ImageGen] Response status: {response.status_code}")
                
                if response.status_code != 200:
                    print(f"[ImageGen] API error: {response.status_code} - {response.text[:200]}")
                    return ""
                
                data = response.json()
                
                # Extract image from response
                candidates = data.get("candidates", [])
                if not candidates:
                    print("[ImageGen] No candidates in response")
                    print(f"[ImageGen] Response: {data}")
                    return ""
                
                content = candidates[0].get("content", {})
                parts = content.get("parts", [])
                
                print(f"[ImageGen] Got {len(parts)} parts in response")
                
                for i, part in enumerate(parts):
                    print(f"[ImageGen] Part {i} keys: {list(part.keys())}")
                    if "inlineData" in part:
                        inline_data = part["inlineData"]
                        mime_type = inline_data.get("mimeType", "image/png")
                        base64_data = inline_data.get("data", "")
                        if base64_data:
                            print(f"[ImageGen] Found image data: {mime_type}, {len(base64_data)} chars")
                            return f"data:{mime_type};base64,{base64_data}"
                    elif "text" in part:
                        print(f"[ImageGen] Text part: {part['text'][:100]}...")
                
                print("[ImageGen] No image data found in response")
                return ""
                
        except Exception as e:
            print(f"[ImageGen] Error generating image: {e}")
            import traceback
            traceback.print_exc()
            return ""


class AIProviderFactory:
    """AI Provider Factory"""
    
    _providers = {
        "yunwu": YunwuProvider,
    }
    
    @classmethod
    def create(cls, provider: str, api_key: str, image_api_key: str = None) -> AIProviderBase:
        """Create provider instance
        
        Args:
            provider: Provider name (e.g., 'yunwu')
            api_key: API key for text generation
            image_api_key: Optional separate API key for image generation
        """
        provider_class = cls._providers.get(provider)
        if not provider_class:
            raise ValueError(f"Unsupported provider: {provider}")
        return provider_class(api_key, image_api_key)
    
    @classmethod
    def get_supported_providers(cls) -> List[str]:
        """Get supported providers list"""
        return list(cls._providers.keys())
