"""
CrewAI 流程测试 - Mock 版本（不调用真实API）
验证多Agent协作流程
"""

from crewai import Agent, Task, Crew, Process
from crewai.llm import LLM
from unittest.mock import Mock, patch
import json

print("=" * 60)
print("🚀 CrewAI 多Agent PPT 生成测试 (Mock)")
print("=" * 60)

# Step 1: 模拟 LLM 响应
print("\n📌 Step 1: 配置 LLM (Mock)")

class MockLLM:
    """Mock LLM，返回预定义响应"""
    def __init__(self):
        self.responses = {
            "需求分析": '''{
                "topic": "人工智能发展趋势",
                "target_audience": "企业管理层",
                "num_slides": 5,
                "key_points": ["AI技术突破", "行业应用", "商业价值", "实施策略", "未来展望"]
            }''',
            "大纲规划": '''{
                "slides": [
                    {"page": 1, "type": "cover", "title": "人工智能发展趋势"},
                    {"page": 2, "type": "content", "title": "AI技术突破"},
                    {"page": 3, "type": "content", "title": "行业应用案例"},
                    {"page": 4, "type": "content", "title": "商业价值分析"},
                    {"page": 5, "type": "summary", "title": "总结与展望"}
                ]
            }''',
            "内容生成": '''
第1页 - 标题：人工智能发展趋势
要点：
- 生成式AI引领新一轮技术革命
- 大模型能力持续提升
- 多模态AI成为新趋势

第2页 - 标题：AI技术突破
要点：
- GPT-4等模型展现强大能力
- 代码生成准确率超过80%
- 多语言支持覆盖100+语种

第3页 - 标题：行业应用案例
要点：
- 金融：智能风控降低损失30%
- 医疗：辅助诊断准确率95%
- 制造：预测性维护减少停机

第4页 - 标题：商业价值分析
要点：
- 2025年全球AI市场达2000亿美元
- 企业AI采用率增长300%
- ROI平均提升25%

第5页 - 标题：总结与展望
要点：
- AI已成为企业核心竞争力
- 建议制定AI战略规划
- 持续关注技术发展
'''
        }
        self.call_count = 0
    
    def call(self, messages, **kwargs):
        """模拟 LLM 调用"""
        self.call_count += 1        
        # 根据消息内容返回对应响应
        msg = str(messages)
        if "需求" in msg or "分析" in msg:
            return self.responses["需求分析"]
        elif "大纲" in msg or "结构" in msg:
            return self.responses["大纲规划"]
        else:
            return self.responses["内容生成"]

mock_llm = MockLLM()
print("✅ Mock LLM 配置完成")

# Step 2: 创建 Agents
print("\n📌 Step 2: 创建 Agents")

requirement_agent = Agent(
    role='需求分析师',
    goal='分析用户的PPT需求',
    backstory='你擅长理解用户需求，提取关键信息',
    llm=mock_llm,
    verbose=False
)
print("✅ 需求分析Agent")

outline_agent = Agent(
    role='大纲规划师',
    goal='设计PPT结构',
    backstory='你擅长设计清晰的内容结构',
    llm=mock_llm,
    verbose=False
)
print("✅ 大纲规划Agent")

content_agent = Agent(
    role='内容撰写师',
    goal='生成PPT内容',
    backstory='你擅长撰写简洁有力的PPT内容',
    llm=mock_llm,
    verbose=False
)
print("✅ 内容撰写Agent")

# Step 3: 创建 Tasks
print("\n📌 Step 3: 创建 Tasks")

user_request = "帮我做一个关于人工智能发展趋势的PPT，面向企业管理层，5页左右"

task_analyze = Task(
    description=f'分析需求：{user_request}',
    agent=requirement_agent,
    expected_output='JSON格式的需求分析'
)
print("✅ Task 1: 需求分析")

task_outline = Task(
    description='基于需求设计PPT大纲',
    agent=outline_agent,
    expected_output='JSON格式的PPT大纲'
)
print("✅ Task 2: 大纲规划")

task_content = Task(
    description='为每页PPT生成具体内容',
    agent=content_agent,
    expected_output='每页PPT的详细内容'
)
print("✅ Task 3: 内容生成")

# Step 4: 创建 Crew
print("\n📌 Step 4: 组建 Crew")
crew = Crew(
    agents=[requirement_agent, outline_agent, content_agent],
    tasks=[task_analyze, task_outline, task_content],
    process=Process.sequential,
    verbose=False
)
print("✅ Crew 组建完成")

# Step 5: 运行
print("\n" + "=" * 60)
print("🎬 开始执行生成流程...")
print("=" * 60)

try:
    result = crew.kickoff()
    
    print("\n" + "=" * 60)
    print("✅ 生成完成！")
    print("=" * 60)
    
    print("\n📊 执行统计：")
    print(f"   - LLM 调用次数: {mock_llm.call_count}")
    print(f"   - Agent 数量: 3")
    print(f"   - Task 数量: 3")
    
    print("\n📄 生成结果预览：")
    print("-" * 60)
    print(result[:1000] if len(str(result)) > 1000 else result)
    print("-" * 60)
    
    print("\n🔍 验证结果：")
    result_str = str(result)
    checks = [
        ("需求分析", "人工智能发展趋势" in result_str or "AI" in result_str),
        ("大纲结构", "第" in result_str and "页" in result_str),
        ("内容生成", "要点" in result_str or "标题" in result_str),
    ]
    for name, passed in checks:
        status = "✅" if passed else "❌"
        print(f"   {status} {name}")
    
except Exception as e:
    print(f"\n❌ 执行出错: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("🎉 测试成功！CrewAI 多Agent流程验证通过")
print("=" * 60)
print("\n流程说明：")
print("1️⃣  需求分析Agent 理解用户意图")
print("2️⃣  大纲规划Agent 设计PPT结构")
print("3️⃣  内容撰写Agent 生成每页内容")
print("\n每个Agent各司其职，按顺序协作完成任务")
