"""
论坛主持人 - Forum Host
学习目标:
1. 引导讨论方向
2. 管理发言顺序
3. 总结讨论结果
"""

import os
from openai import OpenAI
from dotenv import load_dotenv
from typing import List, Dict

load_dotenv()

class ForumHost:
    """
    论坛主持人
    类似 BettaFish 的 ForumEngine
    """
    
    def __init__(self, topic: str):
        self.topic = topic
        self.client = OpenAI(
            api_key=os.getenv("DEEPSEEK_API_KEY"),
            base_url="https://api.deepseek.com"
        )
        
        self.discussion_history = []  # 讨论历史
        self.current_round = 0        # 当前轮次
        self.max_rounds = 3           # 最大轮次
        
        print(f"🎙️ 论坛主持人已就位")
        print(f"📋 讨论主题: {self.topic}\n")
    
    def open_forum(self) -> str:
        """开场白 - 发起讨论"""
        opening = f"""欢迎各位专家!

今天的讨论主题是: {self.topic}

请各位从自己的专业角度,分享观点和发现。
让我们开始第一轮讨论。"""
        
        print("="*70)
        print("🎙️ 主持人开场:")
        print("="*70)
        print(opening)
        print("="*70 + "\n")
        
        return opening
    
    def guide_discussion(self, previous_statements: List[Dict]) -> str:
        """
        引导讨论 - 根据之前的发言,提出新问题
        
        Args:
            previous_statements: [
                {"agent": "QueryAgent", "content": "..."},
                {"agent": "InsightAgent", "content": "..."}
            ]
        """
        self.current_round += 1
        
        # 记录讨论历史
        self.discussion_history.extend(previous_statements)
        
        # 整理之前的讨论
        discussion_summary = "\n\n".join([
            f"{s['agent']}: {s['content'][:200]}..."
            for s in previous_statements
        ])
        
        # 生成引导语
        prompt = f"""你是论坛主持人。

讨论主题: {self.topic}
当前轮次: {self.current_round}/{self.max_rounds}

刚才的发言:
{discussion_summary}

请:
1. 简要总结共识点
2. 指出分歧或需要深入的地方
3. 提出1-2个引导性问题

保持简洁,3-4句话。"""

        response = self.client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        
        guidance = response.choices[0].message.content
        
        print("="*70)
        print(f"🎙️ 主持人引导 (第{self.current_round}轮):")
        print("="*70)
        print(guidance)
        print("="*70 + "\n")
        
        return guidance
    
    def should_continue(self) -> bool:
        """判断是否继续讨论"""
        return self.current_round < self.max_rounds
    
    def conclude_discussion(self) -> str:
        """总结讨论"""
        # 整理完整讨论历史
        full_discussion = "\n\n".join([
            f"[{s['agent']}]: {s['content']}"
            for s in self.discussion_history
        ])
        
        prompt = f"""你是论坛主持人,请总结这次讨论。

主题: {self.topic}

完整讨论记录:
{full_discussion}

请提供:
1. 核心共识 (2-3点)
2. 主要分歧 (1-2点)
3. 综合建议 (2点)

保持专业和简洁。"""

        response = self.client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.6
        )
        
        conclusion = response.choices[0].message.content
        
        print("="*70)
        print("🎙️ 主持人总结:")
        print("="*70)
        print(conclusion)
        print("="*70 + "\n")
        
        return conclusion


# ========== 测试主持人 ==========

if __name__ == "__main__":
    host = ForumHost("AI技术的风险与机遇")
    
    # 开场
    host.open_forum()
    
    # 模拟第一轮发言
    round1 = [
        {
            "agent": "QueryAgent",
            "content": "根据最新研究,AI在医疗诊断准确率已超过95%,但同时引发了数据隐私担忧..."
        },
        {
            "agent": "InsightAgent", 
            "content": "数据显示,AI技术创造的新岗位数量超过替代的岗位,但转型期会有短期失业..."
        }
    ]
    
    # 引导讨论
    guidance = host.guide_discussion(round1)
    
    # 模拟第二轮
    round2 = [
        {
            "agent": "QueryAgent",
            "content": "关于隐私保护,欧盟GDPR已经提供了框架,关键是执行力度..."
        },
        {
            "agent": "InsightAgent",
            "content": "失业问题需要再培训计划,政府和企业应该共同承担责任..."
        }
    ]
    
    host.guide_discussion(round2)
    
    # 总结
    host.conclude_discussion()