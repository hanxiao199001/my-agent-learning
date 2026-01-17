# AI Agent 学习之路 🤖

从零开始学习构建AI Agent系统的完整记录

## 📚 学习进度

### Week 1: Agent 基础

#### Day 1-2: 环境搭建与基础概念
- ✅ 开发环境配置 (Python, Git, VS Code)
- ✅ 第一个LLM调用
- ✅ 理解Agent的感知-决策-行动循环

#### Day 3: 工具集成
- ✅ 网络搜索工具 (Tavily)
- ✅ 数学计算工具
- ✅ 天气查询工具
- ✅ 实现自主工具选择

#### Day 4: 自主决策
- ✅ 工具选择Agent
- ✅ 多步推理
- ✅ 实时信息检索

#### Day 5: 数据库查询 Agent ⭐
- ✅ 数据库设计 (SQLite)
- ✅ Text-to-SQL 系统
- ✅ 完整 Insight Agent
- ✅ 任务规划 + 执行 + 综合分析

## 🎯 学习目标

短期目标:
- [ ] Multi-Agent 协作系统
- [ ] ReAct 模式实现
- [ ] 记忆与反思机制

长期目标:
- [ ] Web3 项目舆情分析系统
- [ ] 智能合约安全监控Agent
- [ ] DeFi协议分析Agent

## 🛠️ 技术栈

- **LLM**: DeepSeek API
- **数据库**: SQLite
- **工具**: Tavily Search, OpenWeatherMap
- **语言**: Python 3.x

## 📂 项目结构
```
my-agent-learning/
├── week1/
│   ├── day1/          # 环境搭建
│   ├── day2/          # 第一个Agent
│   ├── day3/          # 工具集成
│   ├── day4/          # 自主决策
│   └── day5/          # 数据库Agent ⭐
│       ├── sentiment.db       # 数据库
│       ├── create_db.py       # 建表脚本
│       ├── text_to_sql.py     # Text-to-SQL
│       └── insight_agent.py   # 完整Agent
├── .env               # API密钥配置
├── .gitignore        
└── README.md
```

## 🔑 配置说明

复制 `.env.example` 为 `.env`:
```bash
cp .env.example .env
```

填入你的API密钥:
```
DEEPSEEK_API_KEY=your_key_here
TAVILY_API_KEY=your_key_here
OPENWEATHER_API_KEY=your_key_here
```

## 🚀 快速开始
```bash
# 克隆项目
git clone https://github.com/你的用户名/my-agent-learning.git
cd my-agent-learning

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Mac/Linux
# venv\Scripts\activate   # Windows

# 安装依赖
pip install openai python-dotenv tavily-python requests

# 运行 Day 5 的完整 Agent
python week1/day5/insight_agent.py
```

## 💡 核心学习成果

### Text-to-SQL 系统
自然语言转SQL查询,支持:
- 安全验证
- 多表关联
- 聚合统计
- 结果解释

### Insight Agent
完整的数据分析Agent:
1. **任务规划**: 自动分解分析步骤
2. **逐步执行**: Text-to-SQL查询
3. **洞察生成**: 每步总结关键发现
4. **综合分析**: 整合所有结果

## 📖 参考资料

- [BettaFish 项目](https://github.com/666ghj/BettaFish)
- [DeepSeek API 文档](https://platform.deepseek.com/api-docs/)
- [LangGraph 文档](https://langchain-ai.github.io/langgraph/)

## 📝 学习笔记

每天的详细学习笔记在对应的day目录下的 `notes.md` 文件中。

## 🤝 致谢

特别感谢 Claude AI 的学习指导! 🙏

---

**持续更新中...** 🚧