# AI Leaders Tracker - 人物追踪系统

追踪 AI 行业领袖（黄仁勋、孙正义等）的新闻、行程和活动。

## 🎯 核心功能

- **实时新闻采集**：通过 Google News RSS 获取最新新闻
- **反检测爬虫**：使用 patchright（反检测版 Playwright）绕过反爬虫
- **位置提取**：自动从新闻中提取人物所在位置
- **活动识别**：识别演讲、会议、产品发布等活动
- **多语言支持**：支持中、日、英、韩四语

## 📁 项目结构

```
person-tracker/
├── tracker.py              # 主追踪脚本
├── convert-to-page.py      # 数据格式转换
├── deploy.sh               # 一键部署脚本
├── real-data-loader.js     # 前端数据加载器
├── data/                   # 追踪数据
│   ├── jensen-huang.json
│   ├── masayoshi-son.json
│   └── dashboard.json
└── output/                 # 转换后的页面数据
    └── page-data.json
```

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install feedparser patchright
python3 -m patchright install chromium
```

### 2. 运行追踪

```bash
# 追踪所有人
python3 ~/scripts/person-tracker/tracker.py

# 追踪特定人物
python3 ~/scripts/person-tracker/tracker.py jensen-huang
python3 ~/scripts/person-tracker/tracker.py masayoshi-son
```

### 3. 部署到网站

```bash
bash ~/scripts/person-tracker/deploy.sh
```

## 📊 数据格式

### 追踪数据 (data/jensen-huang.json)

```json
{
  "person_id": "jensen-huang",
  "name": "Jensen Huang",
  "name_local": "黄仁勲",
  "title": "NVIDIA CEO & Co-founder",
  "tracked_at": "2026-06-12T06:00:00Z",
  "news_count": 10,
  "recent_news": [...],
  "insights": {
    "locations": ["UK", "Las Vegas (CES)", "China"],
    "activities": ["AI Development", "Product Announcement", "Partnership"]
  },
  "status": "📍 UK · AI Development"
}
```

### 页面数据 (output/page-data.json)

```json
{
  "jensen-huang": {
    "subject": {
      "ja": { "name": "ジェンスン・フアン", "location": "UK", "status": "📍 UK · AI Development" },
      "en": { "name": "Jensen Huang", "location": "UK", "status": "📍 UK · AI Development" }
    },
    "news": [
      {
        "topic": { "en": "Semiconductors", "ja": "Semiconductors" },
        "head": { "en": "Article title...", "ja": "Article title..." },
        "src": { "en": "Source", "ja": "Source" },
        "time": { "en": "2 hours ago", "ja": "2 hours ago" }
      }
    ]
  }
}
```

## 🔧 添加新人物

编辑 `tracker.py` 中的 `PEOPLE` 数组：

```python
{
    "id": "sam-altman",
    "name": "Sam Altman",
    "name_ja": "サム・アルトマン",
    "name_zh": "萨姆·阿尔特曼",
    "title": "OpenAI CEO",
    "queries": [
        "Sam Altman OpenAI",
        "サム・アルトマン OpenAI"
    ]
}
```

## ⏰ 定时任务

```bash
# 每6小时更新一次
0 */6 * * * /usr/bin/python3 /home/ubuntu/scripts/person-tracker/tracker.py >> /home/ubuntu/scripts/person-tracker/cron.log 2>&1
```

## 🛠️ 技术栈

- **Python 3.10+**：主语言
- **feedparser**：RSS 解析
- **patchright**：反检测浏览器自动化
- **Google News RSS**：新闻数据源

## 📝 注意事项

1. **频率限制**：Google News RSS 不要查询过于频繁，每小时一次为宜
2. **位置准确性**：位置提取基于关键词，可能不完全准确
3. **新闻延迟**：RSS 可能有 15-30 分钟延迟
4. **语言混合**：多语言查询可能返回重复文章，已通过标题去重

## 🔗 相关链接

- [patchright GitHub](https://github.com/Kaliiiiiiiiii-Vinyzu/patchright-python)
- [Google News RSS](https://news.google.com/rss)
- [feedparser 文档](https://pythonhosted.org/feedparser/)

## 📄 License

MIT
