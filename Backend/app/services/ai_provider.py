"""
AI Provider Service Wrapper
Unified interface for different AI services - 使用 Gemini 原生 API 格式
"""

import json
import re
from abc import ABC, abstractmethod
from typing import AsyncGenerator, Dict, List, Optional

import httpx

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
    """
    Yunwu AI (yunwu.ai) Provider - 使用 Gemini 原生 API 格式
    
    API 端点: https://yunwu.ai/v1beta/models/{model}:generateContent
    """
    
    def __init__(self, api_key: str):
        super().__init__(api_key)
        self.base_url = "https://yunwu.ai/v1beta"
        self.model = "gemini-3-pro"  # 或 gemini-3-flash-preview
        self.api_key = api_key
    
    async def _call_gemini_api(self, contents: List[Dict], generation_config: Dict = None) -> Dict:
        """
        调用 Gemini 原生 API
        
        Args:
            contents: Gemini 格式的内容数组
            generation_config: 生成配置
            
        Returns:
            API 响应数据
        """
        api_url = f"{self.base_url}/models/{self.model}:generateContent"
        
        payload = {
            "contents": contents
        }
        
        if generation_config:
            payload["generationConfig"] = generation_config
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                api_url,
                json=payload,
                headers=headers,
                timeout=120.0
            )
            response.raise_for_status()
            return response.json()
    
    def _extract_text(self, response: Dict) -> str:
        """从 Gemini 响应中提取文本内容"""
        try:
            candidates = response.get("candidates", [])
            if not candidates:
                return ""
            
            content = candidates[0].get("content", {})
            parts = content.get("parts", [])
            
            # 合并所有文本部分
            texts = []
            for part in parts:
                if "text" in part:
                    texts.append(part["text"])
            
            return "\n".join(texts)
        except Exception as e:
            print(f"[YunwuProvider] Extract text error: {e}")
            return ""
    
    async def generate_ppt_outline(
        self,
        prompt: str,
        num_slides: int,
        language: str = "zh",
        style: str = "business"
    ) -> Dict:
        """使用 Gemini 原生 API 生成 PPT 大纲"""
        
        style_descriptions = {
            "business": "Professional business style, deep blue tones, clean and elegant",
            "education": "Educational style, green tones, fresh and clear",
            "creative": "Creative style, pink/purple tones, modern and lively",
            "minimal": "Minimalist style, black/white/gray tones, simple and elegant",
            "tech": "Tech style, cyan/blue tones, futuristic"
        }
        style_desc = style_descriptions.get(style, style_descriptions["business"])
        
        system_text = f"""You are a professional PPT content strategist. Generate content-rich, data-driven, well-structured presentations based on user topics.

**Critical Requirements**:
1. Generate {num_slides} slides
2. Use {language} language
3. Design style: {style_desc}
4. **IMPORTANT**: Each page must have complete, valuable content with data/cases/analysis, not just simple titles

**Output Format (JSON)**:
{{
    "title": "Main PPT title",
    "summary": "Overall summary around 200 words",
    "theme": {{
        "name": "Theme name",
        "primary_color": "#1a365d",
        "secondary_color": "#3182ce"
    }},
    "slides": [
        {{
            "type": "title",
            "title": "Main title",
            "subtitle": "Subtitle"
        }},
        {{
            "type": "content", 
            "title": "Chapter title",
            "content": "Detailed content...",
            "bullets": ["Point 1", "Point 2", "Point 3"]
        }}
    ]
}}"""

        contents = [
            {"role": "user", "parts": [{"text": system_text}]},
            {"role": "user", "parts": [{"text": f"Generate PPT outline for: {prompt}"}]}
        ]
        
        response = await self._call_gemini_api(contents)
        text = self._extract_text(response)
        
        # 处理可能的截断
        if text and not text.endswith("}"):
            text = _fix_json_content(text)
        
        return robust_json_parse(text)
    
    async def generate_slide_content(
        self,
        title: str,
        slide_type: str,
        context: str,
        language: str = "zh"
    ) -> str:
        """使用 Gemini 原生 API 生成幻灯片内容"""
        
        prompt = f"""Generate detailed slide content.

Title: {title}
Type: {slide_type}
Context: {context}
Language: {language}

Requirements:
1. Provide specific data, examples, or case studies
2. Include analysis and insights
3. Use structured formatting
4. 150-300 words total"""

        contents = [{"role": "user", "parts": [{"text": prompt}]}]
        
        response = await self._call_gemini_api(contents)
        return self._extract_text(response)
    
    async def generate_image_prompt(self, slide_content: str) -> str:
        """使用 Gemini 原生 API 生成图片提示词"""
        
        prompt = f"""Generate an image prompt based on the following content:
{slide_content}

Requirements:
1. Concise and clear
2. Professional business style
3. Suitable for PPT use

Output only the prompt itself."""

        contents = [{"role": "user", "parts": [{"text": prompt}]}]
        
        response = await self._call_gemini_api(contents)
        return self._extract_text(response)
    
    async def generate_image(self, prompt: str) -> str:
        """
        使用 Gemini 原生 API 生成图片
        
        使用支持图片生成的模型端点
        """
        api_url = f"{self.base_url}/models/gemini-3-pro-image-preview:generateContent"
        
        payload = {
            "contents": [{
                "role": "user",
                "parts": [{"text": prompt}]
            }],
            "generationConfig": {
                "responseModalities": ["Text", "Image"]
            }
        }
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    api_url,
                    json=payload,
                    headers=headers,
                    timeout=60.0
                )
                response.raise_for_status()
                
                data = response.json()
                
                # 解析响应中的图片数据
                candidates = data.get("candidates", [])
                if not candidates:
                    return ""
                
                content = candidates[0].get("content", {})
                parts = content.get("parts", [])
                
                for part in parts:
                    if "inlineData" in part:
                        inline_data = part["inlineData"]
                        mime_type = inline_data.get("mimeType", "image/png")
                        base64_data = inline_data.get("data", "")
                        return f"data:{mime_type};base64,{base64_data}"
                
                return ""
                
        except Exception as e:
            print(f"[YunwuProvider] Image generation error: {e}")
            return ""
        
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=200
        )
        
        return response.choices[0].message.content.strip()
    
    async def generate_image(self, prompt: str) -> str:
        """
        使用 Gemini 原生 API 生成图片 (通过 yunwu.ai)
        
        使用端点: /v1beta/models/gemini-3-pro-image-preview:generateContent
        """
        import httpx
        import base64
        
        api_url = "https://yunwu.ai/v1beta/models/gemini-3-pro-image-preview:generateContent"
        
        # 构建 Gemini 原生格式的 payload
        payload = {
            "contents": [{
                "role": "user",
                "parts": [{"text": prompt}]
            }],
            "generationConfig": {
                "responseModalities": ["Text", "Image"]
            }
        }
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    api_url,
                    json=payload,
                    headers=headers,
                    timeout=60.0
                )
                response.raise_for_status()
                
                data = response.json()
                
                # 解析响应中的图片数据
                # Gemini 返回 inlineData，包含 base64 编码的图片
                candidates = data.get("candidates", [])
                if not candidates:
                    return ""
                
                content = candidates[0].get("content", {})
                parts = content.get("parts", [])
                
                for part in parts:
                    # 查找包含 inlineData 的部分
                    if "inlineData" in part:
                        inline_data = part["inlineData"]
                        mime_type = inline_data.get("mimeType", "image/png")
                        base64_data = inline_data.get("data", "")
                        
                        # 返回 data URL 格式
                        return f"data:{mime_type};base64,{base64_data}"
                
                # 如果没有找到图片，返回空
                return ""
                
        except Exception as e:
            print(f"[YunwuProvider] Image generation error: {e}")
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
