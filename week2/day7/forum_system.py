"""
完整论坛系统
整合: ForumHost + ForumAgents
学习目标: 端到端的多Agent辩论系统
"""

from forum_host import ForumHost
from forum_agents import QueryAgent, InsightAgent, MediaAgent
from typing import List, Dict

class ForumSystem:
    """
    完整的论坛系统
    类似 BettaFish 的核心机制
    """
    
    def __init__(self, topic: str, max_rounds: int = 3):
        self.topic = topic
        self.max_rounds = max_rounds
        
        # 创建主持人
        self.host = ForumHost(topic)
        self.host.max_rounds = max_rounds
        
        # 创建参与Agents
        self.agents = [
            QueryAgent(),
            InsightAgent(),
            MediaAgent()
        ]
        
        print("\n" + "="*70)
        print("🎙️ 论坛系统已就绪")
        print(f"📋 主题: {topic}")
        print(f"👥 参与者: {len(self.agents)} 个专家")
        print(f"🔄 最大轮次: {max_rounds}")
        print("="*70 + "\n")
    
    def run_forum(self):
        """运行完整的论坛讨论"""
        
        # 1. 开场
        self.host.open_forum()
        
        # 2. 多轮讨论
        for round_num in range(1, self.max_rounds + 1):
            print(f"\n{'='*70}")
            print(f"🔄 第 {round_num} 轮讨论")
            print(f"{'='*70}\n")
            
            # 收集本轮发言
            round_statements = []
            
            for agent in self.agents:
                # 构建上下文
                context = {
                    "round": round_num,
                    "host_guidance": self.host.discussion_history[-1]["content"] if round_num > 1 and self.host.discussion_history else "",
                    "other_statements": round_statements.copy()  # 其他Agent的发言
                }
                
                # Agent发言
                statement = agent.speak(self.topic, context)
                
                # 记录发言
                round_statements.append({
                    "agent": agent.name,
                    "content": statement
                })
                
                # 显示发言
                print(f"{'🔍' if agent.name == 'QueryAgent' else '📊' if agent.name == 'InsightAgent' else '📱'} {agent.name}:")
                print(f"{statement}\n")
                print("-"*70 + "\n")
            
            # 主持人引导(如果不是最后一轮)
            if round_num < self.max_rounds:
                guidance = self.host.guide_discussion(round_statements)
                # 记录主持人引导
                self.host.discussion_history.append({
                    "agent": "Host",
                    "content": guidance
                })
            else:
                # 最后一轮直接记录
                self.host.discussion_history.extend([
                    {"agent": s["agent"], "content": s["content"]}
                    for s in round_statements
                ])
        
        # 3. 总结
        print("\n" + "="*70)
        print("📊 论坛总结")
        print("="*70 + "\n")
        
        conclusion = self.host.conclude_discussion()
        
        return conclusion


# ========== 运行完整论坛 ==========

if __name__ == "__main__":
    # 创建论坛系统
    forum = ForumSystem(
        topic="AI技术对教育领域的变革",
        max_rounds=3
    )
    
    # 运行讨论
    result = forum.run_forum()
    
    print("\n" + "="*70)
    print("✅ 论坛讨论结束")
    print("="*70)