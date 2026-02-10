"""
CrewAI Module for AI PPT Generator
使用CrewAI多Agent架构生成PPT
"""

from .ppt_crew import PPTGenerationCrew, create_ppt_crew
from .agents.ppt_agents import PPTAgents
from .tasks.ppt_tasks import PPTTasks

__all__ = [
    'PPTGenerationCrew',
    'create_ppt_crew',
    'PPTAgents',
    'PPTTasks'
]
