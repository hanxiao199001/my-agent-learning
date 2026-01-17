"""
记忆系统 Agent - 在任务执行中保存和使用记忆
学习目标:让 Agent 能记住重要信息并在后续步骤中使用
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
        results = [f"{r['title']}: {r['content'][:150]}" for r in response.get('results', [])[:2]]
        return f"总结: {answer}\n详情: " + "; ".join(results) if results else answer
    except Exception as e:
        return f"搜索失败: {str(e)}"

# ========== 记忆类 ==========

class Memory:
    """记忆系统"""
    
    def __init__(self):
        self.facts = []  # 存储事实
        self.steps = []  # 执行步骤历史
        
    def add_fact(self, key, value, importance="normal"):
        """添加一个事实到记忆"""
        fact = {
            "key": key,
            "value": value,
            "importance": importance,
            "step": len(self.steps) + 1
        }
        self.facts.append(fact)
        print(f"💾 记忆已保存: {key} = {value[:100]}...")
        
    def get_fact(self, key):
        """从记忆中获取事实"""
        for fact in reversed(self.facts):  # 从最新的开始找
            if fact['key'] == key:
                return fact['value']
        return None
    
    def get_all_facts(self):
        """获取所有记忆"""
        return self.facts
    
    def add_step(self, action, result):
        """记录执行步骤"""
        self.steps.append({
            "step": len(self.steps) + 1,
            "action": action,
            "result": result[:200]
        })
    
    def summarize(self):
        """总结记忆内容"""
        if not self.facts:
            return "记忆为空"
        
        summary = "📚 当前记忆:\n"
        for fact in self.facts:
            importance_icon = "⭐" if fact['importance'] == "high" else "📌"
            summary += f"{importance_icon} {fact['key']}: {fact['value'][:100]}...\n"
        return summary

# ========== 带记忆的 Agent ==========

def memory_agent(task, max_iterations=6):
    """
    带记忆的动态规划 Agent
    """
    
    print("=" * 80)
    print(f"🎯 任务: {task}")
    print("=" * 80 + "\n")
    
    # 初始化记忆
    memory = Memory()
    
    for iteration in range(max_iterations):
        print(f"\n{'='*80}")
        print(f"🔄 第 {iteration + 1} 轮")
        print("=" * 80 + "\n")
        
        # 显示当前记忆
        if iteration > 0:
            print(memory.summarize() + "\n")
        
        # 决定下一步
        planning_prompt = f"""你是一个智能 Agent,正在执行任务。你有一个记忆系统可以保存重要信息。

原始任务: {task}

当前记忆:
{json.dumps([{'key': f['key'], 'value': f['value'][:100]} for f in memory.get_all_facts()], ensure_ascii=False, indent=2) if memory.get_all_facts() else '(空)'}

已完成的步骤:
{chr(10).join([f"{s['step']}. {s['action']}" for s in memory.steps]) if memory.steps else '(尚未开始)'}

基于以上信息,决定下一步行动。你可以:
1. 使用 web_search 搜索信息
2. 将重要信息保存到记忆 (save_to_memory)
3. 完成任务并给出答案

请用JSON格式回复:
{{
  "status": "continue" 或 "completed",
  "reasoning": "你的思考",
  "action": {{
    "type": "web_search" 或 "save_to_memory" 或 null,
    "query": "搜索内容" (如果是search),
    "memory_key": "记忆键名" (如果是save),
    "memory_value": "要保存的内容" (如果是save),
    "importance": "high" 或 "normal" (如果是save)
  }},
  "final_answer": "最终答案" (如果completed)
}}

记忆使用建议:
- 将关键人名、数据、结论保存到记忆
- 用简洁的 key 命名,如 "nobel_winners_2024"
- 标记重要信息为 "high"

只输出JSON。"""
        
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
        
        print(f"💭 思考: {decision['reasoning']}\n")
        
        # 检查是否完成
        if decision['status'] == 'completed':
            print("=" * 80)
            print("✅ 任务完成!")
            print("=" * 80 + "\n")
            print(decision['final_answer'])
            print("\n" + "=" * 80)
            print("\n📊 最终记忆状态:")
            print(memory.summarize())
            print("=" * 80)
            break
        
        # 执行动作
        action = decision.get('action', {})
        action_type = action.get('type')
        
        if action_type == 'web_search':
            query = action['query']
            print(f"🔍 搜索: {query}\n")
            
            result = web_search(query)
            print(f"📊 结果:\n{result[:400]}...\n")
            
            memory.add_step(f"搜索: {query}", result)
            
        elif action_type == 'save_to_memory':
            key = action['memory_key']
            value = action['memory_value']
            importance = action.get('importance', 'normal')
            
            memory.add_fact(key, value, importance)
            print()
            
        else:
            print("⚠️ 无有效动作")
            break
    
    print("\n" + "=" * 80)

# ========== 测试 ==========

if __name__ == "__main__":
    print("\n🧠 记忆系统 Agent 演示\n")
    
    # 测试:需要记住多个信息的复杂任务
    memory_agent(
        "查找2024年诺贝尔物理学奖得主,记住他们的名字和主要贡献,然后告诉我为什么他们的工作很重要"
    )