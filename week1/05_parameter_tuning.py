"""
参数调整 - 控制 AI 的回复风格
学习目标:理解 temperature、max_tokens 等参数的作用
"""

import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)

print("=" * 60)
print("🎛️  参数调整演示")
print("=" * 60)

# 准备相同的问题
question = "用一句话解释什么是区块链"

# ========== 测试1: 默认参数 ==========
print("\n【测试1】默认参数")
print("-" * 60)

response = client.chat.completions.create(
    model="deepseek-chat",
    messages=[{"role": "user", "content": question}]
)
print(response.choices[0].message.content)

# ========== 测试2: temperature=0 (最保守) ==========
print("\n【测试2】temperature=0 (确定性回答,适合事实查询)")
print("-" * 60)

response = client.chat.completions.create(
    model="deepseek-chat",
    messages=[{"role": "user", "content": question}],
    temperature=0  # 0-2,越低越保守
)
print(response.choices[0].message.content)

# ========== 测试3: temperature=1.5 (更有创意) ==========
print("\n【测试3】temperature=1.5 (更有创意,适合头脑风暴)")
print("-" * 60)

response = client.chat.completions.create(
    model="deepseek-chat",
    messages=[{"role": "user", "content": question}],
    temperature=1.5
)
print(response.choices[0].message.content)

# ========== 测试4: max_tokens 限制长度 ==========
print("\n【测试4】max_tokens=20 (限制回复长度)")
print("-" * 60)

response = client.chat.completions.create(
    model="deepseek-chat",
    messages=[{"role": "user", "content": question}],
    max_tokens=20  # 最多返回 20 个 token
)
print(response.choices[0].message.content)

# ========== 测试5: system 角色 ==========
print("\n【测试5】添加 system 指令(让 AI 扮演角色)")
print("-" * 60)

response = client.chat.completions.create(
    model="deepseek-chat",
    messages=[
        {"role": "system", "content": "你是一个幽默风趣的老师,喜欢用比喻解释技术概念"},
        {"role": "user", "content": question}
    ]
)
print(response.choices[0].message.content)

print("\n" + "=" * 60)
print("📊 参数总结:")
print("=" * 60)
print("temperature: 0-2, 控制随机性")
print("  - 0: 最保守,适合事实查询")
print("  - 1: 平衡(默认)")
print("  - 2: 最创意,适合创作")
print()
print("max_tokens: 限制输出长度")
print("  - 用于控制成本或格式")
print()
print("system: 定义 AI 的角色和行为规则")
print("  - 在 messages 数组的第一条")