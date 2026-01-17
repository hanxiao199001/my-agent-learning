"""
完整 Insight Agent - 模拟 BettaFish
学习目标:
1. 多步骤分析
2. 趋势识别
3. 反思优化
"""

import os
import sqlite3
from openai import OpenAI
from dotenv import load_dotenv
from typing import List, Dict
import json

load_dotenv()

class InsightAgent:
    """
    完整的 Insight Agent
    整合: Text-to-SQL + 数据分析 + 趋势识别 + 反思优化
    """
    
    def __init__(self, db_path="week1/day5/sentiment.db"):
        self.db_path = db_path
        self.client = OpenAI(
            api_key=os.getenv("DEEPSEEK_API_KEY"),
            base_url="https://api.deepseek.com"
        )
        
        self.analysis_history = []  # 分析历史
        
        print("🔍 Insight Agent 已启动\n")
    
    def execute_sql(self, sql: str):
        """执行SQL"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute(sql)
            results = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            conn.close()
            return {"columns": columns, "data": results}
        except Exception as e:
            conn.close()
            print(f"❌ SQL错误: {e}")
            return None
    
    def generate_analysis_plan(self, topic: str) -> List[str]:
        """
        生成分析计划 - 多步骤任务分解
        模拟 BettaFish 的任务规划
        """
        prompt = f"""你是数据分析专家。针对主题: {topic}

生成3-5个分析步骤,每个步骤是一个具体的数据查询问题。

要求:
1. 从不同角度分析
2. 由浅入深
3. 每个问题具体明确

只输出问题列表,每行一个,格式:
1. 问题1
2. 问题2
...
"""
        
        response = self.client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        
        # 解析问题列表
        questions = []
        for line in response.choices[0].message.content.split('\n'):
            line = line.strip()
            if line and (line[0].isdigit() or line.startswith('-')):
                # 去除序号
                question = line.split('.', 1)[-1].strip()
                question = question.lstrip('- ').strip()
                if question:
                    questions.append(question)
        
        return questions
    
    def analyze_question(self, question: str) -> Dict:
        """分析单个问题"""
        # 1. 生成SQL
        sql_prompt = f"""生成SQL查询回答: {question}

数据库表:
- posts (id, platform, content, author, publish_time, likes, comments_count, shares)
- sentiment (id, post_id, sentiment_score, sentiment_label, confidence)

只返回SQL,不要解释。使用SQLite语法。"""

        sql_response = self.client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": sql_prompt}],
            temperature=0.1
        )
        
        sql = sql_response.choices[0].message.content.strip()
        sql = sql.replace('```sql', '').replace('```', '').strip()
        
        # 验证安全性
        if any(kw in sql.upper() for kw in ['DROP', 'DELETE', 'UPDATE', 'INSERT']):
            return {"error": "不安全的SQL"}
        
        # 2. 执行SQL
        results = self.execute_sql(sql)
        
        if not results or not results['data']:
            return {"question": question, "sql": sql, "data": None}
        
        # 3. 生成洞察
        insight_prompt = f"""问题: {question}

查询结果:
{results['data'][:10]}

用2-3句话总结关键发现。"""

        insight_response = self.client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": insight_prompt}],
            temperature=0.5
        )
        
        return {
            "question": question,
            "sql": sql,
            "data": results['data'],
            "insight": insight_response.choices[0].message.content
        }
    
    def comprehensive_analysis(self, topic: str):
        """
        完整分析流程
        模拟 BettaFish 的 Chunked Analysis and Reflection
        """
        print(f"\n{'='*70}")
        print(f"📊 Insight Agent 深度分析")
        print(f"{'='*70}")
        print(f"🎯 主题: {topic}\n")
        
        # 阶段1: 生成分析计划
        print("📋 生成分析计划...")
        questions = self.generate_analysis_plan(topic)
        
        print(f"   ✅ 生成 {len(questions)} 个分析步骤:\n")
        for i, q in enumerate(questions, 1):
            print(f"   {i}. {q}")
        
        # 阶段2: 逐步执行分析
        print(f"\n{'='*70}")
        print("🔬 执行分析")
        print(f"{'='*70}\n")
        
        results = []
        for i, question in enumerate(questions, 1):
            print(f"📍 步骤 {i}/{len(questions)}: {question}")
            
            result = self.analyze_question(question)
            results.append(result)
            
            if result.get('data'):
                print(f"   ✅ 查询成功: {len(result['data'])} 条结果")
                print(f"   💡 {result['insight'][:100]}...\n")
            else:
                print(f"   ⚠️  无数据\n")
        
        # 阶段3: 综合结论
        print(f"\n{'='*70}")
        print("🎯 综合分析")
        print(f"{'='*70}\n")
        
        # 整合所有洞察
        all_insights = "\n".join([
            f"发现{i+1}: {r.get('insight', '无')}" 
            for i, r in enumerate(results) 
            if r.get('insight')
        ])
        
        synthesis_prompt = f"""主题: {topic}

分析过程中的发现:
{all_insights}

请综合以上发现,给出:
1. 核心结论 (2-3句话)
2. 关键趋势 (1-2点)
3. 建议行动 (1-2点)"""

        final_response = self.client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": synthesis_prompt}],
            temperature=0.6
        )
        
        print(final_response.choices[0].message.content)
        print(f"\n{'='*70}\n")
        
        return results

# ========== 测试 ==========

if __name__ == "__main__":
    agent = InsightAgent()
    
    # 完整分析
    agent.comprehensive_analysis("AI技术的舆情分析")