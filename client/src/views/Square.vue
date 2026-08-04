<template>
  <div class="page container page-section">
    <h2 class="section-title">美食广场</h2>
    <p class="text-secondary mb-lg">发现其他食光记用户分享的创意食谱，找到属于你的烹饪灵感</p>

    <!-- 排序 + 筛选工具栏 -->
    <div class="square-toolbar">
      <div class="sort-btns">
        <button class="sort-btn" :class="{ active: sortBy === 'time' }" @click="switchSort('time')">🕐 最新</button>
        <button class="sort-btn" :class="{ active: sortBy === 'hot' }" @click="switchSort('hot')">🔥 最热</button>
        <button class="sort-btn sort-order-btn" :title="order === 'desc' ? '当前：降序 ▼  点击切换为升序' : '当前：升序 ▲  点击切换为降序'" @click="toggleOrder">
          {{ order === 'desc' ? '▼ 降序' : '▲ 升序' }}
        </button>
      </div>
      <select v-if="cuisines.length > 0" class="cuisine-filter" v-model="cuisineFilter" @change="fetchRecipes">
        <option value="">全部菜系</option>
        <option v-for="c in cuisines" :key="c" :value="c">{{ c }}</option>
      </select>
    </div>

    <!-- 加载中 -->
    <div v-if="loading" class="text-center" style="padding: 60px 0;">
      <p>加载中...</p>
    </div>

    <!-- 食谱列表 -->
    <div v-else-if="recipes.length > 0" class="square-grid">
      <div
        class="card square-card"
        v-for="r in recipes"
        :key="r.id"
        @click="goDetail(r.id)"
      >
        <div class="square-img">
          <FoodImage :name="r.name" />
        </div>
        <div class="square-info">
          <h3>{{ r.name }}</h3>
          <p class="text-sm text-muted">by {{ r.author }}</p>
          <div class="square-tags" v-if="r.cuisine">
            <span class="tag tag-default tag-xs">{{ r.cuisine }}</span>
          </div>
          <div class="square-stats text-xs text-muted">
            <span>&#x2764; {{ r.like_count }}</span>
            <span>&#x2B50; {{ r.fav_count }}</span>
          </div>
          <button
            class="btn save-quick-btn"
            :class="savedIds.has(r.id) ? 'saved' : 'btn-outline'"
            @click.stop="quickSave(r)"
            :disabled="savingIds.has(r.id)"
          >
            {{ savedIds.has(r.id) ? '✓ 已收录' : '📥 收录进我的食谱' }}
          </button>
        </div>
      </div>
    </div>

    <!-- 空状态 -->
    <div v-else class="text-center" style="padding: 60px 0;">
      <p class="text-secondary">还没有人分享食谱，快来成为第一个吧！</p>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getRecipes, saveRecipe, getFavorites } from '../api/public'
import FoodImage from '../components/FoodImage.vue'

const router = useRouter()
const recipes = ref([])
const loading = ref(true)
const sortBy = ref('time')
const order = ref('desc')
const cuisineFilter = ref('')
const cuisines = ref([])

function goDetail(id) {
  router.push('/square/' + id)
}

// 快速收录进我的食谱（卡片快捷按钮）
const savedIds = reactive(new Set())
const savingIds = reactive(new Set())

async function quickSave(r) {
  if (savedIds.has(r.id) || savingIds.has(r.id)) return
  savingIds.add(r.id)
  try {
    await saveRecipe(r.id)
    savedIds.add(r.id)
    if (r.fav_count !== undefined) r.fav_count++
  } catch (e) {
    alert('收录失败：' + (e.message || '请重试'))
  } finally {
    savingIds.delete(r.id)
  }
}

function switchSort(by) {
  sortBy.value = by
  fetchRecipes()
}

function toggleOrder() {
  order.value = order.value === 'desc' ? 'asc' : 'desc'
  fetchRecipes()
}

async function fetchRecipes() {
  loading.value = true
  try {
    const params = { sort_by: sortBy.value, order: order.value }
    if (cuisineFilter.value) params.cuisine = cuisineFilter.value
    const res = await getRecipes(1, 12, params)
    recipes.value = res.items || []
    // 从已有数据中提取菜系列表
    if (cuisines.value.length === 0 && recipes.value.length > 0) {
      const set = new Set(recipes.value.map(r => r.cuisine).filter(Boolean))
      cuisines.value = [...set]
    }
  } catch (e) {
    console.error('加载食谱列表失败:', e)
  } finally {
    loading.value = false
  }
}

// 加载当前用户已收藏的食谱 id，初始化「已收录」状态
async function loadFavorites() {
  try {
    const res = await getFavorites()
    ;(res.recipe_ids || []).forEach(id => savedIds.add(id))
  } catch { /* 未登录或失败时忽略 */ }
}

onMounted(() => {
  loadFavorites()
  fetchRecipes()
})
</script>

<style scoped>
.mb-lg { margin-bottom: var(--spacing-lg); }
.square-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-md);
  flex-wrap: wrap;
  gap: var(--spacing-sm);
}
.sort-btns {
  display: flex;
  gap: 4px;
}
.sort-btn {
  padding: 4px 14px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  background: var(--color-bg-card);
  font-size: var(--font-size-xs);
  cursor: pointer;
  transition: all 0.2s;
  color: var(--color-text-muted);
}
.sort-btn:hover { border-color: var(--color-primary); color: var(--color-primary); }
.sort-btn.active {
  border-color: var(--color-primary);
  background: rgba(217, 161, 91, 0.08);
  color: var(--color-primary);
  font-weight: 600;
}
.sort-order-btn {
  margin-left: 4px;
  border-style: dashed;
  font-size: 11px;
  padding: 4px 10px;
}
.cuisine-filter {
  padding: 4px 10px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  font-size: var(--font-size-xs);
  background: var(--color-bg-card);
  color: var(--color-text);
  cursor: pointer;
}
.square-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--spacing-lg);
}
.square-card {
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
}
.square-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}
.square-img {
  height: 160px;
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 48px;
  margin-bottom: var(--spacing-md);
  overflow: hidden;
  background: var(--color-bg-warm);
}
.square-img img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.square-info h3 {
  font-size: var(--font-size-base);
  font-weight: 600;
  margin-bottom: 2px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.square-tags {
  margin: var(--spacing-xs) 0;
}
.tag-xs {
  font-size: 11px;
  padding: 1px 6px;
}
.square-stats {
  display: flex;
  gap: var(--spacing-md);
  margin-top: var(--spacing-sm);
}
.save-quick-btn {
  width: 100%;
  margin-top: var(--spacing-sm);
  font-size: 13px;
  padding: 6px 0;
}
.save-quick-btn.saved {
  border-color: #52c41a;
  color: #52c41a;
  background: rgba(82, 196, 26, 0.06);
}
@media (max-width: 768px) {
  .square-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
@media (max-width: 480px) {
  .square-grid {
    grid-template-columns: 1fr;
  }
}
</style>
