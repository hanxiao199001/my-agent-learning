"""
完整的Multi-Agent分析系统
整合所有组件:
- Day 6: Multi-Agent协作
- Day 7: 论坛辩论机制
- Day 8: 报告生成

学习目标: 构建端到端的分析系统
"""

import sys
import os

# 添加路径以导入之前的模块
sys.path.append(os.path.join(os.path.dirname(__file__), '../day6'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../day7'))

from agent_communication import SharedState, MessageBus
from forum_host import ForumHost
from forum_agents import QueryAgent, InsightAgent, MediaAgent
from report_agent import ReportAgent

class IntegratedAnalysisSystem:
    """
    完整的分析系统
    整合: 数据收集 + 论坛辩论 + 报告生成
    """
    
    def __init__(self, topic: str):
        self.topic = topic
        
        print("\n" + "="*70)
        print("🚀 完整分析系统启动")
        print("="*70)
        print(f"📋 分析主题: {topic}\n")
        
        # 1. 基础设施
        self.state = SharedState()
        self.bus = MessageBus()
        
        # 2. 数据收集Agents
        self.query_agent = QueryAgent()
        self.insight_agent = InsightAgent()
        self.media_agent = MediaAgent()
        
        # 3. 论坛主持人
        self.forum_host = ForumHost(topic)
        self.forum_host.max_rounds = 2  # 简化为2轮
        
        # 4. 报告生成Agent
        self.report_agent = ReportAgent()
        
        print("\n✅ 系统初始化完成\n")
    
    def run_analysis(self):
        """执行完整的分析流程"""
        
        # ========== 阶段1: 数据收集 ==========
        print("="*70)
        print("📊 阶段1: 并行数据收集")
        print("="*70 + "\n")
        
        research_data = self._collect_data()
        
        # ========== 阶段2: 论坛辩论 ==========
        print("\n" + "="*70)
        print("🎙️ 阶段2: 专家论坛辩论")
        print("="*70 + "\n")
        
        forum_conclusion = self._run_forum_discussion(research_data)
        
        # ========== 阶段3: 报告生成 ==========
        print("\n" + "="*70)
        print("📝 阶段3: 生成分析报告")
        print("="*70 + "\n")
        
        final_report = self._generate_report(research_data, forum_conclusion)
        
        # ========== 完成 ==========
        print("\n" + "="*70)
        print("✅ 分析完成!")
        print("="*70 + "\n")
        
        return final_report
    
    def _collect_data(self):
        """阶段1: 收集数据"""
        
        # QueryAgent 搜索网络信息
        print("🔍 QueryAgent 正在搜索网络信息...")
        query_context = {
            "round": 1,
            "host_guidance": f"请从网络信息角度分析: {self.topic}",
            "other_statements": []
        }
        query_result = self.query_agent.speak(self.topic, query_context)
        print(f"✅ QueryAgent 完成\n")
        
        # InsightAgent 分析数据
        print("📊 InsightAgent 正在分析数据...")
        insight_context = {
            "round": 1,
            "host_guidance": f"请从数据分析角度评估: {self.topic}",
            "other_statements": [
                {"agent": "QueryAgent", "content": query_result}
            ]
        }
        insight_result = self.insight_agent.speak(self.topic, insight_context)
        print(f"✅ InsightAgent 完成\n")
        
        # MediaAgent 分析舆情
        print("📱 MediaAgent 正在分析舆情...")
        media_context = {
            "round": 1,
            "host_guidance": f"请从舆情角度观察: {self.topic}",
            "other_statements": [
                {"agent": "QueryAgent", "content": query_result},
                {"agent": "InsightAgent", "content": insight_result}
            ]
        }
        media_result = self.media_agent.speak(self.topic, media_context)
        print(f"✅ MediaAgent 完成\n")
        
        return {
            "query": query_result,
            "insight": insight_result,
            "media": media_result
        }
    
    def _run_forum_discussion(self, research_data):
        """阶段2: 论坛辩论"""
        
        # 开场
        self.forum_host.open_forum()
        
        # 收集所有Agent
        agents = [self.query_agent, self.insight_agent, self.media_agent]
        
        # 2轮讨论
        for round_num in range(1, 3):
            print(f"\n{'='*70}")
            print(f"🔄 第 {round_num} 轮讨论")
            print(f"{'='*70}\n")
            
            round_statements = []
            
            for agent in agents:
                context = {
                    "round": round_num,
                    "host_guidance": self.forum_host.discussion_history[-1]["content"] if round_num > 1 and self.forum_host.discussion_history else "",
                    "other_statements": round_statements.copy()
                }
                
                statement = agent.speak(self.topic, context)
                round_statements.append({
                    "agent": agent.name,
                    "content": statement
                })
                
                emoji = '🔍' if agent.name == 'QueryAgent' else '📊' if agent.name == 'InsightAgent' else '📱'
                print(f"{emoji} {agent.name}:")
                print(f"{statement[:200]}...\n")
            
            # 主持人引导
            if round_num < 2:
                guidance = self.forum_host.guide_discussion(round_statements)
                self.forum_host.discussion_history.append({
                    "agent": "Host",
                    "content": guidance
                })
            else:
                self.forum_host.discussion_history.extend([
                    {"agent": s["agent"], "content": s["content"]}
                    for s in round_statements
                ])
        
        # 总结
        conclusion = self.forum_host.conclude_discussion()
        
        return conclusion
    
    def _generate_report(self, research_data, forum_conclusion):
        """阶段3: 生成报告"""
        
        report = self.report_agent.generate_report(
            topic=self.topic,
            research_data=research_data,
            forum_conclusion=forum_conclusion
        )
        
        # 保存报告
        filename = self.report_agent.save_report(report, self.topic)
        
        # 显示报告
        print("="*70)
        print("📊 最终分析报告")
        print("="*70)
        print(report[:1000] + "\n...(完整报告已保存)\n")
        print("="*70)
        
        return report


# ========== 运行完整系统 ==========

if __name__ == "__main__":
    # 创建分析系统
    system = IntegratedAnalysisSystem(
        topic="区块链技术在金融领域的应用前景"
    )
    
    # 执行完整分析
    final_report = system.run_analysis()
    
    print("\n🎉 系统运行完成!")
    print("📁 完整报告已保存到 reports/ 目录")