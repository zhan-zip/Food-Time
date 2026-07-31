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

          <!-- ECharts 饼图 -->
          <div ref="pieDom" style="width:100%;height:260px"></div>

          <!-- ECharts 折线图 -->
          <div ref="lineDom" style="width:100%;height:260px; margin-top:16px"></div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, nextTick, watch } from 'vue'
import * as echarts from 'echarts'
import { getExpenseRecords, createExpenseRecord, deleteExpenseRecord, getExpenseStats, ocrExpense } from '@/api/expense'

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
const pieDom = ref(null)
const lineDom = ref(null)
let pieChart = null
let lineChart = null

onMounted(() => {
  loadRecords()
  loadStats('month')
  window.addEventListener('resize', onResize)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', onResize)
  pieChart?.dispose()
  lineChart?.dispose()
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
    renderCharts()
  } catch { /* ignore */ }
}

function onResize() {
  pieChart?.resize()
  lineChart?.resize()
}

const PIE_COLORS = ['#D9A15B', '#52c41a', '#3498db', '#e74c3c', '#9b59b6']

function renderCharts() {
  // 饼图
  const pieEl = pieDom.value
  if (pieEl) {
    if (!pieChart) pieChart = echarts.init(pieEl)
    const entries = Object.entries(stats.value.categories || {})
    pieChart.setOption({
      color: PIE_COLORS,
      tooltip: { trigger: 'item', formatter: '{b}: ¥{c} ({d}%)' },
      series: [{
        type: 'pie',
        radius: ['40%', '70%'],
        center: ['50%', '50%'],
        label: { show: true, formatter: '{b}\n¥{c}', fontSize: 12 },
        data: entries.map(([name, val]) => ({ name, value: val.amount })),
      }],
    }, true)
  }

  // 折线图
  const lineEl = lineDom.value
  if (lineEl) {
    if (!lineChart) lineChart = echarts.init(lineEl)
    const points = stats.value.daily_trend || []
    lineChart.setOption({
      color: ['#D9A15B'],
      tooltip: { trigger: 'axis' },
      grid: { left: 50, right: 20, top: 20, bottom: 30 },
      xAxis: {
        type: 'category',
        data: points.map(p => p.date.slice(5)),
        axisLabel: { fontSize: 10 },
      },
      yAxis: {
        type: 'value',
        axisLabel: { fontSize: 10, formatter: '¥{value}' },
      },
      series: [{
        type: 'line',
        data: points.map(p => p.amount),
        smooth: true,
        symbol: 'circle',
        symbolSize: 6,
        label: { show: true, formatter: '¥{c}', fontSize: 10, position: 'top' },
      }],
    }, true)
  }
}

async function onOcrUpload(e) {
  const file = e.target.files?.[0]
  if (!file) return
  ocrLoading.value = true
  ocrMsg.value = ''
  ocrOk.value = false
  const reader = new FileReader()
  reader.onload = async () => {
    const dataUrl = reader.result
    // 提取纯 base64（去掉 data:image/...;base64, 前缀）
    const base64 = dataUrl.split(',')[1] || dataUrl
    try {
      const res = await ocrExpense(base64)
      if (!res.success) {
        ocrMsg.value = res.message || 'OCR 识别失败，请手动录入'
        return
      }
      // 填入表单，让用户核对修改后再手动点"记录"保存
      form.value.amount = res.amount
      form.value.category = res.category
      form.value.description = res.description
      ocrMsg.value = `已识别 ¥${res.amount} - ${res.category_label}，已填入上方表单，请核对后点"记录"`
      ocrOk.value = true
    } catch (err) {
      ocrMsg.value = err?.response?.data?.message || err.message || 'OCR 识别失败，请手动录入'
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
