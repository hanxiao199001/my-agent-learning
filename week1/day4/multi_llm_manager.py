"""
多 LLM 管理器 - 模拟 BettaFish 架构
学习目标:
1. 管理多个不同的 LLM API
2. 实现自动降级和重试
3. 成本追踪和优化
4. 为不同任务选择最佳模型
"""

import os
from openai import OpenAI
from dotenv import load_dotenv
from typing import Dict, Optional, Literal
import time
from datetime import datetime

load_dotenv()

# ========== LLM 客户端封装 ==========

class LLMClient:
    """LLM 客户端基类"""
    
    def __init__(self, name: str, api_key: str, base_url: str, model: str):
        self.name = name
        self.model = model
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.call_count = 0
        self.total_tokens = 0
        
    def chat(self, messages: list, temperature: float = 0.7, max_retries: int = 3):
        """调用 LLM"""
        for attempt in range(max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=temperature
                )
                
                # 统计
                self.call_count += 1
                if hasattr(response, 'usage'):
                    self.total_tokens += response.usage.total_tokens
                
                return response.choices[0].message.content
                
            except Exception as e:
                print(f"❌ [{self.name}] 调用失败 (尝试 {attempt + 1}/{max_retries}): {str(e)}")
                if attempt == max_retries - 1:
                    raise
                time.sleep(2 ** attempt)  # 指数退避
        
    def get_stats(self):
        """获取统计信息"""
        return {
            "name": self.name,
            "calls": self.call_count,
            "tokens": self.total_tokens
        }

# ========== 专业化 LLM 客户端 ==========

class InsightLLM(LLMClient):
    """Insight Engine - 数据分析专用 (Kimi)"""
    
    def __init__(self):
        # 如果没有 Kimi,先用 DeepSeek 代替
        api_key = os.getenv("INSIGHT_ENGINE_API_KEY") or os.getenv("DEEPSEEK_API_KEY")
        base_url = os.getenv("INSIGHT_ENGINE_BASE_URL", "https://api.deepseek.com")
        model = os.getenv("INSIGHT_ENGINE_MODEL_NAME", "deepseek-chat")
        
        super().__init__("Insight(Kimi)", api_key, base_url, model)
        self.specialty = "数据分析、SQL生成、统计推理"

class MediaLLM(LLMClient):
    """Media Engine - 多模态分析 (Gemini)"""
    
    def __init__(self):
        # 如果没有 Gemini,用 DeepSeek 代替
        api_key = os.getenv("MEDIA_ENGINE_API_KEY") or os.getenv("DEEPSEEK_API_KEY")
        base_url = os.getenv("MEDIA_ENGINE_BASE_URL", "https://api.deepseek.com")
        model = os.getenv("MEDIA_ENGINE_MODEL_NAME", "deepseek-chat")
        
        super().__init__("Media(Gemini)", api_key, base_url, model)
        self.specialty = "多模态理解、图文分析"

class QueryLLM(LLMClient):
    """Query Engine - 搜索和推理 (DeepSeek)"""
    
    def __init__(self):
        api_key = os.getenv("QUERY_ENGINE_API_KEY") or os.getenv("DEEPSEEK_API_KEY")
        base_url = os.getenv("QUERY_ENGINE_BASE_URL", "https://api.deepseek.com")
        model = os.getenv("QUERY_ENGINE_MODEL_NAME", "deepseek-chat")
        
        super().__init__("Query(DeepSeek)", api_key, base_url, model)
        self.specialty = "深度推理、逻辑分析"

class ReportLLM(LLMClient):
    """Report Engine - 报告生成 (Gemini)"""
    
    def __init__(self):
        api_key = os.getenv("REPORT_ENGINE_API_KEY") or os.getenv("DEEPSEEK_API_KEY")
        base_url = os.getenv("REPORT_ENGINE_BASE_URL", "https://api.deepseek.com")
        model = os.getenv("REPORT_ENGINE_MODEL_NAME", "deepseek-chat")
        
        super().__init__("Report(Gemini)", api_key, base_url, model)
        self.specialty = "内容生成、报告撰写"

class ForumLLM(LLMClient):
    """Forum Host - 协调和综合 (Qwen)"""
    
    def __init__(self):
        api_key = os.getenv("FORUM_HOST_API_KEY") or os.getenv("DEEPSEEK_API_KEY")
        base_url = os.getenv("FORUM_HOST_BASE_URL", "https://api.deepseek.com")
        model = os.getenv("FORUM_HOST_MODEL_NAME", "deepseek-chat")
        
        super().__init__("Forum(Qwen)", api_key, base_url, model)
        self.specialty = "协调综合、冲突解决"

# ========== LLM 管理器 ==========

class MultiLLMManager:
    """
    多 LLM 管理器
    模拟 BettaFish 的多模型架构
    """
    
    def __init__(self):
        print("🚀 初始化多 LLM 管理器...")
        
        # 初始化所有 LLM
        self.llms = {
            'insight': InsightLLM(),
            'media': MediaLLM(),
            'query': QueryLLM(),
            'report': ReportLLM(),
            'forum': ForumLLM()
        }
        
        print("✅ 5 个专业 LLM 已就绪\n")
        for name, llm in self.llms.items():
            print(f"   📌 {llm.name}: {llm.specialty}")
    
    def call_agent(
        self, 
        agent_type: Literal['insight', 'media', 'query', 'report', 'forum'],
        task: str,
        context: str = "",
        temperature: float = 0.7
    ) -> str:
        """
        调用指定 Agent 的 LLM
        
        Args:
            agent_type: Agent 类型
            task: 任务描述
            context: 上下文信息
            temperature: 温度参数
        """
        llm = self.llms[agent_type]
        
        # 构建专业化提示
        system_prompt = f"""你是 BettaFish 系统的 {llm.name}。

你的专长: {llm.specialty}

请根据你的专业能力完成任务。"""
        
        messages = [
            {"role": "system", "content": system_prompt}
        ]
        
        if context:
            messages.append({"role": "user", "content": f"背景信息:\n{context}"})
        
        messages.append({"role": "user", "content": f"任务:\n{task}"})
        
        print(f"\n🤖 调用 [{llm.name}]")
        print(f"   任务: {task[:50]}...")
        
        result = llm.chat(messages, temperature)
        
        print(f"   ✅ 完成")
        
        return result
    
    def parallel_analysis(self, topic: str) -> Dict[str, str]:
        """
        并行分析 - 多个 Agent 同时工作
        模拟 BettaFish 的并行架构
        """
        print(f"\n{'='*60}")
        print(f"🔄 并行分析主题: {topic}")
        print(f"{'='*60}")
        
        results = {}
        
        # Agent 1: Insight - 数据视角
        results['insight'] = self.call_agent(
            'insight',
            f"从数据分析角度,分析主题: {topic}",
            temperature=0.3
        )
        
        # Agent 2: Query - 搜索视角
        results['query'] = self.call_agent(
            'query',
            f"从信息检索角度,需要搜索什么来了解: {topic}",
            temperature=0.5
        )
        
        # Agent 3: Media - 内容视角
        results['media'] = self.call_agent(
            'media',
            f"从内容分析角度,这个主题的关键要素: {topic}",
            temperature=0.7
        )
        
        return results
    
    def forum_synthesis(self, agent_results: Dict[str, str]) -> str:
        """
        Forum 综合 - 整合多个 Agent 的结果
        模拟 BettaFish 的 Forum Host
        """
        print(f"\n{'='*60}")
        print(f"🎯 Forum Host 综合分析")
        print(f"{'='*60}")
        
        # 构建综合提示
        synthesis_prompt = "请综合以下三个专业 Agent 的分析,给出完整结论:\n\n"
        
        for agent_name, result in agent_results.items():
            synthesis_prompt += f"【{agent_name.upper()} Agent 分析】:\n{result}\n\n"
        
        synthesis_prompt += "请整合以上观点,识别共识和差异,给出综合结论。"
        
        final_result = self.call_agent(
            'forum',
            synthesis_prompt,
            temperature=0.5
        )
        
        return final_result
    
    def generate_report(self, synthesis: str, topic: str) -> str:
        """
        生成报告 - Report Engine
        """
        print(f"\n{'='*60}")
        print(f"📝 生成最终报告")
        print(f"{'='*60}")
        
        report = self.call_agent(
            'report',
            f"基于以下综合分析,撰写一份关于'{topic}'的简短报告:\n\n{synthesis}",
            temperature=0.6
        )
        
        return report
    
    def print_statistics(self):
        """打印统计信息"""
        print(f"\n{'='*60}")
        print("📊 LLM 使用统计")
        print(f"{'='*60}")
        
        total_calls = 0
        total_tokens = 0
        
        for name, llm in self.llms.items():
            stats = llm.get_stats()
            total_calls += stats['calls']
            total_tokens += stats['tokens']
            print(f"{stats['name']:20} | 调用: {stats['calls']:3} 次 | Tokens: {stats['tokens']:6}")
        
        print(f"{'-'*60}")
        print(f"{'总计':20} | 调用: {total_calls:3} 次 | Tokens: {total_tokens:6}")
        print(f"{'='*60}")

# ========== 测试示例 ==========

def demo_bettafish_workflow():
    """
    演示完整的 BettaFish 工作流
    """
    # 初始化
    manager = MultiLLMManager()
    
    # 分析主题
    topic = "2024年诺贝尔物理学奖的意义"
    
    # 阶段1: 并行分析
    agent_results = manager.parallel_analysis(topic)
    
    # 阶段2: Forum 综合
    synthesis = manager.forum_synthesis(agent_results)
    
    # 阶段3: 生成报告
    report = manager.generate_report(synthesis, topic)
    
    # 展示结果
    print(f"\n{'='*60}")
    print("🎯 最终报告")
    print(f"{'='*60}\n")
    print(report)
    
    # 统计
    manager.print_statistics()

if __name__ == "__main__":
    demo_bettafish_workflow()