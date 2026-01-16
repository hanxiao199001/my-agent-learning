"""
第一个工具调用 - 天气查询
学习目标:理解 Function Calling 的基本流程
"""

import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)

# ========== 1. 定义工具函数 ==========
def get_weather(city):
    """
    模拟天气查询 API
    实际项目中这里会调用真实的天气 API
    """
    # 模拟数据
    weather_data = {
        "北京": {"temperature": "15-25℃", "condition": "晴", "wind": "东南风3级"},
        "上海": {"temperature": "18-28℃", "condition": "多云", "wind": "东风2级"},
        "深圳": {"temperature": "22-30℃", "condition": "雷阵雨", "wind": "南风4级"}
    }
    
    if city in weather_data:
        return json.dumps(weather_data[city], ensure_ascii=False)
    else:
        return json.dumps({"error": f"没有找到{city}的天气信息"}, ensure_ascii=False)

# ========== 2. 定义工具描述(告诉 AI 这个工具能做什么) ==========
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "查询指定城市的天气信息",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "城市名称,例如:北京、上海"
                    }
                },
                "required": ["city"]
            }
        }
    }
]

print("=" * 60)
print("🛠️  第一个工具调用 - 天气查询")
print("=" * 60)

# ========== 3. 用户提问 ==========
user_question = "你好,请介绍一下自己"
print(f"\n👤 用户: {user_question}")

messages = [
    {"role": "user", "content": user_question}
]

# ========== 4. 第一次调用 AI(带工具描述) ==========
print("\n🤖 AI 思考中...")
response = client.chat.completions.create(
    model="deepseek-chat",
    messages=messages,
    tools=tools,  # 🔥 告诉 AI 有哪些工具可用
    tool_choice="auto"  # AI 自动决定是否使用工具
)

response_message = response.choices[0].message

# ========== 5. 检查 AI 是否要调用工具 ==========
if response_message.tool_calls:
    print("✅ AI 决定调用工具!")
    
    # 提取工具调用信息
    tool_call = response_message.tool_calls[0]
    function_name = tool_call.function.name
    function_args = json.loads(tool_call.function.arguments)
    
    print(f"   工具: {function_name}")
    print(f"   参数: {function_args}")
    
    # ========== 6. 执行工具 ==========
    if function_name == "get_weather":
        function_result = get_weather(function_args["city"])
        print(f"   结果: {function_result}")
    
    # ========== 7. 把工具结果返回给 AI ==========
    messages.append(response_message)  # AI 的工具调用请求
    messages.append({
        "role": "tool",
        "tool_call_id": tool_call.id,
        "content": function_result
    })
    
    # ========== 8. 第二次调用 AI(带工具结果) ==========
    print("\n🤖 AI 整合信息中...")
    final_response = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages
    )
    
    print(f"\n💬 AI 回复: {final_response.choices[0].message.content}")
    
else:
    # AI 认为不需要工具
    print(f"\n💬 AI 直接回复: {response_message.content}")

print("\n" + "=" * 60)