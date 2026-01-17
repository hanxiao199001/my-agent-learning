"""
多 Agent 系统 - 模拟团队协作
学习目标:让多个专业化的 Agent 协同工作完成复杂任务
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

# ========== Agent 类 ==========

class Agent:
    """基础 Agent 类"""
    
    def __init__(self, name, role, expertise):
        self.name = name
        self.role = role
        self.expertise = expertise
        
    def process(self, task, context=""):
        """处理任务"""
        prompt = f"""你是 {self.name},一个 {self.role}。

你的专长: {self.expertise}

当前任务: {task}

{f"上下文信息: {context}" if context else ""}

请完成这个任务,给出你的专业意见。保持简洁专业。"""

        response = openai_client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        
        return response.choices[0].message.content

class ResearcherAgent(Agent):
    """研究员 Agent - 负责信息搜集"""
    
    def __init__(self):
        super().__init__(
            name="研究员小李",
            role="信息研究专家",
            expertise="擅长搜索、整理和总结互联网信息"
        )
    
    def research(self, topic):
        """执行研究任务"""
        print(f"\n🔍 [{self.name}] 开始研究: {topic}")
        
        # 搜索信息
        search_result = web_search(topic)
        
        # 让 AI 整理搜索结果
        organized = self.process(
            f"请整理以下搜索结果,提取关键信息:\n{search_result}",
            ""
        )
        
        print(f"✅ [{self.name}] 研究完成")
        return organized

class AnalystAgent(Agent):
    """分析师 Agent - 负责数据分析"""
    
    def __init__(self):
        super().__init__(
            name="分析师小王",
            role="数据分析专家",
            expertise="擅长分析数据、发现模式、提出见解"
        )
    
    def analyze(self, data):
        """分析数据"""
        print(f"\n📊 [{self.name}] 开始分析数据...")
        
        analysis = self.process(
            "请分析以下信息,提出关键见解和发现:",
            data
        )
        
        print(f"✅ [{self.name}] 分析完成")
        return analysis

class WriterAgent(Agent):
    """作家 Agent - 负责撰写报告"""
    
    def __init__(self):
        super().__init__(
            name="作家小张",
            role="专业写作专家",
            expertise="擅长将复杂信息整理成清晰易读的报告"
        )
    
    def write_report(self, research, analysis):
        """撰写报告"""
        print(f"\n✍️  [{self.name}] 开始撰写报告...")
        
        report = self.process(
            "基于研究和分析结果,撰写一份结构清晰的报告",
            f"研究结果:\n{research}\n\n分析结果:\n{analysis}"
        )
        
        print(f"✅ [{self.name}] 报告完成")
        return report

class CoordinatorAgent(Agent):
    """协调者 Agent - 管理整个流程"""
    
    def __init__(self):
        super().__init__(
            name="项目经理小刘",
            role="团队协调者",
            expertise="擅长任务分解、团队协调、质量把控"
        )
        
        # 初始化团队成员
        self.researcher = ResearcherAgent()
        self.analyst = AnalystAgent()
        self.writer = WriterAgent()
    
    def coordinate(self, user_task):
        """协调整个流程"""
        print("=" * 80)
        print(f"👔 [{self.name}] 收到任务: {user_task}")
        print("=" * 80)
        
        # 1. 任务分解
        print(f"\n📋 [{self.name}] 正在分解任务...")
        
        task_plan = self.process(
            f"将以下用户任务分解成具体的研究主题:\n{user_task}\n\n请给出2-3个需要研究的具体方面,每个一行。",
            ""
        )
        
        print(f"✅ [{self.name}] 任务分解完成:")
        print(task_plan)
        
        # 2. 研究阶段
        print("\n" + "=" * 80)
        print("📚 阶段1: 信息研究")
        print("=" * 80)
        
        research_results = []
        
        # 简化:只做一次综合研究
        research = self.researcher.research(user_task)
        research_results.append(research)
        
        # 3. 分析阶段
        print("\n" + "=" * 80)
        print("🔬 阶段2: 数据分析")
        print("=" * 80)
        
        combined_research = "\n\n".join(research_results)
        analysis = self.analyst.analyze(combined_research)
        
        # 4. 撰写阶段
        print("\n" + "=" * 80)
        print("📝 阶段3: 报告撰写")
        print("=" * 80)
        
        report = self.writer.write_report(combined_research, analysis)
        
        # 5. 质量审核
        print("\n" + "=" * 80)
        print("✨ 阶段4: 质量审核")
        print("=" * 80)
        
        print(f"\n👔 [{self.name}] 正在审核报告...")
        
        final_report = self.process(
            "请审核以下报告,如果需要可以略作调整,确保质量:",
            report
        )
        
        print(f"✅ [{self.name}] 审核完成,项目交付!")
        
        return final_report

# ========== 主函数 ==========

def run_multi_agent_system(task):
    """运行多 Agent 系统"""
    
    # 创建协调者
    coordinator = CoordinatorAgent()
    
    # 执行任务
    result = coordinator.coordinate(task)
    
    # 展示最终结果
    print("\n" + "=" * 80)
    print("🎯 最终交付报告")
    print("=" * 80 + "\n")
    print(result)
    print("\n" + "=" * 80)

# ========== 测试 ==========

if __name__ == "__main__":
    print("\n🤝 多 Agent 系统演示\n")
    
    # 测试任务
    run_multi_agent_system(
        "研究 2024年诺贝尔物理学奖得主的工作,分析其重要性,并撰写一份简短报告"
    )