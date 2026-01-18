"""
报告生成Agent
学习目标:
1. 整合所有分析结果
2. 生成结构化报告
3. 提供可执行建议
"""

import os
from openai import OpenAI
from dotenv import load_dotenv
from typing import Dict, List
from datetime import datetime

load_dotenv()

class ReportAgent:
    """
    报告生成Agent
    类似 BettaFish 的 ReportEngine
    """
    
    def __init__(self):
        self.name = "ReportAgent"
        self.client = OpenAI(
            api_key=os.getenv("DEEPSEEK_API_KEY"),
            base_url="https://api.deepseek.com"
        )
        
        print(f"📝 {self.name} 已启动 (报告生成专家)")
    
    def generate_report(
        self,
        topic: str,
        research_data: Dict,
        forum_conclusion: str
    ) -> str:
        """
        生成完整分析报告
        
        Args:
            topic: 分析主题
            research_data: {
                "query": "QueryAgent的发现",
                "insight": "InsightAgent的分析",
                "media": "MediaAgent的洞察"
            }
            forum_conclusion: 论坛讨论的总结
        """
        print(f"\n📝 {self.name} 正在生成报告...")
        
        # 整理研究数据
        research_summary = "\n\n".join([
            f"【{agent.upper()}】\n{content}"
            for agent, content in research_data.items()
        ])
        
        # 生成报告
        prompt = f"""你是专业的分析报告撰写专家。

主题: {topic}

===== 研究数据 =====
{research_summary}

===== 专家论坛讨论结论 =====
{forum_conclusion}

请生成一份完整的分析报告,包含:

# {topic} - 综合分析报告

## 一、执行摘要
(3-4句话概括核心发现)

## 二、核心发现
1. 发现1 (用数据支撑)
2. 发现2 (用数据支撑)
3. 发现3 (用数据支撑)

## 三、深度洞察
### 3.1 趋势分析
(识别主要趋势)

### 3.2 风险识别
(潜在风险和挑战)

### 3.3 机会窗口
(可抓住的机遇)

## 四、战略建议
1. 短期行动 (0-6个月)
2. 中期规划 (6-18个月)
3. 长期布局 (18个月+)

## 五、关键指标
(建议跟踪的3-5个关键指标)

---
报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

        response = self.client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4  # 较低温度保证专业性
        )
        
        report = response.choices[0].message.content
        
        print(f"✅ {self.name} 报告生成完成\n")
        
        return report
    
    def save_report(self, report: str, topic: str):
        """保存报告到文件"""
        # 创建reports目录
        import os
        os.makedirs("reports", exist_ok=True)
        
        # 生成文件名
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"reports/analysis_{timestamp}.md"
        
        # 保存报告
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"💾 报告已保存: {filename}")
        
        return filename


# ========== 测试报告生成 ==========

if __name__ == "__main__":
    agent = ReportAgent()
    
    # 模拟数据
    test_data = {
        "query": "根据最新研究,AI技术在医疗诊断准确率已超95%,但数据隐私问题突出...",
        "insight": "数据显示,AI创造新岗位数超过替代岗位,但存在短期失业风险...",
        "media": "社交媒体情绪分化明显,技术乐观派与失业担忧派形成对立..."
    }
    
    forum_result = """
核心共识: AI技术带来效率提升,但需配套治理框架
主要分歧: 风险优先级的侧重不同
综合建议: 强化执行 + 政企合作
"""
    
    # 生成报告
    report = agent.generate_report(
        topic="AI技术的风险与机遇",
        research_data=test_data,
        forum_conclusion=forum_result
    )
    
    print("="*70)
    print("📊 生成的报告:")
    print("="*70)
    print(report)
    
    # 保存报告
    agent.save_report(report, "AI技术的风险与机遇")