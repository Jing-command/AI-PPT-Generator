"""
CrewAI Crew for PPT Generation
PPT生成Crew编排
"""

import json
import asyncio
from typing import Optional, Dict, Any
from crewai import Crew, Process

from app.crew.agents.ppt_agents import PPTAgents
from app.crew.tasks.ppt_tasks import PPTTasks


class PPTGenerationCrew:
    """
    PPT生成Crew
    
    编排多个Agent协作完成PPT生成任务
    """
    
    def __init__(self, provider: str, api_key: str, model: Optional[str] = None):
        """
        初始化PPT生成Crew
        
        Args:
            provider: LLM提供商 (openai/anthropic)
            api_key: API密钥
            model: 模型名称
        """
        self.provider = provider
        self.api_key = api_key
        self.model = model
        
        # 初始化Agents和Tasks
        self.agents = PPTAgents(provider, api_key, model)
        self.tasks = PPTTasks()
        
        # 存储中间结果
        self.context: Dict[str, Any] = {}
    
    async def generate_ppt(
        self,
        user_prompt: str,
        num_slides: int = 10,
        references: str = "",
        style_preference: str = "",
        progress_callback: Optional[callable] = None
    ) -> Dict[str, Any]:
        """
        生成PPT（完整流程）
        
        Args:
            user_prompt: 用户需求
            num_slides: PPT页数
            references: 参考资料
            style_preference: 风格偏好
            progress_callback: 进度回调函数
            
        Returns:
            生成的PPT内容
        """
        try:
            # Step 1: 需求分析
            if progress_callback:
                await progress_callback(10, "正在分析需求...")
            
            requirement_task = self.tasks.analyze_requirement(
                self.agents.requirement_analyst(),
                user_prompt,
                references
            )
            
            requirement_crew = Crew(
                agents=[self.agents.requirement_analyst()],
                tasks=[requirement_task],
                process=Process.sequential,
                verbose=True
            )
            
            requirement_result = await asyncio.to_thread(requirement_crew.kickoff)
            self.context['requirement'] = self._parse_json(str(requirement_result))
            
            # Step 2: 大纲规划
            if progress_callback:
                await progress_callback(25, "正在规划PPT结构...")
            
            outline_task = self.tasks.plan_outline(
                self.agents.outline_planner(),
                json.dumps(self.context['requirement'], ensure_ascii=False),
                num_slides
            )
            
            outline_crew = Crew(
                agents=[self.agents.outline_planner()],
                tasks=[outline_task],
                process=Process.sequential,
                verbose=True
            )
            
            outline_result = await asyncio.to_thread(outline_crew.kickoff)
            self.context['outline'] = self._parse_json(str(outline_result))
            
            # Step 3: 视觉设计
            if progress_callback:
                await progress_callback(40, "正在设计视觉方案...")
            
            visual_task = self.tasks.design_visual(
                self.agents.visual_designer(),
                json.dumps(self.context['outline'], ensure_ascii=False),
                self.context['requirement'].get('topic', ''),
                style_preference
            )
            
            visual_crew = Crew(
                agents=[self.agents.visual_designer()],
                tasks=[visual_task],
                process=Process.sequential,
                verbose=True
            )
            
            visual_result = await asyncio.to_thread(visual_crew.kickoff)
            self.context['visual_design'] = self._parse_json(str(visual_result))
            
            # Step 4: 内容生成（逐页）
            slides_content = []
            outline_slides = self.context['outline'].get('slides', [])
            
            for idx, slide_outline in enumerate(outline_slides):
                progress = 50 + (idx / len(outline_slides)) * 30
                if progress_callback:
                    await progress_callback(
                        int(progress),
                        f"正在生成第 {idx + 1}/{len(outline_slides)} 页内容..."
                    )
                
                content_task = self.tasks.write_content(
                    self.agents.content_writer(),
                    json.dumps(self.context['outline'], ensure_ascii=False),
                    idx + 1
                )
                
                content_crew = Crew(
                    agents=[self.agents.content_writer()],
                    tasks=[content_task],
                    process=Process.sequential,
                    verbose=True
                )
                
                content_result = await asyncio.to_thread(content_crew.kickoff)
                slide_content = self._parse_json(str(content_result))
                slide_content['visual_design'] = self.context['visual_design']
                slides_content.append(slide_content)
            
            self.context['slides'] = slides_content
            
            # Step 5: 质量检查
            if progress_callback:
                await progress_callback(90, "正在进行质量检查...")
            
            full_ppt = {
                'requirement': self.context['requirement'],
                'outline': self.context['outline'],
                'visual_design': self.context['visual_design'],
                'slides': slides_content
            }
            
            quality_task = self.tasks.inspect_quality(
                self.agents.quality_inspector(),
                json.dumps(full_ppt, ensure_ascii=False),
                user_prompt
            )
            
            quality_crew = Crew(
                agents=[self.agents.quality_inspector()],
                tasks=[quality_task],
                process=Process.sequential,
                verbose=True
            )
            
            quality_result = await asyncio.to_thread(quality_crew.kickoff)
            self.context['quality_report'] = self._parse_json(str(quality_result))
            
            if progress_callback:
                await progress_callback(100, "生成完成！")
            
            return {
                'status': 'success',
                'data': full_ppt,
                'quality_report': self.context['quality_report'],
                'metadata': {
                    'provider': self.provider,
                    'model': self.model,
                    'num_slides': len(slides_content)
                }
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'context': self.context
            }
    
    def _parse_json(self, text: str) -> Dict:
        """
        从文本中提取JSON
        
        Args:
            text: 包含JSON的文本
            
        Returns:
            解析后的字典
        """
        try:
            # 尝试直接解析
            return json.loads(text)
        except json.JSONDecodeError:
            # 尝试从代码块中提取
            import re
            json_match = re.search(r'```(?:json)?\n(.*?)\n```', text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(1))
            
            # 尝试查找大括号包裹的内容
            json_match = re.search(r'\{.*\}', text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(0))
            
            # 如果都失败了，返回原始文本
            return {'raw_text': text}


# 便捷函数
def create_ppt_crew(provider: str, api_key: str, model: Optional[str] = None) -> PPTGenerationCrew:
    """
    创建PPT生成Crew实例
    
    Args:
        provider: 提供商
        api_key: API密钥
        model: 模型
        
    Returns:
        PPTGenerationCrew实例
    """
    return PPTGenerationCrew(provider, api_key, model)
