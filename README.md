# 食光记（Food-Time）

基于 **FastAPI + Vue 3 + MySQL** 的 AI 智能饮食助手网站，解决「今天吃什么」的每个选择时刻。

> 一个集食物库、Agent 助手、饮食记录、营养评估、账单 OCR、美食社区于一体的全栈应用。中文品牌名「食光记」。

## 功能特性

- **Agent 助手**（SSE 流式对话 + 12 个 Tool Calling）
  - 搜索食物 / 查营养数据 / 推荐食谱 / 决策辅助
  - 个性化推荐（基于用户偏好 + 历史记录 + 膳食指南）
  - 食物图片识别（Qwen VL）
  - 附近美食（高德 POI）
  - 实时联网搜索（博查 AI）
  - 食物库语义检索（RAG）+ 长期记忆
- **食物库**：分类浏览 + 关键词搜索 + 营养数据（中国食物成分表）
- **我的厨房（DIY）**：双开门冰箱选材 + 岛台备菜 + 烹饪动画 + Agent 烹饪建议
- **今天吃什么**：搜索 / 分类筛选 / 随机转盘 / 决策辅助
- **饮食记录**：记录每餐 + 偏好自动学习 + 营养摄入追踪
- **营养评估**：对照《中国居民膳食指南(2022)》给出达标 / 偏高 / 偏低结论
- **记账**：手动录入 + 账单 OCR 识别（Qwen VL）+ 统计图表
- **美食广场**：分享食谱 + 评论（楼中楼 / 删除 / AI 总结）+ 收藏 + 热度排序
- **用户体系**：邮箱注册（SMTP 验证码）+ JWT + 个人档案 + 忘记 / 修改密码
- **管理后台**：数据统计 + 食谱审核 + 用户管理（封禁 / 升降级 / 删除）+ 删除审计
- **MCP Server**：暴露 6 个饮食工具给外部 AI agent 调用

## 技术栈

| 类别 | 技术 |
|------|------|
| 前端 | Vue 3 + Vite + Pinia + Vue Router + ECharts |
| 后端 | FastAPI（异步）+ SQLAlchemy（异步） |
| 数据库 | MySQL 8.0 |
| AI | DeepSeek（对话 + Tool Calling）、Qwen VL（视觉）、DashScope（Embedding） |
| 检索 | ChromaDB（RAG 向量检索） |
| 其他 | SMTP 邮件、高德 POI、博查搜索、PWA、Docker |

## 快速开始

### 前置要求
- Python 3.13+ / Node.js 20+
- MySQL 8.0（默认端口 3307）

### 1. 创建数据库
```bash
mysql -u root -p -P 3307 -e "CREATE DATABASE IF NOT EXISTS food_time CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
```

### 2. 启动后端
```bash
cd server
pip install -r requirements.txt
cp .env.example .env   # 修改 DATABASE_URL 和 API Key
python -m uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

### 3. 启动前端
```bash
cd client
npm install
npm run dev
```

访问 `http://localhost:5173`，后端 API 文档 `http://localhost:8000/docs`

## 项目结构

```
client/             前端（Vue 3 + Vite）
  src/views/        TodayEat / DIY / Square / Expense / Assistant / About / Admin ...
  src/components/   diy/（冰箱/岛台/调料台/烹饪面板）today/（转盘）
  src/stores/       DIY 厨房状态（Pinia）
server/             后端（FastAPI）
  src/auth/         用户认证（注册/登录/验证码/档案）
  src/food/         食物库
  src/chat/         Agent 对话（SSE + 12 Tool Calling + RAG + 长期记忆）
  src/diet/         饮食记录 + 营养评估
  src/expense/      记账 + OCR
  src/custom_food/  自定义食谱 + 食材识别
  src/public_food/  美食广场 + 评论 + 收藏
  src/admin/        管理后台
  src/mcp_integration/  MCP Server（6 个饮食工具）
  src/services/     DeepSeek / Qwen VL / 向量检索 / 营养参考...
docs/               项目文档
```

## 许可
[MIT](LICENSE)
