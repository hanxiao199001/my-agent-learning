-- BettaFish 舆情数据库设计
-- 简化版,用于学习

-- ========== 1. 帖子表 ==========
CREATE TABLE IF NOT EXISTS posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    platform VARCHAR(50) NOT NULL,           -- 平台: 微博/抖音/小红书等
    post_id VARCHAR(100) UNIQUE NOT NULL,    -- 平台原始ID
    content TEXT NOT NULL,                   -- 帖子内容
    author VARCHAR(100),                     -- 作者
    author_followers INTEGER DEFAULT 0,      -- 粉丝数
    publish_time DATETIME NOT NULL,          -- 发布时间
    likes INTEGER DEFAULT 0,                 -- 点赞数
    comments_count INTEGER DEFAULT 0,        -- 评论数
    shares INTEGER DEFAULT 0,                -- 转发数
    url TEXT,                                -- 原帖链接
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_platform (platform),
    INDEX idx_publish_time (publish_time),
    INDEX idx_author (author)
);

-- ========== 2. 评论表 ==========
CREATE TABLE IF NOT EXISTS comments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    post_id INTEGER NOT NULL,                -- 关联帖子
    comment_id VARCHAR(100),                 -- 评论ID
    content TEXT NOT NULL,                   -- 评论内容
    author VARCHAR(100),                     -- 评论者
    publish_time DATETIME,                   -- 评论时间
    likes INTEGER DEFAULT 0,                 -- 点赞数
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (post_id) REFERENCES posts(id),
    INDEX idx_post_id (post_id)
);

-- ========== 3. 情感分析表 ==========
CREATE TABLE IF NOT EXISTS sentiment (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    post_id INTEGER NOT NULL,                -- 关联帖子
    sentiment_score FLOAT,                   -- 情感分数 (-1到1)
    sentiment_label VARCHAR(20),             -- 标签: positive/negative/neutral
    confidence FLOAT,                        -- 置信度
    keywords TEXT,                           -- 关键词(JSON)
    analyzed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (post_id) REFERENCES posts(id),
    INDEX idx_post_id (post_id),
    INDEX idx_sentiment_label (sentiment_label)
);

-- ========== 4. 话题表 ==========
CREATE TABLE IF NOT EXISTS topics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    topic_name VARCHAR(200) NOT NULL,        -- 话题名称
    platform VARCHAR(50),                    -- 平台
    hot_score INTEGER DEFAULT 0,             -- 热度分数
    post_count INTEGER DEFAULT 0,            -- 帖子数
    first_seen DATETIME,                     -- 首次出现
    last_updated DATETIME,                   -- 最后更新
    status VARCHAR(20) DEFAULT 'active',     -- 状态: active/archived
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_topic_name (topic_name),
    INDEX idx_hot_score (hot_score)
);

-- ========== 5. 话题-帖子关联表 ==========
CREATE TABLE IF NOT EXISTS topic_posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    topic_id INTEGER NOT NULL,
    post_id INTEGER NOT NULL,
    relevance_score FLOAT DEFAULT 1.0,       -- 相关度
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (topic_id) REFERENCES topics(id),
    FOREIGN KEY (post_id) REFERENCES posts(id),
    UNIQUE(topic_id, post_id)
);