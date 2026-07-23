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
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const keyword = ref('')
const selectedCat = ref(null)
const foods = ref([])
const categories = ref([])
const loading = ref(false)

onMounted(async () => {
  try {
    const res = await axios.get('/api/foods/categories')
    categories.value = res.data
  } catch { /* ignore */ }
  search()
})

async function search() {
  loading.value = true
  try {
    const params = { page_size: 20 }
    if (keyword.value) params.keyword = keyword.value
    if (selectedCat.value) params.category_id = selectedCat.value
    const res = await axios.get('/api/foods', { params })
    foods.value = res.data.items
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
  alert('转盘功能将在 P1 阶段实现')
}

function openFilter() {
  alert('高级筛选功能将在 P1 阶段实现')
}
</script>

<style scoped>
.search-bar {
  display: flex;
  gap: var(--spacing-sm);
  margin-bottom: var(--spacing-md);
}
.search-bar .input {
  flex: 1;
}
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
@media (max-width: 640px) {
  .food-grid {
    grid-template-columns: 1fr 1fr;
  }
}
</style>
