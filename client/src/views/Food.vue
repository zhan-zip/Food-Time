<template>
  <div class="food-page">
    <van-nav-bar title="食物库" fixed />

    <div class="food-content">
      <!-- 搜索栏 -->
      <van-search
        v-model="keyword"
        placeholder="搜索食物名称"
        @search="onSearch"
      />

      <!-- 分类标签 -->
      <div class="category-tabs">
        <van-tag
          v-for="cat in categories"
          :key="cat.id"
          :type="cat.id === activeCategory ? 'primary' : 'default'"
          size="medium"
          style="margin: 4px"
          @click="selectCategory(cat.id)"
        >
          {{ cat.name }}
        </van-tag>
      </div>

      <!-- 食物列表 -->
      <van-pull-refresh v-model="refreshing" @refresh="onRefresh">
        <van-list
          v-model:loading="loading"
          :finished="finished"
          finished-text="没有更多了"
          @load="onLoad"
        >
          <van-cell
            v-for="food in foods"
            :key="food.id"
            :title="food.name"
            :label="food.cuisine + ' | ' + (food.calories_per_100g || '?') + ' kcal/100g'"
            is-link
          />
        </van-list>
      </van-pull-refresh>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import request from '../api/request'

const keyword = ref('')
const categories = ref([])
const activeCategory = ref(null)
const foods = ref([])
const loading = ref(false)
const finished = ref(false)
const refreshing = ref(false)
const page = ref(1)

onMounted(async () => {
  try {
    const res = await request.get('/foods/categories')
    categories.value = res || []
  } catch { /* ignored */ }
  onLoad()
})

function selectCategory(id) {
  activeCategory.value = activeCategory.value === id ? null : id
  page.value = 1
  foods.value = []
  finished.value = false
  onLoad()
}

async function onSearch() {
  page.value = 1
  foods.value = []
  finished.value = false
  onLoad()
}

async function onLoad() {
  if (refreshing.value) {
    foods.value = []
    page.value = 1
    finished.value = false
    refreshing.value = false
  }

  loading.value = true
  try {
    const params = { page: page.value, page_size: 20 }
    if (keyword.value) params.keyword = keyword.value
    if (activeCategory.value) params.category_id = activeCategory.value

    const res = await request.get('/foods', { params })
    foods.value = [...foods.value, ...(res.items || [])]
    if (!res.items || res.items.length < 20) {
      finished.value = true
    }
    page.value++
  } catch {
    finished.value = true
  } finally {
    loading.value = false
  }
}

async function onRefresh() {
  refreshing.value = true
  onLoad()
}
</script>

<style scoped>
.food-page {
  padding-top: 46px;
}
.food-content {
  padding: 0 0 50px;
}
.category-tabs {
  padding: 8px 12px;
  display: flex;
  flex-wrap: wrap;
}
</style>
