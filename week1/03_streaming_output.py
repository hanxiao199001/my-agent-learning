"""
流式输出 - 像 ChatGPT 一样逐字显示
学习目标:理解 stream=True 的工作原理
"""

import os
from openai import OpenAI
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 初始化客户端
client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)

print("=" * 50)
print("🌊 流式输出演示")
print("=" * 50)
print("\n💬 AI 正在回复:")

# 关键变化:stream=True
response = client.chat.completions.create(
    model="deepseek-chat",
    messages=[
        {"role": "user", "content": "请用3句话介绍什么是 AI Agent,每句话都要详细一些"}
    ],
    stream=True  # 🔥 开启流式输出!
)

# 逐块接收并打印
for chunk in response:
    # 检查是否有内容
    if chunk.choices[0].delta.content:
        # 打印内容,不换行
        print(chunk.choices[0].delta.content, end="", flush=True)

print("\n" + "=" * 50)