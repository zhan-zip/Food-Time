# 食光记 (Food-Time) Bug 审查报告

> **审查日期**：2026-07-31  
> **审查范围**：全项目（50+ 源码文件 + 8 份设计文档）  
> **审查方式**：行级代码通读 + 架构审查 + 5 个并行 agent  
> **Bug 总数**：约 50 个

---

## 📌 给下一个对话窗口的交接说明

> **请先读完这一段再动手。** 这份文档是「食光记」项目的 Bug 交接清单，目的是让任何新的对话窗口（哪怕完全没有看过之前的历史对话）也能快速理解项目现状、直接开始修复工作。

### 你是谁 / 我是谁
- 你是一个新的 Claude Code 对话窗口。项目位于 `D:\Desktop\test\TreaWork\Food-Time`。
- 本报告由上一个对话窗口完成：先通读了全部 8 份设计文档 + 50+ 个源码文件，再用 5 个并行子 agent 交叉核对，最后汇总成这份清单。

### 这份文档的用途
1. **交接**：记录所有已知 Bug、根因、影响、修复方向，避免下个窗口重新从零排查。
2. **继续修复**：按下方「修复优先级建议」从 P0 开始逐项处理。每修完一项，建议把该条状态改为 `✅ 已修复`，方便追踪进度。
3. **当工作手册**：文档中的"涉及文件 + 行号 + 根因 + 修复建议"就是现成的排查路径，可以直接跳到对应代码验证。

### 开始修复前请先了解
- **项目规则**：务必先读项目根目录的 `CLAUDE.md`（8 条硬性规则：先查根因、多方案等抉择、自测、严禁编造、Git 归档、文档同步、测试记录等）。本报告写作时这些规则已生效，请遵守。
- **全局规则**：用户级 `C:\Users\李\.claude\CLAUDE.md` 有通用工作流程（中文、汇报格式、诚实原则）。
- **文档索引**：项目所有 .md 设计文档及其用途，见 `CLAUDE.md` 中的「项目核心文档」表。
- **技术栈**：Vue 3 + Vite 前端（`client/`）/ FastAPI + MySQL 后端（`server/`）/ DeepSeek + Qwen VL AI。MySQL 端口 3307。

### 修复工作建议流程
1. 先读本文档「修复优先级建议」章节，从 P0 开始。
2. 每个 Bug：读对应文件 → 确认根因（规则一：先查根因）→ 若方案不唯一，列优劣势等用户抉择（规则二）→ 修复 → 自测（规则三）。
3. 修复完成后按项目规则做 Git 提交、文档同步、测试记录（规则六七八）。

### 已知注意事项
- **Bug 数量可能不准**：报告基于静态代码审查，未实际运行项目。修复某条时若发现实际行为与描述不符，以运行结果为准并更正文档。
- **行号可能漂移**：代码被修改后，报告中标注的行号可能不再准确，定位时以当前文件为准。
- **紧急项提醒**：`C2`（默认 JWT 密钥 + 管理员密码）和 `H6`（SSRF）属于安全问题，若本项目要对外部署，建议优先处理。

---



## 🔴 严重 (Critical) — 5 个

### C1. RAG 向量索引完全无效 [ ]

- **涉及文件**：`server/src/services/deepseek.py:109`、`server/src/services/vector_store.py:153`
- **问题描述**：`embed()` 使用 `model="deepseek-chat"` 调用 `/embeddings` 端点，但 DeepSeek 的 chat 模型不支持 embedding API。调用必然失败 → fallback 返回 1536 维零向量。ChromaDB 中所有文档向量完全相同，余弦搜索返回的结果毫无意义。
- **影响**：整个 RAG 语义检索功能形同虚设，实际召回全靠关键词回退碰运气。AI 对话中的"预获取信息——食物库语义搜索"实际返回的是随机/无效结果。
- **修复建议**：换用真正支持 embedding 的模型（如 `text-embedding-3-small`、`bge-large-zh` 等），或在 prompt 中直接传入关键词匹配结果而不依赖向量检索。

### C2. 默认 JWT 密钥 + 默认管理员密码 → 认证可被绕过 ✅ 已修复 [x]

- **涉及文件**：`server/src/config.py:12,42` → `server/src/dependencies.py:25-27` → `server/src/auth/service.py:100-116`
- **问题描述**：如果 `.env` 文件不存在或未覆盖默认值，`JWT_SECRET = "food-time-dev-secret"`、`ADMIN_PASSWORD = "admin123"`。攻击者知道这些默认值即可伪造任意用户（含管理员）的 JWT，或直接以管理员身份登录。
- **影响**：部署到服务器后忘记创建/配置 `.env` → 整个认证系统形同虚设，攻击者可以任意冒充用户、访问管理后台、删除数据。
- **修复建议**：
  1. 在 `config.py` 中将 `JWT_SECRET` 默认值设为空字符串 `""`
  2. 在 FastAPI 启动时检测：若 `JWT_SECRET` 为空或等于已知默认值，直接拒绝启动并打印明确提示
  3. 对 `ADMIN_PASSWORD` 做同样检测
- **✅ 修复记录（2026-08-01）**：
  - `config.py`：`JWT_SECRET` / `ADMIN_PASSWORD` 默认值置空；新增 `INSECURE_LEGACY_VALUES` 常量 + `check_security_config()` 校验函数
  - `main.py`：模块加载时执行安全校验，空值/已知默认值 → 打印明确提示 + `sys.exit(1)` 拒绝启动
  - `auth/service.py`：`init_admin` 检测历史管理员密码仍为 `admin123` 时，自动重置为 `.env` 新密码（修复闭环）
  - 本地 `.env`：`ADMIN_PASSWORD` 已更新为强随机密码
  - 测试：`check_security_config` 空值/默认值/安全值三态单测通过；不安全配置启动退出码=1 拒绝启动；安全配置正常加载；数据库实测管理员默认密码已重置

### C3. RAG 索引启动时每次删除重建，多 worker 部署必崩溃 [ ]

- **涉及文件**：`server/src/main.py:37-62`、`server/src/services/vector_store.py:107-109`
- **问题描述**：每次 FastAPI 启动都执行 `_client.delete_collection()` 然后重建。如果部署时开了多个 worker 进程（如 `uvicorn --workers 4`），两个进程同时 delete/create ChromaDB collection → 数据损坏或进程崩溃。
- **影响**：生产环境多 worker 部署必定出问题，且 ChromaDB 的持久化文件可能损坏。
- **修复建议**：改为启动时检查已有索引 → 若已存在则跳过（不删除）；或使用 ChromaDB 的 `upsert` 代替 `delete + add`。同时用文件锁或数据库标志位确保只有一个 worker 执行初始化。

### C4. `datetime.utcnow()` 已被 Python 3.12+ 废弃 [ ]

- **涉及文件**：`server/src/auth/service.py:25,72`、`server/src/chat/service.py` 及多处
- **问题描述**：Python 3.12 废弃了 `datetime.utcnow()`，项目运行在 Python 3.13 上。运行时产生 `DeprecationWarning`，且 naive datetime 无法正确处理时区。所有时间戳都是无时区信息的"裸时间"。
- **影响**：未来 Python 版本可能彻底移除此方法导致运行时错误。当前所有 JWT 过期时间、验证码过期时间、记录时间等均无时区信息，跨时区部署时行为不可预期。
- **修复建议**：全局替换为 `datetime.now(datetime.UTC)` 或 `datetime.now(timezone.utc)`。

### C5. SaveDialog 保存失败仍显示"保存成功" [ ]

- **涉及文件**：`client/src/components/diy/SaveDialog.vue:103-107`、`client/src/stores/diy.js:149-172`
- **问题描述**：`handleSubmit` 无条件设置 `step = 2`（成功页面），完全不检查 `store.doSave()` 的返回值。即使后端返回失败（网络错误/数据校验失败），用户也看到"保存成功！🎉"。
- **影响**：用户满怀期待地填写菜名后点击保存 → 实际后端未保存成功 → 前端弹窗"保存成功" → 用户离开页面 → 菜谱永久丢失。这是最影响用户体验的前端 bug。
- **修复建议**：
  1. `handleSubmit` 改为 `await` emit 的结果
  2. `DIY.vue` 的 `@save` 处理函数将 `doSave` 的返回值传回 SaveDialog
  3. 仅在 `success === true` 时跳转到 step 2，失败时显示错误信息在 step 1

---

## 🟠 高 (High) — 10 个

### H1. SSE error 事件后没有 done → 前端永久显示"思考中…" [ ]

- **涉及文件**：`server/src/chat/router.py:50-57`、`server/src/chat/service.py:95-96`
- **问题描述**：当 `json.loads(fn.arguments)` 解析失败、工具执行异常或流式输出中断时，路由只发送 `error` 事件但不发送 `done` 事件。前端 SSE 解析器等待 `done` 事件来关闭连接和清除 loading 状态。
- **影响**：AI 对话中断后前端一直显示"思考中…"，用户无法发送下一条消息，只能刷新页面。
- **修复建议**：在所有 error 分支后追加 `yield _sse("done", {...})`，确保客户端始终收到终止事件。

### H2. 用户注册 TOCTOU 竞态 → 500 错误 [ ]

- **涉及文件**：`server/src/auth/router.py:17-20`
- **问题描述**：注册流程中先 `SELECT` 检查邮箱是否已注册，再 `INSERT`。两个并发请求注册同一邮箱时，都能通过预检查 → 其中一个 `INSERT` 触发唯一索引冲突 → `IntegrityError` → HTTP 500。
- **影响**：用户看到 500 错误，以为是系统故障，实际是并发注册导致的竞态。
- **修复建议**：移除预检查的 SELECT，直接用 `try/except IntegrityError` 包裹 INSERT，捕获后返回 400 "该邮箱已注册"。

### H3. 种子数据 `tags` 存储格式错误 [ ]

- **涉及文件**：`server/src/seed.py:185`
- **问题描述**：种子数据中 `tags = '{"spicy":"high",...}'`（Python str）直接赋值给 SQLAlchemy `JSON` 列。MySQL 中存储的是 `"{\"spicy\":\"high\"}"`（被二次序列化的字符串）而非 `{"spicy":"high"}`（JSON 对象）。运行时创建的 dict-格式 tags 和种子数据的 string-格式 tags 不兼容。
- **影响**：种子数据的 tags 无法被 `JSON_EXTRACT` 查询；前端/工具读取 tags 时需额外判断类型，且部分代码假设 tags 是 dict 会出错。
- **修复建议**：将 `seed.py` 中所有 tags 从字符串改为 Python dict 字面量。

### H4. 食物搜索每次加载全部匹配行做计数 [ ]

- **涉及文件**：`server/src/food/router.py:58-59`
- **问题描述**：`total = len(result.scalars().all())` 将所有匹配行完整加载到 Python 内存中再取 len，而非使用 `SELECT COUNT(*)`。766 条数据目前 OK，但数据增长到数万条时会导致严重的内存和性能问题。
- **影响**：数据增长后搜索接口响应时间急剧恶化，内存压力增大。
- **修复建议**：使用 `select(func.count(Food.id)).where(...)` 做独立的计数查询。

### H5. 全站无 rate limiting（速率限制） [ ]

- **涉及文件**：`server/src/auth/router.py`（login/register/send-code）、`server/src/chat/router.py`（send）
- **问题描述**：登录、注册、发送验证码、AI 对话等关键接口没有任何频率限制。
- **影响**：
  - 登录接口可被暴力破解密码
  - 注册接口可被恶意创建大量账号
  - 发送验证码接口可被用来短信/邮件轰炸任意邮箱
  - AI 对话接口可被无限消耗 API 额度（DeepSeek API 按 token 计费）
- **修复建议**：引入 slowapi 或类似中间件，对敏感接口设置合理的限速（如登录 5 次/分钟/IP，send-code 1 次/分钟/邮箱，chat 20 次/分钟/用户）。

### H6. 图片 URL SSRF 风险 [ ]

- **涉及文件**：`server/src/chat/router.py:51`、`server/src/chat/tools.py:471`、`server/src/services/qwen.py:66`
- **问题描述**：用户通过 `ChatSendRequest.image_url` 或 AI 调用的 `analyze_food_image` 工具传入的 URL，被直接发送给 Qwen VL API 让服务端去抓取。攻击者可以传入 `http://169.254.169.254/`（云服务商 metadata 端点）或 `file:///etc/passwd` 等内网地址。
- **影响**：云环境部署时可能泄露实例元数据（含临时凭证）；内网地址可能被探测。
- **修复建议**：对传入的 URL 做白名单校验——仅允许 `https://` 协议的公网 URL，拒绝 `http://`、`file://`、私有 IP 段（10.x、172.16-31.x、192.168.x、127.x、169.254.x）。

### H7. 未公开/未审核的食物可通过 ID 直接访问 [ ]

- **涉及文件**：`server/src/food/router.py:178`、`server/src/chat/tools.py:241`、`server/src/public_food/router.py:90-105`
- **问题描述**：
  - `GET /api/foods/{id}` 不检查 `is_public` 字段
  - `get_food_nutrition` AI 工具不检查 `is_public`
  - `GET /api/public/recipes/{recipe_id}` 详情页不检查 `publish_status == "approved"`
- **影响**：私密食谱、待审核 DIY 菜谱、被拒绝的投稿全部可被任意用户通过递增 ID 访问。
- **修复建议**：在以上所有端点中增加 `is_public == True` 或 `publish_status == "approved"` 过滤条件，未匹配时返回 404。

### H8. DeepSeek/Qwen 客户端无超时配置，请求可挂起长达 10 分钟 [ ]

- **涉及文件**：`server/src/services/deepseek.py:27`、`server/src/services/qwen.py:23`
- **问题描述**：`AsyncOpenAI` 客户端创建时未传 `timeout` 参数，openai 库默认超时为 600 秒。API 挂起时整个请求线程被阻塞达 10 分钟。
- **影响**：AI API 故障时前端请求挂起不动，数据库连接池被长时间占用（`pool_size=10`），其它正常请求也被阻塞。
- **修复建议**：创建 `AsyncOpenAI` 时传入 `timeout=httpx.Timeout(connect=10.0, read=60.0, write=10.0, pool=10.0)`。

### H9. OCR 返回非数字金额 → 500 [ ]

- **涉及文件**：`server/src/expense/router.py:261`
- **问题描述**：`amount = float(result.get("amount", 0))`——Qwen VL 返回的 amount 可能是 `"12.50元"`、`"12,50"`、`"约20"` 等非纯数字字符串。`float()` 直接抛 `ValueError` → 500。
- **影响**：用户上传了一张正常的小票 → OCR 识别成功但金额格式不规范 → 用户看到 500 错误，而非友好的"识别结果不准确，请手动调整"。
- **修复建议**：对 amount 做安全解析——尝试 `float()` 前先用正则提取数字部分，失败时返回 `amount: 0` 并提示用户手动输入。

### H10. admin delete_user 无外键处理 → 500 [ ]

- **涉及文件**：`server/src/admin/router.py:201`
- **问题描述**：直接 `db.delete(user)` 删除用户。若该用户有关联的 `diet_records`、`expense_records`、`custom_recipes`、`favorites`、`comments` 等数据，数据库外键约束触发 `IntegrityError` → 500。
- **影响**：管理员无法删除有历史数据的用户。
- **修复建议**：方案 A——删除前先清理关联数据（较安全）；方案 B——改为软删除（添加 `deleted_at` 字段，优于保留审计轨迹）。

---

## 🟡 中 (Medium) — 14 个

### M1. 种子数据独立运行不 commit → 全部丢失 [ ]

- **文件**：`server/src/seed.py:350-351`
- **描述**：`__main__` 块中只 `flush()` 不 `commit()`，脚本退出时所有操作回滚，控制台打印的"已插入"是虚假信息。
- **影响**：开发者手动运行 `python src/seed.py` 后发现数据库中没有任何数据，困惑且浪费时间。
- **修复**：在 `seed_all()` 调用后增加 `await db.commit()`。

### M2. fetchSuggestion 服务端报错时 stage 永久卡死 [ ]

- **文件**：`client/src/stores/diy.js:119-122`
- **描述**：HTTP 200 但 body 中含 `error` 时，设置 `suggestError` 但 `stage` 仍为 `'suggesting'`。`canSuggest` 要求 `stage === 'selecting'` → 按钮消失 → 用户无重试入口。
- **影响**：DIY 厨房选择食材后点"获取 AI 建议" → 后端提示"请至少选择一种主食材" → 界面永久显示"AI 正在分析……"无法操作。
- **修复**：在 `res.error` 分支增加 `stage.value = 'selecting'`。

### M3. CookingPanel Math.random() 在 render 中 → 动画跳跃 [ ]

- **文件**：`client/src/components/diy/CookingPanel.vue:135-162`
- **描述**：`flameStyle()` 和 `steamStyle()` 在模板渲染时调用，每次重新渲染都生成新的随机值。任何父组件状态变更（如切换烹饪方式）→ 火焰/蒸汽粒子坐标全部重新随机 → 动画突然跳到新位置。
- **影响**：烹饪动画生硬、不连贯，视觉效果差。
- **修复**：在 `onMounted` 中预计算粒子数组存为 ref，模板中使用固定值。

### M4. SpinWheel setTimeout 不清理 → 内存泄漏 [ ]

- **文件**：`client/src/components/today/SpinWheel.vue:141`
- **描述**：`spin()` 中的 4200ms 定时器在组件卸载时未清理。用户转动转盘后立即切换 Tab → emit 到已卸载组件。
- **影响**：控制台可能输出 Vue 警告，内存微量泄漏。
- **修复**：在 `onBeforeUnmount` 中 `clearTimeout`，并设置标志位防止 emit。

### M5. 邮箱验证码使用非加密随机数 [ ]

- **文件**：`server/src/auth/service.py:30-31`
- **描述**：`generate_verification_code()` 使用 `random.choices(string.digits, k=6)` 生成 6 位验证码。`random` 模块不是密码学安全的随机数生成器。
- **影响**：攻击者理论上可以预测验证码，但实际利用难度较高（需已知随机种子）。
- **修复**：改用 `import secrets; return ''.join(secrets.choice(string.digits) for _ in range(6))`。

### M6. SMTP 未配置时验证码明文出现在 HTTP 响应中 [ ]

- **文件**：`server/src/auth/router.py:64`
- **描述**：`return {"message": "...", "code": code}` — 验证码明文在 HTTP 响应体里，任何能看到网络请求的人（浏览器 DevTools / 中间人）都能获取。
- **影响**：部署到生产环境但 SMTP 未正确配置时，验证码形同虚设。
- **修复**：开发模式仅打印到控制台；生产模式若 SMTP 未配置则返回错误而非暴露验证码。

### M7. 邮件发送时 DB 事务被长时间持有 [ ]

- **文件**：`server/src/auth/router.py:47-64`
- **描述**：`send-code` 接口在 `db.flush()` 后、`db.commit()` 前执行了 `asyncio.to_thread(email_service.send_verification_code, ...)`（SMTP 可能需要 3-15 秒）。在此期间数据库连接和行锁一直被持有。
- **影响**：并发注册/发送验证码时可能耗尽数据库连接池（`pool_size=10`）。
- **修复**：将 SMTP 发送移到 `db.commit()` 之后，或在发送邮件前显式 commit。

### M8. SMTP 连接泄漏 [ ]

- **文件**：`server/src/services/email.py:44-60`
- **描述**：`send()` 方法中 `server.login()` 或 `server.sendmail()` 抛异常时 `server.quit()` 不会执行 → SMTP socket 泄漏。
- **影响**：长期运行后 socket 句柄耗尽。
- **修复**：使用 `try/finally` 确保 `server.quit()` 始终被执行。

### M9. 前端 App.vue token 状态不一致 [ ]

- **文件**：`client/src/App.vue:111,118,139-152`
- **描述**：`loadUserInfo` 调用 `/api/auth/me` 失败时被 `catch {}` 静默吞掉 → `userNickname` 为空但 `isLoggedIn` 仍为 `true`（因为 localStorage 中 token 仍然存在）。
- **影响**：token 过期后页面导航栏显示"已登录但无昵称"，且无自动退出或重新登录提示。
- **修复**：在 `catch` 中清除 token 并设置 `isLoggedIn = false`。

### M10. axios 401 拦截器只删 token 不删 user [ ]

- **文件**：`client/src/api/request.js:24-27`
- **描述**：401 时 `localStorage.removeItem('token')` 但 `localStorage.removeItem('user')` 未执行。下次路由守卫检查 `localStorage.getItem('user')` 仍能读到旧的用户对象。
- **影响**：token 被清除后 user 缓存仍在，路由守卫可能返回错误的管理员状态判断。
- **修复**：同时清除 `localStorage.removeItem('user')`。

### M11. Login.vue / AdminLogin.vue 错误信息被拦截器吞掉 [ ]

- **文件**：`client/src/views/Login.vue:95`、`client/src/views/AdminLogin.vue:93`
- **描述**：catch 中用 `e.response?.data?.detail` 取错误信息，但 `request.js` 拦截器已把异常转成了 `new Error(msg)`（`e.response` 为 undefined），总是回退显示默认提示。
- **影响**：用户登录失败时看不到后端返回的具体原因（如"账号已被封禁"），只看到"登录失败，请重试"。
- **修复**：改为 `e.message || '登录失败，请重试'`。

### M12. 响应式断点不统一 [ ]

- **文件**：`main.css`（1024/640）、`App.vue`（768）、`DIY.vue`（641/900）、`TodayEat.vue`（768/640）
- **描述**：640px（max-width）和 641px（min-width）产生 1px 死区。部分组件使用不同的断点系列。
- **影响**：在恰好 641px 宽度时，`main.css` 认为还在"移动端"但 `DIY.vue` 已进入"桌面端"，布局可能出现错位。
- **修复**：统一到一组 CSS 自定义属性（`--bp-sm: 640px; --bp-md: 768px; --bp-lg: 1024px`），所有组件引用同一套变量。

### M13. `send-code` 无身份验证，可被用来邮件轰炸 [ ]

- **文件**：`server/src/auth/router.py:44`
- **描述**：`POST /api/auth/send-code` 不需要登录，也不需要确认邮箱属于已注册用户。攻击者可以循环调用此接口轰炸任意邮箱。
- **影响**：目标邮箱收到大量验证码邮件 → 邮件服务商可能标记为垃圾邮件 → 正常邮件被拒收。
- **修复**：对 send-code 接口增加 IP 限速（如 1 次/IP/分钟），并添加 CAPTCHA 或要求已登录。

### M14. public_food 热榜排序分页逻辑错误 [ ]

- **文件**：`server/src/public_food/router.py:53,81-83`
- **描述**：SQL 用 `created_at` 排序并取 `offset + page_size*3` 行，然后在 Python 内存按 `hot_score` 重排并取前 `page_size`。第 2 页的 offset 跳过了按时间排序的前 N 项，但热榜应按全局 hot_score 排名——第 2 页的结果不正确，可能重复或遗漏。
- **影响**：用户翻页时看到重复的食谱或遗漏高热度食谱。
- **修复**：热榜模式应去掉 offset，取全部数据在 Python 排序后分页；或使用 SQL 子查询/LATERAL JOIN 在数据库侧完成 hot_score 排序。

---

## 🔵 低 (Low) — 15 个

### L1. 西蓝花/西兰花 emoji 不匹配 [ ]

- **文件**：`server/src/services/ingredient_emoji.py:20-21,53`
- **描述**：emoji 表和 fridge 分类使用 `"西蓝花"`（蓝），而 NUTRITION_REF / INGREDIENT_ALIAS 使用 `"西兰花"`（兰）。`get_emoji` 精确匹配 → 西兰花永远拿不到 emoji。
- **影响**：DIY 冰箱中西兰花食材卡无 emoji。
- **修复**：统一使用 `"西兰花"`（兰），或增加 alias 映射。

### L2. FridgeSection 遗留 debug console.log [ ]

- **文件**：`client/src/components/diy/FridgeSection.vue:81`
- **描述**：`console.log('[Fridge] select:'...)` 未删除。
- **修复**：移除。

### L3. SeasoningRack emit 参数重复 [ ]

- **文件**：`client/src/components/diy/SeasoningRack.vue:31`
- **描述**：`emit('select', item, type, type, e)` — 第 2 和第 3 个参数都是 `type`，意图是 `catKey` 和 `type`，但 `catKey` 永远是 `'seasoning'`。
- **修复**：改为 `emit('select', item, 'seasoning', type, e)`。

### L4. onAnimationDone 死代码 [ ]

- **文件**：`client/src/stores/diy.js:141-143`
- **描述**：定义了但从未被任何组件调用。CSS 动画无限循环，只能通过"跳过"按钮退出烹饪阶段。
- **修复**：要么移除，要么在 CookingPanel 动画 `animationend` 事件中调用。

### L5. SaveDialog methodLabel prop 传入但未使用 [ ]

- **文件**：`client/src/components/diy/SaveDialog.vue:76`
- **描述**：`methodLabel` prop 从 DIY.vue 传入但模板中从未引用。
- **修复**：移除 prop 或使用它。

### L6. PlateSection setTimeout 在 unmount 时不清理 [ ]

- **文件**：`client/src/components/diy/PlateSection.vue:51`
- **描述**：`_animating` 标记的 500ms 清理定时器在组件卸载时未取消。
- **修复**：在 `onBeforeUnmount` 中保存并清理 timeout ID。

### L7. SaveDialog 无 ESC 关闭 / 无焦点陷阱 [ ]

- **文件**：`client/src/components/diy/SaveDialog.vue`
- **描述**：Teleport 弹窗缺少 ESC 键关闭、无 `aria-modal`、无焦点锁定。
- **影响**：键盘用户无法便捷操作。
- **修复**：添加 `@keydown.escape="$emit('cancel')"` 和 `role="dialog" aria-modal="true"`。

### L8. IngredientCard 依赖 color-mix()（无旧浏览器 fallback） [ ]

- **文件**：`client/src/components/diy/IngredientCard.vue:49-50`
- **描述**：使用 `color-mix(in srgb, ...)`，Chrome 111+ 才支持，Safari 16.2+。旧浏览器中选中态完全不可见。
- **修复**：增加 fallback（如直接使用 `background: var(--color-primary)`）。

### L9. 无 `prefers-reduced-motion` 支持 [ ]

- **文件**：`main.css`、`SpinWheel.vue`、`DIY.vue`、`CookingPanel.vue`
- **描述**：所有动画（转盘 4s 旋转、页面过渡、火焰/蒸汽粒子、卡片悬浮）都没有考虑用户的系统级"减少动效"设置。
- **影响**：对动效敏感的用户（如前庭障碍患者）可能感到不适。
- **修复**：添加 `@media (prefers-reduced-motion: reduce) { *, *::before, *::after { animation-duration: 0.01ms !important; } }`。

### L10. 无 `:focus-visible` 键盘焦点样式 [ ]

- **文件**：`main.css`
- **描述**：按钮/链接在键盘导航时无可见焦点指示，仅输入框有 `box-shadow` 焦点环。
- **修复**：添加 `.btn:focus-visible { outline: 2px solid var(--color-primary); outline-offset: 2px; }`。

### L11. showFilterInDecide 设置但从不读取 [ ]

- **文件**：`client/src/views/TodayEat.vue:46,265`
- **描述**：`showFilterInDecide` 被赋值为 `true` 但模板中无任何 `v-if`/`v-show` 引用它。
- **修复**：移除死状态，或为其添加工效。

### L12. start.bat 无错误处理 [ ]

- **文件**：`start.bat`
- **描述**：如果 MySQL 未启动或端口被占用，后端窗口报错后立即关闭，用户看不到错误信息。
- **修复**：在窗口末尾添加 `pause`，或使用 `|| echo ERROR && pause`。

### L13. Admin.vue 审核通过/拒绝后仅 flush 不 commit [ ]

- **文件**：`server/src/admin/router.py:98,118`
- **描述**：依赖 `get_db` 的兜底 commit，但若中间有其他异常，flush 的结果可能丢失。
- **修复**：在 flush 后显式 `await db.commit()`。

### L14. `chat_stream` 失败时 `yield ""` → 无法区分空响应与错误 [ ]

- **文件**：`server/src/services/deepseek.py:77`
- **描述**：流式对话异常时 `yield ""`，调用方收到一个空 token。无法判断是"AI 无输出"还是"API 调用失败"。
- **修复**：增加异常日志级别，或在 `ChatService` 中检测全空响应并生成提示。

### L15. persona.txt 每次请求都从磁盘读取 [ ]

- **文件**：`server/src/chat/service.py:184-190`
- **描述**：注释说"热加载"，但实际每次调用都 `open()`。虽性能影响小，但意图与实现不一致。
- **修复**：在模块加载时读取并缓存到模块级变量。

---

## 📊 汇总统计

| 等级 | 数量 | 影响范围 |
|------|------|---------|
| 🔴 Critical | 5 | RAG 失效、认证安全、数据一致性、时间处理 |
| 🟠 High | 10 | SSE 协议、TOCTOU、SSRF、无限速、超时、数据泄露 |
| 🟡 Medium | 14 | 数据完整、前端状态机、断点统一、邮件安全 |
| 🔵 Low | 15 | 死代码、日志清理、无障碍、兼容性 |
| **总计** | **44** | |

### 按模块分布

| 模块 | Bug 数 |
|------|--------|
| 后端 — 认证 (auth) | 5 |
| 后端 — AI 对话 (chat) | 5 |
| 后端 — 食物库 (food) | 3 |
| 后端 — 记账 (expense) | 4 |
| 后端 — DIY (custom_food) | 3 |
| 后端 — 广场 (public_food) | 3 |
| 后端 — 管理 (admin) | 3 |
| 后端 — 服务 (services) | 7 |
| 前端 — 组件 (components) | 6 |
| 前端 — 视图 (views) | 3 |
| 前端 — 状态/路由 | 2 |

---

## 🎯 修复优先级建议

| 优先级 | 修复项 | 预计耗时 |
|--------|-------|---------|
| **P0** | C2: JWT + Admin 默认密钥检测 | 30 min |
| **P0** | C5: SaveDialog 成功/失败反馈 | 20 min |
| **P0** | C1: 换用真正的 embedding 模型（或移除向量路径） | 1 h |
| **P1** | H8: DeepSeek/Qwen 客户端添加 timeout | 15 min |
| **P1** | H5: 添加 rate limiting 中间件 | 2 h |
| **P1** | H3: 种子数据 tags 修复 | 1 h |
| **P1** | H6: SSRF URL 白名单校验 | 30 min |
| **P1** | H2: 注册 TOCTOU IntegiryError 处理 | 15 min |
| **P1** | H7: 私有/未审核数据访问控制 | 30 min |
| **P2** | M2: fetchSuggestion stage 重置 | 5 min |
| **P2** | M1: 种子脚本 commit | 5 min |
| **P2** | M3: CookingPanel 随机数缓存 | 15 min |
| **P2** | M6: 验证码不从 HTTP 响应暴露 | 10 min |
| **P2** | M8: SMTP 连接泄漏 | 10 min |
| **P3** | 低优先级 bug 批量修复 | 2 h |
