<template>
  <div class="page container page-section">
    <h2 class="section-title">今天吃什么</h2>

    <!-- Tab 切换 -->
    <div class="tab-bar">
      <button class="tab-btn" :class="{ active: tab === 'search' }" @click="tab = 'search'">
        &#x1F50D; 搜索浏览
      </button>
      <button class="tab-btn" :class="{ active: tab === 'decide' }" @click="tab = 'decide'">
        &#x1F3AF; 智能决策
      </button>
    </div>

    <!-- ====== Tab 1: 搜索浏览 ====== -->
    <div v-show="tab === 'search'">
      <!-- 搜索栏 -->
      <div class="search-bar">
        <input
          v-model="keyword"
          class="input"
          placeholder="搜索食物名称..."
          @keyup.enter="search"
        />
        <button class="btn btn-primary" @click="search">搜索</button>
      </div>

      <!-- 分类筛选 -->
      <div class="filter-tags">
        <button
          v-for="cat in categories"
          :key="cat.id"
          class="tag"
          :class="selectedCat === cat.id ? 'tag-primary' : 'tag-default'"
          style="cursor: pointer"
          @click="selectCategory(cat.id)"
        >
          {{ cat.name }}
        </button>
        <button class="tag tag-default" style="cursor: pointer" @click="selectCategory(null)">全部</button>
      </div>

      <!-- 决策快捷入口 -->
      <div class="decision-actions">
        <button class="btn btn-outline" @click="tab='decide'">&#x1F3B0; 随机转盘</button>
        <button class="btn btn-outline" @click="tab='decide'">&#x1F50D; 高级筛选</button>
      </div>

      <!-- 结果列表 -->
      <div v-if="loading" class="text-center text-muted" style="padding: 40px 0">搜索中...</div>
      <div v-else-if="foods.length === 0" class="text-center text-muted" style="padding: 40px 0">
        暂无结果，试试其他关键词
      </div>
      <div v-else class="food-grid">
        <div class="card food-card" v-for="food in foods" :key="food.id">
          <div class="food-card-img">&#x1F372;</div>
          <div class="food-card-body">
            <h3>{{ food.name }}</h3>
            <p class="text-sm text-secondary">{{ food.cuisine || '通用' }}</p>
            <div class="food-card-meta">
              <span class="tag tag-default">{{ food.category_name }}</span>
              <span class="text-xs text-muted">{{ food.calories_per_100g || 0 }} kcal/100g</span>
            </div>
            <button class="btn btn-primary btn-sm" style="width:100%; margin-top:10px" @click="openRecordModal(food)">
              我吃了这个
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- ====== Tab 2: 智能决策 ====== -->
    <div v-show="tab === 'decide'" class="decide-layout">
      <!-- 左栏：筛选条件 + AI推荐 -->
      <div class="decide-left">
        <!-- 筛选条件面板 FR-21 -->
        <div class="card decide-card">
          <h3 class="decide-card-title">&#x1F4CB; 筛选条件</h3>

          <div class="form-group">
            <label class="form-label">辣度</label>
            <div class="meal-btns">
              <button
                v-for="s in spicyOptions" :key="s.value"
                class="tag tag-sm"
                :class="filterForm.spicy === s.value ? 'tag-primary' : 'tag-default'"
                style="cursor: pointer"
                @click="filterForm.spicy = filterForm.spicy === s.value ? '' : s.value"
              >{{ s.label }}</button>
            </div>
          </div>

          <div class="form-group">
            <label class="form-label">菜系</label>
            <select v-model="filterForm.cuisine" class="input input-sm">
              <option value="">不限</option>
              <option v-for="c in allCuisineOptions" :key="c" :value="c">{{ c }}</option>
            </select>
          </div>

          <div class="form-group">
            <label class="form-label">热量上限 (kcal/100g)</label>
            <div class="range-row">
              <input v-model.number="filterForm.maxCal" class="input input-sm" type="number" min="0" max="1000" placeholder="不限" style="width:100px" />
              <span class="text-xs text-muted">{{ filterForm.maxCal ? '≤ ' + filterForm.maxCal + ' kcal' : '不设上限' }}</span>
            </div>
          </div>

          <div class="form-group">
            <label class="form-label">烹饪方式</label>
            <select v-model="filterForm.cookMethod" class="input input-sm">
              <option value="">不限</option>
              <option value="炒">炒</option>
              <option value="蒸">蒸</option>
              <option value="煮">煮</option>
              <option value="烤">烤</option>
              <option value="炸">炸</option>
              <option value="炖">炖</option>
              <option value="凉拌">凉拌</option>
            </select>
          </div>

          <button class="btn btn-primary" style="width:100%; margin-top:8px" @click="applyFilterFromDecide">
            &#x1F50D; 应用筛选到结果列表
          </button>
        </div>

        <!-- 附近美食 FR-24 -->
        <div class="card decide-card">
          <h3 class="decide-card-title">&#x1F4CD; 附近美食</h3>
          <p v-if="nearbyCity" class="text-sm text-secondary" style="margin-bottom:12px">
            你的城市：<strong>{{ nearbyCity }}</strong>
          </p>
          <p v-else class="text-sm text-muted" style="margin-bottom:12px">
            正在定位...
          </p>
          <button class="btn btn-outline btn-sm" style="width:100%" :disabled="nearbyLoading" @click="getNearbyRecommend">
            {{ nearbyLoading ? '查询中...' : '查看当地特色菜推荐' }}
          </button>
          <div v-if="nearbyResult" class="nearby-result-card" style="margin-top:10px">
            <div class="nearby-result-text">{{ nearbyResult }}</div>
          </div>
        </div>
      </div>

      <!-- 右栏：转盘 FR-22 -->
      <div class="decide-right">
        <div class="card decide-card" style="text-align:center">
          <h3 class="decide-card-title">&#x1F3B0; 决策转盘</h3>

          <!-- 自定义添加食物 -->
          <div class="wheel-add-row">
            <input
              v-model="customFoodInput"
              class="input input-sm"
              placeholder="输入菜名添加..."
              @keyup.enter="addCustomFood"
              style="flex:1"
            />
            <button class="btn btn-outline btn-sm" @click="addCustomFood" :disabled="!customFoodInput.trim()">
              添加
            </button>
          </div>

          <!-- 当前转盘选项标签 -->
          <div v-if="wheelItems.length" class="wheel-tags">
            <span
              v-for="(item, idx) in wheelItems"
              :key="idx"
              class="tag tag-sm"
              :class="idx < wheelItems.length - customCount ? 'tag-default' : 'tag-warm'"
              :style="{ cursor: 'pointer', borderLeft: '3px solid ' + (item.color || '#ccc') }"
              @click="removeWheelItem(idx)"
              :title="'点击移除: ' + item.label"
            >
              {{ item.label }}
            </span>
          </div>

          <!-- 转盘 -->
          <SpinWheel v-if="wheelItems.length >= 2" :items="wheelItems" @done="onWheelDone" />
          <div v-else class="text-muted text-sm" style="padding:30px 0">
            至少需要 2 个选项才能转动转盘。<br />
            从搜索结果中加载，或手动添加。
          </div>

          <!-- 转盘结果操作 -->
          <div v-if="wheelResult" class="modal-actions" style="justify-content: center; margin-top: 12px">
            <button class="btn btn-primary btn-sm" @click="searchWheelResult">
              &#x1F50D; 查看详情
            </button>
            <button class="btn btn-outline btn-sm" @click="wheelResult = null;">
              再转一次
            </button>
          </div>

          <!-- 加载选项按钮 -->
          <div class="wheel-actions" style="margin-top:12px">
            <button class="btn btn-outline btn-sm" @click="loadFoodsToWheel" :disabled="!foods.length">
              &#x1F4E5; 加载搜索结果 ({{ foods.length }}个)
            </button>
            <button class="btn btn-outline btn-sm" @click="clearWheel" :disabled="!wheelItems.length">
              &#x1F5D1; 清空
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- ====== 弹窗：饮食记录 ====== -->
    <div v-if="showModal" class="modal-overlay" @click.self="showModal = false">
      <div class="modal-content card">
        <h3>记录饮食：{{ selectedFood?.name }}</h3>
        <p class="text-sm text-secondary">每100g 约 {{ selectedFood?.calories_per_100g || 0 }} kcal</p>

        <div class="form-group">
          <label class="form-label">餐别</label>
          <div class="meal-btns">
            <button
              v-for="m in mealOptions" :key="m.value"
              class="tag" :class="recordForm.meal_type === m.value ? 'tag-primary' : 'tag-default'"
              style="cursor: pointer" @click="recordForm.meal_type = m.value"
            >{{ m.label }}</button>
          </div>
        </div>

        <div class="form-group">
          <label class="form-label">分量（克）</label>
          <input v-model.number="recordForm.quantity_g" class="input" type="number" min="10" max="5000" placeholder="例如 200" />
          <p class="text-xs text-muted" style="margin-top:4px">预估热量：{{ estimatedCal }} kcal</p>
        </div>

        <div class="modal-actions">
          <button class="btn btn-outline" @click="showModal = false">取消</button>
          <button class="btn btn-primary" :disabled="!canRecord || recording" @click="submitRecord">
            {{ recording ? '记录中...' : '确认记录' }}
          </button>
        </div>
        <p v-if="recordMsg" class="text-sm" :style="{ color: recordOk ? '#52c41a' : '#e74c3c', marginTop: '8px' }">
          {{ recordMsg }}
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'
import axios from 'axios'
import { createDietRecord } from '@/api/diet'
import SpinWheel from '@/components/today/SpinWheel.vue'

// ====== Tab ======
const tab = ref('search')

// ====== 搜索状态 ======
const keyword = ref('')
const selectedCat = ref(null)
const foods = ref([])
const categories = ref([])
const allCuisineOptions = ref([])
const loading = ref(false)

// ====== 筛选 FR-21 ======
const filterForm = ref({ spicy: '', cuisine: '', maxCal: null, cookMethod: '' })

const spicyOptions = [
  { value: 'none', label: '不辣' },
  { value: 'low', label: '微辣' },
  { value: 'medium', label: '中辣' },
  { value: 'high', label: '重辣' },
]

// ====== 转盘 FR-22 ======
const customFoodInput = ref('')
const wheelItems = ref([])
const wheelResult = ref(null)
const customCount = ref(0)

function addCustomFood() {
  const name = customFoodInput.value.trim()
  if (!name) return
  wheelItems.value.push({ label: name, color: '#D9A15B' })
  customCount.value++
  customFoodInput.value = ''
}

function removeWheelItem(idx) {
  // 移除自定义项时减少 customCount
  const item = wheelItems.value[idx]
  if (item.color === '#D9A15B') customCount.value--
  wheelItems.value.splice(idx, 1)
  wheelResult.value = null
}

function loadFoodsToWheel() {
  wheelResult.value = null
  customCount.value = 0
  wheelItems.value = foods.value.slice(0, 10).map(f => ({
    label: f.name,
    id: f.id,
    color: undefined, // 使用默认颜色
  }))
}

function clearWheel() {
  wheelItems.value = []
  wheelResult.value = null
  customCount.value = 0
}

// ====== 附近美食 FR-24 ======
const nearbyCity = ref('')
const nearbyLoading = ref(false)
const nearbyResult = ref('')

// 页面加载时 IP 定位（高德优先 → 返回中文城市名）
onMounted(async () => {
  const geoAPIs = [
    // 高德 IP 定位 — 返回纯中文城市名
    async () => {
      const r = await fetch(
        'https://restapi.amap.com/v3/ip?key=38b348fb67f2d42cb1fa0fe61301bc45',
        { signal: AbortSignal.timeout(5000) }
      )
      if (!r.ok) throw new Error('fail')
      const d = await r.json()
      const city = (d.city || d.province || '').replace(/市$|省$/, '')
      return city || ''
    },
    // api.ip.sb — 英文/拼音，仅作为备选
    async () => {
      const r = await fetch('https://api.ip.sb/geoip', { signal: AbortSignal.timeout(5000) })
      if (!r.ok) throw new Error('fail')
      const d = await r.json()
      return d.city || d.region || d.country || ''
    },
    // api.vore.top — 备选
    async () => {
      const r = await fetch('https://api.vore.top/api/IPdata', { signal: AbortSignal.timeout(5000) })
      if (!r.ok) throw new Error('fail')
      const d = await r.json()
      return (d.adcode?.o || d.ipdata?.city || '')
    },
  ]

  for (const fn of geoAPIs) {
    try {
      const city = await fn()
      if (city) {
        nearbyCity.value = city
        break
      }
    } catch { /* 尝试下一个 */ }
  }
})

async function getNearbyRecommend() {
  nearbyLoading.value = true
  nearbyResult.value = ''

  const token = localStorage.getItem('token')
  if (!token) {
    nearbyResult.value = '请先登录。'
    nearbyLoading.value = false
    return
  }

  const city = nearbyCity.value || '当前城市'
  const prompt = `我在${city}，请推荐3道当地特色菜，每道菜一行，格式：菜名 — 一句话理由。总共不超过100字。`

  try {
    const resp = await fetch('/api/chat/send', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({ content: prompt, session_id: 'today-nearby' }),
    })

    if (!resp.ok) {
      const err = await resp.json().catch(() => ({ detail: '请求失败' }))
      nearbyResult.value = err.detail || '查询失败'
      nearbyLoading.value = false
      return
    }

    // SSE 流式读取（event: / data: 两行配对）
    const reader = resp.body.getReader()
    const decoder = new TextDecoder()
    let buffer = ''
    let currentEvent = ''
    let fullText = ''

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
            if (currentEvent === 'token') {
              fullText += data.content
              nearbyResult.value = fullText
            }
          } catch { /* skip */ }
          currentEvent = ''
        }
      }
    }

    if (!nearbyResult.value) nearbyResult.value = fullText || '暂无结果，请稍后再试。'
  } catch {
    nearbyResult.value = '网络错误，请检查后端是否启动。'
  } finally {
    nearbyLoading.value = false
  }
}

function onWheelDone(item) {
  wheelResult.value = item
}

function searchWheelResult() {
  if (!wheelResult.value) return
  tab.value = 'search'
  keyword.value = wheelResult.value.label
  nextTick(() => search())
}

// ====== 搜索 & 分类 ======
onMounted(async () => {
  try {
    const res = await axios.get('/api/foods/categories')
    categories.value = res.data
    allCuisineOptions.value = res.data.map(c => c.name)
  } catch { /* ignore */ }
  search()
})

async function search() {
  loading.value = true
  try {
    const params = { page_size: 50 }
    if (keyword.value) params.keyword = keyword.value
    if (selectedCat.value) params.category_id = selectedCat.value
    if (filterForm.value.cuisine) params.cuisine = filterForm.value.cuisine
    const res = await axios.get('/api/foods', { params })
    let items = res.data.items || []

    if (filterForm.value.spicy) {
      items = items.filter(f => {
        try {
          const tags = typeof f.tags === 'string' ? JSON.parse(f.tags) : (f.tags || {})
          return tags.spicy === filterForm.value.spicy
        } catch { return true }
      })
    }
    if (filterForm.value.maxCal) {
      items = items.filter(f => (f.calories_per_100g || 9999) <= filterForm.value.maxCal)
    }
    if (filterForm.value.cookMethod) {
      items = items.filter(f => {
        try {
          const tags = typeof f.tags === 'string' ? JSON.parse(f.tags) : (f.tags || {})
          return tags.cook_method === filterForm.value.cookMethod
        } catch { return true }
      })
    }

    foods.value = items
  } catch {
    foods.value = []
  } finally {
    loading.value = false
  }
}

function selectCategory(id) {
  selectedCat.value = id === selectedCat.value ? null : id
  search()
}

function applyFilterFromDecide() {
  tab.value = 'search'
  search()
}

// ====== 饮食记录 ======
const showModal = ref(false)
const selectedFood = ref(null)
const recording = ref(false)
const recordMsg = ref('')
const recordOk = ref(false)

const mealOptions = [
  { value: 'breakfast', label: '早餐' },
  { value: 'lunch', label: '午餐' },
  { value: 'dinner', label: '晚餐' },
  { value: 'snack', label: '零食' },
]

const recordForm = ref({ meal_type: 'lunch', quantity_g: 200 })

const estimatedCal = computed(() => {
  if (!selectedFood.value) return 0
  const cal = selectedFood.value.calories_per_100g || 0
  return Math.round(cal * recordForm.value.quantity_g / 100)
})

const canRecord = computed(() => recordForm.value.quantity_g >= 10 && recordForm.value.meal_type)

function openRecordModal(food) {
  selectedFood.value = food
  recordForm.value = { meal_type: 'lunch', quantity_g: 200 }
  recordMsg.value = ''
  recordOk.value = false
  showModal.value = true
}

async function submitRecord() {
  if (!canRecord.value || !selectedFood.value) return
  recording.value = true
  recordMsg.value = ''
  try {
    await createDietRecord({
      food_id: selectedFood.value.id,
      meal_type: recordForm.value.meal_type,
      quantity_g: recordForm.value.quantity_g,
    })
    recordMsg.value = `已记录：${selectedFood.value.name} ${recordForm.value.quantity_g}g`
    recordOk.value = true
    setTimeout(() => { showModal.value = false }, 1500)
  } catch (e) {
    recordMsg.value = e?.message || '记录失败，请重试'
    recordOk.value = false
  } finally {
    recording.value = false
  }
}
</script>

<style scoped>
/* ====== Tab 栏 ====== */
.tab-bar {
  display: flex;
  gap: 0;
  margin-bottom: var(--spacing-lg);
  border-bottom: 2px solid var(--color-divider);
}
.tab-btn {
  padding: 10px 24px;
  background: none;
  border: none;
  border-bottom: 2px solid transparent;
  margin-bottom: -2px;
  font-size: 15px;
  font-weight: 500;
  color: var(--color-text-secondary);
  cursor: pointer;
  transition: color 0.2s, border-color 0.2s;
}
.tab-btn.active {
  color: var(--color-primary-dark);
  border-bottom-color: var(--color-primary);
}
.tab-btn:hover:not(.active) {
  color: var(--color-text);
}

/* ====== 搜索栏 ====== */
.search-bar {
  display: flex;
  gap: var(--spacing-sm);
  margin-bottom: var(--spacing-md);
}
.search-bar .input { flex: 1; }
.filter-tags {
  display: flex;
  gap: var(--spacing-sm);
  flex-wrap: wrap;
  margin-bottom: var(--spacing-md);
}
.decision-actions {
  display: flex;
  gap: var(--spacing-sm);
  flex-wrap: wrap;
  margin-bottom: var(--spacing-lg);
  padding-bottom: var(--spacing-lg);
  border-bottom: 1px solid var(--color-divider);
}
.food-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: var(--spacing-md);
}
.food-card-img {
  height: 120px;
  background: var(--color-bg-warm);
  border-radius: var(--radius-md) var(--radius-md) 0 0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 36px;
}
.food-card-body { padding: var(--spacing-md); }
.food-card-body h3 {
  font-size: var(--font-size-base);
  font-weight: 600;
  margin-bottom: 2px;
}
.food-card-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: var(--spacing-sm);
}
.btn-sm { padding: 6px 14px; font-size: 13px; }

/* ====== 决策布局 ====== */
.decide-layout {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--spacing-lg);
  align-items: start;
}
.decide-left, .decide-right {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
}
.decide-card {
  padding: var(--spacing-md) var(--spacing-lg);
}
.decide-card-title {
  font-size: 15px;
  font-weight: 600;
  margin-bottom: var(--spacing-sm);
  color: var(--color-text);
}

/* ====== 表单增强 ====== */
.form-group { margin-top: var(--spacing-md); }
.form-label {
  display: block;
  font-size: 13px;
  font-weight: 500;
  margin-bottom: 4px;
  color: var(--color-text-secondary);
}
.input-sm { padding: 6px 10px; font-size: 13px; }
.meal-btns { display: flex; gap: var(--spacing-sm); flex-wrap: wrap; }
.tag-sm { padding: 4px 10px; font-size: 12px; }
.range-row { display: flex; align-items: center; gap: var(--spacing-sm); }

/* ====== 转盘 ====== */
.wheel-add-row {
  display: flex;
  gap: var(--spacing-sm);
  margin-bottom: var(--spacing-sm);
}
.wheel-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  margin-bottom: var(--spacing-sm);
  justify-content: center;
}
.tag-warm {
  background: #FFF3E0;
  color: var(--color-primary-dark);
  border-color: var(--color-primary-light);
}
.wheel-actions {
  display: flex;
  gap: var(--spacing-sm);
  justify-content: center;
}

/* ====== AI 结果 ====== */
.ai-result-card {
  margin-top: var(--spacing-md);
  padding: var(--spacing-sm);
  background: var(--color-bg-warm);
  border-radius: var(--radius-sm);
  border-left: 3px solid var(--color-primary);
}
.ai-result-text {
  font-size: 13px;
  line-height: 1.7;
  color: var(--color-text);
  white-space: pre-wrap;
}

/* ====== 弹窗 ====== */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}
.modal-content {
  width: 400px;
  max-width: 90vw;
  padding: var(--spacing-lg);
}
.modal-content h3 { margin-bottom: 4px; font-size: var(--font-size-lg); }
.modal-actions {
  display: flex;
  gap: var(--spacing-sm);
  justify-content: flex-end;
  margin-top: var(--spacing-lg);
}

@media (max-width: 768px) {
  .decide-layout {
    grid-template-columns: 1fr;
  }
}
@media (max-width: 640px) {
  .food-grid { grid-template-columns: 1fr 1fr; }
}
</style>
