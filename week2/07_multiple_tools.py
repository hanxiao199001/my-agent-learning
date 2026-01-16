"""
多工具系统 - AI 自动选择合适的工具
学习目标:理解 AI 如何在多个工具中做选择
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

# ========== 1. 定义多个工具函数 ==========

def get_weather(city):
    """天气查询工具"""
    weather_data = {
        "北京": {"temperature": "15-25℃", "condition": "晴"},
        "上海": {"temperature": "18-28℃", "condition": "多云"},
        "深圳": {"temperature": "22-30℃", "condition": "雷阵雨"}
    }
    return json.dumps(weather_data.get(city, {"error": "未找到该城市"}), ensure_ascii=False)

def calculate(expression):
    """计算器工具"""
    try:
        result = eval(expression)
        return json.dumps({"result": result, "expression": expression}, ensure_ascii=False)
    except:
        return json.dumps({"error": "计算表达式错误"}, ensure_ascii=False)

def search_info(keyword):
    """信息搜索工具(模拟)"""
    knowledge_base = {
        "AI Agent": "AI Agent 是能够感知环境、自主决策并执行任务的智能系统",
        "区块链": "区块链是一种去中心化的分布式账本技术",
        "Python": "Python 是一种高级编程语言,广泛用于数据科学和AI开发"
    }
    
    # 模糊匹配改进
    for key in knowledge_base:
        if key.lower() in keyword.lower():
            return json.dumps({"keyword": keyword, "info": knowledge_base[key]}, ensure_ascii=False)
    
    return json.dumps({"keyword": keyword, "info": "未找到相关信息"}, ensure_ascii=False)

# ========== 2. 定义工具描述 ==========
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "查询指定城市的天气信息",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {"type": "string", "description": "城市名称"}
                },
                "required": ["city"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculate",
            "description": "执行数学计算,支持加减乘除和基本函数",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {"type": "string", "description": "数学表达式,例如: 25*4+10"}
                },
                "required": ["expression"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_info",
            "description": "搜索关于特定主题的信息",
            "parameters": {
                "type": "object",
                "properties": {
                    "keyword": {"type": "string", "description": "要搜索的关键词"}
                },
                "required": ["keyword"]
            }
        }
    }
]

# ========== 3. 工具映射 ==========
available_functions = {
    "get_weather": get_weather,
    "calculate": calculate,
    "search_info": search_info
}

# ========== 4. 处理工具调用的函数 ==========
def run_conversation(user_input):
    print(f"\n👤 用户: {user_input}")
    print("-" * 60)
    
    messages = [{"role": "user", "content": user_input}]
    
    # 第一次调用 AI
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages,
        tools=tools,
        tool_choice="auto"
    )
    
    response_message = response.choices[0].message
    
    # 检查是否需要工具
    if response_message.tool_calls:
        print("🤖 AI 决定使用工具:")
        
        # 保存 AI 的消息
        messages.append(response_message)
        
        # 执行所有工具调用
        for tool_call in response_message.tool_calls:
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)
            
            print(f"   📌 工具: {function_name}")
            print(f"   📌 参数: {function_args}")
            
            # 调用对应的函数
            function_to_call = available_functions[function_name]
            function_result = function_to_call(**function_args)
            
            print(f"   ✅ 结果: {function_result}")
            
            # 添加工具结果
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": function_result
            })
        
        # 第二次调用 AI
        final_response = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages
        )
        
        print(f"\n💬 AI 回复:\n{final_response.choices[0].message.content}")
    else:
        print(f"💬 AI 直接回复:\n{response_message.content}")
    
    print("=" * 60)

# ========== 5. 测试多个场景 ==========
print("=" * 60)
print("🛠️  多工具系统演示")
print("=" * 60)

# 场景1: 天气查询
run_conversation("上海今天天气如何?")

# 场景2: 数学计算
run_conversation("帮我算一下 123 * 456 等于多少")

# 场景3: 信息搜索
run_conversation("什么是 AI Agent?")

# 场景4: 不需要工具
run_conversation("你好,介绍一下你自己")