"""
使用 Tavily 的完整 Agent
学习目标:用一个强大的搜索 API 就能做很多事
"""

import os
import json
from openai import OpenAI
from dotenv import load_dotenv
from tavily import TavilyClient

load_dotenv()

openai_client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)

tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

# ========== 工具函数 ==========

def web_search(query):
    """使用 Tavily 搜索"""
    try:
        response = tavily_client.search(
            query=query,
            max_results=5,
            include_answer=True
        )
        
        result = {
            "query": query,
            "answer": response.get('answer', '未找到答案'),
            "results": [
                {
                    "title": r['title'],
                    "url": r['url'],
                    "content": r['content'][:300]
                }
                for r in response.get('results', [])[:3]
            ]
        }
        
        return json.dumps(result, ensure_ascii=False)
    
    except Exception as e:
        return json.dumps({"error": f"搜索失败: {str(e)}"}, ensure_ascii=False)

def calculate(expression):
    """数学计算"""
    try:
        # 替换 ^ 为 **
        expression = expression.replace('^', '**')
        result = eval(expression)
        return json.dumps({"result": result, "expression": expression}, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": f"计算错误: {str(e)}"}, ensure_ascii=False)

# ========== 工具描述 ==========
tools = [
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": "在互联网上搜索最新信息。适用于:天气查询、新闻、事实查询、当前事件等任何需要实时信息的问题",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "搜索关键词,要具体清晰"
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
            "description": "执行数学计算,支持加减乘除、幂运算等",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "数学表达式,如: 123*456"
                    }
                },
                "required": ["expression"]
            }
        }
    }
]

available_functions = {
    "web_search": web_search,
    "calculate": calculate
}

# ========== Agent 主函数 ==========
def run_agent(user_input):
    print(f"\n{'='*70}")
    print(f"👤 {user_input}")
    print("-" * 70)
    
    messages = [{"role": "user", "content": user_input}]
    
    # 第一轮:AI 决策
    response = openai_client.chat.completions.create(
        model="deepseek-chat",
        messages=messages,
        tools=tools,
        tool_choice="auto"
    )
    
    response_message = response.choices[0].message
    
    # 处理工具调用
    if response_message.tool_calls:
        print("🤖 AI 调用工具:")
        messages.append(response_message)
        
        for tool_call in response_message.tool_calls:
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)
            
            print(f"   🔧 {function_name}: {function_args}")
            
            # 执行工具
            function_to_call = available_functions[function_name]
            function_result = function_to_call(**function_args)
            
            # 简化显示
            result_preview = function_result[:150] + "..." if len(function_result) > 150 else function_result
            print(f"   ✅ 返回: {result_preview}")
            
            # 添加结果
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": function_result
            })
        
        # 第二轮:AI 整合答案
        final_response = openai_client.chat.completions.create(
            model="deepseek-chat",
            messages=messages
        )
        
        print(f"\n💬 AI 回复:")
        print(final_response.choices[0].message.content)
    else:
        print(f"💬 AI 直接回复:")
        print(response_message.content)
    
    print("=" * 70)

# ========== 测试场景 ==========
if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("🚀 AI Agent 演示 - Powered by Tavily")
    print("=" * 70)
    
    # 测试1: 天气查询(通过搜索)
    run_agent("北京今天天气怎么样?")
    
    # 测试2: 新闻查询
    run_agent("特斯拉最近有什么新闻?")
    
    # 测试3: 数学计算
    run_agent("2的10次方是多少?")
    
    # 测试4: 知识问答
    run_agent("什么是量子计算?")
    
    # 测试5: 组合查询
    run_agent("比较一下 GPT-4 和 Claude 的特点")