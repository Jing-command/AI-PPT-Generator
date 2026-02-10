"""
CrewAI Agents for PPT Generation (v1.9.3 Compatible)
多Agent协作生成PPT系统 - 适配 CrewAI 1.9.3
"""

from crewai import Agent
from crewai.llm import LLM

from app.config import settings


def get_llm(provider: str = "openai", model: str = None, api_key: str = None):
    """
    获取LLM实例 (CrewAI 1.9.3+ 格式)
    
    Args:
        provider: 提供商 (openai/anthropic/moonshot/gemini)
        model: 模型名称
        api_key: API密钥
    
    Returns:
        LLM实例
    """
    if provider == "gemini":
        # Gemini 3 Pro - 使用 OpenAI 兼容格式
        return LLM(
            model=f"openai/{model or 'gemini-3-pro'}",
            api_key=api_key,
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
            temperature=0.7,
            max_tokens=4000
        )
    elif provider == "moonshot":
        # Moonshot (Kimi) API - 使用 openai 兼容格式
        return LLM(
            model=f"openai/{model or 'kimi-k2-5'}",
            api_key=api_key,
            base_url="https://api.moonshot.cn/v1",
            temperature=0.7,
            max_tokens=4000
        )
    elif provider == "openai":
        return LLM(
            model=f"openai/{model or 'gpt-4o-mini'}",
            api_key=api_key,
            temperature=0.7,
            max_tokens=4000
        )
    elif provider == "anthropic":
        # Anthropic 使用 litellm 格式
        return LLM(
            model=f"anthropic/{model or 'claude-3-sonnet-20240229'}",
            api_key=api_key,
            temperature=0.7,
            max_tokens=4000
        )
    else:
        # 默认使用 OpenAI
        return LLM(
            model="openai/gpt-4o-mini",
            api_key=api_key,
            temperature=0.7
        )


class PPTAgents:
    """PPT生成Agent集合"""
    
    def __init__(self, provider: str, api_key: str, model: str = None):
        self.provider = provider
        self.api_key = api_key
        self.model = model
        self.llm = get_llm(provider, model, api_key)
    
    def requirement_analyst(self) -> Agent:
        """
        需求分析Agent
        理解用户需求，提取关键信息
        """
        return Agent(
            role='PPT需求分析师',
            goal='深入理解用户需求，提取PPT的主题、目标受众、核心要点',
            backstory='''你是一位经验丰富的PPT需求分析师，擅长从用户的描述中提炼关键信息。
            你能够识别用户的真实意图，区分主次信息，为后续的PPT制作提供清晰的方向。
            你注重细节，善于提问，确保不遗漏任何重要信息。''',
            llm=self.llm,
            verbose=True,
            allow_delegation=False
        )
    
    def outline_planner(self) -> Agent:
        """
        大纲规划Agent
        设计PPT整体结构和章节安排
        """
        return Agent(
            role='PPT结构规划师',
            goal='设计逻辑清晰、层次分明的PPT大纲结构',
            backstory='''你是一位资深的PPT结构规划师，精通各种PPT架构设计。
            你擅长将复杂信息组织成易于理解的结构，知道如何安排内容的先后顺序，
            如何设置悬念和转折，让PPT既有逻辑性又有吸引力。
            你了解不同场景（工作汇报、产品介绍、培训讲解等）的最佳结构模式。''',
            llm=self.llm,
            verbose=True,
            allow_delegation=False
        )
    
    def content_writer(self) -> Agent:
        """
        内容撰写Agent
        生成每页PPT的具体内容
        """
        return Agent(
            role='PPT内容撰写专家',
            goal='撰写简洁有力、适合演讲的PPT页面内容',
            backstory='''你是一位专业的PPT内容撰写专家，深谙"少即是多"的原则。
            你擅长将复杂信息转化为简洁的要点，每页PPT的文字精炼且富有表现力。
            你知道如何写标题吸引眼球，如何用要点支撑观点，如何引导观众的思路。
            你的文字风格专业但不晦涩，简洁但不空洞。''',
            llm=self.llm,
            verbose=True,
            allow_delegation=False
        )
    
    def visual_designer(self) -> Agent:
        """
        视觉设计Agent
        设计配色方案和视觉风格
        """
        return Agent(
            role='PPT视觉设计师',
            goal='为PPT设计专业、美观的视觉风格和配色方案',
            backstory='''你是一位富有创意的PPT视觉设计师，对色彩、排版、视觉层次有敏锐的感知。
            你擅长根据PPT的主题和受众选择合适的配色方案，知道如何使用颜色传达情绪，
            如何安排版面让信息一目了然。你熟悉商务、学术、创意等不同风格的设计语言。
            你能够提供具体的设计建议，包括颜色代码、字体选择、布局建议等。''',
            llm=self.llm,
            verbose=True,
            allow_delegation=False
        )
    
    def data_analyst(self) -> Agent:
        """
        数据分析Agent
        分析数据，提供洞察
        """
        return Agent(
            role='数据分析师',
            goal='分析数据，提取关键洞察，建议合适的数据可视化方式',
            backstory='''你是一位资深的数据分析师，擅长从数据中发现趋势和规律。
            你能够快速理解数据的含义，识别关键指标，发现数据背后的故事。
            你熟悉各种图表类型（柱状图、折线图、饼图、散点图等），知道在什么场景下使用什么图表最有效。
            你能够将复杂的数据分析结果转化为普通人都能理解的洞察。''',
            llm=self.llm,
            verbose=True,
            allow_delegation=False
        )
    
    def quality_inspector(self) -> Agent:
        """
        质检Agent
        检查PPT内容的完整性和准确性
        """
        return Agent(
            role='PPT质量检查员',
            goal='检查PPT的完整性、一致性和专业性，确保交付质量',
            backstory='''你是一位严格的PPT质量检查员，对细节有着近乎苛刻的要求。
            你检查每一页PPT的逻辑是否通顺，内容是否完整，风格是否统一。
            你能够发现潜在的问题，如数据不一致、逻辑跳跃、格式错误等。
            你以用户的视角审视PPT，确保最终交付的内容符合用户的期望。
            你的检查清单包括：内容完整性、逻辑连贯性、视觉一致性、语言准确性。''',
            llm=self.llm,
            verbose=True,
            allow_delegation=False
        )
