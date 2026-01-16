"""
多轮对话 - 让 AI 记住上下文
学习目标:理解 messages 数组如何存储对话历史
"""

import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)

print("=" * 50)
print("💬 多轮对话演示")
print("=" * 50)

# 关键:用列表存储对话历史
messages = []

# 第一轮对话
print("\n【第1轮】用户: 我叫老韩,正在学习 AI Agent 开发")

messages.append({
    "role": "user", 
    "content": "我叫老韩,正在学习 AI Agent 开发"
})

response = client.chat.completions.create(
    model="deepseek-chat",
    messages=messages,
    stream=False
)

assistant_reply = response.choices[0].message.content
print(f"【第1轮】AI: {assistant_reply}")

messages.append({
    "role": "assistant",
    "content": assistant_reply
})

# 第二轮对话
print("\n【第2轮】用户: 我叫什么名字?")

messages.append({
    "role": "user",
    "content": "我叫什么名字?"
})

response = client.chat.completions.create(
    model="deepseek-chat",
    messages=messages,
    stream=False
)

assistant_reply = response.choices[0].message.content
print(f"【第2轮】AI: {assistant_reply}")

messages.append({
    "role": "assistant",
    "content": assistant_reply
})

# 第三轮对话
print("\n【第3轮】用户: 我在学什么?")

messages.append({
    "role": "user",
    "content": "我在学什么?"
})

response = client.chat.completions.create(
    model="deepseek-chat",
    messages=messages,
    stream=False
)

assistant_reply = response.choices[0].message.content
print(f"【第3轮】AI: {assistant_reply}")

# 查看完整对话历史
print("\n" + "=" * 50)
print("📝 完整对话历史:")
print("=" * 50)
for i, msg in enumerate(messages, 1):
    role = "用户" if msg["role"] == "user" else "AI"
    print(f"{i}. [{role}] {msg['content'][:50]}...")