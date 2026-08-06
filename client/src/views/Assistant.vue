<template>
  <div class="page container page-section">
    <h2 class="section-title">AI 助手</h2>

    <div class="chat-container">
      <div class="chat-messages" ref="msgContainer">
        <div v-if="messages.length === 0" class="chat-welcome">
          <span>&#x1F916;</span>
          <h3>你好，我是食光记 AI 助手</h3>
          <p class="text-secondary">可以帮你：搜索食物、推荐食谱、分析营养、查看账单</p>
        </div>

        <!-- 快捷决策面板（始终可见） -->
        <div class="quick-decision-panel" v-if="messages.length === 0 || showQuickPanel">
          <div class="quick-decision-title">快速决策</div>
          <div class="quick-prompts">
            <button
              v-for="p in timeAwarePrompts"
              :key="p.label"
              class="quick-prompt-btn"
              @click="sendPrompt(p.text)"
            >
              <span class="prompt-icon">{{ p.icon }}</span>
              <span class="prompt-label">{{ p.label }}</span>
            </button>
          </div>
        </div>

        <!-- 为你推荐面板（个性化数据） -->
        <div v-if="showRecPanel" class="rec-panel card" style="margin-bottom: var(--spacing-md);">
          <div class="rec-panel-header">
            <span class="rec-panel-title">&#x1F3AF; 为你推荐</span>
            <button class="btn btn-ghost btn-sm" style="flex-shrink:0" @click="showRecPanel = false" title="收起">✕</button>
          </div>
          <div v-if="recLoading" class="text-muted text-sm">加载你的偏好数据...</div>
          <template v-else>
            <div class="rec-prefs">
              <span v-for="t in prefLabels" :key="t" class="tag tag-primary tag-sm">{{ t }}</span>
            </div>
            <div v-if="recNutrition.total_days > 0" class="rec-nutrition text-sm">
              📊 近 {{ recNutrition.total_days }} 天日均：<strong>{{ recNutrition.avg_calories }} kcal</strong> · 蛋白 <strong>{{ recNutrition.avg_protein }}g</strong>
            </div>
            <button class="btn btn-primary btn-sm" @click="genRecommend" :disabled="recGenerating" style="margin-top:8px">
              {{ recGenerating ? '🤖 生成中...' : '🤖 生成个性化推荐' }}
            </button>
            <div v-if="recRecommend" class="rec-result" v-html="renderMarkdown(recRecommend)"></div>
          </template>
        </div>

        <div
          v-for="(msg, idx) in messages"
          :key="idx"
          class="chat-bubble"
          :class="msg.role === 'user' ? 'chat-bubble--user' : 'chat-bubble--assistant'"
        >
          <div class="chat-bubble-avatar">
            {{ msg.role === 'user' ? '\u{1F464}' : '\u{1F916}' }}
          </div>
          <div class="chat-bubble-body">
            <div v-if="msg.role === 'user'" class="chat-bubble-text">{{ msg.content }}</div>
            <div v-else class="chat-bubble-text markdown" v-html="renderMarkdown(msg.content)"></div>
            <div v-if="msg.role === 'assistant' && getDishes(msg.content).length" class="eat-dishes">
              <span class="text-xs text-muted">记录我吃了：</span>
              <button v-for="d in getDishes(msg.content)" :key="d" class="tag tag-primary tag-sm eat-dish-btn" @click="eatDish(d)">🍽 {{ d }}</button>
            </div>
            <div v-if="msg.tooling" class="tool-indicator tooling">&#x1F50D; {{ msg.toolMsg }}</div>
            <div v-else-if="msg.toolMsg && !msg.content" class="tool-indicator tool-done">&#x2705; {{ msg.toolMsg }}</div>
          </div>
        </div>

        <div v-if="loading && messages.length > 0 && messages[messages.length-1].role === 'user'" class="chat-bubble chat-bubble--assistant">
          <div class="chat-bubble-avatar">&#x1F916;</div>
          <div class="chat-bubble-body">
            <div class="chat-bubble-text typing">思考中...</div>
          </div>
        </div>
      </div>

      <!-- 输入区 -->
      <div class="chat-input-area">
        <button v-if="!showQuickPanel && messages.length > 0" class="btn btn-ghost btn-sm" style="flex-shrink:0" @click="showQuickPanel = !showQuickPanel" :title="showQuickPanel ? '收起' : '快速决策'">
          🎯 决策
        </button>
        <input
          v-model="input"
          class="input"
          placeholder="输入消息，问问 AI 今天吃什么..."
          @keyup.enter="send"
          :disabled="loading"
        />
        <button class="btn btn-primary" @click="send" :disabled="loading || !input.trim()">
          发送
        </button>
      </div>
    </div>

    <p class="text-center text-muted text-sm" style="margin-top: var(--spacing-xl);">
      AI 对话基于 DeepSeek API（SSE 流式 + Tool Calling + RAG 知识库增强）
    </p>
  </div>
</template>

<script setup>
import { ref, computed, nextTick, onMounted } from 'vue'
import MarkdownIt from 'markdown-it'
import { getPreferences, getNutrition, createDietRecord } from '@/api/diet'

// 轻量 markdown 渲染（html:false 防 XSS，支持粗体/列表/标题/链接）
const md = new MarkdownIt({ html: false, linkify: true })

const input = ref('')
const loading = ref(false)
const messages = ref([])
const msgContainer = ref(null)
const currentSession = ref('default')
const showQuickPanel = ref(true)

// 时间感知快捷决策
const timeAwarePrompts = computed(() => {
  const hour = new Date().getHours()
  const base = [
    { icon: '🎲', label: '帮我选个晚饭', text: '帮我推荐一个适合晚餐的菜，要有肉有菜，营养均衡' },
    { icon: '🔥', label: '低热量推荐', text: '推荐几个低热量高蛋白的菜，适合减脂期吃' },
    { icon: '🍜', label: '快手菜', text: '今天不想做饭太久，推荐几个15分钟内能搞定的快手菜' },
  ]

  if (hour < 10) {
    base.unshift({ icon: '🌅', label: '早餐推荐', text: '推荐几个简单快手的早餐，要有营养' })
  } else if (hour < 14) {
    base.unshift({ icon: '☀️', label: '午餐推荐', text: '推荐几个适合午餐的菜，荤素搭配' })
  } else if (hour < 17) {
    base.unshift({ icon: '🍵', label: '下午茶', text: '推荐几个下午茶小食或饮品' })
  } else {
    base.unshift({ icon: '🌙', label: '晚餐推荐', text: '帮我推荐一个适合晚餐的菜，不要太油腻' })
  }

  base.push({ icon: '📊', label: '营养分析', text: '帮我分析一下我最近的饮食营养情况' })
  return base
})

const prompts = ['今天吃什么好？', '推荐一个低热量的菜', '我最近吃得太油了怎么办', '帮我分析一下我的营养摄入']

function sendPrompt(p) {
  input.value = p
  showQuickPanel.value = false
  send()
}

function renderMarkdown(content) {
  return md.render(content || '')
}

// 从 AI 回复中提取加粗菜名（**番茄炒蛋**），供「记录我吃了」
function getDishes(content) {
  const re = /\*\*([^*\n]+)\*\*/g
  const STOP = ['推荐理由', '做法', '小贴士', '注意', '建议', '营养', '热量', '步骤', '食材', '调料', '为什么', '总结', '点评', '提示', '今日', '近期', '搭配']
  const out = []
  let m
  while ((m = re.exec(content || ''))) {
    let name = m[1].trim().replace(/^\d+[.、)）\s]+/, '').replace(/[（(].*$/, '').trim()
    if (name.length < 2 || name.length > 12) continue
    if (STOP.some(s => name.includes(s))) continue
    if (!out.includes(name)) out.push(name)
  }
  return out.slice(0, 6)
}

// 一键记录「我吃了这个」
async function eatDish(name) {
  const token = localStorage.getItem('token')
  if (!token) return alert('请先登录')
  try {
    const res = await fetch('/api/foods?keyword=' + encodeURIComponent(name) + '&page_size=5', {
      headers: { Authorization: 'Bearer ' + token },
    })
    const data = await res.json()
    const items = (data && data.items) || []
    if (!items.length) { alert('未在食物库找到「' + name + '」'); return }
    const food = items[0]
    const qty = prompt('「' + food.name + '」吃了多少克？（默认 150）', '150')
    const grams = Math.max(1, Number(qty) || 150)
    await createDietRecord({ food_id: food.id, meal_type: 'lunch', quantity_g: grams })
    alert('已记录：' + food.name + ' ' + grams + 'g（午餐）')
  } catch (e) {
    alert('记录失败：' + (e.message || '请重试'))
  }
}

// ========== 为你推荐（个性化数据面板） ==========
const showRecPanel = ref(true)
const recLoading = ref(false)
const recPref = ref({})
const recNutrition = ref({})
const recRecommend = ref('')
const recGenerating = ref(false)

const prefLabels = computed(() => {
  const p = recPref.value
  const labels = []
  if (p.spicy_level >= 0.5) labels.push('🌶 偏辣')
  else if (p.total_records > 0) labels.push('🌶 清淡')
  if (p.fav_cuisines && p.fav_cuisines.length) labels.push(...p.fav_cuisines.map(c => '🍽 ' + c))
  if (!labels.length && !p.total_records) labels.push('暂无偏好（多记录饮食自动生成）')
  return labels
})

async function loadRecData() {
  recLoading.value = true
  try {
    const [pref, nut] = await Promise.all([getPreferences(), getNutrition(7)])
    recPref.value = pref
    recNutrition.value = nut
  } catch { /* 忽略 */ }
  recLoading.value = false
}

async function genRecommend() {
  if (recGenerating.value) return
  const p = recPref.value
  const n = recNutrition.value
  const prefDesc = (p.fav_cuisines && p.fav_cuisines.length) ? p.fav_cuisines.join('、') : '无明确偏好'
  const nutDesc = n.total_days > 0 ? `近${n.total_days}天日均热量${n.avg_calories}kcal、蛋白质${n.avg_protein}g` : '暂无饮食记录'
  const city = localStorage.getItem('nearby_city') || ''
  const content = `请根据我的饮食偏好（${prefDesc}）和近期摄入（${nutDesc}）${city ? `，我在${city}` : ''}，给我 3 条个性化的食物/菜谱推荐，每条用 **加粗菜名** 并说明为什么适合我（引用我的偏好或数据）。用 markdown 列表输出。`
  recGenerating.value = true
  recRecommend.value = ''
  const token = localStorage.getItem('token')
  try {
    const resp = await fetch('/api/chat/send', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Authorization: 'Bearer ' + token },
      body: JSON.stringify({ content, session_id: 'rec-panel' }),
    })
    const reader = resp.body.getReader()
    const decoder = new TextDecoder()
    let buf = '', ev = ''
    while (true) {
      const { done, value } = await reader.read()
      if (done) break
      buf += decoder.decode(value, { stream: true })
      const lines = buf.split('\n')
      buf = lines.pop() || ''
      for (const line of lines) {
        const t = line.trim()
        if (t.startsWith('event:')) ev = t.slice(6).trim()
        else if (t.startsWith('data:')) {
          try {
            const data = JSON.parse(t.slice(5).trim())
            if (ev === 'token') recRecommend.value += data.content || ''
          } catch { /* 忽略 */ }
        }
      }
    }
  } catch { recRecommend.value = '生成失败，请重试' }
  recGenerating.value = false
}

// ========== 定位城市（HTML5 GPS → 高德逆地理，与 TodayEat 一致） ==========
async function locateCity() {
  if (localStorage.getItem('nearby_city')) return
  try {
    if (!navigator.geolocation) return
    const pos = await new Promise((resolve, reject) => {
      navigator.geolocation.getCurrentPosition(resolve, reject, { timeout: 8000, maximumAge: 60000 })
    })
    const { longitude, latitude } = pos.coords
    const resp = await fetch(`https://restapi.amap.com/v3/geocode/regeo?location=${longitude},${latitude}&key=38b348fb67f2d42cb1fa0fe61301bc45`)
    const data = await resp.json()
    const city = data.regeocode?.addressComponent?.city || data.regeocode?.addressComponent?.province || ''
    const clean = String(city).replace(/市$|省$/, '')
    if (clean) localStorage.setItem('nearby_city', clean)
  } catch { /* 忽略 */ }
}

onMounted(() => {
  loadRecData()
  locateCity()
})

async function send() {
  const text = input.value.trim()
  if (!text || loading.value) return
  input.value = ''
  messages.value.push({ role: 'user', content: text })
  loading.value = true
  await nextTick()
  scrollBottom()

  // 注入用户所在城市（TodayEat 定位结果），供 AI 调用「附近美食」工具
  const _city = localStorage.getItem('nearby_city')
  const chatPayload = _city ? `我在${_city}。${text}` : text

  const token = localStorage.getItem('token')
  if (!token) {
    messages.value.push({ role: 'assistant', content: '请先登录后再使用 AI 助手。' })
    loading.value = false
    return
  }

  try {
    const response = await fetch('/api/chat/send', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({ content: chatPayload, session_id: currentSession.value }),
    })

    if (!response.ok) {
      const err = await response.json().catch(() => ({ detail: '请求失败' }))
      messages.value.push({ role: 'assistant', content: err.detail || '请求失败' })
      loading.value = false
      return
    }

    // 创建助手消息占位
    let assistantIdx = messages.value.length
    messages.value.push({ role: 'assistant', content: '' })
    let toolStatus = null

    // 读取 SSE 流
    const reader = response.body.getReader()
    const decoder = new TextDecoder()
    let buffer = ''
    let currentEvent = ''

    while (true) {
      const { done, value } = await reader.read()
      if (done) break

      buffer += decoder.decode(value, { stream: true })
      const lines = buffer.split('\n')
      buffer = lines.pop() || ''

      for (const line of lines) {
        if (line.startsWith('event: ')) {
          currentEvent = line.slice(7).trim()
        } else if (line.startsWith('data: ')) {
          try {
            const data = JSON.parse(line.slice(6))
            processSSEEvent(currentEvent, data, assistantIdx, toolStatus)
          } catch { /* ignore parse errors */ }
          currentEvent = ''
        }
      }
    }
  } catch (e) {
    messages.value.push({ role: 'assistant', content: '网络错误：' + e.message })
  } finally {
    loading.value = false
    await nextTick()
    scrollBottom()
  }
}

function processSSEEvent(eventType, data, assistantIdx, toolStatus) {
  switch (eventType) {
    case 'tool_start':
      messages.value[assistantIdx].tooling = true
      messages.value[assistantIdx].toolMsg = data.message
      break
    case 'tool_end':
      messages.value[assistantIdx].tooling = false
      messages.value[assistantIdx].toolMsg = data.result_preview
      break
    case 'token':
      messages.value[assistantIdx].content += data.content
      nextTick(() => scrollBottom())
      break
    case 'done':
      break
    case 'error':
      messages.value[assistantIdx].content += '\n\n[错误：' + data.message + ']'
      break
  }
}

function scrollBottom() {
  if (msgContainer.value) {
    msgContainer.value.scrollTop = msgContainer.value.scrollHeight
  }
}
</script>

<style scoped>
.chat-container {
  background: var(--color-bg-card);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-sm);
  overflow: hidden;
  max-width: 720px;
  margin: 0 auto;
}
.chat-messages {
  height: 400px;
  overflow-y: auto;
  padding: var(--spacing-lg);
}
.chat-welcome {
  text-align: center;
  padding: 40px 0;
}
.chat-welcome span {
  font-size: 48px;
  display: block;
  margin-bottom: var(--spacing-md);
}
.chat-welcome h3 {
  font-size: var(--font-size-lg);
  margin-bottom: var(--spacing-sm);
}
.quick-prompts {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--spacing-sm);
  padding: 0 var(--spacing-lg) var(--spacing-lg);
}
.quick-decision-panel {
  border-bottom: 1px solid var(--color-divider);
  padding-top: var(--spacing-md);
}
.quick-decision-title {
  font-size: var(--font-size-xs);
  color: var(--color-text-secondary);
  padding: 0 var(--spacing-lg);
  margin-bottom: var(--spacing-sm);
  font-weight: 500;
}
.quick-prompt-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 12px;
  background: var(--color-bg-warm);
  border: 1px solid var(--color-divider);
  border-radius: var(--radius-sm);
  cursor: pointer;
  font-size: var(--font-size-sm);
  color: var(--color-text);
  transition: all 0.2s;
}
.quick-prompt-btn:hover {
  border-color: var(--color-primary);
  background: rgba(217, 161, 91, 0.08);
}
.prompt-icon {
  font-size: 16px;
  flex-shrink: 0;
}
.prompt-label {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.chat-bubble {
  display: flex;
  gap: var(--spacing-sm);
  margin-bottom: var(--spacing-md);
  align-items: flex-start;
}
.chat-bubble--user {
  flex-direction: row-reverse;
}
.chat-bubble-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--color-bg-warm);
  font-size: 16px;
  flex-shrink: 0;
}
.chat-bubble-text {
  max-width: 75%;
  padding: 10px 14px;
  border-radius: var(--radius-md);
  font-size: var(--font-size-sm);
  line-height: 1.6;
  white-space: pre-wrap;
}
/* markdown 渲染内容样式 */
.chat-bubble-text.markdown {
  white-space: normal;
}
.chat-bubble-text.markdown p { margin: 0 0 8px; }
.chat-bubble-text.markdown ul, .chat-bubble-text.markdown ol { padding-left: 18px; margin: 4px 0; }
.chat-bubble-text.markdown li { margin: 2px 0; }
.chat-bubble-text.markdown h1, .chat-bubble-text.markdown h2, .chat-bubble-text.markdown h3 { font-size: 14px; margin: 8px 0 4px; }
.chat-bubble-text.markdown code { background: rgba(0,0,0,0.06); padding: 1px 4px; border-radius: 4px; font-size: 12px; }
.chat-bubble-text.markdown strong { font-weight: 700; }
.chat-bubble-text.markdown a { color: var(--color-primary); }
/* 为你推荐面板 */
.rec-panel {
  padding: var(--spacing-md);
  border-left: 3px solid var(--color-primary);
}
.rec-panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: var(--spacing-sm);
}
.rec-panel-title {
  font-weight: 600;
  font-size: var(--font-size-sm);
  color: var(--color-primary-dark);
}
.rec-prefs {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-bottom: 6px;
}
.rec-nutrition {
  color: var(--color-text-secondary);
  margin-bottom: 4px;
}
.rec-result {
  margin-top: 8px;
  padding: 10px 12px;
  background: var(--color-bg-warm);
  border-radius: var(--radius-sm);
  font-size: var(--font-size-sm);
  line-height: 1.7;
}
.rec-result p { margin: 0 0 6px; }
.rec-result ul, .rec-result ol { padding-left: 18px; margin: 4px 0; }
.rec-result li { margin: 3px 0; }
/* 记录我吃了 */
.eat-dishes {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 6px;
  margin-top: 6px;
}
.eat-dish-btn {
  cursor: pointer;
}
.chat-bubble--user .chat-bubble-text {
  background: rgba(217, 161, 91, 0.15);
  color: var(--color-text);
}
.chat-bubble--assistant .chat-bubble-text {
  background: var(--color-bg-warm);
  color: var(--color-text);
}
.chat-input-area {
  display: flex;
  gap: var(--spacing-sm);
  padding: var(--spacing-md);
  border-top: 1px solid var(--color-divider);
}
.chat-input-area .input {
  flex: 1;
}
.typing {
  opacity: 0.6;
}
.tool-indicator {
  font-size: var(--font-size-xs);
  padding: 4px 10px;
  border-radius: var(--radius-sm);
  margin-top: 4px;
}
.tool-indicator.tooling {
  background: rgba(217, 161, 91, 0.1);
  color: var(--color-primary-dark);
  animation: pulse 1.5s infinite;
}
.tool-indicator.tool-done {
  background: rgba(122, 166, 105, 0.1);
  color: var(--color-success);
}
@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.6; }
}
@media (max-width: 640px) {
  .chat-messages {
    height: 320px;
  }
}
</style>
