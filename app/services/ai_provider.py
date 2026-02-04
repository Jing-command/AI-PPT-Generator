"""
AI 提供商服务封装
统一接口调用不同 AI 服务
"""

from abc import ABC, abstractmethod
from typing import AsyncGenerator, Dict, List, Optional

import httpx
from openai import AsyncOpenAI

from app.config import settings


class AIProviderBase(ABC):
    """AI 提供商基类"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
    
    @abstractmethod
    async def generate_ppt_outline(
        self,
        prompt: str,
        num_slides: int,
        language: str = "zh"
    ) -> Dict:
        """生成 PPT 大纲"""
        pass
    
    @abstractmethod
    async def generate_slide_content(
        self,
        title: str,
        slide_type: str,
        context: str,
        language: str = "zh"
    ) -> str:
        """生成单页内容"""
        pass
    
    @abstractmethod
    async def generate_image_prompt(
        self,
        slide_content: str
    ) -> str:
        """生成配图提示词"""
        pass


class OpenAIProvider(AIProviderBase):
    """OpenAI 提供商"""
    
    def __init__(self, api_key: str):
        super().__init__(api_key)
        self.client = AsyncOpenAI(api_key=api_key)
    
    async def generate_ppt_outline(
        self,
        prompt: str,
        num_slides: int,
        language: str = "zh"
    ) -> Dict:
        """使用 GPT-4 生成大纲"""
        
        system_prompt = f"""你是一个专业的 PPT 设计师。请根据用户要求生成 PPT 大纲。
要求：
1. 生成 {num_slides} 页幻灯片的结构
2. 包含标题页、内容页、结束页
3. 每页包含标题和要点
4. 使用 {language} 语言

输出格式（JSON）：
{{
    "title": "PPT标题",
    "slides": [
        {{"type": "title", "title": "...", "subtitle": "..."}},
        {{"type": "content", "title": "...", "points": ["...", "..."]}},
        ...
    ]
}}"""
        
        response = await self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=2000
        )
        
        # 解析 JSON 响应
        import json
        content = response.choices[0].message.content
        
        # 提取 JSON 部分
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0]
        elif "```" in content:
            content = content.split("```")[1].split("```")[0]
        
        return json.loads(content.strip())
    
    async def generate_slide_content(
        self,
        title: str,
        slide_type: str,
        context: str,
        language: str = "zh"
    ) -> str:
        """生成单页详细内容"""
        
        prompt = f"""为幻灯片生成详细内容。
标题：{title}
类型：{slide_type}
上下文：{context}
语言：{language}

请生成 3-5 个要点，每个要点简洁有力。"""
        
        response = await self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=500
        )
        
        return response.choices[0].message.content
    
    async def generate_image_prompt(self, slide_content: str) -> str:
        """生成配图提示词"""
        
        prompt = f"""根据以下内容生成一个配图提示词（用于 DALL-E）：
{slide_content}

要求：
1. 简洁明了
2. 专业商务风格
3. 适合 PPT 使用

只输出提示词本身，不要其他文字。"""
        
        response = await self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=200
        )
        
        return response.choices[0].message.content.strip()
    
    async def generate_image(self, prompt: str) -> str:
        """生成图片，返回 URL"""
        
        response = await self.client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024",
            quality="standard",
            n=1
        )
        
        return response.data[0].url


class AIProviderFactory:
    """AI 提供商工厂"""
    
    _providers = {
        "openai": OpenAIProvider,
        # 可以添加更多提供商
        # "anthropic": AnthropicProvider,
        # "kimi": KimiProvider,
    }
    
    @classmethod
    def create(cls, provider: str, api_key: str) -> AIProviderBase:
        """创建提供商实例"""
        provider_class = cls._providers.get(provider)
        if not provider_class:
            raise ValueError(f"不支持的提供商: {provider}")
        return provider_class(api_key)
    
    @classmethod
    def get_supported_providers(cls) -> List[str]:
        """获取支持的提供商列表"""
        return list(cls._providers.keys())
