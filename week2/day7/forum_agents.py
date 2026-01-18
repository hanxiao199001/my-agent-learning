"""
论坛参与Agents
学习目标:
1. 不同Agent有不同视角
2. Agent能看到其他Agent的发言
3. Agent会调整自己的观点
"""

import os
from openai import OpenAI
from dotenv import load_dotenv
from typing import List, Dict

load_dotenv()

class ForumAgent:
    """论坛Agent基类"""
    
    def __init__(self, name: str, role: str, perspective: str):
        self.name = name
        self.role = role  # 角色定位
        self.perspective = perspective  # 视角特点
        
        self.client = OpenAI(
            api_key=os.getenv("DEEPSEEK_API_KEY"),
            base_url="https://api.deepseek.com"
        )
        
        self.statements = []  # 自己的发言历史
        
        print(f"✅ {self.name} 加入论坛 ({self.role})")
    
    def speak(self, topic: str, context: Dict) -> str:
        """
        发言
        
        Args:
            topic: 讨论主题
            context: {
                "round": 1,
                "host_guidance": "主持人的引导",
                "other_statements": [其他Agent的发言]
            }
        """
        round_num = context.get("round", 1)
        guidance = context.get("host_guidance", "")
        others = context.get("other_statements", [])
        
        # 构建发言提示
        others_text = ""
        if others:
            others_text = "\n\n其他专家的观点:\n" + "\n".join([
                f"- {s['agent']}: {s['content'][:150]}..."
                for s in others
            ])
        
        prompt = f"""你是{self.name}，{self.role}。
你的视角特点: {self.perspective}

讨论主题: {topic}
当前轮次: {round_num}

主持人引导: {guidance}
{others_text}

请从你的专业角度发表观点:
1. 如果是第一轮,直接阐述你的观点
2. 如果其他专家已发言,可以补充、质疑或深化
3. 保持专业,3-4句话

不要重复他人观点,提供新角度或证据。"""

        response = self.client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.8  # 提高温度增加多样性
        )
        
        statement = response.choices[0].message.content
        self.statements.append(statement)
        
        return statement


class QueryAgent(ForumAgent):
    """网络搜索专家"""
    
    def __init__(self):
        super().__init__(
            name="QueryAgent",
            role="网络信息研究专家",
            perspective="关注最新研究、新闻报道、公众讨论"
        )


class InsightAgent(ForumAgent):
    """数据分析专家"""
    
    def __init__(self):
        super().__init__(
            name="InsightAgent",
            role="数据分析专家",
            perspective="关注统计数据、趋势分析、量化指标"
        )


class MediaAgent(ForumAgent):
    """媒体观察专家"""
    
    def __init__(self):
        super().__init__(
            name="MediaAgent",
            role="媒体与舆情分析专家",
            perspective="关注社交媒体情绪、公众认知、传播效果"
        )


# ========== 测试Agent ==========

if __name__ == "__main__":
    # 创建Agents
    query = QueryAgent()
    insight = InsightAgent()
    media = MediaAgent()
    
    print("\n" + "="*70)
    print("🧪 测试 Agent 发言")
    print("="*70 + "\n")
    
    topic = "AI技术对就业市场的影响"
    
    # 第一轮 - 各自发言
    print("📍 第1轮发言:\n")
    
    context1 = {
        "round": 1,
        "host_guidance": "请各位从自己的角度分析AI对就业的影响",
        "other_statements": []
    }
    
    query_s1 = query.speak(topic, context1)
    print(f"🔍 {query.name}:\n{query_s1}\n")
    
    # InsightAgent 能看到 QueryAgent 的发言
    context1["other_statements"] = [
        {"agent": query.name, "content": query_s1}
    ]
    
    insight_s1 = insight.speak(topic, context1)
    print(f"📊 {insight.name}:\n{insight_s1}\n")
    
    # MediaAgent 能看到前两者的发言
    context1["other_statements"].append(
        {"agent": insight.name, "content": insight_s1}
    )
    
    media_s1 = media.speak(topic, context1)
    print(f"📱 {media.name}:\n{media_s1}\n")
    
    # 第二轮 - 互相回应
    print("="*70)
    print("📍 第2轮发言 (深化讨论):\n")
    
    context2 = {
        "round": 2,
        "host_guidance": "请深入探讨: 如何帮助受影响的工人转型?",
        "other_statements": [
            {"agent": query.name, "content": query_s1},
            {"agent": insight.name, "content": insight_s1},
            {"agent": media.name, "content": media_s1}
        ]
    }
    
    query_s2 = query.speak(topic, context2)
    print(f"🔍 {query.name}:\n{query_s2}\n")
    
    insight_s2 = insight.speak(topic, context2)
    print(f"📊 {insight.name}:\n{insight_s2}\n")
    
    media_s2 = media.speak(topic, context2)
    print(f"📱 {media.name}:\n{media_s2}\n")