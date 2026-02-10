"""
CrewAI 流程测试 - 简化版 PPT 生成
验证多Agent协作流程
"""

import os
import sys
from crewai import Agent, Task, Crew, Process
from crewai.llm import LLM

# 使用 Moonshot API（真实调用）
# 注意：这会消耗 API 额度
os.environ['MOONSHOT_API_KEY'] = 'sk-kimi-ypCKsE0oLqeBXCOohWEAaEe4YgGfsJB49IzUq4OaS4UP0e6u0ZSOXUCoKI59Keta'

print("=" * 60)
print("🚀 CrewAI 多Agent PPT 生成测试")
print("=" * 60)

# Step 1: 创建 LLM
print("\n📌 Step 1: 配置 LLM (Kimi K2.5)")
llm = LLM(
    model="openai/kimi-k2-5",
    api_key=os.environ['MOONSHOT_API_KEY'],
    base_url="https://api.moonshot.cn/v1",
    temperature=0.7
)
print("✅ LLM 配置完成")

# Step 2: 创建 Agents
print("\n📌 Step 2: 创建 Agents")

requirement_agent = Agent(
    role='需求分析师',
    goal='分析用户的PPT需求',
    backstory='你擅长理解用户需求，提取关键信息',
    llm=llm,
    verbose=False
)
print("✅ 需求分析Agent")

outline_agent = Agent(
    role='大纲规划师',
    goal='设计PPT结构',
    backstory='你擅长设计清晰的内容结构',
    llm=llm,
    verbose=False
)
print("✅ 大纲规划Agent")

content_agent = Agent(
    role='内容撰写师',
    goal='生成PPT内容',
    backstory='你擅长撰写简洁有力的PPT内容',
    llm=llm,
    verbose=False
)
print("✅ 内容撰写Agent")

# Step 3: 创建 Tasks
print("\n📌 Step 3: 创建 Tasks")

user_request = "帮我做一个关于人工智能发展趋势的PPT，面向企业管理层，5页左右"

# Task 1: 需求分析
task_analyze = Task(
    description=f'''
    分析用户的PPT需求：
    "{user_request}"
    
    请提取以下信息（用JSON格式回答）：
    - topic: PPT主题
    - target_audience: 目标受众
    - num_slides: 建议页数
    - key_points: 核心要点列表
    ''',
    agent=requirement_agent,
    expected_output='JSON格式的需求分析'
)
print("✅ Task 1: 需求分析")

# Task 2: 大纲规划
task_outline = Task(
    description='''
    基于需求分析结果，设计PPT大纲。
    要求：
    1. 包含封面、目录、3页内容页、总结页
    2. 每页有明确的标题
    3. 逻辑清晰，层层递进
    
    输出JSON格式：
    {
        "slides": [
            {"page": 1, "type": "cover", "title": "..."},
            {"page": 2, "type": "content", "title": "..."}
        ]
    }
    ''',
    agent=outline_agent,
    expected_output='JSON格式的PPT大纲'
)
print("✅ Task 2: 大纲规划")

# Task 3: 内容生成
task_content = Task(
    description='''
    为每页PPT生成具体内容。
    要求：
    1. 标题简洁有力（不超过15字）
    2. 每页3-4个要点
    3. 语言专业但易懂
    
    输出格式：
    第1页 - 标题：xxx
    要点：
    - 要点1
    - 要点2
    
    第2页 - 标题：xxx
    ...
    ''',
    agent=content_agent,
    expected_output='每页PPT的详细内容'
)
print("✅ Task 3: 内容生成")

# Step 4: 创建 Crew
print("\n📌 Step 4: 组建 Crew")
crew = Crew(
    agents=[requirement_agent, outline_agent, content_agent],
    tasks=[task_analyze, task_outline, task_content],
    process=Process.sequential,  # 顺序执行
    verbose=True  # 显示详细日志
)
print("✅ Crew 组建完成")

# Step 5: 运行
print("\n" + "=" * 60)
print("🎬 开始执行生成流程...")
print("=" * 60)
print()

try:
    result = crew.kickoff()
    
    print("\n" + "=" * 60)
    print("✅ 生成完成！")
    print("=" * 60)
    print("\n📊 生成结果：")
    print(result)
    
except Exception as e:
    print(f"\n❌ 执行出错: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n🎉 测试成功！CrewAI + Kimi K2.5 流程验证通过")
