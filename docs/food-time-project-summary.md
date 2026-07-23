# Food-Time 项目进度文档

## 一、项目概述

基于 FastAPI + Vue 3 + DeepSeek/Qwen VL 的智能饮食辅助网站，面向「山东省大学生软件设计大赛」AI 创新应用开发赛道。

**目录：** `d:\Desktop\test\TreaWork\Food-Time\`

**仓库：** <https://github.com/zhan-zip/Food-Time>

**开发周期：** 2026年7月—10月（3个月），单人全栈开发

---

## 二、架构

```
浏览器 (Vue 3 + 纯 CSS 桌面端组件)
  ↕ HTTP REST + SSE 流式
FastAPI 网站服务器 (Python)
  ↕ SQLAlchemy 异步
MySQL 8.0
  ↗ DeepSeek API (对话 + Tool Calling)
  ↗ Qwen VL API (账单 OCR)
```

- **前端**：Vue 3 + Vite + 纯 CSS 桌面端组件 + Pinia + Vue Router
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
│       ├── App.vue                       ← 根组件 (顶部导航栏 + 路由)
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
├── start.bat                            ← 一键启动脚本（前后端同时启动）
│
└── server/                               ← 后端项目
    ├── requirements.txt                  ← Python 依赖
    ├── .env                              ← 环境变量 (gitignored)
    ├── .env.example                      ← 环境变量模板
    └── src/
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
python -m uvicorn src.main:app --host 0.0.0.0 --port 8000
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

### 3. 一键启动（推荐）

```powershell
# 双击项目根目录的 start.bat
# 自动启动后端 (8000) 和前端 (5173)
```

### 4. 关闭顺序

先关前端 `npm run dev` (Ctrl+C)，再关 `uvicorn` (Ctrl+C)。

**注意**：Windows 下 `start.bat` 在新窗口中启动前后端，关闭对应窗口即可。

---

## 五、P0 阶段已完成功能

### 用户认证

| 端点 | 功能 | 状态 |
|------|------|------|
| `POST /api/auth/register` | 邮箱注册，返回 JWT | ✅ |
| `POST /api/auth/login` | 邮箱登录，返回 JWT | ✅ |
| `POST /api/auth/send-code` | 发送邮箱验证码（SMTP 真实发邮件 / 未配置时降级控制台） | ✅ |
| `POST /api/auth/verify-email` | 验证邮箱验证码 | ✅ |
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
# 部署时按需配置，支持 QQ邮箱/163邮箱/Gmail 等
# QQ邮箱：SMTP_HOST=smtp.qq.com  SMTP_PORT=587（需开启SMTP服务并获取授权码）
# 未配置时验证码降级打印到控制台
SMTP_HOST=smtp.qq.com
SMTP_PORT=587
SMTP_USER=your-email@qq.com
SMTP_PASSWORD=your-auth-code
SMTP_FROM=your-email@qq.com

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

### 4. 本机已安装 Node.js (✅ 已解决)
- Node.js v24.18.0 + npm 11.16.0 已通过 winget 安装
- 在 `client/` 目录执行 `npm install && npm run dev` 即可启动前端

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
vue@3.4, vue-router@4.3, pinia@2.1, axios@1.6
@vitejs/plugin-vue@5, vite@5
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

### 十一、2026-07-20 T0 桌面端重构（全部推倒重来）

彻底移除 Vant UI，改为纯 CSS 桌面端组件 + 暖色调品牌设计。

**设计依据**：`界面设计初版方案.md`

**品牌更新**：
- 项目中文名定为「食光记」
- 简介：一款 AI 驱动的智能饮食助手，帮您解决「今天吃什么」的每一刻
- 暖色调色板：铜锣烧金 #D9A15B / 奶咖米 #D8B08C / 黑可可 #3A2418

**T0 架构改动**：

| 文件 | 改动 |
|------|------|
| `main.js` | 移除 Vant CSS import |
| `main.css` | 完全重写：CSS 自定义变量暖色系色板 + 通用组件（按钮/卡片/输入框/标签）+ 3 档响应式 |
| `App.vue` | 完全重写：顶部 sticky navbar + 左侧滑动 sidebar + 汉堡菜单切换 |
| `router/index.js` | 路由重构：5 个标签 → 12 个路由（6 主导航 + 登录/注册/管理/广场详情） |
| `package.json` | 移除 vant / @vant/use / unplugin-vue-components / @vant/auto-import-resolver |
| `vite.config.js` | 移除 Vant 自动导入插件 |
| `index.html` | 标题改为「食光记」 |

**导航结构**：
| 路由 | 页面 | 说明 |
|------|------|------|
| `/` | 首页 | Banner 轮播 + 每日推荐 + 功能介绍 |
| `/today-eat` | 今天吃什么 | 搜索/分类筛选/转盘/AI决策入口 |
| `/diy` | 我的厨房 | 食材篮子 + 调料台 + AI 烹饪建议 |
| `/square` | 美食广场 | 3 列卡片网格 |
| `/square/:id` | 食谱详情 | 食材/步骤/营养数据/评论区 |
| `/expense` | 记账 | 手动录入 + OCR 拍照 + 统计图 |
| `/assistant` | AI 助手 | 聊天界面 + 快捷提问 + SSE 骨架 |
| `/about` | 关于我 | 个人信息 + 饮食偏好 + 营养分析 + 退出 |
| `/admin` | 管理后台 | 数据统计 + 用户管理 + 食谱审核 |

**删除的旧页面**：`Food.vue`、`Chat.vue`、`Profile.vue`

**响应式策略**：
- 桌面（>768px）：粘性顶栏 + 多列网格布局
- 移动（≤768px）：顶栏 + 汉堡菜单展开侧栏 + 单列布局
- 移动（≤640px）：全部单列

---

## 十二、开发计划

| 阶段 | 内容 | 状态 |
|------|------|------|
| P0 | 项目骨架 + 数据库模型 + 用户认证 + 前端导航 + 种子数据 + 真实邮件验证 | ✅ 已完成 |
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

- Vue 3 + Vite + 纯 CSS 桌面端组件
- **响应式双导航**：桌面端（≥768px）顶部导航栏；移动端汉堡菜单 + 侧边栏
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
| `服务器/src/main.py` | **新增** — FastAPI 入口 + lifespan + 路由注册 |
| `服务器/src/config.py` | **新增** — Pydantic Settings 配置管理 |
| `服务器/src/database.py` | **新增** — 异步引擎 + 会话工厂 + Base |
| `服务器/src/init_db.py` | **新增** — 建表逻辑（解循环导入） |
| `服务器/src/dependencies.py` | **新增** — JWT 依赖注入 |
| `服务器/src/models.py` | **新增** — 模型统一导入 |
| `服务器/src/seed.py` | **新增** — 种子数据 |
| `服务器/src/auth/*` | **新增** — 完整认证模块 |
| `服务器/src/food/*` | **新增** — 食物库（搜索 + 分类） |
| `服务器/src/chat/*` | **新增** — AI 对话（骨架） |
| `服务器/src/diet/*` | **新增** — 饮食记录（骨架） |
| `服务器/src/expense/*` | **新增** — 记账（骨架） |
| `服务器/src/custom_food/*` | **新增** — 自定义食物（骨架） |
| `服务器/src/public_food/*` | **新增** — 公共广场（骨架） |
| `服务器/src/admin/*` | **新增** — 管理后台（骨架） |
| `服务器/src/services/*` | **新增** — 外部服务（骨架） |
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

## 十四、2026-07-23 登录注册完善 & 邮件系统联调

### 一、发现问题

1. **注册按钮卡住无响应**：前端 `Register.vue` 使用原生 `axios` 发请求到后端 `localhost:8000`，后端未启动时请求无超时配置导致无限等待
2. **前后端需手动分别启动**：开发体验差，不符合部署预期
3. **邮箱验证码仅打印控制台**：无法真正发送邮件，注册验证形同虚设
4. **登录/注册表单无校验提示**：用户输入错误格式的邮箱或密码没有即时反馈
5. **历史 Bug：登录密码从未被发送**：`auth.js` 的 `login(email, password)` 函数签名与调用不匹配

### 二、功能实现

#### 2.1 真实 SMTP 邮件发送

**新增/修改文件**：
| 文件 | 改动 |
|------|------|
| `服务器/src/services/email.py` | 完全重写：`EmailService` 类支持 SSL(465) 和 STARTTLS(587) 双模式；`send_verification_code()` 发送格式化 HTML 邮件；`is_configured` 自动检测 SMTP 是否就绪 |
| `服务器/src/auth/router.py` | `send-code` 端点增加 SMTP 真实发送分支，内置降级机制（SMTP 未配置时打印到控制台） |
| `server/.env.example` | SMTP 配置模板更新为 QQ邮箱默认值 + 详细注释 |

**技术细节**：
- `smtplib` 是同步阻塞库，会使 FastAPI 异步事件循环卡死
- 修复方式：用 `asyncio.to_thread()` 将 SMTP 调用丢到线程池执行，避免阻塞主循环

#### 2.2 前端表单校验

**新增**：`Register.vue` 完全重写，`Login.vue` 同步升级

| 校验项 | 规则 | 表现 |
|--------|------|------|
| 昵称 | 非空 + ≥2 个字 | 红色边框 + 字段下方红字提示 |
| 邮箱 | 正则 `/^[^\s@]+@[^\s@]+\.[^\s@]+$/` | 红色边框 + "邮箱格式不正确，例如 example@qq.com" |
| 密码 | ≥6 位 + 需含字母或数字 | 红色边框 + 对应提示 |
| 验证码 | 非空 | 红色边框 |

**新增 UI 元素**：
- 正确时：灰色小字提示（如"用于接收验证码和找回密码"）
- 验证码已发送：绿色小字 "验证码已发送到 xxx，请查收"
- 60 秒发送倒计时按钮，防止重复点击

#### 2.3 一键启动脚本

**新增**：`start.bat`（项目根目录）
- 双击打开两个新窗口分别启动前后端
- 自动等待 5 秒给数据库初始化
- 打印启动完成提示和访问地址

#### 2.4 Bug 修复

| Bug | 文件 | 修复 |
|-----|------|------|
| `Register.vue` 用原生 axios 无超时 | `Register.vue` | 改用 `request` 实例（30s 超时 + JWT 拦截器） |
| `Login.vue` 密码从未发送到后端 | `client/src/api/auth.js` | `login(email, password)` 改为独立参数，内部封装 `{ email, password }` |
| 后端未启动时注册无限等待 | 启动后端 + 前端请求实例超时 | 组合修复 |

#### 2.5 文档术语清理

| 文件 | 改动 |
|------|------|
| 全部 5 个 MD 设计文档 | "app"/"App"/"应用" → "服务"/"网站"/"页面" |
| `服务器/src/main.py` | `"app"` key → `"service"` 描述 |

### 三、验证结果

- ✅ SMTP 连接 `smtp.qq.com:587` 成功，邮件 3.4 秒内发送
- ✅ `POST /api/auth/send-code` — 返回 `{"message": "验证码已发送到您的邮箱"}`
- ✅ 退信 `test@test.com` 仅为排查 API 时的测试参数，非注册表单 Bug
- ✅ 登录/注册表单校验即时反馈，红框 + 小字提示
- ✅ `start.bat` 一键启动前后端正常

### 四、文件改动清单

| 文件 | 改动类型 |
|------|----------|
| `server/src/services/email.py` | **重写** — smtplib 真实发送 + 降级机制 |
| `server/src/auth/router.py` | **修改** — send-code 增加 SMTP 分支 + `asyncio.to_thread` |
| `client/src/views/Register.vue` | **重写** — 完整表单校验 + request 实例 + 倒计时 |
| `client/src/views/Login.vue` | **重写** — 表单校验 + 结构对齐 Register |
| `client/src/api/auth.js` | **修改** — login 函数签名修复 |
| `start.bat` | **新增** — 一键启动脚本 |
| `server/.env.example` | **修改** — SMTP 配置模板 |
| `server/.env` | **修改** — SMTP_HOST 修正为 smtp.qq.com |
| `docs/*.md` 全部 5 个文档 | **修改** — "app" 术语替换 |

---

## 十五、2026-07-23 美食广场 + 食谱详情 + 评论区

### 一、实现内容

在 P1 阶段开始前，提前补全了美食广场的三个核心页面，从纯静态占位升级为完整功能。

### 二、后端

#### 2.1 新增 Comment 模型

```python
# server/src/public_food/models.py
class Comment(Base):
    __tablename__ = "recipe_comments"
    id, recipe_id, user_id, content, created_at
```

#### 2.2 Food 模型增加 description 字段

`server/src/food/models.py`：新增 `description = Column(Text, nullable=True)`

#### 2.3 6 个新 API 端点

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/public/recipes` | GET | 食谱列表（分页 + 作者 + 点赞收藏数） |
| `/api/public/recipes/{id}` | GET | 食谱详情（食材/调料/步骤/营养/评论数） |
| `/api/public/recipes/{id}/comments` | GET | 评论列表（含用户昵称） |
| `/api/public/recipes/{id}/comment` | POST | 发表评论（需登录） |
| `/api/public/recipes/{id}/save` | POST | 收藏到我的食物库（需登录） |
| `/api/public/recipes/{id}/save` | DELETE | 取消收藏（需登录） |

#### 2.4 4 个种子食谱

| 食谱 | 菜系 | 食材数 | 步骤数 |
|------|------|--------|--------|
| 番茄炒蛋 | 川菜 | 2食材+3调料 | 5步 |
| 宫保鸡丁（家常版） | 川菜 | 4食材+7调料 | 8步 |
| 日式味噌汤 | 日料 | 3食材+2调料 | 6步 |
| 黑椒牛排 | 西餐 | 3食材+5调料 | 7步 |

### 三、前端

#### 3.1 Square.vue（美食广场列表）

- 移除 `v-for="n in 6"` 静态占位
- 接入 `GET /api/public/recipes` 真实数据
- 卡片悬停上浮动效 (`transform: translateY(-2px)`)
- 空状态提示：暂无食谱时显示"还没有人分享食谱"

#### 3.2 SquareDetail.vue（食谱详情）

完全重写，包含以下功能区块：

| 区块 | 实现方式 |
|------|----------|
| 食物名 + 作者 + 日期 | `h1` + meta 信息行 |
| 菜系/难度标签 | `tag tag-primary` + 自定义中文映射 |
| 食物简介 | 段落文本，行高 1.8 |
| 食材列表 | 金色背景标签，显示名称+分量 |
| 调料列表 | 绿色背景标签 |
| 做法步骤 | `<ol>` 有序列表，1.7 行高 |
| 营养成分卡片 | 左侧 sticky 侧边栏，2x2 网格 |
| 添加到我的食物库 | 大按钮，收藏/取消收藏切换 |
| 评论区 | 发表框 + 评论列表，需登录 |
| 404 处理 | 食谱不存在时显示错误页 + 返回按钮 |

### 四、修复的 Bug

| Bug | 修复 |
|-----|------|
| `/api/api/public/recipes` 双前缀 | `public.js` 路径去掉 `/api` 前缀（`request.js` 已设 `baseURL: '/api'`） |
| `res.data.items` 取不到数据 | axios 拦截器已返回 `response.data`，改为直接 `res.items` |
| `e.response?.data?.detail` 取不到 | 拦截器已转 `Error(message)`，改为 `e.message` |

### 五、文件改动

| 文件 | 类型 | 说明 |
|------|------|------|
| `server/src/public_food/models.py` | 修改 | 新增 Comment 模型 |
| `server/src/public_food/router.py` | 重写 | 6 个 API 端点 |
| `server/src/food/models.py` | 修改 | 新增 description 列 |
| `server/src/models.py` | 修改 | 注册 Comment |
| `server/src/seed.py` | 修改 | 新增 4 个种子食谱 |
| `client/src/api/public.js` | 新增 | 广场 API 封装 |
| `client/src/views/Square.vue` | 重写 | 接入真实数据 |
| `client/src/views/SquareDetail.vue` | 重写 | 完整详情页 |

### 六、验证

- ✅ `GET /api/public/recipes` — 返回 4 个食谱、正确分页
- ✅ `GET /api/public/recipes/1` — 返回番茄炒蛋，含 2食材+3调料+5步骤
- ✅ 前端广场页加载 4 张卡片，点击跳转详情页
- ✅ 详情页展示完整信息，评论区未登录时提示登录

---

**最后更新：** 2026-07-23  
**项目路径：** `d:\Desktop\test\TreaWork\Food-Time\`  
**开发周期：** 3 个月（至 2026 年 10 月）
