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


class YunwuProvider(AIProviderBase):
    """Yunwu AI (yunwu.ai) Provider - Supports various OpenAI-compatible models"""
    
    def __init__(self, api_key: str):
        super().__init__(api_key)
        self.client = AsyncOpenAI(
            api_key=api_key,
            base_url="https://yunwu.ai/v1"
        )
        self.model = "gemini-3-flash-preview"
    
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
            "subtitle": "Subtitle explaining the core of the presentation"
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
            "data": {{"key": "Key metric", "value": "Specific value"}}
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
            "conclusion": "Comparison summary with recommendations"
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
            ]
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
            "insight": "Insights and analysis behind the data"
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
            ]
        }}
    ]
}}"""
        
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=8000
        )
        
        content = response.choices[0].message.content
        
        # Check if truncated
        if response.choices[0].finish_reason == "length":
            content = _fix_json_content(content)
        
        return robust_json_parse(content)
    
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
            model=self.model,
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
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=200
        )
        
        return response.choices[0].message.content.strip()
    
    async def generate_image(self, prompt: str) -> str:
        """Not supported"""
        return ""


class AIProviderFactory:
    """AI Provider Factory"""
    
    _providers = {
        "yunwu": YunwuProvider,
    }
    
    @classmethod
    def create(cls, provider: str, api_key: str) -> AIProviderBase:
        """Create provider instance"""
        provider_class = cls._providers.get(provider)
        if not provider_class:
            raise ValueError(f"Unsupported provider: {provider}")
        return provider_class(api_key)
    
    @classmethod
    def get_supported_providers(cls) -> List[str]:
        """Get supported providers list"""
        return list(cls._providers.keys())
