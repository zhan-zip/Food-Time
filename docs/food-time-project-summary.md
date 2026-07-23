# Food-Time 项目进度文档

## 一、项目概述

基于 FastAPI + Vue 3 + DeepSeek/Qwen VL 的智能饮食辅助 Web 应用，面向「山东省大学生软件设计大赛」AI 创新应用开发赛道。

**目录：** `d:\Desktop\test\TreaWork\Food-Time\`

**仓库：** <https://github.com/zhan-zip/Food-Time>

**开发周期：** 2026年7月—10月（3个月），单人全栈开发

---

## 二、架构

```
浏览器 (Vue 3 + Vant UI)
  ↕ HTTP REST + SSE 流式
FastAPI 应用服务器 (Python)
  ↕ SQLAlchemy 异步
MySQL 8.0
  ↗ DeepSeek API (对话 + Tool Calling)
  ↗ Qwen VL API (账单 OCR)
```

- **前端**：Vue 3 + Vite + Vant UI 移动端组件库 + Pinia + Vue Router
- **后端**：FastAPI 异步框架，8 个功能模块，JWT 认证
- **数据库**：MySQL 8.0，13 张表，utf8mb4
- **AI**：DeepSeek chat 对话与工具调用，Qwen VL 视觉识别

---

## 三、文件结构（2026-07-20 P0 阶段）

```
Food-Time/
├── .gitignore
│
├── docs/                                 ← 项目文档
│   ├── 需求分析说明书.md
│   ├── 概要设计说明书.md
│   ├── 数据库设计说明书.md
│   └── food-time-project-summary.md      ← 本文档
│
├── client/                               ← 前端项目
│   ├── package.json
│   ├── vite.config.js                    ← Vite 配置 + API 代理
│   ├── index.html
│   └── src/
│       ├── main.js                       ← 入口
│       ├── App.vue                       ← 根组件 (TabBar + 路由)
│       ├── router/index.js               ← 路由配置 + 登录守卫
│       ├── api/
│       │   ├── request.js                ← Axios 封装 + JWT 拦截器
│       │   └── auth.js                   ← 认证 API 封装
│       ├── assets/main.css               ← 全局样式
│       └── views/                        ← 页面组件
│           ├── Login.vue                 ← 登录页
│           ├── Register.vue              ← 注册页
│           ├── Home.vue                  ← 首页 (欢迎卡片 + 快捷入口 + 推荐)
│           ├── Food.vue                  ← 食物库 (搜索 + 分类筛选 + 分页)
│           ├── Chat.vue                  ← AI 对话 (占位，P1 实现 SSE)
│           ├── Expense.vue               ← 记账 (占位)
│           ├── Profile.vue               ← 个人中心 (信息展示 + 退出)
│           └── Admin.vue                 ← 管理后台 (数据统计)
│
└── server/                               ← 后端项目
    ├── requirements.txt                  ← Python 依赖
    ├── .env                              ← 环境变量 (gitignored)
    ├── .env.example                      ← 环境变量模板
    └── app/
        ├── main.py                       ← FastAPI 入口 (lifespan 管理)
        ├── config.py                     ← 配置 (Pydantic Settings)
        ├── database.py                   ← 异步引擎 + 会话工厂
        ├── init_db.py                    ← 建表入口
        ├── dependencies.py               ← JWT 依赖注入
        ├── models.py                     ← 模型统一导入
        ├── seed.py                       ← 种子数据 (12 分类 + 20 食物)
        │
        ├── auth/                         ← 用户认证模块
        │   ├── models.py                 ← User, EmailVerification
        │   ├── schemas.py                ← 请求/响应 Pydantic
        │   ├── service.py                ← bcrypt 哈希 + JWT + 验证码
        │   └── router.py                 ← /api/auth/* (注册/登录/验证/个人信息)
        │
        ├── food/                         ← 食物库模块
        │   ├── models.py                 ← FoodCategory, Food
        │   └── router.py                 ← /api/foods/* (搜索/分类/详情)
        │
        ├── chat/                         ← AI 对话模块 (骨架)
        │   ├── models.py                 ← Conversation, LongMemory
        │   └── router.py                 ← /api/chat/* (占位)
        │
        ├── diet/                         ← 饮食记录模块 (骨架)
        │   ├── models.py                 ← DietRecord, UserPreference
        │   └── router.py                 ← /api/diet/* (占位)
        │
        ├── expense/                      ← 记账模块 (骨架)
        │   ├── models.py                 ← ExpenseRecord
        │   └── router.py                 ← /api/expense/* (占位)
        │
        ├── custom_food/                  ← 自定义食物模块 (骨架)
        │   ├── models.py                 ← CustomRecipe, CustomRecipeIngredient
        │   └── router.py                 ← /api/custom/* (占位)
        │
        ├── public_food/                  ← 公共广场模块 (骨架)
        │   ├── models.py                 ← Like, Favorite
        │   └── router.py                 ← /api/public/* (占位)
        │
        ├── admin/                        ← 管理后台模块 (骨架)
        │   └── router.py                 ← /api/admin/* (统计)
        │
        └── services/                     ← 外部服务 (骨架)
            ├── deepseek.py               ← DeepSeek 客户端
            ├── vision.py                 ← Qwen VL 客户端
            └── email.py                  ← 邮件服务
```

**模块独立性说明**：每个功能模块有独立的 `models.py` + `router.py`，跨模块引用走明确包路径。某个模块（如 chat）出问题，food、auth 等模块完全不受影响。

---

## 四、启动方式

### 1. 数据库准备

```powershell
# 确保 MySQL 运行中
mysql -u root -p -P 3307 -e "CREATE DATABASE IF NOT EXISTS food_time CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
```

### 2. 启动后端

```powershell
cd server
pip install -r requirements.txt
# 修改 .env 中的 DATABASE_URL 和 API Key
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

启动后自动完成：
- 建表（13 张表）
- 创建管理员账号（admin@food-time.com / admin123）
- 插入种子数据（12 个食物分类 + 20 条食物）

Swagger 文档：`http://localhost:8000/docs`

### 3. 启动前端

```powershell
cd client
npm install
npm run dev
```

访问：`http://localhost:5173`

### 4. 关闭顺序

先关 `npm run dev` (Ctrl+C)，再关 `uvicorn` (Ctrl+C)。

---

## 五、P0 阶段已完成功能

### 用户认证

| 端点 | 功能 | 状态 |
|------|------|------|
| `POST /api/auth/register` | 邮箱注册，返回 JWT | ✅ |
| `POST /api/auth/login` | 邮箱登录，返回 JWT | ✅ |
| `POST /api/auth/send-code` | 发送邮箱验证码 (开发模式打印控制台) | ✅ |
| `POST /api/auth/verify-email` | 验邮箱证码 | ✅ |
| `GET /api/auth/me` | JWT 获取当前用户信息 | ✅ |
| `PUT /api/auth/profile` | 修改昵称/头像 | ✅ |

### 食物库

| 端点 | 功能 | 状态 |
|------|------|------|
| `GET /api/foods/categories` | 获取 12 个食物分类 | ✅ |
| `GET /api/foods` | 关键词搜索 + 分类筛选 + 分页 | ✅ |
| `GET /api/foods/{id}` | 食物详情 (含营养数据) | ✅ |

### 前端页面

| 页面 | 功能 | 状态 |
|------|------|------|
| 登录/注册 | 绿白渐变背景，表单验证，JWT 存储 | ✅ |
| 首页 | 欢迎卡片 + 快捷入口 + 今日推荐 | ✅ |
| 食物库 | 搜索栏 + 分类标签 + 下拉分页 | ✅ |
| AI 对话 | 消息界面 + 流式 SSE 骨架 | ✅ (占位) |
| 记账 | 占位页 | ✅ (占位) |
| 个人中心 | 用户信息 + 退出 + 管理员入口 | ✅ |
| 管理后台 | 数据统计展示 | ✅ (占位) |
| 路由守卫 | 未登录自动跳转 /login | ✅ |

### 种子数据

- 12 个食物分类：川菜、粤菜、湘菜、鲁菜、日料、韩餐、西餐、小吃、甜品、饮品、面食、粥汤
- 20 条食物：麻婆豆腐、宫保鸡丁、水煮鱼、白切鸡、叉烧、虾饺、剁椒鱼头、红烧肉、寿司、拉面、石锅拌饭、韩式炸鸡、牛排、意面、煎饼果子、臭豆腐、提拉米苏、奶茶、兰州拉面、皮蛋瘦肉粥

---

## 六、关键配置说明 (.env)

```env
# ========== 数据库 ==========
DATABASE_URL=mysql+aiomysql://root:123456@localhost:3307/food_time

# ========== JWT ==========
JWT_SECRET=food-time-dev-secret-key-2026
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=10080       # 7 天

# ========== DeepSeek API ==========
DEEPSEEK_API_KEY=sk-...
DEEPSEEK_BASE_URL=https://api.deepseek.com/v1
DEEPSEEK_MODEL=deepseek-chat

# ========== Qwen VL API ==========
QWEN_API_KEY=sk-...
QWEN_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
QWEN_MODEL=qwen-vl-max

# ========== 邮件 SMTP ==========
SMTP_HOST=smtp.example.com
SMTP_PORT=587
SMTP_USER=noreply@food-time.com
SMTP_PASSWORD=

# ========== CORS ==========
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173

# ========== 管理员 ==========
ADMIN_EMAIL=admin@food-time.com
ADMIN_PASSWORD=admin123
```

- `JWT_SECRET` 部署时务必更换
- `DEEPSEEK_API_KEY` 和 `QWEN_API_KEY` 填入有效的 API Key
- `.env` 已加入 `.gitignore`，不会提交到 GitHub

---

## 七、数据库设计

### 13 张表

| 表名 | 说明 | 状态 |
|------|------|------|
| `users` | 用户表 (邮箱/密码哈希/昵称/管理员) | ✅ |
| `email_verifications` | 邮箱验证码表 | ✅ |
| `food_categories` | 食物分类表 | ✅ |
| `foods` | 食物表 (名称/分类/菜系/营养/标签) | ✅ |
| `custom_recipes` | 自定义食谱表 | ✅ |
| `custom_recipe_ingredients` | 食谱食材关联表 | ✅ |
| `diet_records` | 饮食记录表 | ✅ |
| `user_preferences` | 用户饮食偏好表 (预计算) | ✅ |
| `expense_records` | 账单记录表 | ✅ |
| `conversations` | 对话历史表 | ✅ |
| `long_memories` | 长期记忆表 | ✅ |
| `likes` | 点赞表 | ✅ |
| `favorites` | 收藏表 | ✅ |

### 关键设计决策

1. **食物标签用 JSON 字段**：`foods.tags = {"spicy": "high", "temp": "hot"}`，可用 MySQL JSON 函数查询
2. **营养成分存独立字段**：需要聚合计算，JSON 内字段无法高效聚合
3. **饮食偏好是预计算表**：定时任务分析 `diet_records` 后更新，避免全表扫描
4. **custom_recipes 与 foods 是 1:1**：每个自定义食谱创建一个 food 记录 (source='custom')

---

## 八、已知问题及注意事项

### 1. MySQL 端口
本机 MySQL 在端口 **3307**（非默认 3306），`.env` 中已配置。如果在其他机器部署，修改 `DATABASE_URL` 中的端口。

### 2. jose 库 `sub` 字段类型限制 (✅ 已修复)
- **症状**：`GET /api/auth/me` 返回 "Token 解析失败"
- **根因**：`python-jose` 要求 `sub` 必须是字符串，代码中传入 `int`
- **修复**：`service.py` 中 `str(user_id)`，`dependencies.py` 中 `int(user_id_str)` 转换

### 3. passlib + bcrypt 5.0 不兼容 (✅ 已修复)
- **症状**：启动时 `ValueError: password must be at most 72 bytes`
- **根因**：passlib 1.7.4 不支持 bcrypt 5.0
- **修复**：改用 `bcrypt` 库直接调用 `bcrypt.hashpw()` / `bcrypt.checkpw()`

### 4. 本机未安装 Node.js (⚠️ 需手动处理)
- 前端项目文件已创建，但本开发机未安装 Node.js
- 在 Windows 上安装 Node.js 后，在 `client/` 目录执行 `npm install && npm run dev`
- 或部署到有 Node.js 的云服务器

---

## 九、依赖

### 后端 (Python)

```
fastapi==0.115.6
uvicorn[standard]==0.34.0
sqlalchemy[asyncio]==2.0.36
aiomysql==0.2.0
alembic==1.14.1
pydantic[email]==2.10.4
pydantic-settings==2.7.1
python-jose[cryptography]==3.3.0
bcrypt==5.0.0
python-dotenv==1.0.1
aiohttp==3.11.11
beautifulsoup4==4.12.3
python-multipart==0.0.19
```

### 前端 (Node.js)

```
vue@3.4, vue-router@4.3, pinia@2.1, axios@1.6, vant@4.8
@vitejs/plugin-vue@5, vite@5, vite-plugin-pwa@0.17
unplugin-vue-components@0.26, @vant/auto-import-resolver@1.2
```

---

## 十、快速排查清单

| 现象 | 检查 |
|------|------|
| 启动报 ModuleNotFoundError | `cd server && pip install -r requirements.txt` |
| 数据库连接失败 | MySQL 是否运行？端口是否 3307？`DATABASE_URL` 是否正确？ |
| API 返回 "Token 解析失败" | `JWT_SECRET` 是否与服务端一致？Token 是否过期？ |
| 前端页面空白 | Node.js 是否安装？`cd client && npm install && npm run dev` |
| 食物搜索返回空 | 种子数据是否已插入？检查 `GET /api/foods/categories` 返回数 |
| CORS 报错 | `.env` 中 `CORS_ORIGINS` 是否包含前端地址？ |
| AI 对话无响应 | DeepSeek API Key 是否有效？`.env` 中是否已填写？ |

---

### 十一、2026-07-20 响应式布局改造

将项目从纯移动端（Vant TabBar always-on）改造为 **响应式网站**，适配参赛展示场景。

**改动**：
- `index.html`：移除 `maximum-scale=1.0, user-scalable=no`，回归标准 viewport
- `App.vue`：重写为双布局 — 桌端（≥768px）左侧固定侧边栏 + 主内容区，移动端底部 TabBar
- `main.css`：新增响应式断点、字体基准、通用卡片和页面容器样式

**桌面端**（≥768px）：
- 左侧 220px 绿色主题侧边栏（Logo + 导航 + 版本号）
- 主内容区自适应，max-width 960px 居中

**移动端**（<768px）：
- 全宽布局，底部 Vant TabBar
- 14px 基准字体，12px 卡片内边距

**文件改动**：
| 文件 | 改动 |
|------|------|
| `index.html` | viewport 恢复正常 |
| `App.vue` | 全面重写，双布局 |
| `main.css` | 响应式样式系统 |

---

## 十二、开发计划

| 阶段 | 内容 | 状态 |
|------|------|------|
| P0 | 项目骨架 + 数据库模型 + 用户认证 + 前端导航 + 种子数据 | ✅ 已完成 |
| P1 | AI 对话 (SSE + Tool Calling) + 食物库爬虫 + 饮食记录 + 记账 OCR | 📋 待开始 |
| P2 | 拖拽烹饪 + 公共广场 + 转盘决策 + 营养分析图表 + 食物决策 | 📋 待开始 |
| P3 | PWA 离线缓存 + 偏好分析 + 管理后台 + 测试 + 文档完善 | 📋 待开始 |

---

## 十三、2026-07-20 P0 阶段工作总结（第一轮交接）

### 一、项目骨架搭建

**创建内容**：
- 完整项目目录结构（8 个后端功能模块 + 前端 8 个页面）
- 每个模块独立 `models.py` + `router.py`，互不干扰
- `__init__.py` 包结构清晰

### 二、数据库模型设计

- 13 张表 SQLAlchemy 异步模型
- 统一 `Base` 声明基类 + `models.py` 统一导入入口
- `init_db.py` 独立建表逻辑（避免循环导入）

### 三、用户认证系统

- bcrypt 密码哈希（直调 `bcrypt.hashpw`，不依赖 passlib）
- JWT 签发与验证（7 天过期）
- 邮箱验证码（开发模式打印控制台）
- 管理员账号自动初始化
- 路由守卫中间件（`get_current_user` / `get_admin_user`）

### 四、种子数据

- 12 个食物分类 + 20 条中英文食物（含完整营养数据）
- 幂等插入（重复执行不重复写入）
- 启动时自动执行

### 五、前端脚手架

- Vue 3 + Vite + Vant UI 移动端组件库
- **响应式双导航**：桌面端（≥768px）侧边栏 + 主内容区；移动端底部 TabBar
- 路由守卫（未登录 → /login）
- Axios 拦截器（自动附加 JWT + 401 跳转）
- Vite proxy 代理 `/api` → 后端

### 六、修复的 Bug

| # | 问题 | 修复方式 |
|---|------|----------|
| 1 | `database.py` 循环导入 | 创建 `init_db.py` 独立文件，Base 定义与模型导入分离 |
| 2 | `aiomysql` `pool_pre_ping` 不支持 | 关闭 `pool_pre_ping` |
| 3 | passlib + bcrypt 5.0 不兼容 | 改用 `bcrypt` 直接调用 |
| 4 | jose `sub` 字段必须为字符串 | encoding 用 `str()`，decoding 用 `int()` |

### 七、文件改动清单

| 文件 | 改动类型 |
|------|----------|
| `server/app/main.py` | **新增** — FastAPI 入口 + lifespan + 路由注册 |
| `server/app/config.py` | **新增** — Pydantic Settings 配置管理 |
| `server/app/database.py` | **新增** — 异步引擎 + 会话工厂 + Base |
| `server/app/init_db.py` | **新增** — 建表逻辑（解循环导入） |
| `server/app/dependencies.py` | **新增** — JWT 依赖注入 |
| `server/app/models.py` | **新增** — 模型统一导入 |
| `server/app/seed.py` | **新增** — 种子数据 |
| `server/app/auth/*` | **新增** — 完整认证模块 |
| `server/app/food/*` | **新增** — 食物库（搜索 + 分类） |
| `server/app/chat/*` | **新增** — AI 对话（骨架） |
| `server/app/diet/*` | **新增** — 饮食记录（骨架） |
| `server/app/expense/*` | **新增** — 记账（骨架） |
| `server/app/custom_food/*` | **新增** — 自定义食物（骨架） |
| `server/app/public_food/*` | **新增** — 公共广场（骨架） |
| `server/app/admin/*` | **新增** — 管理后台（骨架） |
| `server/app/services/*` | **新增** — 外部服务（骨架） |
| `server/.env` | **新增** |
| `server/.env.example` | **新增** |
| `server/requirements.txt` | **新增** |
| `.gitignore` | **新增** |
| `client/package.json` | **新增** |
| `client/vite.config.js` | **新增** |
| `client/index.html` | **新增** |
| `client/src/*` | **新增** — 全部前端代码 |
| `docs/` | **新增** — 全部设计文档 |

### 八、验证结果

- ✅ `POST /api/auth/register` — 注册返回 JWT + User
- ✅ `POST /api/auth/login` — 登录返回 JWT + User
- ✅ 重复邮箱注册被正确拒绝
- ✅ `GET /api/foods` — 返回 20 条种子数据
- ✅ `GET /api/foods/categories` — 返回 12 个分类
- ✅ `GET /api/auth/me` — JWT 认证返回用户信息
- ✅ `GET /api/health` — 健康检查

### 九、下次接手建议

1. 先检查 `.env` 中的 `DEEPSEEK_API_KEY` 和 `QWEN_API_KEY` 是否已填入有效值
2. 如果需要测试前端，先安装 Node.js，在 `client/` 目录执行 `npm install && npm run dev`
3. 全部测试通过后，推送到 GitHub：`https://github.com/zhan-zip/Food-Time`

---

**最后更新：** 2026-07-20 18:30  
**项目路径：** `d:\Desktop\test\TreaWork\Food-Time\`  
**开发周期：** 3 个月（至 2026 年 10 月）
