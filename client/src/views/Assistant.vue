<template>
  <div class="page container page-section">
    <h2 class="section-title">AI 助手</h2>

    <div class="chat-container">
      <div class="chat-messages" ref="msgContainer">
        <div v-if="messages.length === 0" class="chat-welcome">
          <span>&#x1F916;</span>
          <h3>你好，我是食光记 AI 助手</h3>
          <p class="text-secondary">可以帮你：搜索食物、推荐食谱、分析营养、查看账单</p>
          <div class="quick-prompts">
            <button v-for="p in prompts" :key="p" class="tag tag-default" style="cursor: pointer" @click="sendPrompt(p)">
              {{ p }}
            </button>
          </div>
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
            <div class="chat-bubble-text">{{ msg.content }}</div>
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
      AI 对话（SSE 流式 + Tool Calling）将在 P1 阶段接入 DeepSeek API
    </p>
  </div>
</template>

<script setup>
import { ref, nextTick } from 'vue'

const input = ref('')
const loading = ref(false)
const messages = ref([])
const msgContainer = ref(null)
const currentSession = ref('default')

const prompts = ['今天吃什么好？', '推荐一个低热量的菜', '我最近吃得太油了怎么办', '帮我分析一下我的营养摄入']

function sendPrompt(p) {
  input.value = p
  send()
}

async function send() {
  const text = input.value.trim()
  if (!text || loading.value) return
  input.value = ''
  messages.value.push({ role: 'user', content: text })
  loading.value = true
  await nextTick()
  scrollBottom()

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
      body: JSON.stringify({ content: text, session_id: currentSession.value }),
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
  display: flex;
  gap: var(--spacing-sm);
  flex-wrap: wrap;
  justify-content: center;
  margin-top: var(--spacing-lg);
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
