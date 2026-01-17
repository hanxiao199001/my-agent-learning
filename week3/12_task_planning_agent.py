"""
任务规划 Agent - 自动分解复杂任务
学习目标:让 AI 学会把大任务拆成小任务并逐步执行
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
        response = tavily_client.search(query=query, max_results=3, include_answer=True)
        
        # 提取答案和结果
        answer = response.get('answer', '')
        results = [
            f"来源: {r['title']}\n内容: {r['content'][:200]}"
            for r in response.get('results', [])[:2]
        ]
        
        output = f"AI总结: {answer}\n\n详细信息:\n" + "\n\n".join(results)
        return output
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

# ========== 任务规划 Agent ==========

def planning_agent(task):
    """
    任务规划 Agent
    1. 分析任务复杂度
    2. 制定执行计划
    3. 逐步执行
    4. 整合结果
    """
    
    print("=" * 80)
    print(f"🎯 收到任务: {task}")
    print("=" * 80)
    
    # ========== 阶段1: 制定计划 ==========
    print("\n📋 阶段1: 制定执行计划\n")
    
    planning_prompt = f"""你是一个任务规划专家。用户给你一个任务,你需要将其分解成可执行的步骤。

可用工具:
- web_search: 搜索互联网信息
- calculate: 数学计算

任务: {task}

请分析这个任务,然后制定执行计划。按以下JSON格式输出:

{{
  "task_analysis": "任务分析:这个任务需要...",
  "steps": [
    {{"step": 1, "action": "web_search", "query": "具体搜索内容", "purpose": "为什么要这样做"}},
    {{"step": 2, "action": "web_search", "query": "...", "purpose": "..."}},
    ...
  ],
  "final_goal": "最终要达成什么目标"
}}

只输出JSON,不要其他内容。"""
    
    response = openai_client.chat.completions.create(
        model="deepseek-chat",
        messages=[{"role": "user", "content": planning_prompt}],
        temperature=0.3
    )
    
    plan_text = response.choices[0].message.content
    
    # 提取JSON
    try:
        # 移除可能的markdown标记
        plan_text = plan_text.replace('```json', '').replace('```', '').strip()
        plan = json.loads(plan_text)
    except:
        print("❌ 计划解析失败,使用简化模式")
        return
    
    print(f"📊 任务分析:\n{plan['task_analysis']}\n")
    print(f"🎯 最终目标: {plan['final_goal']}\n")
    print(f"📝 执行计划: 共 {len(plan['steps'])} 个步骤\n")
    
    for step in plan['steps']:
        print(f"  步骤{step['step']}: {step['action']}('{step['query'][:50]}...')")
        print(f"           目的: {step['purpose']}\n")
    
    # ========== 阶段2: 执行计划 ==========
    print("\n" + "=" * 80)
    print("🚀 阶段2: 执行计划")
    print("=" * 80 + "\n")
    
    results = []
    
    for step_info in plan['steps']:
        step_num = step_info['step']
        action = step_info['action']
        query = step_info['query']
        
        print(f"📍 执行步骤 {step_num}/{len(plan['steps'])}")
        print(f"   动作: {action}")
        print(f"   参数: {query}")
        print(f"   目的: {step_info['purpose']}\n")
        
        # 执行工具
        if action == "web_search":
            result = web_search(query)
        elif action == "calculate":
            result = calculate(query)
        else:
            result = f"未知工具: {action}"
        
        print(f"✅ 结果:\n{result[:300]}...\n")
        print("-" * 80 + "\n")
        
        # 保存结果
        results.append({
            "step": step_num,
            "action": action,
            "query": query,
            "result": result
        })
    
    # ========== 阶段3: 整合结果 ==========
    print("=" * 80)
    print("📊 阶段3: 整合所有信息")
    print("=" * 80 + "\n")
    
    # 构建整合提示
    synthesis_prompt = f"""你刚刚执行了一个多步骤任务。现在需要整合所有信息,给出最终答案。

原始任务: {task}

执行的步骤和结果:
"""
    
    for r in results:
        synthesis_prompt += f"\n步骤{r['step']}: {r['action']}('{r['query']}')\n"
        synthesis_prompt += f"结果: {r['result'][:500]}\n"
        synthesis_prompt += "-" * 40 + "\n"
    
    synthesis_prompt += f"""
请根据以上所有信息,完成原始任务: {task}

要求:
1. 整合所有步骤的信息
2. 给出清晰、完整的答案
3. 用结构化的方式呈现(可以用标题、列表等)
4. 如果某些信息不足,说明需要进一步研究什么
"""
    
    print("🤔 AI 正在整合信息...\n")
    
    final_response = openai_client.chat.completions.create(
        model="deepseek-chat",
        messages=[{"role": "user", "content": synthesis_prompt}],
        temperature=0.5
    )
    
    final_answer = final_response.choices[0].message.content
    
    print("=" * 80)
    print("✨ 最终答案")
    print("=" * 80 + "\n")
    print(final_answer)
    print("\n" + "=" * 80)

# ========== 测试场景 ==========

if __name__ == "__main__":
    print("\n🧠 任务规划 Agent 演示\n")
    
    # 测试1: 中等复杂度任务
    print("\n" + "🔷" * 40 + "\n")
    planning_agent("介绍一下 Rust 编程语言的特点和主要应用领域")
    
    print("\n\n" + "🔷" * 40 + "\n")
    
    # 测试2: 更复杂的研究任务
    planning_agent("研究2024年诺贝尔物理学奖得主的背景和主要贡献,并说明这项工作为什么重要")