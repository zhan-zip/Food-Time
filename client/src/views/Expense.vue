<template>
  <div class="page container page-section">
    <h2 class="section-title">记账</h2>

    <div class="expense-layout">
      <!-- 左侧：录入 + 记录列表 -->
      <div class="expense-left">
        <!-- 输入账单 -->
        <div class="card">
          <h3 class="card-title">输入账单</h3>
          <div class="form-group">
            <label class="form-label">金额</label>
            <input v-model.number="form.amount" class="input" type="number" step="0.01" min="0.01" placeholder="0.00" />
          </div>
          <div class="form-group">
            <label class="form-label">分类</label>
            <div class="cat-btns">
              <button
                v-for="c in categories"
                :key="c.value"
                class="tag"
                :class="form.category === c.value ? 'tag-primary' : 'tag-default'"
                style="cursor: pointer"
                @click="form.category = c.value"
              >
                {{ c.label }}
              </button>
            </div>
          </div>
          <div class="form-group">
            <label class="form-label">备注</label>
            <input v-model="form.description" class="input" placeholder="例如：午餐外卖" />
          </div>
          <button class="btn btn-primary" style="width:100%" :disabled="!canSubmit || submitting" @click="submitExpense">
            {{ submitting ? '记录中...' : '记录' }}
          </button>
          <p v-if="msg" class="text-sm" :style="{ color: msgOk ? '#52c41a' : '#e74c3c', marginTop: '8px' }">{{ msg }}</p>
        </div>

        <!-- 识别账单截图 -->
        <div class="card" style="margin-top: var(--spacing-md);">
          <h3 class="card-title">识别账单截图</h3>
          <div class="ocr-zone">
            <input
              ref="ocrInput"
              type="file"
              accept="image/*"
              style="display: none"
              @change="onOcrUpload"
            />
            <div v-if="ocrLoading" class="text-center text-muted text-sm" style="padding: 30px 0">
              AI 识别中...
            </div>
            <div v-else-if="!ocrMsg" class="text-center text-muted text-sm" style="padding: 30px 0; cursor: pointer" @click="$refs.ocrInput.click()">
              点击上传小票/支付截图，AI 自动识别金额和分类
            </div>
            <div v-else class="text-sm" :style="{ padding: '16px', color: ocrOk ? '#52c41a' : '#e74c3c' }">
              {{ ocrMsg }}
            </div>
          </div>
        </div>

        <!-- 最近记录 -->
        <div class="card" style="margin-top: var(--spacing-md);">
          <h3 class="card-title">最近记录</h3>
          <div v-if="records.length === 0" class="text-muted text-sm">暂无记录</div>
          <div v-else class="record-list">
            <div class="record-item" v-for="r in records" :key="r.id">
              <span class="tag tag-default">{{ catLabel(r.category) }}</span>
              <span class="record-desc">{{ r.description || '-' }}</span>
              <span class="record-date text-sm text-muted">{{ r.record_date }}</span>
              <span class="record-amount">¥{{ r.amount }}</span>
              <button class="btn-close" @click="deleteRecord(r.id)" title="删除">&times;</button>
            </div>
          </div>
        </div>
      </div>

      <!-- 右侧：统计图表 -->
      <div class="expense-right">
        <div class="card">
          <h3 class="card-title">消费统计</h3>
          <div style="margin-bottom: 12px">
            <button
              v-for="p in periods"
              :key="p.value"
              class="tag"
              :class="selectedPeriod === p.value ? 'tag-primary' : 'tag-default'"
              style="cursor: pointer"
              @click="loadStats(p.value)"
            >
              {{ p.label }}
            </button>
          </div>
          <p class="text-sm" style="margin-bottom: 12px">本月合计：<strong>¥{{ stats.total_month }}</strong></p>

          <!-- 饼图 -->
          <canvas ref="pieCanvas" width="280" height="200" class="chart-canvas"></canvas>

          <!-- 折线图 -->
          <canvas ref="lineCanvas" width="560" height="200" class="chart-canvas" style="margin-top: 16px"></canvas>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick, watch } from 'vue'
import { getExpenseRecords, createExpenseRecord, deleteExpenseRecord, getExpenseStats } from '@/api/expense'

// Qwen VL 配置（通过 Vite 代理转发，消除 CORS）
const QWEN_API_KEY = 'sk-eb7e2d8c69e54053ae167d010e00d08b'
const QWEN_BASE_URL = '/qwen/chat/completions'  // Vite 代理 → dashscope.aliyuncs.com

// 表单
const form = ref({ amount: null, category: 'food', description: '' })
const submitting = ref(false)
const msg = ref('')
const msgOk = ref(false)

// OCR
const ocrInput = ref(null)
const ocrLoading = ref(false)
const ocrMsg = ref('')
const ocrOk = ref(false)

const categories = [
  { value: 'food', label: '餐饮' },
  { value: 'delivery', label: '外卖' },
  { value: 'snack', label: '零食' },
  { value: 'drink', label: '饮品' },
  { value: 'grocery', label: '食材采购' },
]

const catMap = {}
categories.forEach(c => { catMap[c.value] = c.label })
function catLabel(v) { return catMap[v] || v }

const canSubmit = computed(() => form.value.amount > 0 && form.value.category)

// 记录列表
const records = ref([])

// 统计
const selectedPeriod = ref('month')
const periods = [
  { value: 'week', label: '本周' },
  { value: 'month', label: '本月' },
]
const stats = ref({ total_month: 0, categories: {}, daily_trend: [] })
const pieCanvas = ref(null)
const lineCanvas = ref(null)

onMounted(() => {
  loadRecords()
  loadStats('month')
})

async function submitExpense() {
  if (!canSubmit.value) return
  submitting.value = true
  msg.value = ''
  try {
    await createExpenseRecord({
      amount: form.value.amount,
      category: form.value.category,
      description: form.value.description || null,
    })
    msg.value = `已记录：¥${form.value.amount}`
    msgOk.value = true
    form.value = { amount: null, category: 'food', description: '' }
    setTimeout(() => { msg.value = '' }, 2000)
    loadRecords()
    loadStats(selectedPeriod.value)
  } catch (e) {
    msg.value = e?.response?.data?.detail || '记录失败'
    msgOk.value = false
  } finally {
    submitting.value = false
  }
}

async function loadRecords() {
  try {
    const res = await getExpenseRecords({ page_size: 10 })
    records.value = res.items
  } catch { /* ignore */ }
}

async function deleteRecord(id) {
  try {
    await deleteExpenseRecord(id)
    loadRecords()
    loadStats(selectedPeriod.value)
  } catch { /* ignore */ }
}

async function loadStats(period) {
  selectedPeriod.value = period
  try {
    const res = await getExpenseStats(period)
    stats.value = res
    await nextTick()
    drawPieChart()
    drawLineChart()
  } catch { /* ignore */ }
}

function drawPieChart() {
  const canvas = pieCanvas.value
  if (!canvas) return
  const ctx = canvas.getContext('2d')
  const W = canvas.width
  const H = canvas.height
  const cx = W / 2
  const cy = H / 2
  const r = Math.min(cx, cy) - 16

  ctx.clearRect(0, 0, W, H)

  const entries = Object.entries(stats.value.categories || {})
  if (!entries.length) {
    ctx.fillStyle = '#999'
    ctx.font = '13px sans-serif'
    ctx.textAlign = 'center'
    ctx.fillText('暂无数据', cx, cy)
    return
  }

  const pieColors = ['#D9A15B', '#52c41a', '#3498db', '#e74c3c', '#9b59b6']
  let total = entries.reduce((s, [, v]) => s + v.amount, 0)
  if (total === 0) total = 1

  let startAngle = -Math.PI / 2
  entries.forEach(([name, val], i) => {
    const sliceAngle = (val.amount / total) * Math.PI * 2
    ctx.beginPath()
    ctx.moveTo(cx, cy)
    ctx.arc(cx, cy, r, startAngle, startAngle + sliceAngle)
    ctx.closePath()
    ctx.fillStyle = pieColors[i % pieColors.length]
    ctx.fill()

    // 标签
    const mid = startAngle + sliceAngle / 2
    const lx = cx + Math.cos(mid) * (r * 0.65)
    const ly = cy + Math.sin(mid) * (r * 0.65)
    ctx.fillStyle = '#fff'
    ctx.font = 'bold 11px sans-serif'
    ctx.textAlign = 'center'
    ctx.fillText(name, lx, ly - 4)
    ctx.fillText('¥' + val.amount, lx, ly + 12)

    startAngle += sliceAngle
  })
}

function drawLineChart() {
  const canvas = lineCanvas.value
  if (!canvas) return
  const ctx = canvas.getContext('2d')
  const W = canvas.width
  const H = canvas.height
  const pad = { top: 24, right: 20, bottom: 36, left: 54 }
  const pw = W - pad.left - pad.right
  const ph = H - pad.top - pad.bottom

  ctx.clearRect(0, 0, W, H)

  const points = stats.value.daily_trend || []
  if (!points.length) {
    ctx.fillStyle = '#999'
    ctx.font = '13px sans-serif'
    ctx.textAlign = 'center'
    ctx.fillText('暂无数据', W / 2, H / 2)
    return
  }

  let maxVal = Math.max(...points.map(p => p.amount), 1)
  maxVal = Math.ceil(maxVal / 50) * 50 || 50

  // 网格线
  ctx.strokeStyle = '#eee'
  ctx.lineWidth = 1
  ctx.font = '10px sans-serif'
  ctx.fillStyle = '#999'
  ctx.textAlign = 'right'
  for (let i = 0; i <= 4; i++) {
    const y = pad.top + ph * (1 - i / 4)
    ctx.beginPath()
    ctx.moveTo(pad.left, y)
    ctx.lineTo(W - pad.right, y)
    ctx.stroke()
    ctx.fillText(Math.round(maxVal * i / 4), pad.left - 8, y + 4)
  }

  // 折线
  ctx.strokeStyle = '#D9A15B'
  ctx.lineWidth = 2.5
  ctx.lineJoin = 'round'
  ctx.beginPath()

  const stepX = points.length > 1 ? pw / (points.length - 1) : pw / 2
  const px = points.length === 1 ? pad.left + pw / 2 : pad.left

  points.forEach((p, i) => {
    const x = px + stepX * i
    const y = pad.top + ph - (p.amount / maxVal) * ph
    if (i === 0) ctx.moveTo(x, y)
    else ctx.lineTo(x, y)
  })
  ctx.stroke()

  // 数据点
  ctx.fillStyle = '#D9A15B'
  points.forEach((p, i) => {
    const x = px + stepX * i
    const y = pad.top + ph - (p.amount / maxVal) * ph
    ctx.beginPath()
    ctx.arc(x, y, 4, 0, Math.PI * 2)
    ctx.fill()

    // 金额标签
    ctx.fillStyle = '#333'
    ctx.font = '10px sans-serif'
    ctx.textAlign = 'center'
    ctx.fillText('¥' + p.amount, x, y - 10)
    ctx.fillStyle = '#D9A15B'
  })

  // 日期标签
  ctx.fillStyle = '#999'
  ctx.font = '10px sans-serif'
  ctx.textAlign = 'center'
  points.forEach((p, i) => {
    const x = px + stepX * i
    ctx.fillText(p.date.slice(5), x, H - pad.bottom + 22)
  })
}

function onOcrUpload(e) {
  const file = e.target.files?.[0]
  if (!file) return
  ocrLoading.value = true
  ocrMsg.value = ''
  ocrOk.value = false
  const reader = new FileReader()
  reader.onload = async () => {
    const dataUrl = reader.result  // 完整 data:image/...;base64,...
    try {
      // 浏览器直连 Qwen VL API
      const qwenResp = await fetch(QWEN_BASE_URL, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${QWEN_API_KEY}`,
        },
        body: JSON.stringify({
          model: 'qwen-vl-max',
          messages: [{
            role: 'user',
            content: [
              { type: 'image_url', image_url: { url: dataUrl } },
              {
                type: 'text',
                text:
                  '你是一个饮食消费记账助手。请分析这张账单/小票/支付截图中的消费信息，' +
                  '以JSON格式返回：\n' +
                  '{"amount": 金额数字, "category": "分类", "description": "简要描述"}\n\n' +
                  '分类只能是: food(餐饮), delivery(外卖), snack(零食), drink(饮品), grocery(食材采购)\n' +
                  '如果无法识别，amount返回0。description用中文简要描述（不超过20字）。' +
                  '只返回JSON，不要包含其他文字。',
              },
            ],
          }],
          max_tokens: 300,
          temperature: 0.1,
        }),
      })

      if (!qwenResp.ok) {
        const errData = await qwenResp.json().catch(() => ({}))
        throw new Error(errData.error?.message || `API 错误 ${qwenResp.status}`)
      }

      const data = await qwenResp.json()
      const content = data.choices?.[0]?.message?.content || ''

      // 解析 JSON（可能被 markdown 包裹）
      let result
      try {
        result = JSON.parse(content)
      } catch {
        const match = content.match(/\{[\s\S]*\}/)
        if (match) result = JSON.parse(match[0])
        else throw new Error('无法解析识别结果')
      }

      const amount = parseFloat(result.amount) || 0
      const category = ['food', 'delivery', 'snack', 'drink', 'grocery'].includes(result.category)
        ? result.category
        : 'food'
      const description = (result.description || '').slice(0, 200)

      if (amount <= 0) {
        ocrMsg.value = '未能识别有效金额，请检查图片或手动录入'
        return
      }

      // 填入表单，让用户核对修改后再手动点"记录"保存
      form.value.amount = amount
      form.value.category = category
      form.value.description = description
      const catLabels = { food: '餐饮', delivery: '外卖', snack: '零食', drink: '饮品', grocery: '食材采购' }
      ocrMsg.value = `已识别 ¥${amount} - ${catLabels[category] || category}，已填入上方表单，请核对后点"记录"`
      ocrOk.value = true
    } catch (err) {
      ocrMsg.value = err.message || 'OCR 识别失败，请手动录入'
      ocrOk.value = false
    } finally {
      ocrLoading.value = false
      if (ocrInput.value) ocrInput.value.value = ''
    }
  }
  reader.readAsDataURL(file)
}
</script>

<style scoped>
.expense-layout {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--spacing-lg);
  align-items: start;
}
.card-title {
  font-size: var(--font-size-base);
  font-weight: 600;
  margin-bottom: var(--spacing-md);
}
.form-group {
  margin-bottom: var(--spacing-sm);
}
.form-label {
  display: block;
  font-size: 13px;
  font-weight: 500;
  margin-bottom: 4px;
  color: var(--color-text-secondary);
}
.cat-btns {
  display: flex;
  gap: var(--spacing-xs);
  flex-wrap: wrap;
}

/* 记录列表 */
.record-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.record-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 0;
  border-bottom: 1px solid var(--color-divider);
}
.record-item:last-child { border-bottom: none; }
.record-desc { flex: 1; font-size: 13px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.record-amount { font-weight: 600; font-size: 14px; color: var(--color-primary); white-space: nowrap; }
.btn-close {
  border: none;
  background: none;
  color: #ccc;
  font-size: 16px;
  cursor: pointer;
  padding: 0 4px;
}
.btn-close:hover { color: #e74c3c; }

/* 图表 */
.chart-canvas {
  width: 100%;
  max-width: 560px;
  height: auto;
  display: block;
  margin: 0 auto;
}

/* OCR */
.ocr-zone {
  border: 2px dashed var(--color-divider);
  border-radius: var(--radius-md);
  min-height: 80px;
  display: flex;
  align-items: center;
  justify-content: center;
}

@media (max-width: 768px) {
  .expense-layout {
    grid-template-columns: 1fr;
  }
}
</style>
