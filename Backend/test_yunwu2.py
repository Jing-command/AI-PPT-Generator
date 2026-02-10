"""
测试云物 AI (yunwu.ai) API - 使用 gpt-4o-mini
"""

import os
from crewai import Agent, Task, Crew
from crewai.llm import LLM

# 配置云物 AI
YUNWU_API_KEY = "sk-0Aur20HgDxn63H0zfePjyZYBaa5XocZUZg0LmOi44gncWXgC"

print("=" * 60)
print("🚀 云物 AI (yunwu.ai) API 测试")
print("=" * 60)

# Step 1: 配置 LLM
print("\n📌 Step 1: 配置 LLM (gpt-4o-mini)")
try:
    llm = LLM(
        model="openai/gpt-4o-mini",
        api_key=YUNWU_API_KEY,
        base_url="https://yunwu.ai/v1",
        temperature=0.7,
        max_tokens=1000
    )
    print("✅ LLM 配置成功")
except Exception as e:
    print(f"❌ LLM 配置失败: {e}")
    exit(1)

# Step 2: 创建简单 Agent
print("\n📌 Step 2: 创建测试 Agent")
agent = Agent(
    role='PPT设计师',
    goal='为用户生成简单的PPT大纲',
    backstory='你是一位专业的PPT设计师，擅长快速生成清晰的PPT结构',
    llm=llm,
    verbose=False
)
print("✅ Agent 创建成功")

# Step 3: 创建测试任务
print("\n📌 Step 3: 创建测试任务")
task = Task(
    description='''
    请为"人工智能发展趋势"这个主题生成一个简单的PPT大纲。
    要求：
    1. 包含3-5页
    2. 每页有标题和要点
    3. 适合企业管理层阅读
    
    请用中文回答，格式如下：
    第1页 - 标题
    - 要点1
    - 要点2
    ''',
    agent=agent,
    expected_output='PPT大纲'
)
print("✅ Task 创建成功")

# Step 4: 执行
print("\n📌 Step 4: 执行测试")
print("正在调用云物 AI API...")

crew = Crew(
    agents=[agent],
    tasks=[task],
    verbose=False
)

try:
    result = crew.kickoff()
    print("\n" + "=" * 60)
    print("✅ 测试成功！")
    print("=" * 60)
    print(f"\n📤 生成结果:\n{result}")
    
except Exception as e:
    print("\n" + "=" * 60)
    print("❌ 测试失败")
    print("=" * 60)
    print(f"\n错误: {e}")

print("\n" + "=" * 60)
print("测试完成")
print("=" * 60)
