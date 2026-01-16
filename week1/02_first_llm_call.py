
"""
第一次调用 LLM API
学习目标:理解基本的 API 调用流程
"""

import os
from openai import OpenAI
from dotenv import load_dotenv

# 加载环境变量(从 .env 文件读取 API Key)
load_dotenv()

# 初始化客户端
client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)

print("=" * 50)
print("🤖 第一次调用 LLM!")
print("=" * 50)

# 发送消息给 AI
response = client.chat.completions.create(
    model="deepseek-chat",
    messages=[
        {"role": "user", "content": "你好!请用一句话介绍什么是 AI Agent"}
    ],
    stream=False
)

# 打印 AI 的回复
print("\n💬 AI 回复:")
print(response.choices[0].message.content)
print("\n" + "=" * 50)
