"""
Text-to-SQL Agent - 自然语言转SQL查询
学习目标:
1. 理解数据库结构
2. 生成安全的SQL查询
3. 执行和解释结果
"""

import os
import sqlite3
from openai import OpenAI
from dotenv import load_dotenv
import json
import re

load_dotenv()

class TextToSQLAgent:
    """Text-to-SQL Agent - Insight Engine 核心"""
    
    def __init__(self, db_path="week1/day5/sentiment.db"):
        # 初始化数据库
        self.db_path = db_path
        self.init_database()
        
        # 初始化 LLM
        self.client = OpenAI(
            api_key=os.getenv("DEEPSEEK_API_KEY"),
            base_url="https://api.deepseek.com"
        )
        
        # 数据库结构说明
        self.schema_description = """
数据库结构:

1. posts (帖子表)
   - id: 主键
   - platform: 平台名称 (微博/抖音/小红书)
   - content: 帖子内容
   - author: 作者
   - publish_time: 发布时间
   - likes: 点赞数
   - comments_count: 评论数
   - shares: 转发数

2. comments (评论表)
   - id: 主键
   - post_id: 关联帖子ID
   - content: 评论内容
   - author: 评论者
   - likes: 点赞数

3. sentiment (情感分析表)
   - id: 主键
   - post_id: 关联帖子ID
   - sentiment_score: 情感分数 (-1到1)
   - sentiment_label: 情感标签 (positive/negative/neutral)
   - confidence: 置信度

4. topics (话题表)
   - id: 主键
   - topic_name: 话题名称
   - platform: 平台
   - hot_score: 热度分数
   - post_count: 帖子数
"""
    
    def init_database(self):
        """初始化数据库和测试数据"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 创建表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                platform VARCHAR(50),
                post_id VARCHAR(100),
                content TEXT,
                author VARCHAR(100),
                publish_time DATETIME,
                likes INTEGER DEFAULT 0,
                comments_count INTEGER DEFAULT 0,
                shares INTEGER DEFAULT 0
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sentiment (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                post_id INTEGER,
                sentiment_score FLOAT,
                sentiment_label VARCHAR(20),
                confidence FLOAT
            )
        """)
        
        # 插入测试数据
        test_posts = [
            ('微博', 'wb001', 'AI Agent技术真的太强大了!未来可期!', '科技博主A', '2024-01-15 10:00:00', 1520, 86, 234),
            ('微博', 'wb002', '担心AI会取代人类工作,失业率会上升', '用户B', '2024-01-15 11:30:00', 892, 156, 67),
            ('抖音', 'dy001', 'ChatGPT帮我写代码,效率提升10倍!', '程序员C', '2024-01-15 14:20:00', 3420, 287, 456),
            ('小红书', 'xhs001', 'AI绘画太美了,但担心画师失业', '艺术爱好者D', '2024-01-15 16:45:00', 2150, 198, 123),
            ('微博', 'wb003', 'DeepSeek真的很强,国产AI崛起!', '数码评测E', '2024-01-16 09:15:00', 4230, 412, 678),
        ]
        
        cursor.executemany(
            "INSERT OR IGNORE INTO posts (platform, post_id, content, author, publish_time, likes, comments_count, shares) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            test_posts
        )
        
        # 插入情感数据
        test_sentiment = [
            (1, 0.85, 'positive', 0.92),
            (2, -0.45, 'negative', 0.78),
            (3, 0.92, 'positive', 0.95),
            (4, -0.32, 'negative', 0.68),
            (5, 0.88, 'positive', 0.91),
        ]
        
        cursor.executemany(
            "INSERT OR IGNORE INTO sentiment (post_id, sentiment_score, sentiment_label, confidence) VALUES (?, ?, ?, ?)",
            test_sentiment
        )
        
        conn.commit()
        conn.close()
        
        print("✅ 数据库初始化完成\n")
    
    def generate_sql(self, question: str) -> str:
        """将自然语言问题转换为SQL"""
        
        prompt = f"""你是一个SQL专家。根据用户问题生成SQL查询。

{self.schema_description}

用户问题: {question}

要求:
1. 只返回SQL语句,不要解释
2. 使用 SQLite 语法
3. 确保SQL安全,不要有注入风险
4. 如果需要统计,使用聚合函数
5. 限制结果数量 (LIMIT 10)

SQL:"""

        response = self.client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1  # 低温度,更确定
        )
        
        sql = response.choices[0].message.content.strip()
        
        # 清理SQL (去除markdown标记)
        sql = sql.replace('```sql', '').replace('```', '').strip()
        
        return sql
    
    def validate_sql(self, sql: str) -> bool:
        """验证SQL安全性"""
        # 简单的安全检查
        dangerous_keywords = ['DROP', 'DELETE', 'UPDATE', 'INSERT', 'ALTER', 'CREATE']
        sql_upper = sql.upper()
        
        for keyword in dangerous_keywords:
            if keyword in sql_upper:
                print(f"❌ 检测到危险操作: {keyword}")
                return False
        
        return True
    
    def execute_sql(self, sql: str):
        """执行SQL并返回结果"""
        if not self.validate_sql(sql):
            return None
        
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
            print(f"❌ SQL执行错误: {str(e)}")
            return None
    
    def explain_results(self, question: str, results: dict) -> str:
        """用自然语言解释查询结果"""
        
        if not results or not results['data']:
            return "没有找到相关数据。"
        
        # 格式化结果
        result_text = f"查询返回了 {len(results['data'])} 条记录:\n\n"
        
        for row in results['data'][:5]:  # 只展示前5条
            row_dict = dict(zip(results['columns'], row))
            result_text += f"{row_dict}\n"
        
        # 让LLM解释
        prompt = f"""用户问题: {question}

查询结果:
{result_text}

请用1-2句话总结这个查询结果,给出关键洞察。"""

        response = self.client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5
        )
        
        return response.choices[0].message.content
    
    def analyze(self, question: str):
        """完整的分析流程"""
        print(f"\n{'='*60}")
        print(f"📊 Insight Engine 分析")
        print(f"{'='*60}")
        print(f"❓ 问题: {question}\n")
        
        # 1. 生成SQL
        print("🔧 生成SQL...")
        sql = self.generate_sql(question)
        print(f"   SQL: {sql}\n")
        
        # 2. 执行SQL
        print("⚙️  执行查询...")
        results = self.execute_sql(sql)
        
        if not results:
            print("❌ 查询失败")
            return
        
        print(f"   ✅ 返回 {len(results['data'])} 条结果\n")
        
        # 3. 展示结果
        print("📈 查询结果:")
        for i, row in enumerate(results['data'][:5], 1):
            row_dict = dict(zip(results['columns'], row))
            print(f"   {i}. {row_dict}")
        
        if len(results['data']) > 5:
            print(f"   ... 还有 {len(results['data']) - 5} 条结果")
        
        # 4. 生成洞察
        print(f"\n💡 AI 洞察:")
        explanation = self.explain_results(question, results)
        print(f"   {explanation}")
        
        print(f"\n{'='*60}\n")

# ========== 测试 ==========

if __name__ == "__main__":
    agent = TextToSQLAgent()
    
    # 测试问题
    questions = [
        "有多少条关于AI的帖子?",
        "哪个平台的帖子最多?",
        "情感最积极的3条帖子是什么?",
        "平均每条帖子有多少点赞?",
        "负面情感的帖子有哪些?"
    ]
    
    for q in questions:
        agent.analyze(q)