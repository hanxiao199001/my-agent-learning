"""
真实 API 集成 - 天气和搜索
学习目标:调用真实的外部 API
"""

import os
import json
import requests
from openai import OpenAI
from dotenv import load_dotenv
from tavily import TavilyClient

load_dotenv()

# 初始化客户端
openai_client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)

tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

# ========== 1. 真实天气 API ==========
def get_weather(city):
    """
    调用 OpenWeatherMap API 获取真实天气
    """
    api_key = os.getenv("OPENWEATHER_API_KEY")
    
    # OpenWeatherMap API 需要城市的英文名
    city_map = {
        "北京": "Beijing",
        "上海": "Shanghai", 
        "深圳": "Shenzhen",
        "广州": "Guangzhou",
        "杭州": "Hangzhou"
    }
    
    english_city = city_map.get(city, city)
    
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={english_city}&appid={api_key}&units=metric&lang=zh_cn"
        response = requests.get(url, timeout=5)
        data = response.json()
        
        if response.status_code == 200:
            result = {
                "city": city,
                "temperature": f"{data['main']['temp']}°C",
                "feels_like": f"{data['main']['feels_like']}°C",
                "condition": data['weather'][0]['description'],
                "humidity": f"{data['main']['humidity']}%",
                "wind_speed": f"{data['wind']['speed']} m/s"
            }
            return json.dumps(result, ensure_ascii=False)
        else:
            return json.dumps({"error": f"无法获取{city}的天气信息"}, ensure_ascii=False)
    
    except Exception as e:
        return json.dumps({"error": f"API 调用失败: {str(e)}"}, ensure_ascii=False)

# ========== 2. 真实搜索 API ==========
def web_search(query):
    """
    使用 Tavily 进行网络搜索
    """
    try:
        response = tavily_client.search(
            query=query,
            max_results=3,  # 最多返回3个结果
            include_answer=True  # 包含 AI 总结的答案
        )
        
        # 提取关键信息
        result = {
            "query": query,
            "answer": response.get('answer', ''),
            "results": [
                {
                    "title": r['title'],
                    "url": r['url'],
                    "content": r['content'][:200] + "..."  # 截取前200字符
                }
                for r in response.get('results', [])[:3]
            ]
        }
        
        return json.dumps(result, ensure_ascii=False)
    
    except Exception as e:
        return json.dumps({"error": f"搜索失败: {str(e)}"}, ensure_ascii=False)

# ========== 3. 计算器(保留) ==========
def calculate(expression):
    """数学计算"""
    try:
        result = eval(expression)
        return json.dumps({"result": result, "expression": expression}, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": f"计算错误: {str(e)}"}, ensure_ascii=False)

# ========== 4. 定义工具描述 ==========
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "获取指定城市的实时天气信息,包括温度、湿度、风速等",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "城市名称,如:北京、上海、深圳"
                    }
                },
                "required": ["city"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": "在互联网上搜索最新信息,适用于需要实时数据或最新新闻的查询",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "搜索关键词或问题"
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculate",
            "description": "执行数学计算",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "数学表达式"
                    }
                },
                "required": ["expression"]
            }
        }
    }
]

# ========== 5. 工具映射 ==========
available_functions = {
    "get_weather": get_weather,
    "web_search": web_search,
    "calculate": calculate
}

# ========== 6. 对话处理函数 ==========
def run_agent(user_input):
    print(f"\n{'='*60}")
    print(f"👤 用户: {user_input}")
    print("-" * 60)
    
    messages = [{"role": "user", "content": user_input}]
    
    response = openai_client.chat.completions.create(
        model="deepseek-chat",
        messages=messages,
        tools=tools,
        tool_choice="auto"
    )
    
    response_message = response.choices[0].message
    
    if response_message.tool_calls:
        print("🤖 AI 调用工具:")
        messages.append(response_message)
        
        for tool_call in response_message.tool_calls:
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)
            
            print(f"   📌 {function_name}({function_args})")
            
            function_to_call = available_functions[function_name]
            function_result = function_to_call(**function_args)
            
            print(f"   ✅ {function_result[:100]}...")
            
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": function_result
            })
        
        final_response = openai_client.chat.completions.create(
            model="deepseek-chat",
            messages=messages
        )
        
        print(f"\n💬 AI:\n{final_response.choices[0].message.content}")
    else:
        print(f"💬 AI:\n{response_message.content}")
    
    print("=" * 60)

# ========== 7. 测试真实 API ==========
if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("🌐 真实 API 工具测试")
    print("=" * 60)
    
    # 测试1: 真实天气
    run_agent("北京现在天气怎么样?")
    
    # 测试2: 网络搜索
    run_agent("2024年诺贝尔物理学奖得主是谁?")
    
    # 测试3: 计算
    run_agent("计算 999 * 888")
    
    # 测试4: 组合使用
    run_agent("搜索一下今天有什么重要新闻")