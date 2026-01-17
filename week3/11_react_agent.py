"""
ReAct 模式 Agent - 显式思维链
学习目标:让 AI 显示思考过程,更透明的决策
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
    """网络搜索"""
    try:
        response = tavily_client.search(query=query, max_results=3)
        results = [
            f"标题: {r['title']}\n内容: {r['content'][:200]}"
            for r in response.get('results', [])[:3]
        ]
        return "\n\n".join(results)
    except Exception as e:
        return f"搜索失败: {str(e)}"

def calculate(expression):
    """数学计算"""
    try:
        expression = expression.replace('^', '**')
        result = eval(expression)
        return f"计算结果: {result}"
    except Exception as e:
        return f"计算错误: {str(e)}"

# ========== 工具映射 ==========
tools = {
    "web_search": web_search,
    "calculate": calculate
}

# ========== ReAct Agent ==========

def react_agent(question, max_steps=5):
    """
    ReAct 模式 Agent
    max_steps: 最多思考几轮
    """
    print("=" * 70)
    print(f"🎯 任务: {question}")
    print("=" * 70)
    
    # 系统提示词 - 教 AI 使用 ReAct 格式
    system_prompt = """你是一个使用 ReAct (Reasoning + Acting) 模式的 AI Agent。

你必须按照以下格式一步一步思考和行动:

Thought: [分析当前情况,思考下一步该做什么]
Action: [选择要执行的动作] tool_name: arguments

⚠️ 重要:
- 写完 Action 后立即停止
- 不要预测 Observation 的结果
- 不要在一轮中写多个 Thought/Action
- 每次只执行一个动作,然后等待真实的 Observation

可用工具:
- web_search: query - 搜索互联网信息
- calculate: expression - 数学计算(用 ** 表示幂运算)

格式示例:
Thought: 我需要先计算15的平方
Action: calculate: 15**2

(然后停止,等待系统返回真实的 Observation)
"""
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": question}
    ]
    
    # ReAct 循环
    for step in range(max_steps):
        print(f"\n--- 第 {step + 1} 轮思考 ---")
        
        # 调用 AI
        response = openai_client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            temperature=0  # 降低随机性,更稳定
        )
        
        ai_response = response.choices[0].message.content
        print(ai_response)
        
        # 检查是否完成
        if "Answer:" in ai_response:
            print("\n" + "=" * 70)
            print("✅ 任务完成!")
            print("=" * 70)
            break
        
        # 解析 Action
        if "Action:" in ai_response:
            # 提取 Action 行
            action_line = [line for line in ai_response.split('\n') if line.startswith('Action:')][0]
            action_content = action_line.replace('Action:', '').strip()
            
            # 解析工具名和参数
            if ':' in action_content:
                tool_name, arguments = action_content.split(':', 1)
                tool_name = tool_name.strip()
                arguments = arguments.strip()
                
                # 执行工具
                if tool_name in tools:
                    print(f"\n🔧 执行: {tool_name}({arguments})")
                    result = tools[tool_name](arguments)
                    print(f"📊 结果:\n{result}\n")
                    
                    # 添加 Observation 到对话
                    messages.append({"role": "assistant", "content": ai_response})
                    messages.append({"role": "user", "content": f"Observation: {result}"})
                else:
                    print(f"❌ 未知工具: {tool_name}")
                    break
            else:
                print("❌ Action 格式错误")
                break
        else:
            # 没有 Action,添加提示继续
            messages.append({"role": "assistant", "content": ai_response})
            messages.append({"role": "user", "content": "请继续使用 Thought/Action/Observation 格式"})
    
    print("\n" + "=" * 70)

# ========== 测试 ==========

if __name__ == "__main__":
    print("\n🧠 ReAct Agent 演示\n")
    
    # 测试1: 简单查询
    react_agent("北京今天天气怎么样?")
    
    print("\n\n")
    
    # 测试2: 需要多步推理
    react_agent("计算 15 的平方,然后搜索这个数字有什么特殊含义")
    
    print("\n\n")
    
    # 测试3: 复杂任务
    react_agent("2024年诺贝尔物理学奖得主是谁?他们的主要贡献是什么?")