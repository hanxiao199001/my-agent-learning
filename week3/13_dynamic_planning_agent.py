"""
动态任务规划 Agent - 根据中间结果调整计划
学习目标:让 Agent 能在执行过程中重新规划
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
        answer = response.get('answer', '')
        results = [f"{r['title']}: {r['content'][:200]}" for r in response.get('results', [])[:2]]
        return f"总结: {answer}\n\n详情:\n" + "\n".join(results) if results else answer
    except Exception as e:
        return f"搜索失败: {str(e)}"

# ========== 动态规划 Agent ==========

def dynamic_agent(task, max_iterations=5):
    """
    动态规划 Agent - 边执行边规划
    """
    
    print("=" * 80)
    print(f"🎯 任务: {task}")
    print("=" * 80 + "\n")
    
    # 初始化
    context = {
        "task": task,
        "completed_steps": [],
        "findings": []
    }
    
    for iteration in range(max_iterations):
        print(f"\n{'='*80}")
        print(f"🔄 第 {iteration + 1} 轮规划与执行")
        print("=" * 80 + "\n")
        
        # 决定下一步
        planning_prompt = f"""你是一个任务规划专家。根据当前进度,决定下一步行动。

原始任务: {task}

已完成的步骤:
{chr(10).join([f"- {s}" for s in context['completed_steps']]) if context['completed_steps'] else "（尚未开始）"}

已获得的信息:
{chr(10).join([f"- {f[:200]}..." for f in context['findings']]) if context['findings'] else "（暂无）"}

基于以上信息,请判断:
1. 任务是否已完成? 如果完成,返回最终答案
2. 如果未完成,下一步应该做什么?

请用JSON格式回复:
{{
  "status": "completed" 或 "continue",
  "reasoning": "你的思考过程",
  "next_action": {{"tool": "web_search", "query": "具体搜索内容"}} 或 null,
  "final_answer": "最终答案" 或 null
}}

只输出JSON,不要其他内容。"""
        
        response = openai_client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": planning_prompt}],
            temperature=0.3
        )
        
        decision_text = response.choices[0].message.content.replace('```json', '').replace('```', '').strip()
        
        try:
            decision = json.loads(decision_text)
        except:
            print("❌ 决策解析失败")
            break
        
        print(f"💭 AI 思考: {decision['reasoning']}\n")
        
        # 检查是否完成
        if decision['status'] == 'completed':
            print("=" * 80)
            print("✅ 任务完成!")
            print("=" * 80 + "\n")
            print(decision['final_answer'])
            print("\n" + "=" * 80)
            break
        
        # 执行下一步
        if decision['next_action']:
            action = decision['next_action']
            query = action['query']
            
            print(f"🔧 执行: web_search('{query}')\n")
            
            result = web_search(query)
            print(f"📊 结果:\n{result[:400]}...\n")
            
            # 更新上下文
            context['completed_steps'].append(f"搜索: {query}")
            context['findings'].append(result)
        else:
            print("⚠️ 无下一步行动")
            break
    
    print("\n" + "=" * 80)

# ========== 测试 ==========

if __name__ == "__main__":
    print("\n🧠 动态规划 Agent 演示\n")
    
    # 测试:需要多步推理的任务
    dynamic_agent(
        "查找2024年诺贝尔物理学奖得主,然后搜索他们各自的主要学术贡献"
    )
