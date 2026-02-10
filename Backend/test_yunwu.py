"""
测试云物 AI (yunwu.ai) API
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
print("\n📌 Step 1: 配置 LLM")
try:
    llm = LLM(
        model="openai/gpt-4o",  # 或其他可用模型
        api_key=YUNWU_API_KEY,
        base_url="https://yunwu.ai/v1",
        temperature=0.7,
        max_tokens=1000
    )
    print("✅ LLM 配置成功")
    print(f"   Base URL: https://yunwu.ai/v1")
    print(f"   Model: openai/gpt-4o")
except Exception as e:
    print(f"❌ LLM 配置失败: {e}")
    exit(1)

# Step 2: 创建简单 Agent
print("\n📌 Step 2: 创建测试 Agent")
agent = Agent(
    role='测试助手',
    goal='验证API可用性',
    backstory='你是一个简单的测试助手',
    llm=llm,
    verbose=False
)
print("✅ Agent 创建成功")

# Step 3: 创建测试任务
print("\n📌 Step 3: 创建测试任务")
task = Task(
    description='请回复：云物AI API测试成功！',
    agent=agent,
    expected_output='确认消息'
)
print("✅ Task 创建成功")

# Step 4: 执行
print("\n📌 Step 4: 执行测试")
print("正在调用 API...")

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
    print(f"\n📤 输出结果:\n{result}")
    
except Exception as e:
    print("\n" + "=" * 60)
    print("❌ 测试失败")
    print("=" * 60)
    print(f"\n错误: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("测试完成")
print("=" * 60)
