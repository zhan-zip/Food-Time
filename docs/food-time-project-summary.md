# Food-Time 项目交接文档

## 一、项目概述

基于 FastAPI + Vue 3 + DeepSeek/Qwen VL 的智能饮食辅助网站，面向「山东省大学生软件设计大赛」AI 创新应用开发赛道。

**目录：** `d:\Desktop\test\TreaWork\Food-Time\`

**仓库：** <https://github.com/zhan-zip/Food-Time>

**开发周期：** 2026年7月—10月（3个月），单人全栈开发

***

## 管理员账号（2026-08-01 更新）

| 项 | 值 |
|---|---|
| 后台入口 | 浏览器网址后输入 `/admin`（无前端导航入口，按设计预期） |
| 管理员邮箱 | `admin@food-time.com` |
| 管理员密码 | `8WnxP*dBPVLQNoLm` |

> ⚠️ **安全提醒**：该密码由 C2 安全修复将默认值 `admin123` 重置为强随机密码，来源为 `server/.env` 的 `ADMIN_PASSWORD`，并已写入本公开仓库文档。**对外部署前务必在 `server/.env` 修改密码，并同步更新本表**。若数据库中的管理员密码仍是旧默认值，后端启动时会被自动重置为本密码。

***

## 二、架构

```
浏览器 (Vue 3 + 纯 CSS 桌面端组件)
  ↕ HTTP REST + SSE 流式
FastAPI 网站服务器 (Python)
  ↕ SQLAlchemy 异步        ↗ DeepSeek API (对话 + Tool Calling + Embedding)
MySQL 8.0                  ↗ Qwen VL API (账单 OCR + 食物图片识别)
                           ↗ ChromaDB (RAG 向量检索)
```

* **前端**：Vue 3 + Vite + 纯 CSS 桌面端组件 + Pinia + Vue Router

* **后端**：FastAPI 异步框架，8 个功能模块，JWT 认证

* **数据库**：MySQL 8.0，15 张表，utf8mb4

* **AI**：DeepSeek chat 对话与工具调用，Qwen VL 视觉识别

***

## 三、文件结构（2026-07-24 P1 阶段）

```
Food-Time/
├── .gitignore
├── start.bat                            ← 一键启动脚本
├── 需求分析说明书.md
├── 概要设计说明书.md
├── 数据库设计说明书.md
├── 界面设计初版方案.md
├── 新增需求记录.md
│
├── docs/                                ← 项目文档
│   ├── food-time-project-summary.md     ← 本文档
│   └── 项目实施计划.md
│
├── client/                              ← 前端项目
│   ├── package.json
│   ├── vite.config.js                   ← Vite 配置 + /api 代理（→ localhost:8000）
│   ├── index.html
│   └── src/
│       ├── main.js
│       ├── App.vue
│       ├── router/index.js              ← 12 个路由 + 登录守卫
│       ├── api/
│       │   ├── request.js               ← Axios 封装 + JWT 拦截器
│       │   ├── auth.js
│       │   ├── diy.js                    ← DIY 厨房 API（食材列表+建议+保存+我的菜谱）
│       │   ├── expense.js
│       │   ├── public.js
│       │   ├── admin.js
│       │   ├── diet.js
│       ├── components/
│       │   ├── diy/                      ← DIY 厨房组件
│       │   │   ├── FridgeSection.vue     ←   双开门冰箱（开合动画+食材选择）
│       │   │   ├── IngredientCard.vue    ←   食材卡片（emoji+名称+色条）
│       │   │   ├── PlateSection.vue      ←   备菜盘（食材排列+弹入动画）
│       │   │   ├── SeasoningRack.vue     ←   调料台（横滚抽屉）
│       │   │   ├── CookingPanel.vue      ←   烹饪面板（方式选择+AI建议展示）
│       │   │   └── SaveDialog.vue        ←   保存弹窗（菜名+描述+烹饪方式可选+发布到广场）
│       │   └── today/                    ← 今天吃什么组件
│       │       └── SpinWheel.vue         ←   决策转盘（Canvas多扇形+旋转动画）
│       ├── stores/
│       │   └── diy.js                    ← DIY 厨房状态管理（Pinia）
│       ├── assets/main.css              ← 暖色调全局样式
│       └── views/
│           ├── Home.vue                 ← 首页
│           ├── TodayEat.vue             ← 今天吃什么（搜索+饮食记录）
│           ├── DIY.vue                  ← 我的厨房（双开门冰箱+岛台+飞入动画）
│           ├── Square.vue               ← 美食广场（真实数据）
│           ├── SquareDetail.vue         ← 食谱详情+评论区
│           ├── Expense.vue              ← 记账（手动录入+OCR识图+统计图表）
│           ├── Assistant.vue            ← AI助手（SSE流式+快捷决策面板）
│           ├── About.vue                ← 关于我（个人信息+营养分析图表）
│           ├── Admin.vue                ← 管理后台（数据统计+食谱审核+用户管理）
│           ├── AdminLogin.vue           ← 管理员独立登录页
│           ├── Login.vue                ← 登录
│           └── Register.vue             ← 注册
│
└── server/                              ← 后端项目
    ├── requirements.txt
    ├── .env                             ← 环境变量 (gitignored)
    ├── .env.example
    ├── import_scraped.py                ← 下厨房数据导入脚本
    ├── import_meishi.py                 ← 美食天下数据导入脚本
    └── src/
        ├── main.py                      ← FastAPI 入口 (lifespan: 建表+种子+向量索引)
        ├── config.py
        ├── database.py
        ├── init_db.py
        ├── dependencies.py
        ├── models.py
        ├── seed.py
        ├── auth/                        ← 用户认证（完整）
        ├── food/                        ← 食物库（完整）
        ├── chat/                        ← AI 对话（完整: SSE + Tool Calling + RAG）
        │   ├── persona.txt              ← AI 人设提示词
        │   └── ...
        ├── diet/                        ← 饮食记录（完整）
        ├── expense/                     ← 记账（完整: 手动+OCR+统计）
        ├── custom_food/                 ← 自定义食物（完整: AI建议+保存+我的菜谱+发布广场）
        ├── public_food/                 ← 公共广场（完整: 列表+详情+评论+收藏）
        ├── admin/                       ← 管理后台（基础统计）
        └── services/
            ├── deepseek.py              ← DeepSeek 客户端（对话+Embedding+Tool Calling）
            ├── qwen.py                  ← Qwen VL 客户端（OCR+食物分析）
            ├── email.py                 ← 邮件服务（SMTP）
            ├── vector_store.py          ← ChromaDB 向量检索
            ├── nutrition_ref.py         ← 213种食材营养参考数据
            ├── ingredient_emoji.py      ← 食材Emoji映射表（50+食材）
            ├── scraper.py               ← 下厨房爬虫
            ├── scraper_meishi.py        ← 美食天下爬虫（curl_cffi）
            └── vision.py                ← Qwen VL 视觉模型客户端（骨架）
```

**模块独立性说明**：每个功能模块有独立的 `models.py` + `router.py`，跨模块引用走明确包路径。某个模块（如 chat）出问题，food、auth 等模块完全不受影响。

***

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
python -m uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

启动后自动完成：

* 建表（15 张表）

* 创建管理员账号（<admin@food-time.com> / admin123）

* 插入种子数据（12 个食物分类 + 102 条食物）

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

***

## 五、已完成功能

### 后端模块

| 模块           | 路由前缀             | 状态   | 说明                                  |
| ------------ | ---------------- | ---- | ----------------------------------- |
| auth         | `/api/auth/*`    | ✅ 完整 | 注册/登录/验证码/个人资料，SMTP真实邮件             |
| food         | `/api/foods/*`   | ✅ 完整 | 搜索/分类/详情/分页，766条数据                  |
| chat         | `/api/chat/*`    | ✅ 完整 | SSE流式 + Tool Calling(10工具) + 多模态    |
| diet         | `/api/diet/*`    | ✅ 完整 | 饮食记录CRUD + 偏好自动更新                   |
| expense      | `/api/expense/*` | ✅ 完整 | 手动录入 + OCR(后端代理Qwen VL) + 统计数据      |
| public\_food | `/api/public/*`  | ✅ 完整 | 广场列表 + 详情 + 评论 + 收藏 + 食谱保存          |
| custom\_food | `/api/custom/*`  | ✅ 完整 | AI建议 + 保存菜谱 + 我的菜谱列表 + 发布到广场        |
| admin        | `/api/admin/*`   | ✅ 完整 | 统计数据 + 审核通过/拒绝 + 用户管理(封禁/解封/升降级/删除) |

### 前端页面

| 页面    | 功能                                               | 状态 |
| ----- | ------------------------------------------------ | -- |
| 登录/注册 | 完整表单校验 + SMTP邮件验证 + 倒计时                          | ✅  |
| 首页    | 欢迎卡片 + 快捷入口 + 今日推荐                               | ✅  |
| 今天吃什么 | 搜索栏 + 分类标签 + 食物卡片 + "我吃了这个"饮食记录                  | ✅  |
| 我的厨房  | 双开门冰箱+岛台备菜盘+飞入动画+AI建议+烹饪保存                       | ✅  |
| 美食广场  | 食谱列表 + 详情页 + 评论区 + 收藏 + 排序切换                     | ✅  |
| 记账    | 输入账单 + OCR识别账单截图 + ECharts饼图/折线图统计                      | ✅  |
| AI 助手 | SSE 流式对话 + 10个Tool Calling + RAG + 快捷决策面板 + 图片分析 | ✅  |
| 关于我   | 个人信息 + 偏好 + 7/30天营养图表                            | ✅  |
| 管理后台  | 数据统计 + 食谱审核 + 用户管理（封禁/升降级/删除）                    | ✅  |
| 管理员登录 | 独立管理员登录页                                         | ✅  |
| 路由守卫  | 未登录自动跳转 /login                                   | ✅  |
| 技术改进  | ECharts 图表（替换 Canvas）+ SCSS 支持（Vite 原生）              | ✅  |

### 用户认证 API

| 端点                            | 功能                              |
| ----------------------------- | ------------------------------- |
| `POST /api/auth/register`     | 邮箱注册，返回 JWT                     |
| `POST /api/auth/login`        | 邮箱登录，返回 JWT                     |
| `POST /api/auth/send-code`    | 发送邮箱验证码（SMTP 真实发邮件 / 未配置时降级控制台） |
| `POST /api/auth/verify-email` | 验证邮箱验证码                         |
| `GET /api/auth/me`            | JWT 获取当前用户信息                    |
| `PUT /api/auth/profile`       | 修改昵称/头像                         |

### 食物库 API

| 端点                          | 功能                |
| --------------------------- | ----------------- |
| `GET /api/foods/categories` | 获取食物分类            |
| `GET /api/foods`            | 关键词搜索 + 分类筛选 + 分页 |
| `GET /api/foods/{id}`       | 食物详情 (含营养数据)      |
| `GET /api/foods/ingredients` | DIY厨房食材列表（冰箱分区+emoji+色条） |

***

## 六、关键配置说明 (.env)

```env
# ========== 数据库 ==========
DATABASE_URL=mysql+aiomysql://root:password@localhost:3306/food_time

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

* `JWT_SECRET` 部署时务必更换

* `DEEPSEEK_API_KEY` 和 `QWEN_API_KEY` 填入有效的 API Key

* `.env` 已加入 `.gitignore`，不会提交到 GitHub

***

## 七、数据库设计

### 15 张表

| 表名                          | 说明                                    | 状态 |
| --------------------------- | ------------------------------------- | -- |
| `users`                     | 用户表 (邮箱/密码哈希/昵称/管理员)                  | ✅  |
| `email_verifications`       | 邮箱验证码表                                | ✅  |
| `food_categories`           | 食物分类表                                 | ✅  |
| `foods`                     | 食物表 (名称/分类/菜系/营养/标签)                  | ✅  |
| `custom_recipes`            | 自定义食谱表                                | ✅  |
| `custom_recipe_ingredients` | 食谱食材关联表                               | ✅  |
| `diet_records`              | 饮食记录表                                 | ✅  |
| `user_preferences`          | 用户饮食偏好表 (预计算)                         | ✅  |
| `expense_records`           | 账单记录表                                 | ✅  |
| `conversations`             | 对话历史表                                 | ✅  |
| `long_memories`             | 长期记忆表                                 | ✅  |
| `likes`                     | 点赞表                                   | ✅  |
| `favorites`                 | 收藏表                                   | ✅  |
| `recipe_comments`           | 食谱评论表 (recipe\_id, user\_id, content) | ✅  |
| `deleted_users`             | 已删除用户审计表（2026-08-01 新增）            | ✅  |

### 关键设计决策

1. **食物标签用 JSON 字段**：`foods.tags = {"spicy": "high", "temp": "hot"}`，可用 MySQL JSON 函数查询
2. **营养成分存独立字段**：需要聚合计算，JSON 内字段无法高效聚合
3. **饮食偏好是预计算表**：定时任务分析 `diet_records` 后更新，避免全表扫描
4. **custom\_recipes 与 foods 是 1:1**：每个自定义食谱创建一个 food 记录 (source='custom')

***

## 八、开发计划

| 阶段 | 内容                                                                        | 状态 |
| -- | ------------------------------------------------------------------------- | ------- |
| P0 | 项目骨架 + 数据库模型 + 用户认证 + 前端导航 + 种子数据 + 真实邮件验证                                | ✅ 已完成   |
| P1 | AI 对话 (SSE + Tool Calling + RAG) + 食物库爬虫(766条) + 饮食记录 + 记账(OCR+统计) + 快捷决策 | ✅ 已完成   |
| P2-1 | DIY 烹饪 + 烹饪动画                                                               | ✅ 已完成   |
| P2-2 | 广场排序/筛选/审核 + 管理员登录安全 + 用户管理                                               | ✅ 已完成   |
| P2-3 | 食物决策辅助（属性筛选 + 随机转盘 + 附近推荐）                                      | ✅ 已完成（FR-23 AI推荐已移除） |
| P2-4 | SCSS 技术改进                                                                  | ✅ 已完成   |
| P3 | PWA 离线缓存 + 赛事文档 + 演示视频 + 全面美化                                            | 📋 待开始  |

***

## 九、已知问题及注意事项

### 1. MySQL 端口

本机 MySQL 在端口 **3307**（非默认 3306），`.env` 中已配置。如果在其他机器部署，修改 `DATABASE_URL` 中的端口。

### 2. jose 库 `sub` 字段类型限制 (✅ 已修复)

* **症状**：`GET /api/auth/me` 返回 "Token 解析失败"

* **根因**：`python-jose` 要求 `sub` 必须是字符串，代码中传入 `int`

* **修复**：`service.py` 中 `str(user_id)`，`dependencies.py` 中 `int(user_id_str)` 转换

### 3. passlib + bcrypt 5.0 不兼容 (✅ 已修复)

* **症状**：启动时 `ValueError: password must be at most 72 bytes`

* **根因**：passlib 1.7.4 不支持 bcrypt 5.0

* **修复**：改用 `bcrypt` 库直接调用 `bcrypt.hashpw()` / `bcrypt.checkpw()`

### 4. 本机已安装 Node.js (✅ 已解决)

* Node.js v24.18.0 + npm 11.16.0 已通过 winget 安装

* 在 `client/` 目录执行 `npm install && npm run dev` 即可启动前端

### 5. openai 与 httpx 版本兼容 (✅ 已解决)

- `openai==1.35.10` 向 `httpx==0.28.1` 传入废弃的 `proxies` 参数 → `AsyncClient.__init__()` 报错 → AI 对话无响应
- **修复**：`pip install "httpx>=0.27,<0.28"` 降级 httpx 到 0.27.2

### 6. passlib[bcrypt] 为遗留依赖 (⚠ 注意)

- `requirements.txt` 中仍保留 `passlib[bcrypt]==1.7.4`，但运行时已改用 `import bcrypt` 直接调用 `bcrypt.hashpw()` / `bcrypt.checkpw()`
- passlib 1.7.4 不兼容 bcrypt 5.0，参见上方问题 3

***

## 十、依赖

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
passlib[bcrypt]==1.7.4
python-dotenv==1.0.1
openai>=1.0.0
aiohttp==3.11.11
beautifulsoup4==4.12.3
python-multipart==0.0.19
chromadb>=0.5.0
httpx>=0.27,<0.28
lxml>=5.0
curl_cffi>=0.7
```

### 前端 (Node.js)

```
vue@3.4, vue-router@4.3, pinia@2.1, axios@1.6
echarts@6.1
@vitejs/plugin-vue@5, vite@5
sass@1.102, vite-plugin-pwa@0.17
```

***

## 十一、快速排查清单

| 现象                      | 检查                                                     |
| ----------------------- | ------------------------------------------------------ |
| 启动报 ModuleNotFoundError | `cd server && pip install -r requirements.txt`         |
| 数据库连接失败                 | MySQL 是否运行？端口是否 3307？`DATABASE_URL` 是否正确？              |
| API 返回 "Token 解析失败"     | `JWT_SECRET` 是否与服务端一致？Token 是否过期？                      |
| 前端页面空白                  | Node.js 是否安装？`cd client && npm install && npm run dev` |
| 食物搜索返回空                 | 种子数据是否已插入？检查 `GET /api/foods/categories` 返回数           |
| CORS 报错                 | `.env` 中 `CORS_ORIGINS` 是否包含前端地址？                      |
| AI 对话无响应                | DeepSeek API Key 是否有效？`.env` 中是否已填写？                   |

***

**最后更新：** 2026-07-24\
**项目路径：** `d:\Desktop\test\TreaWork\Food-Time\`\
**开发周期：** 3 个月（至 2026 年 10 月）

***

## 十二、开发迭代记录

> 以下为按时间顺序记录的开发迭代、设计决策、问题修复详情，供深入了解项目演进过程参考。

***

### 十二.1、2026-07-20 P0 阶段工作总结（第一轮交接）

#### 一、项目骨架搭建

**创建内容**：

* 完整项目目录结构（8 个后端功能模块 + 前端 8 个页面）

* 每个模块独立 `models.py` + `router.py`，互不干扰

* `__init__.py` 包结构清晰

#### 二、数据库模型设计

* 14 张表 SQLAlchemy 异步模型

* 统一 `Base` 声明基类 + `models.py` 统一导入入口

* `init_db.py` 独立建表逻辑（避免循环导入）

#### 三、用户认证系统

* bcrypt 密码哈希（直调 `bcrypt.hashpw`，不依赖 passlib）

* JWT 签发与验证（7 天过期）

* 邮箱验证码（开发模式打印控制台）

* 管理员账号自动初始化

* 路由守卫中间件（`get_current_user` / `get_admin_user`）

#### 四、种子数据

* 12 个食物分类 + 102 条中英文食物（含完整营养数据）

* 幂等插入（重复执行不重复写入）

* 启动时自动执行

#### 五、前端脚手架

* Vue 3 + Vite + 纯 CSS 桌面端组件

* **响应式双导航**：桌面端（≥768px）顶部导航栏；移动端汉堡菜单 + 侧边栏

* 路由守卫（未登录 → /login）

* Axios 拦截器（自动附加 JWT + 401 跳转）

* Vite proxy 代理 `/api` → 后端

#### 六、修复的 Bug

| # | 问题                             | 修复方式                                  |
| - | ------------------------------ | ------------------------------------- |
| 1 | `database.py` 循环导入             | 创建 `init_db.py` 独立文件，Base 定义与模型导入分离   |
| 2 | `aiomysql` `pool_pre_ping` 不支持 | 关闭 `pool_pre_ping`                    |
| 3 | passlib + bcrypt 5.0 不兼容       | 改用 `bcrypt` 直接调用                      |
| 4 | jose `sub` 字段必须为字符串            | encoding 用 `str()`，decoding 用 `int()` |

#### 七、文件改动清单

| 文件                        | 改动类型                                  |
| ------------------------- | ------------------------------------- |
| `server/src/main.py`         | **新增** — FastAPI 入口 + lifespan + 路由注册 |
| `server/src/config.py`       | **新增** — Pydantic Settings 配置管理       |
| `server/src/database.py`     | **新增** — 异步引擎 + 会话工厂 + Base           |
| `server/src/init_db.py`      | **新增** — 建表逻辑（解循环导入）                  |
| `server/src/dependencies.py` | **新增** — JWT 依赖注入                     |
| `server/src/models.py`       | **新增** — 模型统一导入                       |
| `server/src/seed.py`         | **新增** — 种子数据                         |
| `server/src/auth/*`          | **新增** — 完整认证模块                       |
| `server/src/food/*`          | **新增** — 食物库（搜索 + 分类）                 |
| `server/src/chat/*`          | **新增** — AI 对话（骨架）                    |
| `server/src/diet/*`          | **新增** — 饮食记录（骨架）                     |
| `server/src/expense/*`       | **新增** — 记账（骨架）                       |
| `server/src/custom_food/*`   | **新增** — 自定义食物（骨架）                    |
| `server/src/public_food/*`   | **新增** — 公共广场（骨架）                     |
| `server/src/admin/*`         | **新增** — 管理后台（骨架）                     |
| `server/src/services/*`      | **新增** — 外部服务（骨架）                     |
| `server/.env`             | **新增**                                |
| `server/.env.example`     | **新增**                                |
| `server/requirements.txt` | **新增**                                |
| `.gitignore`              | **新增**                                |
| `client/package.json`     | **新增**                                |
| `client/vite.config.js`   | **新增**                                |
| `client/index.html`       | **新增**                                |
| `client/src/*`            | **新增** — 全部前端代码                       |
| `docs/`                   | **新增** — 全部设计文档                       |

#### 八、验证结果

* ✅ `POST /api/auth/register` — 注册返回 JWT + User

* ✅ `POST /api/auth/login` — 登录返回 JWT + User

* ✅ 重复邮箱注册被正确拒绝

* ✅ `GET /api/foods` — 返回 102 条种子数据（十二.1）

* ✅ `GET /api/foods/categories` — 返回 12 个分类

* ✅ `GET /api/auth/me` — JWT 认证返回用户信息

* ✅ `GET /api/health` — 健康检查

#### 九、下次接手建议

1. 先检查 `.env` 中的 `DEEPSEEK_API_KEY` 和 `QWEN_API_KEY` 是否已填入有效值
2. 如果需要测试前端，先安装 Node.js，在 `client/` 目录执行 `npm install && npm run dev`
3. 全部测试通过后，推送到 GitHub：`https://github.com/zhan-zip/Food-Time`

***

### 十二.2、2026-07-20 T0 桌面端重构（全部推倒重来）

彻底移除 Vant UI，改为纯 CSS 桌面端组件 + 暖色调品牌设计。

**设计依据**：`界面设计初版方案.md`

**品牌更新**：

* 项目中文名定为「食光记」

* 简介：一款 AI 驱动的智能饮食助手，帮您解决「今天吃什么」的每一刻

* 暖色调色板：铜锣烧金 #D9A15B / 奶咖米 #D8B08C / 黑可可 #3A2418

**T0 架构改动**：

| 文件                | 改动                                                                         |
| ----------------- | -------------------------------------------------------------------------- |
| `main.js`         | 移除 Vant CSS import                                                         |
| `main.css`        | 完全重写：CSS 自定义变量暖色系色板 + 通用组件（按钮/卡片/输入框/标签）+ 3 档响应式                           |
| `App.vue`         | 完全重写：顶部 sticky navbar + 左侧滑动 sidebar + 汉堡菜单切换                              |
| `router/index.js` | 路由重构：5 个标签 → 12 个路由（6 主导航 + 登录/注册/管理/广场详情）                                 |
| `package.json`    | 移除 vant / @vant/use / unplugin-vue-components / @vant/auto-import-resolver |
| `vite.config.js`  | 移除 Vant 自动导入插件                                                             |
| `index.html`      | 标题改为「食光记」                                                                  |

**导航结构**：

| 路由            | 页面    | 说明                      |
| ------------- | ----- | ----------------------- |
| `/`           | 首页    | Banner 轮播 + 每日推荐 + 功能介绍 |
| `/today-eat`  | 今天吃什么 | 搜索/分类筛选/转盘/AI决策入口       |
| `/diy`        | 我的厨房  | 食材篮子 + 调料台 + AI 烹饪建议    |
| `/square`     | 美食广场  | 3 列卡片网格                 |
| `/square/:id` | 食谱详情  | 食材/步骤/营养数据/评论区          |
| `/expense`    | 记账    | 手动录入 + OCR 拍照 + 统计图     |
| `/assistant`  | AI 助手 | 聊天界面 + 快捷提问 + SSE 骨架    |
| `/about`      | 关于我   | 个人信息 + 饮食偏好 + 营养分析 + 退出 |
| `/admin`      | 管理后台  | 数据统计 + 用户管理 + 食谱审核      |

**删除的旧页面**：`Food.vue`、`Chat.vue`、`Profile.vue`

**响应式策略**：

* 桌面（>768px）：粘性顶栏 + 多列网格布局

* 移动（≤768px）：顶栏 + 汉堡菜单展开侧栏 + 单列布局

* 移动（≤640px）：全部单列

***

### 十二.3、2026-07-23 登录注册完善 & 邮件系统联调

#### 一、发现问题

1. **注册按钮卡住无响应**：前端 `Register.vue` 使用原生 `axios` 发请求到后端 `localhost:8000`，后端未启动时请求无超时配置导致无限等待
2. **前后端需手动分别启动**：开发体验差，不符合部署预期
3. **邮箱验证码仅打印控制台**：无法真正发送邮件，注册验证形同虚设
4. **登录/注册表单无校验提示**：用户输入错误格式的邮箱或密码没有即时反馈
5. **历史 Bug：登录密码从未被发送**：`auth.js` 的 `login(email, password)` 函数签名与调用不匹配

#### 二、功能实现

##### 2.1 真实 SMTP 邮件发送

**新增/修改文件**：

| 文件                          | 改动                                                                                                                           |
| --------------------------- | ---------------------------------------------------------------------------------------------------------------------------- |
| `server/src/services/email.py` | 完全重写：`EmailService` 类支持 SSL(465) 和 STARTTLS(587) 双模式；`send_verification_code()` 发送格式化 HTML 邮件；`is_configured` 自动检测 SMTP 是否就绪 |
| `server/src/auth/router.py`    | `send-code` 端点增加 SMTP 真实发送分支，内置降级机制（SMTP 未配置时打印到控制台）                                                                         |
| `server/.env.example`       | SMTP 配置模板更新为 QQ邮箱默认值 + 详细注释                                                                                                  |

**技术细节**：

* `smtplib` 是同步阻塞库，会使 FastAPI 异步事件循环卡死

* 修复方式：用 `asyncio.to_thread()` 将 SMTP 调用丢到线程池执行，避免阻塞主循环

##### 2.2 前端表单校验

**新增**：`Register.vue` 完全重写，`Login.vue` 同步升级

| 校验项 | 规则                                | 表现                                   |
| --- | --------------------------------- | ------------------------------------ |
| 昵称  | 非空 + ≥2 个字                        | 红色边框 + 字段下方红字提示                      |
| 邮箱  | 正则 `/^[^\s@]+@[^\s@]+\.[^\s@]+$/` | 红色边框 + "邮箱格式不正确，例如 <example@qq.com>" |
| 密码  | ≥6 位 + 需含字母或数字                    | 红色边框 + 对应提示                          |
| 验证码 | 非空                                | 红色边框                                 |

**新增 UI 元素**：

* 正确时：灰色小字提示（如"用于接收验证码和找回密码"）

* 验证码已发送：绿色小字 "验证码已发送到 xxx，请查收"

* 60 秒发送倒计时按钮，防止重复点击

##### 2.3 一键启动脚本

**新增**：`start.bat`（项目根目录）

* 双击打开两个新窗口分别启动前后端

* 自动等待 5 秒给数据库初始化

* 打印启动完成提示和访问地址

##### 2.4 Bug 修复

| Bug                          | 文件                       | 修复                                                         |
| ---------------------------- | ------------------------ | ---------------------------------------------------------- |
| `Register.vue` 用原生 axios 无超时 | `Register.vue`           | 改用 `request` 实例（30s 超时 + JWT 拦截器）                          |
| `Login.vue` 密码从未发送到后端        | `client/src/api/auth.js` | `login(email, password)` 改为独立参数，内部封装 `{ email, password }` |
| 后端未启动时注册无限等待                 | 启动后端 + 前端请求实例超时          | 组合修复                                                       |

##### 2.5 文档术语清理

| 文件                | 改动                                |
| ----------------- | --------------------------------- |
| 全部 5 个 MD 设计文档    | "app"/"App"/"应用" → "服务"/"网站"/"页面" |
| `server/src/main.py` | `"app"` key → `"service"` 描述      |

#### 三、验证结果

* ✅ SMTP 连接 `smtp.qq.com:587` 成功，邮件 3.4 秒内发送

* ✅ `POST /api/auth/send-code` — 返回 `{"message": "验证码已发送到您的邮箱"}`

* ✅ 退信 `test@test.com` 仅为排查 API 时的测试参数，非注册表单 Bug

* ✅ 登录/注册表单校验即时反馈，红框 + 小字提示

* ✅ `start.bat` 一键启动前后端正常

#### 四、文件改动清单

| 文件                              | 改动类型                                                |
| ------------------------------- | --------------------------------------------------- |
| `server/src/services/email.py`  | **重写** — smtplib 真实发送 + 降级机制                        |
| `server/src/auth/router.py`     | **修改** — send-code 增加 SMTP 分支 + `asyncio.to_thread` |
| `client/src/views/Register.vue` | **重写** — 完整表单校验 + request 实例 + 倒计时                  |
| `client/src/views/Login.vue`    | **重写** — 表单校验 + 结构对齐 Register                       |
| `client/src/api/auth.js`        | **修改** — login 函数签名修复                               |
| `start.bat`                     | **新增** — 一键启动脚本                                     |
| `server/.env.example`           | **修改** — SMTP 配置模板                                  |
| `server/.env`                   | **修改** — SMTP\_HOST 修正为 smtp.qq.com                 |
| `docs/*.md` 全部 5 个文档            | **修改** — "app" 术语替换                                 |

***

### 十二.4、2026-07-23 美食广场 + 食谱详情 + 评论区

#### 一、实现内容

在 P1 阶段开始前，提前补全了美食广场的三个核心页面，从纯静态占位升级为完整功能。

#### 二、后端

##### 2.1 新增 Comment 模型

```python
# server/src/public_food/models.py
class Comment(Base):
    __tablename__ = "recipe_comments"
    id, recipe_id, user_id, content, created_at
```

##### 2.2 Food 模型增加 description 字段

`server/src/food/models.py`：新增 `description = Column(Text, nullable=True)`

##### 2.3 6 个新 API 端点

| 端点                                  | 方法     | 说明                    |
| ----------------------------------- | ------ | --------------------- |
| `/api/public/recipes`               | GET    | 食谱列表（分页 + 作者 + 点赞收藏数） |
| `/api/public/recipes/{id}`          | GET    | 食谱详情（食材/调料/步骤/营养/评论数） |
| `/api/public/recipes/{id}/comments` | GET    | 评论列表（含用户昵称）           |
| `/api/public/recipes/{id}/comment`  | POST   | 发表评论（需登录）             |
| `/api/public/recipes/{id}/save`     | POST   | 收藏到我的食物库（需登录）         |
| `/api/public/recipes/{id}/save`     | DELETE | 取消收藏（需登录）             |

##### 2.4 4 个种子食谱

| 食谱        | 菜系 | 食材数     | 步骤数 |
| --------- | -- | ------- | --- |
| 番茄炒蛋      | 川菜 | 2食材+3调料 | 5步  |
| 宫保鸡丁（家常版） | 川菜 | 4食材+7调料 | 8步  |
| 日式味噌汤     | 日料 | 3食材+2调料 | 6步  |
| 黑椒牛排      | 西餐 | 3食材+5调料 | 7步  |

#### 三、前端

##### 3.1 Square.vue（美食广场列表）

* 移除 `v-for="n in 6"` 静态占位

* 接入 `GET /api/public/recipes` 真实数据

* 卡片悬停上浮动效 (`transform: translateY(-2px)`)

* 空状态提示：暂无食谱时显示"还没有人分享食谱"

##### 3.2 SquareDetail.vue（食谱详情）

完全重写，包含以下功能区块：

| 区块            | 实现方式                        |
| ------------- | --------------------------- |
| 食物名 + 作者 + 日期 | `h1` + meta 信息行             |
| 菜系/难度标签       | `tag tag-primary` + 自定义中文映射 |
| 食物简介          | 段落文本，行高 1.8                 |
| 食材列表          | 金色背景标签，显示名称+分量              |
| 调料列表          | 绿色背景标签                      |
| 做法步骤          | `<ol>` 有序列表，1.7 行高          |
| 营养成分卡片        | 左侧 sticky 侧边栏，2x2 网格        |
| 添加到我的食物库      | 大按钮，收藏/取消收藏切换               |
| 评论区           | 发表框 + 评论列表，需登录              |
| 404 处理        | 食谱不存在时显示错误页 + 返回按钮          |

#### 四、修复的 Bug

| Bug                            | 修复                                                            |
| ------------------------------ | ------------------------------------------------------------- |
| `/api/api/public/recipes` 双前缀  | `public.js` 路径去掉 `/api` 前缀（`request.js` 已设 `baseURL: '/api'`） |
| `res.data.items` 取不到数据         | axios 拦截器已返回 `response.data`，改为直接 `res.items`                 |
| `e.response?.data?.detail` 取不到 | 拦截器已转 `Error(message)`，改为 `e.message`                         |

#### 五、文件改动

| 文件                                  | 类型 | 说明               |
| ----------------------------------- | -- | ---------------- |
| `server/src/public_food/models.py`  | 修改 | 新增 Comment 模型    |
| `server/src/public_food/router.py`  | 重写 | 6 个 API 端点       |
| `server/src/food/models.py`         | 修改 | 新增 description 列 |
| `server/src/models.py`              | 修改 | 注册 Comment       |
| `server/src/seed.py`                | 修改 | 新增 4 个种子食谱       |
| `client/src/api/public.js`          | 新增 | 广场 API 封装        |
| `client/src/views/Square.vue`       | 重写 | 接入真实数据           |
| `client/src/views/SquareDetail.vue` | 重写 | 完整详情页            |

#### 六、验证

* ✅ `GET /api/public/recipes` — 返回 4 个食谱、正确分页

* ✅ `GET /api/public/recipes/1` — 返回番茄炒蛋，含 2食材+3调料+5步骤

* ✅ 前端广场页加载 4 张卡片，点击跳转详情页

* ✅ 详情页展示完整信息，评论区未登录时提示登录

***

### 十二.5、2026-07-23 记账分类聚焦 + OCR 修复 + Vite 别名修复

#### 一、问题发现

1. **记账分类扩散**：原有 5 个分类（餐饮/购物/交通/娱乐/其他）是通用记账模式，偏离"食光记"聚焦饮食的定位
2. **OCR 始终失败**：Qwen VL 调用从不成功，前端一直显示"识别中..."然后"识别失败"
3. **前端页面报错**：点击"今天吃什么""关于我"等页面出现黑底错误框

#### 二、问题根源

| 问题     | 根因                                                                                                   | 影响范围                              |
| ------ | ---------------------------------------------------------------------------------------------------- | --------------------------------- |
| 记账分类扩散 | 设计时未限制为饮食分类                                                                                          | `expense/router.py`、`Expense.vue` |
| OCR 失败 | `qwen.py` 使用了 `response_format={"type": "json_object"}`，DashScope 兼容模式不支持该参数 → API 报错被 `except` 静默吞掉 | `qwen.py`、`expense/router.py`     |
| 前端黑框   | `vite.config.js` 缺少 `@` 别名配置，`About.vue`、`TodayEat.vue`、`Expense.vue` 中 `import from '@/api/*'` 解析失败 | `vite.config.js`                  |

#### 三、修复方案

##### 3.1 分类聚焦饮食

| 文件                  | 旧值                                            | 新值                                                        |
| ------------------- | --------------------------------------------- | --------------------------------------------------------- |
| `expense/router.py` | `food/shopping/transport/entertainment/other` | `food(餐饮)/delivery(外卖)/snack(零食)/drink(饮品)/grocery(食材采购)` |
| `Expense.vue`       | 同上                                            | 同上                                                        |

所有 5 个分类均聚焦饮食消费，去除了购物/交通/娱乐等无关分类。

##### 3.2 OCR 修复（第二轮）

| 文件                         | 改动                                                                                |
| -------------------------- | --------------------------------------------------------------------------------- |
| `qwen.py`                  | `parse_receipt()` 去掉 `response_format` 参数（DashScope 不支持）；返回值改为 `(dict, error)` 元组 |
| `expense/router.py` OCR 端点 | `image_base64` 兼容带/不带 `data:` 前缀；错误信息透明化                                          |

→ **仍失败**：沙箱终端无法访问 `dashscope.aliyuncs.com`（即使开梯子，终端网卡与浏览器不同）

##### 3.3 OCR 修复（第三轮 — 后端代理 + 前端直连方案尝试）

**根因**：后端 Python 运行在沙箱终端，网卡环境与用户浏览器不同，无法直连 DashScope API。

**尝试方案**：曾参考 `D:\Desktop\网站\食物\index.html` 的做法，尝试将 OCR 改为前端浏览器直接调用 Qwen VL API，识别成功后再通过后端保存。但此方案会将 API Key 暴露在前端，存在安全隐患。

**最终方案（第四轮 — 后端代理）**：保留后端代理方案，通过 Vite proxy 转发 `/api` → 后端 8000，前端上传图片 base64 → `POST /api/expense/ocr` → 后端调用 Qwen VL（API Key 仅存 server/.env）→ 返回识别结果。API Key 始终不暴露给前端。

| 文件            | 改动                                                                                               |
| ------------- | ------------------------------------------------------------------------------------------------ |
| `Expense.vue` | OCR handler：`FileReader` → `POST /api/expense/ocr`（通过 request.js 实例，走 Vite proxy → 后端代理 Qwen VL） |

流程变更：`前端 → POST /api/expense/ocr → 后端代理 Qwen VL → 返回结果`

##### 3.4 OCR 优化 — 填入表单而非自动保存

| 文件                        | 改动                                                                 |
| ------------------------- | ------------------------------------------------------------------ |
| `Expense.vue` 模板          | "手动录入"→"输入账单"，"拍照识别"→"识别账单截图"，提示文案同步更新                             |
| `Expense.vue` OCR handler | 识别成功后填入 `form.amount/category/description`，提示用户核对后点击"记录"保存（替代自动保存） |

用户体验：上传截图 → AI 识别 → 金额/分类/备注自动填入表单 → 用户可修改 → 手动点"记录"确认。

##### 3.5 Vite 别名

| 文件               | 改动                                      |
| ---------------- | --------------------------------------- |
| `vite.config.js` | 新增 `resolve.alias: { '@': './src' }` 配置 |

#### 四、文件改动清单

| 文件                             | 类型 | 说明                                          |
| ------------------------------ | -- | ------------------------------------------- |
| `server/src/expense/router.py` | 修改 | CATEGORY\_NAMES 改为饮食分类 + OCR 错误透明化          |
| `server/src/services/qwen.py`  | 修改 | parse\_receipt 去掉 response\_format + 返回错误详情 |
| `client/vite.config.js`        | 修改 | 新增 @ 路径别名                                   |
| `client/src/views/Expense.vue` | 修改 | 分类改为饮食聚焦                                    |
| `docs/项目实施计划.md`               | 修改 | P1-4 标注分类聚焦饮食                               |

***

### 十二.6、2026-07-23 OCR 记账交互优化 + Vite 代理

#### 一、优化内容

1. **OCR 识别结果填入表单**：识别成功后自动填入金额/分类/备注到上方表单，用户可修改后手动点击"记录"保存（替代之前识别后自动保存的流程）
2. **前端文案优化**："手动录入"→"输入账单"，"拍照识图"→"识别账单截图"，提示文案同步更新
3. **CORS 由 Vite proxy 统一处理**：前端所有 `/api` 请求通过 Vite proxy 转发到 `localhost:8000`，OCR 请求 `POST /api/expense/ocr` 走同一代理链路，无需额外 `/qwen` 代理规则。API Key 仅在服务端 `.env` 中，不暴露给前端。

#### 二、文件改动

| 文件                             | 类型 | 说明                                     |
| ------------------------------ | -- | -------------------------------------- |
| `client/src/views/Expense.vue` | 修改 | 卡片标题改为"输入账单"/"识别账单截图"，OCR 结果填入表单而非自动保存 |

***

### 十二.7、2026-07-23 P1-2 食物库爬虫（下厨房）

#### 一、实现内容

1. **营养参考数据库**：`nutrition_ref.py` — 213种食材的中国食物成分表营养数据（热量/蛋白质/脂肪/碳水/纤维/钠）
2. **下厨房爬虫**：`scraper.py` — 爬取热门 + 分类页面菜谱数据，匹配食材估算营养
3. **数据导入脚本**：`import_scraped.py` — 将爬取数据转换为 Food 模型保存到数据库

#### 二、技术细节

* 食材→营养匹配：通过 `INGREDIENT_ALIAS` 字典将菜谱食材别名映射到 `NUTRITION_REF` 标准名称

* 营养估算：取所有匹配食材的营养数据，按加权平均计算整道菜的营养成分

* 分类映射：通过 `_get_category_ids()` 从页面提取分类名→数字ID映射

#### 三、当前结果

* 成功爬取并导入 **197 条**菜谱数据

* 食物库总量：303 条（种子102 + 食谱4 + 爬取197）

* **问题**：目标网站下厨房启用了限流（429），大规模爬取中断

#### 四、文件改动

| 文件                                     | 类型 | 说明             |
| -------------------------------------- | -- | -------------- |
| `server/src/services/nutrition_ref.py` | 新增 | 213种食材营养参考数据   |
| `server/src/services/scraper.py`       | 新增 | 下厨房爬虫（热门+分类爬取） |
| `server/import_scraped.py`             | 新增 | 爬取数据导入脚本       |

***

### 十二.8、2026-07-24 P1-2 美食天下爬虫 + P1-1 快捷决策

#### 一、P1-2 美食天下爬虫

**问题**：下厨房限流(429)，需换网站继续扩充数据。

**方案**：改用美食天下(home.meishichina.com)，使用 `curl_cffi` 模拟 Chrome 浏览器绕过 Cloudflare 防护。

**技术实现**：

| 项目   | 说明                                                    |
| ---- | ----------------------------------------------------- |
| 反爬方案 | curl\_cffi + impersonate="chrome120" 成功返回200          |
| 解析方式 | BeautifulSoup 定位 `div.detail` → `h2 > a`(菜名) + 原料正则提取 |
| 数据来源 | 综合列表50页(482条) + 15个分类页补充                              |
| 营养估算 | 复用 NUTRITION\_REF + INGREDIENT\_ALIAS 食材匹配            |

**结果**：

* 爬取558条，去重导入**545条**新食谱

* 数据库总计：**848条**（种子102 + 食谱4 + 下厨房197 + 美食天下545）

* 超额完成500条目标（达成153%）

#### 二、P1-1 FR-30 快捷食物决策

**实现**：Assistant.vue 新增时间感知快捷决策面板。

| 功能   | 说明                             |
| ---- | ------------------------------ |
| 时间感知 | 早晨→早餐推荐，午间→午餐推荐，下午→下午茶，晚间→晚餐推荐 |
| 常驻按钮 | 低热量推荐、快手菜推荐、营养分析               |
| 重新决策 | 对话后可点击"🎯决策"按钮重新唤出快捷面板         |
| 触发方式 | 点击快捷按钮后自动填入消息并发送到AI            |

#### 三、文件改动

| 文件                                      | 类型 | 说明                       |
| --------------------------------------- | -- | ------------------------ |
| `server/src/services/scraper_meishi.py` | 新增 | 美食天下爬虫（curl\_cffi反爬）     |
| `server/import_meishi.py`               | 新增 | 美食天下数据导入脚本               |
| `client/src/views/Assistant.vue`        | 修改 | 时间感知快捷决策面板               |
| `server/requirements.txt`               | 修改 | 新增 curl\_cffi、lxml、httpx |
| `docs/项目实施计划.md`                        | 修改 | P1-2 + P1-1 FR-30 标记完成   |
| `docs/food-time-project-summary.md`     | 修改 | 新增十九节                    |

***

### 十二.9、2026-07-24 项目交接（P1 完成，进入 P2）

#### 一、当前状态总览

**版本**：v0.2（P1 完成）\
**日期**：2026-07-24\
**GitHub**：<https://github.com/zhan-zip/Food-Time>

| 维度    | 数据                                                                      |
| ----- | ----------------------------------------------------------------------- |
| 后端模块  | 8 个（auth/food/chat/diet/expense/custom\_food/public\_food/admin）全部已注册路由 |
| 前端页面  | 12 个路由，其中 10 个完整实现，1 个占位(DIY)                                           |
| 食物库   | 766 条（种子24 + 下厨房197 + 美食天下545），附 213种食材营养数据                             |
| AI 功能 | SSE 流式 + 10 个 Tool Calling + RAG(ChromaDB) + 多模态图片分析                    |
| 数据库   | MySQL 8.0, 14 张表（含 recipe\_comments），utf8mb4                            |

#### 二、P2 进度（2026-07-24）

详见 `docs/项目实施计划.md`。

| 编号   | 内容                                    | 状态           |
| ---- | ------------------------------------- | ------------ |
| P2-1 | DIY 烹饪：[详见十二.10](#十二10-p2-1-diy-烹饪核心设计方案) | ✅ 已完成        |
| P2-1 | 烹饪动画增强：火焰/蒸汽/热风粒子特效                   | ✅ 已完成        |
| P2-2 | 广场排序（热度/时间 + 正序/逆序切换）+ 菜系筛选 + 管理员审核   | ✅ 已完成        |
| P2-3 | 食物决策辅助：属性筛选 + 随机转盘(CSS动画) + AI推荐      | 待完成          |
| P2   | 保存菜谱烹饪方式可选 + 提交广场入口完善 + 管理员登录安全加固     | ✅ 已完成（见十二.12） |
| P3   | PWA 离线缓存 + 赛事文档 + 全面美化                | —            |

#### 三、新增需求记录（未实现）

来源：[新增需求记录.md](file:///d:/Desktop/test/TreaWork/Food-Time/新增需求记录.md)

| 需求                  | 状态    | 说明                |
| ------------------- | ----- | ----------------- |
| 新用户引导步骤（圈出功能+压暗+说明） | ❌ 未开始 | 需前端 Onboarding 组件 |
| 色盲友好设计              | ❌ 未开始 | 后期 UI 调整时统一处理     |

#### 四、关键决策记录

| 决策                   | 原因                                                             |
| -------------------- | -------------------------------------------------------------- |
| OCR 通过后端代理调用 Qwen VL | 前端上传图片 → 后端 `/api/expense/ocr` 解析 → 返回结果填入表单，API Key 仅存 `.env` |
| 记账分类仅饮食              | 聚焦"食光记"定位：餐饮/外卖/零食/饮品/食材采购                                     |
| curl\_cffi 替代 httpx  | 美食天下使用 Cloudflare 防护，httpx 返回 403                              |
| ChromaDB 本地向量存储      | 无需外部向量数据库，启动时自动构建食物库索引                                         |
| 营养数据标注来源             | 所有估算数据 tag 中注明"中国食物成分表（第六版）- 基于食材加权估算"                         |
| 不做英文食谱爬取             | 中文数据已达 766 条，远超 500 条目标                                        |

#### 五、营养数据来源说明

> 所有食物营养数据的计算**不是 LLM 直接生成**，而是基于权威参考数据的科学加权估算。

##### 数据源

| 数据源    | 名称                    | 发布机构             | 说明                                              |
| ------ | --------------------- | ---------------- | ----------------------------------------------- |
| 核心参考数据 | **中国食物成分表（第六版）**      | 中国疾病预防控制中心营养与健康所 | 国家级营养学标准，基于实验室检测数据，收录 2000+ 种食材                 |
| 实现文件   | `nutrition_ref.py`    | —                | 从中精选 213 种常见烹饪食材，字段：热量/蛋白质/脂肪/碳水/纤维/钠（每100g可食部） |
| 等同国际标准 | USDA FoodData Central | 美国农业部            | 同类型的国家食物成分数据库                                   |

##### 计算方法（非 LLM）

```
菜谱食材（如"番茄炒蛋"）
  → INGREDIENT_ALIAS 映射到标准名称（"鸡蛋"→"鸡蛋（白壳）"）
    → 查 NUTRITION_REF 字典获取每100g营养值
      → 所有主料加权平均 = 最终营养数据
```

**不依赖 LLM 判断**，纯基于公式计算。LLM 仅用于 Cooking 建议（步骤/火候），营养部分始终标注来源。

##### 置信度说明

* 所有估算数据 tags 中标明 `"营养数据来源": "中国食物成分表（第六版）- 基于食材加权估算"`

* 未来可选标注置信度等级：精确匹配（>90%）/ 近似匹配（70-90%）/ 推断（<70%）

#### 六、已知注意事项

1. **MySQL 端口**：本机 3307（非默认 3306），`.env` 需正确配置
2. **API Key**：需有效的 DeepSeek + Qwen VL API Key
3. **邮件**：`.env` 中 SMTP 未配置时，验证码降级打印控制台
4. **ChromaDB**：启动时构建向量索引，首次启动需等待 Embedding API 调用

#### 七、测试验证方法

1. **食物库**：`GET /api/foods?keyword=番茄` → 应返回多条结果
2. **AI 对话**：浏览器打开 `/assistant`，点击快捷决策按钮 → AI 应流式回复
3. **OCR 记账**：打开 `/expense`，上传截图 → 识别结果应填入表单
4. **饮食记录**：`/today-eat` 搜索食物 → 点击"我吃了这个" → 弹出确认
5. **Swagger**：`http://localhost:8000/docs` 查看全部 API

***

### 十二.10、P2-1 DIY 烹饪——核心设计方案

> 2026-07-24 讨论确定：方案 C「双开门冰箱 + 岛台」设计。

#### 一、设计理念

模拟真实厨房体验——用户打开冰箱选取食材 → 放到岛台备菜盘 → AI 给出烹饪建议 → 选择烹饪方式 → 烹饪动画 → 保存/分享。

#### 二、页面布局

```
┌─────────────────────────────────────────────────────────┐
│                    我的厨房                               │
├────────────────────────┬────────────────────────────────┤
│                        │   📋 已选食材（备菜盘）           │
│  🧊 双开门冰箱          │   [🥩猪肉] [🍅番茄] [🧅洋葱] ... │
│  ┌────────┬─────────┐  │   [🧂盐] [🧄蒜]               │
│  │ 🥩 肉类 │ 🥬 蔬菜  │  │                                │
│  │ 猪肉    │ 番茄     │  │       🍳 烹饪岛台              │
│  │ 牛肉    │ 青椒     │  │  ┌─────────────────┐         │
│  │ 鸡肉    │ 土豆     │  │  │   🍽️ 备菜盘     │         │
│  │ 排骨    │ 白菜     │  │  │                 │         │
│  │ 五花肉  │ 胡萝卜   │  │  └─────────────────┘         │
│  │ ...     │ ...     │  │                                │
│  ├─────────┴─────────┤  │   [🤖 获取 AI 烹饪建议]        │
│  │ 🦐 海鲜 │ 🧈 豆制品│  │                                │
│  │ 虾仁    │ 豆腐     │  │   [清空] [开始烹饪]            │
│  │ ...     │ ...     │  │                                │
│  └───────────────────┘  │                                │
│                         │                                │
│ 🧂 调料台（始终可见）     │                                │
│ [盐] [酱油] [醋] [糖] ... │                                │
├────────────────────────┴────────────────────────────────┤
│              🤖 AI 烹饪建议 / 匹配结果面板                  │
└─────────────────────────────────────────────────────────┘
```

#### 三、交互流程（5 步）

| 步骤         | 用户操作                  | 系统响应                                                                   |
| ---------- | --------------------- | ---------------------------------------------------------------------- |
| ① 开冰箱选食材   | 点击关闭的冰箱 → 冰箱 CSS 双门打开 | 食材分区展示，分类色条一眼区分                                                        |
| ② 放入备菜盘    | 点击食材卡 / 调料            | 卡片飞入岛台圆盘，可点击移除                                                         |
| ③ 获取 AI 建议 | 点击「获取 AI 烹饪建议」        | ① 先匹配数据库已有菜谱（食材集合匹配）→ 若有则显示已有菜谱；② 若无匹配，DeepSeek 基于科学依据生成烹饪建议（步骤/火候/时间） |
| ④ 选择烹饪方式   | 在炒锅/空气炸锅/蒸锅中选一种       | 对应动画播放（火焰+翻炒 / 热风+倒计时 / 蒸汽升腾）                                          |
| ⑤ 保存/分享    | 填写菜名+简介 → 确认          | 写入 custom\_recipes + foods(source='custom')，可选发布到广场                    |

#### 四、视觉组件规格

##### 冰箱

| 属性   | 规格                                                                  |
| ---- | ------------------------------------------------------------------- |
| 初始状态 | 双门闭合，显示"🧊 点击打开冰箱"提示文字                                              |
| 开门动画 | CSS `perspective` + `rotateY`，左门向左旋、右门向右旋，duration 0.5s ease-in-out |
| 关闭   | 点击冰箱外部区域 / 再次点击冰箱 → 反向动画合上                                          |
| 左门内容 | 🥩 肉类 + 🦐 海鲜，`overflow-y: auto` 可上下滚动                              |
| 右门内容 | 🥬 蔬菜 + 🧈 豆制品 + 🥚 蛋奶，`overflow-y: auto`                           |
| 门底部  | 🦐 海鲜 + 🧈 豆制品（左右各一小区）                                              |

##### 食材卡

| 属性         | 规格                                                           |
| ---------- | ------------------------------------------------------------ |
| 尺寸         | 约 64×72px 卡片                                                 |
| 内容         | emoji（大号 24px）+ 中文名（12px）+ 底部分类色条（4px）                       |
| 色条         | 肉类#e74c3c、海鲜#3498db、蔬菜#27ae60、豆制品#f39c12、蛋奶#f1c40f、调料#95a5a6 |
| 无 emoji 处理 | 显示纯文字卡片，保留分类色条                                               |
| 选中态        | `transform: scale(1.1)` + `box-shadow` 加深                    |

##### 备菜盘

| 属性   | 规格                           |
| ---- | ---------------------------- |
| 形态   | 岛台中央大圆盘（直径约 200px），食材围绕排列    |
| 飞入动画 | 点击食材卡 → 卡片沿贝塞尔曲线缩小飞入圆盘（0.4s） |
| 移除   | 圆盘内点击食材 → 卡片消失 + 飞回原处动画（可选）  |
| 上限   | 建议 10 种以内，超出提示"食材太多了"        |

##### 调料台

| 属性 | 规格                                          |
| -- | ------------------------------------------- |
| 位置 | 冰箱下方 / 页面底部，始终可见                            |
| 布局 | 横滚 `flex` 容器，`overflow-x: auto`             |
| 内容 | 常用调料（盐/酱油/醋/料酒/糖/蒜/姜/辣椒/花椒/蚝油/胡椒粉/淀粉），来自数据库 |

##### 烹饪动画（仅步骤④触发）

| 烹饪方式    | 动画效果                                              |
| ------- | ------------------------------------------------- |
| 🍳 炒锅   | 锅底多层色块火焰跳动（`@keyframes flameDance`，不同延迟）+ 锅中食材微位移 |
| 🔥 空气炸锅 | 橙色热风波纹 + 倒计时数字 + 食材颜色渐变                           |
| ♨️ 蒸锅   | 白色蒸汽粒子从锅口升腾消散（`@keyframes steamRise`）             |

#### 五、AI 烹饪建议逻辑

```
用户已选食材集合 {猪肉, 番茄, 青椒, 盐, 酱油}
  → ① 数据库匹配：foods 表搜索 name/ingredients 与集合交集≥2 的菜谱
    → 有结果：展示"已找到 X 道相似菜谱"，显示菜名+封面→用户可选直接保存
    → 无结果：调用 DeepSeek
  → ② DeepSeek 生成：
      Prompt: "根据以下食材给出科学烹饪建议：
        主料{猪肉、番茄、青椒}，调料{盐、酱油}
        输出格式：菜名|烹饪方式|步骤|预估热量|烹饪时间"
      → 展示建议面板（步骤/热量/时间）
  → ③ 用户确认 → 进入烹饪方式选择 → 动画 → 保存
```

#### 六、数据模型（后端已有，需补路由）

```python
# custom_recipes 表
custom_recipe:
  id, name, description, cover_image
  ingredients: JSON [{name, amount, unit}]
  steps: JSON [order, text, duration]
  cooking_method: str  # "wok"/"air_fryer"/"steamer"
  author_id, is_published, created_at

# 保存时同步写入 foods 表（source='custom'）
food:
  name, category_id(默认"自定义"), calories_per_100g(估算)
  tags: {"来源":"DIY", "食材":[...], "烹饪方式":"..."}
  source: "custom"
```

#### 七、食材数据来源

食材列表（冰箱+调料台）从 `foods` 表按分类动态拉取，确保和食物库数据一致。emoji 通过映射表匹配：

```python
INGREDIENT_EMOJI = {
    "猪肉": "🥩", "牛肉": "🥩", "羊肉": "🥩", "鸡肉": "🍗",
    "排骨": "🦴", "番茄": "🍅", "土豆": "🥔", "青椒": "🫑",
    "豆腐": "🧈", "鸡蛋": "🥚", "虾仁": "🦐", "鱼": "🐟",
    "盐": "🧂", "酱油": "🫗", "醋": "🫗", "糖": "🍬",
    # ... 无匹配时使用文字卡片
}
```

#### 八、用户引导节点

| 时机        | 提示内容                           | 形式       |
| --------- | ------------------------------ | -------- |
| 首次进入页面    | "欢迎来到我的厨房！点击冰箱开始选择食材吧"         | 顶部气泡提示   |
| 冰箱关闭时     | "🧊 点击打开冰箱"                    | 冰箱门上文字   |
| 已有食材但未点建议 | "已选 X 种食材，点击「获取 AI 建议」看看能做什么菜" | 备菜盘旁提示   |
| 烹饪动画播放完   | "看起来不错！要保存这道菜吗？"               | 底部 Toast |
| 保存成功      | 提供"去广场看看"跳转链接                  | 确认弹窗     |

***

### 十二.11、P2-1 DIY 厨房 —— 调试经验与问题修复记录

> 记录开发过程中遇到的技术难点、根因分析和修复方案，供后续迭代参考。

#### 问题 1：冰箱打开后立即自动关闭

**现象**：点击冰箱后，冰箱闪烁打开又立刻合上。

**根因分析**：

* 冰箱关闭逻辑使用 `document.addEventListener('click', onClickOutside)` 监听外部点击

* Vue 在点击事件处理后触发重渲染，替换了 DOM 节点（冰箱从关闭态 `<div v-if="!open">` 切换到打开态 `<div v-else>`）

* 同一个 click 事件冒泡到 document 时，`fridgeOuter.value.contains(e.target)` 返回 `false`——因为原 DOM 节点已被 Vue 销毁替换

* 导致 `onClickOutside` 误判为"外部点击"，执行 `emit('close')`

**修复方案**：
改用 `pointerdown` 事件替代 `click`。`pointerdown` 在 Vue 重渲染之前触发，此时原 DOM 节点仍然存在，`contains()` 检测正确。参考代码：

```js
// FridgeSection.vue
onMounted(() => {
  document.addEventListener('pointerdown', onClickOutside)
})
```

#### 问题 2：食材加入备菜盘无弹入动画

**现象**：点击食材卡后盘中直接出现卡片，没有任何动画效果。

**根因分析（两层）**：

**第一层**：`<transition-group>` 默认渲染为 `<span>` 标签，破坏了备菜盘内 `display: flex` 的布局。且被 `v-if/v-else` 包裹时，Vue 的 `<transition-group>` 初次渲染不会触发 enter 动画。

**第二层**：Pinia store 中 `addToPlate` 使用 `plate.value.push()`，虽然数组内容变了，但 `.value` 引用地址不变。子组件 `props.items`（即 `store.plate`）接收的是同一个引用，Vue 的 prop 浅比较判断"未变化"，`watch` 不触发。

**修复方案**：
放弃 `<transition-group>`，改为手动监听 + CSS class 触发动画：

```js
// PlateSection.vue
let lastLength = 0
watch(() => props.items.length, (newLen) => {
  if (newLen > lastLength) {
    for (let i = lastLength; i < newLen; i++) {
      props.items[i]._animating = true          // 标记动画
      setTimeout(() => { props.items[i]._animating = false }, 500)
    }
  }
  lastLength = newLen
})
```

```html
<!-- 模板中动态绑定动画 class -->
<button :class="{ 'fly-in': item._animating }" ...>
```

```css
/* 弹入动画关键帧：弹性多阶段 */
@keyframes plateFlyIn {
  0%   { transform: translateY(-40px) scale(0.3); opacity: 0; }
  50%  { transform: translateY(8px) scale(1.08); opacity: 1; }
  70%  { transform: translateY(-4px) scale(0.94); }
  100% { transform: translateY(0) scale(1); opacity: 1; }
}
```

#### 问题 3：`[object Object]` 错误提示

**现象**：API 调用失败时，页面上显示 `[object Object]` 而不是可读的错误信息。

**根因分析**：

* 后端返回的错误信息是对象（例如 `{msg: "xxx"}`）

* Axios 拦截器中 `new Error(error)` 将对象原样传入，`Error.message` 期望字符串

* Vue 模板渲染 `{{ error }}` 时调用 `.toString()`，对象显示为 `[object Object]`

**修复方案**：
在 Axios 响应拦截器中对错误信息做序列化处理：

```js
// request.js 响应拦截器 error 分支
let message = error?.response?.data?.detail || error?.message || '请求失败'
if (Array.isArray(message)) message = message.join('; ')
if (typeof message === 'object') message = message.msg || message.message || JSON.stringify(message)
return Promise.reject(new Error(message))
```

#### 问题 4：调料台点击无飞行卡片

**现象**：冰箱食材点击后飞行卡片正常出现，但调料台点击后只有备菜盘弹入，飞行卡片不出现。

**根因分析**：

* 当时调料台的 `@select` 事件处理直接调用 `store.addToPlate()`，没有经过 `onIngredientSelect()` 函数

* `onIngredientSelect` 是统一处理飞行卡片创建 + 延迟加入备菜盘的入口函数

* 冰箱通过此函数 → 有飞行卡片；调料台绕过此函数 → 无飞行卡片

**修复方案**：
统一调料台和冰箱的事件处理链路：

```html
<!-- DIY.vue -->
<SeasoningRack @select="(item, catKey, type, e) => onIngredientSelect(item, type, e)" />
```

同时修改 `SeasoningRack.vue` 和 `IngredientCard.vue` 的事件传递，确保原生 DOM 事件对象能逐层传递到 `onIngredientSelect`：

```html
<!-- IngredientCard.vue -->
<button @click="$emit('click', $event)">

<!-- SeasoningRack.vue -->
<IngredientCard @click="onSelect(item, 'seasoning', $event)" />
```

```js
// SeasoningRack.vue
function onSelect(item, type, e) {
  emit('select', item, type, type, e)  // 传递原生事件 e
}
```

#### 问题 5：飞入动画效果生硬 → 弧线飞行优化

**现象**：初版飞行动画使用 CSS `transition` 做匀速直线运动，视觉效果呆板。

**优化方案**：
从 CSS `transition` 改为 JavaScript `requestAnimationFrame` 逐帧动画，实现四阶段效果：

| 阶段   | 时间(ms)  | 实现方式                                     |
| ---- | ------- | ---------------------------------------- |
| 拾取放大 | 0-50    | `scale: 1 → 1.12`                        |
| 弧线飞行 | 50-420  | 缓出三次方插值 + `Math.sin(π·progress)` 正弦弧线偏移  |
| 弹跳到达 | 420-620 | `cubic-bezier(0.34, 1.56, 0.64, 1)` 弹性缩放 |
| 淡出消失 | 620-870 | `opacity: 1 → 0` + `scale: 0.8 → 0.4`    |

关键代码片段：

```js
// 弧线偏移：正弦曲线，飞行中间点最高
const arcY = -Math.sin(raw * Math.PI) * ARC_HEIGHT

// 缓出三次方，确保尾部减速
const ease = 1 - Math.pow(1 - raw, 3)

// 当前坐标
const cx = sx + (tx - sx) * ease
const cy = sy + (ty - sy) * ease + arcY

card.style.transform = `translate(${cx}px, ${cy}px) translate(-50%, -50%) scale(${scale})`
```

**时序配合**：

```
0ms     → 点击食材卡 → 飞行卡片出现，开始弧线飞行
350ms   → store.addToPlate → 备菜盘卡片开始弹入(450ms)
420ms   → 飞行卡片到达 → 弹跳淡出(450ms)
870ms   → 飞行卡片完全移除
```

#### 技术要点总结

| 要点      | 说明                                                             |
| ------- | -------------------------------------------------------------- |
| 冰箱关闭检测  | 使用 `pointerdown` 而非 `click`，避免 Vue 重渲染导致的 DOM 引用失效             |
| 动画触发机制  | 放弃 `<transition-group>`，改用 `watch` + CSS class 手动控制，更灵活可控      |
| 跨组件事件传递 | 逐层传递原生 `$event` 对象，使飞行卡片能准确获取源元素 `getBoundingClientRect()`     |
| 复杂动画实现  | CSS transition 适合简单过渡，JS `requestAnimationFrame` 适合多阶段、非线性轨迹   |
| 时序协调    | 飞行(420ms) / 弹入(450ms) / 弹跳(450ms) 三段时间配合，通过 `setTimeout` 控制触发点 |
| 错误信息处理  | 始终在边界层（axios 拦截器）对错误做类型序列化，确保下游拿到的是字符串                         |

***

### 十二.12、2026-07-24 P2 Bug 修复与功能完善

#### 一、修复清单

| #  | 问题             | 根因                                                                                                            | 修复方案                                                                               |
| -- | -------------- | ------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------- |
| 1  | 保存菜谱时烹饪方式只能选炒锅 | `diy.js` `fetchSuggestion()` 中 `cookingMethod` 赋值在 `if (res.ai_suggestion)` 内，数据库匹配路径返回 `ai_suggestion: null` | SaveDialog 烹饪方式从只读 `<input>` 改为 `<select>` 下拉框，支持炒锅/空气炸锅/蒸锅三选一                     |
| 2  | DIY 食谱后无提交广场入口 | `doSave()` 成功后立即关闭弹窗，导致 SaveDialog step 2 一闪而过；`done` 状态也缺少入口                                                 | 后端新增 `PUT /api/custom/{id}/publish` 避免重复创建；前端 done 状态新增"📤 发布到广场"按钮；弹窗 step 2 正确展示 |
| 3a | 管理员登录安全        | 前端路由守卫仅检查 token，任何登录用户都能看到 `/admin` 页面                                                                        | 新建 `AdminLogin.vue` 独立管理员登录页；路由守卫检查 `is_admin`，非管理员跳 `/admin/login`                |
| 3b | 后台统计数据显示假数据    | `admin_stats` 硬编码返回 `{users:0, foods:0, recipes:0}`                                                           | 改为查询 `User`/`Food`/`CustomRecipe` 真实数据库数据                                          |
| 3c | 缺少用户管理功能       | 管理后台用户管理为 P3 占位符                                                                                              | 后端新增 `GET/PUT/DELETE /api/admin/users`；前端新增用户管理 Tab — 封禁/解封/设为管理员/取消管理员/删除         |
| 4  | 排序只有降序无正序/逆序   | 前端无 `order` 状态；后端无 `order` 查询参数                                                                               | 后端新增 `order` 参数（desc/asc）；前端新增"▼降序/▲升序"切换按钮                                        |

#### 二、文件改动清单

| 文件                                         | 类型     | 说明                                                                            |
| ------------------------------------------ | ------ | ----------------------------------------------------------------------------- |
| `client/src/components/diy/SaveDialog.vue` | 修改     | 烹饪方式从只读改为下拉选择；新增 `cookingMethods`/`currentMethod` props + `updateMethod` emit |
| `client/src/stores/diy.js`                 | 修改     | `doSave` 不关闭弹窗；新增 `doPublishToSquare` 方法                                      |
| `client/src/views/DIY.vue`                 | 修改     | done 状态新增"发布到广场"按钮；SaveDialog 传递新 props                                       |
| `client/src/views/AdminLogin.vue`          | **新增** | 独立管理员登录页，验证 `is_admin` 后放行                                                    |
| `client/src/views/Admin.vue`               | 修改     | 新增用户管理 Tab（封禁/解封/升降级/删除）；退出登录按钮；真实统计数据                                        |
| `client/src/router/index.js`               | 修改     | 新增 `/admin/login` 路由；路由守卫检查 `requireAdmin` meta                               |
| `client/src/api/admin.js`                  | 修改     | 新增 `getStats`/`getUsers`/`updateUser`/`deleteUser`；修正 API 路径前缀                |
| `client/src/api/diy.js`                    | 修改     | 新增 `publishRecipe` API                                                        |
| `client/src/views/Square.vue`              | 修改     | 新增 `order` 状态 + "▼降序/▲升序"切换按钮                                                 |
| `server/src/custom_food/router.py`         | 修改     | 新增 `PUT /api/custom/{recipe_id}/publish` 发布端点                                 |
| `server/src/admin/router.py`               | 修改     | `admin_stats` 改为真实查询；新增用户管理 CRUD（`GET/PUT/DELETE /api/admin/users`）           |
| `server/src/public_food/router.py`         | 修改     | 新增 `order` 参数（desc/asc）支持正序/逆序排序                                              |

#### 三、涉及的 API 端点

| 方法     | 端点                                    | 用途                   |
| ------ | ------------------------------------- | -------------------- |
| PUT    | `/api/custom/{id}/publish`            | 将已保存菜谱发布到广场（审核中）     |
| GET    | `/api/admin/users`                    | 分页获取用户列表             |
| PUT    | `/api/admin/users/{id}`               | 更新用户（封禁/解封、升级/降级管理员） |
| DELETE | `/api/admin/users/{id}`               | 删除用户                 |
| GET    | `/api/admin/stats`                    | 平台数据统计（真实数据）         |
| GET    | `/api/public/recipes?order=asc\|desc` | 新增正序/逆序排序            |

#### 四、测试验证

* ✅ 烹饪方式下拉可选炒锅/空气炸锅/蒸锅

* ✅ 保存后弹窗询问"是否发布到广场"，done 状态也有备用入口

* ✅ 访问 `/admin` 自动跳 `/admin/login`，普通用户即使登录也无法访问

* ✅ 管理员 <admin@food-time.com> 登录后可查看真实统计数据、审核食谱、管理用户

* ✅ 排序新增"▼降序/▲升序"切换，列表按相反方向重新排序

* ✅ `2259016269@qq.com` 在用户管理 Tab 中正确显示

***

**最后更新：** 2026-07-24（P2 修复与完善完成：烹饪方式可选 + 发布入口 + 管理员安全 + 排序切换）\
**项目路径：** `d:\Desktop\test\TreaWork\Food-Time\`\
**GitHub**：<https://github.com/zhan-zip/Food-Time>

---

### 十二.13 P2 Bug 修复 — 2026-07-24 测试反馈修 bug（当天第1次）

**问题 1：AI 对话不回复（Assistant + TodayEat 均不工作）**

- 根因：`openai==1.35.10` 向 `httpx==0.28.1` 传入已废弃的 `proxies` 参数，导致 `AsyncClient.__init__()` 报错 `unexpected keyword argument 'proxies'`
- `chat_with_tools()` 返回 `None` → `service.run()` 跳过工具调用 → `chat_stream()` 同样失败返回 `""` → `response_text` 为空 → 前端无任何 token 事件 → 显示"AI 暂时无法给出推荐"
- 修复：`pip install "httpx>=0.27,<0.28"` 降级到 `0.27.2`

**问题 2：记账图表 + 转盘 Canvas 模糊**

- 根因：Canvas 未按 `devicePixelRatio` 缩放 → 高 DPI 屏幕上物理像素不足
- 修复：
  - SpinWheel：设置 `canvas.width/height = CSS_SIZE * DPR`，用 `ctx.setTransform(DPR,0,0,DPR,0,0)` 缩放上下文 → 清晰
  - Expense 图表：Canvas 手绘替换为 ECharts（饼图 + 折线图），自动处理 DPR 且交互更好

**问题 3：转盘 GO 按钮跑偏**

- 根因：按钮 `position: absolute` 相对于 `.spin-wheel-wrapper` 但 `.spin-wheel-wrapper` 设置了 `position: relative` 却因 flex 布局导致参考点不正确
- 修复：新增 `.spin-canvas-box` 容器包裹 Canvas + 按钮，按钮绝对定位相对于此容器 → 精确居中

**问题 4：附近美食城市不显示**

- 根因：`ipapi.co` 在中国被墙，请求超时无返回
- 修复：改为多 API 链式尝试（`api.ip.sb` → 高德 → `api.vore.top`），任一成功即使用

---

### 十二.14 P2 Bug 修复（第二轮）— 2026-07-24（当天第2次）

**问题 5：转盘多次转动结果不一致**

- 根因：`currentRotation` 累加后，`targetAngle = currentRotation + (360*5 + 360 - θ)` 总旋转量包含了上次的偏移，导致第 2 次及以后转动时对准了错误的扇形
- 修复：从当前位置计算增量 `delta = (targetStop - currentMod) % 360 + 360*5`，保证无论转动多少次每次都对

**问题 6：TodayEat 中 AI 面板移除**

- 原因：用户反馈 AI 助手页已专职处理对话，TodayEat 中冗余的 AI 智能推荐面板（FR-23）无必要
- 修复：删除 FR-23 AI 智能推荐面板及关联 ~150 行 JS，FR-24 附近美食最初被误删（已在下一条记录恢复）

**问题 7：附近城市显示拼音 + 搜不出内容**

- 根因：
  1. IP 定位 API 顺序错误：`api.ip.sb`（返回英文/拼音）排第一 → 城市名显示 "zaozhuang"
  2. `httpx 0.28.1` 与 `openai` 不兼容 → AI 无法流式输出 → `nearbyResult` 为空
- 修复：高德 API 排第一位（返回中文城市名），httpx 已在上一次修复（十二.13）中降级

**补充说明**：本次 AI 推荐模块移除时，Home.vue 卡片描述中的 `'排序搜索、转盘决策、AI推荐'` 也应同步改为 `'排序搜索、转盘决策'`（AI推荐功能已移除）。

---

### 十二.15 附近美食恢复 + 拼音修复 — 2026-07-24（当天第3次）

- FR-24 附近美食代码被误删（AI 面板删除时一并移除），已完整恢复
- IP 定位 API 链调整为：**高德（中文）→ api.ip.sb（拼音备选）→ api.vore.top（备选）**
- SSE 解析修复：原代码错误地用 `parsed.type === 'token'` 判断（`data` JSON 不含 `type` 字段），改为与 Assistant.vue 一致的 `event:` / `data:` 两行配对解析
- 高德 API Key 替换为用户真实 Key

---

### 十二.16 高德 Key 修复 + Prompt 精简 — 2026-07-24（当天第4次）

- 第一个 Key 报 `USERKEY_PLAT_NOMATCH`（平台类型不匹配），用户申请新 Key 后正常
- 城市名正则修正：`/市|省$/`（匹配任意位置"市"）→ `/市$|省$/`（仅匹配末尾）
- 附近美食 prompt 精简：`3-5 道菜，每道菜注明菜名和简短推荐理由` → `3道菜，每道一行：菜名 — 一句话理由，总共不超过100字`

---

## 十三、测试记录

> 记录每次功能开发后的测试结果。每条测试记录包含测试范围、测试方式、结果和备注。
>
> **测试方式分类**：
> - P0 — 手动执行 API 请求（curl / Swagger / 浏览器直接访问）
> - P1 — 手动操作前端页面 + 浏览器 DevTools 观察
> - P2 — pytest / Vitest 自动化测试（待写）
>
> 每条记录末尾标注了本次测试覆盖的后端模块和前端页面。

### 测试 1 — 2026-07-20 P0 阶段验证

| # | 测试内容 | 方式 | 结果 | 备注 |
|---|---------|------|------|------|
| 1 | `POST /api/auth/register` — 注册返回 JWT + User | P0 | ✅ | 重复邮箱正确拒绝 |
| 2 | `POST /api/auth/login` — 登录返回 JWT + User | P0 | ✅ | |
| 3 | `GET /api/foods` — 返回 102 条种子数据 | P0 | ✅ | |
| 4 | `GET /api/foods/categories` — 返回 12 个分类 | P0 | ✅ | |
| 5 | `GET /api/auth/me` — JWT 认证返回用户信息 | P0 | ✅ | |
| 6 | `GET /api/health` — 健康检查 | P0 | ✅ | |

**覆盖模块**：auth, food  
**覆盖页面**：无（仅后端）

---

### 测试 2 — 2026-07-23 SMTP 邮件系统 + 前端表单校验

| # | 测试内容 | 方式 | 结果 | 备注 |
|---|---------|------|------|------|
| 1 | SMTP 连接 `smtp.qq.com:587` 成功 | P0 | ✅ | 邮件 3.4 秒发送 |
| 2 | `POST /api/auth/send-code` — 返回验证码已发送 | P0 | ✅ | |
| 3 | 登录/注册表单校验 — 红框 + 小字即时提示 | P1 | ✅ | 空邮箱/格式错误/密码过短 |
| 4 | `start.bat` 一键启动前后端 | P1 | ✅ | 两个新窗口正常打开 |

**覆盖模块**：auth  
**覆盖页面**：Login.vue, Register.vue

---

### 测试 3 — 2026-07-23 美食广场 + 食谱详情 + 评论区

| # | 测试内容 | 方式 | 结果 | 备注 |
|---|---------|------|------|------|
| 1 | `GET /api/public/recipes` — 返回 4 个食谱 + 分页正确 | P0 | ✅ | |
| 2 | `GET /api/public/recipes/1` — 番茄炒蛋详情含食材/步骤 | P0 | ✅ | |
| 3 | 前端广场页加载 4 张卡片，点击跳转详情页 | P1 | ✅ | |
| 4 | 详情页展示完整信息 + 评论区未登录提示登录 | P1 | ✅ | |

**覆盖模块**：public_food, food  
**覆盖页面**：Square.vue, SquareDetail.vue

---

### 测试 4 — 2026-07-23 记账分类 + OCR + 前端修复

| # | 测试内容 | 方式 | 结果 | 备注 |
|---|---------|------|------|------|
| 1 | OCR 需有效 Qwen API Key，待补充 | — | 📋 | 需运行时验证 |

**覆盖模块**：expense  
**覆盖页面**：Expense.vue

---

### 测试 5 — 2026-07-24 P2 修复与完善

| # | 测试内容 | 方式 | 结果 | 备注 |
|---|---------|------|------|------|
| 1 | 烹饪方式下拉可选炒锅/空气炸锅/蒸锅 | P1 | ✅ | SaveDialog 下拉选择 |
| 2 | 保存后弹窗询问"是否发布到广场" | P1 | ✅ | done 状态有备用入口 |
| 3 | 访问 `/admin` 自动跳 `/admin/login` | P1 | ✅ | 普通用户跳转 |
| 4 | 管理员查看真实统计数据 | P1 | ✅ | 后台真实查询 |
| 5 | 排序"▼降序/▲升序"切换 | P1 | ✅ | 列表按相反方向重排 |
| 6 | 用户管理 Tab 显示正确 | P1 | ✅ | |

**覆盖模块**：custom_food, admin, public_food  
**覆盖页面**：DIY.vue, Admin.vue, AdminLogin.vue, Square.vue

---

### 测试 6 — 2026-07-24 P2-3 食物决策辅助 + P2-4 SCSS

| # | 测试内容 | 方式 | 结果 | 备注 |
|---|---------|------|------|------|
| 1 | `npm install -D sass` — SCSS 依赖安装 | P1 | ✅ | 9 packages added |
| 2 | `npx vite build` — 前端生产构建 | P1 | ✅ | 131 modules, 0 errors, 891ms |
| 3 | TodayEat "搜索浏览"Tab — 搜索/分类/食物列表 | P1 | 📋 | 需人工验证（启动前后端后测试） |
| 4 | TodayEat "智能决策"Tab — 筛选面板（辣度/菜系/热量/烹饪方式） | P1 | 📋 | 需人工验证 |
| 5 | 决策转盘 — 手动添加选项 / 从搜索结果加载 / 清空 / 转动 | P1 | 📋 | 需人工验证 |
| 6 | AI 智能推荐 — 根据筛选条件 SSE 调用 AI | P1 | 📋 | 需有效 DeepSeek API Key |
| 7 | 附近美食 — IP 定位获取城市 + AI 推荐当地特色菜 | P1 | 📋 | 需有效 DeepSeek API Key + 外网 |

**覆盖模块**：food, chat  
**覆盖页面**：TodayEat.vue（新增 SpinWheel.vue 组件）

**验证方式**：
1. 启动前后端（`start.bat` 或分别启动）
2. 登录后访问 `http://localhost:5173/today-eat`
3. 切换到「智能决策」Tab，测试筛选器、转盘、AI推荐、附近美食
4. 切换到「搜索浏览」Tab，验证原有搜索功能不受影响

---

### 测试 7 — 2026-07-24 P2 Bug 修复（AI + Canvas + 城市定位）

| # | 测试内容 | 方式 | 结果 | 备注 |
|---|---------|------|------|------|
| 1 | `pip install "httpx>=0.27,<0.28"` — 修复 openai/httpx 不兼容 | P1 | ✅ | httpx 0.27.2 |
| 2 | 后端启动日志 — 无 `proxies` 错误 | P1 | ✅ | Application startup complete |
| 3 | `npx vite build` — ECharts + SpinWheel DPR + 城市 API 构建 | P1 | ✅ | 724 modules, 0 errors |
| 4 | AI 对话 — Assistant 页 + TodayEat AI 推荐 | P1 | 📋 | 需人工验证（发送消息测试） |
| 5 | ECharts 饼图 + 折线图 — Expense 页渲染 | P1 | 📋 | 需人工验证 |
| 6 | 转盘 — Canvas 清晰度 + GO 按钮位置 | P1 | 📋 | 需人工验证 |
| 7 | 附近美食 — 城市名显示 | P1 | 📋 | 需人工验证（依赖外网 API） |

**覆盖模块**：chat, expense  
**覆盖页面**：TodayEat.vue, Expense.vue, SpinWheel.vue, Assistant.vue

---

### 测试 8 — 2026-07-24 P2 Bug 修复（第二轮）

| # | 测试内容 | 方式 | 结果 | 备注 |
|---|---------|------|------|------|
| 1 | `npx vite build` — 移除 AI/附近代码后构建 | P1 | ✅ | 724 modules, 0 errors |
| 2 | TodayEat.js 体积 16.94KB → 12.41KB（-27%） | P1 | ✅ | gzip 6.98→5.16KB |
| 3 | 转盘多次转动 — 指针指向与文字结果一致 | P1 | 📋 | 需人工验证 |
| 4 | TodayEat 智能决策 Tab — 无 AI/附近面板 | P1 | 📋 | 需人工验证 |

**覆盖模块**：food  
**覆盖页面**：TodayEat.vue, SpinWheel.vue

---

### 测试 9 — 2026-07-24 附近美食恢复 + 拼音修复

| # | 测试内容 | 方式 | 结果 | 备注 |
|---|---------|------|------|------|
| 1 | TodayEat 智能决策 Tab — 仅 AI 面板消失，附近美食面板存在 | P1 | 📋 | 需人工验证 |
| 2 | IP 定位城市名 — 显示中文（如"枣庄"） | P1 | 📋 | 需人工验证，高德真实 Key |
| 3 | 点击「查看当地特色菜推荐」— AI 流式返回推荐内容 | P1 | 📋 | SSE event: 行解析修复 |
| 4 | `npx vite build` — 无错误 | P1 | ✅ | 724 modules, 0 errors |

**覆盖模块**：food, chat  
**覆盖页面**：TodayEat.vue

**本次根因**：SSE 格式为 `event: token\ndata: {"content":"..."}\n\n`，原代码跳过 `event:` 行直接解析 `data: JSON` 并检查 `parsed.type === 'token'`，但 `data` JSON 不含 `type` 字段 → 永假 → 0 token → "暂无结果"

---

### 测试 10 — 2026-07-24 高德 Key 修复 + Prompt 精简

| # | 测试内容 | 方式 | 结果 | 备注 |
|---|---------|------|------|------|
| 1 | 高德 API 终端测试 — `"city": "枣庄市"` | P1 | ✅ | Key 平台类型为 Web 服务 |
| 2 | 城市名正则 — `枣庄市` → `枣庄`（末尾去"市"） | P1 | ✅ | `/市$|省$/` |
| 3 | 附近美食 Prompt — 响应内容精简 | P1 | 📋 | 需人工验证 |
| 4 | `npx vite build` — 无错误 | P1 | ✅ | 724 modules, 0 errors |

**覆盖模块**：food, chat  
**覆盖页面**：TodayEat.vue

---

### 测试 11 — 2026-08-01 C2 默认密钥修复

| # | 测试内容 | 方式 | 结果 | 备注 |
|---|---------|------|------|------|
| 1 | `check_security_config` 三态单测（空值/默认值/安全值） | P2 | ✅ | 空值→2 条未配置；默认值→2 条默认值警告；安全值→空列表 |
| 2 | 不安全配置启动拦截 — 模拟 `food-time-dev-secret` / `admin123` | P0 | ✅ | 打印明确拒绝提示，进程退出码=1 |
| 3 | 安全配置（本地 .env）加载 `main` 模块 | P0 | ✅ | 通过安全校验，正常加载 |
| 4 | 数据库实测 `init_admin` 重置默认管理员密码 | P2 | ✅ | 密码 admin123 → .env 新密码（verify_password 双验证） |

**覆盖模块**：auth, config, main  
**覆盖页面**：无（后端启动安全校验 + 管理员初始化）

**修复说明**：`JWT_SECRET`/`ADMIN_PASSWORD` 默认值置空；启动时安全校验拒绝空/默认值并 `sys.exit(1)`；`init_admin` 检测历史管理员默认密码并自动重置。

---

### 测试 12 — 2026-08-01 C5 SaveDialog 保存结果反馈修复

| # | 测试内容 | 方式 | 结果 | 备注 |
|---|---------|------|------|------|
| 1 | `vite build` 前端生产构建 | P1 | ✅ | 3.40s，0 errors |
| 2 | 保存失败场景 — 不跳转成功页、停留 step1 显示错误 | P2 | ✅ | Vue reactivity 模拟：step 保持 0，saving 复位 |
| 3 | 保存成功场景 — 跳转成功页 step2 | P2 | ✅ | savedResult 含 id 时 step→2 |
| 4 | 边界 — 保存返回无 id 无效对象不跳转 | P2 | ✅ | 防御性判断生效 |
| 5 | 防重复提交 — saving 期间按钮禁用/提交拦截 | P2 | ✅ | `!name.trim() || saving` 守卫 |

**覆盖模块**：custom_food（前端对接）  
**覆盖页面**：DIY.vue, SaveDialog.vue

**修复说明**：`handleSubmit` 不再无条件跳 step2；`DIY.vue` 将 `doSave` 返回值经 `saveError` 传回；仅成功时跳转，失败时停留在填表页展示错误。

---

### 测试 13 — 2026-08-01 C1 RAG embedding 修复

| # | 测试内容 | 方式 | 结果 | 备注 |
|---|---------|------|------|------|
| 1 | `embed` 真实调用 — 返回 1024 维语义向量 | P0 | ✅ | 全非零（原为零向量），DashScope text-embedding-v3 |
| 2 | 语义相似度区分 — 番茄炒蛋 vs 西红柿炒鸡蛋 / 黑椒牛排 | P0 | ✅ | 0.84 vs 0.52（原零向量全相同） |
| 3 | 完整 RAG 构建 + 语义搜索（60 条样本） | P0 | ✅ | 「番茄/宫保鸡丁/红烧肉」等召回正确，embedding=OK |
| 4 | DashScope 批量限制处理 — 单次 ≤10 条自动分批 | P2 | ✅ | 修复 batch=50 超限导致 embedding 失败问题 |

**覆盖模块**：services(deepseek, vector_store), chat(RAG)  
**覆盖页面**：Assistant.vue（AI 对话 RAG 语义检索）

**修复说明**：`embed()` 改用 Qwen/DashScope `text-embedding-v3`（复用 QWEN_API_KEY，零新增成本），内部按 10 条分批，向量维度 1536→1024，失败自动回退关键词检索。

---

### 测试 14 — 2026-08-01 P1 安全项修复（H6/H2/H7/H8/H3）

| # | 测试内容 | 方式 | 结果 | 备注 |
|---|---------|------|------|------|
| 1 | H6 SSRF — `is_safe_image_url` 12 个 URL 场景 | P2 | ✅ | https 公网放行；http/file/私有 IP/内网域名拦截；OCR data URL 放行 |
| 2 | H2 注册竞态 — 3 并发注册同一邮箱 | P2 | ✅ | 1 成功 + 2 duplicate，无 500 |
| 3 | H7 越权 — 未公开食物/未审核食谱访问 | P0 | ✅ | `GET /api/foods/767` 与 `/api/public/recipes/5` 均返回 404 |
| 4 | H8 超时 — 三个 AI client timeout 配置 | P0 | ✅ | connect 10s / read 60s / write 10s / pool 10s |
| 5 | H3 种子 tags — 111 处字符串转 dict | P2 | ✅ | SAMPLE_FOODS / SAMPLE_RECIPES 全部为 dict |
| 6 | 整体集成 — TestClient 启动完整应用 | P0 | ✅ | lifespan 正常，核心 API 全部 200 |

**覆盖模块**：auth, food, chat, public_food, services(deepseek/qwen), seed  
**覆盖页面**：Assistant.vue（AI 对话）、DIY.vue（保存）、Expense.vue（OCR 不受影响）

**修复说明**：H6 图片 URL 白名单校验防 SSRF；H2 注册改用 `IntegrityError` 捕获防竞态；H7 未公开/未审核数据加访问过滤；H8 AI 客户端显式超时；H3 种子数据 tags 改 dict 格式。

---

### 测试 15 — 2026-08-01 第一批：C4/H9/H10/H1

| # | 测试内容 | 方式 | 结果 | 备注 |
|---|---------|------|------|------|
| 1 | C4 utcnow 替换 — 全库无残留 + JWT 生成 | P2 | ✅ | `timezone.utc`，token 正常 |
| 2 | H9 金额解析 — 11 个金额场景 | P2 | ✅ | 非数字不再 500，返回识别失败提示 |
| 3 | H10 删除用户 — 7 类关联数据清理 | P2 | ✅ | `delete_user` 无外键错误、无残留 |
| 4 | H1 SSE done — mock `run` 抛异常 | P0 | ✅ | error 后补发 done，顺序正确 |

**覆盖模块**：auth, expense, admin, chat  
**覆盖页面**：Expense.vue（OCR）、Admin.vue（用户管理）、Assistant.vue（AI 对话）

**修复说明**：C4 时间戳改时区感知；H9 金额安全解析；H10 删除用户清理关联数据（方案 A）；H1 SSE 错误后补发 done。

---

### 测试 16 — 2026-08-01 删除用户审计记录功能（新功能）

| # | 测试内容 | 方式 | 结果 | 备注 |
|---|---------|------|------|------|
| 1 | 后端 — `deleted_users` 表创建 | P2 | ✅ | `init_db` create_all 建新表 |
| 2 | `delete_user` 生成审计记录（基本信息+数据摘要） | P2 | ✅ | 账单 2 共 55.5 / 饮食 1 / 菜谱 1 / 对话 1 摘要正确 |
| 3 | `GET /api/admin/deleted-users` 分页接口 | P0 | ✅ | 返回删除记录与数据摘要 |
| 4 | 前端 Admin.vue 新增"已删除用户"Tab + `vite build` | P1 | ✅ | 表格展示删除记录，构建通过 |

**覆盖模块**：admin（新增 `deleted_users` 表 + `deleted-users` 接口）  
**覆盖页面**：Admin.vue（新增"已删除用户"Tab）

**功能说明**：删除用户（方案 A）时，将用户基本信息与数据摘要（饮食/账单/菜谱/对话数 + 累计消费）存档到 `deleted_users` 表，后台可通过"已删除用户"Tab 查看审计记录。数据库表从 14 张增至 15 张。
