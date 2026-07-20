<template>
  <div class="chat-page">
    <van-nav-bar title="AI 饮食助手" fixed />

    <div class="chat-content">
      <div class="chat-messages" ref="msgContainer">
        <div v-if="messages.length === 0" class="chat-empty">
          <van-icon name="chat-o" size="48" color="#ccc" />
          <p>问我任何关于饮食的问题吧！</p>
          <div class="quick-prompts">
            <van-tag
              v-for="prompt in quickPrompts"
              :key="prompt"
              type="primary"
              size="medium"
              style="margin: 4px; cursor: pointer;"
              @click="sendMessage(prompt)"
            >
              {{ prompt }}
            </van-tag>
          </div>
        </div>

        <div
          v-for="(msg, idx) in messages"
          :key="idx"
          :class="['msg-item', msg.role === 'user' ? 'msg-user' : 'msg-ai']"
        >
          <div class="msg-bubble">{{ msg.content }}</div>
        </div>

        <div v-if="streaming" class="msg-item msg-ai">
          <div class="msg-bubble">{{ streamText }}<span class="cursor">|</span></div>
        </div>
      </div>

      <div class="chat-input-area">
        <van-field
          v-model="inputText"
          placeholder="输入消息..."
          :disabled="streaming"
          @keypress.enter="sendMessage(inputText)"
        >
          <template #button>
            <van-button
              size="small"
              type="primary"
              :loading="streaming"
              @click="sendMessage(inputText)"
            >
              发送
            </van-button>
          </template>
        </van-field>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick } from 'vue'
import { showToast } from 'vant'

const messages = ref([])
const inputText = ref('')
const streaming = ref(false)
const streamText = ref('')
const msgContainer = ref(null)

const quickPrompts = [
  '帮我选个晚饭',
  '今天吃什么好',
  '推荐几个低卡食物',
]

async function sendMessage(text) {
  const msg = text || inputText.value.trim()
  if (!msg || streaming.value) return
  inputText.value = ''

  messages.value.push({ role: 'user', content: msg })
  await scrollToBottom()

  // P0 阶段：使用普通 HTTP 发送消息（SSE 在 P1 实现）
  // 这里先用一个简单的 mock 展示界面
  streaming.value = true
  streamText.value = ''

  try {
    const token = localStorage.getItem('token')
    const response = await fetch('/api/chat/stream', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
      },
      body: JSON.stringify({
        message: msg,
        session_id: 'default',
      }),
    })

    if (response.ok) {
      const reader = response.body.getReader()
      const decoder = new TextDecoder()
      let fullText = ''

      while (true) {
        const { done, value } = await reader.read()
        if (done) break
        const chunk = decoder.decode(value, { stream: true })
        // 解析 SSE 格式
        const lines = chunk.split('\n')
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = line.slice(6)
            if (data === '[DONE]') continue
            try {
              const parsed = JSON.parse(data)
              if (parsed.content) {
                fullText += parsed.content
                streamText.value = fullText
              }
            } catch {
              fullText += data
              streamText.value = fullText
            }
          }
        }
      }
      if (fullText) {
        messages.value.push({ role: 'assistant', content: fullText })
      }
    } else {
      showToast('AI 服务暂未接入')
    }
  } catch {
    // P0 阶段 AI 对话路由为空，先显示占位提示
    messages.value.push({
      role: 'assistant',
      content: 'AI 对话功能将在 P1 阶段实现，敬请期待！',
    })
  }

  streaming.value = false
  streamText.value = ''
  await scrollToBottom()
}

async function scrollToBottom() {
  await nextTick()
  if (msgContainer.value) {
    msgContainer.value.scrollTop = msgContainer.value.scrollHeight
  }
}
</script>

<style scoped>
.chat-page {
  padding-top: 46px;
}
.chat-content {
  display: flex;
  flex-direction: column;
  height: calc(100vh - 46px - 50px);
}
.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 12px;
}
.chat-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #999;
}
.msg-item {
  margin-bottom: 12px;
  display: flex;
}
.msg-user {
  justify-content: flex-end;
}
.msg-user .msg-bubble {
  background: #4CAF50;
  color: #fff;
}
.msg-ai .msg-bubble {
  background: #fff;
  color: #333;
}
.msg-bubble {
  max-width: 80%;
  padding: 10px 14px;
  border-radius: 12px;
  font-size: 15px;
  line-height: 1.5;
  word-break: break-all;
}
.cursor {
  animation: blink 1s infinite;
}
@keyframes blink {
  0%, 50% { opacity: 1; }
  51%, 100% { opacity: 0; }
}
.chat-input-area {
  background: #fff;
  border-top: 1px solid #eee;
}
.quick-prompts {
  margin-top: 16px;
  text-align: center;
}
</style>
