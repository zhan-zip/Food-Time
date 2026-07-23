<template>
  <div class="page container page-section">
    <h2 class="section-title">今天吃什么</h2>

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
      <button
        class="tag tag-default"
        style="cursor: pointer"
        @click="selectCategory(null)"
      >
        全部
      </button>
    </div>

    <!-- 决策入口 -->
    <div class="decision-actions">
      <button class="btn btn-outline" @click="openRoulette">&#x1F3B0; 随机转盘</button>
      <button class="btn btn-outline" @click="openFilter">&#x1F50D; 高级筛选</button>
      <router-link to="/assistant" class="btn btn-primary">&#x1F916; AI 帮我选</router-link>
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

    <!-- 随机转盘弹窗 -->
    <div v-if="showRoulette" class="modal-overlay" @click.self="showRoulette = false">
      <div class="modal-content card" style="text-align: center">
        <h3>&#x1F3B0; 随机选菜</h3>
        <p class="text-sm text-secondary" style="margin-bottom: 16px">从当前搜索结果中随机抽取</p>
        <div v-if="rouletteResult" class="roulette-result">
          <div class="roulette-icon">&#x1F372;</div>
          <h2>{{ rouletteResult.name }}</h2>
          <p class="text-secondary">{{ rouletteResult.cuisine }} · {{ rouletteResult.category_name }}</p>
          <p class="text-sm">约 {{ rouletteResult.calories_per_100g || 0 }} kcal/100g</p>
        </div>
        <div v-if="spinning" class="text-muted text-sm" style="padding: 40px 0">转转转...</div>
        <div class="modal-actions" style="justify-content: center; margin-top: 16px">
          <button class="btn btn-primary" :disabled="spinning || !foods.length" @click="spinRoulette">
            {{ spinning ? '抽选中...' : '开始抽选' }}
          </button>
          <button v-if="rouletteResult" class="btn btn-outline btn-sm" @click="openRecordModal(rouletteResult); showRoulette = false">
            就吃这个
          </button>
        </div>
      </div>
    </div>

    <!-- 高级筛选弹窗 -->
    <div v-if="showFilter" class="modal-overlay" @click.self="showFilter = false">
      <div class="modal-content card">
        <h3>&#x1F50D; 高级筛选</h3>
        <div class="form-group">
          <label class="form-label">辣度</label>
          <div class="meal-btns">
            <button v-for="s in spicyOptions" :key="s.value"
              class="tag" :class="filterForm.spicy === s.value ? 'tag-primary' : 'tag-default'"
              style="cursor: pointer" @click="filterForm.spicy = filterForm.spicy === s.value ? '' : s.value">
              {{ s.label }}
            </button>
          </div>
        </div>
        <div class="form-group">
          <label class="form-label">菜系</label>
          <select v-model="filterForm.cuisine" class="input">
            <option value="">不限</option>
            <option v-for="c in cuisineOptions" :key="c" :value="c">{{ c }}</option>
          </select>
        </div>
        <div class="form-group">
          <label class="form-label">热量上限 (kcal/100g)</label>
          <input v-model.number="filterForm.maxCal" class="input" type="number" min="0" placeholder="不限" />
        </div>
        <div class="modal-actions">
          <button class="btn btn-outline" @click="resetFilter">重置</button>
          <button class="btn btn-primary" @click="applyFilter">应用筛选</button>
        </div>
      </div>
    </div>

    <!-- 记录弹窗 -->
    <div v-if="showModal" class="modal-overlay" @click.self="showModal = false">
      <div class="modal-content card">
        <h3>记录饮食：{{ selectedFood?.name }}</h3>
        <p class="text-sm text-secondary">每100g 约 {{ selectedFood?.calories_per_100g || 0 }} kcal</p>

        <div class="form-group">
          <label class="form-label">餐别</label>
          <div class="meal-btns">
            <button
              v-for="m in mealOptions"
              :key="m.value"
              class="tag"
              :class="recordForm.meal_type === m.value ? 'tag-primary' : 'tag-default'"
              style="cursor: pointer"
              @click="recordForm.meal_type = m.value"
            >
              {{ m.label }}
            </button>
          </div>
        </div>

        <div class="form-group">
          <label class="form-label">分量（克）</label>
          <input
            v-model.number="recordForm.quantity_g"
            class="input"
            type="number"
            min="10"
            max="5000"
            placeholder="例如 200"
          />
          <p class="text-xs text-muted" style="margin-top:4px">
            预估热量：{{ estimatedCal }} kcal
          </p>
        </div>

        <div class="modal-actions">
          <button class="btn btn-outline" @click="showModal = false">取消</button>
          <button
            class="btn btn-primary"
            :disabled="!canRecord || recording"
            @click="submitRecord"
          >
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
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'
import { createDietRecord } from '@/api/diet'

const keyword = ref('')
const selectedCat = ref(null)
const foods = ref([])
const categories = ref([])
const loading = ref(false)

// 记录弹窗
const showModal = ref(false)
const selectedFood = ref(null)
const recording = ref(false)
const recordMsg = ref('')
const recordOk = ref(false)

// 随机转盘
const showRoulette = ref(false)
const rouletteResult = ref(null)
const spinning = ref(false)

// 高级筛选
const showFilter = ref(false)
const filterForm = ref({ spicy: '', cuisine: '', maxCal: null })
const cuisineOptions = ref([])

const spicyOptions = [
  { value: 'none', label: '不辣' },
  { value: 'low', label: '微辣' },
  { value: 'medium', label: '中辣' },
  { value: 'high', label: '重辣' },
]

const mealOptions = [
  { value: 'breakfast', label: '早餐' },
  { value: 'lunch', label: '午餐' },
  { value: 'dinner', label: '晚餐' },
  { value: 'snack', label: '零食' },
]

const recordForm = ref({
  meal_type: 'lunch',
  quantity_g: 200,
})

const estimatedCal = computed(() => {
  if (!selectedFood.value) return 0
  const cal = selectedFood.value.calories_per_100g || 0
  return Math.round(cal * recordForm.value.quantity_g / 100)
})

const canRecord = computed(() => {
  return recordForm.value.quantity_g >= 10 && recordForm.value.meal_type
})

onMounted(async () => {
  try {
    const res = await axios.get('/api/foods/categories')
    categories.value = res.data
    cuisineOptions.value = res.data.map(c => c.name)
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

    // 前端辣度筛选（后端不支持标签筛选时）
    if (filterForm.value.spicy) {
      items = items.filter(f => {
        try {
          const tags = typeof f.tags === 'string' ? JSON.parse(f.tags) : (f.tags || {})
          return tags.spicy === filterForm.value.spicy
        } catch { return true }
      })
    }
    // 前端热量上限筛选
    if (filterForm.value.maxCal) {
      items = items.filter(f => (f.calories_per_100g || 9999) <= filterForm.value.maxCal)
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

function openRoulette() {
  if (!foods.value.length) {
    alert('请先搜索食物')
    return
  }
  rouletteResult.value = null
  showRoulette.value = true
}

function spinRoulette() {
  if (!foods.value.length) return
  spinning.value = true
  rouletteResult.value = null
  // 模拟转盘动画：快速切换
  let count = 0
  const total = 15
  const interval = setInterval(() => {
    const idx = Math.floor(Math.random() * foods.value.length)
    rouletteResult.value = foods.value[idx]
    count++
    if (count >= total) {
      clearInterval(interval)
      spinning.value = false
    }
  }, 100)
}

function openFilter() {
  showFilter.value = true
}

function applyFilter() {
  showFilter.value = false
  search()
}

function resetFilter() {
  filterForm.value = { spicy: '', cuisine: '', maxCal: null }
  showFilter.value = false
  search()
}

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
    recordMsg.value = e?.response?.data?.detail || '记录失败，请重试'
    recordOk.value = false
  } finally {
    recording.value = false
  }
}
</script>

<style scoped>
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
.food-card-body {
  padding: var(--spacing-md);
}
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
.btn-sm {
  padding: 6px 14px;
  font-size: 13px;
}

/* 弹窗 */
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
.modal-content h3 {
  margin-bottom: 4px;
  font-size: var(--font-size-lg);
}
.form-group {
  margin-top: var(--spacing-md);
}
.form-label {
  display: block;
  font-size: 13px;
  font-weight: 500;
  margin-bottom: 4px;
  color: var(--color-text-secondary);
}
.meal-btns {
  display: flex;
  gap: var(--spacing-sm);
}
.modal-actions {
  display: flex;
  gap: var(--spacing-sm);
  justify-content: flex-end;
  margin-top: var(--spacing-lg);
}

/* 转盘 */
.roulette-result {
  padding: 20px;
  background: var(--color-bg-warm);
  border-radius: var(--radius-md);
}
.roulette-icon {
  font-size: 48px;
  margin-bottom: 8px;
}

@media (max-width: 640px) {
  .food-grid {
    grid-template-columns: 1fr 1fr;
  }
}
</style>
