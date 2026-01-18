"""
Multi-Agent 协作系统
场景: 研究助手系统
- ResearchAgent: 负责搜索资料
- AnalysisAgent: 负责分析总结

学习目标:
1. Agent间任务分工
2. 协作完成复杂任务
3. 结果整合
"""

import os
from openai import OpenAI
from dotenv import load_dotenv
from typing import Dict, List, Any
from agent_communication import Message, SharedState, MessageBus

load_dotenv()

class ResearchAgent:
    """
    研究Agent - 负责搜索信息
    类似 BettaFish 的 Query Agent
    """
    
    def __init__(self, name: str, state: SharedState, bus: MessageBus):
        self.name = name
        self.state = state
        self.bus = bus
        self.client = OpenAI(
            api_key=os.getenv("DEEPSEEK_API_KEY"),
            base_url="https://api.deepseek.com"
        )
        
        # 订阅消息
        self.bus.subscribe(self.name, self.handle_message)
        
        print(f"🔍 {self.name} 已启动 (研究专家)")
    
    def handle_message(self, message: Message):
        """处理收到的消息"""
        if message.msg_type == "research_request":
            print(f"\n📥 {self.name} 收到研究请求: {message.content}")
            self.conduct_research(message.content, message.sender)
    
    def conduct_research(self, topic: str, requester: str):
        """执行研究任务"""
        print(f"🔍 {self.name} 正在研究: {topic}")
        
        # 使用LLM生成研究内容
        prompt = f"""你是研究专家。请针对主题"{topic}"提供:
1. 核心概念 (2-3句话)
2. 关键数据 (2-3个要点)
3. 重要趋势 (1-2个)

保持简洁,每部分不超过100字。"""

        response = self.client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        
        research_result = response.choices[0].message.content
        
        # 更新共享状态
        self.state.update(f"research_{topic}", research_result, self.name)
        
        # 发送结果给请求者
        result_msg = Message(
            sender=self.name,
            receiver="AnalysisAgent",
            content={
                "topic": topic,
                "research": research_result
            },
            msg_type="research_complete"
        )
        self.bus.publish(result_msg)
        
        print(f"✅ {self.name} 研究完成")


class AnalysisAgent:
    """
    分析Agent - 负责综合分析
    类似 BettaFish 的 Insight Agent
    """
    
    def __init__(self, name: str, state: SharedState, bus: MessageBus):
        self.name = name
        self.state = state
        self.bus = bus
        self.client = OpenAI(
            api_key=os.getenv("DEEPSEEK_API_KEY"),
            base_url="https://api.deepseek.com"
        )
        
        self.research_results = []  # 收集的研究结果
        
        # 订阅消息
        self.bus.subscribe(self.name, self.handle_message)
        
        print(f"📊 {self.name} 已启动 (分析专家)")
    
    def handle_message(self, message: Message):
        """处理收到的消息"""
        if message.msg_type == "research_complete":
            print(f"\n📥 {self.name} 收到研究结果")
            self.research_results.append(message.content)
            
            # 检查是否收集完所有结果
            if self.state.get("expected_research_count"):
                if len(self.research_results) >= self.state.get("expected_research_count"):
                    self.generate_analysis()
    
    def generate_analysis(self):
        """生成综合分析"""
        print(f"\n📊 {self.name} 正在生成综合分析...")
        
        # 整合所有研究结果
        all_research = "\n\n".join([
            f"主题: {r['topic']}\n{r['research']}"
            for r in self.research_results
        ])
        
        # 使用LLM生成综合分析
        prompt = f"""你是分析专家。基于以下研究结果:

{all_research}

请提供综合分析报告:
1. 核心洞察 (3-4句话)
2. 关联发现 (2-3点)
3. 建议行动 (2点)

保持专业和简洁。"""

        response = self.client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.6
        )
        
        analysis = response.choices[0].message.content
        
        # 更新状态
        self.state.update("final_analysis", analysis, self.name)
        
        # 广播完成消息
        complete_msg = Message(
            sender=self.name,
            receiver="all",
            content="分析报告已完成",
            msg_type="analysis_complete"
        )
        self.bus.publish(complete_msg)
        
        print(f"✅ {self.name} 分析完成")
        
        return analysis


class Coordinator:
    """
    协调者 - 任务调度
    类似 BettaFish 的主控制器
    """
    
    def __init__(self, state: SharedState, bus: MessageBus):
        self.state = state
        self.bus = bus
        self.name = "Coordinator"
        
        print(f"🎯 {self.name} 已启动")
    
    def run_task(self, main_topic: str, sub_topics: List[str]):
        """
        执行复杂任务
        1. 分配研究任务给 ResearchAgent
        2. AnalysisAgent 等待所有结果
        3. 生成综合报告
        """
        print(f"\n{'='*70}")
        print(f"🎯 开始任务: {main_topic}")
        print(f"{'='*70}")
        print(f"📋 子任务: {', '.join(sub_topics)}\n")
        
        # 设置预期的研究任务数
        self.state.update("expected_research_count", len(sub_topics), self.name)
        
        # 分配研究任务
        for topic in sub_topics:
            msg = Message(
                sender=self.name,
                receiver="ResearchAgent",
                content=topic,
                msg_type="research_request"
            )
            self.bus.publish(msg)


# ========== 测试完整系统 ==========

def test_multi_agent():
    """测试多Agent协作"""
    
    print("\n" + "="*70)
    print("🚀 Multi-Agent 协作系统启动")
    print("="*70 + "\n")
    
    # 1. 创建基础设施
    state = SharedState()
    bus = MessageBus()
    
    # 2. 创建Agents
    research_agent = ResearchAgent("ResearchAgent", state, bus)
    analysis_agent = AnalysisAgent("AnalysisAgent", state, bus)
    coordinator = Coordinator(state, bus)
    
    # 3. 执行任务
    main_topic = "AI技术发展趋势"
    sub_topics = [
        "大语言模型的最新进展",
        "AI在医疗领域的应用",
        "AI Agent技术的发展"
    ]
    
    coordinator.run_task(main_topic, sub_topics)
    
    # 等待任务完成
    import time
    max_wait = 60  # 最多等待60秒
    start_time = time.time()
    
    while not state.get("final_analysis"):
        if time.time() - start_time > max_wait:
            print("⏰ 任务超时")
            break
        time.sleep(1)
    
    # 4. 显示最终结果
    print("\n" + "="*70)
    print("📊 最终分析报告")
    print("="*70 + "\n")
    
    final_analysis = state.get("final_analysis")
    if final_analysis:
        print(final_analysis)
    else:
        print("未能生成分析报告")
    
    print("\n" + "="*70)
    print("✅ 任务完成")
    print("="*70)
    
    # 5. 显示系统状态
    state.print_status()


if __name__ == "__main__":
    test_multi_agent()