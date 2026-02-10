"""
CrewAI Tasks for PPT Generation
PPT生成任务定义
"""

from crewai import Task
from textwrap import dedent


class PPTTasks:
    """PPT生成任务集合"""
    
    def analyze_requirement(self, agent, user_prompt: str, references: str = "") -> Task:
        """
        需求分析任务
        
        Args:
            agent: 需求分析Agent
            user_prompt: 用户输入的需求
            references: 参考资料
        """
        context = f"用户需求：{user_prompt}"
        if references:
            context += f"\n\n参考资料：{references}"
        
        return Task(
            description=dedent(f"""
                分析以下PPT制作需求，提取关键信息：
                
                {context}
                
                请分析并输出以下内容（JSON格式）：
                {{
                    "topic": "PPT主题",
                    "purpose": "制作目的（汇报/培训/销售等）",
                    "target_audience": "目标受众",
                    "key_points": ["核心要点1", "核心要点2", ...],
                    "tone": "风格（正式/轻松/专业/创意等）",
                    "estimated_slides": "预估页数",
                    "special_requirements": "特殊要求"
                }}
                
                注意：
                1. 如果用户提供的信息不完整，请基于常见场景合理推测
                2. key_points应该包含3-7个核心要点
                3. 输出必须是合法的JSON格式
            """),
            agent=agent,
            expected_output='JSON格式的需求分析结果'
        )
    
    def plan_outline(self, agent, requirement_analysis: str, num_slides: int = 10) -> Task:
        """
        大纲规划任务
        
        Args:
            agent: 大纲规划Agent
            requirement_analysis: 需求分析结果
            num_slides: 期望页数
        """
        return Task(
            description=dedent(f"""
                基于以下需求分析，设计PPT的详细大纲结构：
                
                {requirement_analysis}
                
                要求：
                1. 总共设计{num_slides}页PPT
                2. 包含封面页、目录页、内容页、总结页
                3. 每页都有明确的标题和核心内容描述
                4. 内容逻辑清晰，层层递进
                
                输出格式（JSON）：
                {{
                    "slides": [
                        {{
                            "page": 1,
                            "type": "cover",
                            "title": "封面标题",
                            "content": "副标题/说明"
                        }},
                        {{
                            "page": 2,
                            "type": "table_of_contents",
                            "title": "目录",
                            "content": ["章节1", "章节2", ...]
                        }},
                        {{
                            "page": 3,
                            "type": "content",
                            "title": "页面标题",
                            "content": "页面核心内容描述",
                            "key_points": ["要点1", "要点2", "要点3"]
                        }},
                        ...
                    ]
                }}
            """),
            agent=agent,
            expected_output='JSON格式的PPT大纲，包含每页的标题和内容描述'
        )
    
    def write_content(self, agent, outline: str, slide_index: int) -> Task:
        """
        内容撰写任务（单页）
        
        Args:
            agent: 内容撰写Agent
            outline: 大纲内容
            slide_index: 页码
        """
        return Task(
            description=dedent(f"""
                为PPT的第{slide_index}页撰写详细内容。
                
                整体大纲：
                {outline}
                
                请为第{slide_index}页生成：
                1. 精炼的标题（不超过20字）
                2. 3-5个要点（每点不超过30字）
                3. 详细的演讲者备注（100-200字）
                4. 建议的图表类型（如有数据）
                
                输出格式（JSON）：
                {{
                    "page": {slide_index},
                    "title": "页面标题",
                    "bullet_points": ["要点1", "要点2", "要点3"],
                    "speaker_notes": "演讲者备注",
                    "chart_type": "建议的图表类型（bar/line/pie/none）",
                    "chart_data": "如果有图表，描述数据结构"
                }}
            """),
            agent=agent,
            expected_output=f'第{slide_index}页的详细内容（JSON格式）'
        )
    
    def design_visual(self, agent, outline: str, topic: str, style_preference: str = "") -> Task:
        """
        视觉设计任务
        
        Args:
            agent: 视觉设计Agent
            outline: PPT大纲
            topic: PPT主题
            style_preference: 风格偏好
        """
        style_hint = f"\n用户风格偏好：{style_preference}" if style_preference else ""
        
        return Task(
            description=dedent(f"""
                为以下PPT设计视觉方案：
                
                主题：{topic}
                {style_hint}
                
                大纲结构：
                {outline}
                
                请提供：
                1. 配色方案（主色、辅助色、背景色，使用十六进制代码）
                2. 字体建议（标题字体、正文字体）
                3. 整体视觉风格描述
                4. 每页的布局建议（文字为主/图文混排/全图型等）
                5. 配图建议（如有需要）
                
                输出格式（JSON）：
                {{
                    "color_scheme": {{
                        "primary": "#XXXXXX",
                        "secondary": "#XXXXXX",
                        "background": "#XXXXXX",
                        "text": "#XXXXXX"
                    }},
                    "typography": {{
                        "title_font": "字体名称",
                        "body_font": "字体名称"
                    }},
                    "style_description": "整体风格描述",
                    "slide_layouts": [
                        {{"page": 1, "layout": "布局类型", "recommendation": "具体建议"}}
                    ],
                    "image_suggestions": ["配图建议1", "配图建议2"]
                }}
            """),
            agent=agent,
            expected_output='JSON格式的视觉设计方案'
        )
    
    def analyze_data(self, agent, data_description: str) -> Task:
        """
        数据分析任务
        
        Args:
            agent: 数据分析Agent
            data_description: 数据描述
        """
        return Task(
            description=dedent(f"""
                分析以下数据，提供洞察和可视化建议：
                
                {data_description}
                
                请提供：
                1. 数据的关键洞察（3-5条）
                2. 数据的趋势或规律
                3. 建议的图表类型和展示方式
                4. 需要注意的数据异常或亮点
                
                输出格式（JSON）：
                {{
                    "insights": ["洞察1", "洞察2", ...],
                    "trends": "趋势描述",
                    "recommended_charts": [
                        {{"type": "图表类型", "reason": "推荐理由", "data_structure": "数据结构"}}
                    ],
                    "anomalies": "异常或亮点"
                }}
            """),
            agent=agent,
            expected_output='JSON格式的数据分析结果'
        )
    
    def inspect_quality(self, agent, ppt_content: str, original_requirement: str) -> Task:
        """
        质量检查任务
        
        Args:
            agent: 质检Agent
            ppt_content: PPT完整内容
            original_requirement: 原始需求
        """
        return Task(
            description=dedent(f"""
                检查以下PPT是否满足原始需求：
                
                原始需求：
                {original_requirement}
                
                PPT内容：
                {ppt_content}
                
                请检查：
                1. 内容完整性（是否覆盖所有核心要点）
                2. 逻辑连贯性（各页之间逻辑是否通顺）
                3. 语言准确性（有无错别字、语病）
                4. 风格一致性（整体风格是否统一）
                5. 是否满足用户的特殊要求
                
                输出格式（JSON）：
                {{
                    "passed": true/false,
                    "score": "质量评分（1-10）",
                    "issues": ["问题1", "问题2", ...],
                    "suggestions": ["改进建议1", ...]
                }}
                
                如果未通过，请详细说明需要修改的地方。
            """),
            agent=agent,
            expected_output='JSON格式的质检报告'
        )
